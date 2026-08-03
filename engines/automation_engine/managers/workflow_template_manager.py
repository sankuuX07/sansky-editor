"""
Provides predefined workflow templates.
"""
from core.models.automation_models import Workflow, WorkflowStep
import logging

logger = logging.getLogger(__name__)

class WorkflowTemplateManager:
    def get_gaming_shorts_template(self) -> Workflow:
        return Workflow(
            name="Gaming Shorts Pipeline",
            steps=[
                WorkflowStep(step_id="extract_audio", engine_name="video_engine", action="extract_audio"),
                WorkflowStep(step_id="transcribe", engine_name="whisper_engine", action="transcribe", depends_on=["extract_audio"]),
                WorkflowStep(step_id="generate_captions", engine_name="caption_engine", action="generate_captions", depends_on=["transcribe"]),
                WorkflowStep(step_id="build_timeline", engine_name="premiere_engine", action="build_timeline", depends_on=["generate_captions"])
            ]
        )
