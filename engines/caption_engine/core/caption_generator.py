"""
Transforms raw transcription data into a CaptionTimeline.
"""
import logging
from typing import List, Dict, Any
from core.models.caption_models import CaptionTimeline, CaptionSegment, CaptionWord
from core.exceptions.caption_exceptions import CaptionGenerationError

logger = logging.getLogger(__name__)

class CaptionGenerator:
    """Generates CaptionTimeline from Whisper-like transcript dictionaries."""
    
    def generate_from_whisper(self, video_id: str, transcript_data: Dict[str, Any]) -> CaptionTimeline:
        """
        Parses transcript data containing text and segments/words.
        Assumes whisper format: {'text': '...', 'segments': [{'words': [{'word': 'Hello', 'start': 0.0, 'end': 0.5}], ...}]}
        """
        logger.info(f"Generating caption timeline for video {video_id}")
        timeline = CaptionTimeline(video_id=video_id)
        
        try:
            segments_data = transcript_data.get("segments", [])
            segment_idx = 1
            
            for seg in segments_data:
                words_data = seg.get("words", [])
                
                # If no word-level timestamps are provided, create a single-word segment block
                if not words_data:
                    timeline.segments.append(
                        CaptionSegment(
                            index=segment_idx,
                            text=seg.get("text", "").strip(),
                            start_time=seg.get("start", 0.0),
                            end_time=seg.get("end", 0.0)
                        )
                    )
                    segment_idx += 1
                    continue
                
                # Process word-level data
                caption_words = []
                for w in words_data:
                    caption_words.append(
                        CaptionWord(
                            text=w.get("word", "").strip(),
                            start_time=w.get("start", 0.0),
                            end_time=w.get("end", 0.0),
                            probability=w.get("probability", 1.0)
                        )
                    )
                
                if caption_words:
                    timeline.segments.append(
                        CaptionSegment(
                            index=segment_idx,
                            text=" ".join(w.text for w in caption_words),
                            start_time=caption_words[0].start_time,
                            end_time=caption_words[-1].end_time,
                            words=caption_words
                        )
                    )
                    segment_idx += 1

            return timeline
        except Exception as e:
            logger.error(f"Failed to generate captions: {e}", exc_info=True)
            raise CaptionGenerationError("Failed to parse transcript data.") from e
