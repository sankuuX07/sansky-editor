from PySide6.QtWidgets import QLabel
from ui.pages.base_page import BasePage

class ResultsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Generated Shorts", parent)
        lbl = QLabel("Your generated content will appear here.")
        lbl.setProperty("class", "Subtitle")
        self.content_layout.addWidget(lbl)
        
    def display_result(self, result):
        pass # To be implemented
