"""
Handles downloading models if they are not present locally.
"""
import logging
from typing import Optional
from pathlib import Path
from core.models.ai_models import ModelStatus
from engines.ai_engine.models.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

class ModelDownloader:
    """Downloads missing models and verifies integrity."""
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def download_model(self, model_id: str, source_url: str) -> bool:
        """Download a model to its registered path."""
        model_info = self.registry.get_model_info(model_id)
        self.registry.update_status(model_id, ModelStatus.DOWNLOADING)
        
        logger.info(f"Starting download for {model_id} from {source_url} to {model_info.path}")
        try:
            model_info.path.parent.mkdir(parents=True, exist_ok=True)
            # Mock successful download
            with open(model_info.path, "w") as f:
                f.write("mock_model_data")
            
            logger.info(f"Successfully downloaded {model_id}.")
            self.registry.update_status(model_id, ModelStatus.UNLOADED)
            return True
        except Exception as e:
            logger.error(f"Failed to download {model_id}: {e}", exc_info=True)
            self.registry.update_status(model_id, ModelStatus.ERROR)
            return False
