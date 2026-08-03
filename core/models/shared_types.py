"""
Project-wide Shared Types (Strongly Typed Dataclasses).
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from pathlib import Path

class EngineStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"

class TaskState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class VideoMetadata:
    file_path: Path
    duration_sec: float
    width: int
    height: int
    fps: float
    has_audio: bool = True

@dataclass
class Clip:
    start_time: float
    end_time: float
    source_path: Path
    label: str = ""
    score: float = 0.0

@dataclass
class Subtitle:
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = None

@dataclass
class Highlight:
    clip: Clip
    reason: str
    importance_score: float

@dataclass
class ProjectSettings:
    project_name: str
    workspace_dir: Path
    target_resolution: str = "1080x1920"  # Shorts format by default
    target_fps: float = 60.0
    generate_subtitles: bool = True
    export_format: str = "mp4"
