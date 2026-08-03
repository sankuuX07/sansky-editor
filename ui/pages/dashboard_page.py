from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import Signal
from pathlib import Path

class DashboardPage(QWidget):
    generate_requested = Signal(list, str) # video_paths, output_dir

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("Dashboard")
        title.setObjectName("H1")
        layout.addWidget(title)
        
        self.video_paths = []
        self.output_dir = str(Path.home() / "Videos" / "SanskyOutputs")
        
        # Select Video
        self.lbl_video = QLabel("No video selected")
        btn_select_video = QPushButton("Select Gameplay Video")
        btn_select_video.setObjectName("SecondaryButton")
        btn_select_video.clicked.connect(self._select_video)
        
        # Select Output
        self.lbl_output = QLabel(f"Output: {self.output_dir}")
        btn_select_output = QPushButton("Select Output Folder")
        btn_select_output.setObjectName("SecondaryButton")
        btn_select_output.clicked.connect(self._select_output)
        
        # Generate Button
        btn_generate = QPushButton("Generate Shorts")
        btn_generate.setFixedHeight(50)
        btn_generate.clicked.connect(self._on_generate)
        
        layout.addSpacing(20)
        layout.addWidget(btn_select_video)
        layout.addWidget(self.lbl_video)
        
        layout.addSpacing(20)
        layout.addWidget(btn_select_output)
        layout.addWidget(self.lbl_output)
        
        layout.addStretch()
        layout.addWidget(btn_generate)
        
    def _select_video(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", "Video Files (*.mp4 *.mkv *.mov)")
        if files:
            self.video_paths = [Path(p) for p in files]
            self.lbl_video.setText(f"{len(files)} video(s) selected")
            
    def _select_output(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_dir)
        if dir:
            self.output_dir = dir
            self.lbl_output.setText(f"Output: {self.output_dir}")
            
    def _on_generate(self):
        if self.video_paths:
            self.generate_requested.emit(self.video_paths, self.output_dir)
