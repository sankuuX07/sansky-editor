from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
import cv2

class MetadataWorker(QThread):
    metadata_ready = Signal(str, dict, QImage)  # filepath, metadata, thumbnail
    error_occurred = Signal(str, str) # filepath, error

    def __init__(self, filepaths):
        super().__init__()
        self.filepaths = filepaths

    def run(self):
        for path in self.filepaths:
            try:
                cap = cv2.VideoCapture(path)
                if not cap.isOpened():
                    self.error_occurred.emit(path, "Could not open video file.")
                    continue
                
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                # Get thumbnail (first frame)
                ret, frame = cap.read()
                thumbnail = QImage()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    # Resize thumbnail for performance
                    resized = cv2.resize(frame, (160, 90))
                    h, w, ch = resized.shape
                    bytes_per_line = ch * w
                    thumbnail = QImage(resized.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
                
                cap.release()
                
                metadata = {
                    "fps": round(fps, 2),
                    "duration": round(duration, 2),
                    "resolution": f"{width}x{height}",
                    "estimated_processing_time": f"{round(duration * 1.5, 0)}s" # Dummy estimate based on duration
                }
                
                self.metadata_ready.emit(path, metadata, thumbnail)
            except Exception as e:
                self.error_occurred.emit(path, str(e))
