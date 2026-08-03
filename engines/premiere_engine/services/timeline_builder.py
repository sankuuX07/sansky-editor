"""
Arranges clips onto the Premiere Sequence.
"""
import logging
from typing import List
from core.models.premiere_models import SequenceInfo, TimelineClip
from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from core.exceptions.premiere_exceptions import TimelineError

logger = logging.getLogger(__name__)

class TimelineBuilder:
    """Takes abstract clip data and places it onto a specific sequence."""
    def __init__(self, bridge: PremiereBridge) -> None:
        self.bridge = bridge

    def build_timeline(self, sequence: SequenceInfo, clips: List[TimelineClip]) -> None:
        logger.info(f"Building timeline '{sequence.name}' with {len(clips)} clips.")
        try:
            clip_data = []
            for c in clips:
                clip_data.append({
                    "assetPath": str(c.asset_path),
                    "startTime": c.start_time,
                    "endTime": c.end_time,
                    "trackType": c.track_type,
                    "trackIndex": c.track_index
                })
                
            payload = {
                "sequenceId": sequence.sequence_id,
                "clips": clip_data
            }
            
            self.bridge.execute_script("buildTimeline", payload)
            logger.debug("Timeline built successfully.")
        except Exception as e:
            raise TimelineError(f"Failed to build timeline: {e}") from e
