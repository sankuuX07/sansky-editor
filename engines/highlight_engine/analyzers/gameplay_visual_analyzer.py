import cv2
import logging
import numpy as np
from pathlib import Path
from typing import List
from core.models.highlight_models import GameplayVisualEvent

logger = logging.getLogger(__name__)

class GameplayVisualAnalyzer:
    """Analyzes gameplay video for UI structural changes (e.g., kill feed, hit markers)."""
    
    def __init__(self, sample_rate_fps: int = 3, threshold: float = 0.08):
        self.sample_rate_fps = sample_rate_fps
        self.threshold = threshold

    def _get_roi(self, frame: np.ndarray, x_start: float, x_end: float, y_start: float, y_end: float) -> np.ndarray:
        h, w = frame.shape[:2]
        x1, x2 = int(w * x_start), int(w * x_end)
        y1, y2 = int(h * y_start), int(h * y_end)
        return frame[y1:y2, x1:x2]

    def analyze(self, video_path: Path) -> List[GameplayVisualEvent]:
        logger.info(f"Starting GameplayVisualAnalyzer on {video_path}")
        events = []
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error(f"Failed to open video for visual analysis: {video_path}")
            return events

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0
            
        frame_interval = int(max(1, fps / self.sample_rate_fps))
        
        prev_kill_feed = None
        prev_knock_feed = None
        
        current_frame = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if current_frame % frame_interval != 0:
                current_frame += 1
                continue
                
            timestamp = current_frame / fps
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # BGMI Kill Feed (Top Left)
            kill_feed_roi = self._get_roi(gray, 0.0, 0.3, 0.1, 0.5)
            # BGMI Knock/Elim Popup (Bottom Center)
            knock_feed_roi = self._get_roi(gray, 0.3, 0.7, 0.7, 0.9)
            
            # Use Canny to get structural edges rather than just pixel colors
            kill_edges = cv2.Canny(kill_feed_roi, 100, 200)
            knock_edges = cv2.Canny(knock_feed_roi, 100, 200)
            
            if prev_kill_feed is not None:
                kill_diff = cv2.absdiff(kill_edges, prev_kill_feed)
                knock_diff = cv2.absdiff(knock_edges, prev_knock_feed)
                
                kill_change = np.sum(kill_diff) / 255.0 / kill_diff.size
                knock_change = np.sum(knock_diff) / 255.0 / knock_diff.size
                
                if kill_change > self.threshold:
                    # Found a massive structural change in kill feed area
                    events.append(GameplayVisualEvent(
                        start_time=timestamp - 0.5,
                        end_time=timestamp + 0.5,
                        intensity=float(kill_change),
                        evidence_type="kill_feed_activity"
                    ))
                    
                if knock_change > self.threshold:
                    events.append(GameplayVisualEvent(
                        start_time=timestamp - 0.5,
                        end_time=timestamp + 0.5,
                        intensity=float(knock_change),
                        evidence_type="knock_popup_activity"
                    ))
                    
            prev_kill_feed = kill_edges
            prev_knock_feed = knock_edges
            current_frame += 1

        cap.release()
        logger.info(f"Finished Visual Analysis. Found {len(events)} UI events.")
        return events
