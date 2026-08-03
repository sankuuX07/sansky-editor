"""
Schedules execution of workflow steps utilizing the application's TaskManager.
"""
import logging
from typing import Coroutine
from app.scheduler.task_manager import TaskManager
import asyncio

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        
    def schedule_task(self, coro: Coroutine, task_id: str) -> None:
        """Schedules a coroutine via TaskManager."""
        logger.debug(f"Scheduling task: {task_id}")
        self.task_manager.submit_coroutine(coro, priority=5, task_id=task_id)
        
    async def wait_for_task(self, task_id: str) -> any:
        """Wait for a scheduled task to complete and return its result."""
        from core.models.shared_types import TaskState
        while True:
            progress = self.task_manager.get_progress(task_id)
            if progress.state == TaskState.COMPLETED:
                return progress.result
            elif progress.state in [TaskState.FAILED, TaskState.CANCELLED]:
                raise Exception(f"Task {task_id} {progress.state.value}: {progress.error}")
            await asyncio.sleep(0.1)
