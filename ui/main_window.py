from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt

from ui.widgets.sidebar import SidebarWidget
from ui.pages.dashboard_page import DashboardPage
from ui.pages.processing_page import ProcessingPage
from ui.pages.results_page import ResultsPage
from ui.pages.settings_page import SettingsPage
from ui.pages.logs_page import LogsPage
from ui.pages.about_page import AboutPage

from ui.controllers.backend_worker import ShortsGenerationWorker

class MainWindow(QMainWindow):
    def __init__(self, shorts_engine, backend_loop):
        super().__init__()
        self.shorts_engine = shorts_engine
        self.backend_loop = backend_loop
        
        self.setWindowTitle("Sansky AI Editor - Pro")
        self.resize(1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = SidebarWidget()
        self.sidebar.navigation_requested.connect(self.navigate_to)
        
        self.stacked_widget = QStackedWidget()
        
        self.dashboard_page = DashboardPage()
        self.processing_page = ProcessingPage()
        self.results_page = ResultsPage()
        self.settings_page = SettingsPage()
        self.logs_page = LogsPage()
        self.about_page = AboutPage()
        
        self.dashboard_page.generate_requested.connect(self.start_generation)
        
        self.pages = {
            "dashboard": self.dashboard_page,
            "processing": self.processing_page,
            "results": self.results_page,
            "settings": self.settings_page,
            "logs": self.logs_page,
            "about": self.about_page
        }
        
        for p in self.pages.values():
            self.stacked_widget.addWidget(p)
            
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stacked_widget)
        
        self.worker = None

    def navigate_to(self, page_id: str):
        if page_id in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_id])
            self.sidebar.set_active(page_id)
            
    def start_generation(self, video_paths, output_dir):
        settings = self.settings_page.get_settings()
        settings.output_directory = output_dir
        
        self.navigate_to("processing")
        self.processing_page.status_lbl.setText("Initializing worker...")
        
        self.worker = ShortsGenerationWorker(self.shorts_engine, video_paths, settings, self.backend_loop)
        self.worker.progress_updated.connect(self.processing_page.update_progress)
        self.worker.generation_completed.connect(self._on_generation_completed)
        self.worker.generation_failed.connect(self._on_generation_failed)
        self.worker.start()
        
    def _on_generation_completed(self, result):
        self.results_page.display_result(result)
        self.navigate_to("results")
        
    def _on_generation_failed(self, error_msg):
        self.processing_page.update_progress(f"FAILED: {error_msg}", 100)
