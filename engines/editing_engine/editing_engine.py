"""
Editing Engine Facade.
"""
import logging
from typing import List, Tuple
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.models.shorts_models import GeneratedClip, OutputSettings
from engines.editing_engine.decision.decision_engine import EditingDecisionEngine
from engines.editing_engine.render.ffmpeg_filter_builder import FFmpegFilterBuilder

class EditingEngine(BaseEngine):
    """Facade for the Professional Automatic Video Editing subsystem."""
    
    def __init__(self) -> None:
        super().__init__("editing_engine")
        self.decision_engine = EditingDecisionEngine()
        self.filter_builder = FFmpegFilterBuilder()
        
    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Editing Engine...")
        self._status = EngineStatus.INITIALIZED
        self.is_initialized = True
        self.logger.info("Editing Engine initialized successfully.")

    def start(self) -> None:
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Editing Engine started.")

    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Editing Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Editing Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING
        
    def generate_editing_decisions(self, clips: List[GeneratedClip], settings: OutputSettings) -> None:
        """Populates the editing_timeline property of each clip."""
        for clip in clips:
            timeline = self.decision_engine.generate_timeline(clip, settings)
            clip.editing_timeline = timeline
            
    def build_ffmpeg_filters(self, clip: GeneratedClip) -> Tuple[str, str]:
        """Returns (video_filter_string, audio_filter_string)."""
        if not clip.editing_timeline:
            return "", ""
        
        vf_list, af_list = self.filter_builder.build_filter(clip.editing_timeline, clip.start_time)
        
        vf_str = ",".join(vf_list) if vf_list else ""
        af_str = ",".join(af_list) if af_list else ""
        
        return vf_str, af_str
