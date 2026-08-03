"""
Manages Sequences (Timelines) within a Premiere Project.
"""
import logging
from core.models.premiere_models import SequenceInfo
from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from core.exceptions.premiere_exceptions import SequenceCreationError

logger = logging.getLogger(__name__)

class SequenceManager:
    """Handles creating and configuring sequences."""
    def __init__(self, bridge: PremiereBridge) -> None:
        self.bridge = bridge

    def create_sequence(self, name: str, width: int = 1920, height: int = 1080, framerate: float = 60.0) -> SequenceInfo:
        logger.info(f"Creating Sequence '{name}' ({width}x{height} @ {framerate}fps)")
        try:
            payload = {
                "name": name,
                "width": width,
                "height": height,
                "framerate": framerate
            }
            response = self.bridge.execute_script("createSequence", payload)
            
            seq_id = response.get("sequenceId", "sim_seq_123")
            return SequenceInfo(name=name, width=width, height=height, framerate=framerate, sequence_id=seq_id)
        except Exception as e:
            raise SequenceCreationError(f"Failed to create sequence: {e}") from e
