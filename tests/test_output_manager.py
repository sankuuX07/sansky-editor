import pytest
from engines.shorts_generator_engine.managers.output_manager import OutputManager
from core.models.shorts_models import ProcessingResult, ShortsProject, ProcessingStatus

def test_output_manager(tmp_path):
    manager = OutputManager()
    
    p = tmp_path / "project.prproj"
    proj = ShortsProject(project_id="1", clips=[], settings=None, premiere_project_path=p)
    
    res = ProcessingResult(request_id="1", status=ProcessingStatus.COMPLETED, projects=[proj])
    
    manager.finalize(res)
    
    assert p.exists()
