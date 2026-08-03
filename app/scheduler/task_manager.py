"""
Task Manager for scheduling, tracking, and executing async background jobs.
"""
import asyncio
from typing import Any, Callable, Coroutine, Dict, List
import logging
from dataclasses import dataclass, field
import uuid

from core.models.shared_types import TaskState

logger = logging.getLogger(__name__)

@dataclass(order=True)
class PrioritizedTask:
    priority: int
    task_id: str = field(compare=False)
    coro: Coroutine = field(compare=False)

@dataclass
class TaskProgress:
    task_id: str
    state: TaskState = TaskState.PENDING
    progress_percentage: float = 0.0
    error: str = ""
    result: Any = None

class TaskManager:
    """Manages concurrent execution of background tasks using an asyncio PriorityQueue."""
    def __init__(self, max_workers: int = 4) -> None:
        self._queue: asyncio.PriorityQueue[PrioritizedTask] = asyncio.PriorityQueue()
        self._tasks: Dict[str, asyncio.Task] = {}
        self._progress: Dict[str, TaskProgress] = {}
        self._workers: List[asyncio.Task] = []
        self._max_workers = max_workers
        self._running = False

    def start_workers(self) -> None:
        """Start background workers to process the queue."""
        if self._running:
            return
        self._running = True
        for _ in range(self._max_workers):
            self._workers.append(asyncio.create_task(self._worker_loop()))
        logger.info(f"Started {self._max_workers} task workers.")

    async def stop_workers(self) -> None:
        """Stop all workers gracefully."""
        self._running = False
        for _ in range(self._max_workers):
            await self._queue.put(PrioritizedTask(priority=9999, task_id="STOP", coro=self._dummy_coro()))
        await asyncio.gather(*self._workers)
        logger.info("Task workers stopped.")

    async def _dummy_coro(self) -> None:
        pass

    async def _worker_loop(self) -> None:
        """Worker loop to process tasks from the priority queue."""
        while self._running:
            p_task = await self._queue.get()
            if p_task.task_id == "STOP":
                if hasattr(p_task.coro, "close"):
                    p_task.coro.close()
                self._queue.task_done()
                break

            task_id = p_task.task_id
            if self._progress[task_id].state == TaskState.CANCELLED:
                if hasattr(p_task.coro, "close"):
                    p_task.coro.close()
                self._queue.task_done()
                continue

            self._progress[task_id].state = TaskState.RUNNING
            
            task = asyncio.create_task(p_task.coro)
            self._tasks[task_id] = task
            
            try:
                result = await task
                self._progress[task_id].result = result
                self._progress[task_id].state = TaskState.COMPLETED
                self._progress[task_id].progress_percentage = 100.0
            except asyncio.CancelledError:
                self._progress[task_id].state = TaskState.CANCELLED
            except Exception as e:
                self._progress[task_id].state = TaskState.FAILED
                self._progress[task_id].error = str(e)
                logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            finally:
                self._queue.task_done()

    def submit_coroutine(self, coro: Coroutine, priority: int = 10, task_id: str = "") -> str:
        """Submit an asyncio Coroutine to the priority queue. Lower number = higher priority."""
        if not task_id:
            task_id = str(uuid.uuid4())
        
        self._progress[task_id] = TaskProgress(task_id=task_id)
        p_task = PrioritizedTask(priority=priority, task_id=task_id, coro=coro)
        
        try:
            self._queue.put_nowait(p_task)
            logger.info(f"Submitted task: {task_id} with priority {priority}")
        except asyncio.QueueFull:
            logger.error("Task queue is full!")
            self._progress[task_id].state = TaskState.FAILED
            self._progress[task_id].error = "Queue full"
            
        return task_id

    def submit_blocking(self, func: Callable, *args: Any, priority: int = 10, **kwargs: Any) -> str:
        """Submit a blocking function to run in the default executor."""
        import functools
        task_id = str(uuid.uuid4())
        
        async def _wrapper():
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
            
        return self.submit_coroutine(_wrapper(), priority=priority, task_id=task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Attempt to cancel a task."""
        if task_id in self._progress:
            if self._progress[task_id].state == TaskState.PENDING:
                self._progress[task_id].state = TaskState.CANCELLED
                logger.info(f"Cancelled pending task: {task_id}")
                return True
            elif task_id in self._tasks and not self._tasks[task_id].done():
                self._tasks[task_id].cancel()
                logger.info(f"Requested cancellation of running task: {task_id}")
                return True
        return False

    def get_progress(self, task_id: str) -> TaskProgress:
        """Get the current progress of a task."""
        return self._progress.get(task_id, TaskProgress(task_id=task_id, state=TaskState.FAILED, error="Task not found"))
