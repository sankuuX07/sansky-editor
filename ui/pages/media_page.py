from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QImage, QIcon
from ui.pages.base_page import BasePage
from ui.controllers.metadata_worker import MetadataWorker
import os

class MediaCard(QFrame):
    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")
        self.filepath = filepath
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(24)
        
        # Thumbnail
        self.thumbnail_lbl = QLabel()
        self.thumbnail_lbl.setFixedSize(240, 135) # 16:9 ratio
        self.thumbnail_lbl.setStyleSheet("background-color: #171A22; border-radius: 8px;")
        self.thumbnail_lbl.setAlignment(Qt.AlignCenter)
        self.thumbnail_lbl.setText("Generating Preview...")
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        self.name_lbl = QLabel(os.path.basename(filepath))
        self.name_lbl.setProperty("class", "Header2")
        self.name_lbl.setWordWrap(True)
        
        # Metadata Grid
        self.meta_layout = QHBoxLayout()
        self.meta_layout.setSpacing(16)
        
        self.res_lbl = self._create_tag("Resolution", "...")
        self.fps_lbl = self._create_tag("FPS", "...")
        self.dur_lbl = self._create_tag("Duration", "...")
        
        self.meta_layout.addWidget(self.res_lbl)
        self.meta_layout.addWidget(self.fps_lbl)
        self.meta_layout.addWidget(self.dur_lbl)
        self.meta_layout.addStretch()
        
        self.est_lbl = QLabel("Estimated Process Time: Calculating...")
        self.est_lbl.setProperty("class", "Subtitle")
        
        info_layout.addWidget(self.name_lbl)
        info_layout.addLayout(self.meta_layout)
        info_layout.addStretch()
        info_layout.addWidget(self.est_lbl)
        
        # Actions
        action_layout = QVBoxLayout()
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setProperty("class", "SecondaryButton")
        action_layout.addWidget(self.remove_btn)
        action_layout.addStretch()
        
        layout.addWidget(self.thumbnail_lbl)
        layout.addLayout(info_layout, 1)
        layout.addLayout(action_layout)
        
    def _create_tag(self, label, value):
        w = QWidget()
        w.setStyleSheet("background-color: #171A22; border-radius: 6px; padding: 4px 8px;")
        l = QHBoxLayout(w)
        l.setContentsMargins(8, 4, 8, 4)
        
        lbl1 = QLabel(f"{label}:")
        lbl1.setStyleSheet("color: #8C96A8; font-size: 12px;")
        
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
        
        l.addWidget(lbl1)
        l.addWidget(self.val_lbl)
        return w

    def _update_tag_val(self, tag_widget, value):
        val_lbl = tag_widget.findChildren(QLabel)[1]
        val_lbl.setText(str(value))

    def set_metadata(self, meta, thumbnail: QImage):
        self._update_tag_val(self.res_lbl, meta['resolution'])
        self._update_tag_val(self.fps_lbl, meta['fps'])
        self._update_tag_val(self.dur_lbl, f"{meta['duration']}s")
        self.est_lbl.setText(f"Estimated Process Time: {meta['estimated_processing_time']}")
        
        if not thumbnail.isNull():
            pix = QPixmap.fromImage(thumbnail)
            self.thumbnail_lbl.setPixmap(pix.scaled(240, 135, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

class MediaPage(BasePage):
    generate_requested = Signal(list, str) # video_paths, output_dir

    def __init__(self, parent=None):
        super().__init__("Media Library", parent)
        
        self.setAcceptDrops(True)
        self.video_paths = []
        self.cards = {}
        self.worker = None
        
        # --- Top Action Bar ---
        top_bar = QHBoxLayout()
        self.add_btn = QPushButton("Add Media")
        self.add_btn.setProperty("class", "SecondaryButton")
        self.add_btn.clicked.connect(self._on_browse_clicked)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setProperty("class", "SecondaryButton")
        self.clear_btn.clicked.connect(self._clear_all)
        
        self.start_btn = QPushButton("Configure & Generate")
        self.start_btn.setProperty("class", "PrimaryButton")
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.start_btn.setEnabled(False)
        
        top_bar.addWidget(self.add_btn)
        top_bar.addWidget(self.clear_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.start_btn)
        
        self.content_layout.addLayout(top_bar)
        
        # --- Scroll Area ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 16, 0, 16)
        self.scroll_layout.setSpacing(16)
        
        # --- Empty State ---
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        empty_icon = QLabel("🎬")
        empty_icon.setStyleSheet("font-size: 64px;")
        empty_icon.setAlignment(Qt.AlignCenter)
        
        empty_title = QLabel("No Media Loaded")
        empty_title.setProperty("class", "Header2")
        empty_title.setAlignment(Qt.AlignCenter)
        
        empty_sub = QLabel("Drag & drop gameplay footage here or click 'Add Media' to begin.")
        empty_sub.setProperty("class", "Subtitle")
        empty_sub.setAlignment(Qt.AlignCenter)
        
        empty_layout.addStretch()
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_sub)
        empty_layout.addStretch()
        
        self.scroll_layout.addWidget(self.empty_widget)
        self.scroll_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        self.content_layout.addWidget(self.scroll)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".mp4", ".mkv", ".mov", ".avi")) and path not in self.video_paths:
                paths.append(path)
        
        if paths:
            self.video_paths.extend(paths)
            self.process_new_files(paths)
            
    def _on_browse_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Videos", "", "Video Files (*.mp4 *.mkv *.mov *.avi)")
        paths = [f for f in files if f not in self.video_paths]
        if paths:
            self.video_paths.extend(paths)
            self.process_new_files(paths)
            
    def process_new_files(self, paths):
        if not paths: return
        
        self.empty_widget.hide()
        self.start_btn.setEnabled(True)
        
        # Remove stretch
        item = self.scroll_layout.takeAt(self.scroll_layout.count() - 1)
        
        for path in paths:
            card = MediaCard(path)
            card.remove_btn.clicked.connect(lambda checked, p=path: self._remove_file(p))
            self.cards[path] = card
            self.scroll_layout.addWidget(card)
            
        self.scroll_layout.addStretch()
        
        self.worker = MetadataWorker(paths)
        self.worker.metadata_ready.connect(self._on_metadata_ready)
        self.worker.start()
        
    def _remove_file(self, path):
        if path in self.video_paths:
            self.video_paths.remove(path)
        if path in self.cards:
            card = self.cards.pop(path)
            card.setParent(None)
            card.deleteLater()
            
        if not self.video_paths:
            self._clear_all()
            
    def _clear_all(self):
        self.video_paths.clear()
        for card in self.cards.values():
            card.setParent(None)
            card.deleteLater()
        self.cards.clear()
        self.empty_widget.show()
        self.start_btn.setEnabled(False)
        
    def _on_metadata_ready(self, path, meta, thumb):
        if path in self.cards:
            self.cards[path].set_metadata(meta, thumb)
            
    def _on_start_clicked(self):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir and self.video_paths:
            self.generate_requested.emit(self.video_paths, output_dir)
            self._clear_all()
