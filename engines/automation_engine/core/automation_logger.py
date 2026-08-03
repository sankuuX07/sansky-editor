"""
Detailed execution logging for workflows.
"""
import logging
from core.models.automation_models import Workflow

logger = logging.getLogger(__name__)

class AutomationLogger:
    def log_start(self, workflow: Workflow) -> None:
        logger.info(f"--- Workflow Start: {workflow.name} ({workflow.workflow_id}) ---")
        
    def log_end(self, workflow: Workflow) -> None:
        logger.info(f"--- Workflow End: {workflow.name} - Status: {workflow.status.value} ---")
