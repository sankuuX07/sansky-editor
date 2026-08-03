"""
Application Bootstrap process.
Glues the core framework components together.
"""
import logging
from core.dependency_injection.container import container
from core.config.config_manager import ConfigManager
from core.logger.logger import LoggerFactory
from core.events.event_bus import EventBus
from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager

logger = logging.getLogger(__name__)

class ApplicationBootstrapper:
    """Handles the initialization sequence of the application."""
    
    @staticmethod
    def bootstrap() -> None:
        """Run the bootstrap sequence."""
        # 1. Initialize Configuration
        config_manager = ConfigManager()
        config_manager.load()
        container.register_instance(ConfigManager, config_manager)

        # 2. Setup Logging
        LoggerFactory.setup_logging(log_level=config_manager.get().log_level)
        logger.info("Bootstrap: Configuration and Logger initialized.")

        # 3. Setup Event Bus
        event_bus = EventBus()
        container.register_instance(EventBus, event_bus)
        logger.info("Bootstrap: Event Bus initialized.")

        # 4. Setup Engine Manager
        engine_manager = EngineManager()
        container.register_instance(EngineManager, engine_manager)
        logger.info("Bootstrap: Engine Manager initialized.")

        # 5. Setup Task Manager
        task_manager = TaskManager()
        container.register_instance(TaskManager, task_manager)
        logger.info("Bootstrap: Task Manager initialized.")

        # 6. Initialize and start engines
        engine_manager.initialize_all()
        engine_manager.start_all()
        
        logger.info("Bootstrap complete. Application is running.")

    @staticmethod
    def shutdown() -> None:
        """Gracefully shutdown the application."""
        logger.info("Initiating application shutdown...")
        try:
            engine_manager = container.resolve(EngineManager)
            engine_manager.stop_all()
            engine_manager.shutdown_all()
            logger.info("Shutdown complete.")
        except KeyError:
            logger.warning("Engine Manager not found in DI container during shutdown.")
