import json
import logging
from pathlib import Path
from core.models.preference_models import UserEditingProfile, FeedbackRecord
from core.models.shorts_models import OutputSettings

logger = logging.getLogger(__name__)

class PreferenceEngine:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.preferences_path = self.data_dir / "preferences.json"
        self.profile = UserEditingProfile()
        self.learning_rate = 0.05
        
    def initialize(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.load_profile()
        
    def load_profile(self):
        if self.preferences_path.exists():
            try:
                with open(self.preferences_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.profile = UserEditingProfile(**data)
                logger.info("Loaded User Editing Profile.")
            except Exception as e:
                logger.error(f"Failed to load preference profile: {e}")
                self.profile = UserEditingProfile()
        else:
            self.save_profile()
            
    def save_profile(self):
        try:
            with open(self.preferences_path, "w", encoding="utf-8") as f:
                json.dump(self.profile.__dict__, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save preference profile: {e}")
            
    def reset_profile(self):
        self.profile.reset()
        self.save_profile()
        
    def set_learning_enabled(self, enabled: bool):
        self.profile.learning_enabled = enabled
        self.save_profile()
        
    def submit_feedback(self, feedback: FeedbackRecord):
        if not self.profile.learning_enabled:
            return
            
        # Process Editing Feedback
        if feedback.editing_feedback:
            if "Too much zoom" in feedback.editing_feedback:
                self.profile.zoom_preference = max(0.0, self.profile.zoom_preference - self.learning_rate)
            elif "Not enough zoom" in feedback.editing_feedback:
                self.profile.zoom_preference = min(1.0, self.profile.zoom_preference + self.learning_rate)
                
            if "Too much shake" in feedback.editing_feedback:
                self.profile.shake_preference = max(0.0, self.profile.shake_preference - self.learning_rate)
                
            if "Good slow motion" in feedback.editing_feedback:
                self.profile.slow_motion_preference = min(1.0, self.profile.slow_motion_preference + self.learning_rate)
                
            if "Too many effects" in feedback.editing_feedback:
                self.profile.action_intensity_preference = max(0.0, self.profile.action_intensity_preference - self.learning_rate)
            elif "Too simple" in feedback.editing_feedback:
                self.profile.action_intensity_preference = min(1.0, self.profile.action_intensity_preference + self.learning_rate)
                
        # Process Captions Feedback
        if feedback.caption_feedback:
            if "Too many captions" in feedback.caption_feedback:
                self.profile.caption_density = max(0.0, self.profile.caption_density - self.learning_rate)
            elif "More captions" in feedback.caption_feedback:
                self.profile.caption_density = min(1.0, self.profile.caption_density + self.learning_rate)
                
        # Process Audio Feedback
        if feedback.audio_feedback:
            if "Gameplay too loud" in feedback.audio_feedback:
                self.profile.audio_ducking = min(1.0, self.profile.audio_ducking + self.learning_rate)
            elif "Voice too quiet" in feedback.audio_feedback:
                self.profile.audio_ducking = min(1.0, self.profile.audio_ducking + self.learning_rate)
                
        # Process Thumbnail Feedback
        if feedback.thumbnail_feedback:
            if "Too much enhancement" in feedback.thumbnail_feedback:
                self.profile.thumbnail_enhancement = max(0.0, self.profile.thumbnail_enhancement - self.learning_rate)
                
        self.profile.feedback_count += 1
        self.profile.last_updated = __import__('time').time()
        self.save_profile()
        logger.info(f"Updated preferences based on feedback for job {feedback.job_id}")

    def apply_preferences_to_settings(self, settings: OutputSettings) -> OutputSettings:
        """Modifies OutputSettings based on the learned profile, keeping it within safe boundaries."""
        if not self.profile.learning_enabled:
            return settings
            
        # Map continuous [0.0, 1.0] to Discrete Enums
        def get_intensity(val: float) -> str:
            if val < 0.33: return "LIGHT"
            if val > 0.66: return "STRONG"
            return "MEDIUM"
            
        settings.zoom_intensity = get_intensity(self.profile.zoom_preference)
        settings.shake_intensity = get_intensity(self.profile.shake_preference)
        
        # In a real app we might map action_intensity to editing_style or specific thresholds
        if self.profile.action_intensity_preference > 0.7:
            settings.editing_style = "INTENSE"
        elif self.profile.action_intensity_preference < 0.3:
            settings.editing_style = "CLEAN"
            
        return settings
