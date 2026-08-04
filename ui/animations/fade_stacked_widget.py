from PySide6.QtWidgets import QStackedWidget, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup

class FadeStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fade_duration = 200

    def setCurrentWidget(self, widget: QWidget):
        if self.currentWidget() == widget:
            return

        old_widget = self.currentWidget()
        new_widget = widget

        super().setCurrentWidget(new_widget)

        # Apply graphics effects for fade in
        effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(self.fade_duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.finished.connect(lambda: new_widget.setGraphicsEffect(None))
        anim.start()
        
        # Keep a reference so it doesn't get garbage collected immediately
        self._anim = anim
