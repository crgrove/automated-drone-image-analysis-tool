"""
Color Gradient Widget

A widget that displays a horizontal gradient showing min, mid, and max colors
for a color range configuration.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QLinearGradient, QColor
from PySide6.QtWidgets import QWidget


class ColorGradientWidget(QWidget):
    """Widget that displays a horizontal gradient from min to mid to max color."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_color = QColor(0, 0, 0)
        self.mid_color = QColor(128, 128, 128)
        self.max_color = QColor(255, 255, 255)
        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        # Allow the gradient to shrink so the delete button is always visible
        self.setMinimumWidth(0)

    def set_colors(self, min_color, mid_color, max_color):
        """
        Set the three colors for the gradient.

        Args:
            min_color: QColor or tuple (r, g, b) for minimum color
            mid_color: QColor or tuple (r, g, b) for middle/target color
            max_color: QColor or tuple (r, g, b) for maximum color
        """
        if isinstance(min_color, tuple):
            self.min_color = QColor(min_color[0], min_color[1], min_color[2])
        else:
            self.min_color = min_color

        if isinstance(mid_color, tuple):
            self.mid_color = QColor(mid_color[0], mid_color[1], mid_color[2])
        else:
            self.mid_color = mid_color

        if isinstance(max_color, tuple):
            self.max_color = QColor(max_color[0], max_color[1], max_color[2])
        else:
            self.max_color = max_color

        self.update()

    def paintEvent(self, event):
        """Paint the horizontal gradient from min to mid to max."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # Create horizontal gradient from left (min) to right (max)
        # with mid color at the center
        gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
        gradient.setColorAt(0.0, self.min_color)
        gradient.setColorAt(0.5, self.mid_color)
        gradient.setColorAt(1.0, self.max_color)

        painter.fillRect(rect, gradient)

        # Draw border
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(rect)
