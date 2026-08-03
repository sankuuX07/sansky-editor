"""
The Highlight Engine facade.
"""
import logging
from pathlib import Path
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError
from core.models.highlight_models import HighlightConfig, HighlightTimeline, HighlightStatistics
from engines.highlight_engine.highlight_analyzer import HighlightAnalyzer
from engines.highlight_engine.export.highlight_exporter import HighlightExporter

class HighlightEngine(BaseEngine):
    """Facade for the Highlight Detection subsystem."""
    
    def __init__(self) -> None:
        super().__init__("highlight_engine")
        self.analyzer = HighlightAnalyzer()
        self.exporter = HighlightExporter()
        self.default_config = HighlightConfig()

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Highlight Engine...")
        try:
            self._status = EngineStatus.INITIALIZED
            self.is_initialized = True
            self.logger.info("Highlight Engine initialized successfully.")
        except Exception as e:
            self._status = EngineStatus.ERROR
            raise EngineInitError("Failed to initialize HighlightEngine") from e

    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized HighlightEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Highlight Engine started.")

    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Highlight Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Highlight Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING

    def process_video(self, video_id: str, video_path: Path, audio_path: Path, config: HighlightConfig = None) -> HighlightTimeline:
        """Process a video to find highlights and return a timeline."""
        cfg = config or self.default_config
        
        candidates = self.analyzer.analyze_video(video_path, audio_path, cfg)
        
        timeline = HighlightTimeline(
            video_id=video_id,
            highlights=candidates
        )
        return timeline
        
    def export_timeline(self, timeline: HighlightTimeline, output_path: Path) -> Path:
        """Export the timeline to a structured JSON file."""
        return self.exporter.export_to_json(timeline, output_path)
