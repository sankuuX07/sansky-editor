from PySide6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QWidget
from ui.pages.base_page import BasePage

class DashboardPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("Dashboard", parent)
        
        welcome_lbl = QLabel("Welcome back to Sansky AI Editor Pro.")
        welcome_lbl.setProperty("class", "Subtitle")
        self.content_layout.addWidget(welcome_lbl)
        
        card = QWidget()
        card.setProperty("class", "Card")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        
        self.start_btn = QPushButton("New Project")
        self.start_btn.setProperty("class", "PrimaryButton")
        
        settings_btn = QPushButton("Quick Settings")
        settings_btn.setProperty("class", "SecondaryButton")
        
        card_layout.addWidget(self.start_btn)
        card_layout.addWidget(settings_btn)
        card_layout.addStretch()
        
        self.content_layout.addWidget(card)
