import pytest
from engines.shorts_generator_engine.managers.project_assembler import ProjectAssembler
from core.models.shorts_models import TimelineDefinition, OutputSettings

def test_project_assembler(tmp_path):
    manager = ProjectAssembler()
    settings = OutputSettings(output_directory=str(tmp_path))
    timeline = TimelineDefinition(clips=[], resolution="1080x1920", framerate=60.0)
    
    project = manager.assemble(timeline, settings)
    
    assert project.premiere_project_path.parent == tmp_path
    assert project.premiere_project_path.name.startswith("project_")
