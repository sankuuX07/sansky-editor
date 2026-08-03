"""
Executes the full pipeline for a request.
"""
import logging
from core.models.shorts_models import ProcessingRequest, ProcessingResult, ProcessingStatus
from engines.shorts_generator_engine.managers.workflow_launcher import WorkflowLauncher
from engines.shorts_generator_engine.managers.highlight_selection_manager import HighlightSelectionManager
from engines.shorts_generator_engine.managers.caption_placement_manager import CaptionPlacementManager
from engines.shorts_generator_engine.managers.timeline_preparation_manager import TimelinePreparationManager
from engines.shorts_generator_engine.managers.project_assembler import ProjectAssembler

logger = logging.getLogger(__name__)

class ProcessingPipeline:
    def __init__(
        self,
        workflow_launcher: WorkflowLauncher,
        highlight_selector: HighlightSelectionManager,
        caption_placer: CaptionPlacementManager,
        timeline_prep: TimelinePreparationManager,
        project_assembler: ProjectAssembler
    ):
        self.launcher = workflow_launcher
        self.highlight_selector = highlight_selector
        self.caption_placer = caption_placer
        self.timeline_prep = timeline_prep
        self.project_assembler = project_assembler
        
    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        result = ProcessingResult(request_id=request.request_id, status=ProcessingStatus.ANALYZING)
        
        try:
            for video_path in request.video_paths:
                wf_results = await self.launcher.launch_for_video(request, video_path)
                
                raw_captions = wf_results.get("generate_captions", {})
                raw_highlights = wf_results.get("extract_highlights", {})
                
                clips = self.highlight_selector.select_highlights(raw_highlights, video_path, request.settings)
                clips = self.caption_placer.assign_captions(clips, raw_captions)
                timeline = self.timeline_prep.prepare_timeline(clips, request.settings)
                project = self.project_assembler.assemble(timeline, request.settings)
                
                result.projects.append(project)
                
            result.status = ProcessingStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result.status = ProcessingStatus.FAILED
            result.error = str(e)
            
        return result
