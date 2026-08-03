from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QTextEdit

class ProcessingPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("Processing Workflow")
        title.setObjectName("H1")
        
        self.status_lbl = QLabel("Awaiting tasks...")
        self.status_lbl.setObjectName("H2")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(30)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #121212; border: 1px solid #333; font-family: Consolas, monospace;")
        
        layout.addWidget(title)
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_view)
        
    def update_progress(self, message: str, percentage: int):
        self.status_lbl.setText(message)
        self.progress_bar.setValue(percentage)
        self.log_view.append(f"> {message}")
