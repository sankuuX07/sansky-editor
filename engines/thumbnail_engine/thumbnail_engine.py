"""
The Thumbnail Engine Facade.
"""
import logging
from pathlib import Path
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.models.shorts_models import GeneratedClip, OutputSettings
from core.models.thumbnail_models import ThumbnailReport
from core.exceptions.exceptions import EngineInitError

from engines.thumbnail_engine.generators.candidate_generator import CandidateGenerator
from engines.thumbnail_engine.analyzers.frame_analyzer import FrameAnalyzer
from engines.thumbnail_engine.render.thumbnail_composer import ThumbnailComposer
from engines.video_engine.ffmpeg.ffmpeg_manager import FFmpegManager
from engines.video_engine.extractor.frame_extractor import FrameExtractor

class ThumbnailEngine(BaseEngine):
    def __init__(self) -> None:
        super().__init__("thumbnail_engine")
        self.ffmpeg_manager = FFmpegManager()
        self.extractor = FrameExtractor(self.ffmpeg_manager)
        self.candidate_generator = CandidateGenerator()
        self.analyzer = FrameAnalyzer()
        self.composer = ThumbnailComposer()
        
    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Thumbnail Engine...")
        self._status = EngineStatus.INITIALIZED
        self.is_initialized = True
        self.logger.info("Thumbnail Engine initialized successfully.")
        
    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized ThumbnailEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Thumbnail Engine started.")
        
    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Thumbnail Engine stopped.")
        
    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Thumbnail Engine shutdown.")
        
    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING
        
    def generate_thumbnail(self, clip: GeneratedClip, settings: OutputSettings, output_dir: Path) -> ThumbnailReport:
        """
        Generates the best possible thumbnail for a clip.
        Returns a ThumbnailReport detailing the selection.
        """
        self.logger.info(f"Generating thumbnail for clip {clip.clip_id}")
        report = ThumbnailReport()
        output_dir.mkdir(parents=True, exist_ok=True)
        temp_dir = output_dir / "temp_candidates"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Generate Candidates based on M6 events
            candidates = self.candidate_generator.generate(clip)
            
            # 2. Extract frames for candidates
            timestamps = [c.timestamp for c in candidates]
            extracted_paths = self.extractor.extract_multiple_frames(clip.source_video, timestamps, temp_dir)
            
            for i, cand in enumerate(candidates):
                cand.frame_path = extracted_paths[i]
                
            # 3. Analyze quality
            best_candidate = None
            highest_score = -1.0
            
            for cand in candidates:
                self.analyzer.analyze(cand)
                # Combine priority + sharpness
                cand.final_score = (cand.event_priority * 0.4) + (cand.sharpness * 0.6)
                if cand.final_score > highest_score:
                    highest_score = cand.final_score
                    best_candidate = cand
                    
            if not best_candidate and candidates:
                best_candidate = candidates[0]
                
            if best_candidate:
                # 4. Compose Thumbnail
                final_path = output_dir / f"{clip.clip_id}_thumbnail.jpg"
                self.composer.compose(best_candidate, settings, final_path)
                
                report.selected_timestamp = best_candidate.timestamp
                report.event_context = best_candidate.reason
                report.candidate_count = len(candidates)
                report.sharpness_score = best_candidate.sharpness
                report.final_path = final_path
                
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {e}")
            
        finally:
            # Cleanup temp frames
            if temp_dir.exists():
                for f in temp_dir.glob("*.jpg"):
                    f.unlink()
                temp_dir.rmdir()
                
        return report
