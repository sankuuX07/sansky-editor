from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QComboBox
from PySide6.QtGui import QTextCursor, QColor
from ui.pages.base_page import BasePage
import logging

class LogsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("System Logs", parent)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search logs...")
        self.search_input.textChanged.connect(self.filter_logs)
        
        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self.filter_logs)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setProperty("class", "SecondaryButton")
        self.clear_btn.clicked.connect(self.clear_logs)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setProperty("class", "PrimaryButton")
        self.export_btn.clicked.connect(self.export_logs)
        
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.level_filter)
        toolbar.addStretch()
        toolbar.addWidget(self.clear_btn)
        toolbar.addWidget(self.export_btn)
        self.content_layout.addLayout(toolbar)
        
        # Viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setProperty("class", "Card")
        self.log_viewer.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        self.content_layout.addWidget(self.log_viewer)
        
        self._all_logs = []
        
    def append_log(self, level, msg):
        self._all_logs.append((level, msg))
        
        if self._should_show(level, msg):
            self._render_log(level, msg)
            
    def _should_show(self, level, msg):
        current_filter = self.level_filter.currentText()
        if current_filter != "ALL":
            levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            try:
                if levels.index(level) < levels.index(current_filter):
                    return False
            except ValueError:
                pass
                
        search = self.search_input.text().lower()
        if search and search not in msg.lower():
            return False
            
        return True
        
    def _render_log(self, level, msg):
        color = "#E0E0E0"
        if level == "DEBUG": color = "#8A8A8A"
        elif level == "WARNING": color = "#FFA500"
        elif level == "ERROR" or level == "CRITICAL": color = "#FF4500"
        
        self.log_viewer.append(f'<span style="color:{color};">{msg}</span>')
        # Auto-scroll
        cursor = self.log_viewer.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_viewer.setTextCursor(cursor)
        
    def filter_logs(self):
        self.log_viewer.clear()
        for lvl, msg in self._all_logs:
            if self._should_show(lvl, msg):
                self._render_log(lvl, msg)
                
    def clear_logs(self):
        self._all_logs.clear()
        self.log_viewer.clear()
        
    def export_logs(self):
        pass # To be implemented if needed
