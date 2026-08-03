"""
Premiere Engine specific exceptions.
"""
from core.exceptions.exceptions import SanskyException

class PremiereNotInstalledError(SanskyException):
    pass

class ProjectCreationError(SanskyException):
    pass

class SequenceCreationError(SanskyException):
    pass

class MediaImportError(SanskyException):
    pass

class ExportQueueError(SanskyException):
    pass

class TimelineError(SanskyException):
    pass

class BridgeConnectionError(SanskyException):
    pass
