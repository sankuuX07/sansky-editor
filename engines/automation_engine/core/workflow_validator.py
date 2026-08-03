"""
Validates workflows before execution.
"""
from typing import List
from core.models.automation_models import Workflow
from core.exceptions.automation_exceptions import WorkflowValidationError
from app.services.engine_manager import EngineManager
import logging

logger = logging.getLogger(__name__)

class WorkflowValidator:
    def __init__(self, engine_manager: EngineManager):
        self.engine_manager = engine_manager
        
    def validate(self, workflow: Workflow) -> None:
        logger.info(f"Validating workflow: {workflow.name}")
        self._check_cycles(workflow)
        self._check_missing_dependencies(workflow)
        self._check_engines_available(workflow)
        logger.info(f"Workflow '{workflow.name}' is valid.")

    def _check_missing_dependencies(self, workflow: Workflow) -> None:
        step_ids = {step.step_id for step in workflow.steps}
        for step in workflow.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise WorkflowValidationError(f"Step '{step.step_id}' depends on non-existent step '{dep}'")

    def _check_cycles(self, workflow: Workflow) -> None:
        visited = set()
        path = set()
        
        step_map = {step.step_id: step for step in workflow.steps}
        
        def visit(step_id: str):
            if step_id in path:
                raise WorkflowValidationError(f"Circular dependency detected involving step '{step_id}'")
            if step_id in visited:
                return
                
            path.add(step_id)
            for dep in step_map[step_id].depends_on:
                visit(dep)
            path.remove(step_id)
            visited.add(step_id)
            
        for step in workflow.steps:
            visit(step.step_id)
            
    def _check_engines_available(self, workflow: Workflow) -> None:
        for step in workflow.steps:
            try:
                engine = self.engine_manager.get_engine(step.engine_name)
                if not engine.is_running:
                    raise WorkflowValidationError(f"Engine '{step.engine_name}' for step '{step.step_id}' is not running.")
            except KeyError:
                raise WorkflowValidationError(f"Engine '{step.engine_name}' for step '{step.step_id}' is not registered.")
