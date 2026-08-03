import pytest
import asyncio
from pathlib import Path

from core.models.shorts_models import ProcessingStatus, OutputSettings
from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager
from engines.automation_engine.automation_engine import AutomationEngine
from engines.shorts_generator_engine.shorts_generator_engine import ShortsGeneratorEngine
from engines.base_engine import BaseEngine

class MockEngine(BaseEngine):
    def __init__(self, name):
        super().__init__(name)
        
    def initialize(self) -> None:
        from core.models.shared_types import EngineStatus
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = True
        
    def start(self) -> None:
        from core.models.shared_types import EngineStatus
        self._status = EngineStatus.RUNNING
        self.is_running = True
        
    def stop(self) -> None:
        pass
        
    def shutdown(self) -> None:
        pass
        
    def health_check(self) -> bool:
        return True

@pytest.mark.asyncio
async def test_end_to_end_workflow(temp_workspace):
    engine_manager = EngineManager()
    task_manager = TaskManager(max_workers=2)
    task_manager.start_workers()
    
    engine_manager.register(MockEngine("video_engine"))
    engine_manager.register(MockEngine("whisper_engine"))
    engine_manager.register(MockEngine("caption_engine"))
    engine_manager.register(MockEngine("premiere_engine"))
    
    automation_engine = AutomationEngine(engine_manager, task_manager)
    engine_manager.register(automation_engine)
    
    shorts_engine = ShortsGeneratorEngine(automation_engine)
    engine_manager.register(shorts_engine)
    
    engine_manager.initialize_all()
    engine_manager.start_all()
    
    dummy_video = temp_workspace / "gameplay_recording.mp4"
    dummy_video.touch()
    
    settings = OutputSettings(output_directory=str(temp_workspace / "outputs"))
    
    result = await shorts_engine.generate_shorts([dummy_video], settings)
    
    assert result.status == ProcessingStatus.COMPLETED
    assert len(result.projects) == 1
    
    project = result.projects[0]
    assert project.premiere_project_path.exists()
    
    await task_manager.stop_workers()
    engine_manager.shutdown_all()
