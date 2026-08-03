import pytest
import asyncio
from app.scheduler.task_manager import TaskManager
from engines.automation_engine.core.task_scheduler import TaskScheduler

@pytest.mark.asyncio
async def test_automation_task_scheduler():
    task_mgr = TaskManager(max_workers=1)
    task_mgr.start_workers()
    
    scheduler = TaskScheduler(task_mgr)
    
    async def dummy_coro():
        return "success"
        
    scheduler.schedule_task(dummy_coro(), "task1")
    result = await scheduler.wait_for_task("task1")
    
    assert result == "success"
    await task_mgr.stop_workers()
