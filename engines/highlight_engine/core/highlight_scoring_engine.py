"""
Applies a weighted matrix to calculate highlight scores.
"""
import logging
from typing import List
from core.models.highlight_models import HighlightEvent, HighlightScore, HighlightConfig
from core.exceptions.highlight_exceptions import ScoringError

logger = logging.getLogger(__name__)

class HighlightScoringEngine:
    """Calculates scores for merged events using configurable weights."""
    
    def score_events(self, events: List[HighlightEvent], config: HighlightConfig) -> HighlightScore:
        """
        Calculates the score of a group of overlapping/merged events.
        Applies exponential bonus when multiple event types occur simultaneously.
        """
        if not events:
            return HighlightScore(0.0)
            
        try:
            total_score = 0.0
            components = {}
            unique_types = set()
            
            for event in events:
                weight = config.weights.get(event.event_type, 1.0)
                score = event.intensity * weight
                
                # Accumulate component breakdown
                components[event.event_type] = components.get(event.event_type, 0.0) + score
                total_score += score
                unique_types.add(event.event_type)
                
            # Stacking bonus: If motion AND audio spike at the same time, it's a higher quality highlight
            if len(unique_types) > 1:
                multiplier = 1.0 + (0.2 * (len(unique_types) - 1))
                total_score *= multiplier
                logger.debug(f"Applied stacking multiplier {multiplier}x for {len(unique_types)} unique event types.")
                
            return HighlightScore(total_score=round(total_score, 2), components=components)
        except Exception as e:
            raise ScoringError(f"Failed to score events: {e}") from e
