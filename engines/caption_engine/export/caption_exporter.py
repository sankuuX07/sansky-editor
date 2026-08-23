"""
Writes formatted captions to disk safely.
"""
import logging
from pathlib import Path
from core.models.caption_models import CaptionTimeline, CaptionExportSettings, ExportFormat
from engines.caption_engine.export.caption_formatter import CaptionFormatter
from core.exceptions.caption_exceptions import CaptionExportError

logger = logging.getLogger(__name__)

class CaptionExporter:
    """Exports timelines to files."""
    def __init__(self, formatter: CaptionFormatter) -> None:
        self.formatter = formatter

    def export(self, timeline: CaptionTimeline, settings: CaptionExportSettings) -> Path:
        """Export timeline to disk based on settings."""
        try:
            settings.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = settings.output_dir / f"{settings.filename_prefix}.{settings.format.value}"
            
            content = ""
            if settings.format == ExportFormat.SRT:
                content = self.formatter.format_srt(timeline)
            elif settings.format == ExportFormat.VTT:
                content = self.formatter.format_vtt(timeline)
            elif settings.format == ExportFormat.ASS:
                content = self.formatter.format_ass(timeline)
            else:
                raise CaptionExportError(f"Export format {settings.format.value} is not fully implemented yet.")
                
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            logger.info(f"Successfully exported captions to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to export captions: {e}")
            raise CaptionExportError(f"Export failed: {e}") from e
