"""
Composes the final thumbnail image using Pillow.
"""
import logging
import shutil
from pathlib import Path
from core.models.thumbnail_models import ThumbnailCandidate
from core.models.shorts_models import OutputSettings

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageEnhance, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("Pillow not installed. Thumbnail composer will simply copy the frame.")
    PIL_AVAILABLE = False

class ThumbnailComposer:
    def compose(self, candidate: ThumbnailCandidate, settings: OutputSettings, output_path: Path) -> None:
        if not candidate.frame_path or not candidate.frame_path.exists():
            return
            
        if not PIL_AVAILABLE:
            shutil.copy2(candidate.frame_path, output_path)
            return
            
        try:
            with Image.open(candidate.frame_path) as img:
                # 1. Crop/Scale to target aspect ratio (16:9, 9:16, 1:1)
                img = self._apply_aspect_ratio(img, settings.thumbnail_aspect_ratio)
                
                # 2. Enhancement
                img = self._apply_enhancements(img, settings.thumbnail_style)
                
                # 3. Text Overlay
                if settings.thumbnail_text:
                    img = self._apply_text(img, settings.thumbnail_text)
                    
                # Save as high quality JPG
                img.save(output_path, "JPEG", quality=95)
                
        except Exception as e:
            logger.error(f"Failed to compose thumbnail: {e}")
            # Fallback
            shutil.copy2(candidate.frame_path, output_path)
            
    def _apply_aspect_ratio(self, img, aspect_ratio: str):
        # Default img from standard 1080p video is 1920x1080 (16:9)
        w, h = img.size
        
        if aspect_ratio == "16:9":
            return img
            
        if aspect_ratio == "9:16":
            # Crop middle
            target_w = int(h * 9 / 16)
            left = (w - target_w) // 2
            return img.crop((left, 0, left + target_w, h))
            
        if aspect_ratio == "1:1":
            target_w = h
            left = (w - target_w) // 2
            return img.crop((left, 0, left + target_w, h))
            
        return img
        
    def _apply_enhancements(self, img, style: str):
        if style == "CLEAN":
            # minimal contrast boost
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.05)
            
        elif style == "GAMING":
            # Vibrant
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.15)
            
        elif style == "INTENSE":
            # Very strong
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.4)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            # pseudo-sharpening could be done with ImageFilter but we keep it simple
            
        return img
        
    def _apply_text(self, img, text: str):
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        try:
            # Try to load a generic default font
            font = ImageFont.truetype("arial.ttf", size=int(h * 0.1))
        except IOError:
            # Fallback to default
            font = ImageFont.load_default()
            
        # Place text at bottom center (safe area)
        try:
            # PIL 10+
            bbox = font.getbbox(text)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(text, font=font)
            
        x = (w - text_w) / 2
        y = h - text_h - int(h * 0.1) # 10% from bottom
        
        # Draw outline (stroke)
        stroke_color = "black"
        stroke_width = 3
        
        for adj_x in range(-stroke_width, stroke_width+1):
            for adj_y in range(-stroke_width, stroke_width+1):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=stroke_color)
                
        # Draw main text
        draw.text((x, y), text, font=font, fill="white")
        
        return img
