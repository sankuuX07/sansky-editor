from app.services.engine_manager import EngineManager
from engines.base_engine import BaseEngine
import pytest

class MockEngine(BaseEngine):
    def __init__(self, name: str):
        super().__init__(name)
        self.init_called = False
        self.start_called = False
        self.stop_called = False
        
    def initialize(self):
        self.init_called = True
    def start(self):
        self.start_called = True
    def stop(self):
        self.stop_called = True
    def shutdown(self):
        self.stop()
    def health_check(self):
        return True

def test_engine_manager_lifecycle():
    manager = EngineManager()
    engine = MockEngine("mock")
    
    manager.register(engine)
    assert manager.get_engine("mock") == engine
    
    manager.initialize_all()
    assert engine.init_called
    assert engine.is_initialized
    
    manager.start_all()
    assert engine.start_called
    assert engine.is_running
    
    manager.stop_all()
    assert engine.stop_called
    assert not engine.is_running
