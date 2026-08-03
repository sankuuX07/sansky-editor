import pytest
from core.models.automation_models import Workflow, WorkflowStep
from engines.automation_engine.managers.progress_manager import ProgressManager

def test_progress_manager():
    manager = ProgressManager()
    workflow = Workflow(
        name="Test",
        steps=[WorkflowStep(step_id="1", engine_name="a", action="a"), 
               WorkflowStep(step_id="2", engine_name="a", action="a")]
    )
    
    manager.initialize_workflow(workflow)
    prog = manager._progress[workflow.workflow_id]
    
    assert prog.percentage == 0.0
    
    manager.mark_step_completed(workflow.workflow_id, "1")
    assert prog.completed_steps == 1
    assert prog.percentage == 50.0
