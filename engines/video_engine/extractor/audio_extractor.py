"""
Extracts audio from video files for AI analysis.
"""
from pathlib import Path
from engines.video_engine.ffmpeg.ffmpeg_manager import FFmpegManager
from core.exceptions.video_exceptions import ExtractionError
import logging

logger = logging.getLogger(__name__)

class AudioExtractor:
    def __init__(self, ffmpeg_manager: FFmpegManager) -> None:
        self.ffmpeg_manager = ffmpeg_manager

    def extract_wav(self, video_path: Path, output_path: Path, sample_rate: int = 16000, channels: int = 1) -> None:
        """Extract audio to WAV format, commonly used for models like Whisper."""
        args = [
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-y",
            str(output_path)
        ]
        code, _, err = self.ffmpeg_manager.run_ffmpeg(args)
        if code != 0 or not output_path.exists():
            raise ExtractionError(f"Failed to extract audio from {video_path}: {err}")
