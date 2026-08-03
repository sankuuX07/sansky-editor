from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QSpinBox, QComboBox, QDoubleSpinBox, QPushButton
from core.models.shorts_models import OutputSettings

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("Application Settings")
        title.setObjectName("H1")
        
        form_layout = QFormLayout()
        
        self.spin_max_shorts = QSpinBox()
        self.spin_max_shorts.setRange(1, 10)
        self.spin_max_shorts.setValue(3)
        
        self.spin_min_duration = QDoubleSpinBox()
        self.spin_min_duration.setRange(5.0, 30.0)
        self.spin_min_duration.setValue(15.0)
        
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["gaming_bold", "minimal", "dynamic", "tiktok_style"])
        
        form_layout.addRow("Max Shorts per Video:", self.spin_max_shorts)
        form_layout.addRow("Min Clip Duration (sec):", self.spin_min_duration)
        form_layout.addRow("Caption Preset:", self.combo_preset)
        
        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("SecondaryButton")
        
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(btn_save)

    def get_settings(self) -> OutputSettings:
        s = OutputSettings()
        s.max_shorts = self.spin_max_shorts.value()
        s.min_clip_duration = self.spin_min_duration.value()
        s.caption_preset = self.combo_preset.currentText()
        return s
