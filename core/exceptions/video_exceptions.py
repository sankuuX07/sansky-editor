"""
Video-specific exceptions.
"""
from core.exceptions.exceptions import SanskyException

class FFmpegNotFoundError(SanskyException):
    """Raised when FFmpeg or FFprobe cannot be found on the system."""
    pass

class VideoValidationError(SanskyException):
    """Raised when a video file fails validation."""
    pass

class ExtractionError(SanskyException):
    """Raised when frame or audio extraction fails."""
    pass

class ConversionError(SanskyException):
    """Raised when video conversion fails."""
    pass

class VideoCutError(SanskyException):
    """Raised when cutting a video fails."""
    pass
