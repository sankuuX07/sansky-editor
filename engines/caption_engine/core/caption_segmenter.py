"""
Intelligently splits long captions based on limits.
"""
import logging
from core.models.caption_models import CaptionTimeline, CaptionSegment, CaptionPreset

logger = logging.getLogger(__name__)

class CaptionSegmenter:
    """Splits long segments based on preset constraints."""
    
    def apply_segmentation(self, timeline: CaptionTimeline, preset: CaptionPreset) -> CaptionTimeline:
        """Splits segments exceeding word or character limits."""
        logger.info(f"Applying segmentation rules for {timeline.video_id} using preset '{preset.preset_name}'")
        
        new_segments = []
        seg_index = 1
        
        for segment in timeline.segments:
            # If no word level data, we can't split safely, keep as is
            if not segment.words:
                segment.index = seg_index
                new_segments.append(segment)
                seg_index += 1
                continue
                
            current_words = []
            current_chars = 0
            
            for word in segment.words:
                word_len = len(word.text) + 1 # +1 for space
                
                if (len(current_words) >= preset.max_words_per_segment or 
                    current_chars + word_len > preset.max_chars_per_segment):
                    
                    # Cut and commit current batch
                    if current_words:
                        new_segments.append(
                            CaptionSegment(
                                index=seg_index,
                                text=" ".join(w.text for w in current_words),
                                start_time=current_words[0].start_time,
                                end_time=current_words[-1].end_time,
                                words=current_words
                            )
                        )
                        seg_index += 1
                        current_words = []
                        current_chars = 0
                
                current_words.append(word)
                current_chars += word_len
                
            # Commit remainder
            if current_words:
                new_segments.append(
                    CaptionSegment(
                        index=seg_index,
                        text=" ".join(w.text for w in current_words),
                        start_time=current_words[0].start_time,
                        end_time=current_words[-1].end_time,
                        words=current_words
                    )
                )
                seg_index += 1
                
        timeline.segments = new_segments
        return timeline
