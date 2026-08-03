"""
Combines overlapping and nearby events into cohesive clips.
"""
import logging
from typing import List
from core.models.highlight_models import HighlightEvent, HighlightCandidate, HighlightConfig

logger = logging.getLogger(__name__)

class HighlightMerger:
    """Merges events that occur close to each other."""
    
    def merge(self, events: List[HighlightEvent], config: HighlightConfig) -> List[HighlightCandidate]:
        """Group nearby events into Candidates."""
        logger.info(f"Merging {len(events)} events using merge_distance: {config.merge_distance_sec}s")
        
        if not events:
            return []
            
        # Sort chronologically
        events.sort(key=lambda x: x.start_time)
        
        candidates = []
        current_cluster = [events[0]]
        current_start = events[0].start_time
        current_end = events[0].end_time
        
        for event in events[1:]:
            # If event starts within the merge distance from the end of the current cluster
            if event.start_time <= current_end + config.merge_distance_sec:
                current_cluster.append(event)
                current_end = max(current_end, event.end_time)
            else:
                # Close current cluster and start new one
                candidates.append(HighlightCandidate(
                    start_time=current_start,
                    end_time=current_end,
                    score=None, # Will be scored later
                    events_contained=current_cluster
                ))
                current_cluster = [event]
                current_start = event.start_time
                current_end = event.end_time
                
        # Append the final cluster
        if current_cluster:
            candidates.append(HighlightCandidate(
                start_time=current_start,
                end_time=current_end,
                score=None,
                events_contained=current_cluster
            ))
            
        logger.debug(f"Merged into {len(candidates)} candidates.")
        return candidates
