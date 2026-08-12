import logging
from typing import List
from core.models.highlight_models import HighlightCandidate, HighlightConfig, EventType

logger = logging.getLogger(__name__)

class SemanticClassifier:
    """Classifies HighlightCandidates into semantic event types based on grouped signals."""
    
    def classify(self, candidates: List[HighlightCandidate], config: HighlightConfig) -> List[HighlightCandidate]:
        logger.info(f"Classifying {len(candidates)} candidates.")
        for candidate in candidates:
            event_counts = {}
            for e in candidate.events_contained:
                event_counts[e.event_type] = event_counts.get(e.event_type, 0) + 1
            
            has_speech = event_counts.get("speech_keyword", 0) > 0
            has_motion = event_counts.get("high_motion", 0) > 0
            has_audio = event_counts.get("high_audio_intensity", 0) > 0
            
            speech_texts = []
            for e in candidate.events_contained:
                if e.event_type == "speech_keyword":
                    speech_texts.append(getattr(e, "text", ""))
            
            duration = candidate.end_time - candidate.start_time
            event_density = len(candidate.events_contained) / (duration if duration > 0 else 1)
            
            is_clutch_speech = any("clutch" in text or "last guy" in text or "1 hp" in text or "one hp" in text for text in speech_texts)
            is_elim_speech = any("kill" in text or "knock" in text or "finish" in text or "got him" in text for text in speech_texts)
            
            # Heuristics
            if is_clutch_speech and (has_motion or has_audio):
                candidate.semantic_type = EventType.CLUTCH.value
                candidate.confidence = 0.95
                candidate.reason = "Detected clutch keywords along with high action."
            elif is_elim_speech and has_motion and has_audio:
                if event_counts.get("high_audio_intensity", 0) > 3 and event_counts.get("high_motion", 0) > 3:
                    candidate.semantic_type = EventType.MULTI_KILL.value
                    candidate.confidence = 0.85
                    candidate.reason = "Multiple high intensity events with elimination keywords."
                else:
                    candidate.semantic_type = EventType.ELIMINATION.value
                    candidate.confidence = 0.85
                    candidate.reason = "Elimination keywords with combat signals."
            elif has_motion and has_audio and event_density > 0.5:
                # Dense action without explicit keywords
                candidate.semantic_type = EventType.FIGHT.value
                candidate.confidence = 0.8
                candidate.reason = "High density of motion and loud audio overlap."
            elif (has_motion and not has_audio) or (has_audio and not has_motion):
                # Sparse or uncoupled events
                if duration > 10.0:
                    candidate.semantic_type = EventType.TRAVEL.value
                    candidate.confidence = 0.6
                    candidate.reason = "Prolonged single-signal activity."
                else:
                    candidate.semantic_type = EventType.DEAD_TIME.value
                    candidate.confidence = 0.9
                    candidate.reason = "Brief or uncoupled activity not indicative of a fight."
            else:
                candidate.semantic_type = EventType.DEAD_TIME.value
                candidate.confidence = 0.95
                candidate.reason = "Sparse or irrelevant events."
                
        return candidates
