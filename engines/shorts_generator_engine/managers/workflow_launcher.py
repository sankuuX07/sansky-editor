"""
Launches and tracks workflows utilizing AutomationEngine.
"""
import logging
import asyncio
from pathlib import Path
from core.models.shorts_models import ProcessingRequest
from engines.automation_engine.automation_engine import AutomationEngine
from core.models.automation_models import WorkflowStatus
from core.exceptions.shorts_exceptions import PipelineExecutionError

logger = logging.getLogger(__name__)

class WorkflowLauncher:
    def __init__(self, automation_engine: AutomationEngine):
        self.automation_engine = automation_engine
        
    async def launch_for_video(self, request: ProcessingRequest, video_path: Path) -> dict:
        """Launches the automation workflow for a single video."""
        logger.info(f"Launching workflow for video: {video_path}")
        
        workflow = self.automation_engine.template_manager.get_gaming_shorts_template()
        workflow.name = f"Shorts Generator: {video_path.name}"
        
        for step in workflow.steps:
            step.inputs["video_path"] = str(video_path)
            if step.step_id == "extract_audio":
                step.inputs["output_dir"] = request.settings.output_directory
        
        await self.automation_engine.run_workflow(workflow)
        
        if workflow.status == WorkflowStatus.FAILED:
            raise PipelineExecutionError(f"Workflow failed for {video_path}")
            
        results = {}
        for step in workflow.steps:
            results[step.step_id] = step.result
            
        return results
