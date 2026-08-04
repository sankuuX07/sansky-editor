from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QFormLayout
from PySide6.QtCore import Qt
from ui.pages.base_page import BasePage

class AboutPage(BasePage):
    def __init__(self, parent=None):
        super().__init__("About Sansky AI Editor", parent)
        
        card = QWidget()
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        
        title = QLabel("Sansky AI Editor - Premium Desktop Experience")
        title.setProperty("class", "Header2")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Automated short-form content generation powered by AI.")
        subtitle.setProperty("class", "Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        form_layout = QFormLayout()
        form_layout.setContentsMargins(40, 40, 40, 0)
        
        form_layout.addRow("Version:", QLabel("3.0.0 (Production)"))
        form_layout.addRow("Build:", QLabel("2026-08-04"))
        form_layout.addRow("Framework:", QLabel("PySide6 / asyncio"))
        form_layout.addRow("License:", QLabel("Proprietary Commercial License"))
        form_layout.addRow("Repository:", QLabel("<a href='https://github.com/sankuuX07/sansky-editor' style='color:#0078D4;'>github.com/sankuuX07/sansky-editor</a>"))
        
        # Enable link clicking
        for i in range(form_layout.rowCount()):
            widget = form_layout.itemAt(i, QFormLayout.FieldRole).widget()
            if isinstance(widget, QLabel):
                widget.setOpenExternalLinks(True)
                widget.setProperty("class", "Subtitle")
                
        layout.addLayout(form_layout)
        
        self.content_layout.addWidget(card)
