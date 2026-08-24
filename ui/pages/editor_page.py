"""
Smart Manual Editor Workspace (M17)
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, 
    QSplitter, QListWidget, QListWidgetItem, QSlider, QLineEdit, QMessageBox,
    QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from ui.pages.base_page import BasePage
from engines.smart_editor_engine.smart_editor_engine import SmartEditorEngine
from core.models.smart_editor_models import TrackType, EditAction
from engines.library_engine.library_engine import LibraryEngine

try:
    from PySide6.QtMultimedia import QMediaPlayer
    from PySide6.QtMultimediaWidgets import QVideoWidget
    HAS_MULTIMEDIA = True
except ImportError:
    HAS_MULTIMEDIA = False

class TimelineTrackWidget(QFrame):
    def __init__(self, track_name, track_data, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")
        self.track_data = track_data
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        name_lbl = QLabel(track_name)
        name_lbl.setFixedWidth(80)
        name_lbl.setStyleSheet("font-weight: bold; color: #8C96A8;")
        layout.addWidget(name_lbl)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(60)
        self.scroll.setStyleSheet("background-color: #0F1115; border-radius: 4px; border: none;")
        
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        self.content_layout.setAlignment(Qt.AlignLeft)
        
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll, 1)

    def populate(self, on_clip_clicked):
        for i in reversed(range(self.content_layout.count())):
            w = self.content_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        if not self.track_data: return
            
        for item in self.track_data.items:
            clip_btn = QPushButton()
            
            if self.track_data.track_type == TrackType.VIDEO:
                dur = getattr(item, 'duration', 0.0)
                clip_btn.setText(f"Clip ({dur:.1f}s)")
                clip_btn.setFixedWidth(max(50, int(dur * 5))) # 5px per second approx
                clip_btn.setStyleSheet("background-color: #3498DB; color: white; border: none; border-radius: 4px;")
            elif self.track_data.track_type == TrackType.CAPTIONS:
                dur = item.end_time - item.start_time
                clip_btn.setText(f"T: {item.text[:10]}...")
                clip_btn.setFixedWidth(max(40, int(dur * 5)))
                clip_btn.setStyleSheet("background-color: #F39C12; color: white; border: none; border-radius: 4px;")
                
            clip_btn.clicked.connect(lambda checked=False, i=item: on_clip_clicked(i, self.track_data.track_type))
            self.content_layout.addWidget(clip_btn)

class EditorPage(BasePage):
    render_requested = Signal(object) # emit timeline project ID or path
    
    def __init__(self, parent=None):
        super().__init__("Smart Manual Editor", parent)
        self.engine = SmartEditorEngine(LibraryEngine())
        self.selected_item = None
        self.selected_track_type = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        splitter = QSplitter(Qt.Vertical)
        
        # TOP: Preview + Properties
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0,0,0,0)
        
        # Preview Area
        self.preview_container = QFrame()
        self.preview_container.setProperty("class", "Card")
        preview_layout = QVBoxLayout(self.preview_container)
        
        if HAS_MULTIMEDIA:
            self.video_widget = QVideoWidget()
            self.media_player = QMediaPlayer()
            self.media_player.setVideoOutput(self.video_widget)
            preview_layout.addWidget(self.video_widget, 1)
        else:
            self.placeholder_lbl = QLabel("Preview Not Available (QtMultimedia missing)")
            self.placeholder_lbl.setAlignment(Qt.AlignCenter)
            self.placeholder_lbl.setStyleSheet("background-color: #000; color: #fff; font-size: 16px;")
            preview_layout.addWidget(self.placeholder_lbl, 1)
            
        self.controls_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.setProperty("class", "PrimaryButton")
        self.controls_layout.addWidget(self.play_btn)
        preview_layout.addLayout(self.controls_layout)
        
        top_layout.addWidget(self.preview_container, 2)
        
        # Properties Area
        self.props_container = QFrame()
        self.props_container.setProperty("class", "Card")
        props_layout = QVBoxLayout(self.props_container)
        
        props_title = QLabel("Properties")
        props_title.setProperty("class", "Header2")
        props_layout.addWidget(props_title)
        
        self.props_scroll = QScrollArea()
        self.props_scroll.setWidgetResizable(True)
        self.props_scroll.setStyleSheet("background: transparent; border: none;")
        self.props_content = QWidget()
        self.props_inner_layout = QVBoxLayout(self.props_content)
        self.props_inner_layout.setAlignment(Qt.AlignTop)
        self.props_scroll.setWidget(self.props_content)
        props_layout.addWidget(self.props_scroll)
        
        top_layout.addWidget(self.props_container, 1)
        
        splitter.addWidget(top_widget)
        
        # BOTTOM: Timeline & Tools
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0,0,0,0)
        
        # Tools
        tools_layout = QHBoxLayout()
        self.btn_undo = QPushButton("Undo")
        self.btn_redo = QPushButton("Redo")
        self.btn_split = QPushButton("Split")
        self.btn_delete = QPushButton("Delete")
        self.btn_ai_suggest = QPushButton("AI Suggest")
        self.btn_save = QPushButton("Save Version")
        self.btn_render = QPushButton("Render")
        
        for btn in [self.btn_undo, self.btn_redo, self.btn_split, self.btn_delete, self.btn_ai_suggest]:
            btn.setProperty("class", "SecondaryButton")
            tools_layout.addWidget(btn)
            
        tools_layout.addStretch()
        self.btn_save.setProperty("class", "PrimaryButton")
        self.btn_render.setProperty("class", "PrimaryButton")
        self.btn_render.setStyleSheet("background-color: #2ECC71;")
        tools_layout.addWidget(self.btn_save)
        tools_layout.addWidget(self.btn_render)
        
        bottom_layout.addLayout(tools_layout)
        
        # Tracks
        self.tracks_layout = QVBoxLayout()
        bottom_layout.addLayout(self.tracks_layout)
        bottom_layout.addStretch()
        
        splitter.addWidget(bottom_widget)
        self.content_layout.addWidget(splitter)
        
        # Connect signals
        self.btn_undo.clicked.connect(self._on_undo)
        self.btn_redo.clicked.connect(self._on_redo)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_save.clicked.connect(self._on_save)
        
    def load_project(self, entry):
        if self.engine.load_project_from_library(entry):
            self.refresh_timeline()
        else:
            QMessageBox.warning(self, "Load Error", "Failed to load timeline for this project. Ensure project.json exists in the output folder.")
            
    def refresh_timeline(self):
        # Clear tracks
        for i in reversed(range(self.tracks_layout.count())):
            w = self.tracks_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        if not self.engine.current_timeline:
            return
            
        for track in self.engine.current_timeline.tracks:
            tw = TimelineTrackWidget(track.track_type.value, track)
            tw.populate(self._on_clip_clicked)
            self.tracks_layout.addWidget(tw)
            
        self._refresh_props()
        
    def _on_clip_clicked(self, item, track_type):
        self.selected_item = item
        self.selected_track_type = track_type
        self._refresh_props()
        
    def _refresh_props(self):
        for i in reversed(range(self.props_inner_layout.count())):
            w = self.props_inner_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        if not self.selected_item:
            lbl = QLabel("No item selected.")
            self.props_inner_layout.addWidget(lbl)
            return
            
        if self.selected_track_type == TrackType.VIDEO:
            self._build_video_props()
        elif self.selected_track_type == TrackType.CAPTIONS:
            self._build_caption_props()
            
    def _build_video_props(self):
        clip = self.selected_item
        self.props_inner_layout.addWidget(QLabel(f"Clip ID: {clip.clip_id}"))
        self.props_inner_layout.addWidget(QLabel(f"Source Start: {clip.source_start:.1f}"))
        self.props_inner_layout.addWidget(QLabel(f"Source End: {clip.source_end:.1f}"))
        self.props_inner_layout.addWidget(QLabel(f"Timeline Start: {clip.timeline_start:.1f}"))
        
        # Trim Controls
        trim_btn = QPushButton("Trim Clip (Start + 1s)")
        trim_btn.clicked.connect(lambda: self._test_trim(clip))
        self.props_inner_layout.addWidget(trim_btn)
        
    def _test_trim(self, clip):
        if self.engine.trim_clip(clip.clip_id, clip.source_start + 1.0, clip.source_end):
            self.refresh_timeline()
            
    def _build_caption_props(self):
        cap = self.selected_item
        self.props_inner_layout.addWidget(QLabel(f"Text: {cap.text}"))
        # Add a line edit to change text
        self.cap_edit = QLineEdit(cap.text)
        self.props_inner_layout.addWidget(self.cap_edit)
        
        update_btn = QPushButton("Update Caption")
        update_btn.clicked.connect(self._update_caption)
        self.props_inner_layout.addWidget(update_btn)
        
    def _update_caption(self):
        if self.selected_item and self.selected_track_type == TrackType.CAPTIONS:
            new_text = self.cap_edit.text()
            # Need to implement caption edit in engine
            self.selected_item.text = new_text
            self.refresh_timeline()

    def _on_delete(self):
        if self.selected_item and self.selected_track_type == TrackType.VIDEO:
            if self.engine.delete_clip(self.selected_item.clip_id):
                self.selected_item = None
                self.refresh_timeline()
                
    def _on_undo(self):
        if self.engine.undo():
            self.selected_item = None
            self.refresh_timeline()
            
    def _on_redo(self):
        if self.engine.redo():
            self.selected_item = None
            self.refresh_timeline()
            
    def _on_save(self):
        new_id = self.engine.save_version()
        if new_id:
            QMessageBox.information(self, "Saved", f"Version saved: {new_id}")
