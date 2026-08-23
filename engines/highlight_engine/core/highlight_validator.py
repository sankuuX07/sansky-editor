"""
Ensures highlight candidates are valid before export.
"""
import logging
from typing import List
from core.models.highlight_models import HighlightCandidate, HighlightConfig
from core.exceptions.highlight_exceptions import InvalidHighlightError

logger = logging.getLogger(__name__)

class HighlightValidator:
    """Validates structural integrity of highlight candidates."""
    
    def validate(self, candidates: List[HighlightCandidate], config: HighlightConfig) -> List[HighlightCandidate]:
        """Remove highlights that violate duration or integrity rules."""
        logger.debug(f"Validating {len(candidates)} candidates.")
        
        valid_candidates = []
        for c in candidates:
            duration = c.end_time - c.start_time
            
            if duration < config.min_clip_duration_sec:
                logger.debug(f"Rejecting clip: Duration {duration:.2f}s is less than {config.min_clip_duration_sec}s.")
                continue
                
            if duration > config.max_clip_duration_sec:
                logger.debug(f"Rejecting clip: Duration {duration:.2f}s exceeds {config.max_clip_duration_sec}s.")
                continue
                
            if c.start_time < 0 or c.end_time <= c.start_time:
                logger.warning(f"Rejecting corrupted clip: Invalid timestamps {c.start_time} - {c.end_time}.")
                continue
                
            from core.models.highlight_models import EventType
            if c.semantic_type in [EventType.DEAD_TIME.value, EventType.TRAVEL.value, EventType.LOOTING.value, EventType.LOW_ACTION.value]:
                logger.debug(f"Rejecting clip: Tagged as {c.semantic_type}.")
                continue
                
            valid_candidates.append(c)
            
        return valid_candidates
