import logging
from PySide6.QtCore import QObject, Signal

class QtLogSignals(QObject):
    log_emitted = Signal(str, str) # levelname, formatted_msg

class QtLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.signals = QtLogSignals()
        
    def emit(self, record):
        try:
            msg = self.format(record)
            self.signals.log_emitted.emit(record.levelname, msg)
        except Exception:
            self.handleError(record)
