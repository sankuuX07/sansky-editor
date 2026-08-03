"""
Strongly typed dataclasses for Highlight Engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path

@dataclass
class HighlightEvent:
    """A generic event detected in the media (e.g. motion spike, audio peak)."""
    event_type: str
    start_time: float
    end_time: float
    intensity: float  # Normalized 0.0 to 1.0

@dataclass
class SceneEvent(HighlightEvent):
    def __init__(self, start_time: float, end_time: float, intensity: float = 1.0) -> None:
        super().__init__(event_type="scene_change", start_time=start_time, end_time=end_time, intensity=intensity)

@dataclass
class MotionEvent(HighlightEvent):
    def __init__(self, start_time: float, end_time: float, intensity: float) -> None:
        super().__init__(event_type="high_motion", start_time=start_time, end_time=end_time, intensity=intensity)

@dataclass
class AudioEvent(HighlightEvent):
    def __init__(self, start_time: float, end_time: float, intensity: float) -> None:
        super().__init__(event_type="audio_peak", start_time=start_time, end_time=end_time, intensity=intensity)

@dataclass
class HighlightScore:
    total_score: float
    components: Dict[str, float] = field(default_factory=dict)
    
@dataclass
class HighlightCandidate:
    start_time: float
    end_time: float
    score: HighlightScore
    events_contained: List[HighlightEvent] = field(default_factory=list)

@dataclass
class HighlightTimeline:
    video_id: str
    highlights: List[HighlightCandidate] = field(default_factory=list)
    
@dataclass
class HighlightConfig:
    min_clip_duration_sec: float = 3.0
    max_clip_duration_sec: float = 60.0
    merge_distance_sec: float = 5.0
    score_threshold: float = 2.0
    weights: Dict[str, float] = field(default_factory=lambda: {
        "scene_change": 1.0,
        "high_motion": 1.5,
        "audio_peak": 2.0,
        "custom_kill": 3.0
    })

@dataclass
class HighlightStatistics:
    video_id: str
    total_events_detected: int
    total_candidates_generated: int
    highest_score: float
