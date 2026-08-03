"""
Manages Export and Sequence presets for Premiere.
"""
import logging
from typing import Dict
from core.models.premiere_models import ExportPreset

logger = logging.getLogger(__name__)

class PresetManager:
    """Handles `.epr` (Export Preset) definitions."""
    def __init__(self) -> None:
        self.export_presets: Dict[str, ExportPreset] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        self.export_presets["youtube_1080p"] = ExportPreset(name="youtube_1080p")
        self.export_presets["shorts_1080p"] = ExportPreset(name="shorts_1080p")

    def get_export_preset(self, name: str) -> ExportPreset:
        if name not in self.export_presets:
            logger.warning(f"Export preset '{name}' not found. Falling back to default.")
            return self.export_presets.get("youtube_1080p")
        return self.export_presets[name]
