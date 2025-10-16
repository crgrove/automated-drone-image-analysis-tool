"""
HSV Range Picker Widget - Qt5 implementation of advanced HSV color range selection

This widget provides a sophisticated interface for selecting HSV color ranges,
matching the functionality of the HTML mockup with interactive hue ring,
saturation/value square, and real-time range visualization.
"""

import sys
import math
from typing import Tuple, Optional

from PySide6.QtCore import Qt, QRect, QPoint, Signal, QSize
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QConicalGradient,
                           QLinearGradient, QPolygonF, QFont, QFontMetrics,
                           QPainterPath, QMouseEvent, QIcon)
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFrame, QGridLayout,
                               QSizePolicy, QColorDialog, QToolButton, QStyle)


class HSVRangePickerWidget(QWidget):
    """Advanced HSV color range picker with visual feedback."""

    # Signals emitted when values change
    colorChanged = Signal(float, float, float)  # h, s, v (0-1 range)
    rangeChanged = Signal(float, float, float, float, float, float)  # h-, h+, s-, s+, v-, v+

    def __init__(self, parent=None):
        super().__init__(parent)

        # HSV values (0-1 range)
        self.h = 0.0
        self.s = 0.5
        self.v = 1.0

        # Range values (0-1 range)
        self.h_minus = 20/360
        self.h_plus = 20/360
        self.s_minus = 0.2
        self.s_plus = 0.2
        self.v_minus = 0.2
        self.v_plus = 0.2

        # Widget dimensions
        self.hue_ring_size = 300
        self.sv_square_size = 300

        # Custom colors storage (16 slots like QColorDialog)
        self.custom_colors = [QColor(255, 255, 255) for _ in range(16)]

        # Initialize UI
        self.setup_ui()
        self.setMinimumSize(800, 750)

    def setup_ui(self):
        """Setup the main UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with hex input and reset
        header_layout = self.create_header()
        layout.addLayout(header_layout)

        # Main selector area
        selector_layout = self.create_selectors()
        layout.addLayout(selector_layout)

        # Additional color picker tools
        tools_layout = self.create_color_tools()
        layout.addLayout(tools_layout)

        # Info panel
        info_panel = self.create_info_panel()
        layout.addWidget(info_panel)

    def create_header(self):
        """Create header with hex input and reset button."""
        header_layout = QHBoxLayout()

        # Hex input
        hex_label = QLabel("HEX:")
        hex_label.setFont(QFont("Arial", 10, QFont.Bold))

        self.hex_input = QLineEdit("#FF0000")
        self.hex_input.setMaxLength(7)
        self.hex_input.setFixedWidth(120)
        self.hex_input.setFont(QFont("Courier", 10))
        self.hex_input.textChanged.connect(self.on_hex_changed)

        # Reset button
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self.reset_to_default)

        header_layout.addWidget(hex_label)
        header_layout.addWidget(self.hex_input)
        header_layout.addStretch()
        header_layout.addWidget(self.reset_button)

        return header_layout

    def create_selectors(self):
        """Create the main selector widgets."""
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(30)

        # SV Square section
        sv_layout = QVBoxLayout()
        sv_label = QLabel("Saturation / Value")
        sv_label.setAlignment(Qt.AlignCenter)
        sv_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.sv_widget = SVSquareWidget(self)
        self.sv_widget.setFixedSize(self.sv_square_size, self.sv_square_size)
        self.sv_widget.valueChanged.connect(self.on_sv_changed)

        sv_layout.addWidget(sv_label)
        sv_layout.addWidget(self.sv_widget)

        # Hue Ring section
        hue_layout = QVBoxLayout()
        hue_label = QLabel("Hue")
        hue_label.setAlignment(Qt.AlignCenter)
        hue_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.hue_widget = HueRingWidget(self)
        self.hue_widget.setFixedSize(self.hue_ring_size, self.hue_ring_size)
        self.hue_widget.valueChanged.connect(self.on_hue_changed)

        hue_layout.addWidget(hue_label)
        hue_layout.addWidget(self.hue_widget)

        selector_layout.addLayout(sv_layout)
        selector_layout.addLayout(hue_layout)

        return selector_layout

    def create_color_tools(self):
        """Create additional color picker tools section."""
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(15)

        # Buttons row
        buttons_layout = QHBoxLayout()

        # HSV Assistant button - now a regular button like "Pick Screen Color"
        self.hsv_assistant_button = QPushButton("Use Image")
        self.hsv_assistant_button.setFixedHeight(35)
        self.hsv_assistant_button.setToolTip("HSV Color Range Assistant - Click to select colors from image")
        self.hsv_assistant_button.clicked.connect(self.open_hsv_assistant)

        self.pick_screen_button = QPushButton("Pick Screen Color")
        self.pick_screen_button.setFixedHeight(35)
        self.pick_screen_button.clicked.connect(self.pick_screen_color)

        self.add_custom_button = QPushButton("Add to Custom Colors")
        self.add_custom_button.setFixedHeight(35)
        self.add_custom_button.clicked.connect(self.add_to_custom_colors)

        buttons_layout.addWidget(self.hsv_assistant_button)
        buttons_layout.addWidget(self.pick_screen_button)
        buttons_layout.addWidget(self.add_custom_button)
        buttons_layout.addStretch()

        tools_layout.addLayout(buttons_layout)

        # Basic Colors section
        basic_colors_layout = QVBoxLayout()
        basic_label = QLabel("Basic Colors:")
        basic_label.setFont(QFont("Arial", 10, QFont.Bold))
        basic_colors_layout.addWidget(basic_label)

        self.basic_colors_grid = self.create_basic_colors_grid()
        basic_colors_layout.addWidget(self.basic_colors_grid)

        # Custom Colors section
        custom_colors_layout = QVBoxLayout()
        custom_label = QLabel("Custom Colors:")
        custom_label.setFont(QFont("Arial", 10, QFont.Bold))
        custom_colors_layout.addWidget(custom_label)

        self.custom_colors_grid = self.create_custom_colors_grid()
        custom_colors_layout.addWidget(self.custom_colors_grid)

        # Side by side layout for color grids
        colors_layout = QHBoxLayout()
        colors_layout.addLayout(basic_colors_layout)
        colors_layout.addLayout(custom_colors_layout)
        colors_layout.addStretch()

        tools_layout.addLayout(colors_layout)

        return tools_layout

    def create_basic_colors_grid(self):
        """Create basic colors grid similar to QColorDialog."""
        basic_colors = [
            # Row 1
            QColor(255, 0, 0),    # Red
            QColor(255, 165, 0),  # Orange
            QColor(255, 255, 0),  # Yellow
            QColor(0, 255, 0),    # Green
            QColor(0, 255, 255),  # Cyan
            QColor(0, 0, 255),    # Blue
            QColor(128, 0, 128),  # Purple
            QColor(255, 0, 255),  # Magenta
            # Row 2
            QColor(192, 192, 192),  # Light Gray
            QColor(128, 128, 128),  # Gray
            QColor(128, 0, 0),     # Dark Red
            QColor(128, 128, 0),   # Olive
            QColor(0, 128, 0),     # Dark Green
            QColor(0, 128, 128),   # Teal
            QColor(0, 0, 128),     # Navy
            QColor(64, 64, 64),    # Dark Gray
        ]

        grid_widget = QFrame()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(2)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        for i, color in enumerate(basic_colors):
            row = i // 8
            col = i % 8
            color_button = self.create_color_button(color, is_custom=False)
            grid_layout.addWidget(color_button, row, col)

        return grid_widget

    def create_custom_colors_grid(self):
        """Create custom colors grid."""
        grid_widget = QFrame()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(2)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        for i in range(16):
            row = i // 8
            col = i % 8
            color_button = self.create_color_button(self.custom_colors[i], is_custom=True, custom_index=i)
            grid_layout.addWidget(color_button, row, col)

        return grid_widget

    def create_color_button(self, color, is_custom=False, custom_index=None):
        """Create a clickable color button."""
        button = QPushButton()
        button.setFixedSize(25, 25)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 1px solid #888;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                border: 2px solid #333;
            }}
        """)

        if is_custom:
            button.clicked.connect(lambda: self.select_custom_color(custom_index))
        else:
            button.clicked.connect(lambda: self.select_basic_color(color))

        return button

    def select_basic_color(self, color):
        """Select a basic color."""
        h, s, v = self.rgb_to_hsv(color.red(), color.green(), color.blue())
        self.set_hsv(h, s, v)

    def select_custom_color(self, index):
        """Select a custom color."""
        color = self.custom_colors[index]
        h, s, v = self.rgb_to_hsv(color.red(), color.green(), color.blue())
        self.set_hsv(h, s, v)

    def pick_screen_color(self):
        """Pick a color from the screen using QColorDialog."""
        # Use QColorDialog's built-in screen color picker
        color = QColorDialog.getColor(options=QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if color.isValid():
            h, s, v = self.rgb_to_hsv(color.red(), color.green(), color.blue())
            self.set_hsv(h, s, v)

    def add_to_custom_colors(self):
        """Add current color to the first available custom color slot."""
        current_rgb = self.hsv_to_rgb(self.h, self.s, self.v)
        current_color = QColor(*current_rgb)

        # Find first white (unused) slot or use slot 0
        slot_index = 0
        for i, color in enumerate(self.custom_colors):
            if color == QColor(255, 255, 255):
                slot_index = i
                break

        self.custom_colors[slot_index] = current_color
        self.update_custom_colors_grid()

    def open_hsv_assistant(self):
        """Open the HSV Color Range Assistant dialog."""
        from .HSVColorRangeAssistant import HSVColorRangeAssistant

        dialog = HSVColorRangeAssistant(self)
        dialog.rangeAccepted.connect(self.apply_hsv_assistant_ranges)
        dialog.exec()

    def apply_hsv_assistant_ranges(self, ranges):
        """Apply ranges from HSV Assistant."""
        # Extract values from ranges dict
        h_center = ranges['h_center'] / 179  # Convert from OpenCV to 0-1
        s_center = ranges['s_center'] / 255
        v_center = ranges['v_center'] / 255

        # Set center color
        self.h = h_center
        self.s = s_center
        self.v = v_center

        # Set ranges
        self.h_minus = ranges['h_minus']
        self.h_plus = ranges['h_plus']
        self.s_minus = ranges['s_minus']
        self.s_plus = ranges['s_plus']
        self.v_minus = ranges['v_minus']
        self.v_plus = ranges['v_plus']

        # Update display and check warnings
        self.update_display()
        self.emit_signals()

    def update_custom_colors_grid(self):
        """Update the custom colors grid display."""
        grid_layout = self.custom_colors_grid.layout()
        for i in range(16):
            row = i // 8
            col = i % 8
            # Remove old button
            old_button = grid_layout.itemAtPosition(row, col)
            if old_button:
                old_button.widget().setParent(None)
            # Add new button
            new_button = self.create_color_button(self.custom_colors[i], is_custom=True, custom_index=i)
            grid_layout.addWidget(new_button, row, col)

    def create_info_panel(self):
        """Create info panel showing current values."""
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel)
        info_frame.setStyleSheet("QFrame { background-color: #555555; border-radius: 8px; }")

        info_layout = QGridLayout(info_frame)
        info_layout.setContentsMargins(20, 15, 20, 15)

        # Labels
        labels = ["Center HSV:", "Hue Range:", "Sat Range:", "Val Range:"]
        self.info_labels = []
        self.warning_labels = []  # Store warning labels

        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            label.setStyleSheet("QLabel { color: white; }")

            value_label = QLabel()
            value_label.setFont(QFont("Courier", 10))
            value_label.setStyleSheet("QLabel { color: white; }")

            info_layout.addWidget(label, i, 0)
            info_layout.addWidget(value_label, i, 1)
            self.info_labels.append(value_label)

            # Add warning labels for Hue, Sat, and Val ranges (to the right)
            if i == 1:  # Hue Range
                self.h_warning_label = QLabel("⚠ Too wide!")
                self.h_warning_label.setStyleSheet("QLabel { color: yellow; font-size: 10px; font-weight: bold; }")
                self.h_warning_label.setVisible(False)
                self.h_warning_label.setAlignment(Qt.AlignLeft)
                info_layout.addWidget(self.h_warning_label, i, 2)
                self.warning_labels.append(self.h_warning_label)
            elif i == 2:  # Sat Range
                self.s_warning_label = QLabel("⚠ Too low!")
                self.s_warning_label.setStyleSheet("QLabel { color: yellow; font-size: 10px; font-weight: bold; }")
                self.s_warning_label.setVisible(False)
                self.s_warning_label.setAlignment(Qt.AlignLeft)
                info_layout.addWidget(self.s_warning_label, i, 2)
                self.warning_labels.append(self.s_warning_label)
            elif i == 3:  # Val Range
                self.v_warning_label = QLabel("⚠ Too low!")
                self.v_warning_label.setStyleSheet("QLabel { color: yellow; font-size: 10px; font-weight: bold; }")
                self.v_warning_label.setVisible(False)
                self.v_warning_label.setAlignment(Qt.AlignLeft)
                info_layout.addWidget(self.v_warning_label, i, 2)
                self.warning_labels.append(self.v_warning_label)

        info_layout.setColumnStretch(1, 0)  # Don't stretch column 1
        info_layout.setColumnStretch(2, 1)  # Stretch column 2 instead

        # Update initial values
        self.update_info_panel()

        return info_frame

    def on_hex_changed(self, hex_value):
        """Handle hex input changes."""
        if self.is_valid_hex(hex_value):
            rgb = self.hex_to_rgb(hex_value)
            if rgb:
                h, s, v = self.rgb_to_hsv(*rgb)
                self.set_hsv(h, s, v, update_hex=False)

    def on_sv_changed(self, s, v, s_minus, s_plus, v_minus, v_plus):
        """Handle SV widget changes."""
        self.s = s
        self.v = v
        self.s_minus = s_minus
        self.s_plus = s_plus
        self.v_minus = v_minus
        self.v_plus = v_plus
        self.update_display()
        self.emit_signals()

    def on_hue_changed(self, h, h_minus, h_plus):
        """Handle hue widget changes."""
        self.h = h
        self.h_minus = h_minus
        self.h_plus = h_plus
        self.update_display()
        self.emit_signals()

    def set_hsv(self, h, s, v, update_hex=True):
        """Set HSV values and update display."""
        self.h = max(0, min(1, h))
        self.s = max(0, min(1, s))
        self.v = max(0, min(1, v))

        if update_hex:
            rgb = self.hsv_to_rgb(self.h, self.s, self.v)
            hex_value = self.rgb_to_hex(*rgb)
            self.hex_input.setText(hex_value)

        self.update_display()
        self.emit_signals()

    def update_display(self):
        """Update all visual elements."""
        self.sv_widget.set_values(self.h, self.s, self.v,
                                  self.s_minus, self.s_plus,
                                  self.v_minus, self.v_plus)
        self.hue_widget.set_values(self.h, self.h_minus, self.h_plus)
        self.update_info_panel()

        # Update hex input to reflect current HSV values
        rgb = self.hsv_to_rgb(self.h, self.s, self.v)
        hex_value = self.rgb_to_hex(*rgb)
        self.hex_input.setText(hex_value)

    def update_info_panel(self):
        """Update info panel text."""
        if hasattr(self, 'info_labels') and self.info_labels:
            # Center HSV
            self.info_labels[0].setText(f"H: {int(self.h * 360)}°, S: {int(self.s * 100)}%, V: {int(self.v * 100)}%")

            # Ranges
            self.info_labels[1].setText(f"-{int(self.h_minus * 360)}° / +{int(self.h_plus * 360)}°")
            self.info_labels[2].setText(f"-{int(self.s_minus * 100)}% / +{int(self.s_plus * 100)}%")
            self.info_labels[3].setText(f"-{int(self.v_minus * 100)}% / +{int(self.v_plus * 100)}%")

            # Check and update warnings
            self.check_range_warnings()

    def check_range_warnings(self):
        """Check and display warning labels based on range values."""
        if not hasattr(self, 'h_warning_label'):
            return

        # Check Hue warning - if range is wider than 60 degrees total
        # Convert to degrees and check if total range is more than 60 degrees
        h_total_range_degrees = (self.h_minus + self.h_plus) * 360
        self.h_warning_label.setVisible(h_total_range_degrees > 60)

        # Check Saturation warning - if lower bound is in the bottom 25%
        s_low = max(0, self.s - self.s_minus)
        self.s_warning_label.setVisible(s_low < 0.25)

        # Check Value warning - if lower bound is in the bottom 25%
        v_low = max(0, self.v - self.v_minus)
        self.v_warning_label.setVisible(v_low < 0.25)

    def emit_signals(self):
        """Emit change signals."""
        self.colorChanged.emit(self.h, self.s, self.v)
        self.rangeChanged.emit(self.h_minus, self.h_plus,
                               self.s_minus, self.s_plus,
                               self.v_minus, self.v_plus)

    def reset_to_default(self):
        """Reset to default red color with standard ranges."""
        self.h_minus = self.h_plus = 20/360
        self.s_minus = self.s_plus = 0.2
        self.v_minus = self.v_plus = 0.2
        self.set_hsv(0, 1, 1)  # Pure red

    def get_hsv_ranges(self):
        """Get current HSV ranges in OpenCV format (0-179, 0-255, 0-255)."""
        h_center = int(self.h * 179)
        s_center = int(self.s * 255)
        v_center = int(self.v * 255)

        h_range = int(self.h_minus * 179), int(self.h_plus * 179)
        s_range = int(self.s_minus * 255), int(self.s_plus * 255)
        v_range = int(self.v_minus * 255), int(self.v_plus * 255)

        return {
            'center': (h_center, s_center, v_center),
            'ranges': (h_range, s_range, v_range)
        }

    # Color conversion utilities
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB (0-255 range)."""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    def rgb_to_hsv(self, r, g, b):
        """Convert RGB to HSV (0-1 range)."""
        import colorsys
        return colorsys.rgb_to_hsv(r/255, g/255, b/255)

    def rgb_to_hex(self, r, g, b):
        """Convert RGB to hex string."""
        return f"#{r:02X}{g:02X}{b:02X}"

    def hex_to_rgb(self, hex_value):
        """Convert hex string to RGB tuple."""
        try:
            hex_value = hex_value.lstrip('#')
            if len(hex_value) == 3:
                hex_value = ''.join([c*2 for c in hex_value])
            if len(hex_value) == 6:
                return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, TypeError):
            pass
        return None

    def is_valid_hex(self, hex_value):
        """Check if hex string is valid."""
        import re
        return bool(re.match(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', hex_value))


class SVSquareWidget(QWidget):
    """Saturation/Value square selector with range visualization."""

    valueChanged = Signal(float, float, float, float, float, float)  # s, v, s-, s+, v-, v+

    def __init__(self, parent=None):
        super().__init__(parent)
        self.h = 0.0
        self.s = 0.5
        self.v = 1.0
        self.s_minus = 0.2
        self.s_plus = 0.2
        self.v_minus = 0.2
        self.v_plus = 0.2

        self.dragging = False
        self.drag_corner = None
        self.setMouseTracking(True)

    def set_values(self, h, s, v, s_minus, s_plus, v_minus, v_plus):
        """Update values and repaint."""
        self.h = h
        self.s = s
        self.v = v
        self.s_minus = s_minus
        self.s_plus = s_plus
        self.v_minus = v_minus
        self.v_plus = v_plus
        self.update()

    def paintEvent(self, event):
        """Paint the SV square with gradients and range box."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)

        # Draw SV gradient
        self.draw_sv_gradient(painter, rect)

        # Draw range box
        self.draw_range_box(painter, rect)

        # Draw center point
        self.draw_center_point(painter, rect)

    def draw_sv_gradient(self, painter, rect):
        """Draw the saturation/value gradient background."""
        # Create the base hue color
        base_color = QColor.fromHsvF(self.h, 1.0, 1.0)

        # Draw horizontal gradient (saturation)
        h_gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
        h_gradient.setColorAt(0, QColor(255, 255, 255))  # White
        h_gradient.setColorAt(1, base_color)

        painter.fillRect(rect, QBrush(h_gradient))

        # Draw vertical gradient (value/brightness)
        v_gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        v_gradient.setColorAt(0, QColor(0, 0, 0, 0))  # Transparent
        v_gradient.setColorAt(1, QColor(0, 0, 0, 255))  # Black

        painter.fillRect(rect, QBrush(v_gradient))

        # Draw border
        painter.setPen(QPen(QColor(224, 224, 224), 2))
        painter.drawRect(rect)

    def draw_range_box(self, painter, rect):
        """Draw the range selection box."""
        # Calculate range box dimensions
        # S is horizontal (X-axis): 0 at left, 1 at right
        # V is vertical (Y-axis): 0 at bottom, 1 at top
        center_x = rect.left() + self.s * rect.width()
        center_y = rect.top() + (1 - self.v) * rect.height()

        left = center_x - self.s_minus * rect.width()
        right = center_x + self.s_plus * rect.width()
        top = center_y - self.v_plus * rect.height()
        bottom = center_y + self.v_minus * rect.height()

        # Clamp to widget bounds
        left = max(rect.left(), left)
        right = min(rect.right(), right)
        top = max(rect.top(), top)
        bottom = min(rect.bottom(), bottom)

        range_rect = QRect(int(left), int(top), int(right - left), int(bottom - top))

        # Draw range box
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255, 25)))
        painter.drawRect(range_rect)

        # Draw corner handles
        handle_size = 12
        handles = [
            (range_rect.topLeft(), "tl"),
            (range_rect.topRight(), "tr"),
            (range_rect.bottomLeft(), "bl"),
            (range_rect.bottomRight(), "br")
        ]

        painter.setPen(QPen(QColor(51, 51, 51), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))

        for pos, _ in handles:
            handle_rect = QRect(pos.x() - handle_size//2, pos.y() - handle_size//2,
                                handle_size, handle_size)
            painter.drawEllipse(handle_rect)

    def draw_center_point(self, painter, rect):
        """Draw the center point marker."""
        # S is horizontal (X-axis): 0 at left, 1 at right
        # V is vertical (Y-axis): 0 at bottom, 1 at top
        center_x = rect.left() + self.s * rect.width()
        center_y = rect.top() + (1 - self.v) * rect.height()

        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.setBrush(QBrush())
        painter.drawEllipse(QPoint(int(center_x), int(center_y)), 10, 10)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_corner = self.get_handle_at_pos(event.pos())
            if not self.drag_corner:
                self.update_sv_from_pos(event.pos())

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.dragging:
            if self.drag_corner:
                self.drag_corner_handle(self.drag_corner, event.pos())
            else:
                self.update_sv_from_pos(event.pos())

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        self.dragging = False
        self.drag_corner = None

    def get_handle_at_pos(self, pos):
        """Check if position is over a corner handle."""
        rect = self.rect().adjusted(10, 10, -10, -10)
        # S is horizontal (X-axis): 0 at left, 1 at right
        # V is vertical (Y-axis): 0 at bottom, 1 at top
        center_x = rect.left() + self.s * rect.width()
        center_y = rect.top() + (1 - self.v) * rect.height()

        left = center_x - self.s_minus * rect.width()
        right = center_x + self.s_plus * rect.width()
        top = center_y - self.v_plus * rect.height()
        bottom = center_y + self.v_minus * rect.height()

        handles = {
            "tl": QPoint(int(left), int(top)),
            "tr": QPoint(int(right), int(top)),
            "bl": QPoint(int(left), int(bottom)),
            "br": QPoint(int(right), int(bottom))
        }

        for handle_id, handle_pos in handles.items():
            if (pos - handle_pos).manhattanLength() < 15:
                return handle_id

        return None

    def update_sv_from_pos(self, pos):
        """Update S/V values from mouse position."""
        rect = self.rect().adjusted(10, 10, -10, -10)

        if rect.contains(pos):
            # S is horizontal (X-axis): 0 at left, 1 at right
            # V is vertical (Y-axis): 0 at bottom, 1 at top
            self.s = max(0, min(1, (pos.x() - rect.left()) / rect.width()))
            self.v = max(0, min(1, 1 - (pos.y() - rect.top()) / rect.height()))

            self.update()
            self.valueChanged.emit(self.s, self.v, self.s_minus, self.s_plus,
                                   self.v_minus, self.v_plus)

    def drag_corner_handle(self, corner, pos):
        """Drag a corner handle to adjust ranges."""
        rect = self.rect().adjusted(10, 10, -10, -10)
        # S is horizontal (X-axis): 0 at left, 1 at right
        # V is vertical (Y-axis): 0 at bottom, 1 at top
        center_x = rect.left() + self.s * rect.width()
        center_y = rect.top() + (1 - self.v) * rect.height()

        if corner in ["tl", "bl"]:  # Left handles
            # Calculate the desired s_minus (unconstrained)
            desired_s_minus = (center_x - pos.x()) / rect.width()
            # Don't constrain - allow full range
            new_s_minus = max(0, min(1.0, desired_s_minus))
            self.s_minus = new_s_minus

        if corner in ["tr", "br"]:  # Right handles
            # Calculate the desired s_plus (unconstrained)
            desired_s_plus = (pos.x() - center_x) / rect.width()
            # Don't constrain - allow full range
            new_s_plus = max(0, min(1.0, desired_s_plus))
            self.s_plus = new_s_plus

        if corner in ["tl", "tr"]:  # Top handles
            # Calculate the desired v_plus (unconstrained)
            desired_v_plus = (center_y - pos.y()) / rect.height()
            # Don't constrain - allow full range
            new_v_plus = max(0, min(1.0, desired_v_plus))
            self.v_plus = new_v_plus

        if corner in ["bl", "br"]:  # Bottom handles
            # Calculate the desired v_minus (unconstrained)
            desired_v_minus = (pos.y() - center_y) / rect.height()
            # Don't constrain - allow full range
            new_v_minus = max(0, min(1.0, desired_v_minus))
            self.v_minus = new_v_minus

        self.update()
        self.valueChanged.emit(self.s, self.v, self.s_minus, self.s_plus,
                               self.v_minus, self.v_plus)


