import json
import logging
import time
import dataclasses
import shutil
from pathlib import Path
from typing import List, Optional, Dict

from core.models.library_models import ProjectLibraryEntry, StorageStatus, ProjectType

logger = logging.getLogger(__name__)

class LibraryEngine:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.library_dir = self.data_dir / "library"
        self.index_file = self.library_dir / "project_index.json"
        self._entries: Dict[str, ProjectLibraryEntry] = {}
        self.initialize()

    def initialize(self):
        self.library_dir.mkdir(parents=True, exist_ok=True)
        if self.index_file.exists():
            self._load_index()
        else:
            self._save_index()
            
    def _load_index(self):
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self._entries.clear()
            for item in data:
                entry = ProjectLibraryEntry(**item)
                self._entries[entry.project_id] = entry
        except Exception as e:
            logger.error(f"Failed to load library index: {e}")
            
    def _save_index(self):
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                data = [dataclasses.asdict(entry) for entry in self._entries.values()]
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save library index: {e}")
            
    def register_project(self, entry: ProjectLibraryEntry):
        entry.updated_at = time.time()
        self._entries[entry.project_id] = entry
        self._save_index()
        logger.info(f"Registered project {entry.project_id} in library.")
        
    def update_project(self, entry: ProjectLibraryEntry):
        entry.updated_at = time.time()
        self._entries[entry.project_id] = entry
        self._save_index()
        
    def get_project(self, project_id: str) -> Optional[ProjectLibraryEntry]:
        return self._entries.get(project_id)
        
    def get_all(self, sort_by="updated_desc") -> List[ProjectLibraryEntry]:
        entries = list(self._entries.values())
        if sort_by == "updated_desc":
            entries.sort(key=lambda x: x.updated_at, reverse=True)
        elif sort_by == "updated_asc":
            entries.sort(key=lambda x: x.updated_at)
        elif sort_by == "created_desc":
            entries.sort(key=lambda x: x.created_at, reverse=True)
        return entries
        
    def search(self, query: str) -> List[ProjectLibraryEntry]:
        q = query.lower()
        results = []
        for e in self.get_all():
            if (q in e.source_name.lower() or 
                q in e.project_id.lower() or 
                (e.batch_id and q in e.batch_id.lower()) or
                any(q in tag.lower() for tag in e.tags)):
                results.append(e)
        return results

    def check_health(self, project_id: str) -> str:
        entry = self.get_project(project_id)
        if not entry:
            return StorageStatus.UNKNOWN.value
            
        src_exists = Path(entry.source_path).exists()
        out_exists = False
        if entry.output_path:
            out_exists = Path(entry.output_path).exists()
            
        if src_exists and out_exists:
            status = StorageStatus.AVAILABLE.value
        elif src_exists and not out_exists:
            status = StorageStatus.MISSING_OUTPUT.value
        elif not src_exists and out_exists:
            status = StorageStatus.MISSING_SOURCE.value
        else:
            status = StorageStatus.MISSING_BOTH.value
            
        entry.storage_status = status
        self.update_project(entry)
        return status
        
    def toggle_favorite(self, project_id: str) -> bool:
        entry = self.get_project(project_id)
        if entry:
            entry.favorite = not entry.favorite
            self.update_project(entry)
            return entry.favorite
        return False

    def toggle_archive(self, project_id: str) -> bool:
        entry = self.get_project(project_id)
        if entry:
            entry.archived = not entry.archived
            self.update_project(entry)
            return entry.archived
        return False
        
    def add_tag(self, project_id: str, tag: str):
        entry = self.get_project(project_id)
        if entry and tag not in entry.tags:
            entry.tags.append(tag)
            self.update_project(entry)
            
    def remove_tag(self, project_id: str, tag: str):
        entry = self.get_project(project_id)
        if entry and tag in entry.tags:
            entry.tags.remove(tag)
            self.update_project(entry)

    def remove_from_library(self, project_id: str):
        if project_id in self._entries:
            del self._entries[project_id]
            self._save_index()
            logger.info(f"Removed project {project_id} from library (metadata only).")

    def delete_outputs(self, project_id: str) -> bool:
        entry = self.get_project(project_id)
        if not entry or not entry.output_path:
            return False
            
        out_path = Path(entry.output_path)
        if out_path.exists() and out_path.is_dir():
            try:
                shutil.rmtree(out_path)
                logger.info(f"Deleted output directory for project {project_id}.")
                self.check_health(project_id) # Update status
                return True
            except Exception as e:
                logger.error(f"Failed to delete outputs for {project_id}: {e}")
        return False
