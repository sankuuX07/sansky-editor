"""
Tracks workflow progress and estimated time.
"""
from typing import Dict
from core.models.automation_models import Workflow, WorkflowProgress, WorkflowStatus
import logging

logger = logging.getLogger(__name__)

class ProgressManager:
    def __init__(self):
        self._progress: Dict[str, WorkflowProgress] = {}
        
    def initialize_workflow(self, workflow: Workflow) -> None:
        self._progress[workflow.workflow_id] = WorkflowProgress(
            workflow_id=workflow.workflow_id,
            total_steps=len(workflow.steps),
            completed_steps=0,
            status=WorkflowStatus.RUNNING
        )
        
    def mark_step_completed(self, workflow_id: str, step_id: str) -> None:
        prog = self._progress.get(workflow_id)
        if prog:
            prog.completed_steps += 1
            prog.percentage = (prog.completed_steps / max(prog.total_steps, 1)) * 100.0
            logger.info(f"Workflow {workflow_id} progress: {prog.percentage:.1f}%")
