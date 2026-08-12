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
            candidate.evidence = []
            speech_texts = []
            
            for e in candidate.events_contained:
                event_counts[e.event_type] = event_counts.get(e.event_type, 0) + 1
                if e.event_type == "speech_keyword":
                    speech_texts.append(getattr(e, "text", ""))
                    if "speech_detected" not in candidate.evidence:
                        candidate.evidence.append("speech_detected")
                if e.event_type == "gameplay_visual_evidence":
                    ev_type = getattr(e, "evidence_type", "visual_evidence")
                    if ev_type not in candidate.evidence:
                        candidate.evidence.append(ev_type)
                if e.event_type == "high_audio_intensity" and "sharp_audio_attack" not in candidate.evidence:
                    candidate.evidence.append("sharp_audio_attack")
                if e.event_type == "high_motion" and "high_visual_activity" not in candidate.evidence:
                    candidate.evidence.append("high_visual_activity")
            
            has_speech = event_counts.get("speech_keyword", 0) > 0
            has_motion = event_counts.get("high_motion", 0) > 0
            has_audio = event_counts.get("high_audio_intensity", 0) > 0
            has_visual = event_counts.get("gameplay_visual_evidence", 0) > 0
            
            duration = candidate.end_time - candidate.start_time
            event_density = len(candidate.events_contained) / (duration if duration > 0 else 1)
            
            is_clutch_speech = any("clutch" in text or "last guy" in text or "1 hp" in text or "one hp" in text for text in speech_texts)
            is_elim_speech = any("kill" in text or "knock" in text or "finish" in text or "got him" in text or "dead" in text for text in speech_texts)
            
            # Strict Fight classification: needs motion/audio + gameplay evidence or speech
            has_combat_signals = has_motion and has_audio
            has_gameplay_evidence = has_visual or is_elim_speech or is_clutch_speech
            
            # Heuristics
            if is_clutch_speech and has_combat_signals:
                candidate.semantic_type = EventType.CLUTCH.value
                candidate.confidence = 0.95
                candidate.reason = "Detected clutch keywords along with high action."
            elif has_visual and event_counts.get("gameplay_visual_evidence", 0) > 2 and duration > 20 and has_combat_signals:
                candidate.semantic_type = EventType.CLUTCH.value
                candidate.confidence = 0.90
                candidate.reason = "Sustained high intensity and multiple UI events over a long period."
            elif (is_elim_speech or (has_visual and "kill_feed_activity" in candidate.evidence)) and has_combat_signals:
                if event_counts.get("high_audio_intensity", 0) > 3 and event_counts.get("gameplay_visual_evidence", 0) > 2:
                    candidate.semantic_type = EventType.MULTI_KILL.value
                    candidate.confidence = 0.88
                    candidate.reason = "Multiple visual/audio events with elimination evidence."
                else:
                    candidate.semantic_type = EventType.ELIMINATION.value
                    candidate.confidence = 0.85
                    candidate.reason = "Elimination evidence combined with combat signals."
            elif has_combat_signals and has_gameplay_evidence:
                candidate.semantic_type = EventType.FIGHT.value
                candidate.confidence = 0.85
                candidate.reason = "Visual/audio combat signals validated by gameplay evidence."
            elif has_combat_signals and event_density > 1.0:
                # Still allow FIGHT if density is extremely high but no direct OCR/speech
                candidate.semantic_type = EventType.FIGHT.value
                candidate.confidence = 0.70
                candidate.reason = "Very high density of motion/audio overlap (weak evidence)."
            elif (has_motion and not has_audio) or (has_audio and not has_motion):
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
                candidate.reason = "Sparse or irrelevant events. Lack of gameplay evidence."
                
        return candidates
