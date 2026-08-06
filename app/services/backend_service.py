import threading
import asyncio
import logging
from concurrent.futures import Future

from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager
from engines.automation_engine.automation_engine import AutomationEngine
from engines.shorts_generator_engine.shorts_generator_engine import ShortsGeneratorEngine

logger = logging.getLogger(__name__)

class BackendService(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = None
        self.engine_manager = None
        self.task_manager = None
        self.shorts_generator = None
        self._ready_event = threading.Event()
        self._shutdown_event = threading.Event()
        self._shutdown_future = None

    async def _main_task(self):
        try:
            import os
            from pathlib import Path
            ffmpeg_dir = Path("tools/ffmpeg/bin").absolute()
            if ffmpeg_dir.exists():
                os.environ["PATH"] += os.pathsep + str(ffmpeg_dir)
                logger.info(f"Added {ffmpeg_dir} to system PATH")

            # Initialize core components INSIDE the running event loop
            self.engine_manager = EngineManager()
            
            from core.dependency_injection.container import container
            container.register_instance(EngineManager, self.engine_manager)
            
            self.task_manager = TaskManager(max_workers=4)
            
            from engines.video_engine.video_engine import VideoEngine
            from engines.ai_engine.ai_engine import AIEngine
            from engines.caption_engine.caption_engine import CaptionEngine
            from engines.highlight_engine.highlight_engine import HighlightEngine
            from engines.premiere_engine.premiere_engine import PremiereEngine
            
            video_engine = VideoEngine()
            ai_engine = AIEngine()
            caption_engine = CaptionEngine()
            highlight_engine = HighlightEngine()
            premiere_engine = PremiereEngine()
            
            self.engine_manager.register(video_engine)
            self.engine_manager.register(ai_engine)
            self.engine_manager.register(caption_engine)
            self.engine_manager.register(highlight_engine)
            self.engine_manager.register(premiere_engine)
            
            automation = AutomationEngine(self.engine_manager, self.task_manager)
            self.engine_manager.register(automation)
            
            self.shorts_generator = ShortsGeneratorEngine(automation)
            self.engine_manager.register(self.shorts_generator)
            
            # Start everything up
            self.engine_manager.initialize_all()
            self.engine_manager.start_all()
            self.task_manager.start_workers()
            
            logger.info("BackendService is fully initialized and running.")
            self._ready_event.set()
            
            # Wait until shutdown is triggered
            await self._shutdown_future
            
        except Exception as e:
            logger.error("Failed to initialize backend", exc_info=True)
        finally:
            # Teardown
            logger.info("BackendService shutting down...")
            if self.engine_manager:
                self.engine_manager.shutdown_all()
            if self.task_manager:
                await self.task_manager.stop_workers()

    def run(self):
        """Runs the asyncio event loop in this background thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self._shutdown_future = self.loop.create_future()
        
        try:
            # This completely solves the RuntimeError by ensuring the loop is "running"
            # before any asyncio primitive instantiation happens.
            self.loop.run_until_complete(self._main_task())
        finally:
            # Clean up loop
            pending = asyncio.all_tasks(loop=self.loop)
            for task in pending:
                task.cancel()
            if pending:
                self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
            self.loop.close()
            self._shutdown_event.set()

    def wait_until_ready(self, timeout=None):
        return self._ready_event.wait(timeout)

    def shutdown(self):
        """Safely stops the event loop from another thread."""
        if self.loop and self.loop.is_running() and not self._shutdown_future.done():
            self.loop.call_soon_threadsafe(self._shutdown_future.set_result, None)
            self._shutdown_event.wait()
