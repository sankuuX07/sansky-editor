"""
Professional Logging System for Sansky AI Editor.
Supports colored console output and rotating file logs.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import colorlog

class LoggerFactory:
    """Factory for setting up application-wide logging."""
    
    @staticmethod
    def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log") -> None:
        """Initialize root logger with colored console and rotating file handlers."""
        level = getattr(logging, log_level.upper(), logging.INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Clear existing handlers if setup is called multiple times
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # Console Handler with Colorlog
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)

        # File Handler (Rotating)
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(funcName)s:%(lineno)d: %(message)s"
        )
        file_handler = RotatingFileHandler(
            log_path, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
