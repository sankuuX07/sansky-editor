"""
Strongly typed dataclasses for Premiere Engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
from enum import Enum

class PremiereStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class PremiereProject:
    name: str
    path: Path
    is_open: bool = False

@dataclass
class SequenceInfo:
    name: str
    width: int
    height: int
    framerate: float
    sequence_id: str = ""

@dataclass
class TimelineClip:
    asset_path: Path
    start_time: float
    end_time: float
    track_type: str = "video" # 'video' or 'audio'
    track_index: int = 1

@dataclass
class MediaAsset:
    path: Path
    bin_path: str = "Root"

@dataclass
class ImportTask:
    assets: List[MediaAsset]
    create_bins_if_missing: bool = True

@dataclass
class ExportPreset:
    name: str
    epr_path: Optional[Path] = None

@dataclass
class ExportTask:
    sequence: SequenceInfo
    preset: ExportPreset
    output_path: Path
    status: str = "pending"

@dataclass
class TimelineMarker:
    name: str
    time: float
    duration: float = 0.0
    color: str = "green"
