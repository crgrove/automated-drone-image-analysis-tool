"""
Color Row Widget

A widget representing a single color range configuration row with:
- Color swatch (showing RGB values)
- RGB min/max controls (Red, Green, Blue min and max)
- Gradient display
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIntValidator, QPainter, QFont
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QLabel,
                               QLineEdit, QPushButton, QSizePolicy, QColorDialog)
import qtawesome as qta
from algorithms.Shared.views.ColorGradientWidget import ColorGradientWidget
from core.services.color.CustomColorsService import get_custom_colors_service


class ClickableColorSwatch(QFrame):
    """A clickable color swatch that opens a color picker when clicked and displays RGB values."""

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
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); "
            f"border: 1px solid #888;"
        )
        # Set tooltip with RGB values
        self.setToolTip(f"RGB: ({r}, {g}, {b})\nClick to change color")
        # Trigger repaint to show RGB text
        self.update()

    def paintEvent(self, event):
        """Override paint event to draw RGB text on the swatch."""
        super().paintEvent(event)
        if self._color:
            r, g, b = self._color.red(), self._color.green(), self._color.blue()
            text_color = Qt.white if (r + g + b) < 384 else Qt.black

            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(text_color)

            # Use smaller font
            font = QFont(self.font())
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)

            # Draw RGB text centered
            text = f"({r},{g},{b})"
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


class ColorRowWidget(QWidget):
    """Widget representing a single color range configuration."""

    # Signal emitted when this row should be deleted
    delete_requested = Signal(QWidget)
    # Signal emitted when color or ranges change
    changed = Signal()

    def __init__(self, parent=None, color=None, r_min=None, r_max=None, g_min=None, g_max=None, b_min=None, b_max=None):
        """
        Initialize a color row widget.

        Args:
            parent: Parent widget
            color: QColor or tuple (r, g, b) for the target color
            r_min, r_max: Red channel min/max (0-255)
            g_min, g_max: Green channel min/max (0-255)
            b_min, b_max: Blue channel min/max (0-255)
        """
        super().__init__(parent)

        # Store color
        if color is None:
            self.color = QColor(255, 0, 0)  # Default to red
        elif isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color

        # Calculate default min/max if not provided (selected color ±50, clamped to 0-255)
        r, g, b = self.color.red(), self.color.green(), self.color.blue()

        if r_min is None:
            r_min = max(0, r - 50)
        if r_max is None:
            r_max = min(255, r + 50)
        if g_min is None:
            g_min = max(0, g - 50)
        if g_max is None:
            g_max = min(255, g + 50)
        if b_min is None:
            b_min = max(0, b - 50)
        if b_max is None:
            b_max = min(255, b + 50)

        # Ensure min <= max
        if r_min > r_max:
            r_max = r_min + 1 if r_min < 255 else 255
        if g_min > g_max:
            g_max = g_min + 1 if g_min < 255 else 255
        if b_min > b_max:
            b_max = b_min + 1 if b_min < 255 else 255

        self.r_min = r_min
        self.r_max = r_max
        self.g_min = g_min
        self.g_max = g_max
        self.b_min = b_min
        self.b_max = b_max

        self._setup_ui()
        self._update_display()

    def _setup_ui(self):
        """Set up the UI layout and widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        self.setFixedHeight(42)

        # Column 1: Color swatch (clickable to change color, shows RGB)
        self.colorSwatch = ClickableColorSwatch(self, self.color)
        self.colorSwatch.colorChanged.connect(self._on_color_changed)
        layout.addWidget(self.colorSwatch)

        # Column 2: RGB Min/Max Controls
        range_layout = QHBoxLayout()
        range_layout.setSpacing(4)

        # Integer validator for 0-255
        validator = QIntValidator(0, 255, self)

        # Red Min/Max
        r_label = QLabel("R:", self)
        r_label.setFont(self.font())
        range_layout.addWidget(r_label)

        self.rMinEdit = QLineEdit(self)
        self.rMinEdit.setValidator(validator)
        self.rMinEdit.setText(str(self.r_min))
        self.rMinEdit.setMinimumWidth(35)
        self.rMinEdit.setMaximumWidth(35)
        self.rMinEdit.setMinimumHeight(24)
        self.rMinEdit.setMaximumHeight(28)
        self.rMinEdit.editingFinished.connect(self._on_r_min_changed)
        range_layout.addWidget(self.rMinEdit)

        r_sep = QLabel("-", self)
        range_layout.addWidget(r_sep)

        self.rMaxEdit = QLineEdit(self)
        self.rMaxEdit.setValidator(validator)
        self.rMaxEdit.setText(str(self.r_max))
        self.rMaxEdit.setMinimumWidth(35)
        self.rMaxEdit.setMaximumWidth(35)
        self.rMaxEdit.setMinimumHeight(24)
        self.rMaxEdit.setMaximumHeight(28)
        self.rMaxEdit.editingFinished.connect(self._on_r_max_changed)
        range_layout.addWidget(self.rMaxEdit)

        range_layout.addSpacing(8)

        # Green Min/Max
        g_label = QLabel("G:", self)
        g_label.setFont(self.font())
        range_layout.addWidget(g_label)

        self.gMinEdit = QLineEdit(self)
        self.gMinEdit.setValidator(validator)
        self.gMinEdit.setText(str(self.g_min))
        self.gMinEdit.setMinimumWidth(35)
        self.gMinEdit.setMaximumWidth(35)
        self.gMinEdit.setMinimumHeight(24)
        self.gMinEdit.setMaximumHeight(28)
        self.gMinEdit.editingFinished.connect(self._on_g_min_changed)
        range_layout.addWidget(self.gMinEdit)

        g_sep = QLabel("-", self)
        range_layout.addWidget(g_sep)

        self.gMaxEdit = QLineEdit(self)
        self.gMaxEdit.setValidator(validator)
        self.gMaxEdit.setText(str(self.g_max))
        self.gMaxEdit.setMinimumWidth(35)
        self.gMaxEdit.setMaximumWidth(35)
        self.gMaxEdit.setMinimumHeight(24)
        self.gMaxEdit.setMaximumHeight(28)
        self.gMaxEdit.editingFinished.connect(self._on_g_max_changed)
        range_layout.addWidget(self.gMaxEdit)

        range_layout.addSpacing(8)

        # Blue Min/Max
        b_label = QLabel("B:", self)
        b_label.setFont(self.font())
        range_layout.addWidget(b_label)

        self.bMinEdit = QLineEdit(self)
        self.bMinEdit.setValidator(validator)
        self.bMinEdit.setText(str(self.b_min))
        self.bMinEdit.setMinimumWidth(35)
        self.bMinEdit.setMaximumWidth(35)
        self.bMinEdit.setMinimumHeight(24)
        self.bMinEdit.setMaximumHeight(28)
        self.bMinEdit.editingFinished.connect(self._on_b_min_changed)
        range_layout.addWidget(self.bMinEdit)

        b_sep = QLabel("-", self)
        range_layout.addWidget(b_sep)

        self.bMaxEdit = QLineEdit(self)
        self.bMaxEdit.setValidator(validator)
        self.bMaxEdit.setText(str(self.b_max))
        self.bMaxEdit.setMinimumWidth(35)
        self.bMaxEdit.setMaximumWidth(35)
        self.bMaxEdit.setMinimumHeight(24)
        self.bMaxEdit.setMaximumHeight(28)
        self.bMaxEdit.editingFinished.connect(self._on_b_max_changed)
        range_layout.addWidget(self.bMaxEdit)

        layout.addLayout(range_layout)

        # Column 3: Gradient display
        self.gradientWidget = ColorGradientWidget(self)
        self.gradientWidget.setMinimumHeight(35)
        self.gradientWidget.setMaximumHeight(35)
        self.gradientWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.gradientWidget)

        # Column 4: Delete button
        self.deleteButton = QPushButton(self)
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setMinimumSize(28, 28)
        self.deleteButton.setMaximumSize(28, 28)
        self.deleteButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.deleteButton.setIcon(qta.icon('fa6s.xmark', color='white'))
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
        layout.addWidget(self.deleteButton)

    def _on_color_changed(self, color):
        """Handle color swatch change - update min/max to ±50 of new color."""
        self.color = color
        r, g, b = color.red(), color.green(), color.blue()

        # Update min/max to ±50 (clamped)
        self.r_min = max(0, r - 50)
        self.r_max = min(255, r + 50)
        self.g_min = max(0, g - 50)
        self.g_max = min(255, g + 50)
        self.b_min = max(0, b - 50)
        self.b_max = min(255, b + 50)

        # Update UI
        self._update_inputs()
        self._update_display()
        self.changed.emit()

    def _on_r_min_changed(self):
        """Handle red min value change."""
        try:
            value = int(self.rMinEdit.text() or 0)
            value = max(0, min(255, value))
            if value > self.r_max:
                self.r_max = value + 1 if value < 255 else 255
                self.rMaxEdit.setText(str(self.r_max))
            self.r_min = value
            self._update_display()
            self.changed.emit()
        except ValueError:
            self.rMinEdit.setText(str(self.r_min))

    def _on_r_max_changed(self):
        """Handle red max value change."""
        try:
            value = int(self.rMaxEdit.text() or 0)
            value = max(0, min(255, value))
            if value < self.r_min:
                self.r_min = value - 1 if value > 0 else 0
                self.rMinEdit.setText(str(self.r_min))
            self.r_max = value
            self._update_display()
            self.changed.emit()
        except ValueError:
            self.rMaxEdit.setText(str(self.r_max))

    def _on_g_min_changed(self):
        """Handle green min value change."""
        try:
            value = int(self.gMinEdit.text() or 0)
            value = max(0, min(255, value))
            if value > self.g_max:
                self.g_max = value + 1 if value < 255 else 255
                self.gMaxEdit.setText(str(self.g_max))
            self.g_min = value
            self._update_display()
            self.changed.emit()
        except ValueError:
            self.gMinEdit.setText(str(self.g_min))

    def _on_g_max_changed(self):
        """Handle green max value change."""
        try:
            value = int(self.gMaxEdit.text() or 0)
            value = max(0, min(255, value))
            if value < self.g_min:
                self.g_min = value - 1 if value > 0 else 0
                self.gMinEdit.setText(str(self.g_min))
            self.g_max = value
            self._update_display()
            self.changed.emit()
        except ValueError:
            self.gMaxEdit.setText(str(self.g_max))

    def _on_b_min_changed(self):
        """Handle blue min value change."""
        try:
            value = int(self.bMinEdit.text() or 0)
            value = max(0, min(255, value))
            if value > self.b_max:
                self.b_max = value + 1 if value < 255 else 255
                self.bMaxEdit.setText(str(self.b_max))
            self.b_min = value
            self._update_display()
            self.changed.emit()
        except ValueError:
            self.bMinEdit.setText(str(self.b_min))

    def _on_b_max_changed(self):
        """Handle blue max value change."""
        try:
            value = int(self.bMaxEdit.text() or 0)
            value = max(0, min(255, value))
            if value < self.b_min:
                self.b_min = value - 1 if value > 0 else 0
                self.bMinEdit.setText(str(self.b_min))
            self.b_max = value
            self._update_display()
            self.changed.emit()
        except ValueError:
            self.bMaxEdit.setText(str(self.b_max))

    def _update_inputs(self):
        """Update input field values from stored min/max."""
        self.rMinEdit.setText(str(self.r_min))
        self.rMaxEdit.setText(str(self.r_max))
        self.gMinEdit.setText(str(self.g_min))
        self.gMaxEdit.setText(str(self.g_max))
        self.bMinEdit.setText(str(self.b_min))
        self.bMaxEdit.setText(str(self.b_max))

    def _update_display(self):
        """Update the color swatch and gradient display."""
        # Update color swatch (block signals to avoid loop)
        if self.colorSwatch.getColor() != self.color:
            self.colorSwatch.blockSignals(True)
            self.colorSwatch.setColor(self.color)
            self.colorSwatch.blockSignals(False)

        # Calculate min and max colors from explicit min/max values
        min_rgb = (self.r_min, self.g_min, self.b_min)
        max_rgb = (self.r_max, self.g_max, self.b_max)
        rgb = (self.color.red(), self.color.green(), self.color.blue())

        # Update gradient
        self.gradientWidget.set_colors(min_rgb, rgb, max_rgb)

    def set_color(self, color):
        """
        Set the target color and update min/max to ±50.

        Args:
            color: QColor or tuple (r, g, b)
        """
        if isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color

        r, g, b = self.color.red(), self.color.green(), self.color.blue()

        # Update min/max to ±50 (clamped)
        self.r_min = max(0, r - 50)
        self.r_max = min(255, r + 50)
        self.g_min = max(0, g - 50)
        self.g_max = min(255, g + 50)
        self.b_min = max(0, b - 50)
        self.b_max = min(255, b + 50)

        self._update_inputs()
        self._update_display()
        self.changed.emit()

    def get_color(self):
        """Get the target color as QColor."""
        return self.color

    def get_rgb(self):
        """Get the target color as RGB tuple."""
        return (self.color.red(), self.color.green(), self.color.blue())

    def get_ranges(self):
        """Get the range values as a tuple (for backward compatibility, returns calculated ranges)."""
        r, g, b = self.color.red(), self.color.green(), self.color.blue()
        r_range = max(abs(self.r_max - r), abs(r - self.r_min))
        g_range = max(abs(self.g_max - g), abs(g - self.g_min))
        b_range = max(abs(self.b_max - b), abs(b - self.b_min))
        return (r_range, g_range, b_range)

    def get_color_range(self):
        """Get the min and max color range as tuples."""
        min_rgb = (self.r_min, self.g_min, self.b_min)
        max_rgb = (self.r_max, self.g_max, self.b_max)
        return min_rgb, max_rgb
