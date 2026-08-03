import pytest
import asyncio
from app.scheduler.task_manager import TaskManager
from core.models.shared_types import TaskState

@pytest.mark.asyncio
async def test_task_manager_coroutine():
    manager = TaskManager(max_workers=1)
    manager.start_workers()
    
    async def dummy_task():
        await asyncio.sleep(0.1)
        return "success"
        
    task_id = manager.submit_coroutine(dummy_task())
    
    # Wait for completion
    while manager.get_progress(task_id).state not in [TaskState.COMPLETED, TaskState.FAILED]:
        await asyncio.sleep(0.05)
        
    progress = manager.get_progress(task_id)
    assert progress.state == TaskState.COMPLETED
    assert progress.result == "success"
    
    await manager.stop_workers()

@pytest.mark.asyncio
async def test_task_manager_blocking():
    manager = TaskManager(max_workers=1)
    manager.start_workers()
    
    def blocking_task():
        return "blocking success"
        
    task_id = manager.submit_blocking(blocking_task)
    
    while manager.get_progress(task_id).state not in [TaskState.COMPLETED, TaskState.FAILED]:
        await asyncio.sleep(0.05)
        
    progress = manager.get_progress(task_id)
    assert progress.state == TaskState.COMPLETED
    assert progress.result == "blocking success"
    
    await manager.stop_workers()
