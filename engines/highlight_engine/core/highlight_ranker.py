"""
Sorts and filters highlight candidates by score.
"""
import logging
from typing import List
from core.models.highlight_models import HighlightCandidate, HighlightConfig

logger = logging.getLogger(__name__)

class HighlightRanker:
    """Sorts highlights to find the best moments."""
    
    def rank(self, candidates: List[HighlightCandidate], config: HighlightConfig, top_n: int = 5) -> List[HighlightCandidate]:
        """Filter by threshold and sort descending by score."""
        logger.debug(f"Ranking {len(candidates)} candidates.")
        
        # Filter by threshold
        filtered = [c for c in candidates if c.score and c.score.total_score >= config.score_threshold]
        
        # Sort descending
        filtered.sort(key=lambda x: x.score.total_score, reverse=True)
        
        # Return top N
        return filtered[:top_n]
