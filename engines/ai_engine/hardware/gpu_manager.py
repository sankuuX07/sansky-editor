"""
GPU Manager for detecting and allocating hardware resources.
"""
import logging
from typing import List, Optional
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from core.models.ai_models import HardwareBackend, GPUInfo, CPUInfo
from core.exceptions.ai_exceptions import GPUInitializationError

logger = logging.getLogger(__name__)

class GPUManager:
    """Manages AI hardware acceleration backends."""
    def __init__(self) -> None:
        self.active_backend: HardwareBackend = HardwareBackend.CPU
        self.gpus: List[GPUInfo] = []
        self.cpu_info: Optional[CPUInfo] = None

    def initialize(self) -> None:
        """Detect available hardware backends and pick the optimal one."""
        self._detect_cpu()
        self._detect_cuda()
        self._detect_mps()
        
        if len(self.gpus) > 0 and self.gpus[0].backend == HardwareBackend.CUDA:
            self.active_backend = HardwareBackend.CUDA
            logger.info(f"GPUManager initialized with CUDA. Found {len(self.gpus)} GPUs.")
        elif len(self.gpus) > 0 and self.gpus[0].backend == HardwareBackend.MPS:
            self.active_backend = HardwareBackend.MPS
            logger.info("GPUManager initialized with Apple MPS.")
        else:
            self.active_backend = HardwareBackend.CPU
            logger.info("GPUManager initialized with CPU fallback.")

    def _detect_cpu(self) -> None:
        """Fallback CPU detection."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            total_mem = int(mem.total / (1024 * 1024))
            free_mem = int(mem.available / (1024 * 1024))
            cores = psutil.cpu_count(logical=False) or 1
        except ImportError:
            logger.warning("psutil is not installed; using placeholder CPU detection.")
            total_mem = 8192
            free_mem = 4096
            cores = 4

        self.cpu_info = CPUInfo(
            backend=HardwareBackend.CPU,
            device_name="System CPU",
            total_memory_mb=total_mem,
            free_memory_mb=free_mem,
            core_count=cores
        )

    def _detect_cuda(self) -> None:
        """Detect NVIDIA CUDA GPUs."""
        if not TORCH_AVAILABLE:
            logger.warning("Torch is not installed; skipping CUDA detection.")
            return
        try:
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    self.gpus.append(GPUInfo(
                        backend=HardwareBackend.CUDA,
                        device_name=props.name,
                        total_memory_mb=int(props.total_memory / (1024 * 1024)),
                        free_memory_mb=int(torch.cuda.mem_get_info(i)[0] / (1024 * 1024)),
                        index=i,
                        compute_capability=f"{props.major}.{props.minor}"
                    ))
        except Exception as e:
            logger.warning(f"CUDA detection failed: {e}")

    def _detect_mps(self) -> None:
        """Detect Apple Silicon MPS."""
        if not TORCH_AVAILABLE:
            logger.warning("Torch is not installed; skipping MPS detection.")
            return
        try:
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.gpus.append(GPUInfo(
                    backend=HardwareBackend.MPS,
                    device_name="Apple Silicon",
                    total_memory_mb=0,
                    free_memory_mb=0,
                    index=0,
                    compute_capability="MPS"
                ))
        except Exception as e:
            logger.warning(f"MPS detection failed: {e}")

    def get_optimal_device(self) -> str:
        """Return the optimal torch device string."""
        if self.active_backend == HardwareBackend.CUDA:
            return "cuda:0"
        elif self.active_backend == HardwareBackend.MPS:
            return "mps"
        return "cpu"
