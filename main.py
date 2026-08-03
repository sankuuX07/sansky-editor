import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

import logging
logging.basicConfig(level=logging.INFO)

from ui.main_window import MainWindow
from app.services.backend_service import BackendService

def main():
    # 1. Start the Backend Service thread
    backend = BackendService()
    backend.start()
    
    # Wait for the async loop and managers to initialize safely
    if not backend.wait_until_ready(timeout=10.0):
        logging.error("Backend Service failed to initialize in time. Exiting.")
        sys.exit(1)
        
    # 2. Initialize GUI
    app = QApplication(sys.argv)
    
    style_path = Path(__file__).parent / "ui" / "resources" / "styles" / "style.qss"
    if style_path.exists():
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
            
    # Provide the initialized shorts_generator and the background loop to the GUI
    window = MainWindow(backend.shorts_generator, backend.loop)
    window.show()
    
    exit_code = app.exec()
    
    # 3. Teardown Backend safely
    backend.shutdown()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
