"""
Determines recovery actions for failed steps.
"""
from core.models.automation_models import WorkflowStep, RecoveryAction, RecoveryActionType
import logging

logger = logging.getLogger(__name__)

class ErrorRecoveryManager:
    def determine_action(self, step: WorkflowStep) -> RecoveryAction:
        if step.retry_count < step.max_retries:
            return RecoveryAction(action_type=RecoveryActionType.RETRY)
        return RecoveryAction(action_type=RecoveryActionType.ABORT)
