"""
ColorDetectionControlWidget.py - Control widget for color detection parameters.

This widget provides a tabbed interface for configuring all ColorDetectionService
parameters. It matches the IntegratedDetection UI structure.
"""

from typing import Dict, Any, List, Tuple, Optional
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QDoubleSpinBox, QCheckBox,
                               QComboBox, QGroupBox, QPushButton, QListWidget, QListWidgetItem)
from PySide6.QtGui import QColor

from core.services.LoggerService import LoggerService
from algorithms.streaming.ColorDetection.views.HSVControlWidget_ui import Ui_HSVControlWidget
from algorithms.Shared.views import HSVColorRowWidget, ColorRangeDialog


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

        # Initialize with one default red range
        self._add_default_range()

        # Setup UI from UI file
        self.setupUi(self)

        # Get tab widget reference
        self.tabs = self.tabs  # From Ui_HSVControlWidget

        # Populate tabs with actual controls
        self._populate_tabs()

        # Connect signals
        self.connect_signals()

    def _add_default_range(self):
        """Add default red color range."""
        default_range = {
            'name': 'Red',
            'color': QColor(255, 0, 0),
            'hue_minus': 20,
            'hue_plus': 20,
            'sat_minus': 50,
            'sat_plus': 50,
            'val_minus': 50,
            'val_plus': 50
        }
        self.color_ranges.append(default_range)

    def _populate_tabs(self):
        """Populate tabs with control panels."""
        # Clear placeholder tabs
        self.tabs.clear()

        # Add actual tabs - Input & Processing first, then Color Selection, Detection, and Rendering
        self.tabs.addTab(self._create_input_processing_tab(), "Input & Processing")
        self.tabs.addTab(self._create_color_selection_tab(), "Color Selection")
        self.tabs.addTab(self._create_detection_tab(), "Detection")
        self.tabs.addTab(self._create_rendering_tab(), "Rendering")

    def _create_input_processing_tab(self) -> QWidget:
        """Create Input & Processing tab - matches IntegratedDetection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Processing Resolution
        res_group = QGroupBox("Processing Resolution")
        res_layout = QVBoxLayout(res_group)

        # Dropdown for preset resolutions
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.resolution_preset = QComboBox()

        # Common 16:9 resolutions (matching IntegratedDetection)
        self.resolution_presets = {
            "Original": None,  # Use video's native resolution
            "426x240": (426, 240),
            "640x360": (640, 360),
            "960x540": (960, 540),
            "1280x720": (1280, 720),
            "1600x900": (1600, 900),
            "1920x1080": (1920, 1080),
            "2560x1440": (2560, 1440),
            "3200x1800": (3200, 1800),
            "3840x2160": (3840, 2160),
            "5120x2880": (5120, 2880),
            "7680x4320": (7680, 4320),
            "Custom": "custom"  # Special marker for custom resolution
        }

        for preset in self.resolution_presets.keys():
            self.resolution_preset.addItem(preset)

        self.resolution_preset.setCurrentText("1280x720")
        self.resolution_preset.setToolTip("Select a preset resolution for processing. Lower resolutions are faster but less detailed.\n"
                                          "'Original' uses the video's native resolution (no downsampling).\n"
                                          "720p (1280x720) provides excellent balance between speed and detection accuracy.\n"
                                          "Select 'Custom' to manually set width and height.")
        preset_layout.addWidget(self.resolution_preset)
        res_layout.addLayout(preset_layout)

        # Custom resolution inputs (hidden by default)
        custom_layout = QGridLayout()
        custom_layout.addWidget(QLabel("Width:"), 0, 0)
        self.processing_width = QSpinBox()
        self.processing_width.setRange(320, 3840)
        self.processing_width.setValue(1280)
        self.processing_width.setEnabled(False)
        self.processing_width.setToolTip(
            "Custom processing width in pixels (320-3840).\nOnly enabled when 'Custom' preset is selected.\nLower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_width, 0, 1)

        custom_layout.addWidget(QLabel("Height:"), 1, 0)
        self.processing_height = QSpinBox()
        self.processing_height.setRange(240, 2160)
        self.processing_height.setValue(720)
        self.processing_height.setEnabled(False)
        self.processing_height.setToolTip(
            "Custom processing height in pixels (240-2160).\nOnly enabled when 'Custom' preset is selected.\nLower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_height, 1, 1)

        res_layout.addLayout(custom_layout)
        layout.addWidget(res_group)

        # Performance Options
        perf_group = QGroupBox("Performance Options")
        perf_layout = QVBoxLayout(perf_group)

        self.threaded_capture = QCheckBox("Use Threaded Capture")
        self.threaded_capture.setChecked(True)  # Default ON
        self.threaded_capture.setToolTip("Enables background video decoding in a separate thread.\n"
                                         "Allows processing to happen in parallel with video capture.\n"
                                         "Improves performance especially for high-resolution videos (2K/4K).\n"
                                         "Highly recommended for all video sources. No downsides.")
        perf_layout.addWidget(self.threaded_capture)

        self.render_at_processing_res = QCheckBox("Render at Processing Resolution (faster for high-res)")
        self.render_at_processing_res.setChecked(True)  # Default ON
        self.render_at_processing_res.setToolTip("Renders detection overlays at processing resolution instead of original video resolution.\n"
                                                 "Significantly faster for high-resolution videos (1080p+) with minimal visual impact.\n"
                                                 "Example: Processing at 720p but video is 4K - renders at 720p then upscales.\n"
                                                 "Recommended: ON for high-res videos, OFF for native 720p or lower.")
        perf_layout.addWidget(self.render_at_processing_res)

        layout.addWidget(perf_group)
        layout.addStretch()

        return widget

    def _create_color_selection_tab(self) -> QWidget:
        """Create color selection tab matching screenshot - inline editing with HSV ranges."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Top buttons
        btn_layout = QHBoxLayout()
        self.add_color_btn = QPushButton("Add Color")
        btn_layout.addWidget(self.add_color_btn)

        btn_layout.addStretch()

        self.view_range_btn = QPushButton("View Range")
        btn_layout.addWidget(self.view_range_btn)
        layout.addLayout(btn_layout)

        # Scroll area for color ranges
        from PySide6.QtWidgets import QScrollArea
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

        grid.addWidget(QLabel("Min Area (px²):"), 0, 0)
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setRange(10, 50000)
        self.min_area_spinbox.setValue(100)
        grid.addWidget(self.min_area_spinbox, 0, 1)

        grid.addWidget(QLabel("Max Area (px²):"), 1, 0)
        self.max_area_spinbox = QSpinBox()
        self.max_area_spinbox.setRange(100, 500000)
        self.max_area_spinbox.setValue(100000)
        grid.addWidget(self.max_area_spinbox, 1, 1)

        grid.addWidget(QLabel("Confidence Threshold:"), 2, 0)
        self.confidence_spinbox = QDoubleSpinBox()
        self.confidence_spinbox.setRange(0.0, 1.0)
        self.confidence_spinbox.setSingleStep(0.05)
        self.confidence_spinbox.setValue(0.5)
        grid.addWidget(self.confidence_spinbox, 2, 1)

        layout.addLayout(grid)
        layout.addStretch()

        return widget

    def _create_rendering_tab(self) -> QWidget:
        """Create Rendering tab - matches IntegratedDetection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Shape Options
        shape_group = QGroupBox("Shape Options")
        shape_layout = QGridLayout(shape_group)

        shape_layout.addWidget(QLabel("Shape Mode:"), 0, 0)
        self.render_shape = QComboBox()
        self.render_shape.addItems(["Box", "Circle", "Dot", "Off"])
        self.render_shape.setCurrentText("Circle")
        self.render_shape.setToolTip("Shape to draw around detections:\n\n"
                                     "• Box: Rectangle around detection bounding box.\n"
                                     "  Use for: Precise boundaries, technical visualization.\n\n"
                                     "• Circle: Circle encompassing detection (150% of contour radius).\n"
                                     "  Use for: General use, cleaner look (default).\n\n"
                                     "• Dot: Small dot at detection centroid.\n"
                                     "  Use for: Minimal overlay, fast rendering.\n\n"
                                     "• Off: No shape overlay (only thumbnails/text if enabled).\n"
                                     "  Use for: Clean video with minimal overlays.")
        shape_layout.addWidget(self.render_shape, 0, 1)

        layout.addWidget(shape_group)

        # Text & Contours
        vis_group = QGroupBox("Visual Options")
        vis_layout = QVBoxLayout(vis_group)

        self.render_text = QCheckBox("Show Text Labels (slower)")
        self.render_text.setToolTip("Displays text labels near detections showing detection information.\n"
                                    "Adds ~5-15ms processing overhead depending on detection count.\n"
                                    "Labels show: detection type, confidence, area.\n"
                                    "Recommended: OFF for speed, ON for debugging/analysis.")
        vis_layout.addWidget(self.render_text)

        self.render_contours = QCheckBox("Show Contours (slowest)")
        self.render_contours.setToolTip("Draws exact detection contours (pixel-precise boundaries).\n"
                                        "Adds ~10-20ms processing overhead (very expensive).\n"
                                        "Shows exact shape detected by algorithm.\n"
                                        "Recommended: OFF for speed, ON only for detailed analysis.")
        vis_layout.addWidget(self.render_contours)

        self.use_detection_color = QCheckBox("Use Detection Color (hue @ 100% sat/val for color anomalies)")
        self.use_detection_color.setChecked(True)  # Default ON
        self.use_detection_color.setToolTip("Color the detection overlay based on detected color.\n"
                                            "For color anomalies: Uses the detected hue at 100% saturation/value.\n"
                                            "For motion detections: Uses default color (green/blue).\n"
                                            "Helps visually identify what color was detected.\n"
                                            "Recommended: ON for color detection, OFF for motion-only.")
        vis_layout.addWidget(self.use_detection_color)

        layout.addWidget(vis_group)

        # Detection Limits
        limit_group = QGroupBox("Performance Limits")
        limit_layout = QGridLayout(limit_group)

        limit_layout.addWidget(QLabel("Max Detections:"), 0, 0)
        self.max_detections_to_render = QSpinBox()
        self.max_detections_to_render.setRange(0, 1000)
        self.max_detections_to_render.setValue(100)
        self.max_detections_to_render.setSpecialValueText("Unlimited")
        self.max_detections_to_render.setToolTip("Maximum number of detections to render on screen (0-1000).\n"
                                                 "Prevents rendering slowdown when hundreds of detections occur.\n"
                                                 "Shows highest confidence detections first.\n"
                                                 "0 = Unlimited (may cause lag with many detections).\n"
                                                 "Recommended: 100 for general use, 50 for complex rendering (text+contours).")
        limit_layout.addWidget(self.max_detections_to_render, 0, 1)

        layout.addWidget(limit_group)

        # Overlay Options
        overlay_group = QGroupBox("Overlay Options")
        overlay_layout = QVBoxLayout(overlay_group)

        self.show_timing_overlay = QCheckBox("Show Timing Overlay (FPS, metrics)")
        self.show_timing_overlay.setChecked(False)  # Default OFF
        self.show_timing_overlay.setToolTip("Displays detailed timing information on video overlay.\n"
                                            "Shows: FPS, processing time, detection counts, pipeline breakdown.\n"
                                            "Useful for performance tuning and debugging.\n"
                                            "Recommended: OFF for clean view, ON when optimizing performance.")
        overlay_layout.addWidget(self.show_timing_overlay)

        self.show_detection_thumbnails = QCheckBox("Show Detection Thumbnails (auto-fit window width)")
        self.show_detection_thumbnails.setChecked(False)  # Default OFF
        self.show_detection_thumbnails.setToolTip("Shows zoomed thumbnails of detected objects below video.\n"
                                                  "Number of thumbnails adjusts automatically to window width (1-20).\n"
                                                  "Thumbnails persist for 2 seconds minimum (reduces flicker).\n"
                                                  "Useful for: Close-up view of detections, tracking specific objects.\n"
                                                  "Recommended: ON for analysis, OFF for clean display.")
        overlay_layout.addWidget(self.show_detection_thumbnails)

        layout.addWidget(overlay_group)
        layout.addStretch()

        return widget

    def connect_signals(self):
        """Connect all control signals."""
        # Input & Processing
        self.resolution_preset.currentTextChanged.connect(self.on_resolution_preset_changed)
        self.processing_width.valueChanged.connect(self._emit_config_changed)
        self.processing_height.valueChanged.connect(self._emit_config_changed)
        self.threaded_capture.toggled.connect(self._emit_config_changed)
        self.render_at_processing_res.toggled.connect(self._emit_config_changed)

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

        # Rendering
        if hasattr(self, 'render_shape'):
            self.render_shape.currentTextChanged.connect(self._emit_config_changed)
            self.render_text.toggled.connect(self._emit_config_changed)
            self.render_contours.toggled.connect(self._emit_config_changed)
            self.use_detection_color.toggled.connect(self._emit_config_changed)
            self.max_detections_to_render.valueChanged.connect(self._emit_config_changed)
            self.show_timing_overlay.toggled.connect(self._emit_config_changed)
            self.show_detection_thumbnails.toggled.connect(self._emit_config_changed)

    def on_resolution_preset_changed(self, preset_name: str):
        """Handle resolution preset change."""
        if preset_name == "Custom":
            self.processing_width.setEnabled(True)
            self.processing_height.setEnabled(True)
        else:
            self.processing_width.setEnabled(False)
            self.processing_height.setEnabled(False)
        self._emit_config_changed()

    def _on_add_color(self):
        """Add a new color range using HSV ColorRange dialog."""
        # Open the HSV ColorRange dialog
        from PySide6.QtWidgets import QDialog
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
        """View range - show all color ranges in a viewer dialog."""
        if not self.color_ranges:
            return

        # Import the range viewer
        try:
            from algorithms.images.HSVColorRange.controllers.HSVColorRangeViewerController import HSVColorRangeRangeViewer
        except ImportError:
            return

        # For now, show the first color range (can be extended to show all)
        if self.color_ranges:
            first_range = self.color_ranges[0]
            # Get RGB color
            color = first_range.get('color', QColor(255, 0, 0))
            if isinstance(color, QColor):
                rgb = (color.red(), color.green(), color.blue())
            else:
                rgb = (255, 0, 0)

            # Calculate average thresholds for viewer (backward compatibility)
            hue_minus = first_range.get('hue_minus', 20)
            hue_plus = first_range.get('hue_plus', 20)
            sat_minus = first_range.get('sat_minus', 50)
            sat_plus = first_range.get('sat_plus', 50)
            val_minus = first_range.get('val_minus', 50)
            val_plus = first_range.get('val_plus', 50)

            h_avg = int((hue_minus + hue_plus) / 2)
            s_avg = int((sat_minus + sat_plus) / 2)
            v_avg = int((val_minus + val_plus) / 2)

            range_dialog = HSVColorRangeRangeViewer(rgb, h_avg, s_avg, v_avg)
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

            # HSVColorRowWidget expects h_minus/h_plus in 0-179, s_minus/s_plus in 0-100%, v_minus/v_plus in 0-100%
            row_widget = HSVColorRowWidget(
                parent=self,
                color=color,
                h_minus=color_range.get('hue_minus', 20),
                h_plus=color_range.get('hue_plus', 20),
                s_minus=int(color_range.get('sat_minus', 50) * 100 / 255),  # Convert 0-255 to 0-100%
                s_plus=int(color_range.get('sat_plus', 50) * 100 / 255),
                v_minus=int(color_range.get('val_minus', 50) * 100 / 255),
                v_plus=int(color_range.get('val_plus', 50) * 100 / 255)
            )
            row_widget.changed.connect(self._emit_config_changed)
            row_widget.delete_requested.connect(lambda w=row_widget: self._on_remove_color_range(w))
            self.color_ranges_layout.insertWidget(i, row_widget)
            self.color_range_widgets.append(row_widget)

    def _emit_config_changed(self):
        """Emit configuration changed signal."""
        self.configChanged.emit(self.get_config())

    def get_config(self) -> dict:
        """Get current configuration matching IntegratedDetection format."""
        # Parse processing resolution
        preset_name = self.resolution_preset.currentText()
        if preset_name == "Custom":
            processing_resolution = (self.processing_width.value(), self.processing_height.value())
        else:
            processing_resolution = self.resolution_presets.get(preset_name)

        # Map render shape to enum value (0=Box, 1=Circle, 2=Dot, 3=Off)
        shape_map = {
            "Box": 0,
            "Circle": 1,
            "Dot": 2,
            "Off": 3
        }
        render_shape = shape_map.get(self.render_shape.currentText(), 1)

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
            # Input & Processing
            'processing_resolution': processing_resolution,
            'processing_width': self.processing_width.value() if preset_name == "Custom" else None,
            'processing_height': self.processing_height.value() if preset_name == "Custom" else None,
            'threaded_capture': self.threaded_capture.isChecked(),
            'render_at_processing_res': self.render_at_processing_res.isChecked(),

            # Color Selection
            'color_ranges': updated_color_ranges,

            # Detection
            'min_area': self.min_area_spinbox.value() if hasattr(self, 'min_area_spinbox') else 100,
            'max_area': self.max_area_spinbox.value() if hasattr(self, 'max_area_spinbox') else 100000,
            'confidence_threshold': self.confidence_spinbox.value() if hasattr(self, 'confidence_spinbox') else 0.5,

            # Rendering
            'render_shape': render_shape,
            'render_text': self.render_text.isChecked() if hasattr(self, 'render_text') else False,
            'render_contours': self.render_contours.isChecked() if hasattr(self, 'render_contours') else False,
            'use_detection_color_for_rendering': self.use_detection_color.isChecked() if hasattr(self, 'use_detection_color') else True,
            'max_detections_to_render': self.max_detections_to_render.value() if hasattr(self, 'max_detections_to_render') else 100,
            'show_timing_overlay': self.show_timing_overlay.isChecked() if hasattr(self, 'show_timing_overlay') else False,
            'show_detection_thumbnails': self.show_detection_thumbnails.isChecked() if hasattr(self, 'show_detection_thumbnails') else False,
        }
        return config
