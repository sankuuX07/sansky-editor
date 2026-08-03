"""
Exceptions for the Shorts Generator Engine.
"""
from core.exceptions.exceptions import SanskyException

class WorkflowFailedError(SanskyException):
    pass

class ShortGenerationError(SanskyException):
    pass

class PipelineExecutionError(SanskyException):
    pass

class InvalidInputVideoError(SanskyException):
    pass

class TimelineGenerationError(SanskyException):
    pass

class OutputGenerationError(SanskyException):
    pass
