"""
Applies a weighted matrix to calculate highlight scores.
"""
import logging
from typing import List
from core.models.highlight_models import HighlightCandidate, HighlightScore, HighlightConfig
from core.exceptions.highlight_exceptions import ScoringError

logger = logging.getLogger(__name__)

class HighlightScoringEngine:
    """Calculates scores for candidates using configurable weights and semantic types."""
    
    def score_candidate(self, candidate: HighlightCandidate, config: HighlightConfig) -> HighlightScore:
        """
        Calculates the score of a candidate based on contained events and its semantic type.
        """
        if not candidate.events_contained and not candidate.semantic_type:
            return HighlightScore(0.0)
            
        try:
            total_score = 0.0
            components = {}
            unique_types = set()
            
            # 1. Score individual events
            for event in candidate.events_contained:
                weight = config.weights.get(event.event_type, 1.0)
                score = event.intensity * weight
                
                components[event.event_type] = components.get(event.event_type, 0.0) + score
                total_score += score
                unique_types.add(event.event_type)
                
            # 2. Add semantic type bonus/penalty
            if candidate.semantic_type:
                semantic_weight = config.weights.get(candidate.semantic_type, 0.0)
                semantic_score = candidate.confidence * semantic_weight
                components[candidate.semantic_type] = semantic_score
                total_score += semantic_score
                
            # Stacking bonus for diverse events
            if len(unique_types) > 1:
                multiplier = 1.0 + (0.2 * (len(unique_types) - 1))
                total_score *= multiplier
                logger.debug(f"Applied stacking multiplier {multiplier}x for {len(unique_types)} unique event types.")
                
            return HighlightScore(total_score=round(total_score, 2), components=components)
        except Exception as e:
            raise ScoringError(f"Failed to score candidate: {e}") from e
