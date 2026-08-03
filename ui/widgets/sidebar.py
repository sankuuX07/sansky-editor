from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Signal, Qt

class SidebarWidget(QWidget):
    navigation_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(250)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 20, 0, 20)
        self.layout.setSpacing(5)
        
        self.buttons = {}
        
        self.add_nav_button("Dashboard", "dashboard")
        self.add_nav_button("Processing", "processing")
        self.add_nav_button("Results", "results")
        self.add_nav_button("Settings", "settings")
        self.add_nav_button("Logs", "logs")
        
        self.layout.addStretch()
        
        self.add_nav_button("About", "about")
        
        self.set_active("dashboard")

    def add_nav_button(self, text, page_id):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self._on_button_clicked(page_id))
        self.layout.addWidget(btn)
        self.buttons[page_id] = btn

    def _on_button_clicked(self, page_id):
        self.set_active(page_id)
        self.navigation_requested.emit(page_id)
        
    def set_active(self, page_id):
        for pid, btn in self.buttons.items():
            btn.setChecked(pid == page_id)
