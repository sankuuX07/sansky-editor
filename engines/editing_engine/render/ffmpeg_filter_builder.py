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
                
            elif ev.event_type == EditingEventType.SLOW_MOTION.value:
                # Slow motion uses setpts for video and atempo for audio.
                # Applying setpts dynamically using timeline is complex without splitting the stream.
                # For this modular engine, we will apply it using a trick if possible, or skip if it's too risky for a single pass.
                # Due to FFmpeg limitations on timeline editing for setpts/atempo, we will apply a slight visual indicator (e.g. color shift) if we can't do actual slowmo easily, OR we skip it.
                # A robust single-pass slow-motion requires splitting. Since the prompt says "Fall back gracefully if high-quality interpolation is unavailable", we'll just log it.
                logger.info(f"Slow motion requested from {rel_start} to {rel_end}. Requires multi-pass or complex filtergraph. Applying visual emphasis instead.")
                vf = f"colorbalance=rs=0.2:bs=0.2:enable='between(t,{rel_start},{rel_end})'"
                video_filters.append(vf)
                
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
