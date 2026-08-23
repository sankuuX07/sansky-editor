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

    def format_ass(self, timeline: CaptionTimeline) -> str:
        """Convert timeline to ASS (.ass) format."""
        try:
            # We determine style dynamically from the preset if available.
            # Default to some standard values.
            font_name = "Arial"
            font_size = 80
            pri_color = "&H00FFFFFF" # BGR hex in ASS
            outline_color = "&H00000000"
            back_color = "&H00000000"
            bold = -1
            margin_v = 150
            alignment = 2 # Bottom center
            
            # Map styling if preset_used is available
            preset_name = getattr(timeline, "preset_name", "GAMING").upper()
            if preset_name == "GAMING":
                font_name = "Impact"
                font_size = 90
                pri_color = "&H0000FFFF" # Yellow
                outline_color = "&H00000000"
            elif preset_name == "STREAMER":
                font_name = "Verdana"
                font_size = 85
                bold = -1
                pri_color = "&H00FFFFFF"
            elif preset_name == "CINEMATIC":
                font_name = "Times New Roman"
                font_size = 60
                bold = 0
                pri_color = "&H00FFFFFF"
                margin_v = 100
                
            ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{pri_color},&H000000FF,{outline_color},{back_color},{bold},0,0,0,100,100,0,0,1,3,0,{alignment},10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            lines = [ass_header]
            
            for seg in timeline.segments:
                start_str = self._format_time_ass(seg.start_time)
                end_str = self._format_time_ass(seg.end_time)
                
                # Build ASS text with animation tags for emphasized words
                ass_text = ""
                
                if hasattr(seg, 'words') and seg.words:
                    for w in seg.words:
                        if getattr(w, "is_emphasized", False):
                            if preset_name == "GAMING":
                                # Pop-in scale and color change for emphasis
                                ass_text += f"{{\\c&H000000FF&}}{{\\fscx120\\fscy120}}{w.text}{{\\fscx100\\fscy100}}{{\\c{pri_color}}} "
                            else:
                                ass_text += f"{{\\c&H000000FF&}}{w.text}{{\\c{pri_color}}} "
                        else:
                            ass_text += f"{w.text} "
                else:
                    ass_text = seg.text
                    
                ass_text = ass_text.strip()
                
                # Add dialogue line
                lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{ass_text}")
                
            return "".join(lines)
        except Exception as e:
            raise CaptionFormattingError(f"Failed to format ASS: {e}") from e

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

    def _format_time_ass(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100) # centiseconds for ASS
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
