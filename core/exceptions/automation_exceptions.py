"""
Automation Engine specific exceptions.
"""
from core.exceptions.exceptions import SanskyException

class WorkflowExecutionError(SanskyException):
    pass

class WorkflowValidationError(SanskyException):
    pass

class EngineUnavailableError(SanskyException):
    pass

class DependencyResolutionError(SanskyException):
    pass

class AutomationTimeoutError(SanskyException):
    pass

class TaskExecutionError(SanskyException):
    pass
