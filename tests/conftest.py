import pytest
from pathlib import Path
import tempfile
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)
