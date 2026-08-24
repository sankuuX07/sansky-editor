"""
Creator Publishing Hub (M18) UI.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, 
    QCheckBox, QLineEdit, QTextEdit, QProgressBar, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from pathlib import Path
import asyncio

from ui.pages.base_page import BasePage
from engines.publishing_engine.publishing_engine import PublishingEngine
from core.models.publishing_models import PublishingProject, ExportTarget, ExportStatus
from engines.library_engine.library_engine import LibraryEngine

class TargetProgressWidget(QFrame):
    def __init__(self, target: ExportTarget, parent=None):
        super().__init__(parent)
        self.target = target
        self.setProperty("class", "Card")
        
        layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        self.name_lbl = QLabel(target.profile.name)
        self.name_lbl.setStyleSheet("font-weight: bold;")
        self.status_lbl = QLabel(target.status.value)
        header.addWidget(self.name_lbl)
        header.addStretch()
        header.addWidget(self.status_lbl)
        layout.addLayout(header)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(int(target.progress))
        layout.addWidget(self.progress)
        
        self.error_lbl = QLabel()
        self.error_lbl.setStyleSheet("color: #E74C3C;")
        self.error_lbl.hide()
        layout.addWidget(self.error_lbl)
        
    def update_state(self):
        self.progress.setValue(int(self.target.progress))
        self.status_lbl.setText(self.target.status.value)
        if self.target.status == ExportStatus.FAILED:
            self.status_lbl.setStyleSheet("color: #E74C3C;")
            self.error_lbl.setText(self.target.error_message or "Unknown error")
            self.error_lbl.show()
        elif self.target.status == ExportStatus.COMPLETED:
            self.status_lbl.setStyleSheet("color: #2ECC71;")
            self.error_lbl.hide()

class PublishingPage(BasePage):
    def __init__(self, backend_loop=None, parent=None):
        super().__init__("Creator Publishing Hub", parent)
        self.engine = PublishingEngine(LibraryEngine())
        self.engine.initialize()
        self.backend_loop = backend_loop
        self.current_project = None
        self.project_entry = None
        self.source_video_path = None
        
        self.platform_checkboxes = {}
        self.progress_widgets = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        main_layout = QHBoxLayout()
        
        # LEFT: Configuration
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 1. Platform Selection
        plat_frame = QFrame()
        plat_frame.setProperty("class", "Card")
        plat_layout = QVBoxLayout(plat_frame)
        plat_layout.addWidget(QLabel("1. Select Platforms", property="class:Header2"))
        
        for profile in self.engine.get_profiles():
            cb = QCheckBox(profile.name)
            self.platform_checkboxes[profile.platform] = cb
            plat_layout.addWidget(cb)
            
        left_layout.addWidget(plat_frame)
        
        # 2. Metadata Editor
        meta_frame = QFrame()
        meta_frame.setProperty("class", "Card")
        meta_layout = QVBoxLayout(meta_frame)
        meta_layout.addWidget(QLabel("2. Metadata", property="class:Header2"))
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Video Title...")
        meta_layout.addWidget(QLabel("Title:"))
        meta_layout.addWidget(self.title_edit)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Description...")
        meta_layout.addWidget(QLabel("Description:"))
        meta_layout.addWidget(self.desc_edit)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("#gaming #highlights")
        meta_layout.addWidget(QLabel("Hashtags:"))
        meta_layout.addWidget(self.tags_edit)
        
        regen_btn = QPushButton("Regenerate AI Metadata")
        regen_btn.clicked.connect(self._regenerate_metadata)
        meta_layout.addWidget(regen_btn)
        
        left_layout.addWidget(meta_frame)
        left_layout.addStretch()
        
        # RIGHT: Thumbnails & Export
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 3. Thumbnail
        thumb_frame = QFrame()
        thumb_frame.setProperty("class", "Card")
        thumb_layout = QVBoxLayout(thumb_frame)
        thumb_layout.addWidget(QLabel("3. Thumbnail", property="class:Header2"))
        
        self.thumb_preview = QLabel("No Thumbnail Selected")
        self.thumb_preview.setAlignment(Qt.AlignCenter)
        self.thumb_preview.setStyleSheet("background-color: #1A1D24; min-height: 150px;")
        thumb_layout.addWidget(self.thumb_preview)
        
        right_layout.addWidget(thumb_frame)
        
        # 4. Export Controls & Progress
        export_frame = QFrame()
        export_frame.setProperty("class", "Card")
        self.export_layout = QVBoxLayout(export_frame)
        self.export_layout.addWidget(QLabel("4. Export Package", property="class:Header2"))
        
        self.export_btn = QPushButton("Create Export Package")
        self.export_btn.setProperty("class", "PrimaryButton")
        self.export_btn.setStyleSheet("background-color: #2ECC71;")
        self.export_btn.clicked.connect(self._start_export)
        self.export_layout.addWidget(self.export_btn)
        
        self.progress_container = QWidget()
        self.progress_layout = QVBoxLayout(self.progress_container)
        self.export_layout.addWidget(self.progress_container)
        
        right_layout.addWidget(export_frame)
        right_layout.addStretch()
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        self.content_layout.addLayout(main_layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_ui_progress)

    def load_project(self, entry):
        self.project_entry = entry
        
        # Resolve source video path (assuming we want to export the FINAL output of M7)
        if entry.output_path:
            p = Path(entry.output_path) / "output.mp4"
            if p.exists():
                self.source_video_path = p
        
        if not self.source_video_path:
            QMessageBox.warning(self, "Source Missing", "Could not find final output.mp4 in the project folder.")
            return
            
        self.current_project = PublishingProject(
            project_id=entry.project_id,
            source_job_id=entry.project_id
        )
        
        self._regenerate_metadata()

    def _regenerate_metadata(self):
        if not self.project_entry: return
        report = self.engine.generate_metadata(self.project_entry.output_path)
        
        if report:
            self.title_edit.setText(report.title_suggestions[0] if report.title_suggestions else "")
            self.desc_edit.setText(report.description_suggestion)
            self.tags_edit.setText(" ".join(report.hashtags))
            
            if report.recommended_thumbnail:
                thumb_path = Path(self.project_entry.output_path) / "thumbnails" / report.recommended_thumbnail
                if thumb_path.exists():
                    from PySide6.QtGui import QPixmap
                    pixmap = QPixmap(str(thumb_path))
                    self.thumb_preview.setPixmap(pixmap.scaled(self.thumb_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.current_project.thumbnail_path = str(thumb_path)
                    
    def _start_export(self):
        if not self.current_project or not self.source_video_path:
            return
            
        # Build targets
        targets = []
        for profile in self.engine.get_profiles():
            if self.platform_checkboxes[profile.platform].isChecked():
                target = ExportTarget(
                    profile=profile,
                    title=self.title_edit.text(),
                    description=self.desc_edit.toPlainText(),
                    hashtags=self.tags_edit.text().split(),
                    thumbnail_path=getattr(self.current_project, 'thumbnail_path', None)
                )
                targets.append(target)
                
        if not targets:
            QMessageBox.warning(self, "No Platform Selected", "Please select at least one platform.")
            return
            
        self.current_project.export_targets = targets
        
        # Clear old progress UI
        for w in self.progress_widgets:
            self.progress_layout.removeWidget(w)
            w.deleteLater()
        self.progress_widgets.clear()
        
        for t in targets:
            pw = TargetProgressWidget(t)
            self.progress_widgets.append(pw)
            self.progress_layout.addWidget(pw)
            
        self.export_btn.setEnabled(False)
        self.timer.start(500)
        
        if self.backend_loop:
            out_dir = Path(self.project_entry.output_path) / "publishing" / f"pub_{self.current_project.publishing_id[:8]}"
            asyncio.run_coroutine_threadsafe(
                self.engine.export_package(self.current_project, self.source_video_path, out_dir),
                self.backend_loop
            )
            
    def _update_ui_progress(self):
        all_done = True
        for pw in self.progress_widgets:
            pw.update_state()
            if pw.target.status in [ExportStatus.PENDING, ExportStatus.PROCESSING]:
                all_done = False
                
        if all_done:
            self.timer.stop()
            self.export_btn.setEnabled(True)
            QMessageBox.information(self, "Export Finished", "Publishing packages have been processed.")
