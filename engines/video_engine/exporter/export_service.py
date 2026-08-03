"""
Manages output folders and file naming for exports.
"""
from pathlib import Path
import uuid
import logging

logger = logging.getLogger(__name__)

class ExportService:
    def __init__(self, default_output_dir: Path) -> None:
        self.default_output_dir = default_output_dir

    def resolve_output_path(self, original_name: str, suffix: str, overwrite: bool = False) -> Path:
        """Resolve a safe output path avoiding collisions."""
        self.default_output_dir.mkdir(parents=True, exist_ok=True)
        base_name = Path(original_name).stem
        
        if not suffix.startswith("."):
            suffix = f".{suffix}"
            
        out_path = self.default_output_dir / f"{base_name}{suffix}"
        
        if out_path.exists() and not overwrite:
            unique_id = str(uuid.uuid4())[:8]
            out_path = self.default_output_dir / f"{base_name}_{unique_id}{suffix}"
            
        return out_path
