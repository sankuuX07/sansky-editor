"""
Shorts Generator Engine Facade.
"""
import logging
import asyncio
from typing import Union, List
from pathlib import Path
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError

from engines.automation_engine.automation_engine import AutomationEngine

from engines.shorts_generator_engine.managers.input_manager import InputManager
from engines.shorts_generator_engine.managers.workflow_launcher import WorkflowLauncher
from engines.shorts_generator_engine.managers.highlight_selection_manager import HighlightSelectionManager
from engines.shorts_generator_engine.managers.caption_placement_manager import CaptionPlacementManager
from engines.shorts_generator_engine.managers.timeline_preparation_manager import TimelinePreparationManager
from engines.shorts_generator_engine.managers.project_assembler import ProjectAssembler
from engines.shorts_generator_engine.managers.report_generator import ReportGenerator
from engines.shorts_generator_engine.managers.output_manager import OutputManager

from engines.shorts_generator_engine.core.processing_pipeline import ProcessingPipeline
from core.models.shorts_models import OutputSettings, ProcessingResult

class ShortsGeneratorEngine(BaseEngine):
    def __init__(self, automation_engine: AutomationEngine) -> None:
        super().__init__("shorts_generator_engine")
        
        self.input_manager = InputManager()
        self.workflow_launcher = WorkflowLauncher(automation_engine)
        self.highlight_selector = HighlightSelectionManager()
        self.caption_placer = CaptionPlacementManager()
        self.timeline_prep = TimelinePreparationManager()
        self.project_assembler = ProjectAssembler()
        self.report_generator = ReportGenerator()
        self.output_manager = OutputManager()
        
        self.pipeline = ProcessingPipeline(
            self.workflow_launcher,
            self.highlight_selector,
            self.caption_placer,
            self.timeline_prep,
            self.project_assembler
        )

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Shorts Generator Engine...")
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = True
        self.logger.info("Shorts Generator Engine initialized successfully.")

    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized ShortsGeneratorEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Shorts Generator Engine started.")

    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Shorts Generator Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Shorts Generator Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING
        
    async def generate_shorts(self, inputs: Union[str, Path, List[Union[str, Path]]], settings: OutputSettings = None, progress_callback=None, is_cancelled_callback=None) -> ProcessingResult:
        self.logger.info("Starting generate_shorts workflow.")
        request = self.input_manager.create_request(inputs, settings)
        request.progress_callback = progress_callback
        request.is_cancelled = is_cancelled_callback
        
        result = await self.pipeline.process(request)
        
        self.output_manager.finalize(result)
        self.report_generator.generate(result)
        
        try:
            from engines.library_engine.library_engine import LibraryEngine
            from core.models.library_models import ProjectLibraryEntry, ProjectType
            import os
            
            lib = LibraryEngine()
            for p in result.projects:
                src_path = str(p.clips[0].source_video) if p.clips else "unknown"
                out_path = str(p.premiere_project_path.parent) if p.premiere_project_path else None
                
                # Check if it was a re-edit
                # If we passed a specific re-edit flag, we could use RE_EDIT, but we can default to SINGLE_VIDEO
                ptype = ProjectType.SINGLE_VIDEO.value
                
                entry = ProjectLibraryEntry(
                    project_id=p.project_id,
                    project_type=ptype,
                    source_name=os.path.basename(src_path),
                    source_path=src_path,
                    output_path=out_path,
                    status=result.status.value,
                    highlight_count=len(p.clips),
                    creator_report_path=str(p.premiere_project_path.parent / "content_strategy_report.json") if out_path else None
                )
                lib.register_project(entry)
        except Exception as e:
            self.logger.error(f"Failed to register project in Library: {e}")
            
        return result
