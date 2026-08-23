"""
Models for the Composition Engine.
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CompositionEvent:
    start_time: float
    end_time: float
    focus_region: str # e.g. "CENTER", "LEFT", "RIGHT", "ACTION"
    fallback_used: bool = False
    reason: str = ""

@dataclass
class CompositionTimeline:
    clip_id: str
    target_aspect_ratio: str
    target_resolution: str
    layout: str
    events: List[CompositionEvent] = field(default_factory=list)
