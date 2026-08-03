import pytest
from pathlib import Path
from engines.shorts_generator_engine.managers.highlight_selection_manager import HighlightSelectionManager
from core.models.shorts_models import OutputSettings

def test_highlight_selection():
    manager = HighlightSelectionManager()
    settings = OutputSettings(max_shorts=2, highlight_threshold=0.8)
    
    raw = {
        "candidates": [
            {"start": 0, "end": 20, "score": 0.9},
            {"start": 100, "end": 120, "score": 0.7}, # Below threshold
            {"start": 200, "end": 220, "score": 0.95},
            {"start": 300, "end": 320, "score": 0.85}
        ]
    }
    
    clips = manager.select_highlights(raw, Path("test.mp4"), settings)
    
    assert len(clips) == 2
    assert clips[0].score == 0.95
    assert clips[1].score == 0.9
