"""
Converts video formats.
"""
from pathlib import Path
from engines.video_engine.ffmpeg.ffmpeg_manager import FFmpegManager
from core.models.video_models import EncodingSettings
from core.exceptions.video_exceptions import ConversionError
import logging

logger = logging.getLogger(__name__)

class VideoConverter:
    def __init__(self, ffmpeg_manager: FFmpegManager) -> None:
        self.ffmpeg_manager = ffmpeg_manager

    def convert(self, source_path: Path, output_path: Path, settings: EncodingSettings) -> Path:
        """Convert a video file based on explicit encoding settings."""
        args = ["-i", str(source_path)]
        
        args.extend(["-c:v", settings.video_codec])
        if settings.video_bitrate:
            args.extend(["-b:v", settings.video_bitrate])
        elif settings.video_codec == "libx264":
            args.extend(["-preset", settings.preset, "-crf", str(settings.crf)])
            
        args.extend(["-c:a", settings.audio_codec])
        if settings.audio_bitrate:
            args.extend(["-b:a", settings.audio_bitrate])
            
        args.extend(settings.extra_args)
        args.extend(["-y", str(output_path)])
        
        code, _, err = self.ffmpeg_manager.run_ffmpeg(args)
        if code != 0 or not output_path.exists():
            raise ConversionError(f"Failed to convert video {source_path}: {err}")
            
        return output_path
