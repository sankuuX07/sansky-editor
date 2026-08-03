"""
Caches generated captions to prevent redundant processing.
"""
import logging
from typing import Dict, Optional
from core.models.caption_models import CaptionTimeline

logger = logging.getLogger(__name__)

class CaptionCache:
    """In-memory cache for generated caption timelines."""
    def __init__(self) -> None:
        self._cache: Dict[str, CaptionTimeline] = {}

    def get_cached_timeline(self, video_id: str, preset_name: str) -> Optional[CaptionTimeline]:
        """Retrieve timeline if it was generated with the same preset."""
        cache_key = f"{video_id}_{preset_name}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]
        return None

    def store_timeline(self, timeline: CaptionTimeline) -> None:
        """Store a timeline in cache."""
        preset_name = timeline.preset_used.preset_name if timeline.preset_used else "default"
        cache_key = f"{timeline.video_id}_{preset_name}"
        self._cache[cache_key] = timeline
        logger.debug(f"Cached timeline for {cache_key}")

    def invalidate(self, video_id: str) -> None:
        """Clear all cached timelines for a specific video."""
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(f"{video_id}_")]
        for k in keys_to_delete:
            del self._cache[k]
        logger.debug(f"Invalidated cache for {video_id}")
