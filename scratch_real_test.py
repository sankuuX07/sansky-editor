import logging
from pathlib import Path
from engines.highlight_engine.highlight_analyzer import HighlightAnalyzer
from core.models.highlight_models import HighlightConfig
from app.services.engine_manager import EngineManager
from core.dependency_injection.container import container
from engines.ai_engine.ai_engine import AIEngine

logging.basicConfig(level=logging.INFO)

def test_real_video():
    print("Running Pipeline on Dummy Gameplay...")
    engine_manager = EngineManager()
    ai_engine = AIEngine()
    ai_engine.initialize()
    engine_manager.register(ai_engine)
    container.register_instance(EngineManager, engine_manager)
    
    analyzer = HighlightAnalyzer()
    config = HighlightConfig(min_clip_duration_sec=0.1)
    video_path = Path("test_assets/dummy_gameplay.mp4")
    
    candidates = analyzer.analyze_video(video_path, video_path, config)
    for c in candidates:
        print(f"Time: {c.start_time}-{c.end_time} | Type: {c.semantic_type} | Conf: {c.confidence} | Score: {c.score.total_score if c.score else None}")
        
if __name__ == "__main__":
    test_real_video()
