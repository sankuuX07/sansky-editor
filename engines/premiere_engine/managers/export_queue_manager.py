"""
Manages rendering jobs.
"""
import logging
from core.models.premiere_models import ExportTask
from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from core.exceptions.premiere_exceptions import ExportQueueError

logger = logging.getLogger(__name__)

class ExportQueueManager:
    """Sends sequences to Adobe Media Encoder or Premiere internal renderer."""
    def __init__(self, bridge: PremiereBridge) -> None:
        self.bridge = bridge

    def queue_export(self, task: ExportTask) -> None:
        logger.info(f"Queueing export for sequence '{task.sequence.name}' to {task.output_path}")
        try:
            payload = {
                "sequenceId": task.sequence.sequence_id,
                "outputPath": str(task.output_path),
                "presetName": task.preset.name
            }
            self.bridge.execute_script("exportSequence", payload)
            task.status = "queued"
            logger.debug("Export queued successfully.")
        except Exception as e:
            task.status = "error"
            raise ExportQueueError(f"Failed to queue export: {e}") from e
