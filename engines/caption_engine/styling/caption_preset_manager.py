"""
Manages rendering presets for different platforms.
"""
import logging
from typing import Dict, List
from core.models.caption_models import CaptionPreset, CaptionStyle
from engines.caption_engine.styling.caption_style_manager import CaptionStyleManager

logger = logging.getLogger(__name__)

class CaptionPresetManager:
    """Provides built-in presets and manages custom presets."""
    def __init__(self, style_manager: CaptionStyleManager) -> None:
        self.style_manager = style_manager
        self.presets: Dict[str, CaptionPreset] = {}
        self._initialize_default_presets()

    def _initialize_default_presets(self) -> None:
        # YouTube Shorts / TikTok style
        self.register_preset(CaptionPreset(
            preset_name="shorts_dynamic",
            style=CaptionStyle(
                font_family="Impact",
                font_size=72,
                color_hex="#FFFFFF",
                stroke_color_hex="#000000",
                stroke_width=3,
                animation_type="pop"
            ),
            max_words_per_segment=3,
            max_chars_per_segment=15,
            max_duration_sec=1.5
        ))
        
        # Standard Long Form
        self.register_preset(CaptionPreset(
            preset_name="standard",
            style=CaptionStyle(
                font_family="Arial",
                font_size=48,
                color_hex="#FFFFFF",
                stroke_width=2,
                animation_type="none"
            ),
            max_words_per_segment=8,
            max_chars_per_segment=45,
            max_duration_sec=4.0
        ))

    def register_preset(self, preset: CaptionPreset) -> None:
        self.presets[preset.preset_name] = preset
        logger.debug(f"Registered caption preset: {preset.preset_name}")

    def get_preset(self, name: str) -> CaptionPreset:
        return self.presets.get(name, self.presets.get("standard"))
