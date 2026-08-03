"""
Inference Manager for handling inference requests.
"""
import logging
import time
from typing import Callable, Any
from core.models.ai_models import InferenceRequest, InferenceResult
from core.exceptions.ai_exceptions import InferenceError
from engines.ai_engine.models.model_manager import ModelManager
from engines.ai_engine.hardware.gpu_manager import GPUManager

logger = logging.getLogger(__name__)

class InferenceManager:
    """Executes AI inferences seamlessly."""
    def __init__(self, model_manager: ModelManager, gpu_manager: GPUManager) -> None:
        self.model_manager = model_manager
        self.gpu_manager = gpu_manager

    def run_inference(self, request: InferenceRequest, load_func: Callable, inference_func: Callable) -> InferenceResult:
        """
        Execute an inference request.
        load_func: how to load the model (passed to ModelManager)
        inference_func: the actual logic (model, inputs, params) -> output
        """
        start_time = time.time()
        try:
            model_obj = self.model_manager.load_model(request.model_id, load_func)
            
            logger.debug(f"Running inference for {request.model_id}")
            device = self.gpu_manager.get_optimal_device()
            
            outputs = inference_func(model_obj, request.inputs, request.parameters, device)
            
            execution_time = (time.time() - start_time) * 1000.0
            
            return InferenceResult(
                model_id=request.model_id,
                success=True,
                outputs=outputs,
                execution_time_ms=execution_time
            )
        except Exception as e:
            logger.error(f"Inference failed for {request.model_id}: {e}", exc_info=True)
            return InferenceResult(
                model_id=request.model_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000.0
            )
