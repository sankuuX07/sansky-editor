"""
Models for the Smart Manual Editor (M17).
"""
from dataclasses import dataclass, field, replace
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid
import copy

class TrackType(str, Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    CAPTIONS = "CAPTIONS"
    EFFECTS = "EFFECTS"

@dataclass
class CaptionBlock:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = 0.0
    end_time: float = 0.0
    text: str = ""
    speaker: Optional[str] = None
    enabled: bool = True

@dataclass
class TimelineClip:
    clip_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_path: str = ""
    source_start: float = 0.0
    source_end: float = 0.0
    timeline_start: float = 0.0
    timeline_end: float = 0.0
    duration: float = 0.0
    enabled: bool = True
    effects: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def copy(self):
        return copy.deepcopy(self)

@dataclass
class Track:
    track_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    track_type: TrackType = TrackType.VIDEO
    items: List[Any] = field(default_factory=list) # List of TimelineClip or CaptionBlock
    
    def copy(self):
        return copy.deepcopy(self)

@dataclass
class EditableTimeline:
    timeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    source_job_id: str = ""
    created_at: str = ""
    duration: float = 0.0
    version: int = 1
    tracks: List[Track] = field(default_factory=list)
    parent_project_id: Optional[str] = None
    
    def get_track(self, track_type: TrackType) -> Optional[Track]:
        for track in self.tracks:
            if track.track_type == track_type:
                return track
        return None

    def copy(self):
        return copy.deepcopy(self)

# History / Undo Redo
class EditAction(str, Enum):
    TRIM_CLIP = "TRIM_CLIP"
    SPLIT_CLIP = "SPLIT_CLIP"
    DELETE_CLIP = "DELETE_CLIP"
    REORDER_CLIPS = "REORDER_CLIPS"
    EDIT_EFFECT = "EDIT_EFFECT"
    EDIT_CAPTION = "EDIT_CAPTION"
    UNDO = "UNDO"
    REDO = "REDO"

@dataclass
class EditCommand:
    action: EditAction
    description: str
    previous_state: EditableTimeline
    new_state: EditableTimeline
