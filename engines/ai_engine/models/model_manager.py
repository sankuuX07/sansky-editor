"""
Model Manager for lazy loading and lifecycle control.
"""
import logging
from typing import Any
from pathlib import Path

from core.models.ai_models import ModelStatus
from core.exceptions.ai_exceptions import ModelLoadError, ModelNotFoundError
from engines.ai_engine.models.model_registry import ModelRegistry
from engines.ai_engine.hardware.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class ModelManager:
    """Handles lazy loading of models and integrates with MemoryManager."""
    def __init__(self, registry: ModelRegistry, memory_manager: MemoryManager) -> None:
        self.registry = registry
        self.memory_manager = memory_manager

    def load_model(self, model_id: str, load_func: Any) -> Any:
        """
        Lazily load a model using the provided load_func.
        Retrieves from cache if already loaded.
        """
        model_info = self.registry.get_model_info(model_id)
        
        cached_model = self.memory_manager.get_model(model_id)
        if cached_model is not None:
            logger.debug(f"Model {model_id} retrieved from cache.")
            return cached_model

        if not model_info.path.exists():
            raise ModelNotFoundError(f"Model file not found at {model_info.path}")

        self.registry.update_status(model_id, ModelStatus.LOADING)
        try:
            logger.info(f"Loading model {model_id} into memory...")
            model_obj = load_func(model_info.path) 
            
            self.memory_manager.cache_model(model_id, model_obj, model_info.memory_requirement_mb)
            self.registry.update_status(model_id, ModelStatus.LOADED)
            
            return model_obj
        except Exception as e:
            self.registry.update_status(model_id, ModelStatus.ERROR)
            raise ModelLoadError(f"Failed to load model {model_id}") from e

    def unload_model(self, model_id: str) -> None:
        """Manually force a model to unload."""
        self.memory_manager.remove_model(model_id)
        self.registry.update_status(model_id, ModelStatus.UNLOADED)
