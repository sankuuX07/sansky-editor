"""
Detects high motion or action density sequences.
"""
import logging
from typing import List
from pathlib import Path
from core.models.highlight_models import MotionEvent
from core.exceptions.highlight_exceptions import MotionAnalysisError

logger = logging.getLogger(__name__)

class MotionAnalyzer:
    """Analyzes pixel deltas to find action-heavy moments."""
    def analyze(self, video_path: Path) -> List[MotionEvent]:
        logger.info(f"Starting motion analysis on {video_path}")
        events = []
        try:
            import cv2
            import numpy as np
            
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise MotionAnalysisError("Could not open video file.")
                
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            
            prev_frame = None
            frame_idx = 0
            frame_skip = int(fps / 2) # check twice a second
            
            while True:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    break
                    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if prev_frame is not None:
                    diff = cv2.absdiff(gray, prev_frame)
                    score = np.mean(diff)
                    if score > 15.0 and score < 50.0:  # High motion but not a full scene cut
                        time_sec = frame_idx / fps
                        events.append(MotionEvent(start_time=time_sec, end_time=time_sec+0.5, intensity=float(score/255.0)))
                
                prev_frame = gray
                frame_idx += frame_skip
                
            cap.release()

            logger.debug(f"Detected {len(events)} motion events.")
            return events
        except ImportError:
            logger.warning("OpenCV not installed, returning empty motion events.")
            return events
        except Exception as e:
            raise MotionAnalysisError(f"Failed to analyze motion: {e}") from e
