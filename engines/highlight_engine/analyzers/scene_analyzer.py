"""
Detects scene changes and visual transitions.
"""
import logging
from typing import List
from pathlib import Path
from core.models.highlight_models import SceneEvent
from core.exceptions.highlight_exceptions import SceneAnalysisError

logger = logging.getLogger(__name__)

class SceneAnalyzer:
    """Analyzes a video for scene changes."""
    def analyze(self, video_path: Path) -> List[SceneEvent]:
        logger.info(f"Starting scene analysis on {video_path}")
        events = []
        try:
            import cv2
            import numpy as np
            
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise SceneAnalysisError("Could not open video file.")
                
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            
            prev_frame = None
            frame_idx = 0
            
            # Read 1 frame per second to speed up processing
            frame_skip = int(fps)
            
            while True:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    break
                    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if prev_frame is not None:
                    diff = cv2.absdiff(gray, prev_frame)
                    score = np.mean(diff)
                    if score > 30.0:  # Threshold for scene change
                        time_sec = frame_idx / fps
                        events.append(SceneEvent(start_time=time_sec, end_time=time_sec+1.0, intensity=float(score/255.0)))
                
                prev_frame = gray
                frame_idx += frame_skip
                
            cap.release()
            
            logger.debug(f"Detected {len(events)} scene events.")
            return events
        except ImportError:
            logger.warning("OpenCV not installed, returning empty scene events.")
            return events
        except Exception as e:
            raise SceneAnalysisError(f"Failed to analyze scenes: {e}") from e
