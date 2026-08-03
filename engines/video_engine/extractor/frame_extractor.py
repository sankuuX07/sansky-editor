"""
Extracts frames from video files.
"""
from pathlib import Path
from typing import List
from engines.video_engine.ffmpeg.ffmpeg_manager import FFmpegManager
from core.exceptions.video_exceptions import ExtractionError
import logging

logger = logging.getLogger(__name__)

class FrameExtractor:
    def __init__(self, ffmpeg_manager: FFmpegManager) -> None:
        self.ffmpeg_manager = ffmpeg_manager

    def extract_single_frame(self, video_path: Path, timestamp_sec: float, output_path: Path, qscale: int = 2) -> None:
        """Extract a single frame accurately."""
        args = [
            "-ss", str(timestamp_sec),
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", str(qscale),
            "-y",
            str(output_path)
        ]
        code, _, err = self.ffmpeg_manager.run_ffmpeg(args)
        if code != 0 or not output_path.exists():
            raise ExtractionError(f"Failed to extract frame at {timestamp_sec}s: {err}")

    def extract_multiple_frames(self, video_path: Path, timestamps_sec: List[float], output_dir: Path, qscale: int = 2) -> List[Path]:
        """Extract multiple frames based on timestamps."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for ts in timestamps_sec:
            out_path = output_dir / f"frame_{ts:.3f}.jpg"
            self.extract_single_frame(video_path, ts, out_path, qscale)
            paths.append(out_path)
        return paths
