"""
Synchronous pipeline for standardizing video processing.
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from engines.video_engine.validator import VideoValidator
from engines.video_engine.metadata.metadata_service import MetadataService
from engines.video_engine.extractor.audio_extractor import AudioExtractor
from engines.video_engine.exporter.export_service import ExportService
from core.models.video_models import ExtendedVideoMetadata
import logging

logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    original_path: Path
    metadata: ExtendedVideoMetadata
    extracted_audio_path: Optional[Path] = None

class VideoPipeline:
    def __init__(
        self,
        validator: VideoValidator,
        metadata_service: MetadataService,
        audio_extractor: AudioExtractor,
        export_service: ExportService
    ) -> None:
        self.validator = validator
        self.metadata_service = metadata_service
        self.audio_extractor = audio_extractor
        self.export_service = export_service

    def run_standard_ingestion(self, video_path: Path, extract_audio: bool = True) -> PipelineResult:
        """Standard ingestion pipeline: Validate -> Metadata -> [Audio Extraction]"""
        logger.info(f"Starting pipeline ingestion for {video_path}")
        
        self.validator.validate(video_path)
        metadata = self.metadata_service.extract_metadata(video_path)
        
        audio_path = None
        if extract_audio and metadata.has_audio:
            audio_path = self.export_service.resolve_output_path(video_path.name, ".wav", overwrite=True)
            self.audio_extractor.extract_wav(video_path, audio_path)
            
        logger.info(f"Pipeline ingestion complete for {video_path}")
        return PipelineResult(original_path=video_path, metadata=metadata, extracted_audio_path=audio_path)
