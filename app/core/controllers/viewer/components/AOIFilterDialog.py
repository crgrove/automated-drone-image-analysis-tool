"""AOIFilterDialog - Dialog for filtering AOIs by color and pixel area."""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QSlider, QSpinBox,
                               QCheckBox, QColorDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import colorsys


class AOIFilterDialog(QDialog):
    """Dialog for setting color and pixel area filters for AOIs."""

    def __init__(self, parent, current_filters=None):
        """Initialize the filter dialog.

        Args:
            parent: Parent widget
            current_filters: Dict with current filter settings {
                'color_hue': int (0-360) or None,
                'color_range': int (degrees) or None,
                'area_min': float or None,
                'area_max': float or None,
                'flagged_only': bool or None
            }
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
        instructions = QLabel("Filter Areas of Interest by flagged status, color, and/or pixel area:")
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
        self.on_color_filter_toggled(self.color_filter_enabled.isChecked())
        self.on_area_filter_toggled(self.area_filter_enabled.isChecked())
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

    def clear_all_filters(self):
        """Clear all filter settings."""
        self.flagged_filter_enabled.setChecked(False)
        self.color_filter_enabled.setChecked(False)
        self.area_filter_enabled.setChecked(False)
        self.color_hue = None
        self.update_color_preview()

    def get_filters(self):
        """Get the current filter settings.

        Returns:
            dict: Filter settings {
                'flagged_only': bool,
                'color_hue': int or None,
                'color_range': int or None,
                'area_min': float or None,
                'area_max': float or None
            }
        """
        filters = {
            'flagged_only': self.flagged_filter_enabled.isChecked(),
            'color_hue': self.color_hue if self.color_filter_enabled.isChecked() else None,
            'color_range': self.color_range if self.color_filter_enabled.isChecked() else None,
            'area_min': float(self.min_area_spin.value()) if self.area_filter_enabled.isChecked() else None,
            'area_max': float(self.max_area_spin.value()) if self.area_filter_enabled.isChecked() else None
        }
        return filters
