from PySide6.QtWidgets import QLabel, QTextEdit
from ui.pages.base_page import BasePage

class LogsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("System Logs", parent)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.content_layout.addWidget(self.log_viewer)
