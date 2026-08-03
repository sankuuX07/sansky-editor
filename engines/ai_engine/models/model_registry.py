"""
Model Registry for tracking known and downloaded models.
"""
import logging
from typing import Dict, List, Optional
from core.models.ai_models import ModelInfo, ModelStatus
from core.exceptions.ai_exceptions import ModelNotFoundError

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Maintains a database of all AI models known to the system."""
    def __init__(self) -> None:
        self._models: Dict[str, ModelInfo] = {}

    def register(self, model_info: ModelInfo) -> None:
        """Register a model's metadata."""
        self._models[model_info.model_id] = model_info
        logger.info(f"Registered model info: {model_info.model_id}")

    def get_model_info(self, model_id: str) -> ModelInfo:
        """Retrieve metadata for a model."""
        if model_id not in self._models:
            raise ModelNotFoundError(f"Model {model_id} is not registered in the system.")
        return self._models[model_id]

    def update_status(self, model_id: str, status: ModelStatus) -> None:
        """Update the status of a registered model."""
        model = self.get_model_info(model_id)
        model.status = status
        logger.debug(f"Model {model_id} status changed to {status.name}")

    def get_all_models(self) -> List[ModelInfo]:
        """List all known models."""
        return list(self._models.values())
