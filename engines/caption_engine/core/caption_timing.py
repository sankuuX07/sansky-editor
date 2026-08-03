"""
Fixes overlaps and enforces timing constraints.
"""
import logging
from core.models.caption_models import CaptionTimeline

logger = logging.getLogger(__name__)

class CaptionTimingService:
    """Enforces timing integrity."""
    
    def adjust_timings(self, timeline: CaptionTimeline, min_duration_sec: float = 0.5) -> CaptionTimeline:
        """Prevent overlaps and enforce minimum duration."""
        logger.debug(f"Adjusting timings for timeline: {timeline.video_id}")
        
        for i in range(len(timeline.segments)):
            segment = timeline.segments[i]
            
            # Enforce minimum duration
            if segment.end_time - segment.start_time < min_duration_sec:
                segment.end_time = segment.start_time + min_duration_sec
                
            # Prevent overlap with next segment
            if i < len(timeline.segments) - 1:
                next_seg = timeline.segments[i+1]
                if segment.end_time > next_seg.start_time:
                    # Snap end time to next start time
                    segment.end_time = next_seg.start_time - 0.001
                    if segment.end_time < segment.start_time:
                        segment.end_time = segment.start_time # Fallback
                        
        return timeline
