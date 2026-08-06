"""
Coordinates high-level business logic, mapping outputs to inputs.
"""
import logging
import asyncio
from typing import Any
from core.models.automation_models import WorkflowStep
from app.services.engine_manager import EngineManager

logger = logging.getLogger(__name__)

class PipelineCoordinator:
    def __init__(self, engine_manager: EngineManager):
        self.engine_manager = engine_manager
        
    async def execute_step(self, step: WorkflowStep, context: dict) -> Any:
        """Executes the specific action on the required engine."""
        logger.info(f"Coordinator executing step: {step.step_id} on {step.engine_name}")
        engine = self.engine_manager.get_engine(step.engine_name)
        
        # Here we map step.action to actual engine method calls.
        if step.engine_name == "video_engine" and step.action == "extract_audio":
            video_path = step.inputs.get("video_path")
            from pathlib import Path
            result = engine.pipeline.run_standard_ingestion(Path(video_path), extract_audio=True)
            return {"audio_path": str(result.extracted_audio_path)}
                
        elif step.engine_name == "ai_engine" and step.action == "transcribe":
            audio_path = context.get("extract_audio", {}).get("audio_path")
            if not hasattr(engine, "transcribe"):
                raise NotImplementedError("AIEngine lacks a transcribe method.")
            transcript = engine.transcribe(audio_path)
            return {"transcript_data": transcript}
                
        elif step.engine_name == "caption_engine" and step.action == "generate_captions":
            video_path = step.inputs.get("video_path")
            transcript_data = context.get("transcribe", {}).get("transcript_data")
            from pathlib import Path
            timeline = engine.process_transcript(Path(video_path).stem, transcript_data)
            return {"caption_timeline": timeline}
            
        elif step.engine_name == "highlight_engine" and step.action == "extract_highlights":
            video_path = step.inputs.get("video_path")
            audio_path = context.get("extract_audio", {}).get("audio_path")
            from pathlib import Path
            timeline = engine.process_video(Path(video_path).stem, Path(video_path), Path(audio_path))
            return {"highlight_timeline": timeline}
                
        elif step.engine_name == "premiere_engine" and step.action == "build_timeline":
            from core.models.premiere_models import SequenceInfo, TimelineClip
            from pathlib import Path
            
            video_path = step.inputs.get("video_path")
            highlight_timeline = context.get("extract_highlights", {}).get("highlight_timeline")
            
            sequence = SequenceInfo(name="Generated Shorts", width=1080, height=1920, framerate=30.0)
            
            clips = []
            if highlight_timeline:
                for c in highlight_timeline.highlights:
                    clips.append(TimelineClip(
                        asset_path=Path(video_path),
                        start_time=c.start_time,
                        end_time=c.end_time
                    ))
            
            # The engine has a timeline_builder
            engine.timeline_builder.build_timeline(sequence, clips)
            
            xml_data = engine.timeline_builder.get_last_xml()
            
            return {"timeline_status": "built", "xml_data": xml_data}
                
        # Generic fallback for direct method execution
        method = getattr(engine, step.action, None)
        if method:
            import inspect
            if inspect.iscoroutinefunction(method):
                return await method(**step.inputs)
            else:
                loop = asyncio.get_running_loop()
                import functools
                return await loop.run_in_executor(None, functools.partial(method, **step.inputs))

        raise NotImplementedError(f"Action '{step.action}' on engine '{step.engine_name}' is not supported.")
