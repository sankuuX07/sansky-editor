import os
import json
from pathlib import Path
from core.config.config_manager import ConfigManager

def test_config_load_save(tmp_path: Path):
    config_file = tmp_path / "config.json"
    manager = ConfigManager(config_path=str(config_file))
    
    # Load should create default if missing
    manager.load()
    assert config_file.exists()
    
    config = manager.get()
    assert config.log_level == "INFO"
    
    # Modify and test env overrides
    os.environ["SANSKY_LOG_LEVEL"] = "DEBUG"
    manager.load()
    assert manager.get().log_level == "DEBUG"
    
    # Clean up env
    del os.environ["SANSKY_LOG_LEVEL"]
