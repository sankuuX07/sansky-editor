"""
Imports Subtitles onto Premiere sequences.
"""
import logging
from pathlib import Path
from core.models.premiere_models import SequenceInfo
from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from core.exceptions.premiere_exceptions import MediaImportError

logger = logging.getLogger(__name__)

class CaptionImportService:
    """Takes generated subtitle files (SRT/VTT) and syncs them to the timeline."""
    def __init__(self, bridge: PremiereBridge) -> None:
        self.bridge = bridge

    def import_captions(self, sequence: SequenceInfo, caption_file: Path) -> None:
        logger.info(f"Importing captions from {caption_file} to sequence '{sequence.name}'")
        try:
            payload = {
                "sequenceId": sequence.sequence_id,
                "captionFilePath": str(caption_file)
            }
            
            self.bridge.execute_script("importCaptions", payload)
            logger.debug("Captions imported and synced successfully.")
        except Exception as e:
            raise MediaImportError(f"Failed to import captions: {e}") from e
