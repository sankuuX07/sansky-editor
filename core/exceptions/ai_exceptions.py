"""
AI-specific exceptions.
"""
from core.exceptions.exceptions import SanskyException

class ModelNotFoundError(SanskyException):
    pass

class UnsupportedHardwareError(SanskyException):
    pass

class ModelLoadError(SanskyException):
    pass

class InferenceError(SanskyException):
    pass

class OutOfMemoryError(SanskyException):
    pass

class GPUInitializationError(SanskyException):
    pass
