import sys
import os
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QCoreApplication
import logging

logging.basicConfig(level=logging.DEBUG)

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from app.services.backend_service import BackendService
from ui.main_window.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Initialize backend
    backend = BackendService()
    backend.start()
    
    print("Waiting for backend to be ready...")
    if not backend.wait_until_ready(timeout=20.0):
        print("Backend failed to start")
        sys.exit(1)
        
    print("Backend ready. Initializing UI...")
    
    main_window = MainWindow(backend.shorts_generator, backend.loop, backend.engine_manager)
    # Don't show to avoid display issues in headless environment, just test logic
    
    # Setup test video
    video_path = Path("test_assets/dummy_gameplay.mp4").absolute()
    if not video_path.exists():
        print(f"Error: {video_path} not found")
        backend.shutdown()
        sys.exit(1)
        
    # Simulate adding file to media page
    media_page = main_window.pages["media"]
    media_page.video_paths.append(str(video_path))
    media_page.process_new_files([str(video_path)])
    
    output_dir = str(Path("data/test_output").absolute())
    
    # Patch QFileDialog to automatically return our output_dir without blocking
    with patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory", return_value=output_dir):
        print("Simulating 'Configure & Generate' click...")
        # Since start_btn is enabled by process_new_files, we can click it
        media_page.start_btn.setEnabled(True)
        media_page.start_btn.click()
        
    # Now we need to wait for the worker to finish
    print("Worker started. Processing events until Results page is active...")
    
    def check_status():
        current_page = main_window.stacked_widget.currentWidget()
        if current_page == main_window.pages["results"]:
            print("Successfully reached Results page!")
            # Verify output files
            if list(Path(output_dir).glob("*.mp4")) or list(Path(output_dir).glob("*.xml")):
                print("Real output files verified!")
            else:
                print("Error: Reached results but no real output files found.")
            backend.shutdown()
            app.quit()
        elif current_page == main_window.pages["processing"]:
            progress = main_window.pages["processing"].progress_bar.value()
            status = main_window.pages["processing"].status_lbl.text()
            print(f"Processing... {progress}%: {status}")
            if "FAILED" in status:
                print(f"Failed! Status: {status}")
                backend.shutdown()
                app.quit()
        else:
            print(f"Current page: {current_page.__class__.__name__}")
            
    timer = QTimer()
    timer.timeout.connect(check_status)
    timer.start(2000)
    
    app.exec()
    
if __name__ == "__main__":
    main()
