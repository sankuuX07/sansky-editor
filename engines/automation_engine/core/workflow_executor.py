"""
Executes the workflow graph.
"""
import logging
import asyncio
from typing import Dict, Any, List
from core.models.automation_models import Workflow, WorkflowStatus, WorkflowStep, RecoveryActionType
from engines.automation_engine.core.pipeline_coordinator import PipelineCoordinator
from engines.automation_engine.managers.error_recovery_manager import ErrorRecoveryManager
from engines.automation_engine.managers.progress_manager import ProgressManager
from engines.automation_engine.core.task_scheduler import TaskScheduler
from core.exceptions.automation_exceptions import WorkflowExecutionError

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    def __init__(self, 
                 coordinator: PipelineCoordinator, 
                 scheduler: TaskScheduler, 
                 progress: ProgressManager,
                 recovery: ErrorRecoveryManager):
        self.coordinator = coordinator
        self.scheduler = scheduler
        self.progress = progress
        self.recovery = recovery
        self._context: Dict[str, Any] = {}

    async def execute(self, workflow: Workflow) -> None:
        logger.info(f"Starting execution of workflow '{workflow.name}'")
        workflow.status = WorkflowStatus.RUNNING
        self.progress.initialize_workflow(workflow)
        
        pending_steps = list(workflow.steps)
        completed_step_ids = set()
        in_progress = {}

        while pending_steps or in_progress:
            for step in list(pending_steps):
                if all(dep in completed_step_ids for dep in step.depends_on):
                    pending_steps.remove(step)
                    step.status = WorkflowStatus.RUNNING
                    in_progress[step.step_id] = asyncio.create_task(self._run_step(step))
            
            if not in_progress and pending_steps:
                raise WorkflowExecutionError("Deadlock: Cannot resolve remaining dependencies.")
                
            done, _ = await asyncio.wait(in_progress.values(), return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                step_id = next(s_id for s_id, t in in_progress.items() if t == task)
                del in_progress[step_id]
                step = next(s for s in workflow.steps if s.step_id == step_id)
                
                try:
                    result = task.result()
                    step.status = WorkflowStatus.COMPLETED
                    step.result = result
                    self._context[step_id] = result
                    completed_step_ids.add(step_id)
                    self.progress.mark_step_completed(workflow.workflow_id, step_id)
                except Exception as e:
                    step.status = WorkflowStatus.FAILED
                    step.error = str(e)
                    action = self.recovery.determine_action(step)
                    if action.action_type == RecoveryActionType.RETRY:
                        logger.warning(f"Retrying step '{step_id}'")
                        step.retry_count += 1
                        step.status = WorkflowStatus.PENDING
                        pending_steps.append(step)
                    elif action.action_type == RecoveryActionType.ABORT:
                        workflow.status = WorkflowStatus.FAILED
                        for t in in_progress.values():
                            t.cancel()
                        raise WorkflowExecutionError(f"Workflow failed at step '{step_id}': {e}") from e

        workflow.status = WorkflowStatus.COMPLETED
        logger.info(f"Workflow '{workflow.name}' completed successfully.")

    async def _run_step(self, step: WorkflowStep) -> Any:
        return await self.coordinator.execute_step(step, self._context)
