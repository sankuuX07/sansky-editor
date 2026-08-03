"""
Handles batch importing and bin organization.
"""
import logging
from core.models.premiere_models import ImportTask
from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from core.exceptions.premiere_exceptions import MediaImportError

logger = logging.getLogger(__name__)

class MediaImportService:
    """Batch imports files and organizes them into Premiere Bins."""
    def __init__(self, bridge: PremiereBridge) -> None:
        self.bridge = bridge

    def execute_import(self, task: ImportTask) -> None:
        logger.info(f"Executing batch import for {len(task.assets)} assets.")
        try:
            payload = {
                "createBins": task.create_bins_if_missing,
                "assets": [{"path": str(a.path), "bin": a.bin_path} for a in task.assets]
            }
            
            self.bridge.execute_script("batchImport", payload)
            logger.debug("Batch import completed successfully.")
        except Exception as e:
            raise MediaImportError(f"Failed to import media: {e}") from e