class HueRingWidget(QWidget):
    """Hue ring selector with range visualization."""

    valueChanged = Signal(float, float, float)  # h, h_minus, h_plus

    def __init__(self, parent=None):
        super().__init__(parent)
        self.h = 0.0
        self.h_minus = 20/360
        self.h_plus = 20/360

        self.dragging_hue = False
        self.dragging_left = False
        self.dragging_right = False

        self.setMouseTracking(True)

    def set_values(self, h, h_minus, h_plus):
        """Update values and repaint."""
        self.h = h
        self.h_minus = h_minus
        self.h_plus = h_plus
        self.update()

    def paintEvent(self, event):
        """Paint the hue ring with range indicators."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.rect().center()
        size = min(self.width(), self.height()) - 20
        outer_radius = size * 0.4
        inner_radius = size * 0.27
        handle_radius = size * 0.33

        # Draw hue ring
        self.draw_hue_ring(painter, center, outer_radius, inner_radius)

        # Draw range indicators
        self.draw_range_indicators(painter, center, outer_radius, inner_radius)

        # Draw center line and handles
        self.draw_handles(painter, center, outer_radius, inner_radius, handle_radius)

    def draw_hue_ring(self, painter, center, outer_radius, inner_radius):
        """Draw the colorful hue ring."""
        # Convert to integers for QRect
        outer_radius = int(outer_radius)
        inner_radius = int(inner_radius)

        for degree in range(360):
            # Original working code - hue colors will be upside down but handles work
            color = QColor.fromHsv(degree, 255, 255)

            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))

            # Create arc path using QRectF for floating point precision
            outer_rect = QRectF(center.x() - outer_radius, center.y() - outer_radius,
                                outer_radius * 2, outer_radius * 2)
            inner_rect = QRectF(center.x() - inner_radius, center.y() - inner_radius,
                                inner_radius * 2, inner_radius * 2)

            path = QPainterPath()
            path.arcMoveTo(outer_rect, degree - 90)
            path.arcTo(outer_rect, degree - 90, 1)
            path.arcTo(inner_rect, degree - 89, -1)
            path.closeSubpath()

            painter.fillPath(path, color)

    def draw_range_indicators(self, painter, center, outer_radius, inner_radius):
        """Draw the range selection indicators."""
        # Convert to integers
        outer_radius = int(outer_radius)
        inner_radius = int(inner_radius)

        # Original working coordinate system
        start_angle = (self.h - self.h_minus) * 360 - 90
        end_angle = (self.h + self.h_plus) * 360 - 90

        painter.setPen(QPen(QColor(204, 204, 204), 4))

        # Draw outer arc
        outer_rect = QRect(center.x() - outer_radius - 4, center.y() - outer_radius - 4,
                           (outer_radius + 4) * 2, (outer_radius + 4) * 2)
        painter.drawArc(outer_rect, int(start_angle * 16), int((end_angle - start_angle) * 16))

        # Draw inner arc
        inner_rect = QRect(center.x() - inner_radius + 4, center.y() - inner_radius + 4,
                           (inner_radius - 4) * 2, (inner_radius - 4) * 2)
        painter.drawArc(inner_rect, int(start_angle * 16), int((end_angle - start_angle) * 16))

        # Draw radial lines
        for angle in [start_angle, end_angle]:
            rad = math.radians(angle)
            start_point = QPoint(int(center.x() + (inner_radius - 4) * math.cos(rad)),
                                 int(center.y() - (inner_radius - 4) * math.sin(rad)))  # Negative sin for Qt coordinate system
            end_point = QPoint(int(center.x() + (outer_radius + 4) * math.cos(rad)),
                               int(center.y() - (outer_radius + 4) * math.sin(rad)))    # Negative sin for Qt coordinate system
            painter.drawLine(start_point, end_point)

    def draw_handles(self, painter, center, outer_radius, inner_radius, handle_radius):
        """Draw center line and range handles."""
        # Convert to integers
        outer_radius = int(outer_radius)
        inner_radius = int(inner_radius)
        handle_radius = int(handle_radius)

        # Center line - original working coordinate system
        line_angle = self.h * 360 - 90
        line_rad = math.radians(line_angle)

        start_point = QPoint(int(center.x() + inner_radius * math.cos(line_rad)),
                             int(center.y() - inner_radius * math.sin(line_rad)))  # Negative sin for Qt coords
        end_point = QPoint(int(center.x() + outer_radius * math.cos(line_rad)),
                           int(center.y() - outer_radius * math.sin(line_rad)))   # Negative sin for Qt coords

        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawLine(start_point, end_point)

        # Range handles - original working coordinate system
        left_angle = (self.h - self.h_minus) * 360 - 90
        right_angle = (self.h + self.h_plus) * 360 - 90

        for angle in [left_angle, right_angle]:
            rad = math.radians(angle)
            handle_center = QPoint(int(center.x() + handle_radius * math.cos(rad)),
                                   int(center.y() - handle_radius * math.sin(rad)))  # Negative sin for Qt coords

            painter.setPen(QPen(QColor(51, 51, 51), 2))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(handle_center, 10, 10)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            center = self.rect().center()

            # Check which element was clicked
            dx = pos.x() - center.x()
            dy = pos.y() - center.y()
            distance = math.sqrt(dx*dx + dy*dy)

            size = min(self.width(), self.height()) - 20
            outer_radius = size * 0.4
            inner_radius = size * 0.27
            handle_radius = size * 0.33

            # Check handle clicks - original working coordinate system
            left_angle = math.radians((self.h - self.h_minus) * 360 - 90)
            right_angle = math.radians((self.h + self.h_plus) * 360 - 90)

            left_handle = QPoint(int(center.x() + handle_radius * math.cos(left_angle)),
                                 int(center.y() - handle_radius * math.sin(left_angle)))   # Negative sin for Qt coords
            right_handle = QPoint(int(center.x() + handle_radius * math.cos(right_angle)),
                                  int(center.y() - handle_radius * math.sin(right_angle)))  # Negative sin for Qt coords

            if (pos - left_handle).manhattanLength() < 15:
                self.dragging_left = True
            elif (pos - right_handle).manhattanLength() < 15:
                self.dragging_right = True
            elif inner_radius < distance < outer_radius:
                self.dragging_hue = True
                self.update_hue_from_pos(pos)

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.dragging_hue or self.dragging_left or self.dragging_right:
            self.update_hue_from_pos(event.pos())

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        self.dragging_hue = False
        self.dragging_left = False
        self.dragging_right = False

    def update_hue_from_pos(self, pos):
        """Update hue value from mouse position."""
        center = self.rect().center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()

        # Calculate angle from mouse position
        # We need to match our new drawing coordinate system where:
        # - Red (hue 0°) is at 12 o'clock (top)
        # - Drawing uses: qt_angle = (-hue_degrees + 90) % 360
        # So we need to reverse this: hue_degrees = (90 - qt_angle) % 360

        # First get Qt angle (0° = right, positive clockwise)
        qt_angle = math.atan2(dy, dx)  # Qt coordinate system
        qt_angle_degrees = math.degrees(qt_angle)

        # Convert Qt angle back to hue degrees (reverse of drawing conversion)
        hue_degrees = (90 - qt_angle_degrees) % 360

        # Normalize to 0-1 range
        normalized_angle = hue_degrees / 360.0

        EPS = 1e-3

        if self.dragging_hue:
            self.h = normalized_angle
        elif self.dragging_left:
            clockwise_gap = (self.h - normalized_angle + 1) % 1
            clockwise_gap = min(clockwise_gap, 1 - EPS)
            self.h_minus = min(1 - self.h_plus - EPS, clockwise_gap)
        elif self.dragging_right:
            counter_clockwise_gap = (normalized_angle - self.h + 1) % 1
            counter_clockwise_gap = min(counter_clockwise_gap, 1 - EPS)
            self.h_plus = min(1 - self.h_minus - EPS, counter_clockwise_gap)

        self.update()
        self.valueChanged.emit(self.h, self.h_minus, self.h_plus)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = HSVRangePickerWidget()
    widget.show()

    sys.exit(app.exec())
