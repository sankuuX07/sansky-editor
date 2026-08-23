"""
Analyzes extracted frames using OpenCV for sharpness and exposure.
"""
import logging
from core.models.thumbnail_models import ThumbnailCandidate

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    logger.warning("OpenCV not installed. Frame analyzer will fallback to naive scoring.")
    CV2_AVAILABLE = False

class FrameAnalyzer:
    def analyze(self, candidate: ThumbnailCandidate) -> None:
        if not candidate.frame_path or not candidate.frame_path.exists():
            return
            
        if CV2_AVAILABLE:
            try:
                # Read image in grayscale
                img = cv2.imread(str(candidate.frame_path), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    return
                    
                # 1. Sharpness (Laplacian Variance)
                # The higher the variance, the sharper the image.
                variance = cv2.Laplacian(img, cv2.CV_64F).var()
                
                # Normalize sharpness roughly (variance can go up to 1000s, usually >100 is ok)
                norm_sharp = min(1.0, variance / 500.0)
                candidate.sharpness = norm_sharp
                
                # 2. Exposure (Mean brightness)
                mean_bright = np.mean(img)
                # Optimal brightness is usually between 50 and 200.
                if 50 < mean_bright < 200:
                    candidate.exposure = 1.0
                else:
                    # Penalize over/under exposed frames
                    candidate.exposure = 0.5
                    
            except Exception as e:
                logger.error(f"Error analyzing frame {candidate.frame_path}: {e}")
                candidate.sharpness = 0.5
                candidate.exposure = 0.5
        else:
            # Fallback if cv2 is not available
            candidate.sharpness = 0.5
            candidate.exposure = 0.5
