"""
Models for the Shorts Generator Engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
import uuid
from enum import Enum

class ProcessingStatus(Enum):
    PENDING = "PENDING"
    ANALYZING = "ANALYZING"
    TRANSCRIBING = "TRANSCRIBING"
    CAPTIONING = "CAPTIONING"
    HIGHLIGHTING = "HIGHLIGHTING"
    ASSEMBLING = "ASSEMBLING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class OutputSettings:
    max_shorts: int = 3
    min_clip_duration: float = 15.0
    max_clip_duration: float = 60.0
    output_resolution: str = "1080x1920"
    target_aspect_ratio: str = "9:16"
    caption_preset: str = "gaming_bold"
    highlight_threshold: float = 0.7
    premiere_template: str = "default_vertical"
    output_directory: str = "./outputs"
    auto_edit_enabled: bool = True
    editing_style: str = "GAMING" # CLEAN, GAMING, CINEMATIC, INTENSE
    zoom_intensity: str = "MEDIUM" # LIGHT, MEDIUM, STRONG
    shake_intensity: str = "MEDIUM" # LIGHT, MEDIUM, STRONG
    color_preset: str = "NATURAL" # NATURAL, VIBRANT, CINEMATIC, GAMING
    transition_style: str = "CUT" # CUT, FADE, FLASH
    bgm_path: Optional[str] = None # Path to background music
    audio_preset: str = "GAMING" # CLEAN, GAMING, CINEMATIC, INTENSE
    composition_style: str = "ACTION" # GAMEPLAY_FOCUS, CREATOR, ACTION, CLEAN
    facecam_layout: str = "NONE" # NONE, GAMEPLAY_FOCUS, FACE_CAM_TOP, PICTURE_IN_PICTURE
    thumbnail_text: Optional[str] = None # Text to overlay on thumbnail
    thumbnail_style: str = "GAMING" # CLEAN, GAMING, INTENSE
    thumbnail_aspect_ratio: str = "16:9" # 16:9, 9:16, 1:1

@dataclass
class ProcessingRequest:
    video_paths: List[Path]
    settings: OutputSettings = field(default_factory=OutputSettings)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    progress_callback: Optional[Any] = None # callable(msg: str, pct: int)
    is_cancelled: Optional[Any] = None # callable() -> bool

@dataclass
class GeneratedClip:
    clip_id: str
    source_video: Path
    start_time: float
    end_time: float
    score: float
    captions: List[Any] = field(default_factory=list)
    thumbnail_path: Optional[Path] = None
    semantic_type: Optional[str] = None
    events_contained: List[Any] = field(default_factory=list)
    editing_timeline: Optional[Any] = None

@dataclass
class ClipStatistics:
    total_duration: float
    caption_count: int
    average_score: float

@dataclass
class ShortsProject:
    project_id: str
    clips: List[GeneratedClip]
    settings: OutputSettings
    premiere_project_path: Optional[Path] = None
    creator_report: Optional[Any] = None

@dataclass
class CaptionAssignment:
    clip_id: str
    assigned_captions: List[Any]

@dataclass
class TimelineDefinition:
    clips: List[GeneratedClip]
    resolution: str
    framerate: float

@dataclass
class ProcessingSummary:
    total_videos: int
    successful: int
    failed: int
    generated_shorts: int
    total_time_sec: float

@dataclass
class ProjectReport:
    request_id: str
    summary: ProcessingSummary
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class ProcessingResult:
    request_id: str
    status: ProcessingStatus
    projects: List[ShortsProject] = field(default_factory=list)
    report: Optional[ProjectReport] = None
    error: Optional[str] = None
    stage_statuses: Dict[str, str] = field(default_factory=dict)
