"""
Manages workflow CRUD operations.
"""
from typing import Dict, Optional
from core.models.automation_models import Workflow
import logging

logger = logging.getLogger(__name__)

class WorkflowManager:
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
        
    def register_workflow(self, workflow: Workflow) -> str:
        self._workflows[workflow.workflow_id] = workflow
        logger.debug(f"Registered workflow: {workflow.workflow_id}")
        return workflow.workflow_id
        
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)
