from PySide6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QGridLayout, QFrame, QSpacerItem, QSizePolicy, QFileDialog
from PySide6.QtCore import Qt, QTimer, Signal
from ui.pages.base_page import BasePage
import shutil

class DashboardPage(BasePage):
    # Signal to request navigation and file loading
    files_dropped = Signal(list)

    def __init__(self, engine_manager=None, parent=None):
        super().__init__("Dashboard", parent)
        self.engine_manager = engine_manager
        
        # Remove standard title from BasePage since we want a custom Hero
        self._clear_layout(self.content_layout)
        
        # --- Hero Section ---
        hero_widget = QWidget()
        hero_layout = QVBoxLayout(hero_widget)
        hero_layout.setAlignment(Qt.AlignCenter)
        hero_layout.setSpacing(16)
        
        title = QLabel("Ready to Create.")
        title.setProperty("class", "HeroTitle")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Import gameplay and generate professional shorts in one click.")
        subtitle.setProperty("class", "Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        hero_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # --- Massive Drag & Drop Area ---
        self.drop_area = QFrame()
        self.drop_area.setProperty("class", "Card")
        self.drop_area.setAcceptDrops(True)
        self.drop_area.setMinimumHeight(250)
        self.drop_area.setStyleSheet("""
            QFrame.Card {
                border: 2px dashed #2D3344;
                background-color: rgba(31, 35, 48, 0.5);
            }
            QFrame.Card:hover {
                border: 2px solid #4364F7;
                background-color: #1F2330;
            }
        """)
        
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setAlignment(Qt.AlignCenter)
        
        drop_icon = QLabel("📁") # Placeholder for an actual SVG icon if available
        drop_icon.setStyleSheet("font-size: 48px; color: #4364F7;")
        drop_icon.setAlignment(Qt.AlignCenter)
        
        drop_text = QLabel("Drag & Drop Media Files Here")
        drop_text.setProperty("class", "Header2")
        drop_text.setAlignment(Qt.AlignCenter)
        
        drop_sub = QLabel("Supports MP4, MKV, MOV, AVI")
        drop_sub.setProperty("class", "Subtitle")
        drop_sub.setAlignment(Qt.AlignCenter)
        
        browse_btn = QPushButton("Browse Files")
        browse_btn.setProperty("class", "PrimaryButton")
        browse_btn.setFixedWidth(200)
        browse_btn.clicked.connect(self._on_browse_clicked)
        
        drop_layout.addWidget(drop_icon)
        drop_layout.addWidget(drop_text)
        drop_layout.addWidget(drop_sub)
        drop_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        drop_layout.addWidget(browse_btn, 0, Qt.AlignCenter)
        
        # Event overrides for drop area
        self.drop_area.dragEnterEvent = self._drag_enter_event
        self.drop_area.dropEvent = self._drop_event
        
        hero_layout.addWidget(self.drop_area)
        self.content_layout.addWidget(hero_widget)
        
        self.content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # --- Bottom Grid: Health & Recent ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(24)
        
        # System Status
        health_card = QWidget()
        health_card.setProperty("class", "Card")
        health_layout = QVBoxLayout(health_card)
        health_title = QLabel("System Status")
        health_title.setProperty("class", "Header3")
        health_layout.addWidget(health_title)
        
        grid = QGridLayout()
        grid.setSpacing(16)
        self.status_labels = {}
        
        indicators = ["GPU", "Whisper", "Premiere", "FFmpeg", "Automation Engine"]
        for i, ind in enumerate(indicators):
            lbl = QLabel(ind)
            val = QLabel("Checking...")
            val.setProperty("class", "Subtitle")
            self.status_labels[ind] = val
            grid.addWidget(lbl, i // 2, (i % 2) * 2)
            grid.addWidget(val, i // 2, (i % 2) * 2 + 1)
            
        health_layout.addLayout(grid)
        bottom_layout.addWidget(health_card, 2)
        
        # Recent/Quick Generate
        recent_card = QWidget()
        recent_card.setProperty("class", "Card")
        recent_layout = QVBoxLayout(recent_card)
        recent_title = QLabel("Quick Actions")
        recent_title.setProperty("class", "Header3")
        recent_layout.addWidget(recent_title)
        
        empty_recent = QLabel("No recent projects found.")
        empty_recent.setProperty("class", "Subtitle")
        recent_layout.addWidget(empty_recent)
        recent_layout.addStretch()
        
        quick_gen_btn = QPushButton("Quick Generate (Default Preset)")
        quick_gen_btn.setProperty("class", "SecondaryButton")
        recent_layout.addWidget(quick_gen_btn)
        
        bottom_layout.addWidget(recent_card, 1)
        
        self.content_layout.addLayout(bottom_layout)
        
        # Start health check timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_health)
        self.timer.start(2000)
        self.update_health()
        
    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def _drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                QFrame.Card {
                    border: 2px solid #2ECC71;
                    background-color: rgba(46, 204, 113, 0.1);
                }
            """)
            
    def _drop_event(self, event):
        self.drop_area.setStyleSheet("""
            QFrame.Card {
                border: 2px dashed #2D3344;
                background-color: rgba(31, 35, 48, 0.5);
            }
        """)
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".mp4", ".mkv", ".mov", ".avi")):
                paths.append(path)
        if paths:
            self.files_dropped.emit(paths)
            
    def _on_browse_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", "Video Files (*.mp4 *.mkv *.mov *.avi)")
        if files:
            self.files_dropped.emit(files)

    def update_health(self):
        self.status_labels["GPU"].setText("Accelerated")
        self.status_labels["GPU"].setProperty("class", "StatusGreen")
        
        ffmpeg_exists = shutil.which("ffmpeg") is not None
        self.status_labels["FFmpeg"].setText("Installed" if ffmpeg_exists else "Missing")
        self.status_labels["FFmpeg"].setProperty("class", "StatusGreen" if ffmpeg_exists else "StatusRed")
        
        self.status_labels["Whisper"].setText("Ready")
        self.status_labels["Premiere"].setText("Ready")
        
        if self.engine_manager:
            try:
                auto = self.engine_manager.get_engine("automation_engine")
                self.status_labels["Automation Engine"].setText("Running" if auto.health_check() else "Stopped")
                self.status_labels["Automation Engine"].setProperty("class", "StatusGreen" if auto.health_check() else "StatusAmber")
            except KeyError:
                self.status_labels["Automation Engine"].setText("Not Registered")
                
        # Force style re-eval
        for val in self.status_labels.values():
            val.style().unpolish(val)
            val.style().polish(val)
