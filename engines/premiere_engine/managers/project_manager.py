"""
Manages .prproj files.
"""
import logging
from pathlib import Path
from core.models.premiere_models import PremiereProject
from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from core.exceptions.premiere_exceptions import ProjectCreationError

logger = logging.getLogger(__name__)

class ProjectManager:
    """Handles creating, opening, and saving projects."""
    def __init__(self, bridge: PremiereBridge) -> None:
        self.bridge = bridge
        self.active_project = None

    def create_project(self, name: str, path: Path) -> PremiereProject:
        logger.info(f"Creating new Premiere project: {name} at {path}")
        try:
            self.bridge.execute_script("createProject", {"name": name, "path": str(path)})
            self.active_project = PremiereProject(name=name, path=path, is_open=True)
            return self.active_project
        except Exception as e:
            raise ProjectCreationError(f"Failed to create project: {e}") from e

    def open_project(self, path: Path) -> PremiereProject:
        logger.info(f"Opening Premiere project: {path}")
        try:
            self.bridge.execute_script("openProject", {"path": str(path)})
            name = path.stem
            self.active_project = PremiereProject(name=name, path=path, is_open=True)
            return self.active_project
        except Exception as e:
            raise ProjectCreationError(f"Failed to open project: {e}") from e
            
    def save_project(self) -> None:
        if self.active_project:
            logger.info(f"Saving project: {self.active_project.name}")
            self.bridge.execute_script("saveProject", {})
