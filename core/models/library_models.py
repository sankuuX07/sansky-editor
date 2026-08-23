from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import time

class ProjectType(Enum):
    SINGLE_VIDEO = "SINGLE_VIDEO"
    BATCH = "BATCH"
    RE_EDIT = "RE_EDIT"
    IMPORTED = "IMPORTED"

class StorageStatus(Enum):
    AVAILABLE = "AVAILABLE"
    MISSING_OUTPUT = "MISSING_OUTPUT"
    MISSING_SOURCE = "MISSING_SOURCE"
    MISSING_BOTH = "MISSING_BOTH"
    UNKNOWN = "UNKNOWN"

@dataclass
class ProjectLibraryEntry:
    project_id: str
    project_type: str # String representation of ProjectType
    source_name: str
    source_path: str
    output_path: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "PENDING"
    
    # User state
    favorite: bool = False
    archived: bool = False
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    duration: float = 0.0
    resolution: str = "unknown"
    job_id: Optional[str] = None
    batch_id: Optional[str] = None
    parent_job_id: Optional[str] = None # For re-edits
    
    # Outputs info
    highlight_count: int = 0
    thumbnail_count: int = 0
    creator_report_path: Optional[str] = None
    
    # Storage health
    last_opened: float = field(default_factory=time.time)
    storage_status: str = StorageStatus.UNKNOWN.value
    metadata_version: int = 1
