"""
The Composition Engine Facade and Decision logic.
"""
import logging
from typing import Optional
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.models.shorts_models import GeneratedClip, OutputSettings
from core.models.composition_models import CompositionTimeline, CompositionEvent
from core.exceptions.exceptions import EngineInitError

logger = logging.getLogger(__name__)

class CompositionDecisionEngine:
    def generate_timeline(self, clip: GeneratedClip, settings: OutputSettings) -> CompositionTimeline:
        timeline = CompositionTimeline(
            clip_id=clip.clip_id,
            target_aspect_ratio=settings.target_aspect_ratio,
            target_resolution=settings.output_resolution,
            layout=settings.facecam_layout
        )
        
        # Determine focus based on semantics/events
        # Since we don't have bounding boxes, we use a stable fallback by default,
        # but if we have high_motion or gameplay_visual_evidence, we can schedule an action event.
        
        has_action = False
        if clip.events_contained:
            has_action = any(e.event_type in ["gameplay_visual_evidence", "high_motion"] for e in clip.events_contained)
            
        if has_action and settings.composition_style == "ACTION":
            # Schedule action focus
            timeline.events.append(CompositionEvent(
                start_time=0.0,
                end_time=clip.end_time - clip.start_time,
                focus_region="ACTION",
                fallback_used=False,
                reason="HIGH_ACTION_REGION"
            ))
        else:
            # Fallback
            timeline.events.append(CompositionEvent(
                start_time=0.0,
                end_time=clip.end_time - clip.start_time,
                focus_region="CENTER",
                fallback_used=True,
                reason="STABLE_FALLBACK"
            ))
            
        return timeline

class CompositionEngine(BaseEngine):
    def __init__(self) -> None:
        super().__init__("composition_engine")
        self.decision_engine = CompositionDecisionEngine()
        
    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Composition Engine...")
        self._status = EngineStatus.INITIALIZED
        self.is_initialized = True
        self.logger.info("Composition Engine initialized successfully.")
        
    def start(self) -> None:
        self._status = EngineStatus.RUNNING
        self.is_running = True
        
    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        
    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        
    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING
        
    def build_ffmpeg_filters(self, clip: GeneratedClip, settings: OutputSettings) -> tuple[str, CompositionTimeline]:
        """
        Builds the base FFmpeg scale/crop filters for M10.
        Returns (vf_str, timeline).
        """
        timeline = self.decision_engine.generate_timeline(clip, settings)
        
        if settings.target_aspect_ratio == "16:9":
            # No base crop needed, just scale if necessary
            return "", timeline
            
        # For 9:16 vertical shorts
        if settings.target_aspect_ratio == "9:16":
            w, h = settings.output_resolution.split('x')
            out_w, out_h = int(w), int(h)
            
            # The crop is applied to the original video (usually 16:9 like 1920x1080)
            # Crop to 9:16 aspect ratio. For a 1920x1080 video, this is crop=607:1080
            # Instead of hardcoding 1920x1080, we use ih*9/16 for width, ih for height.
            # Center crop coordinates: x=(iw-ow)/2, y=0
            
            # Since we just want a stable center crop as fallback:
            crop_expr = "crop=ih*9/16:ih"
            
            # Smooth tracking simulation:
            # We use FFmpeg's `lerp` if we wanted to animate x/y over time. 
            # But since we're using a single stable "center of gravity" per clip to avoid jitter:
            crop_expr += ":(iw-ow)/2:0" 
            
            # Finally scale to requested output resolution
            scale_expr = f"scale={out_w}:{out_h}"
            
            vf_str = f"{crop_expr},{scale_expr}"
            
            # If facecam layout is enabled (e.g. FACE_CAM_TOP)
            # We would build a complex filtergraph, but for a simple filterchain returning a string,
            # we rely on the primary gameplay crop. Real multi-stream facecam requires complex graphs.
            return vf_str, timeline
            
        # For 1:1 Square
        if settings.target_aspect_ratio == "1:1":
            w, h = settings.output_resolution.split('x')
            crop_expr = "crop=ih:ih:(iw-ow)/2:0"
            scale_expr = f"scale={w}:{h}"
            return f"{crop_expr},{scale_expr}", timeline
            
        return "", timeline
