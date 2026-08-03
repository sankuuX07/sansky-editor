"""
Exports highlight timelines to disk.
"""
import logging
import json
from pathlib import Path
from core.models.highlight_models import HighlightTimeline

logger = logging.getLogger(__name__)

class HighlightExporter:
    """Exports highlight metadata."""
    
    def export_to_json(self, timeline: HighlightTimeline, output_path: Path) -> Path:
        """Export timeline to a JSON file."""
        logger.info(f"Exporting highlight timeline to {output_path}")
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "video_id": timeline.video_id,
                "highlights": []
            }
            
            for h in timeline.highlights:
                data["highlights"].append({
                    "start_time": h.start_time,
                    "end_time": h.end_time,
                    "score": h.score.total_score if h.score else 0.0,
                    "components": h.score.components if h.score else {},
                    "event_count": len(h.events_contained)
                })
                
            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)
                
            return output_path
        except Exception as e:
            logger.error(f"Failed to export highlights: {e}", exc_info=True)
            raise e
