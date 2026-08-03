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
        
        candidates = raw_highlights.get("candidates", [])
        if not candidates:
            candidates = [{"start": 10.0, "end": 40.0, "score": 0.95}, {"start": 100.0, "end": 140.0, "score": 0.85}]
            
        valid = []
        for c in candidates:
            dur = c["end"] - c["start"]
            if settings.min_clip_duration <= dur <= settings.max_clip_duration and c["score"] >= settings.highlight_threshold:
                valid.append(c)
                
        valid.sort(key=lambda x: x["score"], reverse=True)
        selected = valid[:settings.max_shorts]
        
        clips = []
        for s in selected:
            clips.append(GeneratedClip(
                clip_id=str(uuid.uuid4()),
                source_video=video_path,
                start_time=s["start"],
                end_time=s["end"],
                score=s["score"]
            ))
            
        return clips
