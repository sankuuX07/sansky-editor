import pytest
from engines.shorts_generator_engine.managers.caption_placement_manager import CaptionPlacementManager
from core.models.shorts_models import GeneratedClip
from pathlib import Path

def test_caption_placement():
    manager = CaptionPlacementManager()
    
    clips = [
        GeneratedClip(clip_id="1", source_video=Path("a.mp4"), start_time=10.0, end_time=20.0, score=0.9),
        GeneratedClip(clip_id="2", source_video=Path("a.mp4"), start_time=50.0, end_time=60.0, score=0.9)
    ]
    
    raw_caps = {
        "captions": [
            {"start": 12.0, "end": 14.0, "text": "Inside clip 1"},
            {"start": 30.0, "end": 32.0, "text": "Outside both"},
            {"start": 55.0, "end": 57.0, "text": "Inside clip 2"}
        ]
    }
    
    res = manager.assign_captions(clips, raw_caps)
    
    assert len(res[0].captions) == 1
    assert res[0].captions[0]["text"] == "Inside clip 1"
    assert res[0].captions[0]["relative_start"] == 2.0
    
    assert len(res[1].captions) == 1
    assert res[1].captions[0]["text"] == "Inside clip 2"
