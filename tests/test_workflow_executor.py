import pytest
import asyncio
from core.models.automation_models import Workflow, WorkflowStep, WorkflowStatus
from engines.automation_engine.core.workflow_executor import WorkflowExecutor
from core.exceptions.automation_exceptions import WorkflowExecutionError

class MockProgress:
    def initialize_workflow(self, workflow): pass
    def mark_step_completed(self, w_id, s_id): pass

class MockRecovery:
    def determine_action(self, step): 
        from core.models.automation_models import RecoveryAction, RecoveryActionType
        return RecoveryAction(action_type=RecoveryActionType.ABORT)

class MockCoordinator:
    async def execute_step(self, step, context):
        if step.action == "fail":
            raise ValueError("Intentional failure")
        return f"result_of_{step.step_id}"

@pytest.mark.asyncio
async def test_workflow_executor_success():
    coordinator = MockCoordinator()
    executor = WorkflowExecutor(coordinator, None, MockProgress(), MockRecovery())
    
    workflow = Workflow(
        name="Test",
        steps=[
            WorkflowStep(step_id="1", engine_name="e", action="a"),
            WorkflowStep(step_id="2", engine_name="e", action="a", depends_on=["1"])
        ]
    )
    
    await executor.execute(workflow)
    
    assert workflow.status == WorkflowStatus.COMPLETED
    assert workflow.steps[0].status == WorkflowStatus.COMPLETED
    assert workflow.steps[1].status == WorkflowStatus.COMPLETED
    assert workflow.steps[1].result == "result_of_2"

@pytest.mark.asyncio
async def test_workflow_executor_failure():
    coordinator = MockCoordinator()
    executor = WorkflowExecutor(coordinator, None, MockProgress(), MockRecovery())
    
    workflow = Workflow(
        name="Test Fail",
        steps=[
            WorkflowStep(step_id="1", engine_name="e", action="fail")
        ]
    )
    
    with pytest.raises(WorkflowExecutionError):
        await executor.execute(workflow)
        
    assert workflow.status == WorkflowStatus.FAILED
    assert workflow.steps[0].status == WorkflowStatus.FAILED
