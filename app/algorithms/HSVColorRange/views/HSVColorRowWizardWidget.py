"""
HSV Color Row Widget for Wizard

A simplified widget for HSV color range configuration in the wizard with:
- Color swatch
- Tolerance dropdown (instead of numeric inputs)
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QLabel, QComboBox,
                               QPushButton, QSizePolicy, QColorDialog)
from core.services.color.CustomColorsService import get_custom_colors_service
import cv2
import numpy as np


class ClickableColorSwatch(QFrame):
    """A clickable color swatch that opens a color picker when clicked."""

    colorChanged = Signal(QColor)

    def __init__(self, parent=None, color=None):
        super().__init__(parent)
        self._color = color or QColor(255, 0, 0)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(80, 35)
        self.setMaximumSize(80, 35)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def setColor(self, color):
        """Set the color and update display."""
        self._color = color
        self._update_style()
        self.colorChanged.emit(color)

    def getColor(self):
        """Get the current color."""
        return self._color

    def _update_style(self):
        """Update the stylesheet with current color."""
        if not self._color or not self._color.isValid():
            return
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        # Compute HSV in OpenCV scale for display and tooltip
        hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])
        self.setAutoFillBackground(True)
        self.setStyleSheet(
            f"QFrame {{ background-color: rgb({r}, {g}, {b}); border: 1px solid #888; }}"
        )
        self.setToolTip(f"HSV: ({h}, {s}, {v})\nClick to change color")
        self.update()
        self.repaint()

    def paintEvent(self, event):
        """Draw HSV text on top of the swatch color."""
        super().paintEvent(event)
        if not self._color or not self._color.isValid():
            return
        # Determine contrasting text color based on RGB brightness
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        from PySide6.QtGui import QPainter, QFont
        text_color = Qt.white if (r + g + b) < 384 else Qt.black

        # Compute HSV in OpenCV scale for display
        hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])
        text = f"({h},{s},{v})"

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(text_color)
        font = QFont(self.font())
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, text)
        painter.end()

    def mousePressEvent(self, event):
        """Handle mouse click to open color picker."""
        if event.button() == Qt.LeftButton:
            try:
                custom_colors_service = get_custom_colors_service()
                color = QColorDialog.getColor(self._color)
                custom_colors_service.sync_with_dialog()
                if color.isValid():
                    self.setColor(color)
            except Exception:
                pass
        super().mousePressEvent(event)


class HSVColorRowWizardWidget(QWidget):
    """Simplified widget representing an HSV color range configuration for wizard."""

    delete_requested = Signal(QWidget)
    changed = Signal()

    # Tolerance presets for HSV: (label, (h_range, s_range, v_range))
    TOLERANCE_PRESETS = [
        ("Very Narrow", (10, 30, 30)),
        ("Narrow", (15, 50, 50)),
        ("Moderate", (20, 70, 70)),
        ("Wide", (30, 100, 100)),
        ("Very Wide", (40, 120, 120))
    ]

    def __init__(self, parent=None, color=None, tolerance_index=2):
        """
        Initialize an HSV color row wizard widget.

        Args:
            parent: Parent widget
            color: QColor or tuple (r, g, b) for the target color
            tolerance_index: Index into TOLERANCE_PRESETS (0-4, default 2 = Moderate)
        """
        super().__init__(parent)

        # Store color
        if color is None:
            self.color = QColor(255, 0, 0)
        elif isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color

        self.tolerance_index = max(0, min(tolerance_index, len(self.TOLERANCE_PRESETS) - 1))

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI layout and widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignLeft)
        # Keep row compact: don't expand to full dialog width
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(42)

        # Color swatch - ensure color is set properly
        self.colorSwatch = ClickableColorSwatch(self, self.color)
        self.colorSwatch.colorChanged.connect(self._on_color_changed)
        # Force update to ensure color is displayed
        self.colorSwatch.setColor(self.color)
        layout.addWidget(self.colorSwatch)

        # Tolerance label
        tolerance_label = QLabel("Match\nTolerance:", self)
        tolerance_label.setFont(self.font())
        tolerance_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(tolerance_label)

        # Tolerance dropdown
        self.toleranceCombo = QComboBox(self)
        # Inputs should be 11pt
        combo_font = QFont(self.font())
        combo_font.setPointSize(11)
        self.toleranceCombo.setFont(combo_font)
        for label, _ in self.TOLERANCE_PRESETS:
            self.toleranceCombo.addItem(label)
        self.toleranceCombo.setCurrentIndex(self.tolerance_index)
        self.toleranceCombo.currentIndexChanged.connect(self._on_tolerance_changed)
        self.toleranceCombo.setMinimumWidth(150)
        self.toleranceCombo.setMaximumWidth(200)
        self.toleranceCombo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.toleranceCombo)

        # Delete button
        self.deleteButton = QPushButton("✕", self)
        btn_font = QFont(self.font())
        btn_font.setPointSize(11)
        self.deleteButton.setFont(btn_font)
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setMinimumSize(28, 28)
        self.deleteButton.setMaximumSize(28, 28)
        self.deleteButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.deleteButton.setStyleSheet("""
            QPushButton#deleteButton {
                background-color: #d32f2f;
                color: white;
                border: 1px solid #b71c1c;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton#deleteButton:hover {
                background-color: #f44336;
            }
            QPushButton#deleteButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.deleteButton.clicked.connect(lambda: self.delete_requested.emit(self))
        self.deleteButton.setFocusPolicy(Qt.NoFocus)  # Prevent delete button from getting focus
        layout.addWidget(self.deleteButton)

    def _on_color_changed(self, color):
        """Handle color swatch change."""
        self.color = color
        self.changed.emit()

    def _on_tolerance_changed(self, index):
        """Handle tolerance dropdown change."""
        self.tolerance_index = index
        self.changed.emit()

    def set_color(self, color):
        """Set the target color."""
        if isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color
        self.colorSwatch.blockSignals(True)
        self.colorSwatch.setColor(self.color)
        self.colorSwatch.blockSignals(False)
        self.changed.emit()

    def get_color(self):
        """Get the target color as QColor."""
        return self.color

    def get_rgb(self):
        """Get the target color as RGB tuple."""
        return (self.color.red(), self.color.green(), self.color.blue())

    def get_tolerance_index(self):
        """Get the selected tolerance index."""
        return self.tolerance_index

    def get_tolerance_values(self):
        """Get the HSV tolerance values (h_range, s_range, v_range)."""
        return self.TOLERANCE_PRESETS[self.tolerance_index][1]

    def get_ranges(self):
        """Get the range values for backward compatibility."""
        return self.get_tolerance_values()

    def get_color_range(self):
        """Get the min and max HSV range as tuples based on tolerance."""
        r, g, b = self.color.red(), self.color.green(), self.color.blue()

        # Convert RGB to HSV (OpenCV format: H=0-179, S=0-255, V=0-255)
        hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

        # Get tolerance values
        h_range, s_range, v_range = self.get_tolerance_values()

        # Calculate min/max with clamping
        min_hsv = (max(0, h - h_range), max(0, s - s_range), max(0, v - v_range))
        max_hsv = (min(179, h + h_range), min(255, s + s_range), min(255, v + v_range))
        return min_hsv, max_hsv
