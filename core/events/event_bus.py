"""
Thread-safe Event Bus for decoupled engine communication.
"""
from typing import Any, Callable, Dict, List, Type
import threading
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """Publish-Subscribe Event Bus."""
    def __init__(self) -> None:
        self._subscribers: Dict[Type, List[Callable[[Any], None]]] = {}
        self._lock = threading.RLock()

    def subscribe(self, event_type: Type, callback: Callable[[Any], None]) -> None:
        """Subscribe to a specific event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to {event_type.__name__}")

    def unsubscribe(self, event_type: Type, callback: Callable[[Any], None]) -> None:
        """Unsubscribe from a specific event type."""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                    logger.debug(f"Unsubscribed {callback.__name__} from {event_type.__name__}")
                except ValueError:
                    pass

    def publish(self, event: Any) -> None:
        """Publish an event to all subscribers synchronously."""
        event_type = type(event)
        with self._lock:
            callbacks = self._subscribers.get(event_type, []).copy()

        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event handler {callback.__name__} for {event_type.__name__}: {e}", exc_info=True)
