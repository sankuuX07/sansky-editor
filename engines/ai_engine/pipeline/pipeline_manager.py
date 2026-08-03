"""
Manages generic AI inference pipelines.
"""
import logging
from typing import List, Dict, Any
from core.models.ai_models import PipelineStage

logger = logging.getLogger(__name__)

class PipelineManager:
    """Executes sequential AI operations generically."""
    def __init__(self) -> None:
        self.stages: List[PipelineStage] = []

    def register_stage(self, stage: PipelineStage) -> None:
        """Add a stage to the pipeline."""
        self.stages.append(stage)
        logger.info(f"Registered pipeline stage: {stage.stage_id}")

    def execute_pipeline(self, initial_inputs: Dict[str, Any], inference_callback: Any) -> Dict[str, Any]:
        """
        Execute all stages sequentially.
        inference_callback receives (model_id, inputs) and returns results.
        """
        context = initial_inputs.copy()
        
        for stage in self.stages:
            logger.info(f"Executing pipeline stage: {stage.stage_id} for model {stage.model_id}")
            
            stage_inputs = {}
            for target_arg, source_key in stage.input_mapping.items():
                if source_key in context:
                    stage_inputs[target_arg] = context[source_key]
                else:
                    logger.warning(f"Missing input {source_key} for stage {stage.stage_id}")
            
            result = inference_callback(stage.model_id, stage_inputs)
            
            context[f"{stage.stage_id}_result"] = result
            
        return context
