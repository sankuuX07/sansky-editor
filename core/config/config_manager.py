"""
Configuration Manager handling application settings.
"""
import json
import os
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from typing import Optional

class AppConfig(BaseModel):
    """Main application configuration model. Immutable during runtime."""
    model_config = ConfigDict(frozen=True)

    log_level: str = "INFO"
    data_dir: str = "data"
    output_dir: str = "data/output"
    whisper_model_size: str = "base"
    ffmpeg_path: Optional[str] = None

class ConfigManager:
    """Manages loading, validating, and saving configuration with env overrides."""
    def __init__(self, config_path: str = "config/config.json") -> None:
        self.config_path = Path(config_path)
        self.config: AppConfig = AppConfig()

    def load(self) -> None:
        """Load and validate configuration from file and env vars."""
        data = {}
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            self.save()  # Generate default config if it doesn't exist
            
        # Environment Overrides
        for key in AppConfig.model_fields.keys():
            env_val = os.getenv(f"SANSKY_{key.upper()}")
            if env_val is not None:
                data[key] = env_val

        self.config = AppConfig(**data)

    def save(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(self.config.model_dump_json(indent=4))

    def get(self) -> AppConfig:
        """Return the current immutable configuration."""
        return self.config
