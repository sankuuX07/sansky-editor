"""
Highlight Engine specific exceptions.
"""
from core.exceptions.exceptions import SanskyException

class HighlightDetectionError(SanskyException):
    pass

class InvalidHighlightError(SanskyException):
    pass

class ScoringError(SanskyException):
    pass

class SceneAnalysisError(SanskyException):
    pass

class MotionAnalysisError(SanskyException):
    pass

class AudioAnalysisError(SanskyException):
    pass
