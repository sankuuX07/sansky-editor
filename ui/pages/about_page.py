from PySide6.QtWidgets import QLabel
from ui.pages.base_page import BasePage

class AboutPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("About", parent)
        lbl = QLabel("Sansky AI Editor - Premium Desktop Experience\nVersion 3.0")
        lbl.setProperty("class", "Subtitle")
        self.content_layout.addWidget(lbl)
