"""
Custom domain exceptions for Sansky AI Editor.
"""

class SanskyException(Exception):
    """Base exception for all custom exceptions in the application."""
    pass

class ConfigurationError(SanskyException):
    """Raised when there is an error in configuration loading or validation."""
    pass

class EngineInitError(SanskyException):
    """Raised when an engine fails to initialize."""
    pass

class DependencyError(SanskyException):
    """Raised when an engine's dependencies are not met."""
    pass
