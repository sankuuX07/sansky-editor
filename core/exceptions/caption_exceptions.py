"""
Caption Engine specific exceptions.
"""
from core.exceptions.exceptions import SanskyException

class CaptionGenerationError(SanskyException):
    pass

class CaptionFormattingError(SanskyException):
    pass

class CaptionExportError(SanskyException):
    pass

class CaptionValidationError(SanskyException):
    pass

class InvalidTimestampError(SanskyException):
    pass

class UnsupportedSubtitleFormatError(SanskyException):
    pass
