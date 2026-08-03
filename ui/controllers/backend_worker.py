from PySide6.QtCore import QThread, Signal
import asyncio
import logging
from core.models.shorts_models import OutputSettings
from pathlib import Path

logger = logging.getLogger(__name__)

class ShortsGenerationWorker(QThread):
    progress_updated = Signal(str, int)  # status_message, percentage
    generation_completed = Signal(object) # result object
    generation_failed = Signal(str) # error message

    def __init__(self, shorts_engine, video_paths, settings: OutputSettings, backend_loop):
        super().__init__()
        self.shorts_engine = shorts_engine
        self.video_paths = video_paths
        self.settings = settings
        self.backend_loop = backend_loop
        
    def run(self):
        try:
            self.progress_updated.emit("Submitting workflow to background thread...", 5)
            
            # Submit the coroutine to the background event loop in a thread-safe manner
            future = asyncio.run_coroutine_threadsafe(
                self.shorts_engine.generate_shorts(self.video_paths, self.settings),
                self.backend_loop
            )
            
            # Block the QThread (not the GUI thread!) until the future completes
            result = future.result()
            
            self.progress_updated.emit("Workflow Completed", 100)
            self.generation_completed.emit(result)
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            self.generation_failed.emit(str(e))
