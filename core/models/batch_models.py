from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional
import time
import uuid

from core.models.shorts_models import ProcessingResult, ProcessingStatus

class BatchJobStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

@dataclass
class SingleJob:
    video_path: Path
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Optional[ProcessingResult] = None
    error_message: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0

@dataclass
class BatchJob:
    batch_id: str = field(default_factory=lambda: f"BATCH_{uuid.uuid4().hex[:8].upper()}")
    created_at: float = field(default_factory=time.time)
    status: BatchJobStatus = BatchJobStatus.PENDING
    jobs: List[SingleJob] = field(default_factory=list)
    
    @property
    def total_jobs(self) -> int:
        return len(self.jobs)
        
    @property
    def completed_jobs(self) -> int:
        return sum(1 for j in self.jobs if j.status == ProcessingStatus.COMPLETED)
        
    @property
    def failed_jobs(self) -> int:
        return sum(1 for j in self.jobs if j.status == ProcessingStatus.FAILED)
