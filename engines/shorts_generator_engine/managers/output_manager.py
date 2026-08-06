"""
Manages physical output files.
"""
import logging
from pathlib import Path
from core.models.shorts_models import ProcessingResult

logger = logging.getLogger(__name__)

class OutputManager:
    def finalize(self, result: ProcessingResult) -> None:
        logger.info(f"Finalizing output for request {result.request_id}")
        
        for proj in result.projects:
            if proj.premiere_project_path:
                proj.premiere_project_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the XML if it was passed via context (we will inject it)
                xml_data = getattr(proj, '_xml_data', None)
                if xml_data:
                    with open(proj.premiere_project_path, "w", encoding="utf-8") as f:
                        f.write(xml_data)
                else:
                    proj.premiere_project_path.touch(exist_ok=True)
                    
                # Generate real output video
                try:
                    import subprocess
                    import os
                    from core.dependency_injection.container import container
                    from app.services.engine_manager import EngineManager
                    engine_manager = container.resolve(EngineManager)
                    video_engine = engine_manager.get_engine("video_engine")
                    
                    concat_list_path = proj.premiere_project_path.parent / "concat_list.txt"
                    clips_to_concat = []
                    
                    with open(concat_list_path, "w", encoding="utf-8") as f:
                        for i, clip in enumerate(proj.clips):
                            clip_out = proj.premiere_project_path.parent / f"clip_{i}.mp4"
                            # We use subprocess to cut since it's synchronous and simple
                            cmd = [
                                "ffmpeg", "-y", "-i", str(clip.source_video),
                                "-ss", str(clip.start_time), "-to", str(clip.end_time),
                                "-c:v", "libx264", "-c:a", "aac", str(clip_out)
                            ]
                            subprocess.run(cmd, capture_output=True, check=True)
                            
                            f.write(f"file '{clip_out.name}'\n")
                            clips_to_concat.append(clip_out)
                            
                    final_out = proj.premiere_project_path.parent / "output.mp4"
                    cmd_concat = [
                        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(concat_list_path),
                        "-c", "copy", str(final_out)
                    ]
                    subprocess.run(cmd_concat, capture_output=True, check=True)
                    logger.info(f"Generated final output video at {final_out}")
                    
                    # Cleanup temp clips
                    for c in clips_to_concat:
                        if c.exists(): c.unlink()
                    if concat_list_path.exists(): concat_list_path.unlink()
                    
                except Exception as e:
                    logger.error(f"Failed to generate output video: {e}")
