from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtCore import Signal, Qt
from ui.pages.base_page import BasePage

class MediaPage(BasePage):
    generate_requested = Signal(list, str) # video_paths, output_dir

    def __init__(self, parent=None):
        super().__init__("Media Library", parent)
        
        self.setAcceptDrops(True)
        self.video_paths = []
        
        self.drop_area = QWidget()
        self.drop_area.setProperty("class", "Card")
        drop_layout = QVBoxLayout(self.drop_area)
        
        self.lbl = QLabel("Drag & Drop your video files here\nor Click to Browse")
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setProperty("class", "Subtitle")
        drop_layout.addWidget(self.lbl)
        
        self.content_layout.addWidget(self.drop_area)
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.setProperty("class", "PrimaryButton")
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.start_btn.setEnabled(False)
        self.content_layout.addWidget(self.start_btn)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".mp4"):
                self.video_paths.append(path)
        self.update_ui()
        
    def mousePressEvent(self, event):
        if self.drop_area.geometry().contains(event.pos()):
            files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", "Video Files (*.mp4 *.avi *.mkv)")
            if files:
                self.video_paths.extend(files)
                self.update_ui()
                
    def update_ui(self):
        if self.video_paths:
            self.lbl.setText(f"{len(self.video_paths)} file(s) selected.\n" + "\n".join(self.video_paths[:3]))
            self.start_btn.setEnabled(True)
            
    def _on_start_clicked(self):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir and self.video_paths:
            self.generate_requested.emit(self.video_paths, output_dir)
            self.video_paths = []
            self.update_ui()
