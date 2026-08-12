import logging
from pathlib import Path
from core.models.highlight_models import HighlightCandidate, HighlightConfig, MotionEvent, AudioEvent, SpeechEvent, SceneEvent
from engines.highlight_engine.core.semantic_classifier import SemanticClassifier
from engines.highlight_engine.core.highlight_scoring_engine import HighlightScoringEngine

logging.basicConfig(level=logging.DEBUG)

def test_synthetic_highlights():
    print("Running Synthetic Highlight Tests...")
    classifier = SemanticClassifier()
    scorer = HighlightScoringEngine()
    config = HighlightConfig()
    
    # 1. Short gameplay with one fight
    fight_candidate = HighlightCandidate(start_time=10.0, end_time=15.0, score=None, events_contained=[
        MotionEvent(10.0, 10.5, 0.8),
        AudioEvent(10.2, 10.7, 0.9),
        MotionEvent(12.0, 12.5, 0.7),
        AudioEvent(12.1, 12.6, 0.8)
    ])
    
    # 2. Gameplay containing a clutch
    clutch_candidate = HighlightCandidate(start_time=30.0, end_time=40.0, score=None, events_contained=[
        MotionEvent(30.0, 30.5, 0.9),
        AudioEvent(30.2, 30.7, 0.9),
        SpeechEvent(31.0, 32.0, 1.0, "last guy is low"),
        MotionEvent(35.0, 35.5, 0.9),
        AudioEvent(35.2, 35.7, 0.9),
        SpeechEvent(36.0, 37.0, 1.0, "nice clutch!"),
    ])
    
    # 3. Boring section
    boring_candidate = HighlightCandidate(start_time=50.0, end_time=80.0, score=None, events_contained=[
        MotionEvent(50.0, 50.5, 0.4),
        MotionEvent(65.0, 65.5, 0.3)
    ])
    
    candidates = [fight_candidate, clutch_candidate, boring_candidate]
    classified = classifier.classify(candidates, config)
    
    for c in classified:
        c.score = scorer.score_candidate(c, config)
        print(f"Time: {c.start_time}-{c.end_time} | Type: {c.semantic_type} | Conf: {c.confidence} | Score: {c.score.total_score} | Reason: {c.reason}")
        
if __name__ == "__main__":
    test_synthetic_highlights()
