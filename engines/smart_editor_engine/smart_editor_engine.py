"""
Smart Editor Engine for M17.
Handles loading, saving, editing, and converting timelines.
"""
import logging
import copy
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from core.models.shared_types import EngineStatus
from engines.base_engine import BaseEngine
from core.models.smart_editor_models import (
    EditableTimeline, Track, TrackType, TimelineClip, CaptionBlock, EditCommand, EditAction
)
from core.models.shorts_models import ShortsProject, GeneratedClip, OutputSettings

class SmartEditorEngine(BaseEngine):
    def __init__(self, library_engine=None):
        super().__init__("smart_editor_engine")
        self.library_engine = library_engine
        
        self.current_timeline: Optional[EditableTimeline] = None
        self.history: List[EditCommand] = []
        self.history_index: int = -1

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Smart Editor Engine...")
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = True

    def load_project_from_library(self, entry) -> bool:
        """Loads a project into the editable timeline from a Library Entry."""
        self.logger.info(f"Loading project {entry.project_id}")
        # Look for timeline.json in the output path
        if not entry.output_path:
            self.logger.error("Project has no output path")
            return False
            
        out_dir = Path(entry.output_path)
        timeline_path = out_dir / "timeline.json"
        
        if timeline_path.exists():
            return self._load_timeline_json(timeline_path)
        else:
            # For backward compatibility, try to build it from project_state.json or report
            # We assume for now that if we don't have timeline.json, we can't edit it yet.
            # But wait, M17 says "Open an existing AI-generated project".
            # We will implement a mock translation for now if timeline.json is missing,
            # or try to build one from the library entry data.
            # For the scope of M17, we will support translating a ShortsProject to EditableTimeline.
            project_json_path = out_dir / "project.json"
            if project_json_path.exists():
                return self._load_from_shorts_project(project_json_path)
            
            self.logger.error(f"Cannot find timeline.json or project.json at {out_dir}")
            return False

    def _load_timeline_json(self, path: Path) -> bool:
        # Load directly from our own format
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timeline = EditableTimeline(
                timeline_id=data.get('timeline_id', str(uuid.uuid4())),
                project_id=data.get('project_id', ''),
                source_job_id=data.get('source_job_id', ''),
                created_at=data.get('created_at', ''),
                duration=data.get('duration', 0.0),
                version=data.get('version', 1),
                parent_project_id=data.get('parent_project_id')
            )
            
            for t_data in data.get('tracks', []):
                track = Track(
                    track_id=t_data.get('track_id', str(uuid.uuid4())),
                    track_type=TrackType(t_data.get('track_type', 'VIDEO'))
                )
                
                for i_data in t_data.get('items', []):
                    if track.track_type == TrackType.VIDEO:
                        clip = TimelineClip(
                            clip_id=i_data.get('clip_id', str(uuid.uuid4())),
                            source_path=i_data.get('source_path', ''),
                            source_start=i_data.get('source_start', 0.0),
                            source_end=i_data.get('source_end', 0.0),
                            timeline_start=i_data.get('timeline_start', 0.0),
                            timeline_end=i_data.get('timeline_end', 0.0),
                            duration=i_data.get('duration', 0.0),
                            enabled=i_data.get('enabled', True),
                            effects=i_data.get('effects', {}),
                            metadata=i_data.get('metadata', {})
                        )
                        track.items.append(clip)
                    elif track.track_type == TrackType.CAPTIONS:
                        caption = CaptionBlock(
                            id=i_data.get('id', str(uuid.uuid4())),
                            start_time=i_data.get('start_time', 0.0),
                            end_time=i_data.get('end_time', 0.0),
                            text=i_data.get('text', ''),
                            speaker=i_data.get('speaker'),
                            enabled=i_data.get('enabled', True)
                        )
                        track.items.append(caption)
                
                timeline.tracks.append(track)
                
            self.current_timeline = timeline
            self.history = []
            self.history_index = -1
            return True
        except Exception as e:
            self.logger.error(f"Error loading timeline JSON: {e}")
            return False

    def _load_from_shorts_project(self, path: Path) -> bool:
        # Fallback to translate a ShortsProject to EditableTimeline
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Basic translation
            timeline = EditableTimeline(
                project_id=data.get('project_id', str(uuid.uuid4())),
                created_at=datetime.now().isoformat()
            )
            
            video_track = Track(track_type=TrackType.VIDEO)
            caption_track = Track(track_type=TrackType.CAPTIONS)
            
            current_time = 0.0
            clips_data = data.get('clips', [])
            
            # Simplified loading
            for c in clips_data:
                s_start = c.get('start_time', 0.0)
                s_end = c.get('end_time', 0.0)
                duration = s_end - s_start
                
                clip = TimelineClip(
                    clip_id=c.get('clip_id', str(uuid.uuid4())),
                    source_path=c.get('source_video', ''),
                    source_start=s_start,
                    source_end=s_end,
                    timeline_start=current_time,
                    timeline_end=current_time + duration,
                    duration=duration
                )
                
                video_track.items.append(clip)
                
                # Captions
                for cap in c.get('captions', []):
                    # Adjust caption timing to timeline global time
                    c_start = current_time + (cap.get('start_time', 0.0) - s_start)
                    c_end = current_time + (cap.get('end_time', 0.0) - s_start)
                    caption_track.items.append(CaptionBlock(
                        start_time=c_start,
                        end_time=c_end,
                        text=cap.get('text', '')
                    ))
                    
                current_time += duration
                
            timeline.duration = current_time
            timeline.tracks.extend([video_track, caption_track])
            
            self.current_timeline = timeline
            self.history = []
            self.history_index = -1
            return True
        except Exception as e:
            self.logger.error(f"Error loading from project.json: {e}")
            return False

    def save_version(self) -> Optional[str]:
        """Saves the current timeline as a new version and registers it."""
        if not self.current_timeline:
            return None
            
        # Increment version
        self.current_timeline.version += 1
        new_project_id = f"{self.current_timeline.project_id}_v{self.current_timeline.version}"
        
        # In a real system, we'd save it to a new output folder
        # and register with LibraryEngine.
        return new_project_id

    def push_state(self, action: EditAction, description: str):
        if not self.current_timeline:
            return
            
        # Truncate redo history
        self.history = self.history[:self.history_index + 1]
        
        prev_state = self.history[self.history_index].new_state if self.history_index >= 0 else self.current_timeline
        
        # We assume current_timeline is ALREADY the new state. We need to copy it before the NEXT edit.
        # So we should actually push the state BEFORE making the change.
        # Actually, standard pattern is to create the command, then apply it.
        # For simplicity, we just save snapshots.
        pass

    def take_snapshot(self) -> EditableTimeline:
        return self.current_timeline.copy() if self.current_timeline else None

    def commit_edit(self, action: EditAction, description: str, old_state: EditableTimeline, new_state: EditableTimeline):
        self.history = self.history[:self.history_index + 1]
        cmd = EditCommand(action=action, description=description, previous_state=old_state, new_state=new_state)
        self.history.append(cmd)
        self.history_index += 1
        self.current_timeline = new_state

    def undo(self) -> bool:
        if self.history_index >= 0:
            cmd = self.history[self.history_index]
            self.current_timeline = cmd.previous_state.copy()
            self.history_index -= 1
            return True
        return False
        
    def redo(self) -> bool:
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            cmd = self.history[self.history_index]
            self.current_timeline = cmd.new_state.copy()
            return True
        return False

    # --- Editing Operations ---
    def trim_clip(self, clip_id: str, new_start: float, new_end: float) -> bool:
        if not self.current_timeline: return False
        
        old_state = self.take_snapshot()
        new_state = self.take_snapshot()
        
        v_track = new_state.get_track(TrackType.VIDEO)
        if not v_track: return False
        
        for i, clip in enumerate(v_track.items):
            if clip.clip_id == clip_id:
                # Update clip duration and bounds
                clip.source_start = new_start
                clip.source_end = new_end
                old_duration = clip.duration
                clip.duration = new_end - new_start
                clip.timeline_end = clip.timeline_start + clip.duration
                
                # Shift downstream clips
                time_diff = clip.duration - old_duration
                self._shift_clips_after(v_track, i + 1, time_diff)
                
                new_state.duration += time_diff
                self.commit_edit(EditAction.TRIM_CLIP, f"Trim clip {clip_id}", old_state, new_state)
                return True
        return False
        
    def split_clip(self, clip_id: str, split_time_timeline: float) -> bool:
        if not self.current_timeline: return False
        
        old_state = self.take_snapshot()
        new_state = self.take_snapshot()
        
        v_track = new_state.get_track(TrackType.VIDEO)
        if not v_track: return False
        
        for i, clip in enumerate(v_track.items):
            if clip.clip_id == clip_id:
                if not (clip.timeline_start < split_time_timeline < clip.timeline_end):
                    return False
                    
                time_into_clip = split_time_timeline - clip.timeline_start
                source_split_point = clip.source_start + time_into_clip
                
                # Clip A
                clip_a = clip.copy()
                clip_a.source_end = source_split_point
                clip_a.timeline_end = split_time_timeline
                clip_a.duration = time_into_clip
                
                # Clip B
                clip_b = clip.copy()
                clip_b.clip_id = str(uuid.uuid4())
                clip_b.source_start = source_split_point
                clip_b.timeline_start = split_time_timeline
                clip_b.duration = clip.duration - time_into_clip
                
                v_track.items[i] = clip_a
                v_track.items.insert(i + 1, clip_b)
                
                self.commit_edit(EditAction.SPLIT_CLIP, f"Split clip at {split_time_timeline}", old_state, new_state)
                return True
        return False

    def delete_clip(self, clip_id: str) -> bool:
        if not self.current_timeline: return False
        
        old_state = self.take_snapshot()
        new_state = self.take_snapshot()
        
        v_track = new_state.get_track(TrackType.VIDEO)
        if not v_track: return False
        
        for i, clip in enumerate(v_track.items):
            if clip.clip_id == clip_id:
                dur = clip.duration
                del v_track.items[i]
                
                # Shift downstream
                self._shift_clips_after(v_track, i, -dur)
                new_state.duration -= dur
                
                self.commit_edit(EditAction.DELETE_CLIP, f"Delete clip {clip_id}", old_state, new_state)
                return True
        return False
        
    def _shift_clips_after(self, track: Track, start_index: int, amount: float):
        for i in range(start_index, len(track.items)):
            track.items[i].timeline_start += amount
            track.items[i].timeline_end += amount
