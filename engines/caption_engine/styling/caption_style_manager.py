"""
Manages individual caption styles.
"""
import logging
from core.models.caption_models import CaptionStyle

logger = logging.getLogger(__name__)

class CaptionStyleManager:
    """Provides utilities for managing CaptionStyle configurations."""
    
    def get_default_style(self) -> CaptionStyle:
        return CaptionStyle()
        
    def merge_styles(self, base: CaptionStyle, override: CaptionStyle) -> CaptionStyle:
        """Merge two styles, taking overrides into account."""
        return CaptionStyle(
            font_family=override.font_family or base.font_family,
            font_size=override.font_size or base.font_size,
            color_hex=override.color_hex or base.color_hex,
            stroke_color_hex=override.stroke_color_hex or base.stroke_color_hex,
            stroke_width=override.stroke_width or base.stroke_width,
            shadow_color_hex=override.shadow_color_hex or base.shadow_color_hex,
            shadow_offset=override.shadow_offset or base.shadow_offset,
            alignment=override.alignment or base.alignment,
            margin_bottom=override.margin_bottom or base.margin_bottom,
            animation_type=override.animation_type or base.animation_type
        )
