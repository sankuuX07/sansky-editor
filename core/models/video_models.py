"""
Strongly typed models for Video operations.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from core.models.shared_types import VideoMetadata

@dataclass
class AudioStreamMetadata:
    index: int
    codec_name: str
    sample_rate: int
    channels: int
    bitrate: Optional[int] = None

@dataclass
class VideoStreamMetadata:
    index: int
    codec_name: str
    width: int
    height: int
    fps: float
    bitrate: Optional[int] = None

@dataclass
class ExtendedVideoMetadata(VideoMetadata):
    """Detailed metadata encompassing streams and container information."""
    container_format: str = ""
    video_streams: List[VideoStreamMetadata] = field(default_factory=list)
    audio_streams: List[AudioStreamMetadata] = field(default_factory=list)
    aspect_ratio: str = ""
    rotation: int = 0
    creation_time: Optional[str] = None
    file_size_bytes: int = 0

@dataclass
class EncodingSettings:
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "fast"
    crf: int = 23
    video_bitrate: Optional[str] = None
    audio_bitrate: str = "192k"
    extra_args: List[str] = field(default_factory=list)
