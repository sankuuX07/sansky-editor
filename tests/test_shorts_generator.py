import pytest
import asyncio
from engines.shorts_generator_engine.shorts_generator_engine import ShortsGeneratorEngine
from core.models.shared_types import EngineStatus

class MockAutomation:
    pass

def test_shorts_generator_lifecycle():
    engine = ShortsGeneratorEngine(MockAutomation())
    
    assert engine.status() == EngineStatus.UNINITIALIZED
    
    engine.initialize()
    assert engine.status() == EngineStatus.UNINITIALIZED
    
    engine.start()
    assert engine.status() == EngineStatus.RUNNING
    
    engine.stop()
    assert engine.status() == EngineStatus.STOPPED
