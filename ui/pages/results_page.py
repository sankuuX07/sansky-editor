from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget
from PySide6.QtCore import Signal
import os

class ResultsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("Processing Results")
        title.setObjectName("H1")
        
        self.summary_lbl = QLabel("No results to display.")
        self.summary_lbl.setObjectName("H3")
        
        self.project_list = QListWidget()
        
        btn_open_folder = QPushButton("Open Output Folder")
        btn_open_folder.setObjectName("SecondaryButton")
        btn_open_folder.clicked.connect(self._open_folder)
        
        layout.addWidget(title)
        layout.addWidget(self.summary_lbl)
        layout.addWidget(self.project_list)
        layout.addWidget(btn_open_folder)
        
        self.last_output_dir = None
        
    def display_result(self, processing_result):
        self.project_list.clear()
        
        report = processing_result.report
        if report:
            self.summary_lbl.setText(f"Generated {report.summary.generated_shorts} shorts in {report.summary.total_time_sec:.1f} seconds.")
            
        for proj in processing_result.projects:
            self.project_list.addItem(f"Project: {proj.project_id} | Clips: {len(proj.clips)} | Path: {proj.premiere_project_path}")
            if proj.premiere_project_path:
                self.last_output_dir = str(proj.premiere_project_path.parent)
                
    def _open_folder(self):
        if self.last_output_dir and os.path.exists(self.last_output_dir):
            os.startfile(self.last_output_dir)
