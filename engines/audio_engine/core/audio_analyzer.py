"""
Analyzes audio files using FFmpeg to determine loudness, peaks, and silence.
"""
import logging
import subprocess
import re
from pathlib import Path
from core.models.audio_models import AudioAnalysis

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def analyze(self, audio_path: Path) -> AudioAnalysis:
        logger.info(f"Analyzing audio: {audio_path}")
        analysis = AudioAnalysis()
        
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return analysis
            
        try:
            # We run ffmpeg with volumedetect and silencedetect
            cmd = [
                "ffmpeg", "-i", str(audio_path),
                "-af", "volumedetect,silencedetect=noise=-50dB:d=1.5",
                "-f", "null", "-"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            output = result.stderr
            
            # Parse volumedetect
            # [Parsed_volumedetect_0 @ 0x...] mean_volume: -23.5 dB
            # [Parsed_volumedetect_0 @ 0x...] max_volume: -2.1 dB
            mean_match = re.search(r"mean_volume:\s+([-0-9.]+)\s+dB", output)
            if mean_match:
                analysis.integrated_loudness = float(mean_match.group(1))
                
            max_match = re.search(r"max_volume:\s+([-0-9.]+)\s+dB", output)
            if max_match:
                analysis.peak_level = float(max_match.group(1))
                
            # Parse silencedetect
            # [silencedetect @ 0x...] silence_start: 4.5
            # [silencedetect @ 0x...] silence_end: 6.2 | silence_duration: 1.7
            silence_starts = re.findall(r"silence_start:\s+([0-9.]+)", output)
            silence_ends = re.findall(r"silence_end:\s+([0-9.]+)", output)
            
            for s_start, s_end in zip(silence_starts, silence_ends):
                analysis.silence_regions.append((float(s_start), float(s_end)))
                
        except Exception as e:
            logger.error(f"Failed to analyze audio: {e}")
            
        return analysis
