"""
Selects and ranks highlights.
"""
from typing import List
from pathlib import Path
import logging
from core.models.shorts_models import GeneratedClip, OutputSettings
import uuid

logger = logging.getLogger(__name__)

class HighlightSelectionManager:
    def select_highlights(self, raw_highlights: dict, video_path: Path, settings: OutputSettings) -> List[GeneratedClip]:
        logger.info(f"Selecting top {settings.max_shorts} highlights for {video_path.name}")
        
        timeline = raw_highlights.get("highlight_timeline")
        if not timeline or not timeline.highlights:
            logger.warning("No high-confidence highlights found in the timeline.")
            return []
            
        candidates = timeline.highlights
        
        valid = []
        for c in candidates:
            dur = c.end_time - c.start_time
            # Safely check score.total_score if c.score exists, else use 0.0
            score_val = c.score.total_score if c.score else 0.0
            
            if settings.min_clip_duration <= dur <= settings.max_clip_duration and score_val >= settings.highlight_threshold:
                valid.append((c, score_val))
                
        valid.sort(key=lambda x: x[1], reverse=True)
        selected = valid[:settings.max_shorts]
        
        clips = []
        for c, score_val in selected:
            clips.append(GeneratedClip(
                clip_id=str(uuid.uuid4()),
                source_video=video_path,
                start_time=c.start_time,
                end_time=c.end_time,
                score=score_val,
                semantic_type=c.semantic_type,
                events_contained=c.events_contained
            ))
            
        return clips
