"""
Models for the Thumbnail Engine.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

@dataclass
class ThumbnailCandidate:
    timestamp: float
    frame_path: Optional[Path] = None
    event_priority: float = 0.0
    sharpness: float = 0.0
    exposure: float = 0.0
    final_score: float = 0.0
    reason: str = ""

@dataclass
class ThumbnailReport:
    selected_timestamp: float = 0.0
    event_context: str = ""
    candidate_count: int = 0
    sharpness_score: float = 0.0
    final_path: Optional[Path] = None
