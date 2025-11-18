"""
HSV Color Row Widget

A widget representing a single HSV color range configuration row with:
- Color swatch (showing HSV values)
- HSV range controls (Hue, Saturation, Value min/max)
- Gradient display (min, mid, max)
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIntValidator
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QLabel,
                               QLineEdit, QPushButton, QSizePolicy, QColorDialog)
from algorithms.Shared.views.ColorGradientWidget import ColorGradientWidget
from core.services.color.CustomColorsService import get_custom_colors_service


class ClickableColorSwatch(QFrame):
    """A clickable color swatch that opens HSV color picker when clicked and displays HSV values."""

    colorChanged = Signal(QColor)

    def __init__(self, parent=None, color=None, on_click_callback=None):
        super().__init__(parent)
        self._color = color or QColor(255, 0, 0)
        self._on_click_callback = on_click_callback
        self._hsv_values = None  # Store HSV values for display
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        # Increase size to prevent text cutoff
        self.setMinimumSize(90, 40)
        self.setMaximumSize(90, 40)
        self.setCursor(Qt.PointingHandCursor)
        # Always initialize HSV values
        self._update_hsv_values()
        self._update_style()

    def setColor(self, color):
        """Set the color and update display."""
        self._color = color
        self._update_hsv_values()
        self._update_style()
        self.colorChanged.emit(color)

    def setHSV(self, h, s, v):
        """Set HSV values for display."""
        self._hsv_values = (h, s, v)
        self._update_style()

    def getColor(self):
        """Get the current color."""
        return self._color

    def _update_hsv_values(self):
        """Update HSV values from current color."""
        h, s, v, _ = self._color.getHsvF()
        # Convert to display format: H in degrees (0-359), S/V in percent (0-100)
        h_deg = int(round(h * 360))
        s_pct = int(round(s * 100))
        v_pct = int(round(v * 100))
        self._hsv_values = (h_deg, s_pct, v_pct)

    def _update_style(self):
        """Update the stylesheet with current color."""
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); "
            f"border: 1px solid #888;"
        )
        if self._hsv_values:
            h, s, v = self._hsv_values
            self.setToolTip(f"HSV: ({h}°, {s}%, {v}%)\nRGB: ({r}, {g}, {b})\nClick to change color")
        else:
            self.setToolTip(f"RGB: ({r}, {g}, {b})\nClick to change color")
        # Trigger repaint to show HSV text
        self.update()

    def paintEvent(self, event):
        """Override paint event to draw HSV text on the swatch."""
        super().paintEvent(event)
        # Always show HSV values if color is valid
        if self._color and self._color.isValid():
            # Ensure HSV values are set
            if not self._hsv_values:
                self._update_hsv_values()

            if self._hsv_values:
                from PySide6.QtGui import QPainter, QFont, QFontMetrics
                h, s, v = self._hsv_values
                r, g, b = self._color.red(), self._color.green(), self._color.blue()
                text_color = Qt.white if (r + g + b) < 384 else Qt.black

                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setPen(text_color)

                # Use smaller font that fits - remove parentheses to save space
                font = QFont(self.font())
                font.setPointSize(7)
                font.setBold(True)
                painter.setFont(font)

                # Draw HSV text centered - format without parentheses to prevent cutoff
                text = f"{h}°,{s}%,{v}%"

                # Check if text fits, if not use smaller font
                metrics = QFontMetrics(font)
                text_width = metrics.horizontalAdvance(text)
                if text_width > self.width() - 4:
                    font.setPointSize(6)
                    painter.setFont(font)

                painter.drawText(self.rect(), Qt.AlignCenter, text)
                painter.end()

    def mousePressEvent(self, event):
        """Handle mouse click to open color picker."""
        if event.button() == Qt.LeftButton:
            try:
                # Use custom callback if provided (for HSV picker), otherwise use RGB picker
                if self._on_click_callback:
                    self._on_click_callback()
                else:
                    custom_colors_service = get_custom_colors_service()
                    color = QColorDialog.getColor(self._color)
                    custom_colors_service.sync_with_dialog()
                    if color.isValid():
                        self.setColor(color)
            except Exception:
                pass
        super().mousePressEvent(event)


class HSVColorRowWidget(QWidget):
    """Widget representing a single HSV color range configuration."""

    # Signal emitted when this row should be deleted
    delete_requested = Signal(QWidget)
    # Signal emitted when color or ranges change
    changed = Signal()

    def __init__(self, parent=None, color=None, h_minus=None, h_plus=None,
                 s_minus=None, s_plus=None, v_minus=None, v_plus=None,
                 hsv_ranges=None):
        """
        Initialize an HSV color row widget.

        Args:
            parent: Parent widget
            color: QColor or tuple (r, g, b) for the target color
            h_minus, h_plus: Hue range (0-179, defaults to 20)
            s_minus, s_plus: Saturation range (0-100%, defaults to 50%)
            v_minus, v_plus: Value range (0-100%, defaults to 50%)
            hsv_ranges: Dict with HSV range data (alternative to individual params)
        """
        super().__init__(parent)

        # Store color
        if color is None:
            self.color = QColor(255, 0, 0)  # Default to red
        elif isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color

        # Initialize HSV window data
        if hsv_ranges:
            # Use provided HSV ranges (already in normalized 0-1 format)
            # IMPORTANT: Use the passed-in color, not the HSV values from ranges
            # The color parameter is the source of truth for the actual color
            h, s, v, _ = self.color.getHsvF()
            self._hsv_window = {
                'h': h,
                's': s,
                'v': v,
                'h_minus': hsv_ranges.get('h_minus', 20/179),
                'h_plus': hsv_ranges.get('h_plus', 20/179),
                's_minus': hsv_ranges.get('s_minus', 50/100),  # Default 50% = 0.5
                's_plus': hsv_ranges.get('s_plus', 50/100),  # Default 50% = 0.5
                'v_minus': hsv_ranges.get('v_minus', 50/100),  # Default 50% = 0.5
                'v_plus': hsv_ranges.get('v_plus', 50/100)  # Default 50% = 0.5
            }
            # DO NOT overwrite self.color - use the passed-in color which is the source of truth
        else:
            # Convert color to HSV
            h, s, v, _ = self.color.getHsvF()
            # If h_minus, etc. are provided, they're in display format, convert to normalized
            # Otherwise use default percentages (50% = 0.5 normalized)
            self._hsv_window = {
                'h': h,
                's': s,
                'v': v,
                'h_minus': (h_minus / 179) if h_minus is not None else (20/179),
                'h_plus': (h_plus / 179) if h_plus is not None else (20/179),
                's_minus': (s_minus / 100) if s_minus is not None else (50/100),  # Convert from percentage
                's_plus': (s_plus / 100) if s_plus is not None else (50/100),  # Convert from percentage
                'v_minus': (v_minus / 100) if v_minus is not None else (50/100),  # Convert from percentage
                'v_plus': (v_plus / 100) if v_plus is not None else (50/100)  # Convert from percentage
            }

        self._setup_ui()
        self._update_inputs()
        self._update_display()

    def _setup_ui(self):
        """Set up the UI layout and widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        self.setFixedHeight(42)

        # Column 1: Color swatch (clickable to change color, shows HSV)
        # Pass callback to open HSV picker when clicked
        self.colorSwatch = ClickableColorSwatch(self, self.color, on_click_callback=self._open_hsv_picker)
        self.colorSwatch.colorChanged.connect(self._on_color_changed)
        layout.addWidget(self.colorSwatch)

        # Column 2: HSV Range Controls
        range_layout = QHBoxLayout()
        range_layout.setSpacing(4)

        # Integer validators
        h_validator = QIntValidator(0, 359, self)
        sv_validator = QIntValidator(0, 100, self)

        # Hue Min/Max
        h_label = QLabel("H (°):", self)
        h_label.setFont(self.font())
        range_layout.addWidget(h_label)

        self.hMinEdit = QLineEdit(self)
        self.hMinEdit.setValidator(h_validator)
        # Absolute min degrees; text will be set in _update_inputs
        self.hMinEdit.setMinimumWidth(35)
        self.hMinEdit.setMaximumWidth(35)
        self.hMinEdit.setMinimumHeight(24)
        self.hMinEdit.setMaximumHeight(28)
        self.hMinEdit.editingFinished.connect(self._on_h_minus_changed)
        range_layout.addWidget(self.hMinEdit)

        h_sep = QLabel("-", self)
        range_layout.addWidget(h_sep)

        self.hPlusEdit = QLineEdit(self)
        self.hPlusEdit.setValidator(h_validator)
        # Absolute max degrees; text will be set in _update_inputs
        self.hPlusEdit.setMinimumWidth(35)
        self.hPlusEdit.setMaximumWidth(35)
        self.hPlusEdit.setMinimumHeight(24)
        self.hPlusEdit.setMaximumHeight(28)
        self.hPlusEdit.editingFinished.connect(self._on_h_plus_changed)
        range_layout.addWidget(self.hPlusEdit)

        range_layout.addSpacing(8)

        # Saturation Min/Max (display as percentages)
        s_label = QLabel("S (%):", self)
        s_label.setFont(self.font())
        range_layout.addWidget(s_label)

        self.sMinEdit = QLineEdit(self)
        self.sMinEdit.setValidator(sv_validator)
        self.sMinEdit.setMinimumWidth(35)
        self.sMinEdit.setMaximumWidth(35)
        self.sMinEdit.setMinimumHeight(24)
        self.sMinEdit.setMaximumHeight(28)
        self.sMinEdit.editingFinished.connect(self._on_s_minus_changed)
        range_layout.addWidget(self.sMinEdit)

        s_sep = QLabel("-", self)
        range_layout.addWidget(s_sep)

        self.sPlusEdit = QLineEdit(self)
        self.sPlusEdit.setValidator(sv_validator)
        self.sPlusEdit.setMinimumWidth(35)
        self.sPlusEdit.setMaximumWidth(35)
        self.sPlusEdit.setMinimumHeight(24)
        self.sPlusEdit.setMaximumHeight(28)
        self.sPlusEdit.editingFinished.connect(self._on_s_plus_changed)
        range_layout.addWidget(self.sPlusEdit)

        range_layout.addSpacing(8)

        # Value Min/Max (display as percentages)
        v_label = QLabel("V (%):", self)
        v_label.setFont(self.font())
        range_layout.addWidget(v_label)

        self.vMinEdit = QLineEdit(self)
        self.vMinEdit.setValidator(sv_validator)
        self.vMinEdit.setMinimumWidth(35)
        self.vMinEdit.setMaximumWidth(35)
        self.vMinEdit.setMinimumHeight(24)
        self.vMinEdit.setMaximumHeight(28)
        self.vMinEdit.editingFinished.connect(self._on_v_minus_changed)
        range_layout.addWidget(self.vMinEdit)

        v_sep = QLabel("-", self)
        range_layout.addWidget(v_sep)

        self.vPlusEdit = QLineEdit(self)
        self.vPlusEdit.setValidator(sv_validator)
        self.vPlusEdit.setMinimumWidth(35)
        self.vPlusEdit.setMaximumWidth(35)
        self.vPlusEdit.setMinimumHeight(24)
        self.vPlusEdit.setMaximumHeight(28)
        self.vPlusEdit.editingFinished.connect(self._on_v_plus_changed)
        range_layout.addWidget(self.vPlusEdit)

        layout.addLayout(range_layout)

        # Column 3: Gradient display
        self.gradientWidget = ColorGradientWidget(self)
        self.gradientWidget.setMinimumHeight(35)
        self.gradientWidget.setMaximumHeight(35)
        self.gradientWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.gradientWidget)

        # Column 4: Delete button
        self.deleteButton = QPushButton("✕", self)
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
        layout.addWidget(self.deleteButton)

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV (0-1 normalized) to RGB (0-255)."""
        color = QColor.fromHsvF(h, s, v)
        return (color.red(), color.green(), color.blue())

    def _calculate_gradient_colors(self):
        """Calculate min, mid, max RGB colors from HSV ranges for gradient display."""
        h, s, v = self._hsv_window['h'], self._hsv_window['s'], self._hsv_window['v']
        h_minus, h_plus = self._hsv_window['h_minus'], self._hsv_window['h_plus']
        s_minus, s_plus = self._hsv_window['s_minus'], self._hsv_window['s_plus']
        v_minus, v_plus = self._hsv_window['v_minus'], self._hsv_window['v_plus']

        # Calculate min HSV with wrapping for hue
        # Use modulo 1.0 to wrap hue around 0-360 degrees
        h_min = (h - h_minus) % 1.0
        s_min = max(0.0, min(1.0, s - s_minus))
        v_min = max(0.0, min(1.0, v - v_minus))

        # Mid HSV (center color)
        h_mid, s_mid, v_mid = h, s, v

        # Calculate max HSV with wrapping for hue
        h_max = (h + h_plus) % 1.0
        s_max = max(0.0, min(1.0, s + s_plus))
        v_max = max(0.0, min(1.0, v + v_plus))

        # Convert to RGB
        min_rgb = self._hsv_to_rgb(h_min, s_min, v_min)
        mid_rgb = self._hsv_to_rgb(h_mid, s_mid, v_mid)
        max_rgb = self._hsv_to_rgb(h_max, s_max, v_max)

        return min_rgb, mid_rgb, max_rgb

    def _open_hsv_picker(self):
        """Open the HSV color range picker dialog."""
        try:
            from algorithms.Shared.views.ColorRangeDialog import ColorRangeDialog
            from core.services.color.CustomColorsService import get_custom_colors_service

            # Get current HSV values
            initial_hsv = (self._hsv_window['h'], self._hsv_window['s'], self._hsv_window['v'])
            initial_ranges = {
                'h_minus': self._hsv_window['h_minus'],
                'h_plus': self._hsv_window['h_plus'],
                's_minus': self._hsv_window['s_minus'],
                's_plus': self._hsv_window['s_plus'],
                'v_minus': self._hsv_window['v_minus'],
                'v_plus': self._hsv_window['v_plus']
            }

            # Open dialog
            dialog = ColorRangeDialog(None, initial_hsv, initial_ranges, self)

            if dialog.exec() == ColorRangeDialog.Accepted:
                hsv_data = dialog.get_hsv_ranges()

                # Save any custom colors that may have been modified
                custom_colors_service = get_custom_colors_service()
                custom_colors_service.sync_with_dialog()

                # Update HSV window data
                self._hsv_window = hsv_data

                # Update color from HSV
                h, s, v = hsv_data['h'], hsv_data['s'], hsv_data['v']
                self.color = QColor.fromHsvF(h, s, v)

                # Update inputs
                self._update_inputs()

                # Update display
                self._update_display()
                self.changed.emit()
        except Exception:
            # Silently fail if there's an error
            pass

    def _on_color_changed(self, color):
        """Handle color swatch change - update HSV window."""
        self.color = color
        h, s, v, _ = color.getHsvF()
        self._hsv_window['h'] = h
        self._hsv_window['s'] = s
        self._hsv_window['v'] = v

        # Update min/max to ±50% for S/V, ±20 for H (defaults)
        self._hsv_window['h_minus'] = 20/179
        self._hsv_window['h_plus'] = 20/179
        self._hsv_window['s_minus'] = 50/100
        self._hsv_window['s_plus'] = 50/100
        self._hsv_window['v_minus'] = 50/100
        self._hsv_window['v_plus'] = 50/100

        # Update UI
        self._update_inputs()
        self._update_display()
        self.changed.emit()

    def _on_h_minus_changed(self):
        """Handle hue MIN value change (absolute degrees)."""
        try:
            center_deg = int(round(self._hsv_window['h'] * 360))
            min_deg = int(self.hMinEdit.text() or 0)
            # Clamp to valid degree range
            min_deg = max(0, min(359, min_deg))
            # Calculate the range, handling wrapping
            if min_deg <= center_deg:
                # Normal case: min is before center
                range_deg = center_deg - min_deg
            else:
                # Wrapped case: min is after center (e.g., 330 to 0)
                range_deg = center_deg + (360 - min_deg)
            # Update minus fraction (relative to 360)
            self._hsv_window['h_minus'] = range_deg / 360.0
            self.hMinEdit.setText(str(min_deg))
            self._update_display()
            self.changed.emit()
        except ValueError:
            # Reset to computed min
            center_deg = int(round(self._hsv_window['h'] * 360))
            min_deg = (center_deg - int(round(self._hsv_window['h_minus'] * 360))) % 360
            self.hMinEdit.setText(str(min_deg))

    def _on_h_plus_changed(self):
        """Handle hue MAX value change (absolute degrees)."""
        try:
            center_deg = int(round(self._hsv_window['h'] * 360))
            max_deg = int(self.hPlusEdit.text() or 0)
            # Clamp to valid degree range
            max_deg = max(0, min(359, max_deg))
            # Calculate the range, handling wrapping
            if max_deg >= center_deg:
                # Normal case: max is after center
                range_deg = max_deg - center_deg
            else:
                # Wrapped case: max is before center (e.g., 0 to 30 when center is 350)
                range_deg = max_deg + (360 - center_deg)
            # Update plus fraction (relative to 360)
            self._hsv_window['h_plus'] = range_deg / 360.0
            self.hPlusEdit.setText(str(max_deg))
            self._update_display()
            self.changed.emit()
        except ValueError:
            # Reset to computed max
            center_deg = int(round(self._hsv_window['h'] * 360))
            max_deg = (center_deg + int(round(self._hsv_window['h_plus'] * 360))) % 360
            self.hPlusEdit.setText(str(max_deg))

    def _on_s_minus_changed(self):
        """Handle saturation MIN value change (absolute %)."""
        try:
            center_pct = int(round(self._hsv_window['s'] * 100))
            min_pct = int(self.sMinEdit.text() or 0)
            min_pct = max(0, min(100, min(min_pct, center_pct)))
            try:
                max_pct = int(self.sPlusEdit.text() or 0)
            except ValueError:
                max_pct = center_pct + int(round(self._hsv_window['s_plus'] * 100))
            if min_pct > max_pct:
                max_pct = min_pct
                self.sPlusEdit.setText(str(max_pct))
            self._hsv_window['s_minus'] = max(0.0, (center_pct - min_pct) / 100.0)
            self.sMinEdit.setText(str(min_pct))
            self._update_display()
            self.changed.emit()
        except ValueError:
            center_pct = int(round(self._hsv_window['s'] * 100))
            min_pct = max(0, center_pct - int(round(self._hsv_window['s_minus'] * 100)))
            self.sMinEdit.setText(str(min_pct))

    def _on_s_plus_changed(self):
        """Handle saturation MAX value change (absolute %)."""
        try:
            center_pct = int(round(self._hsv_window['s'] * 100))
            max_pct = int(self.sPlusEdit.text() or 0)
            max_pct = max(0, min(100, max(max_pct, center_pct)))
            try:
                min_pct = int(self.sMinEdit.text() or 0)
            except ValueError:
                min_pct = center_pct - int(round(self._hsv_window['s_minus'] * 100))
            if max_pct < min_pct:
                min_pct = max_pct
                self.sMinEdit.setText(str(min_pct))
            self._hsv_window['s_plus'] = max(0.0, (max_pct - center_pct) / 100.0)
            self.sPlusEdit.setText(str(max_pct))
            self._update_display()
            self.changed.emit()
        except ValueError:
            center_pct = int(round(self._hsv_window['s'] * 100))
            max_pct = min(100, center_pct + int(round(self._hsv_window['s_plus'] * 100)))
            self.sPlusEdit.setText(str(max_pct))

    def _on_v_minus_changed(self):
        """Handle value MIN value change (absolute %)."""
        try:
            center_pct = int(round(self._hsv_window['v'] * 100))
            min_pct = int(self.vMinEdit.text() or 0)
            min_pct = max(0, min(100, min(min_pct, center_pct)))
            try:
                max_pct = int(self.vPlusEdit.text() or 0)
            except ValueError:
                max_pct = center_pct + int(round(self._hsv_window['v_plus'] * 100))
            if min_pct > max_pct:
                max_pct = min_pct
                self.vPlusEdit.setText(str(max_pct))
            self._hsv_window['v_minus'] = max(0.0, (center_pct - min_pct) / 100.0)
            self.vMinEdit.setText(str(min_pct))
            self._update_display()
            self.changed.emit()
        except ValueError:
            center_pct = int(round(self._hsv_window['v'] * 100))
            min_pct = max(0, center_pct - int(round(self._hsv_window['v_minus'] * 100)))
            self.vMinEdit.setText(str(min_pct))

    def _on_v_plus_changed(self):
        """Handle value MAX value change (absolute %)."""
        try:
            center_pct = int(round(self._hsv_window['v'] * 100))
            max_pct = int(self.vPlusEdit.text() or 0)
            max_pct = max(0, min(100, max(max_pct, center_pct)))
            try:
                min_pct = int(self.vMinEdit.text() or 0)
            except ValueError:
                min_pct = center_pct - int(round(self._hsv_window['v_minus'] * 100))
            if max_pct < min_pct:
                min_pct = max_pct
                self.vMinEdit.setText(str(min_pct))
            self._hsv_window['v_plus'] = max(0.0, (max_pct - center_pct) / 100.0)
            self.vPlusEdit.setText(str(max_pct))
            self._update_display()
            self.changed.emit()
        except ValueError:
            center_pct = int(round(self._hsv_window['v'] * 100))
            max_pct = min(100, center_pct + int(round(self._hsv_window['v_plus'] * 100)))
            self.vPlusEdit.setText(str(max_pct))

    def _update_inputs(self):
        """Update input field values from stored ranges as ABSOLUTE bounds."""
        center_deg = int(round(self._hsv_window['h'] * 360))
        h_min = (center_deg - int(round(self._hsv_window['h_minus'] * 360))) % 360
        h_max = (center_deg + int(round(self._hsv_window['h_plus'] * 360))) % 360
        self.hMinEdit.setText(str(h_min))
        self.hPlusEdit.setText(str(h_max))
        center_s = int(round(self._hsv_window['s'] * 100))
        # Fix rounding: use round() before converting to int to avoid off-by-one errors
        s_minus_pct = round(self._hsv_window['s_minus'] * 100)
        s_plus_pct = round(self._hsv_window['s_plus'] * 100)
        s_min = max(0, center_s - int(s_minus_pct))
        s_max = min(100, center_s + int(s_plus_pct))
        self.sMinEdit.setText(str(s_min))
        self.sPlusEdit.setText(str(s_max))
        center_v = int(round(self._hsv_window['v'] * 100))
        # Fix rounding: use round() before converting to int to avoid off-by-one errors
        v_minus_pct = round(self._hsv_window['v_minus'] * 100)
        v_plus_pct = round(self._hsv_window['v_plus'] * 100)
        v_min = max(0, center_v - int(v_minus_pct))
        v_max = min(100, center_v + int(v_plus_pct))
        self.vMinEdit.setText(str(v_min))
        self.vPlusEdit.setText(str(v_max))

    def _update_display(self):
        """Update the color swatch and gradient display."""
        # Update color swatch (block signals to avoid loop)
        if self.colorSwatch.getColor() != self.color:
            self.colorSwatch.blockSignals(True)
            self.colorSwatch.setColor(self.color)
            self.colorSwatch.blockSignals(False)

        # Always update HSV display on swatch to ensure it's shown consistently
        h, s, v = self._hsv_window['h'], self._hsv_window['s'], self._hsv_window['v']
        h_deg = int(round(h * 360))
        s_pct = int(round(s * 100))
        v_pct = int(round(v * 100))
        self.colorSwatch.setHSV(h_deg, s_pct, v_pct)

        # Calculate and update gradient
        min_rgb, mid_rgb, max_rgb = self._calculate_gradient_colors()
        self.gradientWidget.set_colors(min_rgb, mid_rgb, max_rgb)

    def set_color(self, color):
        """
        Set the target color and update HSV window.

        Args:
            color: QColor or tuple (r, g, b)
        """
        if isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color

        h, s, v, _ = self.color.getHsvF()
        self._hsv_window['h'] = h
        self._hsv_window['s'] = s
        self._hsv_window['v'] = v

        # Set default ranges (±50% for S/V, ±20 for H)
        self._hsv_window['h_minus'] = 20/179
        self._hsv_window['h_plus'] = 20/179
        self._hsv_window['s_minus'] = 50/100
        self._hsv_window['s_plus'] = 50/100
        self._hsv_window['v_minus'] = 50/100
        self._hsv_window['v_plus'] = 50/100

        self._update_inputs()
        self._update_display()
        self.changed.emit()

    def get_color(self):
        """Get the target color as QColor."""
        return self.color

    def get_rgb(self):
        """Get the target color as RGB tuple."""
        return (self.color.red(), self.color.green(), self.color.blue())

    def get_hsv_ranges(self):
        """Get the HSV range data."""
        return self._hsv_window.copy()
