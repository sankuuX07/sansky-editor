import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from core.models.library_models import ProjectLibraryEntry, ProjectType

class LibraryProjectCard(QFrame):
    clicked = Signal(ProjectLibraryEntry)
    
    def __init__(self, entry: ProjectLibraryEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setProperty("class", "Card")
        # Ensure card shrinks instead of stretching forever
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setStyleSheet("""
            LibraryProjectCard {
                background-color: #171A22;
                border-radius: 8px;
                border: 1px solid transparent;
            }
            LibraryProjectCard:hover {
                background-color: #1A1D24;
                border: 1px solid #3498DB;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header (Icon/Type + Name)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        type_icon = QLabel("🎬" if entry.project_type == ProjectType.SINGLE_VIDEO.value else "📚")
        type_icon.setStyleSheet("font-size: 16px;")
        
        name_lbl = QLabel(entry.source_name)
        name_lbl.setProperty("class", "Header2")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        fav_lbl = QLabel("⭐" if entry.favorite else "")
        
        header_layout.addWidget(type_icon)
        header_layout.addWidget(name_lbl, 1)
        header_layout.addWidget(fav_lbl)
        
        # Meta info
        meta_layout = QHBoxLayout()
        
        status_lbl = QLabel(entry.status)
        if "COMPLETED" in entry.status or "SUCCESS" in entry.status:
            status_lbl.setStyleSheet("color: #2ECC71; font-weight: bold; font-size: 12px;")
        elif "FAILED" in entry.status:
            status_lbl.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 12px;")
        else:
            status_lbl.setStyleSheet("color: #F1C40F; font-weight: bold; font-size: 12px;")
            
        import datetime
        dt_str = datetime.datetime.fromtimestamp(entry.updated_at).strftime("%Y-%m-%d %H:%M")
        date_lbl = QLabel(dt_str)
        date_lbl.setStyleSheet("color: #8C96A8; font-size: 12px;")
        
        meta_layout.addWidget(status_lbl)
        meta_layout.addStretch()
        meta_layout.addWidget(date_lbl)
        
        layout.addLayout(header_layout)
        layout.addLayout(meta_layout)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.entry)
        super().mousePressEvent(event)
