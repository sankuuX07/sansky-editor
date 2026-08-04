from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QPainter, QPen, QColor
from ui.pages.base_page import BasePage

class PipelineNode(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 100)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.circle = QLabel()
        self.circle.setFixedSize(32, 32)
        self.circle.setStyleSheet("background-color: #2D3344; border-radius: 16px; border: 2px solid #444E66;")
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: #8C96A8; font-weight: 600; font-size: 13px;")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        
        self.status_lbl = QLabel("Pending")
        self.status_lbl.setStyleSheet("color: #556075; font-size: 11px;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.circle, 0, Qt.AlignCenter)
        layout.addWidget(self.title_lbl, 0, Qt.AlignCenter)
        layout.addWidget(self.status_lbl, 0, Qt.AlignCenter)
        
    def set_active(self, pct):
        self.circle.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0052D4, stop:1 #4364F7); 
            border-radius: 16px; 
            border: 2px solid #FFFFFF;
        """)
        self.title_lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
        self.status_lbl.setText(f"Running... {pct}%")
        self.status_lbl.setStyleSheet("color: #4364F7; font-size: 11px;")
        
    def set_completed(self):
        self.circle.setStyleSheet("background-color: #2ECC71; border-radius: 16px;")
        self.title_lbl.setStyleSheet("color: #2ECC71; font-weight: bold; font-size: 13px;")
        self.status_lbl.setText("Completed")
        self.status_lbl.setStyleSheet("color: #2ECC71; font-size: 11px;")
        
    def set_pending(self):
        self.circle.setStyleSheet("background-color: #2D3344; border-radius: 16px; border: 2px solid #444E66;")
        self.title_lbl.setStyleSheet("color: #8C96A8; font-weight: 600; font-size: 13px;")
        self.status_lbl.setText("Pending")
        self.status_lbl.setStyleSheet("color: #556075; font-size: 11px;")

class PipelineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.stages = ["Analysis", "Whisper", "Captions", "Highlights", "Assembly"]
        self.nodes = {}
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addStretch()
        for i, stage in enumerate(self.stages):
            node = PipelineNode(stage)
            self.nodes[stage] = node
            layout.addWidget(node)
            
            if i < len(self.stages) - 1:
                line = QFrame()
                line.setFixedSize(60, 2)
                line.setStyleSheet("background-color: #2D3344; margin-bottom: 24px;")
                layout.addWidget(line)
                
        layout.addStretch()
        
    def reset(self):
        for node in self.nodes.values():
            node.set_pending()
            
    def update_progress(self, msg, pct):
        msg_lower = msg.lower()
        active_stage = None
        
        if "analy" in msg_lower or "metadata" in msg_lower: active_stage = "Analysis"
        elif "transcrib" in msg_lower or "whisper" in msg_lower: active_stage = "Whisper"
        elif "caption" in msg_lower: active_stage = "Captions"
        elif "highlight" in msg_lower or "score" in msg_lower: active_stage = "Highlights"
        elif "assembl" in msg_lower or "premiere" in msg_lower: active_stage = "Assembly"
        
        if active_stage:
            # Mark previous as completed
            idx = self.stages.index(active_stage)
            for i in range(idx):
                self.nodes[self.stages[i]].set_completed()
                
            self.nodes[active_stage].set_active(pct)

class ProcessingPage(BasePage):
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Workflow Processing", parent)
        
        # --- Top Status Area ---
        top_layout = QHBoxLayout()
        self.status_lbl = QLabel("Initializing Workflow...")
        self.status_lbl.setProperty("class", "Header2")
        
        self.elapsed_lbl = QLabel("00:00")
        self.elapsed_lbl.setProperty("class", "Header3")
        self.elapsed_lbl.setStyleSheet("color: #4364F7;")
        
        top_layout.addWidget(self.status_lbl)
        top_layout.addStretch()
        top_layout.addWidget(self.elapsed_lbl)
        
        self.content_layout.addLayout(top_layout)
        
        # --- Pipeline Card ---
        pipe_card = QWidget()
        pipe_card.setProperty("class", "Card")
        pipe_layout = QVBoxLayout(pipe_card)
        pipe_layout.setContentsMargins(24, 32, 24, 32)
        
        self.pipeline = PipelineWidget()
        pipe_layout.addWidget(self.pipeline)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setFixedHeight(8)
        self.overall_progress.setTextVisible(False)
        pipe_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        pipe_layout.addWidget(self.overall_progress)
        
        self.content_layout.addWidget(pipe_card)
        
        self.content_layout.addStretch()
        
        # --- Actions ---
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel Generation")
        self.cancel_btn.setProperty("class", "DangerButton")
        self.cancel_btn.setFixedWidth(200)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        
        self.content_layout.addLayout(btn_layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.elapsed_seconds = 0
        
    def start_timer(self):
        self.elapsed_seconds = 0
        self.timer.start(1000)
        self.cancel_btn.setEnabled(True)
        self.pipeline.reset()
        self.overall_progress.setValue(0)
        
    def stop_timer(self):
        self.timer.stop()
        self.cancel_btn.setEnabled(False)
        
    def _update_timer(self):
        self.elapsed_seconds += 1
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        self.elapsed_lbl.setText(f"{mins:02d}:{secs:02d}")
        
    def _on_cancel_clicked(self):
        self.cancel_btn.setEnabled(False)
        self.cancel_requested.emit()
        
    def update_progress(self, msg, pct):
        self.status_lbl.setText(msg)
        self.overall_progress.setValue(pct)
        self.pipeline.update_progress(msg, pct)
