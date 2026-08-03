import pytest
import asyncio
from pathlib import Path
from engines.shorts_generator_engine.core.processing_pipeline import ProcessingPipeline
from core.models.shorts_models import ProcessingRequest, ProcessingStatus

class MockLauncher:
    async def launch_for_video(self, req, path):
        return {"generate_captions": {"captions": []}, "extract_highlights": {"candidates": []}}

class MockHighlight:
    def select_highlights(self, raw, path, settings): return []

class MockCaption:
    def assign_captions(self, clips, raw): return clips
    
class MockTimeline:
    def prepare_timeline(self, clips, settings): return None

class MockProject:
    def assemble(self, timeline, settings): return "project"

@pytest.mark.asyncio
async def test_processing_pipeline(tmp_path):
    pipeline = ProcessingPipeline(MockLauncher(), MockHighlight(), MockCaption(), MockTimeline(), MockProject())
    
    vid = tmp_path / "vid.mp4"
    vid.touch()
    req = ProcessingRequest([vid])
    
    res = await pipeline.process(req)
    
    assert res.status == ProcessingStatus.COMPLETED
    assert len(res.projects) == 1
    assert res.projects[0] == "project"
