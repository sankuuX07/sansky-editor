from PySide6.QtWidgets import QLabel, QLineEdit, QFormLayout, QVBoxLayout, QWidget, QComboBox, QCheckBox, QSpinBox, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal
from ui.pages.base_page import BasePage
from core.models.shorts_models import OutputSettings
from core.config.config_manager import ConfigManager, AppConfig

class SettingsPage(BasePage):
    settings_saved = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.config_manager = ConfigManager()
        self.config_manager.load()
        
        card = QWidget()
        card.setProperty("class", "Card")
        form_layout = QFormLayout(card)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)
        
        self.whisper_input = QComboBox()
        self.whisper_input.addItems(["tiny", "base", "small", "medium", "large"])
        
        self.ffmpeg_input = QLineEdit()
        self.premiere_input = QLineEdit()
        self.output_input = QLineEdit()
        self.cache_input = QLineEdit()
        
        self.theme_input = QComboBox()
        self.theme_input.addItems(["Dark", "Light", "System"])
        
        self.performance_input = QComboBox()
        self.performance_input.addItems(["Fastest", "Balanced", "Highest Quality"])
        
        self.gpu_input = QCheckBox("Enable GPU Acceleration")
        
        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 32)
        
        self.autosave_input = QCheckBox("Enable Autosave")
        
        form_layout.addRow("Whisper Model:", self.whisper_input)
        form_layout.addRow("FFmpeg Path:", self.ffmpeg_input)
        form_layout.addRow("Premiere Path:", self.premiere_input)
        form_layout.addRow("Output Folder:", self.output_input)
        form_layout.addRow("Cache Folder:", self.cache_input)
        form_layout.addRow("Theme:", self.theme_input)
        form_layout.addRow("Performance:", self.performance_input)
        form_layout.addRow("Threads:", self.threads_input)
        form_layout.addRow("", self.gpu_input)
        form_layout.addRow("", self.autosave_input)
        
        self.content_layout.addWidget(card)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("Save Settings")
        save_btn.setProperty("class", "PrimaryButton")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        self.content_layout.addLayout(btn_layout)
        
        self.load_settings()
        
    def load_settings(self):
        config = self.config_manager.get()
        self.whisper_input.setCurrentText(config.whisper_model_size)
        self.ffmpeg_input.setText(config.ffmpeg_path or "")
        self.premiere_input.setText(config.premiere_path or "")
        self.output_input.setText(config.output_dir)
        self.cache_input.setText(config.cache_dir)
        self.theme_input.setCurrentText(config.theme)
        self.performance_input.setCurrentText(config.performance_preset)
        self.gpu_input.setChecked(config.use_gpu)
        self.threads_input.setValue(config.threads)
        self.autosave_input.setChecked(config.autosave)

    def save_settings(self):
        # Create a new config dict and instantiate AppConfig
        data = {
            "whisper_model_size": self.whisper_input.currentText(),
            "ffmpeg_path": self.ffmpeg_input.text() or None,
            "premiere_path": self.premiere_input.text() or None,
            "output_dir": self.output_input.text(),
            "cache_dir": self.cache_input.text(),
            "theme": self.theme_input.currentText(),
            "performance_preset": self.performance_input.currentText(),
            "use_gpu": self.gpu_input.isChecked(),
            "threads": self.threads_input.value(),
            "autosave": self.autosave_input.isChecked(),
            "log_level": self.config_manager.get().log_level,
            "data_dir": self.config_manager.get().data_dir
        }
        
        self.config_manager.config = AppConfig(**data)
        self.config_manager.save()
        self.settings_saved.emit()

    def get_settings(self):
        # Returns OutputSettings for the generation worker based on current UI state
        settings = OutputSettings()
        settings.output_directory = self.output_input.text()
        return settings
