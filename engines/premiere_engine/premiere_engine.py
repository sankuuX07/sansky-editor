"""
The Premiere Engine facade.
"""
import logging
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError

from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from engines.premiere_engine.bridge.installation_manager import PremiereInstallationManager
from engines.premiere_engine.managers.project_manager import ProjectManager
from engines.premiere_engine.managers.sequence_manager import SequenceManager
from engines.premiere_engine.managers.preset_manager import PresetManager
from engines.premiere_engine.managers.export_queue_manager import ExportQueueManager
from engines.premiere_engine.services.media_import_service import MediaImportService
from engines.premiere_engine.services.timeline_builder import TimelineBuilder
from engines.premiere_engine.services.caption_import_service import CaptionImportService

class PremiereEngine(BaseEngine):
    """Facade for the Adobe Premiere Pro Automation subsystem."""
    
    def __init__(self) -> None:
        super().__init__("premiere_engine")
        
        self.bridge = PremiereBridge()
        self.installation_manager = PremiereInstallationManager()
        
        self.project_manager = ProjectManager(self.bridge)
        self.sequence_manager = SequenceManager(self.bridge)
        self.preset_manager = PresetManager()
        self.export_manager = ExportQueueManager(self.bridge)
        
        self.media_importer = MediaImportService(self.bridge)
        self.timeline_builder = TimelineBuilder(self.bridge)
        self.caption_importer = CaptionImportService(self.bridge)

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Premiere Engine...")
        try:
            exe_path = self.installation_manager.detect_installation()
            self.installation_manager.validate_compatibility(exe_path)
            
            self._status = EngineStatus.INITIALIZED
            self.is_initialized = True
            self.logger.info("Premiere Engine initialized successfully.")
        except Exception as e:
            self._status = EngineStatus.ERROR
            raise EngineInitError("Failed to initialize PremiereEngine") from e

    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized PremiereEngine")
            
        self.bridge.connect()
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Premiere Engine started and connected to Adobe IPC.")

    def stop(self) -> None:
        self.bridge.disconnect()
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Premiere Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Premiere Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING and self.bridge.is_connected
