import pytest
from core.models.automation_models import Workflow, WorkflowStep, WorkflowStatus
from engines.automation_engine.managers.workflow_manager import WorkflowManager

def test_workflow_manager_registration():
    manager = WorkflowManager()
    workflow = Workflow(
        name="Test Workflow",
        steps=[WorkflowStep(step_id="1", engine_name="test", action="do_test")]
    )
    
    wf_id = manager.register_workflow(workflow)
    fetched = manager.get_workflow(wf_id)
    
    assert fetched is not None
    assert fetched.name == "Test Workflow"
    assert len(fetched.steps) == 1
    assert fetched.status == WorkflowStatus.PENDING
