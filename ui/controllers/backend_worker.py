from PySide6.QtCore import QThread, Signal
import asyncio
import logging

logger = logging.getLogger(__name__)

class ShortsGenerationWorker(QThread):
    progress_updated = Signal(str, int)  # status_message, percentage
    generation_completed = Signal(object) # result object
    generation_failed = Signal(str) # error message

    def __init__(self, shorts_engine, video_paths, settings, backend_loop):
        super().__init__()
        self.shorts_engine = shorts_engine
        self.video_paths = video_paths
        self.settings = settings
        self.backend_loop = backend_loop
        self._future = None
        self._is_cancelled = False
        
    def cancel(self):
        self._is_cancelled = True
        if self._future:
            # Thread-safe cancellation of asyncio task
            self.backend_loop.call_soon_threadsafe(self._future.cancel)
            
    def run(self):
        try:
            self.progress_updated.emit("Submitting workflow to background thread...", 5)
            
            # Helper callbacks
            def progress_cb(msg: str, pct: int):
                self.progress_updated.emit(msg, pct)
                
            def is_cancelled_cb() -> bool:
                return self._is_cancelled
                
            from core.models.batch_models import BatchJob, SingleJob
            from engines.batch_engine.batch_engine import BatchProcessingEngine
            
            batch = BatchJob()
            for vp in self.video_paths:
                batch.jobs.append(SingleJob(video_path=vp))
                
            batch_engine = BatchProcessingEngine(self.shorts_engine)
                
            self._future = asyncio.run_coroutine_threadsafe(
                batch_engine.process_batch(
                    batch, 
                    self.settings,
                    progress_callback=progress_cb,
                    is_cancelled_callback=is_cancelled_cb
                ),
                self.backend_loop
            )
            
            result = self._future.result()
            
            if not self._is_cancelled:
                self.progress_updated.emit("Workflow Completed", 100)
                self.generation_completed.emit(result)
            else:
                self.generation_failed.emit("Workflow Cancelled by User")
                
        except asyncio.CancelledError:
            self.generation_failed.emit("Workflow Cancelled by User")
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            self.generation_failed.emit(str(e))
