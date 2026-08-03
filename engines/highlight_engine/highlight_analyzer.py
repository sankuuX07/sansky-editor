"""
Orchestrates individual sub-analyzers and merges their results.
"""
import logging
from typing import List
from pathlib import Path
from core.models.highlight_models import HighlightEvent, HighlightCandidate, HighlightConfig
from engines.highlight_engine.analyzers.scene_analyzer import SceneAnalyzer
from engines.highlight_engine.analyzers.motion_analyzer import MotionAnalyzer
from engines.highlight_engine.analyzers.audio_analyzer_adapter import AudioAnalyzerAdapter
from engines.highlight_engine.core.highlight_merger import HighlightMerger
from engines.highlight_engine.core.highlight_scoring_engine import HighlightScoringEngine
from engines.highlight_engine.core.highlight_validator import HighlightValidator
from engines.highlight_engine.core.highlight_ranker import HighlightRanker

logger = logging.getLogger(__name__)

class HighlightAnalyzer:
    """Coordinates analysis, merging, scoring, validation and ranking."""
    
    def __init__(self) -> None:
        self.scene_analyzer = SceneAnalyzer()
        self.motion_analyzer = MotionAnalyzer()
        self.audio_analyzer = AudioAnalyzerAdapter()
        
        self.merger = HighlightMerger()
        self.scoring_engine = HighlightScoringEngine()
        self.validator = HighlightValidator()
        self.ranker = HighlightRanker()

    def analyze_video(self, video_path: Path, audio_path: Path, config: HighlightConfig) -> List[HighlightCandidate]:
        """Run full analysis pipeline."""
        logger.info(f"Starting highlight analysis for {video_path}")
        
        all_events: List[HighlightEvent] = []
        all_events.extend(self.scene_analyzer.analyze(video_path))
        all_events.extend(self.motion_analyzer.analyze(video_path))
        all_events.extend(self.audio_analyzer.analyze(audio_path))
        
        logger.info(f"Total raw events detected: {len(all_events)}")
        
        candidates = self.merger.merge(all_events, config)
        valid_candidates = self.validator.validate(candidates, config)
        
        for candidate in valid_candidates:
            candidate.score = self.scoring_engine.score_events(candidate.events_contained, config)
            
        ranked = self.ranker.rank(valid_candidates, config)
        
        logger.info(f"Finished highlight analysis. Found {len(ranked)} top candidates.")
        return ranked
