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
from engines.highlight_engine.analyzers.speech_analyzer import SpeechAnalyzer
from engines.highlight_engine.analyzers.gameplay_visual_analyzer import GameplayVisualAnalyzer
from engines.highlight_engine.core.highlight_merger import HighlightMerger
from engines.highlight_engine.core.semantic_classifier import SemanticClassifier
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
        self.speech_analyzer = SpeechAnalyzer()
        self.visual_analyzer = GameplayVisualAnalyzer()
        
        self.merger = HighlightMerger()
        self.semantic_classifier = SemanticClassifier()
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
        all_events.extend(self.speech_analyzer.analyze(audio_path))
        all_events.extend(self.visual_analyzer.analyze(video_path))
        
        logger.info(f"Total raw events detected: {len(all_events)}")
        
        candidates = self.merger.merge(all_events, config)
        candidates = self.semantic_classifier.classify(candidates, config)
        valid_candidates = self.validator.validate(candidates, config)
        
        for candidate in valid_candidates:
            candidate.score = self.scoring_engine.score_candidate(candidate, config)
            
        ranked = self.ranker.rank(valid_candidates, config)
        
        self._generate_debug_report(ranked, video_path)
        
        logger.info(f"Finished highlight analysis. Found {len(ranked)} top candidates.")
        return ranked

    def _generate_debug_report(self, ranked: List[HighlightCandidate], video_path: Path) -> None:
        report_path = video_path.parent / f"{video_path.stem}_debug_report.txt"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("SANSKY AI EDITOR - HIGHLIGHT DEBUG REPORT\n")
                f.write("="*50 + "\n\n")
                
                for i, c in enumerate(ranked, 1):
                    start = f"{int(c.start_time//60):02d}:{int(c.start_time%60):02d}"
                    end = f"{int(c.end_time//60):02d}:{int(c.end_time%60):02d}"
                    
                    f.write(f"Highlight #{i}\n")
                    f.write(f"{start} - {end}\n\n")
                    
                    f.write(f"Type: {c.semantic_type} ({c.confidence:.2f})\n")
                    if c.score:
                        f.write(f"Overall Score: {c.score.total_score}\n")
                        for k, v in c.score.components.items():
                            f.write(f"  - {k}: {v:.2f}\n")
                    
                    f.write(f"Engagement Score: {c.engagement_score}\n\n")
                    
                    f.write("Evidence:\n")
                    for ev in c.evidence:
                        f.write(f"  * {ev}\n")
                        
                    f.write(f"\nReasoning: {c.reason}\n")
                    f.write("-" * 50 + "\n\n")
            logger.info(f"Debug report generated at {report_path}")
        except Exception as e:
            logger.error(f"Failed to write debug report: {e}")
