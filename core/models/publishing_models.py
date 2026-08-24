"""
Models for the Creator Publishing Hub (M18).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid

class ExportStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class PlatformExportProfile:
    platform: str
    name: str
    aspect_ratio: str = "16:9"
    width: int = 1920
    height: int = 1080
    fps: float = 60.0
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    container: str = "mp4"
    bitrate: Optional[str] = None
    max_duration: Optional[float] = None
    thumbnail_supported: bool = True
    metadata_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExportTarget:
    target_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    profile: PlatformExportProfile = field(default_factory=lambda: PlatformExportProfile("CUSTOM", "Custom"))
    title: str = ""
    description: str = ""
    hashtags: List[str] = field(default_factory=list)
    thumbnail_path: Optional[str] = None
    status: ExportStatus = ExportStatus.PENDING
    progress: float = 0.0
    output_path: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class PublishingProject:
    publishing_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    source_job_id: str = ""
    source_version: int = 1
    created_at: str = ""
    updated_at: str = ""
    export_targets: List[ExportTarget] = field(default_factory=list)
    status: ExportStatus = ExportStatus.PENDING
    metadata_version: int = 1
