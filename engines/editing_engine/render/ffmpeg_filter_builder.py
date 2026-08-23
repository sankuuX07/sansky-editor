"""
Converts an EditingTimeline into an FFmpeg filtergraph.
"""
import logging
from typing import List, Tuple
from core.models.editing_models import EditingTimeline, EditingEventType

logger = logging.getLogger(__name__)

class FFmpegFilterBuilder:
    def build_filter(self, timeline: EditingTimeline, clip_start: float) -> Tuple[List[str], List[str]]:
        """
        Builds video (-vf) and audio (-af) filters.
        Returns a tuple of (video_filters, audio_filters).
        Uses simple chaining since multiple complex filters on the same stream can be tricky.
        """
        video_filters = []
        audio_filters = []
        
        for ev in timeline.editing_events:
            # Shift event times relative to the clip start
            rel_start = max(0.0, ev.start_time - clip_start)
            rel_end = max(0.0, ev.end_time - clip_start)
            
            if ev.event_type == EditingEventType.ZOOM.value:
                # Dynamic zoom: we use the zoompan filter. We apply it only between rel_start and rel_end.
                # Since zoompan changes framerate and resolution, we need to be careful.
                # A safer approach for a dynamic zoom in a simple filterchain is cropping and scaling,
                # but 'zoompan' is the standard way.
                # Because zoompan affects the whole video if not bounded, we use the `enable` option if supported,
                # but zoompan doesn't support timeline editing natively in all versions.
                # Alternatively, a simple scale + crop based on time.
                zoom_factor = min(1.5, 1.0 + (0.1 * ev.intensity))
                # Using a safe crop based zoom for the specific time window
                vf = f"crop=iw/{zoom_factor}:ih/{zoom_factor}:(iw-iw/{zoom_factor})/2:(ih-ih/{zoom_factor})/2:enable='between(t,{rel_start},{rel_end})',scale=iw*1.0:ih*1.0"
                video_filters.append(vf)
                
            elif ev.event_type == EditingEventType.SHAKE.value:
                # Shake effect using crop and offset
                intensity = ev.intensity * 10
                vf = f"crop=iw-{intensity*2}:ih-{intensity*2}:(iw-out_w)/2+((sin(t*20)*{intensity})):(ih-out_h)/2+((cos(t*15)*{intensity})):enable='between(t,{rel_start},{rel_end})',scale=iw*1.0:ih*1.0"
                video_filters.append(vf)
                
                # We don't apply slow motion here anymore, it's handled via segments
                pass
                
            elif ev.event_type == EditingEventType.SPEED_RAMP.value:
                # Speed ramp handled via segments
                pass
                
            elif ev.event_type == EditingEventType.FREEZE_FRAME.value:
                # Freeze frame handled via segments
                pass
                
            elif ev.event_type == EditingEventType.IMPACT.value:
                # Short flash / brightness burst
                vf = f"eq=brightness=0.3:enable='between(t,{rel_start},{rel_end})'"
                video_filters.append(vf)
                
            elif ev.event_type == EditingEventType.COLOR_ADJUSTMENT.value:
                preset = ev.parameters.get("preset", "NATURAL")
                if preset == "VIBRANT":
                    video_filters.append("eq=saturation=1.5:contrast=1.1")
                elif preset == "CINEMATIC":
                    video_filters.append("eq=saturation=0.9:contrast=1.2")
                elif preset == "GAMING":
                    video_filters.append("eq=saturation=1.3:contrast=1.2:brightness=0.05")
                    
        return video_filters, audio_filters

    def get_time_warp_segments(self, timeline: EditingTimeline, clip_start: float, clip_end: float) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries defining how to slice the clip into micro-segments.
        Each dict has: {'start': float, 'end': float, 'type': str, 'speed': float}
        """
        warp_events = []
        for ev in timeline.editing_events:
            if ev.event_type in [EditingEventType.SLOW_MOTION.value, EditingEventType.SPEED_RAMP.value, EditingEventType.FREEZE_FRAME.value]:
                warp_events.append(ev)
                
        if not warp_events:
            return [{'start': clip_start, 'end': clip_end, 'type': 'NORMAL', 'speed': 1.0}]
            
        warp_events.sort(key=lambda x: x.start_time)
        
        segments = []
        current_time = clip_start
        
        for ev in warp_events:
            ev_start = max(clip_start, ev.start_time)
            ev_end = min(clip_end, ev.end_time)
            
            if ev_start > current_time:
                # Normal segment before the warp
                segments.append({'start': current_time, 'end': ev_start, 'type': 'NORMAL', 'speed': 1.0})
                
            if ev_start < ev_end:
                speed = 1.0
                if ev.event_type == EditingEventType.SLOW_MOTION.value:
                    speed = 0.5
                elif ev.event_type == EditingEventType.SPEED_RAMP.value:
                    speed = 2.0
                elif ev.event_type == EditingEventType.FREEZE_FRAME.value:
                    speed = 0.01 # Extremely slow for freeze frame effect
                    
                segments.append({'start': ev_start, 'end': ev_end, 'type': ev.event_type, 'speed': speed})
                current_time = ev_end
                
        if current_time < clip_end:
            segments.append({'start': current_time, 'end': clip_end, 'type': 'NORMAL', 'speed': 1.0})
            
        return segments
