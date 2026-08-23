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
                    
                    # Track time for absolute audio timeline
                    current_output_time = 0.0
                    from core.models.audio_models import AudioTimeline, AudioEvent
                    audio_timeline = AudioTimeline(video_id=proj.project_id)
                    
                    with open(debug_report_path, "w", encoding="utf-8") as dr:
                        dr.write(f"SANSKY AI EDITOR - M7/M9 EDITING REPORT\n")
                        dr.write("="*50 + "\n\n")
                        
                        with open(concat_list_path, "w", encoding="utf-8") as f:
                            for i, clip in enumerate(proj.clips):
                                clip_out = proj.premiere_project_path.parent / f"clip_{i}.mp4"
                                
                                dr.write(f"HIGHLIGHT #{i+1}\n")
                                dr.write(f"Source: {int(clip.start_time//60):02d}:{int(clip.start_time%60):02d} -> {int(clip.end_time//60):02d}:{int(clip.end_time%60):02d}\n")
                                dr.write(f"Editing Style: {proj.settings.editing_style}\n")
                                dr.write("Editing Decisions:\n")
                                
                                # 1. M10 - Composition Engine (Crop & Layout)
                                from engines.composition_engine.composition_engine import CompositionEngine
                                comp_engine = CompositionEngine()
                                comp_vf_str, comp_timeline = comp_engine.build_ffmpeg_filters(clip, proj.settings)
                                
                                # 2. M7 - Editing Engine (Zoom, Shake, Speed)
                                vf_str, af_str = editing_engine.build_ffmpeg_filters(clip)
                                
                                # Prepend the composition filter so M7 zooms operate on the cropped frame seamlessly
                                if comp_vf_str:
                                    if vf_str:
                                        vf_str = f"{comp_vf_str},{vf_str}"
                                    else:
                                        vf_str = comp_vf_str
                                        
                                # Write Composition Report
                                dr.write("SHORTS COMPOSITION REPORT\n")
                                dr.write(f"Target Aspect Ratio: {proj.settings.target_aspect_ratio}\n")
                                dr.write(f"Output Resolution: {proj.settings.output_resolution}\n")
                                dr.write(f"Composition Style: {proj.settings.composition_style}\n")
                                for ev in comp_timeline.events:
                                    dr.write(f"\nFocus Region: {ev.focus_region}\n")
                                    dr.write(f"Reason: {ev.reason}\n")
                                    dr.write(f"Fallback Used: {'YES' if ev.fallback_used else 'NO'}\n")
                                dr.write("-" * 50 + "\n\n")
                                # Track audio ducking based on captions
                                has_speech = False
                                if hasattr(clip, "captions") and clip.captions:
                                    has_speech = True
                                    dr.write(f"\nCaptions: Generated {len(clip.captions)} segments\n")
                                    emph_words = sum(1 for cap in clip.captions for w in cap.words if getattr(w, "is_emphasized", False))
                                    dr.write(f"Emphasized Words: {emph_words}\n")
                                else:
                                    dr.write("Captions: None (No speech or failed transcription)\n")
                                    
                                if clip.editing_timeline and clip.editing_timeline.editing_events:
                                    for ev in clip.editing_timeline.editing_events:
                                        dr.write(f"\n{ev.start_time - clip.start_time:.1f}s\n")
                                        dr.write(f"{ev.event_type}\n")
                                        dr.write(f"Reason: {ev.reason}\n")
                                else:
                                    dr.write("None\n")
                                    
                                dr.write("-" * 50 + "\n\n")
                                
                                # Generate ASS file for the clip if it has captions
                                clip_ass_path = None
                                if hasattr(clip, "captions") and clip.captions:
                                    clip_ass_path = proj.premiere_project_path.parent / f"clip_{i}_caps.ass"
                                    # We can mock a Timeline to use the formatter
                                    from core.models.caption_models import CaptionTimeline
                                    from engines.caption_engine.export.caption_formatter import CaptionFormatter
                                    
                                    mock_timeline = CaptionTimeline(video_id=f"clip_{i}", segments=clip.captions)
                                    mock_timeline.preset_name = proj.settings.editing_style # Pass down editing style
                                    
                                    formatter = CaptionFormatter()
                                    ass_content = formatter.format_ass(mock_timeline)
                                    
                                    with open(clip_ass_path, "w", encoding="utf-8") as f_ass:
                                        f_ass.write(ass_content)
                                        
                                    # We need to escape the path for FFmpeg filter on Windows
                                    escaped_ass_path = str(clip_ass_path.absolute()).replace('\\', '/').replace(':', '\\:')
                                    
                                    ass_filter = f"ass='{escaped_ass_path}'"
                                    if vf_str:
                                        vf_str = f"{vf_str},{ass_filter}"
                                    else:
                                        vf_str = ass_filter
                                        
                                segments = editing_engine.get_time_warp_segments(clip)
                                
                                clip_start_abs = current_output_time
                                
                                for seg_idx, seg in enumerate(segments):
                                    seg_out = proj.premiere_project_path.parent / f"clip_{i}_seg_{seg_idx}.mp4"
                                    
                                    cmd = [
                                        "ffmpeg", "-y", "-i", str(clip.source_video),
                                        "-ss", str(seg['start']), "-to", str(seg['end'])
                                    ]
                                    
                                    seg_vf_str = vf_str
                                    seg_af_str = af_str
                                    
                                    seg_duration = seg['end'] - seg['start']
                                    if seg['speed'] != 1.0:
                                        # Apply setpts and atempo
                                        speed = seg['speed']
                                        pts_mult = 1.0 / speed
                                        seg_duration = seg_duration * pts_mult
                                        
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
                                    current_output_time += seg_duration
                                
                                clip_end_abs = current_output_time
                                
                                # Add Audio Timeline Events for Ducking & Emphasis
                                if has_speech:
                                    audio_timeline.events.append(AudioEvent(
                                        start_time=clip_start_abs,
                                        end_time=clip_end_abs,
                                        event_type='DUCKING',
                                        target_volume=0.05,
                                        reason="COMMENTARY"
                                    ))
                                
                                if clip.events_contained:
                                    has_action = any(e.event_type in ["gameplay_visual_evidence", "high_motion"] for e in clip.events_contained)
                                    if has_action:
                                        audio_timeline.events.append(AudioEvent(
                                            start_time=clip_start_abs,
                                            end_time=clip_end_abs,
                                            event_type='EMPHASIS',
                                            target_volume=1.5,
                                            reason="ACTION"
                                        ))
                                
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
                                        current_output_time += 0.2
                                
                    final_out = proj.premiere_project_path.parent / "output.mp4"
                    cmd_concat = [
                        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(concat_list_path),
                        "-c", "copy", str(final_out)
                    ]
                    subprocess.run(cmd_concat, capture_output=True, check=True)
                    logger.info(f"Generated intermediate output video at {final_out}")
                    
                    # --- M9 AUDIO ENGINE PASS ---
                    try:
                        from engines.audio_engine.audio_engine import AudioEngine
                        audio_engine = AudioEngine()
                        audio_engine.initialize()
                        audio_engine.start()
                        
                        mixed_out = proj.premiere_project_path.parent / "output_mixed.mp4"
                        analysis = audio_engine.process_audio(final_out, mixed_out, audio_timeline, proj.settings)
                        
                        if mixed_out.exists():
                            final_out.unlink()
                            mixed_out.rename(final_out)
                            logger.info(f"Generated final audio-mixed video at {final_out}")
                            
                            with open(debug_report_path, "a", encoding="utf-8") as dr:
                                dr.write("AUDIO MIX REPORT\n")
                                dr.write("="*50 + "\n")
                                dr.write(f"Source Audio: Present\n")
                                dr.write(f"Integrated Loudness: {analysis.integrated_loudness} dB\n")
                                dr.write(f"Peak Level: {analysis.peak_level} dB\n")
                                dr.write(f"Background Music: {'YES' if proj.settings.bgm_path else 'NO'}\n")
                                dr.write(f"Audio Preset: {proj.settings.audio_preset}\n")
                                dr.write(f"Ducking Events: {sum(1 for e in audio_timeline.events if e.event_type == 'DUCKING')}\n")
                                dr.write(f"Emphasis Events: {sum(1 for e in audio_timeline.events if e.event_type == 'EMPHASIS')}\n")
                                dr.write(f"Silence Regions Detected: {len(analysis.silence_regions)}\n")
                                dr.write("-" * 50 + "\n\n")
                                
                        audio_engine.shutdown()
                    except Exception as ae:
                        logger.error(f"Audio Engine processing failed, using intermediate output: {ae}")
                        
                    # Cleanup temp clips
                    for c in clips_to_concat:
                        if c.exists(): c.unlink()
                    if concat_list_path.exists(): concat_list_path.unlink()
                    
                except Exception as e:
                    logger.error(f"Failed to generate output video: {e}")
