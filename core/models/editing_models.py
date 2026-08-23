"""
Strongly typed dataclasses for the Editing Engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class EditingEventType(str, Enum):
    ZOOM = "ZOOM"
    SLOW_MOTION = "SLOW_MOTION"
    SPEED_RAMP = "SPEED_RAMP"
    IMPACT = "IMPACT"
    SHAKE = "SHAKE"
    FREEZE_FRAME = "FREEZE_FRAME"
    TRANSITION = "TRANSITION"
    COLOR_ADJUSTMENT = "COLOR_ADJUSTMENT"

@dataclass
class EditingEvent:
    event_type: str
    start_time: float
    end_time: float
    intensity: float  # Normalized 0.0 to 1.0, or specific meaning depending on type
    reason: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    source_event: Optional[Any] = None

@dataclass
class EditingTimeline:
    clip_id: str
    editing_events: List[EditingEvent] = field(default_factory=list)
