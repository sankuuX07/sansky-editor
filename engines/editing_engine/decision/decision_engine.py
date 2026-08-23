"""
Generates editing decisions based on highlight evidence and style settings.
"""
import logging
from typing import List, Dict, Any
from core.models.shorts_models import GeneratedClip, OutputSettings
from core.models.editing_models import EditingTimeline, EditingEvent, EditingEventType

logger = logging.getLogger(__name__)

class EditingDecisionEngine:
    """Decides what effects to apply and when."""
    
    def generate_timeline(self, clip: GeneratedClip, settings: OutputSettings) -> EditingTimeline:
        logger.info(f"Generating editing decisions for clip {clip.clip_id}")
        timeline = EditingTimeline(clip_id=clip.clip_id)
        
        if not settings.auto_edit_enabled or settings.editing_style == "CLEAN":
            logger.debug("Auto edit disabled or CLEAN style. Using minimal editing.")
            return timeline
            
        style = settings.editing_style
        z_intensity = self._get_intensity_value(settings.zoom_intensity)
        s_intensity = self._get_intensity_value(settings.shake_intensity)
        
        events = clip.events_contained or []
        
        for ev in events:
            # Map events to editing decisions
            ev_type = getattr(ev, "event_type", "")
            
            # ELIMINATION / KNOCK popup -> SHAKE + IMPACT + FREEZE FRAME
            if ev_type == "gameplay_visual_evidence" and getattr(ev, "evidence_type", "") == "knock_popup_activity":
                if style in ["GAMING", "INTENSE"]:
                    timeline.editing_events.append(EditingEvent(
                        event_type=EditingEventType.SHAKE.value,
                        start_time=ev.start_time,
                        end_time=ev.start_time + 0.3,
                        intensity=s_intensity,
                        reason="Elimination/Knock event detected"
                    ))
                    timeline.editing_events.append(EditingEvent(
                        event_type=EditingEventType.IMPACT.value,
                        start_time=ev.start_time,
                        end_time=ev.start_time + 0.1,
                        intensity=1.0,
                        reason="Elimination visual emphasis"
                    ))
                if style in ["INTENSE", "CINEMATIC"]:
                    timeline.editing_events.append(EditingEvent(
                        event_type=EditingEventType.FREEZE_FRAME.value,
                        start_time=ev.start_time,
                        end_time=ev.start_time + 0.5,
                        intensity=1.0,
                        reason="Freeze frame for elimination"
                    ))
                    
            # CLUTCH / KILL Speech -> SLOW MOTION
            elif ev_type == "speech_keyword":
                text = getattr(ev, "text", "").lower()
                if "clutch" in text or "kill" in text:
                    if style in ["CINEMATIC", "INTENSE", "GAMING"]:
                        timeline.editing_events.append(EditingEvent(
                            event_type=EditingEventType.SLOW_MOTION.value,
                            start_time=ev.start_time,
                            end_time=ev.end_time + 1.0, # Extend slightly
                            intensity=0.5, # 0.5x speed
                            reason=f"Important speech: {text}"
                        ))
                        
            # HIGH MOTION / FIGHT START -> ZOOM + SPEED_RAMP
            elif ev_type == "high_motion":
                if style in ["GAMING", "CINEMATIC", "INTENSE"]:
                    # Ensure we don't overlap zooms too heavily
                    timeline.editing_events.append(EditingEvent(
                        event_type=EditingEventType.ZOOM.value,
                        start_time=ev.start_time,
                        end_time=ev.end_time + 1.0,
                        intensity=1.0 + (0.1 * z_intensity),
                        reason="Action sequence starting"
                    ))
                if style in ["INTENSE", "GAMING"]:
                    timeline.editing_events.append(EditingEvent(
                        event_type=EditingEventType.SPEED_RAMP.value,
                        start_time=max(clip.start_time, ev.start_time - 1.0),
                        end_time=ev.start_time,
                        intensity=2.0, # 2x speed for buildup
                        reason="Fast buildup to action"
                    ))
        
        # Deduplicate or resolve overlapping events
        timeline.editing_events = self._resolve_overlaps(timeline.editing_events)
        
        # Color Adjustment applies globally to the clip
        if settings.color_preset != "NATURAL":
            timeline.editing_events.append(EditingEvent(
                event_type=EditingEventType.COLOR_ADJUSTMENT.value,
                start_time=clip.start_time,
                end_time=clip.end_time,
                intensity=1.0,
                reason="Global color preset applied",
                parameters={"preset": settings.color_preset}
            ))

        return timeline
        
    def _get_intensity_value(self, intensity_str: str) -> float:
        mapping = {"LIGHT": 1.0, "MEDIUM": 2.0, "STRONG": 3.0}
        return mapping.get(intensity_str.upper(), 2.0)
        
    def _resolve_overlaps(self, events: List[EditingEvent]) -> List[EditingEvent]:
        # Simple overlap resolution: prefer the earliest event of the same type, ignore overlapping
        resolved = []
        events.sort(key=lambda x: x.start_time)
        for ev in events:
            overlap = False
            for r in resolved:
                if r.event_type == ev.event_type:
                    # Check if times overlap
                    if max(r.start_time, ev.start_time) < min(r.end_time, ev.end_time):
                        overlap = True
                        # merge end time
                        r.end_time = max(r.end_time, ev.end_time)
                        break
            if not overlap:
                resolved.append(ev)
        return resolved
