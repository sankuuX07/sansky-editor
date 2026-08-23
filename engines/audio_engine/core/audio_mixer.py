"""
Generates and executes FFmpeg audio filtergraphs for mixing and normalization.
"""
import logging
import subprocess
from pathlib import Path
from core.models.audio_models import AudioTimeline
from core.models.shorts_models import OutputSettings

logger = logging.getLogger(__name__)

class AudioMixer:
    def mix(self, input_video: Path, output_video: Path, timeline: AudioTimeline, settings: OutputSettings) -> None:
        logger.info(f"Mixing audio for {input_video} to {output_video}")
        
        try:
            # Base command
            cmd = ["ffmpeg", "-y", "-i", str(input_video)]
            
            filter_complex = []
            audio_inputs = 1
            
            # Map of inputs
            # [0:a] is the main gameplay audio
            # If bgm is present, we add it as input [1:a]
            
            if settings.bgm_path and Path(settings.bgm_path).exists():
                cmd.extend(["-stream_loop", "-1", "-i", settings.bgm_path])
                audio_inputs += 1
                
                # Apply ducking to background music [1:a]
                # Default background volume is low, say 0.2
                bgm_vol_filter = "volume=0.2"
                
                ducking_events = [ev for ev in timeline.events if ev.event_type == 'DUCKING']
                for ev in ducking_events:
                    # duck down to 0.05 during speech
                    bgm_vol_filter += f":eval=frame:enable='between(t,{ev.start_time},{ev.end_time})':volume=0.05"
                    
                filter_complex.append(f"[1:a]{bgm_vol_filter}[bgm]")
                
            # Apply emphasis to main audio [0:a]
            main_vol_filter = "volume=1.0"
            emphasis_events = [ev for ev in timeline.events if ev.event_type == 'EMPHASIS']
            for ev in emphasis_events:
                # boost to 1.5 during action
                main_vol_filter += f":eval=frame:enable='between(t,{ev.start_time},{ev.end_time})':volume={ev.target_volume}"
                
            filter_complex.append(f"[0:a]{main_vol_filter}[main]")
            
            # Mix streams
            mix_input = "[main]"
            if audio_inputs > 1:
                mix_input = "[main][bgm]"
                filter_complex.append(f"{mix_input}amix=inputs=2:duration=first[mixed]")
            else:
                filter_complex.append(f"[main]copy[mixed]")
                
            # Normalization based on preset
            i_val = "-16"
            tp_val = "-1.5"
            lra_val = "11"
            
            preset = getattr(settings, 'audio_preset', 'GAMING').upper()
            if preset == "CLEAN":
                i_val = "-20"
                lra_val = "15"
            elif preset == "GAMING":
                i_val = "-16"
                lra_val = "11"
            elif preset == "CINEMATIC":
                i_val = "-14"
                lra_val = "9"
            elif preset == "INTENSE":
                i_val = "-12"
                lra_val = "7"
                
            norm_filter = f"[mixed]loudnorm=I={i_val}:TP={tp_val}:LRA={lra_val}[final_a]"
            filter_complex.append(norm_filter)
            
            cmd.extend([
                "-filter_complex", ";".join(filter_complex),
                "-map", "0:v",
                "-map", "[final_a]",
                "-c:v", "copy",
                "-c:a", "aac",
                str(output_video)
            ])
            
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info("Audio mixing completed successfully.")
            
        except Exception as e:
            logger.error(f"Failed to mix audio: {e}")
            raise
