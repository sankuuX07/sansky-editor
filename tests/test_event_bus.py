from core.events.event_bus import EventBus
import pytest

class DummyEvent:
    def __init__(self, message: str):
        self.message = message

def test_event_bus_subscribe_publish():
    bus = EventBus()
    received = []
    
    def handler(event: DummyEvent):
        received.append(event.message)
        
    bus.subscribe(DummyEvent, handler)
    bus.publish(DummyEvent("Hello"))
    
    assert len(received) == 1
    assert received[0] == "Hello"

def test_event_bus_unsubscribe():
    bus = EventBus()
    received = []
    
    def handler(event: DummyEvent):
        received.append(event.message)
        
    bus.subscribe(DummyEvent, handler)
    bus.unsubscribe(DummyEvent, handler)
    bus.publish(DummyEvent("Hello"))
    
    assert len(received) == 0
