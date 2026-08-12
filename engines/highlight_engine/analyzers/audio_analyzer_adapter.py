"""
Adapts audio data to detect peaks, screaming, or silence.
"""
import logging
from typing import List
from pathlib import Path
from core.models.highlight_models import AudioEvent
from core.exceptions.highlight_exceptions import AudioAnalysisError

logger = logging.getLogger(__name__)

class AudioAnalyzerAdapter:
    """Consumes audio streams to detect sonic anomalies."""
    def analyze(self, audio_path: Path) -> List[AudioEvent]:
        logger.info(f"Starting audio analysis on {audio_path}")
        events = []
        try:
            import subprocess
            import re
            
            # Use ffmpeg astats or ebur128 to get loudness
            # ffmpeg -i audio -af ebur128=framelog=verbose -f null -
            cmd = ["ffmpeg", "-i", str(audio_path), "-af", "ebur128=framelog=verbose", "-f", "null", "-"]
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            # Parse the output to find peaks
            # Output format: [Parsed_ebur128_0 @ 0x...] t: 0.100000 M:-120.0 S:-120.0     I: -70.0 LUFS     LRA:   0.0 LU
            pattern = re.compile(r"t:\s*([\d\.]+)\s+M:\s*([\-\d\.]+)")
            
            prev_m = None
            prev_t = None
            
            for line in process.stderr.splitlines():
                match = pattern.search(line)
                if match:
                    t = float(match.group(1))
                    m = float(match.group(2))
                    
                    if prev_m is not None:
                        # Calculate derivative (attack)
                        dm = m - prev_m
                        dt = t - prev_t
                        if dt > 0:
                            attack_rate = dm / dt
                            
                            # If loud AND sudden jump (sharp attack)
                            if m > -15.0 and attack_rate > 50.0:  # e.g. 5 LUFS jump in 0.1s
                                intensity = min(1.0, (m + 20) / 10)
                                events.append(AudioEvent(start_time=t, end_time=t+0.5, intensity=intensity))
                    
                    prev_m = m
                    prev_t = t
            
            # If no peaks, add some defaults to prevent empty lists if perfectly quiet
            if not events:
                logger.debug("No significant high audio intensity events found.")
                
            logger.info("Current local analysis cannot reliably classify audio events (gunshot vs shout) without an audio classification model. Using attack heuristics.")
            logger.debug(f"Detected {len(events)} sharp audio intensity events.")
            return events
        except Exception as e:
            raise AudioAnalysisError(f"Failed to analyze audio: {e}") from e
