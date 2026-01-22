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
                               QScrollArea, QDialog, QSlider)
from PySide6.QtGui import QColor

from core.services.LoggerService import LoggerService
from core.views.streaming.components import InputProcessingTab, RenderingTab, CleanupTab, FrameTab
from algorithms.streaming.ColorDetection.views.HSVControlWidget_ui import Ui_HSVControlWidget
from algorithms.Shared.views import HSVColorRowWidget
from algorithms.Shared.views.HSVColorRangeRangeViewer import HSVColorRangeRangeViewer
from algorithms.images.Shared.views.ColorSelectionMenu import ColorSelectionMenu
from core.services.color.RecentColorsService import get_recent_colors_service
from helpers.TranslationMixin import TranslationMixin


class ColorDetectionControlWidget(TranslationMixin, QWidget, Ui_HSVControlWidget):
    """Control widget for color detection parameters."""

    configChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Multiple color range support
        self.color_ranges = []
        self.current_range_index = 0
        self.color_range_widgets = []  # Store row widgets

        # Recent colors service
        self.recent_colors_service = get_recent_colors_service()

        # Setup UI from UI file
        self.setupUi(self)

        # Get tab widget reference
        self.tabs = self.tabs  # From Ui_HSVControlWidget

        # Populate tabs with actual controls
        self._populate_tabs()

        # Connect signals
        self.connect_signals()
        self._apply_translations()

    def _populate_tabs(self):
        """Populate tabs with control panels."""
        # Clear placeholder tabs
        self.tabs.clear()

        # Use shared tabs for Input & Processing, Cleanup, Frame, and Rendering
        self.input_processing_tab = InputProcessingTab()
        self.cleanup_tab = CleanupTab()
        self.frame_tab = FrameTab()
        self.rendering_tab = RenderingTab(show_detection_color_option=True)
        self.tabs.addTab(self._create_color_selection_tab(), self.tr("Color Selection"))
        self.tabs.addTab(self._create_detection_tab(), self.tr("Detection"))
        self.tabs.addTab(self.input_processing_tab, self.tr("Input && Processing"))
        self.tabs.addTab(self.frame_tab, self.tr("Frame"))
        self.tabs.addTab(self.rendering_tab, self.tr("Rendering && Cleanup"))

    def _create_color_selection_tab(self) -> QWidget:
        """Create color selection tab matching screenshot - inline editing with HSV ranges."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Top buttons
        btn_layout = QHBoxLayout()
        self.add_color_btn = QPushButton(self.tr("Add Color"))
        self.add_color_btn.setToolTip(
            self.tr(
                "Add a new color range to detect.\n"
                "Choose from HSV Color Picker, Image, List, or Recent Colors.\n"
                "You can add multiple color ranges to detect different colors simultaneously."
            )
        )
        btn_layout.addWidget(self.add_color_btn)

        # Set up color selection menu (same as wizard)
        self.color_selection_menu = ColorSelectionMenu(
            self,
            on_color_selected=self._on_color_selected_from_menu,
            get_default_qcolor=self._get_default_qcolor,
            on_hsv_selected=self._on_hsv_selected_from_picker,
            on_recent_color_selected=self._on_recent_color_selected,
            mode='HSV'
        )
        self.color_selection_menu.attach_to(self.add_color_btn)

        btn_layout.addStretch()

        self.view_range_btn = QPushButton(self.tr("View Range"))
        self.view_range_btn.setToolTip(
            self.tr(
                "View HSV color ranges for all configured colors.\n"
                "Opens a viewer dialog for each color range showing\n"
                "the hue, saturation, and value ranges that will be detected.\n"
                "Useful for understanding and fine-tuning multi-color detection."
            )
        )
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

        grid.addWidget(QLabel(self.tr("Min Object Area (px):")), 0, 0)
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setRange(10, 50000)
        self.min_area_spinbox.setValue(10)
        self.min_area_spinbox.setToolTip(
            self.tr(
                "Minimum detection area in pixels (10-50000).\n"
                "Filters out very small detections (noise, small objects, fragments).\n"
                "Lower values = detect smaller objects, more detections, more noise.\n"
                "Higher values = only large objects, fewer detections, less noise.\n"
                "Recommended: 100 for general use, 50 for small objects, 200-500 for large objects."
            )
        )
        grid.addWidget(self.min_area_spinbox, 0, 1)

        grid.addWidget(QLabel(self.tr("Max Object Area (px):")), 1, 0)
        self.max_area_spinbox = QSpinBox()
        self.max_area_spinbox.setRange(100, 500000)
        self.max_area_spinbox.setValue(100000)
        self.max_area_spinbox.setToolTip(
            self.tr(
                "Maximum detection area in pixels (100-500000).\n"
                "Filters out very large detections (shadows, lighting changes, entire scene).\n"
                "Lower values = only small/medium objects.\n"
                "Higher values = allow large objects, may include unwanted large regions.\n"
                "Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects."
            )
        )
        grid.addWidget(self.max_area_spinbox, 1, 1)

        grid.addWidget(QLabel(self.tr("Confidence Threshold:")), 2, 0)
        confidence_layout = QHBoxLayout()
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(50)  # Default 0.5 (50%)
        self.confidence_slider.setToolTip(
            self.tr(
                "Minimum confidence score to accept a detection (0-100%).\n"
                "Confidence is calculated from:\n"
                "• Size score: area relative to max area\n"
                "• Shape score: solidity (how compact/regular the shape is)\n"
                "• Final: average of both scores\n\n"
                "Lower values (0-30%) = accept more detections, including weak/fragmented ones.\n"
                "Higher values (70-100%) = only high-quality detections, well-formed shapes.\n"
                "Recommended: 50% for balanced filtering, 30% for more detections, 70% for strict quality."
            )
        )
        confidence_layout.addWidget(self.confidence_slider)
        self.confidence_label = QLabel(self.tr("50%"))
        confidence_layout.addWidget(self.confidence_label)
        grid.addLayout(confidence_layout, 2, 1)

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
        if hasattr(self, 'view_range_btn'):
            self.view_range_btn.clicked.connect(self._on_view_range)

        # Detection parameters
        if hasattr(self, 'min_area_spinbox'):
            self.min_area_spinbox.valueChanged.connect(self._emit_config_changed)
            self.max_area_spinbox.valueChanged.connect(self._emit_config_changed)
            self.confidence_slider.valueChanged.connect(self._update_confidence_label)
            self.confidence_slider.valueChanged.connect(self._emit_config_changed)

        # Cleanup (from shared CleanupTab)
        self.cleanup_tab.enable_temporal_voting.toggled.connect(self._emit_config_changed)
        self.cleanup_tab.temporal_window_frames.valueChanged.connect(self._emit_config_changed)
        self.cleanup_tab.temporal_threshold_frames.valueChanged.connect(self._emit_config_changed)
        self.cleanup_tab.enable_aspect_ratio_filter.toggled.connect(self._emit_config_changed)
        self.cleanup_tab.min_aspect_ratio.valueChanged.connect(self._emit_config_changed)
        self.cleanup_tab.max_aspect_ratio.valueChanged.connect(self._emit_config_changed)
        self.cleanup_tab.enable_detection_clustering.toggled.connect(self._emit_config_changed)
        self.cleanup_tab.clustering_distance.valueChanged.connect(self._emit_config_changed)

        # Frame/Mask (from shared FrameTab)
        self.frame_tab.configChanged.connect(self._emit_config_changed)

        # Rendering (from shared RenderingTab)
        self.rendering_tab.render_shape.currentTextChanged.connect(self._emit_config_changed)
        self.rendering_tab.render_text.toggled.connect(self._emit_config_changed)
        self.rendering_tab.render_contours.toggled.connect(self._emit_config_changed)
        self.rendering_tab.use_detection_color.toggled.connect(self._emit_config_changed)
        self.rendering_tab.max_detections_to_render.valueChanged.connect(self._emit_config_changed)
        # Temporal Voting and Cleanup
        self.rendering_tab.enable_temporal_voting.toggled.connect(self._emit_config_changed)
        self.rendering_tab.temporal_window_frames.valueChanged.connect(self._emit_config_changed)
        self.rendering_tab.temporal_threshold_frames.valueChanged.connect(self._emit_config_changed)
        self.rendering_tab.enable_aspect_ratio_filter.toggled.connect(self._emit_config_changed)
        self.rendering_tab.min_aspect_ratio.valueChanged.connect(self._emit_config_changed)
        self.rendering_tab.max_aspect_ratio.valueChanged.connect(self._emit_config_changed)
        self.rendering_tab.enable_detection_clustering.toggled.connect(self._emit_config_changed)
        self.rendering_tab.clustering_distance.valueChanged.connect(self._emit_config_changed)

    def _get_default_qcolor(self):
        """Return the most recent color or a sensible default."""
        if self.color_ranges:
            last_range = self.color_ranges[-1]
            color = last_range.get('color', QColor(255, 0, 0))
            if isinstance(color, QColor):
                return color
            elif isinstance(color, tuple):
                return QColor(color[0], color[1], color[2])
        return QColor(255, 0, 0)

    def _on_color_selected_from_menu(self, color: QColor):
        """Handle color chosen from the shared color selection menu."""
        # Add color with default tolerance ranges
        self._add_color_range_from_color(color)
        # Save to recent colors
        try:
            rgb = (color.red(), color.green(), color.blue())
            color_config = {
                'selected_color': rgb,
                'color_range': None  # No specific range for tolerance-based
            }
            self.recent_colors_service.add_rgb_color(color_config)
        except Exception:
            pass  # Silently fail if tracking fails

    def _on_hsv_selected_from_picker(self, hsv_data: dict):
        """Handle HSV color range selected from HSV picker dialog."""
        import cv2
        import numpy as np

        # Extract the center HSV color from the data
        if 'center_hsv' in hsv_data:
            h, s, v = hsv_data['center_hsv']
        elif 'h' in hsv_data and 's' in hsv_data and 'v' in hsv_data:
            # Convert from 0-1 range to OpenCV range (0-179, 0-255, 0-255)
            h = int(hsv_data['h'] * 179)
            s = int(hsv_data['s'] * 255)
            v = int(hsv_data['v'] * 255)
        else:
            return  # Invalid data

        # Convert HSV to RGB (OpenCV format: H=0-179, S=0-255, V=0-255)
        if 'h' in hsv_data and isinstance(hsv_data['h'], float) and 0 <= hsv_data['h'] <= 1:
            # Already in 0-1 range, convert to OpenCV for RGB conversion
            h_cv = int(hsv_data['h'] * 179)
            s_cv = int(hsv_data['s'] * 255)
            v_cv = int(hsv_data['v'] * 255)
        else:
            # Already in OpenCV range
            h_cv, s_cv, v_cv = h, s, v

        hsv_array = np.uint8([[[h_cv, s_cv, v_cv]]])
        bgr = cv2.cvtColor(hsv_array, cv2.COLOR_HSV2BGR)[0][0]
        b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2])
        color = QColor(r, g, b)

        # Convert HSV ranges from fractional (0-1) to OpenCV format
        h_minus_frac = hsv_data.get('h_minus', 0.1)
        h_plus_frac = hsv_data.get('h_plus', 0.1)
        s_minus_frac = hsv_data.get('s_minus', 0.2)
        s_plus_frac = hsv_data.get('s_plus', 0.2)
        v_minus_frac = hsv_data.get('v_minus', 0.2)
        v_plus_frac = hsv_data.get('v_plus', 0.2)

        new_range = {
            'name': self.tr("Color_{index}").format(index=len(self.color_ranges) + 1),
            'color': color,
            'hue_minus': int(h_minus_frac * 179),
            'hue_plus': int(h_plus_frac * 179),
            'sat_minus': int(s_minus_frac * 255),
            'sat_plus': int(s_plus_frac * 255),
            'val_minus': int(v_minus_frac * 255),
            'val_plus': int(v_plus_frac * 255)
        }
        self.color_ranges.append(new_range)
        self._update_color_ranges_display()
        self._emit_config_changed()

        # Save to recent colors with HSV ranges
        try:
            rgb = (color.red(), color.green(), color.blue())
            hsv_config = {
                'selected_color': rgb,
                'hsv_ranges': {
                    'h': hsv_data.get('h', 0.0),
                    's': hsv_data.get('s', 1.0),
                    'v': hsv_data.get('v', 1.0),
                    'h_minus': h_minus_frac,
                    'h_plus': h_plus_frac,
                    's_minus': s_minus_frac,
                    's_plus': s_plus_frac,
                    'v_minus': v_minus_frac,
                    'v_plus': v_plus_frac
                }
            }
            self.recent_colors_service.add_hsv_color(hsv_config)
        except Exception:
            pass  # Silently fail if tracking fails

    def _on_recent_color_selected(self, color_data: dict):
        """Handle selection from recent colors list."""
        try:
            selected_color = color_data.get('selected_color', (255, 0, 0))
            r, g, b = selected_color
            color = QColor(r, g, b)

            # Try to get HSV ranges from data if available
            hsv_ranges = color_data.get('hsv_ranges')
            if hsv_ranges:
                # Recent color has HSV ranges, use them
                h_minus_frac = hsv_ranges.get('h_minus', 0.1)
                h_plus_frac = hsv_ranges.get('h_plus', 0.1)
                s_minus_frac = hsv_ranges.get('s_minus', 0.2)
                s_plus_frac = hsv_ranges.get('s_plus', 0.2)
                v_minus_frac = hsv_ranges.get('v_minus', 0.2)
                v_plus_frac = hsv_ranges.get('v_plus', 0.2)

                new_range = {
                    'name': self.tr("Color_{index}").format(index=len(self.color_ranges) + 1),
                    'color': color,
                    'hue_minus': int(h_minus_frac * 179),
                    'hue_plus': int(h_plus_frac * 179),
                    'sat_minus': int(s_minus_frac * 255),
                    'sat_plus': int(s_plus_frac * 255),
                    'val_minus': int(v_minus_frac * 255),
                    'val_plus': int(v_plus_frac * 255)
                }
                self.color_ranges.append(new_range)
            else:
                # Fallback: use default ranges
                self._add_color_range_from_color(color)
            self._update_color_ranges_display()
            self._emit_config_changed()
        except Exception:
            # Fallback to basic color selection
            selected_color = color_data.get('selected_color', (255, 0, 0))
            if isinstance(selected_color, (list, tuple)) and len(selected_color) == 3:
                r, g, b = selected_color
                color = QColor(r, g, b)
                self._add_color_range_from_color(color)

    def _add_color_range_from_color(self, color: QColor):
        """Add a color range from a QColor with default tolerance ranges."""
        # Use reasonable default tolerance values (Moderate preset)
        # These are stored in OpenCV format (H: 0-179, S/V: 0-255)
        # Hue: ±15° is reasonable for most colors
        # Saturation/Value: Use 20% of full range (51) instead of 75 (29%) for tighter matching
        # The old value of 75 was too wide - it would match almost all colors except extremes
        hue_tolerance = 15  # ±15° in OpenCV (0-179 range) - reasonable hue variation
        sat_tolerance = 51  # 20% of full saturation range (0.2 * 255) - tighter than old 75
        val_tolerance = 51  # 20% of full value range (0.2 * 255) - tighter than old 75

        new_range = {
            'name': self.tr("Color_{index}").format(index=len(self.color_ranges) + 1),
            'color': color,
            'hue_minus': hue_tolerance,
            'hue_plus': hue_tolerance,
            'sat_minus': sat_tolerance,
            'sat_plus': sat_tolerance,
            'val_minus': val_tolerance,
            'val_plus': val_tolerance
        }
        self.color_ranges.append(new_range)
        self._update_color_ranges_display()
        self._emit_config_changed()

        # Save to recent colors (when called from _on_color_selected_from_menu, it's already saved there)
        # But if called from elsewhere (like _on_recent_color_selected fallback), save it
        # Actually, we'll save it here too to ensure it's always tracked
        try:
            rgb = (color.red(), color.green(), color.blue())
            color_config = {
                'selected_color': rgb,
                'color_range': None  # No specific range for tolerance-based
            }
            self.recent_colors_service.add_rgb_color(color_config)
        except Exception:
            pass  # Silently fail if tracking fails

    def _on_view_range(self):
        """View range - show all color ranges in a single combined viewer dialog."""
        # IMPORTANT: Sync current widget values to self.color_ranges before building the list
        # This ensures the dialog shows the latest modifications made in the widgets
        if self.color_range_widgets:
            for i, widget in enumerate(self.color_range_widgets):
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
            range_dialog.setWindowTitle(
                self.tr("Color Ranges: {count} colors").format(count=len(hsv_ranges_list))
            )
        range_dialog.exec()

    def _on_remove_color_range(self, widget):
        """Remove a color range by widget reference."""
        if widget in self.color_range_widgets:
            # Find the index before removing
            index = self.color_range_widgets.index(widget)

            # First, sync data from all widgets to color_ranges to preserve any edits
            # This must happen before removing to keep indices aligned
            if self.color_range_widgets:
                for i, w in enumerate(self.color_range_widgets):
                    if i < len(self.color_ranges):
                        hsv_ranges = w.get_hsv_ranges()
                        color = w.get_color()
                        self.color_ranges[i]['color'] = color
                        self.color_ranges[i]['hue_minus'] = int(hsv_ranges['h_minus'] * 179)
                        self.color_ranges[i]['hue_plus'] = int(hsv_ranges['h_plus'] * 179)
                        self.color_ranges[i]['sat_minus'] = int(hsv_ranges['s_minus'] * 255)
                        self.color_ranges[i]['sat_plus'] = int(hsv_ranges['s_plus'] * 255)
                        self.color_ranges[i]['val_minus'] = int(hsv_ranges['v_minus'] * 255)
                        self.color_ranges[i]['val_plus'] = int(hsv_ranges['v_plus'] * 255)

            # Now remove from color_ranges using the correct index
            if index < len(self.color_ranges):
                self.color_ranges.pop(index)
                # Remove widget from list to prevent sync issues in _update_color_ranges_display
                self.color_range_widgets.remove(widget)
                widget.setParent(None)
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

    def _update_confidence_label(self):
        """Update confidence threshold label."""
        value = self.confidence_slider.value()
        self.confidence_label.setText(f"{value}%")

    def get_config(self) -> dict:
        """Get current configuration matching ColorAnomalyAndMotionDetection format."""
        # Get processing resolution from shared InputProcessingTab
        processing_width, processing_height = self.input_processing_tab.get_processing_resolution()
        if processing_width == 99999:  # "Original" resolution
            processing_resolution = None
        else:
            processing_resolution = (processing_width, processing_height)

        # Get cleanup config from shared CleanupTab
        cleanup_config = self.cleanup_tab.get_config()

        # Get frame/mask config from shared FrameTab
        frame_config = self.frame_tab.get_config()

        # Get rendering config from shared RenderingTab
        rendering_config = self.rendering_tab.get_config()

        # Get updated color ranges from row widgets
        # Collect color ranges from widgets
        updated_color_ranges = []
        for widget in self.color_range_widgets:
            # Save colors to recent colors when config is retrieved (when actually used)
            try:
                color = widget.get_color()
                hsv_ranges = widget.get_hsv_ranges()
                rgb = (color.red(), color.green(), color.blue())

                # HSVColorRowWidget always returns hsv_ranges with h, s, v, h_minus, h_plus, etc.
                # All values are in normalized 0-1 format
                if hsv_ranges and isinstance(hsv_ranges, dict):
                    hsv_config = {
                        'selected_color': rgb,
                        'hsv_ranges': hsv_ranges  # Already in correct format (0-1 normalized)
                    }
                    self.recent_colors_service.add_hsv_color(hsv_config)
                else:
                    # Fallback: RGB color without HSV ranges
                    color_config = {
                        'selected_color': rgb,
                        'color_range': None
                    }
                    self.recent_colors_service.add_rgb_color(color_config)
            except Exception as e:
                # Log error for debugging instead of silently failing
                self.logger.debug(f"Error saving color to recent colors: {e}")
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
                'name': self.tr("Color_{index}").format(index=len(updated_color_ranges) + 1),
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
            'confidence_threshold': self.confidence_slider.value() / 100.0 if hasattr(self, 'confidence_slider') else 0.5,

            # Cleanup (from shared CleanupTab)
            **cleanup_config,

            # Frame/Mask (from shared FrameTab)
            **frame_config,

            # Rendering (from shared RenderingTab)
            **rendering_config,
        }
        return config
