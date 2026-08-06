"""
FFmpeg Manager. The only module allowed to execute FFmpeg binaries.
"""
import subprocess
import logging
import shutil
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from core.config.config_manager import ConfigManager
from core.exceptions.video_exceptions import FFmpegNotFoundError
from core.dependency_injection.container import container

logger = logging.getLogger(__name__)

class FFmpegManager:
    """Manages FFmpeg execution and path resolution."""
    def __init__(self) -> None:
        self.ffmpeg_path = ""
        self.ffprobe_path = ""
        self.is_ready = False

    def initialize(self) -> None:
        """Resolve paths for FFmpeg and FFprobe."""
        try:
            config = container.resolve(ConfigManager).get()
            custom_path = config.ffmpeg_path
        except KeyError:
            custom_path = None

        search_paths = []
        if custom_path:
            search_paths.append(Path(custom_path))
            
        # Common and portable paths
        base_dir = Path(__file__).resolve().parent.parent.parent.parent # antigravity-editor
        search_paths.extend([
            base_dir / "tools" / "ffmpeg" / "bin",
            Path("C:/ffmpeg/bin"),
            Path("C:/Program Files/ffmpeg/bin")
        ])

        for path in search_paths:
            if path.exists():
                ffmpeg = path / "ffmpeg"
                ffprobe = path / "ffprobe"
                if not ffmpeg.exists(): ffmpeg = path / "ffmpeg.exe"
                if not ffprobe.exists(): ffprobe = path / "ffprobe.exe"
                
                if ffmpeg.exists() and ffprobe.exists():
                    self.ffmpeg_path = str(ffmpeg)
                    self.ffprobe_path = str(ffprobe)
                    self.is_ready = True
                    logger.info(f"FFmpeg Manager initialized. Path: {self.ffmpeg_path}")
                    return

        # Fallback to system PATH
        ffmpeg_sys = shutil.which("ffmpeg")
        ffprobe_sys = shutil.which("ffprobe")
        if ffmpeg_sys and ffprobe_sys:
            self.ffmpeg_path = ffmpeg_sys
            self.ffprobe_path = ffprobe_sys
            self.is_ready = True
            logger.info(f"FFmpeg Manager initialized from system PATH. Path: {self.ffmpeg_path}")
            return
            
        self.is_ready = False
        logger.error("Could not locate FFmpeg binary. Please install it or set 'ffmpeg_path' in config.")
        logger.info(f"FFmpeg Manager initialized. Path: {self.ffmpeg_path}")

    def run_ffprobe(self, file_path: Path) -> Dict[str, Any]:
        """Run FFprobe and return JSON metadata."""
        if not self.is_ready:
            self.initialize()
            
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]
        logger.debug(f"Executing ffprobe on: {file_path}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"FFprobe failed: {result.stderr}")
            return {}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.error("Failed to decode FFprobe output.")
            return {}

    def run_ffmpeg(self, args: List[str]) -> Tuple[int, str, str]:
        """Run FFmpeg with given arguments."""
        if not self.is_ready:
            self.initialize()
            
        cmd = [self.ffmpeg_path] + args
        logger.debug(f"Executing FFmpeg: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.warning(f"FFmpeg executed with non-zero exit code {result.returncode}")
            logger.debug(f"FFmpeg stderr: {result.stderr}")
        return result.returncode, result.stdout, result.stderr
