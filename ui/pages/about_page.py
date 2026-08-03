from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("About Sansky AI Editor")
        title.setObjectName("H1")
        
        info = QLabel(
            "Version 1.0.0\n\n"
            "A professional desktop application for automating gameplay highlights and YouTube Shorts creation.\n"
            "Powered by PySide6, asyncio, and custom AI orchestration engines.\n\n"
            "© 2026 Sansky Software"
        )
        info.setObjectName("H3")
        info.setWordWrap(True)
        
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
