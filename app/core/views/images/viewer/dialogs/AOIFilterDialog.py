"""AOIFilterDialog - Dialog for filtering AOIs by color, pixel area, spatial density, and image mask."""

import colorsys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QSlider, QSpinBox,
                               QCheckBox, QColorDialog, QFileDialog, QLineEdit,
                               QDoubleSpinBox, QRadioButton, QButtonGroup, QFrame,
                               QMessageBox, QScrollArea, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from helpers.TranslationMixin import TranslationMixin


class AOIFilterDialog(TranslationMixin, QDialog):
    """Dialog for setting color, pixel area, and spatial density filters for AOIs."""

    def __init__(self, parent, current_filters=None, temperature_unit='C', is_thermal=False,
                 heatmap_available=False, heatmap_service=None):
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
                'temperature_max': float or None,
                'heatmap_mode': str ('off'/'filter'/'display') or None,
                'heatmap_threshold': int (0-100) or None
            }
            temperature_unit: Temperature unit ('F' or 'C') for display
            is_thermal: Whether dataset has thermal data
            heatmap_available: Whether heatmap data is available for filtering
            heatmap_service: HeatmapService instance (for the viewer dialog)
        """
        super().__init__(parent)

        # Initialize filter values
        if current_filters is None:
            current_filters = {}

        self.color_hue = current_filters.get('color_hue', None)
        self.color_range = current_filters.get('color_range', 30)
        self.color_filter_mode = current_filters.get('color_filter_mode', 'include')
        self.area_min = current_filters.get('area_min', None)
        self.area_max = current_filters.get('area_max', None)
        self.flagged_only = current_filters.get('flagged_only', False)
        self.comment_filter = current_filters.get('comment_filter', None)
        self.temperature_min = current_filters.get('temperature_min', None)
        self.temperature_max = current_filters.get('temperature_max', None)
        self.temperature_unit = temperature_unit
        self.is_thermal = is_thermal

        # Heatmap filter state
        self.heatmap_available = heatmap_available
        self.heatmap_service = heatmap_service
        self.heatmap_mode = current_filters.get('heatmap_mode', 'off')
        self.heatmap_threshold = current_filters.get('heatmap_threshold', 75)

        # Mask filter state
        self.mask_filter_path = current_filters.get('mask_filter_path', None)
        self.mask_filter_mode = current_filters.get('mask_filter_mode', 'include')

        self.setupUi()
        self._apply_translations()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle(self.tr("Filter AOIs"))
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)

        # Main layout
        outer_layout = QVBoxLayout()

        # Scroll area for filter content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        layout = QVBoxLayout(container)

        # Instructions
        instructions = QLabel(self.tr("Filter Areas of Interest by flagged status, comments, color, and/or pixel area:"))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # ===== Flagged AOI Filter =====
        flagged_group = QGroupBox(self.tr("Flagged AOIs"))
        flagged_layout = QVBoxLayout()

        self.flagged_filter_enabled = QCheckBox(self.tr("Show Only Flagged AOIs"))
        self.flagged_filter_enabled.setChecked(self.flagged_only)
        flagged_layout.addWidget(self.flagged_filter_enabled)

        info_label = QLabel(self.tr("Only AOIs marked with a flag will be displayed"))
        info_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        flagged_layout.addWidget(info_label)

        flagged_group.setLayout(flagged_layout)
        layout.addWidget(flagged_group)

        # ===== Comment Filter Group =====
        comment_group = QGroupBox(self.tr("Comment Filter"))
        comment_layout = QVBoxLayout()

        # Enable comment filter checkbox
        self.comment_filter_enabled = QCheckBox(self.tr("Enable Comment Filter"))
        self.comment_filter_enabled.setChecked(self.comment_filter is not None and self.comment_filter != "")
        self.comment_filter_enabled.toggled.connect(self.on_comment_filter_toggled)
        comment_layout.addWidget(self.comment_filter_enabled)

        # Comment pattern input
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel(self.tr("Pattern:")))

        self.comment_pattern_input = QLineEdit()
        self.comment_pattern_input.setPlaceholderText(self.tr("e.g., damage or crack"))
        if self.comment_filter:
            self.comment_pattern_input.setText(self.comment_filter)
        pattern_layout.addWidget(self.comment_pattern_input)

        comment_layout.addLayout(pattern_layout)

        # Info labels
        info_label1 = QLabel(self.tr("Case-insensitive substring match (e.g. \"blue\" matches \"blueface\")"))
        info_label1.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        comment_layout.addWidget(info_label1)

        info_label2 = QLabel(self.tr("Only AOIs with non-empty comments matching the pattern will be shown"))
        info_label2.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        comment_layout.addWidget(info_label2)

        comment_group.setLayout(comment_layout)
        layout.addWidget(comment_group)

        # ===== Color Filter Group =====
        color_group = QGroupBox(self.tr("Color Filter"))
        color_layout = QVBoxLayout()

        # Enable color filter checkbox
        self.color_filter_enabled = QCheckBox(self.tr("Enable Color Filter"))
        self.color_filter_enabled.setChecked(self.color_hue is not None)
        self.color_filter_enabled.toggled.connect(self.on_color_filter_toggled)
        color_layout.addWidget(self.color_filter_enabled)

        # Color filter mode radio buttons
        self.color_mode_group = QButtonGroup(self)
        self.color_include_radio = QRadioButton(self.tr("Show Only This Color"))
        self.color_exclude_radio = QRadioButton(self.tr("Exclude This Color"))
        self.color_mode_group.addButton(self.color_include_radio, 0)
        self.color_mode_group.addButton(self.color_exclude_radio, 1)

        if self.color_filter_mode == 'exclude':
            self.color_exclude_radio.setChecked(True)
        else:
            self.color_include_radio.setChecked(True)

        color_mode_layout = QHBoxLayout()
        color_mode_layout.addWidget(self.color_include_radio)
        color_mode_layout.addWidget(self.color_exclude_radio)
        color_mode_layout.addStretch()
        color_layout.addLayout(color_mode_layout)

        # Color selection button
        color_select_layout = QHBoxLayout()
        color_select_layout.addWidget(QLabel(self.tr("Target Hue:")))

        self.color_button = QPushButton(self.tr("Select Color"))
        self.color_button.setFixedHeight(30)
        self.color_button.clicked.connect(self.select_color)
        color_select_layout.addWidget(self.color_button)

        # Color preview square
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet("QLabel { border: 1px solid gray; }")
        color_select_layout.addWidget(self.color_preview)

        # Hue value label
        self.hue_label = QLabel(self.tr("No color selected"))
        color_select_layout.addWidget(self.hue_label)
        color_select_layout.addStretch()

        color_layout.addLayout(color_select_layout)

        # Hue range slider
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel(self.tr("Hue Range (±):")))

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
        info_label = QLabel(self.tr("AOIs with hue within ±range of target will be shown"))
        info_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        color_layout.addWidget(info_label)

        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        # ===== Pixel Area Filter Group =====
        area_group = QGroupBox(self.tr("Pixel Area Filter"))
        area_layout = QVBoxLayout()

        # Enable area filter checkbox
        self.area_filter_enabled = QCheckBox(self.tr("Enable Pixel Area Filter"))
        self.area_filter_enabled.setChecked(self.area_min is not None or self.area_max is not None)
        self.area_filter_enabled.toggled.connect(self.on_area_filter_toggled)
        area_layout.addWidget(self.area_filter_enabled)

        # Min area
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel(self.tr("Minimum Area (px):")))

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
        max_layout.addWidget(QLabel(self.tr("Maximum Area (px):")))

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
        temp_group = QGroupBox(self.tr("Temperature Filter"))
        temp_layout = QVBoxLayout()

        # Enable temperature filter checkbox
        self.temperature_filter_enabled = QCheckBox(self.tr("Enable Temperature Filter"))
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
            info_label = QLabel(self.tr("Temperature filtering unavailable (no thermal data)"))
            info_label.setStyleSheet("QLabel { color: #F44336; font-size: 9pt; font-weight: bold; }")
            temp_layout.addWidget(info_label)
            # Disable temperature filter controls
            self.temperature_filter_enabled.setEnabled(False)

        temp_group.setLayout(temp_layout)
        layout.addWidget(temp_group)

        # ===== Spatial Filters Separator =====
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        spatial_header = QLabel(self.tr("Spatial Filters"))
        spatial_header.setStyleSheet("QLabel { font-weight: bold; font-size: 10pt; }")
        layout.addWidget(spatial_header)

        # ===== Detection Density Heatmap Filter =====
        heatmap_group = QGroupBox(self.tr("Detection Density Heatmap"))
        heatmap_layout = QVBoxLayout()

        # Radio buttons for mode selection
        self.heatmap_mode_group = QButtonGroup(self)

        self.heatmap_off_radio = QRadioButton(self.tr("Off"))
        self.heatmap_filter_radio = QRadioButton(self.tr("Filter Hot Zones"))
        self.heatmap_display_radio = QRadioButton(self.tr("Show Hot Zones Only"))

        self.heatmap_mode_group.addButton(self.heatmap_off_radio, 0)
        self.heatmap_mode_group.addButton(self.heatmap_filter_radio, 1)
        self.heatmap_mode_group.addButton(self.heatmap_display_radio, 2)

        # Set current mode
        if self.heatmap_mode == 'filter':
            self.heatmap_filter_radio.setChecked(True)
        elif self.heatmap_mode == 'display':
            self.heatmap_display_radio.setChecked(True)
        else:
            self.heatmap_off_radio.setChecked(True)

        self.heatmap_mode_group.idClicked.connect(self.on_heatmap_mode_changed)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.heatmap_off_radio)
        mode_layout.addWidget(self.heatmap_filter_radio)
        mode_layout.addWidget(self.heatmap_display_radio)
        mode_layout.addStretch()
        heatmap_layout.addLayout(mode_layout)

        # Threshold slider
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel(self.tr("Threshold:")))

        self.heatmap_threshold_slider = QSlider(Qt.Horizontal)
        self.heatmap_threshold_slider.setMinimum(0)
        self.heatmap_threshold_slider.setMaximum(100)
        self.heatmap_threshold_slider.setValue(self.heatmap_threshold)
        self.heatmap_threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.heatmap_threshold_slider.setTickInterval(25)
        self.heatmap_threshold_slider.valueChanged.connect(self.on_heatmap_threshold_changed)
        threshold_layout.addWidget(self.heatmap_threshold_slider)

        self.heatmap_threshold_label = QLabel(f"{self.heatmap_threshold}%")
        self.heatmap_threshold_label.setMinimumWidth(40)
        threshold_layout.addWidget(self.heatmap_threshold_label)

        heatmap_layout.addLayout(threshold_layout)

        # View Heatmap button
        self.view_heatmap_button = QPushButton(self.tr("View Heatmap"))
        self.view_heatmap_button.clicked.connect(self.open_heatmap_viewer)
        heatmap_layout.addWidget(self.view_heatmap_button)

        # Info label for current mode
        self.heatmap_info_label = QLabel()
        self.heatmap_info_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        self.heatmap_info_label.setWordWrap(True)
        heatmap_layout.addWidget(self.heatmap_info_label)
        self._update_heatmap_info_label()

        # Unavailable message
        if not self.heatmap_available:
            unavail_label = QLabel(self.tr("Heatmap filtering unavailable (image dimensions not in dataset)"))
            unavail_label.setStyleSheet("QLabel { color: #F44336; font-size: 9pt; font-weight: bold; }")
            heatmap_layout.addWidget(unavail_label)
            # Disable mode radios and slider, but keep View Heatmap enabled
            self.heatmap_off_radio.setEnabled(False)
            self.heatmap_filter_radio.setEnabled(False)
            self.heatmap_display_radio.setEnabled(False)
            self.heatmap_threshold_slider.setEnabled(False)

        heatmap_group.setLayout(heatmap_layout)
        layout.addWidget(heatmap_group)

        # ===== Image Mask Filter =====
        mask_group = QGroupBox(self.tr("Image Mask Filter"))
        mask_layout = QVBoxLayout()

        # Enable mask filter checkbox
        self.mask_filter_enabled = QCheckBox(self.tr("Enable Image Mask Filter"))
        self.mask_filter_enabled.setChecked(self.mask_filter_path is not None)
        self.mask_filter_enabled.toggled.connect(self.on_mask_filter_toggled)
        mask_layout.addWidget(self.mask_filter_enabled)

        # Mask filter mode radio buttons
        self.mask_mode_group = QButtonGroup(self)
        self.mask_include_radio = QRadioButton(self.tr("Show Only Detections in Mask"))
        self.mask_exclude_radio = QRadioButton(self.tr("Exclude Detections in Mask"))
        self.mask_mode_group.addButton(self.mask_include_radio, 0)
        self.mask_mode_group.addButton(self.mask_exclude_radio, 1)

        if self.mask_filter_mode == 'exclude':
            self.mask_exclude_radio.setChecked(True)
        else:
            self.mask_include_radio.setChecked(True)

        mask_mode_layout = QHBoxLayout()
        mask_mode_layout.addWidget(self.mask_include_radio)
        mask_mode_layout.addWidget(self.mask_exclude_radio)
        mask_mode_layout.addStretch()
        mask_layout.addLayout(mask_mode_layout)

        # File selection row
        file_layout = QHBoxLayout()
        self.mask_path_display = QLineEdit()
        self.mask_path_display.setReadOnly(True)
        self.mask_path_display.setPlaceholderText(self.tr("No mask image selected"))
        if self.mask_filter_path:
            self.mask_path_display.setText(os.path.basename(self.mask_filter_path))
        file_layout.addWidget(self.mask_path_display)

        self.mask_browse_button = QPushButton(self.tr("Browse..."))
        self.mask_browse_button.clicked.connect(self.browse_mask_image)
        file_layout.addWidget(self.mask_browse_button)

        self.mask_clear_button = QPushButton(self.tr("Clear"))
        self.mask_clear_button.clicked.connect(self.clear_mask_image)
        file_layout.addWidget(self.mask_clear_button)

        mask_layout.addLayout(file_layout)

        # Info label
        mask_info = QLabel(self.tr("White regions = areas of interest. Mask is scaled to each image's dimensions."))
        mask_info.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        mask_info.setWordWrap(True)
        mask_layout.addWidget(mask_info)

        mask_group.setLayout(mask_layout)
        layout.addWidget(mask_group)

        # Spacer
        layout.addStretch()

        # Set container as scroll area content
        scroll_area.setWidget(container)
        outer_layout.addWidget(scroll_area)

        # ===== Buttons =====
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton(self.tr("Clear All Filters"))
        self.clear_button.clicked.connect(self.clear_all_filters)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()

        self.apply_button = QPushButton(self.tr("Apply"))
        self.apply_button.setDefault(True)
        self.apply_button.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        outer_layout.addLayout(button_layout)

        self.setLayout(outer_layout)

        # Update initial UI state
        self.on_comment_filter_toggled(self.comment_filter_enabled.isChecked())
        self.on_color_filter_toggled(self.color_filter_enabled.isChecked())
        self.on_area_filter_toggled(self.area_filter_enabled.isChecked())
        self.on_temperature_filter_toggled(self.temperature_filter_enabled.isChecked())
        self.on_heatmap_mode_changed(self.heatmap_mode_group.checkedId())
        self.on_mask_filter_toggled(self.mask_filter_enabled.isChecked())
        self.update_color_preview()

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, modal dialogs sometimes need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the comment pattern input if enabled, otherwise first enabled control
        if hasattr(self, 'comment_pattern_input') and self.comment_filter_enabled.isChecked():
            self.comment_pattern_input.setFocus()

    def select_color(self):
        """Open color picker dialog."""
        # Create initial color from current hue if available
        initial_color = QColor(Qt.white)
        if self.color_hue is not None:
            # Convert hue to RGB for color dialog
            r, g, b = colorsys.hsv_to_rgb(self.color_hue / 360.0, 1.0, 1.0)
            initial_color = QColor(int(r * 255), int(g * 255), int(b * 255))

        # Open color dialog
        color = QColorDialog.getColor(initial_color, self, self.tr("Select Target Hue"))

        if color.isValid():
            # Convert to HSV and extract hue
            h = color.getHsv()[0]
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
                    background-color: rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)});
                    border: 1px solid gray;
                }}
            """)
            self.hue_label.setText(f"Hue: {self.color_hue}°")
        else:
            self.color_preview.setStyleSheet("QLabel { background-color: white; border: 1px solid gray; }")
            self.hue_label.setText(self.tr("No color selected"))

    def on_range_changed(self, value):
        """Handle range slider changes."""
        self.color_range = value
        self.range_value_label.setText(f"{value}°")

    def on_color_filter_toggled(self, checked):
        """Enable/disable color filter controls."""
        self.color_button.setEnabled(checked)
        self.range_slider.setEnabled(checked)
        self.color_include_radio.setEnabled(checked)
        self.color_exclude_radio.setEnabled(checked)

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

    def on_heatmap_mode_changed(self, mode_id):
        """Handle heatmap mode radio button changes."""
        enabled = mode_id != 0  # Not "Off"
        self.heatmap_threshold_slider.setEnabled(enabled and self.heatmap_available)
        self._update_heatmap_info_label()

    def on_heatmap_threshold_changed(self, value):
        """Handle heatmap threshold slider changes."""
        self.heatmap_threshold = value
        self.heatmap_threshold_label.setText(f"{value}%")

    def on_mask_filter_toggled(self, checked):
        """Enable/disable mask filter controls."""
        self.mask_include_radio.setEnabled(checked)
        self.mask_exclude_radio.setEnabled(checked)
        self.mask_browse_button.setEnabled(checked)
        self.mask_clear_button.setEnabled(checked)
        self.mask_path_display.setEnabled(checked)

    def browse_mask_image(self):
        """Open file dialog to select a mask image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Mask Image"),
            "",
            self.tr("Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)")
        )

        if file_path:
            from core.services.streaming.MaskManager import MaskManager
            is_valid, error_msg, dimensions = MaskManager.validate_mask_image(file_path)

            if not is_valid:
                QMessageBox.warning(
                    self, self.tr("Invalid Image"),
                    error_msg or self.tr("Could not load the selected image. Please choose a valid image file.")
                )
                return

            self.mask_filter_path = file_path
            self.mask_path_display.setText(os.path.basename(file_path))

    def clear_mask_image(self):
        """Clear the selected mask image."""
        self.mask_filter_path = None
        self.mask_path_display.clear()
        self.mask_path_display.setPlaceholderText(self.tr("No mask image selected"))

    def _update_heatmap_info_label(self):
        """Update the heatmap info label based on current mode."""
        mode_id = self.heatmap_mode_group.checkedId()
        if mode_id == 1:
            self.heatmap_info_label.setText(
                self.tr("AOIs in high-density zones (above threshold) will be hidden"))
        elif mode_id == 2:
            self.heatmap_info_label.setText(
                self.tr("Only AOIs in high-density zones (above threshold) will be shown"))
        else:
            self.heatmap_info_label.setText(
                self.tr("Heatmap spatial filtering is disabled"))

    def open_heatmap_viewer(self):
        """Open the heatmap viewer dialog."""
        if self.heatmap_service is None or not self.heatmap_service.has_data():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("Heatmap"),
                                    self.tr("No heatmap data available. Ensure image dimensions are present in the dataset."))
            return

        from core.views.images.viewer.dialogs.HeatmapViewerDialog import HeatmapViewerDialog
        viewer = HeatmapViewerDialog(
            self, self.heatmap_service,
            currentThreshold=self.heatmap_threshold,
            currentGridSize=self.heatmap_service._gridSize
        )
        if viewer.exec():
            # Sync threshold back from viewer
            self.heatmap_threshold = viewer.get_threshold()
            self.heatmap_threshold_slider.setValue(self.heatmap_threshold)
            self.heatmap_threshold_label.setText(f"{self.heatmap_threshold}%")

    def clear_all_filters(self):
        """Clear all filter settings."""
        self.flagged_filter_enabled.setChecked(False)
        self.comment_filter_enabled.setChecked(False)
        self.comment_pattern_input.clear()
        self.color_filter_enabled.setChecked(False)
        self.area_filter_enabled.setChecked(False)
        self.temperature_filter_enabled.setChecked(False)
        self.color_hue = None
        self.color_include_radio.setChecked(True)
        self.update_color_preview()

        # Reset heatmap filter
        self.heatmap_off_radio.setChecked(True)
        self.heatmap_threshold = 75
        self.heatmap_threshold_slider.setValue(75)
        self.heatmap_threshold_label.setText("75%")
        self.on_heatmap_mode_changed(0)

        # Reset mask filter
        self.mask_filter_enabled.setChecked(False)
        self.mask_filter_path = None
        self.mask_filter_mode = 'include'
        self.mask_include_radio.setChecked(True)
        self.mask_path_display.clear()
        self.mask_path_display.setPlaceholderText(self.tr("No mask image selected"))
        self.on_mask_filter_toggled(False)

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
                'temperature_max': float or None (in Celsius),
                'heatmap_mode': str ('off', 'filter', or 'display'),
                'heatmap_threshold': int (0-100)
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

        # Get heatmap mode from radio buttons
        mode_id = self.heatmap_mode_group.checkedId()
        if mode_id == 1:
            heatmap_mode = 'filter'
        elif mode_id == 2:
            heatmap_mode = 'display'
        else:
            heatmap_mode = 'off'

        filters = {
            'flagged_only': self.flagged_filter_enabled.isChecked(),
            'comment_filter': comment_pattern,
            'color_hue': self.color_hue if self.color_filter_enabled.isChecked() else None,
            'color_range': self.color_range if self.color_filter_enabled.isChecked() else None,
            'color_filter_mode': 'exclude' if self.color_exclude_radio.isChecked() else 'include',
            'area_min': float(self.min_area_spin.value()) if self.area_filter_enabled.isChecked() else None,
            'area_max': float(self.max_area_spin.value()) if self.area_filter_enabled.isChecked() else None,
            'temperature_min': temp_min,
            'temperature_max': temp_max,
            'heatmap_mode': heatmap_mode,
            'heatmap_threshold': self.heatmap_threshold,
            'mask_filter_path': self.mask_filter_path if self.mask_filter_enabled.isChecked() else None,
            'mask_filter_mode': 'exclude' if self.mask_exclude_radio.isChecked() else 'include'
        }
        return filters
