"""
Manages physical output files.
"""
import logging
from pathlib import Path
from core.models.shorts_models import ProcessingResult

logger = logging.getLogger(__name__)

class OutputManager:
    def finalize(self, result: ProcessingResult) -> None:
        logger.info(f"Finalizing output for request {result.request_id}")
        
        for proj in result.projects:
            if proj.premiere_project_path:
                proj.premiere_project_path.parent.mkdir(parents=True, exist_ok=True)
                proj.premiere_project_path.touch(exist_ok=True)
