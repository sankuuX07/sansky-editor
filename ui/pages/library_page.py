from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from ui.pages.base_page import BasePage
from ui.widgets.library_project_card import LibraryProjectCard
from ui.widgets.library_details_dialog import LibraryDetailsDialog
from engines.library_engine.library_engine import LibraryEngine

class FlowLayout(QVBoxLayout):
    # A simple vertical layout for cards
    pass

class LibraryPage(BasePage):
    reedit_requested = Signal(object) # pass the entry
    publish_requested = Signal(object) # pass the entry
    
    def __init__(self, parent=None):
        super().__init__("Content Library", parent)
        self.lib_engine = LibraryEngine()
        
        # Top Bar (Search + Filter)
        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search projects, files, or tags...")
        self.search_input.textChanged.connect(self._on_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #171A22;
                border: 1px solid #2A2D35;
                border-radius: 8px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #3498DB; }
        """)
        
        self.filter_btn = QPushButton("All")
        self.filter_btn.setProperty("class", "SecondaryButton")
        self.filter_btn.clicked.connect(self._toggle_filter)
        self.current_filter = "All"
        
        top_bar.addWidget(self.search_input, 1)
        top_bar.addWidget(self.filter_btn)
        
        self.content_layout.addLayout(top_bar)
        
        # Main Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.grid_widget = QWidget()
        self.grid_layout = QVBoxLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignTop)
        self.grid_layout.setSpacing(12)
        
        self.scroll.setWidget(self.grid_widget)
        self.content_layout.addWidget(self.scroll, 1)
        
        self.refresh()
        
    def _toggle_filter(self):
        filters = ["All", "Favorites", "Archived", "Failed"]
        idx = filters.index(self.current_filter)
        self.current_filter = filters[(idx + 1) % len(filters)]
        self.filter_btn.setText(self.current_filter)
        self.refresh()
        
    def _on_search(self, text):
        self.refresh()
        
    def refresh(self):
        # Clear
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
                
        query = self.search_input.text().strip()
        if query:
            entries = self.lib_engine.search(query)
        else:
            entries = self.lib_engine.get_all()
            
        # Apply filter
        filtered = []
        for e in entries:
            if self.current_filter == "Favorites" and not e.favorite: continue
            if self.current_filter == "Archived" and not e.archived: continue
            if self.current_filter == "Failed" and "FAILED" not in e.status: continue
            if self.current_filter != "Archived" and e.archived: continue # Hide archived by default
            
            filtered.append(e)
            
        if not filtered:
            lbl = QLabel("No projects found.")
            lbl.setStyleSheet("color: #8C96A8; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(lbl)
            return
            
        for e in filtered:
            card = LibraryProjectCard(e)
            card.clicked.connect(self._on_card_clicked)
            self.grid_layout.addWidget(card)
            
    def _on_card_clicked(self, entry):
        dialog = LibraryDetailsDialog(entry, self.lib_engine, self)
        dialog.action_requested.connect(self._handle_dialog_action)
        dialog.exec()
        
    def _handle_dialog_action(self, action, entry):
        if action == "refresh":
            self.refresh()
        elif action == "reedit":
            self.reedit_requested.emit(entry)
        elif action == "publish":
            self.publish_requested.emit(entry)
