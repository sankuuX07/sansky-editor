"""
The AI Engine facade.
"""
import logging
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError

from engines.ai_engine.hardware.gpu_manager import GPUManager
from engines.ai_engine.hardware.memory_manager import MemoryManager
from engines.ai_engine.models.model_registry import ModelRegistry
from engines.ai_engine.models.model_manager import ModelManager
from engines.ai_engine.models.model_downloader import ModelDownloader
from engines.ai_engine.inference.inference_manager import InferenceManager
from engines.ai_engine.pipeline.pipeline_manager import PipelineManager

class AIEngine(BaseEngine):
    def __init__(self) -> None:
        super().__init__("ai_engine")
        self.gpu_manager = GPUManager()
        self.memory_manager = MemoryManager(self.gpu_manager)
        self.registry = ModelRegistry()
        self.downloader = ModelDownloader(self.registry)
        self.model_manager = ModelManager(self.registry, self.memory_manager)
        self.inference_manager = InferenceManager(self.model_manager, self.gpu_manager)
        self.pipeline_manager = PipelineManager()

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing AI Engine...")
        try:
            self.gpu_manager.initialize()
            
            self._status = EngineStatus.INITIALIZED
            self.is_initialized = True
            self.logger.info("AI Engine initialized successfully.")
        except Exception as e:
            self._status = EngineStatus.ERROR
            raise EngineInitError("Failed to initialize AIEngine") from e

    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized AIEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("AI Engine started.")

    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("AI Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("AI Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING and self.gpu_manager.active_backend is not None

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribes audio using a Whisper model.
        Falls back to a mocked dictionary if no real inference is available.
        """
        self.logger.info(f"Transcribing audio: {audio_path}")
        
        try:
            import whisper
        except ImportError:
            self.logger.error("Whisper is not installed. Returning fallback.")
            return {
                "text": "Fallback generated transcript because whisper is not installed.",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 2.0,
                        "text": "Fallback generated transcript",
                        "words": [
                            {"word": "Fallback", "start": 0.0, "end": 0.5, "probability": 0.9},
                            {"word": "generated", "start": 0.5, "end": 1.0, "probability": 0.9},
                            {"word": "transcript", "start": 1.0, "end": 2.0, "probability": 0.9}
                        ]
                    }
                ]
            }

        try:
            # We use 'tiny' model for speed in execution
            model = whisper.load_model("tiny", device="cpu")
            self.logger.info("Whisper model loaded successfully.")
            
            result = model.transcribe(audio_path, word_timestamps=True)
            self.logger.info("Audio transcribed successfully.")
            return result
        except Exception as e:
            self.logger.error(f"Failed to transcribe audio: {e}")
            raise
