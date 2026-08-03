import pytest
from core.models.automation_models import WorkflowStep, RecoveryActionType
from engines.automation_engine.managers.error_recovery_manager import ErrorRecoveryManager

def test_error_recovery():
    manager = ErrorRecoveryManager()
    
    step = WorkflowStep(step_id="1", engine_name="e", action="a", retry_count=0, max_retries=3)
    
    action1 = manager.determine_action(step)
    assert action1.action_type == RecoveryActionType.RETRY
    
    step.retry_count = 3
    action2 = manager.determine_action(step)
    assert action2.action_type == RecoveryActionType.ABORT
