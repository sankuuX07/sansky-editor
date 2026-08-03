"""
Validates video files before processing.
"""
from pathlib import Path
from core.exceptions.video_exceptions import VideoValidationError
from engines.video_engine.metadata.metadata_service import MetadataService

class VideoValidator:
    def __init__(self, metadata_service: MetadataService) -> None:
        self.metadata_service = metadata_service
        self.supported_extensions = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

    def validate(self, file_path: Path) -> None:
        """Validate if a file is a supported, non-corrupt video."""
        if not file_path.exists():
            raise VideoValidationError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise VideoValidationError(f"Path is not a file: {file_path}")

        if file_path.suffix.lower() not in self.supported_extensions:
            raise VideoValidationError(f"Unsupported format {file_path.suffix}. Supported: {self.supported_extensions}")

        # Extract metadata to verify it's not corrupt
        metadata = self.metadata_service.extract_metadata(file_path)
        if metadata.duration_sec <= 0:
            raise VideoValidationError(f"Video has 0 duration or is corrupt: {file_path}")
        if len(metadata.video_streams) == 0:
            raise VideoValidationError(f"No video streams found in file: {file_path}")
