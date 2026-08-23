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
                    
                    from engines.editing_engine.editing_engine import EditingEngine
                    editing_engine = EditingEngine()
                    
                    concat_list_path = proj.premiere_project_path.parent / "concat_list.txt"
                    clips_to_concat = []
                    
                    debug_report_path = proj.premiere_project_path.parent / "editing_report.txt"
                    
                    with open(debug_report_path, "w", encoding="utf-8") as dr:
                        dr.write(f"SANSKY AI EDITOR - M7 EDITING REPORT\n")
                        dr.write("="*50 + "\n\n")
                        
                        with open(concat_list_path, "w", encoding="utf-8") as f:
                            for i, clip in enumerate(proj.clips):
                                clip_out = proj.premiere_project_path.parent / f"clip_{i}.mp4"
                                
                                dr.write(f"HIGHLIGHT #{i+1}\n")
                                dr.write(f"Source: {int(clip.start_time//60):02d}:{int(clip.start_time%60):02d} -> {int(clip.end_time//60):02d}:{int(clip.end_time%60):02d}\n")
                                dr.write(f"Editing Style: {proj.settings.editing_style}\n")
                                dr.write("Editing Decisions:\n")
                                
                                vf_str, af_str = editing_engine.build_ffmpeg_filters(clip)
                                
                                if clip.editing_timeline and clip.editing_timeline.editing_events:
                                    for ev in clip.editing_timeline.editing_events:
                                        dr.write(f"\n{ev.start_time - clip.start_time:.1f}s\n")
                                        dr.write(f"{ev.event_type}\n")
                                        dr.write(f"Reason: {ev.reason}\n")
                                else:
                                    dr.write("None\n")
                                dr.write("-" * 50 + "\n\n")
                                
                                segments = editing_engine.get_time_warp_segments(clip)
                                
                                for seg_idx, seg in enumerate(segments):
                                    seg_out = proj.premiere_project_path.parent / f"clip_{i}_seg_{seg_idx}.mp4"
                                    
                                    cmd = [
                                        "ffmpeg", "-y", "-i", str(clip.source_video),
                                        "-ss", str(seg['start']), "-to", str(seg['end'])
                                    ]
                                    
                                    seg_vf_str = vf_str
                                    seg_af_str = af_str
                                    
                                    if seg['speed'] != 1.0:
                                        # Apply setpts and atempo
                                        speed = seg['speed']
                                        pts_mult = 1.0 / speed
                                        
                                        time_vf = f"setpts={pts_mult}*PTS"
                                        time_af = f"atempo={speed}"
                                        
                                        if seg_vf_str:
                                            seg_vf_str = f"{seg_vf_str},{time_vf}"
                                        else:
                                            seg_vf_str = time_vf
                                            
                                        if seg_af_str:
                                            seg_af_str = f"{seg_af_str},{time_af}"
                                        else:
                                            seg_af_str = time_af
                                            
                                        dr.write(f"Segment {seg_idx} ({seg['start']:.1f}-{seg['end']:.1f}): Time warp {speed}x\n")
                                        
                                    if seg_vf_str:
                                        cmd.extend(["-vf", seg_vf_str])
                                    if seg_af_str:
                                        cmd.extend(["-af", seg_af_str])
                                        
                                    cmd.extend(["-c:v", "libx264", "-c:a", "aac", str(seg_out)])
                                    
                                    try:
                                        subprocess.run(cmd, capture_output=True, check=True)
                                    except subprocess.CalledProcessError as err:
                                        logger.warning(f"Failed to apply filters for clip {i} seg {seg_idx}. Error: {err.stderr}")
                                        fallback_cmd = [
                                            "ffmpeg", "-y", "-i", str(clip.source_video),
                                            "-ss", str(seg['start']), "-to", str(seg['end']),
                                            "-c:v", "libx264", "-c:a", "aac", str(seg_out)
                                        ]
                                        subprocess.run(fallback_cmd, capture_output=True, check=True)
                                    
                                    f.write(f"file '{seg_out.name}'\n")
                                    clips_to_concat.append(seg_out)
                                
                                # Apply transitions between clips
                                if i < len(proj.clips) - 1:
                                    if proj.settings.transition_style == "FLASH":
                                        flash_out = proj.premiere_project_path.parent / f"trans_flash_{i}.mp4"
                                        flash_cmd = [
                                            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=white:s=1080x1920:d=0.2",
                                            "-f", "lavfi", "-i", "anullsrc=d=0.2",
                                            "-c:v", "libx264", "-c:a", "aac", str(flash_out)
                                        ]
                                        subprocess.run(flash_cmd, capture_output=True, check=True)
                                        f.write(f"file '{flash_out.name}'\n")
                                        clips_to_concat.append(flash_out)
                                
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
