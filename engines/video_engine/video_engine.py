"""
The core Video Engine facade inheriting from BaseEngine.
"""
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError
from core.dependency_injection.container import container
from core.config.config_manager import ConfigManager
from pathlib import Path

from engines.video_engine.ffmpeg.ffmpeg_manager import FFmpegManager
from engines.video_engine.metadata.metadata_service import MetadataService
from engines.video_engine.validator import VideoValidator
from engines.video_engine.extractor.frame_extractor import FrameExtractor
from engines.video_engine.extractor.audio_extractor import AudioExtractor
from engines.video_engine.cutter.video_cutter import VideoCutter
from engines.video_engine.converter.video_converter import VideoConverter
from engines.video_engine.exporter.export_service import ExportService
from engines.video_engine.pipeline import VideoPipeline

class VideoEngine(BaseEngine):
    def __init__(self) -> None:
        super().__init__("video_engine")
        self.ffmpeg_manager = FFmpegManager()
        self.metadata_service = MetadataService(self.ffmpeg_manager)
        self.validator = VideoValidator(self.metadata_service)
        self.frame_extractor = FrameExtractor(self.ffmpeg_manager)
        self.audio_extractor = AudioExtractor(self.ffmpeg_manager)
        self.cutter = VideoCutter(self.ffmpeg_manager)
        self.converter = VideoConverter(self.ffmpeg_manager)
        
        try:
            config = container.resolve(ConfigManager).get()
            out_dir = Path(config.output_dir)
        except Exception:
            out_dir = Path("data/output")
            
        self.export_service = ExportService(out_dir)
        self.pipeline = VideoPipeline(
            self.validator, 
            self.metadata_service, 
            self.audio_extractor, 
            self.export_service
        )

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Video Engine...")
        try:
            self.ffmpeg_manager.initialize()
            # We will use INITIALIZING or RUNNING logic appropriately
            self.is_initialized = True
            self.logger.info("Video Engine initialized successfully.")
        except Exception as e:
            self._status = EngineStatus.ERROR
            raise EngineInitError("Failed to initialize VideoEngine") from e

    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized VideoEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Video Engine started.")

    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Video Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Video Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING and self.ffmpeg_manager.is_ready
