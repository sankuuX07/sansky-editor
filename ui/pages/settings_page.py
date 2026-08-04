from PySide6.QtWidgets import QLabel, QLineEdit, QFormLayout, QWidget
from ui.pages.base_page import BasePage
from core.models.shorts_models import OutputSettings

class SettingsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        
        card = QWidget()
        card.setProperty("class", "Card")
        form_layout = QFormLayout(card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)
        
        self.font_input = QLineEdit("Arial")
        self.size_input = QLineEdit("60")
        self.color_input = QLineEdit("yellow")
        
        form_layout.addRow("Caption Font:", self.font_input)
        form_layout.addRow("Caption Size:", self.size_input)
        form_layout.addRow("Caption Color:", self.color_input)
        
        self.content_layout.addWidget(card)
        
    def get_settings(self):
        settings = OutputSettings()
        settings.font = self.font_input.text()
        settings.font_size = int(self.size_input.text())
        settings.color = self.color_input.text()
        return settings
