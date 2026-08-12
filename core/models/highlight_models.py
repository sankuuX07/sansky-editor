"""
Strongly typed dataclasses for Highlight Engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
from enum import Enum

class EventType(str, Enum):
    FIGHT = "FIGHT"
    ENEMY_ENCOUNTER = "ENEMY_ENCOUNTER"
    GUNFIRE = "GUNFIRE"
    KNOCK = "KNOCK"
    ELIMINATION = "ELIMINATION"
    MULTI_KILL = "MULTI_KILL"
    CLUTCH = "CLUTCH"
    CLOSE_FIGHT = "CLOSE_FIGHT"
    FINAL_CIRCLE = "FINAL_CIRCLE"
    HIGH_ACTION = "HIGH_ACTION"
    LOW_ACTION = "LOW_ACTION"
    LOOTING = "LOOTING"
    TRAVEL = "TRAVEL"
    DEAD_TIME = "DEAD_TIME"

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
        super().__init__(event_type="high_audio_intensity", start_time=start_time, end_time=end_time, intensity=intensity)

@dataclass
class SpeechEvent(HighlightEvent):
    text: str
    def __init__(self, start_time: float, end_time: float, intensity: float, text: str) -> None:
        super().__init__(event_type="speech_keyword", start_time=start_time, end_time=end_time, intensity=intensity)
        self.text = text

@dataclass
class HighlightScore:
    total_score: float
    components: Dict[str, float] = field(default_factory=dict)
    
@dataclass
class HighlightCandidate:
    start_time: float
    end_time: float
    score: Optional[HighlightScore]
    events_contained: List[HighlightEvent] = field(default_factory=list)
    semantic_type: Optional[str] = None
    confidence: float = 0.0
    reason: str = ""

@dataclass
class HighlightTimeline:
    video_id: str
    highlights: List[HighlightCandidate] = field(default_factory=list)
    
@dataclass
class HighlightConfig:
    min_clip_duration_sec: float = 3.0
    max_clip_duration_sec: float = 60.0
    merge_distance_sec: float = 10.0  # Increased for better temporal grouping
    pre_roll_sec: float = 3.0
    post_roll_sec: float = 3.0
    score_threshold: float = 2.0
    weights: Dict[str, float] = field(default_factory=lambda: {
        "scene_change": 1.0,
        "high_motion": 1.5,
        "high_audio_intensity": 2.0,
        "speech_keyword": 3.0,
        EventType.CLUTCH.value: 10.0,
        EventType.MULTI_KILL.value: 8.0,
        EventType.ELIMINATION.value: 6.0,
        EventType.FIGHT.value: 5.0,
        EventType.ENEMY_ENCOUNTER.value: 3.0,
        EventType.DEAD_TIME.value: -5.0,
    })

@dataclass
class HighlightStatistics:
    video_id: str
    total_events_detected: int
    total_candidates_generated: int
    highest_score: float
