from dataclasses import dataclass, field
from typing import Dict, Optional, List
import time

@dataclass
class FeedbackRecord:
    job_id: str
    clip_id: str
    timestamp: float = field(default_factory=time.time)
    
    # 1 to 5 rating
    overall_rating: int = 0
    
    # Optional feedback strings per category
    highlight_feedback: Optional[str] = None
    editing_feedback: Optional[str] = None
    caption_feedback: Optional[str] = None
    audio_feedback: Optional[str] = None
    composition_feedback: Optional[str] = None
    thumbnail_feedback: Optional[str] = None

@dataclass
class UserEditingProfile:
    learning_enabled: bool = True
    feedback_count: int = 0
    last_updated: float = 0.0
    
    # Continuous learned values (0.0 to 1.0 generally)
    # Higher values indicate stronger preference.
    zoom_preference: float = 0.5
    shake_preference: float = 0.5
    slow_motion_preference: float = 0.5
    action_intensity_preference: float = 0.5
    caption_density: float = 0.5
    audio_ducking: float = 0.5
    thumbnail_enhancement: float = 0.5
    
    def reset(self):
        self.feedback_count = 0
        self.zoom_preference = 0.5
        self.shake_preference = 0.5
        self.slow_motion_preference = 0.5
        self.action_intensity_preference = 0.5
        self.caption_density = 0.5
        self.audio_ducking = 0.5
        self.thumbnail_enhancement = 0.5
        self.last_updated = time.time()
