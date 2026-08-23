"""
Strongly typed dataclasses for the Audio Engine.
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AudioEvent:
    start_time: float
    end_time: float
    event_type: str # 'DUCKING', 'EMPHASIS'
    target_volume: float
    reason: str
    source_event: Optional[str] = None

@dataclass
class AudioTimeline:
    video_id: str
    events: List[AudioEvent] = field(default_factory=list)

@dataclass
class AudioAnalysis:
    duration: float = 0.0
    integrated_loudness: float = 0.0
    peak_level: float = 0.0
    quiet_regions: List[tuple] = field(default_factory=list)
    loud_regions: List[tuple] = field(default_factory=list)
    silence_regions: List[tuple] = field(default_factory=list)
