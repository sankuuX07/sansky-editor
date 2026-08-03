"""
Engine Manager responsible for engine lifecycle and dependency validation.
"""
from typing import Dict
import logging
from engines.base_engine import BaseEngine
from core.exceptions.exceptions import EngineInitError

logger = logging.getLogger(__name__)

class EngineManager:
    """Manages the registration, initialization, and lifecycle of all engines."""
    def __init__(self) -> None:
        self._engines: Dict[str, BaseEngine] = {}

    def register(self, engine: BaseEngine) -> None:
        """Register an engine instance."""
        if engine.name in self._engines:
            logger.warning(f"Engine {engine.name} is already registered. Overwriting.")
        self._engines[engine.name] = engine
        logger.info(f"Registered engine: {engine.name}")

    def get_engine(self, name: str) -> BaseEngine:
        """Retrieve a registered engine by name."""
        return self._engines[name]

    def initialize_all(self) -> None:
        """Initialize all registered engines."""
        logger.info("Initializing all engines...")
        for name, engine in self._engines.items():
            try:
                if not engine.is_initialized:
                    engine.initialize()
                    engine.is_initialized = True
                    logger.info(f"Initialized engine: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize engine {name}: {e}", exc_info=True)
                raise EngineInitError(f"Failed to initialize {name}") from e

    def start_all(self) -> None:
        """Start all registered engines."""
        logger.info("Starting all engines...")
        for name, engine in self._engines.items():
            if engine.is_initialized and not engine.is_running:
                engine.start()
                engine.is_running = True
                logger.info(f"Started engine: {name}")

    def stop_all(self) -> None:
        """Stop all registered engines."""
        logger.info("Stopping all engines...")
        for name, engine in self._engines.items():
            if engine.is_running:
                engine.stop()
                engine.is_running = False
                logger.info(f"Stopped engine: {name}")

    def shutdown_all(self) -> None:
        """Shutdown all registered engines."""
        logger.info("Shutting down all engines...")
        for name, engine in self._engines.items():
            if engine.is_initialized:
                engine.shutdown()
                engine.is_initialized = False
                logger.info(f"Shut down engine: {name}")
