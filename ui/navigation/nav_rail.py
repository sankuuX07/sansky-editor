from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

class NavRail(QWidget):
    navigation_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavRail")
        self.setFixedWidth(220)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 16, 0, 16)
        self.layout.setSpacing(4)

        self.buttons = {}

        # Top section
        self.add_nav_item("dashboard", "🏠 Dashboard")
        self.add_nav_item("media", "📁 Media")
        self.add_nav_item("processing", "⚙️ Processing")
        self.add_nav_item("results", "✨ Results")

        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Bottom section
        self.add_nav_item("settings", "🔧 Settings")
        self.add_nav_item("logs", "📜 Logs")
        self.add_nav_item("about", "ℹ️ About")

    def add_nav_item(self, page_id: str, label: str):
        btn = QPushButton(label)
        btn.setObjectName(f"NavBtn_{page_id}")
        btn.setProperty("class", "NavButton")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self._on_nav_clicked(page_id))
        self.layout.addWidget(btn)
        self.buttons[page_id] = btn

    def _on_nav_clicked(self, page_id: str):
        self.set_active(page_id)
        self.navigation_requested.emit(page_id)

    def set_active(self, page_id: str):
        for pid, btn in self.buttons.items():
            btn.setChecked(pid == page_id)
