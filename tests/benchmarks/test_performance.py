"""
Performance benchmarks for core operations.
"""
import pytest
import time
from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager
from engines.automation_engine.automation_engine import AutomationEngine

def test_engine_startup_benchmark():
    start = time.perf_counter()
    
    engine_manager = EngineManager()
    task_manager = TaskManager(max_workers=1)
    automation_engine = AutomationEngine(engine_manager, task_manager)
    
    engine_manager.register(automation_engine)
    engine_manager.initialize_all()
    engine_manager.start_all()
    
    duration = time.perf_counter() - start
    
    engine_manager.shutdown_all()
    
    # Assert startup takes less than 0.5 seconds
    assert duration < 0.5
