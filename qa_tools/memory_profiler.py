"""
Memory profiling tool to check for memory leaks in the engine workflow.
"""
import tracemalloc
import logging
import asyncio
from pathlib import Path
import tempfile
import sys
import os

# Ensure the root path is accessible if run as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager
from engines.automation_engine.automation_engine import AutomationEngine
from engines.shorts_generator_engine.shorts_generator_engine import ShortsGeneratorEngine
from core.models.shorts_models import OutputSettings
from engines.base_engine import BaseEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

async def run_profiler():
    tracemalloc.start()
    
    snapshot_start = tracemalloc.take_snapshot()
    logger.info("Took starting memory snapshot.")
    
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
    
    with tempfile.TemporaryDirectory() as d:
        temp_dir = Path(d)
        dummy_video = temp_dir / "gameplay_recording.mp4"
        dummy_video.touch()
        
        settings = OutputSettings(output_directory=str(temp_dir / "outputs"))
        
        await shorts_engine.generate_shorts([dummy_video], settings)
        
    await task_manager.stop_workers()
    engine_manager.shutdown_all()
    
    snapshot_end = tracemalloc.take_snapshot()
    logger.info("Took ending memory snapshot.")
    
    stats = snapshot_end.compare_to(snapshot_start, 'lineno')
    
    print("\n[ Top 10 Memory Differences ]")
    for stat in stats[:10]:
        print(stat)

if __name__ == "__main__":
    asyncio.run(run_profiler())
