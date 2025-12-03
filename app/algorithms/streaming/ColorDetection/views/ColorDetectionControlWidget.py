"""
ColorDetectionControlWidget.py - Control widget for color detection parameters.

This widget provides a tabbed interface for configuring all ColorDetectionService
parameters. It matches the ColorAnomalyAndMotionDetection UI structure.
"""

from typing import Dict, Any, List, Tuple, Optional
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QDoubleSpinBox, QCheckBox,
                               QComboBox, QGroupBox, QPushButton, QListWidget, QListWidgetItem,
                               QScrollArea, QDialog)
from PySide6.QtGui import QColor

from core.services.LoggerService import LoggerService
from core.views.streaming.components import InputProcessingTab, RenderingTab
from algorithms.streaming.ColorDetection.views.HSVControlWidget_ui import Ui_HSVControlWidget
from algorithms.Shared.views import HSVColorRowWidget, ColorRangeDialog
from algorithms.Shared.views.HSVColorRangeRangeViewer import HSVColorRangeRangeViewer


class ColorDetectionControlWidget(QWidget, Ui_HSVControlWidget):
    """Control widget for color detection parameters."""

    configChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Multiple color range support
        self.color_ranges = []
        self.current_range_index = 0
        self.color_range_widgets = []  # Store row widgets

        # Setup UI from UI file
        self.setupUi(self)

        # Get tab widget reference
        self.tabs = self.tabs  # From Ui_HSVControlWidget

        # Populate tabs with actual controls
        self._populate_tabs()

        # Connect signals
        self.connect_signals()

    def _populate_tabs(self):
        """Populate tabs with control panels."""
        # Clear placeholder tabs
        self.tabs.clear()

        # Use shared tabs for Input & Processing and Rendering
        self.input_processing_tab = InputProcessingTab()
        self.rendering_tab = RenderingTab(show_detection_color_option=True)
        self.tabs.addTab(self._create_color_selection_tab(), "Color Selection")
        self.tabs.addTab(self._create_detection_tab(), "Detection")
        self.tabs.addTab(self.input_processing_tab, "Input & Processing")
        self.tabs.addTab(self.rendering_tab, "Rendering")

    def _create_color_selection_tab(self) -> QWidget:
        """Create color selection tab matching screenshot - inline editing with HSV ranges."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Top buttons
        btn_layout = QHBoxLayout()
        self.add_color_btn = QPushButton("Add Color")
        self.add_color_btn.setToolTip("Add a new color range to detect.\n"
                                      "Opens a color picker dialog where you can select a color\n"
                                      "and configure its HSV tolerance ranges.\n"
                                      "You can add multiple color ranges to detect different colors simultaneously.")
        btn_layout.addWidget(self.add_color_btn)

        btn_layout.addStretch()

        self.view_range_btn = QPushButton("View Range")
        self.view_range_btn.setToolTip("View HSV color ranges for all configured colors.\n"
                                       "Opens a viewer dialog for each color range showing\n"
                                       "the hue, saturation, and value ranges that will be detected.\n"
                                       "Useful for understanding and fine-tuning multi-color detection.")
        btn_layout.addWidget(self.view_range_btn)
        layout.addLayout(btn_layout)

        # Scroll area for color ranges
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.color_ranges_container = QWidget()
        self.color_ranges_layout = QVBoxLayout(self.color_ranges_container)
        self.color_ranges_layout.setContentsMargins(0, 0, 0, 0)
        self.color_ranges_layout.setSpacing(5)
        self.color_ranges_layout.addStretch()

        scroll.setWidget(self.color_ranges_container)
        layout.addWidget(scroll)

        # Store row widgets
        self.color_range_widgets = []

        # Update display
        self._update_color_ranges_display()

        return widget

    def _create_detection_tab(self) -> QWidget:
        """Create detection parameters tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 160)
        grid.setColumnStretch(1, 1)

        grid.addWidget(QLabel("Min Object Area (px):"), 0, 0)
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setRange(10, 50000)
        self.min_area_spinbox.setValue(10)
        self.min_area_spinbox.setToolTip("Minimum detection area in pixels (10-50000).\n"
                                         "Filters out very small detections (noise, small objects, fragments).\n"
                                         "Lower values = detect smaller objects, more detections, more noise.\n"
                                         "Higher values = only large objects, fewer detections, less noise.\n"
                                         "Recommended: 100 for general use, 50 for small objects, 200-500 for large objects.")
        grid.addWidget(self.min_area_spinbox, 0, 1)

        grid.addWidget(QLabel("Max Object Area (px):"), 1, 0)
        self.max_area_spinbox = QSpinBox()
        self.max_area_spinbox.setRange(100, 500000)
        self.max_area_spinbox.setValue(100000)
        self.max_area_spinbox.setToolTip("Maximum detection area in pixels (100-500000).\n"
                                         "Filters out very large detections (shadows, lighting changes, entire scene).\n"
                                         "Lower values = only small/medium objects.\n"
                                         "Higher values = allow large objects, may include unwanted large regions.\n"
                                         "Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects.")
        grid.addWidget(self.max_area_spinbox, 1, 1)

        grid.addWidget(QLabel("Confidence Threshold:"), 2, 0)
        self.confidence_spinbox = QDoubleSpinBox()
        self.confidence_spinbox.setRange(0.0, 1.0)
        self.confidence_spinbox.setSingleStep(0.05)
        self.confidence_spinbox.setValue(0.5)
        self.confidence_spinbox.setToolTip("Minimum confidence score to accept a detection (0.0-1.0).\n"
                                           "Confidence is calculated from:\n"
                                           "• Size score: area relative to max area\n"
                                           "• Shape score: solidity (how compact/regular the shape is)\n"
                                           "• Final: average of both scores\n\n"
                                           "Lower values (0.0-0.3) = accept more detections, including weak/fragmented ones.\n"
                                           "Higher values (0.7-1.0) = only high-quality detections, well-formed shapes.\n"
                                           "Recommended: 0.5 for balanced filtering, 0.3 for more detections, 0.7 for strict quality.")
        grid.addWidget(self.confidence_spinbox, 2, 1)

        layout.addLayout(grid)
        layout.addStretch()

        return widget

    def connect_signals(self):
        """Connect all control signals."""
        # Input & Processing (from shared InputProcessingTab)
        self.input_processing_tab.resolution_preset.currentTextChanged.connect(
            self.input_processing_tab.on_resolution_preset_changed)
        self.input_processing_tab.resolution_preset.currentTextChanged.connect(self._emit_config_changed)
        self.input_processing_tab.processing_width.valueChanged.connect(self._emit_config_changed)
        self.input_processing_tab.processing_height.valueChanged.connect(self._emit_config_changed)
        self.input_processing_tab.render_at_processing_res.toggled.connect(self._emit_config_changed)

        # Color selection
        if hasattr(self, 'add_color_btn'):
            self.add_color_btn.clicked.connect(self._on_add_color)
            if hasattr(self, 'view_range_btn'):
                self.view_range_btn.clicked.connect(self._on_view_range)

        # Detection parameters
        if hasattr(self, 'min_area_spinbox'):
            self.min_area_spinbox.valueChanged.connect(self._emit_config_changed)
            self.max_area_spinbox.valueChanged.connect(self._emit_config_changed)
            self.confidence_spinbox.valueChanged.connect(self._emit_config_changed)

        # Rendering (from shared RenderingTab)
        self.rendering_tab.render_shape.currentTextChanged.connect(self._emit_config_changed)
        self.rendering_tab.render_text.toggled.connect(self._emit_config_changed)
        self.rendering_tab.render_contours.toggled.connect(self._emit_config_changed)
        self.rendering_tab.use_detection_color.toggled.connect(self._emit_config_changed)
        self.rendering_tab.max_detections_to_render.valueChanged.connect(self._emit_config_changed)

    def _on_add_color(self):
        """Add a new color range using HSV ColorRange dialog."""
        # Open the HSV ColorRange dialog
        dialog = ColorRangeDialog(initial_image=None, initial_hsv=(0, 1, 1), initial_ranges=None, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            hsv_data = dialog.get_hsv_ranges()

            # Create color from normalized HSV (0-1)
            color = QColor.fromHsvF(hsv_data['h'], hsv_data['s'], hsv_data['v'])

            # Convert normalized ranges to OpenCV ranges
            # h_minus/h_plus are fractions of 360°, convert to 0-179 range
            # h_minus of 0.2 means 20% of 360° = 72°, which is 72 * 179/360 = 35.8 ≈ 36 in 0-179 range
            hue_minus = int(hsv_data['h_minus'] * 179)
            hue_plus = int(hsv_data['h_plus'] * 179)
            # s_minus/s_plus are fractions of 100%, convert to 0-255 range
            # s_minus of 0.2 means 20%, which is 20 * 255/100 = 51 in 0-255 range
            sat_minus = int(hsv_data['s_minus'] * 255)
            sat_plus = int(hsv_data['s_plus'] * 255)
            # v_minus/v_plus are fractions of 100%, convert to 0-255 range
            # v_minus of 0.2 means 20%, which is 20 * 255/100 = 51 in 0-255 range
            val_minus = int(hsv_data['v_minus'] * 255)
            val_plus = int(hsv_data['v_plus'] * 255)

            new_range = {
                'name': f"Color_{len(self.color_ranges)+1}",
                'color': color,
                'hue_minus': hue_minus,
                'hue_plus': hue_plus,
                'sat_minus': sat_minus,
                'sat_plus': sat_plus,
                'val_minus': val_minus,
                'val_plus': val_plus
            }
            self.color_ranges.append(new_range)
            self._update_color_ranges_display()
            self._emit_config_changed()

    def _on_view_range(self):
        """View range - show all color ranges in a single combined viewer dialog."""
        if not self.color_ranges:
            return

        # Build list of HSV range configs for multi-color viewer
        hsv_ranges_list = []
        for i, color_range in enumerate(self.color_ranges):
            # Get RGB color
            color = color_range.get('color', QColor(255, 0, 0))
            if isinstance(color, QColor):
                rgb = (color.red(), color.green(), color.blue())
            else:
                rgb = (255, 0, 0)

            # Get thresholds in OpenCV format (already in correct format)
            # hue_minus/hue_plus are in 0-179 range
            hue_minus = color_range.get('hue_minus', 20)
            hue_plus = color_range.get('hue_plus', 20)
            # sat_minus/sat_plus are in 0-255 range
            sat_minus = color_range.get('sat_minus', 50)
            sat_plus = color_range.get('sat_plus', 50)
            # val_minus/val_plus are in 0-255 range
            val_minus = color_range.get('val_minus', 50)
            val_plus = color_range.get('val_plus', 50)

            hsv_ranges_list.append({
                'rgb': rgb,
                'hue_minus': hue_minus,
                'hue_plus': hue_plus,
                'sat_minus': sat_minus,
                'sat_plus': sat_plus,
                'val_minus': val_minus,
                'val_plus': val_plus
            })

        # Create combined viewer dialog showing all color ranges
        range_dialog = HSVColorRangeRangeViewer(hsv_ranges_list=hsv_ranges_list)
        if hasattr(range_dialog, 'setWindowTitle'):
            range_dialog.setWindowTitle(f"Color Ranges: {len(hsv_ranges_list)} colors")
        range_dialog.exec()

    def _on_remove_color_range(self, widget):
        """Remove a color range by widget reference."""
        if widget in self.color_range_widgets:
            index = self.color_range_widgets.index(widget)
            if index < len(self.color_ranges):
                self.color_ranges.pop(index)
                self._update_color_ranges_display()
                self._emit_config_changed()

    def _update_color_ranges_display(self):
        """Update the color ranges display with row widgets."""
        if not hasattr(self, 'color_ranges_layout'):
            return

        # IMPORTANT: Sync self.color_ranges from existing widgets BEFORE clearing them
        # This ensures that any user modifications to the widgets are preserved
        # Sync as many widgets as exist (may be fewer than color_ranges if we're adding a new one)
        if self.color_range_widgets:
            for i, widget in enumerate(self.color_range_widgets):
                # Only update if this index exists in color_ranges
                if i < len(self.color_ranges):
                    hsv_ranges = widget.get_hsv_ranges()
                    color = widget.get_color()
                    
                    # Update self.color_ranges with current widget values
                    self.color_ranges[i]['color'] = color
                    self.color_ranges[i]['hue_minus'] = int(hsv_ranges['h_minus'] * 179)
                    self.color_ranges[i]['hue_plus'] = int(hsv_ranges['h_plus'] * 179)
                    self.color_ranges[i]['sat_minus'] = int(hsv_ranges['s_minus'] * 255)
                    self.color_ranges[i]['sat_plus'] = int(hsv_ranges['s_plus'] * 255)
                    self.color_ranges[i]['val_minus'] = int(hsv_ranges['v_minus'] * 255)
                    self.color_ranges[i]['val_plus'] = int(hsv_ranges['v_plus'] * 255)

        # Clear existing widgets
        for widget in self.color_range_widgets:
            widget.setParent(None)
        self.color_range_widgets.clear()

        # Create row widget for each color range using shared HSVColorRowWidget
        for i, color_range in enumerate(self.color_ranges):
            # Convert color_range dict to format expected by HSVColorRowWidget
            color = color_range.get('color', QColor(255, 0, 0))
            if isinstance(color, tuple):
                color = QColor(color[0], color[1], color[2])

            # Get HSV values from color for the widget
            h, s, v, _ = color.getHsvF()
            
            # Build hsv_ranges dict in normalized 0-1 format expected by HSVColorRowWidget
            # hue_minus/hue_plus are in 0-179 range (OpenCV), convert to 0-1 fractional
            # sat_minus/sat_plus are in 0-255 range (OpenCV), convert to 0-1 fractional
            # val_minus/val_plus are in 0-255 range (OpenCV), convert to 0-1 fractional
            hsv_ranges_dict = {
                'h': h,
                's': s,
                'v': v,
                'h_minus': color_range.get('hue_minus', 20) / 179.0,
                'h_plus': color_range.get('hue_plus', 20) / 179.0,
                's_minus': color_range.get('sat_minus', 50) / 255.0,
                's_plus': color_range.get('sat_plus', 50) / 255.0,
                'v_minus': color_range.get('val_minus', 50) / 255.0,
                'v_plus': color_range.get('val_plus', 50) / 255.0
            }
            
            # HSVColorRowWidget expects hsv_ranges dict in normalized 0-1 format
            row_widget = HSVColorRowWidget(
                parent=self,
                color=color,
                hsv_ranges=hsv_ranges_dict
            )
            row_widget.changed.connect(self._emit_config_changed)
            row_widget.delete_requested.connect(lambda w=row_widget: self._on_remove_color_range(w))
            self.color_ranges_layout.insertWidget(i, row_widget)
            self.color_range_widgets.append(row_widget)

    def _emit_config_changed(self):
        """Emit configuration changed signal."""
        self.configChanged.emit(self.get_config())

    def get_config(self) -> dict:
        """Get current configuration matching ColorAnomalyAndMotionDetection format."""
        # Get processing resolution from shared InputProcessingTab
        processing_width, processing_height = self.input_processing_tab.get_processing_resolution()
        if processing_width == 99999:  # "Original" resolution
            processing_resolution = None
        else:
            processing_resolution = (processing_width, processing_height)

        # Get rendering config from shared RenderingTab
        rendering_config = self.rendering_tab.get_config()

        # Get updated color ranges from row widgets
        # Collect color ranges from widgets
        updated_color_ranges = []
        for widget in self.color_range_widgets:
            # Convert from HSVColorRowWidget format to our format
            hsv_ranges = widget.get_hsv_ranges()
            color = widget.get_color()

            # Convert normalized ranges back to OpenCV format
            # h_minus/h_plus are fractions of 360°, convert to 0-179
            hue_minus = int(hsv_ranges['h_minus'] * 179)
            hue_plus = int(hsv_ranges['h_plus'] * 179)
            # s_minus/s_plus are fractions of 100%, convert to 0-255
            sat_minus = int(hsv_ranges['s_minus'] * 255)
            sat_plus = int(hsv_ranges['s_plus'] * 255)
            # v_minus/v_plus are fractions of 100%, convert to 0-255
            val_minus = int(hsv_ranges['v_minus'] * 255)
            val_plus = int(hsv_ranges['v_plus'] * 255)

            updated_color_ranges.append({
                'name': f"Color_{len(updated_color_ranges)+1}",
                'color': color,
                'hue_minus': hue_minus,
                'hue_plus': hue_plus,
                'sat_minus': sat_minus,
                'sat_plus': sat_plus,
                'val_minus': val_minus,
                'val_plus': val_plus
            })
        if not updated_color_ranges:
            updated_color_ranges = self.color_ranges  # Fallback to stored ranges

        config = {
            # Input & Processing (from shared InputProcessingTab)
            'processing_resolution': processing_resolution,
            'processing_width': processing_width if processing_width != 99999 else None,
            'processing_height': processing_height if processing_height != 99999 else None,
            'render_at_processing_res': self.input_processing_tab.render_at_processing_res.isChecked(),

            # Color Selection
            'color_ranges': updated_color_ranges,

            # Detection
            'min_area': self.min_area_spinbox.value() if hasattr(self, 'min_area_spinbox') else 100,
            'max_area': self.max_area_spinbox.value() if hasattr(self, 'max_area_spinbox') else 100000,
            'confidence_threshold': self.confidence_spinbox.value() if hasattr(self, 'confidence_spinbox') else 0.5,

            # Rendering (from shared RenderingTab)
            **rendering_config,
        }
        return config
