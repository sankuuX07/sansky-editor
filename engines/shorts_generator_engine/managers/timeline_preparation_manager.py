"""
Prepares timeline definitions.
"""
import logging
from typing import List
from core.models.shorts_models import GeneratedClip, TimelineDefinition, OutputSettings

logger = logging.getLogger(__name__)

class TimelinePreparationManager:
    def prepare_timeline(self, clips: List[GeneratedClip], settings: OutputSettings) -> TimelineDefinition:
        logger.info("Preparing timeline definition")
        return TimelineDefinition(
            clips=clips,
            resolution=settings.output_resolution,
            framerate=60.0
        )
