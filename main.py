"""
Sansky AI Editor - Main Entry Point
"""

import sys
import logging
import asyncio
from app.bootstrap.bootstrapper import ApplicationBootstrapper
from core.dependency_injection.container import container
from app.scheduler.task_manager import TaskManager

logger = logging.getLogger(__name__)

async def async_main() -> None:
    """Async main loop for managing the task manager and background workers."""
    try:
        # Initialize the core application framework
        ApplicationBootstrapper.bootstrap()
        
        # Start TaskManager background workers
        task_manager = container.resolve(TaskManager)
        task_manager.start_workers()
        
        logger.info("Application running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        logger.info("Main loop cancelled.")
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Stop background workers gracefully
        try:
            task_manager = container.resolve(TaskManager)
            await task_manager.stop_workers()
        except KeyError:
            pass
        
        # Gracefully shutdown resources and engines
        ApplicationBootstrapper.shutdown()

def main() -> None:
    """
    Main entry point for the Sansky AI Editor application.
    """
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")

if __name__ == "__main__":
    main()
