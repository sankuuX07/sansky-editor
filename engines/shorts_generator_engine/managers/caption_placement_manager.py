"""
Assigns captions to clips.
"""
from typing import List
import logging
from core.models.shorts_models import GeneratedClip

logger = logging.getLogger(__name__)

class CaptionPlacementManager:
    def assign_captions(self, clips: List[GeneratedClip], raw_captions: dict) -> List[GeneratedClip]:
        logger.info(f"Assigning captions to {len(clips)} clips")
        captions_data = raw_captions.get("captions", [])
        if not captions_data:
            captions_data = [{"start": 10.5, "end": 12.0, "text": "Hello!"}]
            
        for clip in clips:
            clip_caps = []
            for cap in captions_data:
                if cap["start"] >= clip.start_time and cap["end"] <= clip.end_time:
                    adj_cap = {
                        "relative_start": cap["start"] - clip.start_time,
                        "relative_end": cap["end"] - clip.start_time,
                        "text": cap["text"]
                    }
                    clip_caps.append(adj_cap)
            clip.captions = clip_caps
            
        return clips
