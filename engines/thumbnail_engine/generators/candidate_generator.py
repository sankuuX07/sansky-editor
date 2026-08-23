"""
Generates thumbnail candidate frames by targeting M6 highlight events.
"""
from typing import List
from core.models.shorts_models import GeneratedClip
from core.models.thumbnail_models import ThumbnailCandidate

class CandidateGenerator:
    def generate(self, clip: GeneratedClip) -> List[ThumbnailCandidate]:
        candidates = []
        
        # Priority mapping
        priority_map = {
            "elimination": 1.0,
            "high_motion": 0.8,
            "gameplay_visual_evidence": 0.7,
            "audio_peak": 0.5
        }
        
        if clip.events_contained:
            for ev in clip.events_contained:
                priority = priority_map.get(ev.event_type, 0.4)
                
                # We extract frames around the event timestamp (e.g. -1s, -0.5s, 0s, 0.5s, 1s)
                # to avoid the exact "kill" frame which might be blurry.
                offsets = [-1.0, -0.5, 0.0, 0.5, 1.0]
                
                for offset in offsets:
                    cand_ts = ev.timestamp + offset
                    # Ensure it's within clip bounds
                    if clip.start_time <= cand_ts <= clip.end_time:
                        candidates.append(ThumbnailCandidate(
                            timestamp=cand_ts,
                            event_priority=priority,
                            reason=ev.event_type.upper()
                        ))
                        
        # Fallback: if no candidates, just sample the middle and quarter points
        if not candidates:
            duration = clip.end_time - clip.start_time
            for offset_pct in [0.25, 0.5, 0.75]:
                cand_ts = clip.start_time + (duration * offset_pct)
                candidates.append(ThumbnailCandidate(
                    timestamp=cand_ts,
                    event_priority=0.1,
                    reason="FALLBACK_SAMPLING"
                ))
                
        return candidates
