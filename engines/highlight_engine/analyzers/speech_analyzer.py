import logging
from typing import List
from pathlib import Path
from core.models.highlight_models import SpeechEvent
from core.dependency_injection.container import container
from app.services.engine_manager import EngineManager

logger = logging.getLogger(__name__)

# Game-specific keywords that often indicate high action or a highlight
GAMEPLAY_KEYWORDS = [
    "clutch", "one hp", "1 hp", "knocked", "knock", "finish him", 
    "last guy", "one more", "let's go", "chicken dinner", "dead",
    "kill", "nice", "got him", "he's low"
]

class SpeechAnalyzer:
    """Uses AIEngine to transcribe audio and detect gameplay-related keywords."""
    def analyze(self, audio_path: Path) -> List[SpeechEvent]:
        logger.info(f"Starting speech analysis on {audio_path}")
        events = []
        try:
            engine_manager = container.resolve(EngineManager)
            ai_engine = engine_manager.get_engine("ai_engine")
            
            transcript_data = ai_engine.transcribe(str(audio_path))
            
            segments = transcript_data.get("segments", [])
            for segment in segments:
                text = segment.get("text", "").lower()
                start = segment.get("start", 0.0)
                end = segment.get("end", 0.0)
                
                # Check for keywords
                matched_keywords = [kw for kw in GAMEPLAY_KEYWORDS if kw in text]
                if matched_keywords:
                    intensity = min(1.0, len(matched_keywords) * 0.5) # Scale intensity based on number of keywords
                    events.append(SpeechEvent(
                        start_time=start,
                        end_time=end,
                        intensity=intensity,
                        text=text
                    ))
            
            logger.debug(f"Detected {len(events)} speech events containing gameplay keywords.")
            return events
        except Exception as e:
            logger.error(f"Speech analysis failed, continuing without speech events: {e}")
            return events
