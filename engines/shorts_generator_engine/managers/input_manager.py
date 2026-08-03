"""
Input Manager for Shorts Generator.
"""
from typing import List, Union
from pathlib import Path
import logging
from core.models.shorts_models import ProcessingRequest, OutputSettings
from core.exceptions.shorts_exceptions import InvalidInputVideoError

logger = logging.getLogger(__name__)

class InputManager:
    def create_request(self, inputs: Union[str, Path, List[Union[str, Path]]], settings: OutputSettings = None) -> ProcessingRequest:
        if not isinstance(inputs, list):
            inputs = [inputs]
            
        valid_paths = []
        for inp in inputs:
            path = Path(inp)
            if path.is_file() and path.suffix.lower() in [".mp4", ".mov", ".mkv"]:
                valid_paths.append(path)
            elif path.is_dir():
                valid_paths.extend(p for p in path.glob("*") if p.is_file() and p.suffix.lower() in [".mp4", ".mov", ".mkv"])
        
        if not valid_paths:
            raise InvalidInputVideoError("No valid video files provided.")
            
        settings = settings or OutputSettings()
        logger.info(f"Created request with {len(valid_paths)} videos.")
        return ProcessingRequest(video_paths=valid_paths, settings=settings)
