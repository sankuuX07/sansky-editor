from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizeGrip
from PySide6.QtCore import Qt

from ui.navigation.title_bar import TitleBar
from ui.navigation.nav_rail import NavRail
from ui.navigation.status_bar import StatusBar

from ui.pages.dashboard_page import DashboardPage
from ui.pages.library_page import LibraryPage
from ui.pages.media_page import MediaPage
from ui.pages.processing_page import ProcessingPage
from ui.pages.results_page import ResultsPage
from ui.pages.settings_page import SettingsPage
from ui.pages.logs_page import LogsPage
from ui.pages.about_page import AboutPage

from ui.controllers.backend_worker import ShortsGenerationWorker
from ui.animations.fade_stacked_widget import FadeStackedWidget
from ui.controllers.log_handler import QtLogHandler

class MainWindow(QMainWindow):
    def __init__(self, shorts_engine, backend_loop, engine_manager=None, log_handler=None):
        super().__init__()
        self.shorts_engine = shorts_engine
        self.backend_loop = backend_loop
        self.engine_manager = engine_manager
        
        if log_handler:
            log_handler.signals.log_emitted.connect(self._on_log_emitted)
        
        self.setWindowTitle("Sansky AI Editor - Pro")
        self.resize(1280, 800)
        
        # Frameless Window Hint
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.worker = None
        
        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Title Bar
        self.title_bar = TitleBar(parent=self)
        self.title_bar.close_requested.connect(self.close)
        self.title_bar.minimize_requested.connect(self.showMinimized)
        self.title_bar.maximize_requested.connect(self.toggle_maximize)
        main_layout.addWidget(self.title_bar)
        
        # 2. Content Area (Nav + Pages)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.nav_rail = NavRail()
        self.nav_rail.navigation_requested.connect(self.navigate_to)
        content_layout.addWidget(self.nav_rail)
        
        self.stacked_widget = FadeStackedWidget()
        
        self.pages = {
            "dashboard": DashboardPage(self.engine_manager),
            "library": LibraryPage(),
            "media": MediaPage(),
            "processing": ProcessingPage(),
            "results": ResultsPage(),
            "settings": SettingsPage(),
            "logs": LogsPage(),
            "about": AboutPage()
        }
        
        self.pages["library"].reedit_requested.connect(self.handle_reedit)
        
        self.pages["media"].generate_requested.connect(self.start_generation)
        self.pages["dashboard"].files_dropped.connect(self._on_dashboard_files_dropped)
        self.pages["processing"].cancel_requested.connect(self.cancel_generation)
        
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
            
        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_widget)
        
        # 3. Status Bar
        self.status_bar = StatusBar()
        
        # Add size grip to status bar area
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.addWidget(self.status_bar)
        
        size_grip = QSizeGrip(self)
        status_layout.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        
        main_layout.addLayout(status_layout)
        
        self.navigate_to("dashboard")
        
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            
    def navigate_to(self, page_id: str):
        if page_id in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_id])
            self.nav_rail.set_active(page_id)

    def _on_dashboard_files_dropped(self, paths):
        # When files are dropped on the dashboard, navigate to media page and load them
        self.navigate_to("media")
        
        # We need to manually add them to the media page's processing queue
        for path in paths:
            if path not in self.pages["media"].video_paths:
                self.pages["media"].video_paths.append(path)
                
        self.pages["media"].process_new_files(paths)

    def start_generation(self, video_paths, output_dir):
        settings = self.pages["settings"].get_settings()
        settings.output_directory = output_dir
        
        self.navigate_to("processing")
        self.pages["processing"].status_lbl.setText("Initializing worker...")
        self.pages["processing"].start_timer()
        
        self.worker = ShortsGenerationWorker(self.shorts_engine, video_paths, settings, self.backend_loop)
        self.worker.progress_updated.connect(self.pages["processing"].update_progress)
        self.worker.generation_completed.connect(self._on_generation_completed)
        self.worker.generation_failed.connect(self._on_generation_failed)
        self.worker.start()
        
    def cancel_generation(self):
        if self.worker:
            self.worker.cancel()
        
    def _on_generation_completed(self, result):
        self.pages["processing"].stop_timer()
        self.pages["results"].display_result(result)
        self.navigate_to("results")
        
    def _on_generation_failed(self, error_msg):
        self.pages["processing"].stop_timer()
        self.pages["processing"].update_progress(f"FAILED: {error_msg}", 100)
        
    def _on_log_emitted(self, level, msg):
        self.pages["logs"].append_log(level, msg)

    def handle_reedit(self, entry):
        from pathlib import Path
        import os
        src = Path(entry.source_path)
        if not src.exists():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Missing Source", "The source video for this project is missing. Cannot re-edit.")
            return
            
        # Add it to the media page queue
        self.pages["media"].video_paths.clear()
        self.pages["media"].process_new_files([str(src)])
        self.navigate_to("media")
        
        # In a full implementation, we'd also load the previous settings from the old output folder
        # (e.g. settings.json), but for now we just seed the media queue with the old file.

