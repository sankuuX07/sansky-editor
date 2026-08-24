from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices, QUrl
import os
from pathlib import Path
from core.models.library_models import ProjectLibraryEntry
from engines.library_engine.library_engine import LibraryEngine

class LibraryDetailsDialog(QDialog):
    action_requested = Signal(str, ProjectLibraryEntry) # Action string, entry
    
    def __init__(self, entry: ProjectLibraryEntry, lib_engine: LibraryEngine, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.lib_engine = lib_engine
        self.setWindowTitle("Project Details")
        self.setMinimumWidth(500)
        
        self.setStyleSheet("""
            QDialog { background-color: #12141A; }
            QLabel { color: #FFFFFF; font-family: Inter, sans-serif; }
            QPushButton { 
                background-color: #3498DB; 
                color: white; 
                border: none; 
                border-radius: 6px; 
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980B9; }
            QPushButton.Secondary { 
                background-color: #2C3E50; 
            }
            QPushButton.Secondary:hover { background-color: #34495E; }
            QPushButton.Danger {
                background-color: #E74C3C;
            }
            QPushButton.Danger:hover { background-color: #C0392B; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel(self.entry.source_name)
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)
        
        # Info grid
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        info_layout.addWidget(self._prop("Project ID", self.entry.project_id))
        info_layout.addWidget(self._prop("Type", self.entry.project_type))
        info_layout.addWidget(self._prop("Status", self.entry.status))
        
        import datetime
        dt_str = datetime.datetime.fromtimestamp(self.entry.created_at).strftime("%Y-%m-%d %H:%M")
        info_layout.addWidget(self._prop("Created", dt_str))
        
        # Health Check
        health = self.lib_engine.check_health(self.entry.project_id)
        health_color = "#2ECC71" if health == "AVAILABLE" else "#E74C3C"
        health_lbl = QLabel(f"Health: <font color='{health_color}'>{health}</font>")
        info_layout.addWidget(health_lbl)
        
        layout.addLayout(info_layout)
        
        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel(f"Highlights: {self.entry.highlight_count}"))
        stats_layout.addWidget(QLabel(f"Thumbnails: {self.entry.thumbnail_count}"))
        stats_layout.addWidget(QLabel(f"Reports: {'Yes' if self.entry.creator_report_path else 'No'}"))
        layout.addLayout(stats_layout)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        open_btn = QPushButton("Open Folder")
        open_btn.clicked.connect(self._open_folder)
        
        reedit_btn = QPushButton("Re-Edit")
        reedit_btn.setProperty("class", "Secondary")
        reedit_btn.clicked.connect(lambda: self._emit_action("reedit"))
        
        publish_btn = QPushButton("Publish")
        publish_btn.setProperty("class", "Secondary")
        publish_btn.setStyleSheet("background-color: #9B59B6;")
        publish_btn.clicked.connect(lambda: self._emit_action("publish"))
        
        fav_btn = QPushButton("Unfavorite" if self.entry.favorite else "Favorite")
        fav_btn.setProperty("class", "Secondary")
        fav_btn.clicked.connect(self._toggle_fav)
        self.fav_btn = fav_btn
        
        archive_btn = QPushButton("Unarchive" if self.entry.archived else "Archive")
        archive_btn.setProperty("class", "Secondary")
        archive_btn.clicked.connect(self._toggle_archive)
        self.archive_btn = archive_btn
        
        delete_btn = QPushButton("Delete Outputs")
        delete_btn.setProperty("class", "Danger")
        delete_btn.clicked.connect(self._delete_outputs)
        
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(reedit_btn)
        btn_layout.addWidget(publish_btn)
        btn_layout.addWidget(fav_btn)
        btn_layout.addWidget(archive_btn)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
    def _prop(self, k, v):
        lbl = QLabel(f"<b>{k}:</b> {v}")
        lbl.setStyleSheet("font-size: 13px;")
        return lbl
        
    def _open_folder(self):
        if self.entry.output_path and os.path.exists(self.entry.output_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.entry.output_path))
        else:
            QMessageBox.warning(self, "Not Found", "Output folder is missing.")
            
    def _emit_action(self, action):
        self.action_requested.emit(action, self.entry)
        self.accept()
        
    def _toggle_fav(self):
        is_fav = self.lib_engine.toggle_favorite(self.entry.project_id)
        self.fav_btn.setText("Unfavorite" if is_fav else "Favorite")
        self.action_requested.emit("refresh", self.entry)
        
    def _toggle_archive(self):
        is_arch = self.lib_engine.toggle_archive(self.entry.project_id)
        self.archive_btn.setText("Unarchive" if is_arch else "Archive")
        self.action_requested.emit("refresh", self.entry)
        
    def _delete_outputs(self):
        reply = QMessageBox.question(self, 'Confirm Deletion', 
            "Are you sure you want to delete all output files for this project?\n\nThe source video will NOT be deleted.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            if self.lib_engine.delete_outputs(self.entry.project_id):
                QMessageBox.information(self, "Deleted", "Outputs deleted successfully.")
                self.action_requested.emit("refresh", self.entry)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete outputs or directory was missing.")
