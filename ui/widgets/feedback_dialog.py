from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QSlider, QWidget)
from PySide6.QtCore import Qt
from core.models.preference_models import FeedbackRecord

class FeedbackDialog(QDialog):
    def __init__(self, clip_id: str, job_id: str, parent=None):
        super().__init__(parent)
        self.clip_id = clip_id
        self.job_id = job_id
        
        self.setWindowTitle(f"Provide Feedback for {clip_id}")
        self.setMinimumWidth(400)
        self.setStyleSheet("background-color: #0D1017; color: #FFFFFF; font-family: 'Inter', sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("How was this clip?")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Overall Rating
        rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel("Overall Rating:"))
        self.rating_combo = QComboBox()
        self.rating_combo.addItems(["5 - Excellent", "4 - Good", "3 - Okay", "2 - Needs Work", "1 - Poor"])
        self.rating_combo.setStyleSheet("background-color: #1A1D24; padding: 4px; border-radius: 4px;")
        rating_layout.addWidget(self.rating_combo)
        layout.addLayout(rating_layout)
        
        # Specific Feedback Dropdowns
        self.editing_combo = self._create_feedback_row(layout, "Editing:", 
            ["Looks good", "Too much zoom", "Not enough zoom", "Too much shake", "Good slow motion", "Too many effects", "Too simple"])
            
        self.caption_combo = self._create_feedback_row(layout, "Captions:", 
            ["Looks good", "Too many captions", "More captions", "Timing is off"])
            
        self.audio_combo = self._create_feedback_row(layout, "Audio:", 
            ["Sounds good", "Gameplay too loud", "Voice too quiet"])
            
        self.thumbnail_combo = self._create_feedback_row(layout, "Thumbnail:", 
            ["Looks good", "Too much enhancement", "Wrong moment"])
            
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("padding: 8px 16px; background-color: #1A1D24; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        
        submit_btn = QPushButton("Submit Feedback")
        submit_btn.setStyleSheet("padding: 8px 16px; background-color: #2ECC71; color: #000000; border-radius: 4px; font-weight: bold;")
        submit_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        
        layout.addLayout(btn_layout)
        
    def _create_feedback_row(self, layout, label_text, options):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setFixedWidth(100)
        row.addWidget(lbl)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setStyleSheet("background-color: #1A1D24; padding: 4px; border-radius: 4px;")
        row.addWidget(combo)
        
        layout.addLayout(row)
        return combo
        
    def get_feedback_record(self) -> FeedbackRecord:
        record = FeedbackRecord(job_id=self.job_id, clip_id=self.clip_id)
        
        # Parse rating (e.g. "5 - Excellent" -> 5)
        rating_str = self.rating_combo.currentText()
        record.overall_rating = int(rating_str.split(" - ")[0])
        
        e_fb = self.editing_combo.currentText()
        if e_fb != "Looks good": record.editing_feedback = e_fb
            
        c_fb = self.caption_combo.currentText()
        if c_fb != "Looks good": record.caption_feedback = c_fb
            
        a_fb = self.audio_combo.currentText()
        if a_fb != "Sounds good": record.audio_feedback = a_fb
            
        t_fb = self.thumbnail_combo.currentText()
        if t_fb != "Looks good": record.thumbnail_feedback = t_fb
            
        return record
