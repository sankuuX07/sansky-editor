"""
Strongly typed dataclasses for AI Engine.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from pathlib import Path

class HardwareBackend(Enum):
    CUDA = "CUDA"
    DIRECTML = "DIRECTML"
    MPS = "MPS"
    CPU = "CPU"

class ModelStatus(Enum):
    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    LOADED = "LOADED"
    DOWNLOADING = "DOWNLOADING"
    ERROR = "ERROR"

@dataclass
class HardwareInfo:
    backend: HardwareBackend
    device_name: str
    total_memory_mb: int
    free_memory_mb: int

@dataclass
class GPUInfo(HardwareInfo):
    index: int
    compute_capability: str = ""

@dataclass
class CPUInfo(HardwareInfo):
    core_count: int

@dataclass
class MemorySnapshot:
    ram_used_mb: float
    ram_total_mb: float
    vram_used_mb: float
    vram_total_mb: float

@dataclass
class ModelInfo:
    model_id: str
    name: str
    version: str
    path: Path
    dependencies: List[str] = field(default_factory=list)
    memory_requirement_mb: int = 0
    status: ModelStatus = ModelStatus.UNLOADED

@dataclass
class InferenceRequest:
    model_id: str
    inputs: Dict[str, Any]
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_sec: Optional[float] = None

@dataclass
class InferenceResult:
    model_id: str
    success: bool
    outputs: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

@dataclass
class PipelineStage:
    stage_id: str
    model_id: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
