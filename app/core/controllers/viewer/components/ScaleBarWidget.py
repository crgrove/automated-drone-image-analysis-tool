from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtCore import Qt


class ScaleBarWidget(QWidget):
    """
    Draws a *fixed‑width* scale bar (default 120 px) and a text label that you
    can change at runtime with setLabel().
    """

    def __init__(self, parent=None, bar_px=120):
        super().__init__(parent)
        self._bar_px = bar_px
        self._label_text = ""
        self.setFixedSize(bar_px + 80, 30)          # +80 leaves room for text

    # ---------- public API ----------
    def setLabel(self, text: str):
        if text != self._label_text:
            self._label_text = text
            self.update()        # trigger paintEvent

    # ---------- paint ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.white, 2)
        painter.setPen(pen)

        mid_y = self.height() // 2
        start = 10                       # left margin
        end = start + self._bar_px

        # bar + end caps
        painter.drawLine(start, mid_y, end, mid_y)
        painter.drawLine(start, mid_y - 5, start, mid_y + 5)
        painter.drawLine(end,   mid_y - 5, end,   mid_y + 5)

        # label
        painter.setFont(QFont("Arial", 10))
        painter.drawText(end + 8, mid_y + 4, self._label_text)
