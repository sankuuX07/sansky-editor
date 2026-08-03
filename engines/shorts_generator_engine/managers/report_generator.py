"""
Generates processing reports.
"""
import logging
import time
from core.models.shorts_models import ProjectReport, ProcessingSummary, ProcessingResult, ProcessingStatus

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.start_time = time.time()
        
    def generate(self, result: ProcessingResult) -> None:
        duration = time.time() - self.start_time
        
        total = len(result.projects)
        failed = 1 if result.status == ProcessingStatus.FAILED else 0
        successful = 1 if result.status == ProcessingStatus.COMPLETED else 0
        generated = sum(len(p.clips) for p in result.projects)
        
        summary = ProcessingSummary(
            total_videos=total + failed,
            successful=successful,
            failed=failed,
            generated_shorts=generated,
            total_time_sec=duration
        )
        
        report = ProjectReport(
            request_id=result.request_id,
            summary=summary,
            errors=[result.error] if result.error else []
        )
        result.report = report
        logger.info(f"Generated report for {result.request_id}. Shorts: {generated}, Time: {duration:.1f}s")
