"""
The Caption Engine facade.
"""
import logging
from typing import Dict, Any, Optional
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError
from core.models.caption_models import CaptionTimeline, CaptionExportSettings, CaptionPreset

from engines.caption_engine.core.caption_generator import CaptionGenerator
from engines.caption_engine.core.caption_segmenter import CaptionSegmenter
from engines.caption_engine.core.caption_timing import CaptionTimingService
from engines.caption_engine.core.caption_validator import CaptionValidator
from engines.caption_engine.styling.caption_style_manager import CaptionStyleManager
from engines.caption_engine.styling.caption_preset_manager import CaptionPresetManager
from engines.caption_engine.export.caption_formatter import CaptionFormatter
from engines.caption_engine.export.caption_exporter import CaptionExporter
from engines.caption_engine.cache.caption_cache import CaptionCache

class CaptionEngine(BaseEngine):
    """Facade for the Caption generation subsystem."""
    def __init__(self) -> None:
        super().__init__("caption_engine")
        
        self.generator = CaptionGenerator()
        self.segmenter = CaptionSegmenter()
        self.timing_service = CaptionTimingService()
        self.validator = CaptionValidator()
        
        self.style_manager = CaptionStyleManager()
        self.preset_manager = CaptionPresetManager(self.style_manager)
        
        self.formatter = CaptionFormatter()
        self.exporter = CaptionExporter(self.formatter)
        
        self.cache = CaptionCache()

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Caption Engine...")
        try:
            self._status = EngineStatus.INITIALIZED
            self.is_initialized = True
            self.logger.info("Caption Engine initialized successfully.")
        except Exception as e:
            self._status = EngineStatus.ERROR
            raise EngineInitError("Failed to initialize CaptionEngine") from e

    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized CaptionEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Caption Engine started.")

    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Caption Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Caption Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING

    def process_transcript(self, video_id: str, transcript_data: Dict[str, Any], preset_name: str = "standard") -> CaptionTimeline:
        """Full pipeline: Generate -> Segment -> Time -> Validate -> Cache."""
        
        cached = self.cache.get_cached_timeline(video_id, preset_name)
        if cached:
            return cached
            
        preset = self.preset_manager.get_preset(preset_name)
        
        timeline = self.generator.generate_from_whisper(video_id, transcript_data)
        timeline.preset_used = preset
        
        timeline = self.segmenter.apply_segmentation(timeline, preset)
        timeline = self.timing_service.adjust_timings(timeline)
        
        validation_result = self.validator.validate(timeline)
        if not validation_result.is_valid:
            self.logger.warning(f"Caption validation failed: {validation_result.errors}")
            
        self.cache.store_timeline(timeline)
        
        return timeline
        
    def export_captions(self, timeline: CaptionTimeline, settings: CaptionExportSettings) -> None:
        """Export timeline via Exporter."""
        self.exporter.export(timeline, settings)
