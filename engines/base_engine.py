"""
Base Engine definition for all subsystems.
"""
from abc import ABC, abstractmethod
import logging
from core.models.shared_types import EngineStatus

class BaseEngine(ABC):
    """
    Abstract Base Class for all engines.
    Defines the standard lifecycle methods.
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = logging.getLogger(f"engine.{self.name}")
        self._status: EngineStatus = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.is_running = False

    @abstractmethod
    def initialize(self) -> None:
        """Initialize engine resources and state."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Start engine processing or event loop."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop engine processing."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Release engine resources."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if engine is in a healthy, operational state."""
        pass

    def status(self) -> EngineStatus:
        """Return the current status of the engine."""
        return self._status
