"""
Lightweight Dependency Injection Container.
"""
from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar('T')

class DIContainer:
    """A simple Service Locator / DI Container."""
    def __init__(self) -> None:
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}

    def register_instance(self, cls: Type[T], instance: T) -> None:
        """Register a singleton instance."""
        self._services[cls] = instance

    def register_factory(self, cls: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for transient resolution."""
        self._factories[cls] = factory

    def resolve(self, cls: Type[T]) -> T:
        """Resolve a dependency."""
        if cls in self._services:
            return self._services[cls]
        if cls in self._factories:
            return self._factories[cls]()
        raise KeyError(f"Service {cls} not registered in container.")

# Global container instance for convenience
container = DIContainer()
