"""
Assigns captions to clips.
"""
from typing import List
import logging
import copy
from core.models.shorts_models import GeneratedClip
from core.models.caption_models import CaptionTimeline, CaptionSegment

logger = logging.getLogger(__name__)

class CaptionPlacementManager:
    def assign_captions(self, clips: List[GeneratedClip], raw_captions: dict) -> List[GeneratedClip]:
        logger.info(f"Assigning captions to {len(clips)} clips")
        
        timeline: CaptionTimeline = raw_captions.get("caption_timeline")
        if not timeline or not timeline.segments:
            logger.warning("No caption timeline provided. Clips will have no captions.")
            return clips
            
        emphasis_keywords = ["clutch", "kill", "knock", "finish", "last guy", "one hp", "let's go", "no way"]
            
        for clip in clips:
            clip_caps = []
            
            for seg in timeline.segments:
                # Check if the segment overlaps with the clip
                if max(seg.start_time, clip.start_time) < min(seg.end_time, clip.end_time):
                    # Deep copy the segment because we will modify its relative timestamps
                    adj_seg = copy.deepcopy(seg)
                    
                    # Shift segment times
                    adj_seg.start_time = max(0.0, adj_seg.start_time - clip.start_time)
                    adj_seg.end_time = min(clip.end_time - clip.start_time, adj_seg.end_time - clip.start_time)
                    
                    # Check for emphasis words
                    for word in adj_seg.words:
                        # Shift word times
                        word.start_time = max(0.0, word.start_time - clip.start_time)
                        word.end_time = min(clip.end_time - clip.start_time, word.end_time - clip.start_time)
                        
                        clean_word = "".join(c for c in word.text.lower() if c.isalnum())
                        if any(k in clean_word for k in emphasis_keywords) or any(k in adj_seg.text.lower() for k in emphasis_keywords):
                            word.is_emphasized = True
                            
                        # Also emphasize if the word overlaps with an intense highlight event
                        if not word.is_emphasized and clip.events_contained:
                            for ev in clip.events_contained:
                                ev_type = getattr(ev, "event_type", "")
                                if ev_type in ["gameplay_visual_evidence", "high_motion", "speech_keyword"]:
                                    if max(ev.start_time - clip.start_time, word.start_time) < min(ev.end_time - clip.start_time, word.end_time):
                                        word.is_emphasized = True
                                        break
                                        
                    clip_caps.append(adj_seg)
                    
            clip.captions = clip_caps
            
        return clips
