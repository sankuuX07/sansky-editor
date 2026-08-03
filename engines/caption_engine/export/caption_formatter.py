"""
Formats internal Timeline data into textual outputs (SRT/VTT).
"""
import logging
from core.models.caption_models import CaptionTimeline
from core.exceptions.caption_exceptions import CaptionFormattingError

logger = logging.getLogger(__name__)

class CaptionFormatter:
    """Formats timelines to string representations."""
    
    def format_srt(self, timeline: CaptionTimeline) -> str:
        """Convert timeline to SubRip (.srt) format."""
        try:
            lines = []
            for seg in timeline.segments:
                start_str = self._format_time_srt(seg.start_time)
                end_str = self._format_time_srt(seg.end_time)
                lines.append(str(seg.index))
                lines.append(f"{start_str} --> {end_str}")
                lines.append(seg.text)
                lines.append("") # Blank line
            return "\n".join(lines)
        except Exception as e:
            raise CaptionFormattingError(f"Failed to format SRT: {e}") from e

    def format_vtt(self, timeline: CaptionTimeline) -> str:
        """Convert timeline to WebVTT (.vtt) format."""
        try:
            lines = ["WEBVTT\n"]
            for seg in timeline.segments:
                start_str = self._format_time_vtt(seg.start_time)
                end_str = self._format_time_vtt(seg.end_time)
                lines.append(str(seg.index))
                lines.append(f"{start_str} --> {end_str}")
                lines.append(seg.text)
                lines.append("")
            return "\n".join(lines)
        except Exception as e:
            raise CaptionFormattingError(f"Failed to format VTT: {e}") from e

    def _format_time_srt(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
    def _format_time_vtt(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
