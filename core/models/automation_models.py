"""
Strongly typed dataclasses for Automation Engine workflows.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid

class WorkflowStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class RecoveryActionType(Enum):
    RETRY = "RETRY"
    ABORT = "ABORT"
    IGNORE = "IGNORE"

@dataclass
class WorkflowStep:
    step_id: str
    engine_name: str
    action: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class Workflow:
    name: str
    steps: List[WorkflowStep]
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: WorkflowStatus = WorkflowStatus.PENDING

@dataclass
class WorkflowProgress:
    workflow_id: str
    total_steps: int
    completed_steps: int
    current_step: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    percentage: float = 0.0

@dataclass
class RecoveryAction:
    action_type: RecoveryActionType
    max_retries: int = 3
    delay_sec: float = 0.0
    
@dataclass
class AutomationSettings:
    max_concurrent_tasks: int = 4
    default_retry_count: int = 3
