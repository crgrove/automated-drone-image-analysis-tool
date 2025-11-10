"""AOIFilterDialog - Dialog for filtering AOIs by color and pixel area."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QSlider, QSpinBox,
                               QCheckBox, QColorDialog, QLineEdit, QDoubleSpinBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import colorsys


class AOIFilterDialog(QDialog):
    """Dialog for setting color and pixel area filters for AOIs."""

    def __init__(self, parent, current_filters=None, temperature_unit='C', is_thermal=False):
        """Initialize the filter dialog.

        Args:
            parent: Parent widget
            current_filters: Dict with current filter settings {
                'color_hue': int (0-360) or None,
                'color_range': int (degrees) or None,
                'area_min': float or None,
                'area_max': float or None,
                'flagged_only': bool or None,
                'comment_filter': str or None,
                'temperature_min': float or None,
                'temperature_max': float or None
            }
            temperature_unit: Temperature unit ('F' or 'C') for display
            is_thermal: Whether dataset has thermal data
        """
        super().__init__(parent)

        # Initialize filter values
        if current_filters is None:
            current_filters = {}

        self.color_hue = current_filters.get('color_hue', None)
        self.color_range = current_filters.get('color_range', 30)
        self.area_min = current_filters.get('area_min', None)
        self.area_max = current_filters.get('area_max', None)
        self.flagged_only = current_filters.get('flagged_only', False)
        self.comment_filter = current_filters.get('comment_filter', None)
        self.temperature_min = current_filters.get('temperature_min', None)
        self.temperature_max = current_filters.get('temperature_max', None)
        self.temperature_unit = temperature_unit
        self.is_thermal = is_thermal

        self.setupUi()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Filter AOIs")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)

        # Main layout
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel("Filter Areas of Interest by flagged status, comments, color, and/or pixel area:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # ===== Flagged AOI Filter =====
        flagged_group = QGroupBox("Flagged AOIs")
        flagged_layout = QVBoxLayout()

        self.flagged_filter_enabled = QCheckBox("Show Only Flagged AOIs")
        self.flagged_filter_enabled.setChecked(self.flagged_only)
        flagged_layout.addWidget(self.flagged_filter_enabled)

        info_label = QLabel("Only AOIs marked with a flag will be displayed")
        info_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        flagged_layout.addWidget(info_label)

        flagged_group.setLayout(flagged_layout)
        layout.addWidget(flagged_group)

        # ===== Comment Filter Group =====
        comment_group = QGroupBox("Comment Filter")
        comment_layout = QVBoxLayout()

        # Enable comment filter checkbox
        self.comment_filter_enabled = QCheckBox("Enable Comment Filter")
        self.comment_filter_enabled.setChecked(self.comment_filter is not None and self.comment_filter != "")
        self.comment_filter_enabled.toggled.connect(self.on_comment_filter_toggled)
        comment_layout.addWidget(self.comment_filter_enabled)

        # Comment pattern input
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Pattern:"))

        self.comment_pattern_input = QLineEdit()
        self.comment_pattern_input.setPlaceholderText("e.g., *work* or crack* or *damage")
        if self.comment_filter:
            self.comment_pattern_input.setText(self.comment_filter)
        pattern_layout.addWidget(self.comment_pattern_input)

        comment_layout.addLayout(pattern_layout)

        # Info labels
        info_label1 = QLabel("Use * as wildcard for any characters (case-insensitive)")
        info_label1.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        comment_layout.addWidget(info_label1)

        info_label2 = QLabel("Only AOIs with non-empty comments matching the pattern will be shown")
        info_label2.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        comment_layout.addWidget(info_label2)

        comment_group.setLayout(comment_layout)
        layout.addWidget(comment_group)

        # ===== Color Filter Group =====
        color_group = QGroupBox("Color Filter")
        color_layout = QVBoxLayout()

        # Enable color filter checkbox
        self.color_filter_enabled = QCheckBox("Enable Color Filter")
        self.color_filter_enabled.setChecked(self.color_hue is not None)
        self.color_filter_enabled.toggled.connect(self.on_color_filter_toggled)
        color_layout.addWidget(self.color_filter_enabled)

        # Color selection button
        color_select_layout = QHBoxLayout()
        color_select_layout.addWidget(QLabel("Target Hue:"))

        self.color_button = QPushButton("Select Color")
        self.color_button.setFixedHeight(30)
        self.color_button.clicked.connect(self.select_color)
        color_select_layout.addWidget(self.color_button)

        # Color preview square
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet("QLabel { border: 1px solid gray; }")
        color_select_layout.addWidget(self.color_preview)

        # Hue value label
        self.hue_label = QLabel("No color selected")
        color_select_layout.addWidget(self.hue_label)
        color_select_layout.addStretch()

        color_layout.addLayout(color_select_layout)

        # Hue range slider
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Hue Range (±):"))

        self.range_slider = QSlider(Qt.Horizontal)
        self.range_slider.setMinimum(1)
        self.range_slider.setMaximum(180)
        self.range_slider.setValue(self.color_range)
        self.range_slider.setTickPosition(QSlider.TicksBelow)
        self.range_slider.setTickInterval(30)
        self.range_slider.valueChanged.connect(self.on_range_changed)
        range_layout.addWidget(self.range_slider)

        self.range_value_label = QLabel(f"{self.color_range}°")
        self.range_value_label.setMinimumWidth(40)
        range_layout.addWidget(self.range_value_label)

        color_layout.addLayout(range_layout)

        # Info label
        info_label = QLabel("AOIs with hue within ±range of target will be shown")
        info_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        color_layout.addWidget(info_label)

        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        # ===== Pixel Area Filter Group =====
        area_group = QGroupBox("Pixel Area Filter")
        area_layout = QVBoxLayout()

        # Enable area filter checkbox
        self.area_filter_enabled = QCheckBox("Enable Pixel Area Filter")
        self.area_filter_enabled.setChecked(self.area_min is not None or self.area_max is not None)
        self.area_filter_enabled.toggled.connect(self.on_area_filter_toggled)
        area_layout.addWidget(self.area_filter_enabled)

        # Min area
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("Minimum Area (px):"))

        self.min_area_spin = QSpinBox()
        self.min_area_spin.setMinimum(0)
        self.min_area_spin.setMaximum(1000000)
        self.min_area_spin.setValue(int(self.area_min) if self.area_min is not None else 0)
        self.min_area_spin.setSuffix(" px")
        min_layout.addWidget(self.min_area_spin)
        min_layout.addStretch()

        area_layout.addLayout(min_layout)

        # Max area
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Maximum Area (px):"))

        self.max_area_spin = QSpinBox()
        self.max_area_spin.setMinimum(0)
        self.max_area_spin.setMaximum(1000000)
        self.max_area_spin.setValue(int(self.area_max) if self.area_max is not None else 100000)
        self.max_area_spin.setSuffix(" px")
        max_layout.addWidget(self.max_area_spin)
        max_layout.addStretch()

        area_layout.addLayout(max_layout)

        area_group.setLayout(area_layout)
        layout.addWidget(area_group)

        # ===== Temperature Filter Group =====
        temp_group = QGroupBox("Temperature Filter")
        temp_layout = QVBoxLayout()

        # Enable temperature filter checkbox
        self.temperature_filter_enabled = QCheckBox("Enable Temperature Filter")
        self.temperature_filter_enabled.setChecked(self.temperature_min is not None or self.temperature_max is not None)
        self.temperature_filter_enabled.toggled.connect(self.on_temperature_filter_toggled)
        temp_layout.addWidget(self.temperature_filter_enabled)

        # Temperature unit suffix
        temp_suffix = f" °{self.temperature_unit}"

        # Min temperature
        min_temp_layout = QHBoxLayout()
        min_temp_layout.addWidget(QLabel(f"Minimum Temperature ({self.temperature_unit}):"))

        self.min_temp_spin = QDoubleSpinBox()
        self.min_temp_spin.setMinimum(-273.15 if self.temperature_unit == 'C' else -459.67)
        self.min_temp_spin.setMaximum(1000 if self.temperature_unit == 'C' else 1832)
        self.min_temp_spin.setDecimals(1)
        # Convert from Celsius to user's unit for display
        if self.temperature_min is not None:
            if self.temperature_unit == 'F':
                self.min_temp_spin.setValue(self.temperature_min * 1.8 + 32.0)
            else:
                self.min_temp_spin.setValue(self.temperature_min)
        else:
            self.min_temp_spin.setValue(-50 if self.temperature_unit == 'C' else -58)
        self.min_temp_spin.setSuffix(temp_suffix)
        min_temp_layout.addWidget(self.min_temp_spin)
        min_temp_layout.addStretch()

        temp_layout.addLayout(min_temp_layout)

        # Max temperature
        max_temp_layout = QHBoxLayout()
        max_temp_layout.addWidget(QLabel(f"Maximum Temperature ({self.temperature_unit}):"))

        self.max_temp_spin = QDoubleSpinBox()
        self.max_temp_spin.setMinimum(-273.15 if self.temperature_unit == 'C' else -459.67)
        self.max_temp_spin.setMaximum(1000 if self.temperature_unit == 'C' else 1832)
        self.max_temp_spin.setDecimals(1)
        # Convert from Celsius to user's unit for display
        if self.temperature_max is not None:
            if self.temperature_unit == 'F':
                self.max_temp_spin.setValue(self.temperature_max * 1.8 + 32.0)
            else:
                self.max_temp_spin.setValue(self.temperature_max)
        else:
            self.max_temp_spin.setValue(200 if self.temperature_unit == 'C' else 392)
        self.max_temp_spin.setSuffix(temp_suffix)
        max_temp_layout.addWidget(self.max_temp_spin)
        max_temp_layout.addStretch()

        temp_layout.addLayout(max_temp_layout)

        # Info label
        if not self.is_thermal:
            info_label = QLabel("Temperature filtering unavailable (no thermal data)")
            info_label.setStyleSheet("QLabel { color: #F44336; font-size: 9pt; font-weight: bold; }")
            temp_layout.addWidget(info_label)
            # Disable temperature filter controls
            self.temperature_filter_enabled.setEnabled(False)

        temp_group.setLayout(temp_layout)
        layout.addWidget(temp_group)

        # Spacer
        layout.addStretch()

        # ===== Buttons =====
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear All Filters")
        self.clear_button.clicked.connect(self.clear_all_filters)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()

        self.apply_button = QPushButton("Apply")
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Update initial UI state
        self.on_comment_filter_toggled(self.comment_filter_enabled.isChecked())
        self.on_color_filter_toggled(self.color_filter_enabled.isChecked())
        self.on_area_filter_toggled(self.area_filter_enabled.isChecked())
        self.on_temperature_filter_toggled(self.temperature_filter_enabled.isChecked())
        self.update_color_preview()

    def select_color(self):
        """Open color picker dialog."""
        # Create initial color from current hue if available
        initial_color = QColor(Qt.white)
        if self.color_hue is not None:
            # Convert hue to RGB for color dialog
            r, g, b = colorsys.hsv_to_rgb(self.color_hue / 360.0, 1.0, 1.0)
            initial_color = QColor(int(r * 255), int(g * 255), int(b * 255))

        # Open color dialog
        color = QColorDialog.getColor(initial_color, self, "Select Target Hue")

        if color.isValid():
            # Convert to HSV and extract hue
            h, s, v = color.getHsv()[0], color.getHsv()[1], color.getHsv()[2]
            # Qt hue is 0-359 (-1 for achromatic), we want 0-360
            if h == -1:
                h = 0
            self.color_hue = h
            self.update_color_preview()

    def update_color_preview(self):
        """Update the color preview square and label."""
        if self.color_hue is not None:
            # Create color from hue (full saturation and value)
            r, g, b = colorsys.hsv_to_rgb(self.color_hue / 360.0, 1.0, 1.0)
            self.color_preview.setStyleSheet(f"""
                QLabel {{
                    background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)});
                    border: 1px solid gray;
                }}
            """)
            self.hue_label.setText(f"Hue: {self.color_hue}°")
        else:
            self.color_preview.setStyleSheet("QLabel { background-color: white; border: 1px solid gray; }")
            self.hue_label.setText("No color selected")

    def on_range_changed(self, value):
        """Handle range slider changes."""
        self.color_range = value
        self.range_value_label.setText(f"{value}°")

    def on_color_filter_toggled(self, checked):
        """Enable/disable color filter controls."""
        self.color_button.setEnabled(checked)
        self.range_slider.setEnabled(checked)

    def on_area_filter_toggled(self, checked):
        """Enable/disable area filter controls."""
        self.min_area_spin.setEnabled(checked)
        self.max_area_spin.setEnabled(checked)

    def on_temperature_filter_toggled(self, checked):
        """Enable/disable temperature filter controls."""
        self.min_temp_spin.setEnabled(checked)
        self.max_temp_spin.setEnabled(checked)

    def on_comment_filter_toggled(self, checked):
        """Enable/disable comment filter controls."""
        self.comment_pattern_input.setEnabled(checked)

    def clear_all_filters(self):
        """Clear all filter settings."""
        self.flagged_filter_enabled.setChecked(False)
        self.comment_filter_enabled.setChecked(False)
        self.comment_pattern_input.clear()
        self.color_filter_enabled.setChecked(False)
        self.area_filter_enabled.setChecked(False)
        self.temperature_filter_enabled.setChecked(False)
        self.color_hue = None
        self.update_color_preview()

    def get_filters(self):
        """Get the current filter settings.

        Returns:
            dict: Filter settings {
                'flagged_only': bool,
                'comment_filter': str or None,
                'color_hue': int or None,
                'color_range': int or None,
                'area_min': float or None,
                'area_max': float or None,
                'temperature_min': float or None (in Celsius),
                'temperature_max': float or None (in Celsius)
            }
        """
        # Get comment filter pattern if enabled and not empty
        comment_pattern = None
        if self.comment_filter_enabled.isChecked():
            pattern_text = self.comment_pattern_input.text().strip()
            if pattern_text:
                comment_pattern = pattern_text

        # Get temperature filter values (convert to Celsius for internal storage)
        temp_min = None
        temp_max = None
        if self.temperature_filter_enabled.isChecked():
            temp_min_value = self.min_temp_spin.value()
            temp_max_value = self.max_temp_spin.value()
            # Convert from user's unit to Celsius
            if self.temperature_unit == 'F':
                temp_min = (temp_min_value - 32.0) / 1.8
                temp_max = (temp_max_value - 32.0) / 1.8
            else:
                temp_min = temp_min_value
                temp_max = temp_max_value

        filters = {
            'flagged_only': self.flagged_filter_enabled.isChecked(),
            'comment_filter': comment_pattern,
            'color_hue': self.color_hue if self.color_filter_enabled.isChecked() else None,
            'color_range': self.color_range if self.color_filter_enabled.isChecked() else None,
            'area_min': float(self.min_area_spin.value()) if self.area_filter_enabled.isChecked() else None,
            'area_max': float(self.max_area_spin.value()) if self.area_filter_enabled.isChecked() else None,
            'temperature_min': temp_min,
            'temperature_max': temp_max
        }
        return filters
