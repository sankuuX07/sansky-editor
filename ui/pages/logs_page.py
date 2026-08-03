from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton

class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("System Logs")
        title.setObjectName("H1")
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #121212; border: 1px solid #333; font-family: Consolas, monospace;")
        
        btn_clear = QPushButton("Clear Logs")
        btn_clear.setObjectName("SecondaryButton")
        btn_clear.clicked.connect(self.log_view.clear)
        
        layout.addWidget(title)
        layout.addWidget(self.log_view)
        layout.addWidget(btn_clear)
