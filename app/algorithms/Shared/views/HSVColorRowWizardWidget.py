"""
HSV Color Row Widget for Wizard

A simplified widget for HSV color range configuration in the wizard with:
- Color swatch
- Tolerance dropdown (instead of numeric inputs)
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QLabel, QComboBox,
                               QPushButton, QSizePolicy)
import qtawesome as qta
from algorithms.Shared.views.ColorRangeDialog import ColorRangeDialog
import cv2
import numpy as np
from helpers.TranslationMixin import TranslationMixin


class ClickableColorSwatch(TranslationMixin, QFrame):
    """A clickable color swatch. Uses a provided callback when clicked."""

    colorChanged = Signal(QColor)

    def __init__(self, parent=None, color=None, on_click_callback=None):
        super().__init__(parent)
        self._on_click_callback = on_click_callback
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(80, 35)
        self.setMaximumSize(80, 35)
        self.setCursor(Qt.PointingHandCursor)
        # Set color after frame setup - use setColor to ensure proper initialization
        if color is not None:
            self.setColor(color)
        else:
            self.setColor(QColor(255, 0, 0))

    def setColor(self, color):
        """Set the color and update display."""
        if isinstance(color, QColor) and color.isValid():
            self._color = QColor(color.red(), color.green(), color.blue())
        elif isinstance(color, tuple) and len(color) >= 3:
            self._color = QColor(color[0], color[1], color[2])
        elif color is None:
            self._color = QColor(255, 0, 0)
        else:
            self._color = QColor(255, 0, 0)
        if not self._color.isValid():
            self._color = QColor(255, 0, 0)
        self._update_style()
        self.colorChanged.emit(self._color)

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
        self.setStyleSheet(
            f"QFrame {{ background-color: rgb({r}, {g}, {b}); border: 1px solid #888; }}"
        )
        self.setToolTip(
            self.tr("HSV: ({h}, {s}, {v})\nClick to change color").format(h=h, s=s, v=v)
        )
        self.update()
        self.repaint()

    def paintEvent(self, event):
        """Draw HSV text on top of the swatch color."""
        super().paintEvent(event)
        if not self._color or not self._color.isValid():
            return
        # Determine contrasting text color based on RGB brightness
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
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
        """Handle mouse click to invoke callback."""
        if event.button() == Qt.LeftButton:
            try:
                if callable(self._on_click_callback):
                    self._on_click_callback()
            except Exception:
                pass
        super().mousePressEvent(event)


class HSVColorRowWizardWidget(TranslationMixin, QWidget):
    """Simplified widget representing an HSV color range configuration for wizard."""

    delete_requested = Signal(QWidget)
    changed = Signal()

    # Default fixed width for each row so all rows match but do not span dialog
    DEFAULT_ROW_WIDTH = 520

    # Tolerance presets for HSV: (label, (h_range, s_range, v_range))
    # h_range: OpenCV scale (0-179)
    # s_range, v_range: OpenCV scale (0-255), NOT percentages
    TOLERANCE_PRESETS = [
        ("Very Narrow", (5, 25, 25)),
        ("Narrow", (10, 50, 50)),
        ("Moderate", (15, 75, 75)),
        ("Wide", (20, 100, 100)),
        ("Very Wide", (35, 125, 125))
    ]

    def __init__(self, parent=None, color=None, tolerance_index=2, from_hsv_picker=False, row_width=None):
        """
        Initialize an HSV color row wizard widget.

        Args:
            parent: Parent widget
            color: QColor or tuple (r, g, b) for the target color
            tolerance_index: Index into TOLERANCE_PRESETS (0-4, default 2 = Moderate)
            from_hsv_picker: If True, color was added via HSV picker (show message instead of tolerance dropdown)
            row_width: Optional fixed width for the row (defaults to DEFAULT_ROW_WIDTH)
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
        self.from_hsv_picker = from_hsv_picker
        self.hsv_ranges = None  # When using HSV picker, holds dict with fractional ranges
        self.row_width = row_width or self.DEFAULT_ROW_WIDTH

        self._setup_ui()
        self._apply_translations()

    def _setup_ui(self):
        """Set up the UI layout and widgets."""
        # Remove all margins from the widget itself
        self.setContentsMargins(0, 0, 0, 0)

        # Outer layout for the row widget
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Frame to visually emulate a table row (bordered container)
        # Borders will connect to form a table appearance
        self.rowFrame = QFrame(self)
        self.rowFrame.setObjectName("rowFrame")
        # Style will be set based on row position (first/last/middle)
        rowLayout = QHBoxLayout(self.rowFrame)
        # Symmetric top/bottom margins so content isn't flush against borders
        rowLayout.setContentsMargins(8, 6, 8, 6)
        rowLayout.setSpacing(12)
        rowLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self.rowFrame)

        # Keep rows compact horizontally (not full width)
        # Height must accommodate: 6px top margin + 35px swatch + 6px bottom margin = 47px minimum
        # Use 54px to provide visible spacing above and below the swatch (54 - 6 - 6 = 42px available, 35px swatch = 7px total space, ~3.5px each side)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(54)

        # Make rowFrame expand to fill the row
        self.rowFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Ensure consistent width across all rows without spanning entire dialog
        try:
            self.rowFrame.setFixedWidth(int(self.row_width))
        except Exception:
            # Fallback to default width in case of invalid value
            self.rowFrame.setFixedWidth(self.DEFAULT_ROW_WIDTH)

        # Set border style - will be updated when row is added to container
        self._update_border_style()

        # Color swatch - pass color directly to constructor to ensure it's set correctly
        # Block signals during initialization to prevent any circular updates
        self.colorSwatch = ClickableColorSwatch(self.rowFrame, self.color, on_click_callback=self._open_hsv_picker)
        # Connect signal AFTER swatch is created to avoid triggering during initialization
        self.colorSwatch.colorChanged.connect(self._on_color_changed)
        rowLayout.addWidget(self.colorSwatch)
        try:
            rowLayout.setAlignment(self.colorSwatch, Qt.AlignVCenter)
        except Exception:
            pass

        # Tolerance label (for preset mode)
        self.toleranceLabel = QLabel("Match\nTolerance:", self.rowFrame)
        # Force 11pt font
        _lbl_font = QFont(self.font())
        _lbl_font.setPointSize(11)
        self.toleranceLabel.setFont(_lbl_font)
        self.toleranceLabel.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        rowLayout.addWidget(self.toleranceLabel)

        # Tolerance dropdown (preset selection)
        self.toleranceCombo = QComboBox(self.rowFrame)
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
        rowLayout.addWidget(self.toleranceCombo)
        try:
            rowLayout.setAlignment(self.toleranceCombo, Qt.AlignVCenter)
        except Exception:
            pass

        # HSV ranges display for HSV picker mode (read-only)
        self.hsvRangesLabel = QLabel("", self.rowFrame)
        # Force 11pt font
        _ranges_font = QFont(self.font())
        _ranges_font.setPointSize(11)
        self.hsvRangesLabel.setFont(_ranges_font)
        self.hsvRangesLabel.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.hsvRangesLabel.setStyleSheet("color: #bbb;")
        self.hsvRangesLabel.setWordWrap(False)
        self.hsvRangesLabel.setMinimumWidth(250)  # Ensure text isn't cut off
        rowLayout.addWidget(self.hsvRangesLabel)

        # Toggle visibility based on current mode
        self._apply_mode_visibility()

        # Add spacer to push delete button to the right
        rowLayout.addStretch()

        # Delete button
        self.deleteButton = QPushButton(self.rowFrame)
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
        self.deleteButton.setFocusPolicy(Qt.NoFocus)  # Prevent delete button from getting focus
        rowLayout.addWidget(self.deleteButton)

    def _update_border_style(self):
        """Update border style based on row position to create table appearance."""
        if not self.parent():
            # Default: show all borders if parent not ready
            self.rowFrame.setStyleSheet("""
                QFrame#rowFrame {
                    border: 1px solid #666;
                    background-color: transparent;
                }
            """)
            return

        parent_layout = self.parent().layout()
        if not parent_layout:
            self.rowFrame.setStyleSheet("""
                QFrame#rowFrame {
                    border: 1px solid #666;
                    background-color: transparent;
                }
            """)
            return

        # Find index of this widget among other row widgets (filter out non-row widgets)
        # Check for row widgets by looking for the _update_border_style method
        row_widgets = []
        for i in range(parent_layout.count()):
            item = parent_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget and hasattr(widget, '_update_border_style'):
                row_widgets.append(widget)

        # Find our index in the list of row widgets
        try:
            row_index = row_widgets.index(self)
        except ValueError:
            # Not found, default to showing all borders
            self.rowFrame.setStyleSheet("""
                QFrame#rowFrame {
                    border: 1px solid #666;
                    background-color: transparent;
                }
            """)
            return

        is_first = (row_index == 0)

        # Style borders to connect and form a table
        # First row: all borders (including top)
        # Other rows: left, right, bottom (no top border to connect)
        if is_first:
            border_style = "border: 1px solid #666;"
        else:
            border_style = "border-left: 1px solid #666; border-right: 1px solid #666; border-bottom: 1px solid #666; border-top: none;"

        self.rowFrame.setStyleSheet(f"""
            QFrame#rowFrame {{
                {border_style}
                background-color: transparent;
            }}
        """)

    def showEvent(self, event):
        """Update border style when widget is shown."""
        super().showEvent(event)
        # Update border style - method handles parent not ready gracefully
        self._update_border_style()

    def _update_hsv_ranges_display(self):
        """Update the HSV ranges display text."""
        if not self.from_hsv_picker:
            self.hsvRangesLabel.setText("")
            return

        if not self.hsv_ranges:
            self.hsvRangesLabel.setText("")
            return

        # Get center values and ranges from hsv_ranges dict (all fractional 0-1)
        h_center = self.hsv_ranges.get('h', 0.0)
        s_center = self.hsv_ranges.get('s', 0.0)
        v_center = self.hsv_ranges.get('v', 0.0)
        h_minus = self.hsv_ranges.get('h_minus', 0.0)
        h_plus = self.hsv_ranges.get('h_plus', 0.0)
        s_minus = self.hsv_ranges.get('s_minus', 0.0)
        s_plus = self.hsv_ranges.get('s_plus', 0.0)
        v_minus = self.hsv_ranges.get('v_minus', 0.0)
        v_plus = self.hsv_ranges.get('v_plus', 0.0)

        # Ensure values are in 0-1 range (fractional)
        h_center = max(0.0, min(1.0, float(h_center)))
        s_center = max(0.0, min(1.0, float(s_center)))
        v_center = max(0.0, min(1.0, float(v_center)))
        h_minus = max(0.0, min(1.0, float(h_minus)))
        h_plus = max(0.0, min(1.0, float(h_plus)))
        s_minus = max(0.0, min(1.0, float(s_minus)))
        s_plus = max(0.0, min(1.0, float(s_plus)))
        v_minus = max(0.0, min(1.0, float(v_minus)))
        v_plus = max(0.0, min(1.0, float(v_plus)))

        # Calculate min/max values
        # Hue: convert to degrees (0-360) for display, handle circular wrapping
        h_min_deg = int((h_center - h_minus) * 360) % 360
        h_max_deg = int((h_center + h_plus) * 360) % 360
        # Saturation and Value: use OpenCV scale (0-255) for display
        s_min = max(0, int((s_center - s_minus) * 255))
        s_max = min(255, int((s_center + s_plus) * 255))
        v_min = max(0, int((v_center - v_minus) * 255))
        v_max = min(255, int((v_center + v_plus) * 255))

        # Format as "H: min-max°, S: min-max, V: min-max"
        ranges_text = self.tr("H: {h_min}-{h_max}°, S: {s_min}-{s_max}, V: {v_min}-{v_max}").format(
            h_min=h_min_deg,
            h_max=h_max_deg,
            s_min=s_min,
            s_max=s_max,
            v_min=v_min,
            v_max=v_max
        )
        self.hsvRangesLabel.setText(ranges_text)

    def _apply_mode_visibility(self):
        """Show/hide controls based on HSV picker mode."""
        if self.from_hsv_picker:
            self.toleranceLabel.hide()
            self.toleranceCombo.hide()
            self.hsvRangesLabel.show()
            self._update_hsv_ranges_display()
        else:
            self.toleranceLabel.show()
            self.toleranceCombo.show()
            self.hsvRangesLabel.hide()

    def _open_hsv_picker(self):
        """Open the HSV color range picker dialog and update this row."""
        try:

            # Initial HSV values from current color (0-1 floats)
            h_f, s_f, v_f, _ = self.color.getHsvF()
            if h_f < 0:  # Handle grayscale case where hue may be -1
                h_f = 0.0

            initial_hsv = (h_f, s_f, v_f)

            # Initial ranges - use existing picker ranges if present, else derive from tolerance
            if self.hsv_ranges:
                initial_ranges = {
                    'h_minus': self.hsv_ranges.get('h_minus', 0.1),
                    'h_plus': self.hsv_ranges.get('h_plus', 0.1),
                    's_minus': self.hsv_ranges.get('s_minus', 0.2),
                    's_plus': self.hsv_ranges.get('s_plus', 0.2),
                    'v_minus': self.hsv_ranges.get('v_minus', 0.2),
                    'v_plus': self.hsv_ranges.get('v_plus', 0.2),
                }
            else:
                h_range, s_range, v_range = self.get_tolerance_values()
                initial_ranges = {
                    'h_minus': h_range / 179.0,
                    'h_plus': h_range / 179.0,
                    's_minus': s_range / 255.0,
                    's_plus': s_range / 255.0,
                    'v_minus': v_range / 255.0,
                    'v_plus': v_range / 255.0,
                }

            dialog = ColorRangeDialog(None, initial_hsv, initial_ranges, self)

            if dialog.exec() == ColorRangeDialog.Accepted:
                hsv_data = dialog.get_hsv_ranges()  # dict with h,s,v,h_minus,h_plus,...

                # Persist selected ranges and set mode
                self.hsv_ranges = hsv_data
                self.from_hsv_picker = True

                # Update color from HSV floats BEFORE applying mode visibility
                # Block signals to prevent _on_color_changed from clearing HSV ranges
                self.colorSwatch.blockSignals(True)
                self.color = QColor.fromHsvF(hsv_data['h'], hsv_data['s'], hsv_data['v'])
                self.colorSwatch.setColor(self.color)
                self.colorSwatch.blockSignals(False)

                # Now apply mode visibility and update display
                self._apply_mode_visibility()
                self._update_hsv_ranges_display()
                self.changed.emit()
        except Exception:
            # Intentionally swallow exceptions from dialog to avoid crashing the wizard
            pass

    def _on_color_changed(self, color):
        """Handle color swatch change."""
        self.color = color
        # If color is changed via swatch (not HSV picker), clear HSV ranges and switch to tolerance mode
        # This ensures RGB and HSV values stay in sync
        if self.from_hsv_picker:
            self.hsv_ranges = None
            self.from_hsv_picker = False
            self._apply_mode_visibility()
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
        # If color is set externally (not via HSV picker), clear HSV ranges to keep them in sync
        if self.from_hsv_picker:
            self.hsv_ranges = None
            self.from_hsv_picker = False
            self._apply_mode_visibility()
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

    def has_hsv_ranges(self):
        """Return True if this row has custom HSV ranges from the picker."""
        return self.from_hsv_picker and isinstance(self.hsv_ranges, dict)

    def get_hsv_ranges_fractional(self):
        """
        Get fractional HSV ranges dictionary.
        Returns a dict with keys: h_minus, h_plus, s_minus, s_plus, v_minus, v_plus, h, s, v
        """
        if self.has_hsv_ranges():
            return self.hsv_ranges
        # Derive symmetrical ranges from tolerance selection
        h_range, s_range, v_range = self.get_tolerance_values()
        h_f = max(0.0, min(1.0, self.color.getHsvF()[0] if self.color.getHsvF()[0] >= 0 else 0.0))
        s_f = max(0.0, min(1.0, self.color.getHsvF()[1]))
        v_f = max(0.0, min(1.0, self.color.getHsvF()[2]))

        # Convert to fractional
        # h_range is in OpenCV scale (0-179), convert to fractional
        h_minus_frac = h_range / 179.0
        h_plus_frac = h_range / 179.0
        # s_range and v_range are in OpenCV scale (0-255), convert to fractional (0-1)
        s_minus_frac = s_range / 255.0
        s_plus_frac = s_range / 255.0
        v_minus_frac = v_range / 255.0
        v_plus_frac = v_range / 255.0

        return {
            'h_minus': h_minus_frac,
            'h_plus': h_plus_frac,
            's_minus': s_minus_frac,
            's_plus': s_plus_frac,
            'v_minus': v_minus_frac,
            'v_plus': v_plus_frac,
            'h': h_f,
            's': s_f,
            'v': v_f,
        }

    def get_color_range(self):
        """Get the min and max HSV range as tuples based on tolerance."""
        r, g, b = self.color.red(), self.color.green(), self.color.blue()

        # Convert RGB to HSV (OpenCV format: H=0-179, S=0-255, V=0-255)
        hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

        # Get tolerance values
        h_range, s_range, v_range = self.get_tolerance_values()

        # Calculate min/max with clamping
        # h_range is in OpenCV scale (0-179)
        # s_range and v_range are PERCENTAGES (0-100), convert to OpenCV scale for calculation
        s_range_cv = int((s_range / 100.0) * s)  # Convert percentage to actual OpenCV value
        v_range_cv = int((v_range / 100.0) * v)  # Convert percentage to actual OpenCV value
        min_hsv = (max(0, h - h_range), max(0, s - s_range_cv), max(0, v - v_range_cv))
        max_hsv = (min(179, h + h_range), min(255, s + s_range_cv), min(255, v + v_range_cv))
        return min_hsv, max_hsv
