from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QListWidget
from ui.pages.base_page import BasePage

class ProcessingPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Processing Workflow", parent)
        
        card = QWidget()
        card.setProperty("class", "Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        self.status_lbl = QLabel("Idle")
        self.status_lbl.setProperty("class", "Header2")
        card_layout.addWidget(self.status_lbl)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        card_layout.addWidget(self.progress_bar)
        
        self.timeline_list = QListWidget()
        self.timeline_list.setProperty("class", "Timeline")
        self.timeline_list.setStyleSheet("background: transparent; border: none;")
        self.timeline_list.setSelectionMode(QListWidget.NoSelection)
        card_layout.addWidget(self.timeline_list)
        
        self.content_layout.addWidget(card)
        
    def update_progress(self, msg, pct):
        self.status_lbl.setText(f"Task: {msg}")
        self.progress_bar.setValue(pct)
        if pct < 100 and msg != "Idle":
            self.timeline_list.addItem(f"• {msg} ({pct}%)")
            self.timeline_list.scrollToBottom()
