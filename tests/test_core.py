from core.exceptions.exceptions import SanskyException
from core.models.shared_types import TaskState

def test_base_exception():
    exc = SanskyException("test error")
    assert str(exc) == "test error"
    
def test_shared_types():
    assert TaskState.PENDING.value == "PENDING"
    assert TaskState.COMPLETED.value == "COMPLETED"
