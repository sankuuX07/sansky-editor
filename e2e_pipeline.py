import sys
import os
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))

from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager
from engines.video_engine.video_engine import VideoEngine
from engines.ai_engine.ai_engine import AIEngine
from engines.caption_engine.caption_engine import CaptionEngine
from engines.highlight_engine.highlight_engine import HighlightEngine
from engines.premiere_engine.premiere_engine import PremiereEngine
from engines.automation_engine.automation_engine import AutomationEngine
from engines.shorts_generator_engine.shorts_generator_engine import ShortsGeneratorEngine

from core.models.shorts_models import ProcessingRequest, OutputSettings
from core.dependency_injection.container import container

logging.basicConfig(level=logging.DEBUG)

async def run():
    engine_manager = EngineManager()
    task_manager = TaskManager(max_workers=4)
    
    # We must register the EngineManager to the container so that output_manager can resolve it
    container.register(EngineManager, engine_manager)

    video_engine = VideoEngine()
    ai_engine = AIEngine()
    caption_engine = CaptionEngine()
    highlight_engine = HighlightEngine()
    premiere_engine = PremiereEngine()

    engine_manager.register(video_engine)
    engine_manager.register(ai_engine)
    engine_manager.register(caption_engine)
    engine_manager.register(highlight_engine)
    engine_manager.register(premiere_engine)

    automation = AutomationEngine(engine_manager, task_manager)
    engine_manager.register(automation)

    shorts_generator = ShortsGeneratorEngine(automation)
    engine_manager.register(shorts_generator)

    engine_manager.initialize_all()
    engine_manager.start_all()
    task_manager.start_workers()

    video_path = Path("test_assets/dummy_gameplay.mp4").absolute()
    request = ProcessingRequest(
        video_paths=[video_path],
        settings=OutputSettings(output_directory="data/test_output")
    )
    
    try:
        result = await shorts_generator.pipeline.process(request)
        
        # We also need to run finalize!
        shorts_generator.output_manager.finalize(result)
        shorts_generator.report_generator.generate(result)
        
        print(f"Result: {result.status}")
    finally:
        engine_manager.shutdown_all()
        await task_manager.stop_workers()

if __name__ == "__main__":
    asyncio.run(run())
