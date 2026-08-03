import pytest
from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager
from engines.automation_engine.automation_engine import AutomationEngine
from core.models.shared_types import EngineStatus

def test_automation_engine_lifecycle():
    engine_mgr = EngineManager()
    task_mgr = TaskManager()
    
    engine = AutomationEngine(engine_mgr, task_mgr)
    
    assert engine.status() == EngineStatus.UNINITIALIZED
    
    engine.initialize()
    assert engine.status() == EngineStatus.UNINITIALIZED
    
    engine.start()
    assert engine.status() == EngineStatus.RUNNING
    assert engine.health_check() is True
    
    engine.stop()
    assert engine.status() == EngineStatus.STOPPED
    
    engine.shutdown()
    assert engine.status() == EngineStatus.UNINITIALIZED
