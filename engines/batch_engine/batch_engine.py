import logging
import time
import asyncio
from typing import Optional, Callable
from pathlib import Path

from core.models.batch_models import BatchJob, BatchJobStatus, SingleJob
from core.models.shorts_models import ProcessingRequest, ProcessingStatus, OutputSettings
from engines.shorts_generator_engine.shorts_generator_engine import ShortsGeneratorEngine

logger = logging.getLogger(__name__)

class BatchProcessingEngine:
    """
    Orchestrates sequential processing of multiple videos, guaranteeing job isolation.
    """
    def __init__(self, shorts_engine: ShortsGeneratorEngine):
        self.shorts_engine = shorts_engine

    async def process_batch(
        self, 
        batch: BatchJob, 
        settings: OutputSettings,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        is_cancelled_callback: Optional[Callable[[], bool]] = None
    ) -> BatchJob:
        
        batch.status = BatchJobStatus.RUNNING
        logger.info(f"Starting batch {batch.batch_id} with {batch.total_jobs} jobs.")
        
        for index, job in enumerate(batch.jobs):
            if is_cancelled_callback and is_cancelled_callback():
                logger.info(f"Batch {batch.batch_id} cancelled by user.")
                batch.status = BatchJobStatus.CANCELLED
                job.status = ProcessingStatus.FAILED
                job.error_message = "Cancelled by User"
                continue
                
            job.status = ProcessingStatus.ANALYZING
            job.start_time = time.time()
            logger.info(f"[{batch.batch_id}] Starting isolated job for {job.video_path.name}")
            
            def job_progress(msg: str, pct: int):
                if progress_callback:
                    overall_base = (index / batch.total_jobs) * 100
                    overall_add = (pct / 100) * (100 / batch.total_jobs)
                    progress_callback(f"({index+1}/{batch.total_jobs}) {msg}", int(overall_base + overall_add))
            
            # The ShortsGeneratorEngine expects paths, we pass just this ONE file to guarantee isolation
            try:
                # We call the underlying pipeline instead of the facade wrapper to avoid
                # re-triggering finalized steps if we just want isolated loops, OR we can just call generate_shorts
                # Wait, generate_shorts handles finalize and report generation! So calling it per-video is perfect.
                result = await self.shorts_engine.generate_shorts(
                    inputs=[job.video_path],
                    settings=settings,
                    progress_callback=job_progress,
                    is_cancelled_callback=is_cancelled_callback
                )
                
                job.result = result
                job.status = result.status
                if result.status == ProcessingStatus.FAILED:
                    job.error_message = result.error
                    
            except asyncio.CancelledError:
                job.status = ProcessingStatus.FAILED
                job.error_message = "Cancelled by User"
                batch.status = BatchJobStatus.CANCELLED
            except Exception as e:
                logger.error(f"[{batch.batch_id}] Job failed for {job.video_path.name}: {e}", exc_info=True)
                job.status = ProcessingStatus.FAILED
                job.error_message = str(e)
            
            job.end_time = time.time()
            
        if batch.status != BatchJobStatus.CANCELLED:
            batch.status = BatchJobStatus.COMPLETED
            
        try:
            from engines.library_engine.library_engine import LibraryEngine
            from core.models.library_models import ProjectLibraryEntry, ProjectType
            
            lib = LibraryEngine()
            
            # Record the batch itself as an entry so the user can find the batch.
            src_names = [j.video_path.name for j in batch.jobs]
            summary_name = f"Batch: {', '.join(src_names[:2])}{' and others' if len(src_names) > 2 else ''}"
            
            b_entry = ProjectLibraryEntry(
                project_id=batch.batch_id,
                project_type=ProjectType.BATCH.value,
                source_name=summary_name,
                source_path="Multiple",
                output_path="Multiple",
                status=batch.status.value,
                highlight_count=0
            )
            lib.register_project(b_entry)
            
            # For each job in the batch, tag them with the batch_id
            for job in batch.jobs:
                if job.result and job.result.projects:
                    for p in job.result.projects:
                        sub_entry = lib.get_project(p.project_id)
                        if sub_entry:
                            sub_entry.batch_id = batch.batch_id
                            lib.update_project(sub_entry)
                            
        except Exception as e:
            logger.error(f"Failed to register batch in Library: {e}")
            
        logger.info(f"Completed batch {batch.batch_id}. {batch.completed_jobs} completed, {batch.failed_jobs} failed.")
        return batch
