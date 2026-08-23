from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QFrame, QMessageBox, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtCore import QUrl
from ui.pages.base_page import BasePage
import os

class ClipCard(QFrame):
    def __init__(self, clip, premiere_path, output_dir, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")
        self.premiere_path = premiere_path
        self.output_dir = output_dir
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(24)
        
        self.thumbnail_lbl = QLabel()
        self.thumbnail_lbl.setFixedSize(240, 135)
        self.thumbnail_lbl.setStyleSheet("background-color: #171A22; border-radius: 8px;")
        self.thumbnail_lbl.setAlignment(Qt.AlignCenter)
        
        if getattr(clip, 'thumbnail_path', None) and os.path.exists(clip.thumbnail_path):
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(str(clip.thumbnail_path))
            self.thumbnail_lbl.setPixmap(pixmap.scaled(self.thumbnail_lbl.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            self.thumbnail_lbl.setText("Thumbnail Unavailable")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        name_lbl = QLabel(f"Short Sequence {clip.clip_id.split('_')[-1] if '_' in clip.clip_id else clip.clip_id}")
        name_lbl.setProperty("class", "Header2")
        
        meta_grid = QGridLayout()
        meta_grid.setSpacing(12)
        
        duration = round(clip.end_time - clip.start_time, 2)
        meta_grid.addWidget(self._tag("Source", os.path.basename(str(clip.source_video))), 0, 0)
        meta_grid.addWidget(self._tag("Duration", f"{duration}s"), 0, 1)
        meta_grid.addWidget(self._tag("Confidence", f"{round(clip.score, 2)}%"), 1, 0)
        meta_grid.addWidget(self._tag("Captions", f"{len(clip.captions)} blocks"), 1, 1)
        
        info_layout.addWidget(name_lbl)
        info_layout.addLayout(meta_grid)
        info_layout.addStretch()
        
        action_layout = QVBoxLayout()
        action_layout.setSpacing(12)
        
        open_video_btn = QPushButton("Play Video")
        open_video_btn.setProperty("class", "PrimaryButton")
        open_video_btn.clicked.connect(self._open_video)
        
        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setProperty("class", "SecondaryButton")
        open_folder_btn.clicked.connect(self._open_folder)
        
        action_layout.addWidget(open_video_btn)
        action_layout.addWidget(open_folder_btn)
        action_layout.addStretch()
        
        layout.addWidget(self.thumbnail_lbl)
        layout.addLayout(info_layout, 1)
        layout.addLayout(action_layout)
        
    def _tag(self, label, value):
        w = QWidget()
        w.setStyleSheet("background-color: #171A22; border-radius: 6px; padding: 4px 8px;")
        l = QHBoxLayout(w)
        l.setContentsMargins(8, 4, 8, 4)
        lbl1 = QLabel(f"{label}:")
        lbl1.setStyleSheet("color: #8C96A8; font-size: 12px;")
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
        l.addWidget(lbl1)
        l.addWidget(val_lbl)
        return w

    def _open_folder(self):
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create output directory:\n{e}")
                return
                
        if not os.listdir(self.output_dir):
            QMessageBox.information(self, "Directory Empty", "The output folder was created, but no files have been generated yet.")
            
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_dir))
            
    def _open_video(self):
        video_path = os.path.join(self.output_dir, "output.mp4")
        if os.path.exists(video_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(video_path))
        else:
            QMessageBox.warning(self, "Video Not Found", "No valid MP4 video file was generated. The Video Engine may have failed during rendering.")

class ResultsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Generated Shorts", parent)
        
        self.result = None
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(16)
        
        # --- Empty State ---
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        empty_icon = QLabel("✨")
        empty_icon.setStyleSheet("font-size: 64px;")
        empty_icon.setAlignment(Qt.AlignCenter)
        
        empty_title = QLabel("No Shorts Generated")
        empty_title.setProperty("class", "Header2")
        empty_title.setAlignment(Qt.AlignCenter)
        
        empty_sub = QLabel("Go to the Dashboard to start creating premium short-form content.")
        empty_sub.setProperty("class", "Subtitle")
        empty_sub.setAlignment(Qt.AlignCenter)
        
        empty_layout.addStretch()
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_sub)
        empty_layout.addStretch()
        
        self.scroll_layout.addWidget(self.empty_widget)
        self.scroll_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        self.content_layout.addWidget(self.scroll)
        
    def display_result(self, result):
        self.result = result
        
        # Clear existing cards
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            widget = item.widget()
            if widget and widget is not self.empty_widget:
                self.scroll_layout.takeAt(i)
                widget.deleteLater()
                
        if not result or not result.projects:
            self.empty_widget.show()
            if self.scroll_layout.indexOf(self.empty_widget) == -1:
                self.scroll_layout.insertWidget(0, self.empty_widget)
            return
            
        self.empty_widget.hide()
        
        # Add summary header
        summary = QLabel(f"Generated {sum(len(p.clips) for p in result.projects)} sequences successfully.")
        summary.setProperty("class", "Subtitle")
        summary.setStyleSheet("color: #2ECC71;")
        self.scroll_layout.insertWidget(0, summary)
        
        # Add Pipeline Stage Statuses if present
        if hasattr(result, "stage_statuses") and result.stage_statuses:
            status_container = QWidget()
            status_container.setStyleSheet("background-color: #1A1D24; border-radius: 8px; padding: 12px;")
            status_layout = QVBoxLayout(status_container)
            
            title = QLabel("PIPELINE STATUS")
            title.setStyleSheet("color: #8C96A8; font-weight: bold; font-size: 11px;")
            status_layout.addWidget(title)
            
            grid = QGridLayout()
            grid.setSpacing(8)
            row, col = 0, 0
            for stage, state in result.stage_statuses.items():
                lbl_stage = QLabel(f"{stage}:")
                lbl_stage.setStyleSheet("color: #8C96A8; font-size: 12px;")
                lbl_state = QLabel(state)
                
                if "SUCCESS" in state or "COMPLETED" in state:
                    lbl_state.setStyleSheet("color: #2ECC71; font-weight: bold; font-size: 12px;")
                elif "FAILED" in state:
                    lbl_state.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 12px;")
                elif "SKIPPED" in state or "PARTIAL" in state:
                    lbl_state.setStyleSheet("color: #F1C40F; font-weight: bold; font-size: 12px;")
                else:
                    lbl_state.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 12px;")
                    
                grid.addWidget(lbl_stage, row, col * 2)
                grid.addWidget(lbl_state, row, col * 2 + 1)
                
                col += 1
                if col > 1:
                    col = 0
                    row += 1
            
            status_layout.addLayout(grid)
            self.scroll_layout.insertWidget(1, status_container)
        
        for project in result.projects:
            for clip in project.clips:
                card = ClipCard(clip, project.premiere_project_path, project.settings.output_directory)
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)
