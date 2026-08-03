import pytest
from pathlib import Path
from engines.shorts_generator_engine.managers.input_manager import InputManager
from core.exceptions.shorts_exceptions import InvalidInputVideoError

def test_input_manager_valid(tmp_path):
    manager = InputManager()
    
    # Create dummy video
    vid = tmp_path / "test.mp4"
    vid.touch()
    
    req = manager.create_request([vid])
    
    assert len(req.video_paths) == 1
    assert req.video_paths[0] == vid

def test_input_manager_invalid():
    manager = InputManager()
    with pytest.raises(InvalidInputVideoError):
        manager.create_request(["nonexistent.mp4"])
