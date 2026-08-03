"""
Cuts video files by timestamps.
"""
from pathlib import Path
from typing import List
from engines.video_engine.ffmpeg.ffmpeg_manager import FFmpegManager
from core.models.shared_types import Clip
from core.exceptions.video_exceptions import VideoCutError
import logging

logger = logging.getLogger(__name__)

class VideoCutter:
    def __init__(self, ffmpeg_manager: FFmpegManager) -> None:
        self.ffmpeg_manager = ffmpeg_manager

    def cut_clip(self, clip: Clip, output_path: Path, re_encode: bool = False) -> Path:
        """Cut a specific clip from a video."""
        args = [
            "-ss", str(clip.start_time),
            "-i", str(clip.source_path),
            "-t", str(clip.end_time - clip.start_time)
        ]
        
        if not re_encode:
            args.extend(["-c", "copy"])
        else:
            args.extend(["-c:v", "libx264", "-c:a", "aac"])
            
        args.extend(["-y", str(output_path)])
        
        code, _, err = self.ffmpeg_manager.run_ffmpeg(args)
        if code != 0 or not output_path.exists():
            raise VideoCutError(f"Failed to cut video from {clip.start_time} to {clip.end_time}: {err}")
            
        return output_path

    def batch_cut(self, clips: List[Clip], output_dir: Path, re_encode: bool = False) -> List[Path]:
        """Cut multiple clips in sequence."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for i, clip in enumerate(clips):
            out_path = output_dir / f"clip_{i}_{clip.start_time:.2f}_{clip.end_time:.2f}.mp4"
            self.cut_clip(clip, out_path, re_encode)
            paths.append(out_path)
        return paths
