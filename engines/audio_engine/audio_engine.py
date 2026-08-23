"""
The Audio Engine Facade.
"""
import logging
import shutil
from pathlib import Path
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError

from engines.audio_engine.core.audio_analyzer import AudioAnalyzer
from engines.audio_engine.core.audio_mixer import AudioMixer
from core.models.audio_models import AudioTimeline, AudioAnalysis
from core.models.shorts_models import OutputSettings

class AudioEngine(BaseEngine):
    def __init__(self) -> None:
        super().__init__("audio_engine")
        self.analyzer = AudioAnalyzer()
        self.mixer = AudioMixer()
        self.last_analysis = None
        
    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Audio Engine...")
        self._status = EngineStatus.INITIALIZED
        self.is_initialized = True
        self.logger.info("Audio Engine initialized successfully.")
        
    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized AudioEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Audio Engine started.")
        
    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Audio Engine stopped.")
        
    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Audio Engine shutdown.")
        
    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING
        
    def process_audio(self, input_video: Path, output_video: Path, timeline: AudioTimeline, settings: OutputSettings) -> AudioAnalysis:
        """Analyzes and mixes the audio, generating a final output video."""
        self.logger.info(f"Processing audio for {input_video}")
        
        try:
            # 1. Analyze existing audio
            analysis = self.analyzer.analyze(input_video)
            self.last_analysis = analysis
            
            # 2. Mix audio according to events and settings
            self.mixer.mix(input_video, output_video, timeline, settings)
            
            return analysis
        except Exception as e:
            self.logger.error(f"AudioEngine failed to process audio: {e}")
            # Fallback: copy input to output if we fail
            if input_video.exists() and not output_video.exists():
                shutil.copy2(input_video, output_video)
            raise
