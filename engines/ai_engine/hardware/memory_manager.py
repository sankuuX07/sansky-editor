"""
Memory Manager for monitoring RAM/VRAM and caching loaded models safely.
"""
import logging
import psutil
from typing import Dict, Any, List
import torch
from core.models.ai_models import MemorySnapshot
from core.exceptions.ai_exceptions import OutOfMemoryError
from engines.ai_engine.hardware.gpu_manager import GPUManager

logger = logging.getLogger(__name__)

class MemoryManager:
    """Monitors system memory and manages model cache to prevent OOM."""
    def __init__(self, gpu_manager: GPUManager) -> None:
        self.gpu_manager = gpu_manager
        self.loaded_models: Dict[str, Any] = {}
        self._model_usage_order: List[str] = []

    def get_memory_snapshot(self) -> MemorySnapshot:
        """Get current RAM and VRAM usage."""
        ram = psutil.virtual_memory()
        vram_used = 0.0
        vram_total = 0.0

        if self.gpu_manager.active_backend == self.gpu_manager.active_backend.CUDA:
            try:
                free, total = torch.cuda.mem_get_info(0)
                vram_used = (total - free) / (1024 * 1024)
                vram_total = total / (1024 * 1024)
            except Exception:
                pass

        return MemorySnapshot(
            ram_used_mb=ram.used / (1024 * 1024),
            ram_total_mb=ram.total / (1024 * 1024),
            vram_used_mb=vram_used,
            vram_total_mb=vram_total
        )

    def cache_model(self, model_id: str, model_obj: Any, required_memory_mb: int) -> None:
        """Cache a model into memory. Evicts oldest if space is needed."""
        snapshot = self.get_memory_snapshot()
        
        if snapshot.vram_total_mb > 0:
            free_vram = snapshot.vram_total_mb - snapshot.vram_used_mb
            if free_vram < required_memory_mb:
                logger.warning(f"Low VRAM ({free_vram}MB). Attempting to free space for {model_id}.")
                self._evict_models(required_memory_mb - free_vram)
                
        self.loaded_models[model_id] = model_obj
        if model_id in self._model_usage_order:
            self._model_usage_order.remove(model_id)
        self._model_usage_order.append(model_id)
        logger.info(f"Cached model {model_id} in memory.")

    def get_model(self, model_id: str) -> Any:
        """Retrieve a model from cache and update LRU."""
        if model_id in self.loaded_models:
            self._model_usage_order.remove(model_id)
            self._model_usage_order.append(model_id)
            return self.loaded_models[model_id]
        return None

    def remove_model(self, model_id: str) -> None:
        """Remove a model from cache explicitly."""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            self._model_usage_order.remove(model_id)
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"Unloaded model {model_id} manually.")

    def _evict_models(self, required_freed_mb: float) -> None:
        """Evict oldest models to free memory (LRU strategy)."""
        while self._model_usage_order and required_freed_mb > 0:
            oldest = self._model_usage_order.pop(0)
            del self.loaded_models[oldest]
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"Evicted model {oldest} to free memory.")
            break
