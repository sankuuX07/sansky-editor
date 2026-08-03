import logging
from pathlib import Path
from core.logger.logger import LoggerFactory

def test_logger_initialization(tmp_path: Path):
    log_file = tmp_path / "app.log"
    LoggerFactory.setup_logging(log_level="DEBUG", log_file=str(log_file))
    
    logger = logging.getLogger("test_logger")
    logger.debug("Test debug message")
    logger.info("Test info message")
    
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Test debug message" in content
    assert "Test info message" in content
    
    # Check root logger handlers
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 2 # Console and File
