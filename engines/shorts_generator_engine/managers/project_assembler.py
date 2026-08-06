"""
Assembles the final Premiere project representation.
"""
import logging
from pathlib import Path
from core.models.shorts_models import ShortsProject, TimelineDefinition, OutputSettings
import uuid

logger = logging.getLogger(__name__)

class ProjectAssembler:
    def assemble(self, timeline: TimelineDefinition, settings: OutputSettings) -> ShortsProject:
        logger.info("Assembling Shorts Project")
        
        out_dir = Path(settings.output_directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        project_id = str(uuid.uuid4())
        project_path = out_dir / f"project_{project_id}.xml"
        
        return ShortsProject(
            project_id=project_id,
            clips=timeline.clips,
            settings=settings,
            premiere_project_path=project_path
        )
