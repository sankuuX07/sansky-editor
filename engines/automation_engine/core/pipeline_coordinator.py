"""
Coordinates high-level business logic, mapping outputs to inputs.
"""
import logging
import asyncio
from typing import Any
from core.models.automation_models import WorkflowStep
from app.services.engine_manager import EngineManager

logger = logging.getLogger(__name__)

class PipelineCoordinator:
    def __init__(self, engine_manager: EngineManager):
        self.engine_manager = engine_manager
        
    async def execute_step(self, step: WorkflowStep, context: dict) -> Any:
        """Executes the specific action on the required engine."""
        logger.info(f"Coordinator executing step: {step.step_id} on {step.engine_name}")
        engine = self.engine_manager.get_engine(step.engine_name)
        
        # Here we map step.action to actual engine method calls.
        if step.engine_name == "video_engine" and step.action == "extract_audio":
            return {"audio_path": "simulated_audio.wav"}
                
        elif step.engine_name == "whisper_engine" and step.action == "transcribe":
            return {"transcription": "simulated text"}
                
        elif step.engine_name == "caption_engine" and step.action == "generate_captions":
            return {"caption_file": "simulated_captions.srt"}
                
        elif step.engine_name == "premiere_engine" and step.action == "build_timeline":
            return {"timeline_status": "built"}
                
        # Generic fallback for direct method execution
        method = getattr(engine, step.action, None)
        if method:
            import inspect
            if inspect.iscoroutinefunction(method):
                return await method(**step.inputs)
            else:
                loop = asyncio.get_running_loop()
                import functools
                return await loop.run_in_executor(None, functools.partial(method, **step.inputs))

        raise NotImplementedError(f"Action '{step.action}' on engine '{step.engine_name}' is not supported.")
