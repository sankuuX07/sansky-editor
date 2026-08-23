"""
Strongly typed dataclasses for Caption Engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path

class ExportFormat(Enum):
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    JSON = "json"
    TXT = "txt"

@dataclass
class CaptionWord:
    text: str
    start_time: float
    end_time: float
    probability: float = 1.0
    is_emphasized: bool = False

@dataclass
class CaptionSegment:
    index: int
    text: str
    start_time: float
    end_time: float
    words: List[CaptionWord] = field(default_factory=list)

@dataclass
class CaptionStyle:
    font_family: str = "Arial"
    font_size: int = 48
    color_hex: str = "#FFFFFF"
    stroke_color_hex: str = "#000000"
    stroke_width: int = 2
    shadow_color_hex: str = "#000000"
    shadow_offset: int = 4
    alignment: str = "center"
    margin_bottom: int = 50
    # Reserved for future AI animation mapping
    animation_type: str = "none" 

@dataclass
class CaptionPreset:
    preset_name: str
    style: CaptionStyle
    max_words_per_segment: int = 5
    max_chars_per_segment: int = 30
    max_duration_sec: float = 3.0

@dataclass
class CaptionTimeline:
    video_id: str
    segments: List[CaptionSegment] = field(default_factory=list)
    preset_used: Optional[CaptionPreset] = None

@dataclass
class CaptionExportSettings:
    format: ExportFormat
    output_dir: Path
    filename_prefix: str = "captions"

@dataclass
class CaptionValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
