import logging
from core.models.highlight_models import HighlightCandidate, HighlightConfig, MotionEvent, AudioEvent, SpeechEvent, GameplayVisualEvent
from engines.highlight_engine.core.semantic_classifier import SemanticClassifier
from engines.highlight_engine.core.highlight_scoring_engine import HighlightScoringEngine

logging.basicConfig(level=logging.INFO)

def test_new_intelligence():
    print("\n--- Testing Highlight Intelligence (V2) ---")
    classifier = SemanticClassifier()
    scorer = HighlightScoringEngine()
    config = HighlightConfig()
    
    # Candidate 1: Random loud driving or wind (High motion + loud audio)
    random_clip = HighlightCandidate(start_time=10.0, end_time=25.0, score=None, events_contained=[
        MotionEvent(10.0, 10.5, 0.9), AudioEvent(10.2, 10.7, 0.9),
        MotionEvent(15.0, 15.5, 0.8), AudioEvent(15.2, 15.7, 0.8),
        MotionEvent(20.0, 20.5, 0.9), AudioEvent(20.2, 20.7, 0.9)
    ])
    
    # Candidate 2: Actual Fight (Motion + Audio + Kill Feed UI Edge Change)
    fight_clip = HighlightCandidate(start_time=40.0, end_time=50.0, score=None, events_contained=[
        MotionEvent(40.0, 40.5, 0.9), AudioEvent(40.2, 40.7, 0.9), # Sharp audio attack
        GameplayVisualEvent(42.0, 42.5, 0.8, "kill_feed_activity"),
        GameplayVisualEvent(45.0, 45.5, 0.7, "knock_popup_activity"),
        MotionEvent(48.0, 48.5, 0.9), AudioEvent(48.2, 48.7, 0.9)
    ])
    
    # Candidate 3: Clutch Moment (Sustained action + Visuals + Speech)
    clutch_clip = HighlightCandidate(start_time=60.0, end_time=90.0, score=None, events_contained=[
        MotionEvent(60.0, 60.5, 0.9), AudioEvent(60.2, 60.7, 0.9),
        GameplayVisualEvent(65.0, 65.5, 0.8, "kill_feed_activity"),
        SpeechEvent(70.0, 75.0, 1.0, "last guy is low, clutch it"),
        MotionEvent(80.0, 80.5, 0.9), AudioEvent(80.2, 80.7, 0.9),
        GameplayVisualEvent(85.0, 85.5, 0.9, "kill_feed_activity")
    ])
    
    candidates = [random_clip, fight_clip, clutch_clip]
    classified = classifier.classify(candidates, config)
    
    for i, c in enumerate(classified, 1):
        c.score = scorer.score_candidate(c, config)
        print(f"\nHighlight #{i} ({c.start_time} - {c.end_time})")
        print(f"Semantic Type: {c.semantic_type} | Confidence: {c.confidence}")
        print(f"Engagement Score: {c.engagement_score} | Raw Base Score: {c.score.total_score}")
        print(f"Evidence: {c.evidence}")
        print(f"Reason: {c.reason}")
        
if __name__ == "__main__":
    test_new_intelligence()
