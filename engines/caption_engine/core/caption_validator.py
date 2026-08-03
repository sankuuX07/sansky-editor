"""
Validates the structural integrity of CaptionTimelines.
"""
import logging
from core.models.caption_models import CaptionTimeline, CaptionValidationResult
from core.exceptions.caption_exceptions import CaptionValidationError

logger = logging.getLogger(__name__)

class CaptionValidator:
    """Validates captions before export."""
    
    def validate(self, timeline: CaptionTimeline) -> CaptionValidationResult:
        """Runs checks and returns validation results."""
        logger.debug(f"Validating timeline: {timeline.video_id}")
        errors = []
        
        if not timeline.segments:
            errors.append("Timeline has no segments.")
            return CaptionValidationResult(is_valid=False, errors=errors)
            
        for i, seg in enumerate(timeline.segments):
            if not seg.text.strip():
                errors.append(f"Segment {seg.index} is empty.")
                
            if seg.start_time < 0 or seg.end_time < 0:
                errors.append(f"Segment {seg.index} has negative timestamps.")
                
            if seg.end_time <= seg.start_time:
                errors.append(f"Segment {seg.index} has invalid duration (end <= start).")
                
            if i < len(timeline.segments) - 1:
                next_seg = timeline.segments[i+1]
                if seg.end_time > next_seg.start_time:
                    errors.append(f"Segment {seg.index} overlaps with segment {next_seg.index}.")
                    
        is_valid = len(errors) == 0
        if not is_valid:
            logger.warning(f"Validation failed for {timeline.video_id}: {errors}")
            
        return CaptionValidationResult(is_valid=is_valid, errors=errors)
