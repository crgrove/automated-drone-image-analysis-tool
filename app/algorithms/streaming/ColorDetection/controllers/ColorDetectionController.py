"""
ColorDetectionController.py - HSV color detection algorithm controller for ADIAT

Provides real-time color detection using HSV color space matching.
Integrated into StreamViewerWindow following the StreamAlgorithmController pattern.
"""

# Set environment variables
from algorithms.streaming.ColorDetection.views import ColorDetectionControlWidget
from algorithms.streaming.ColorDetection.services import ColorDetectionService, HSVConfig, Detection
from core.services.LoggerService import LoggerService
from core.controllers.streaming.base import StreamAlgorithmController
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox
from PySide6.QtCore import Qt, Slot, Signal
from typing import Dict, List, Any
import numpy as np
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')


# Import control widget from views


class ColorDetectionController(StreamAlgorithmController):
    """
    HSV color detection algorithm controller.

    Provides real-time color detection using HSV color space matching
    with support for:
    - Multiple color ranges
    - Adjustable HSV thresholds
    - Motion-based filtering
    - Temporal tracking
    - False positive reduction
    """

    def __init__(self, algorithm_config: Dict[str, Any], theme: str, parent=None):
        """Initialize color detection controller."""
        super().__init__(algorithm_config, theme, parent)

        self.logger = LoggerService()
        self.provides_custom_rendering = True

        # Initialize color detector service
        # IMPORTANT: Don't pass parent so it can be moved to worker thread
        self.color_detector = ColorDetectionService(parent=None)

        # State
        self.detection_count = 0

        # Connect detector signals
        self.color_detector.detectionsReady.connect(self._on_detections_ready)
        self.color_detector.performanceUpdate.connect(self._on_performance_update)

        # Apply initial config from widget to service (setup_ui was called in super().__init__)
        if hasattr(self, 'control_widget'):
            initial_config = self.control_widget.get_config()
            self._on_config_changed(initial_config)

        self.logger.info(f"ColorDetectionController initialized (provides_custom_rendering={self.provides_custom_rendering})")

    def setup_ui(self):
        """Setup the algorithm-specific UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Color Detection Control Widget
        self.control_widget = ColorDetectionControlWidget()
        self.control_widget.configChanged.connect(self._on_config_changed)
        layout.addWidget(self.control_widget)
        
        # Apply initial config from widget to service (if detector is initialized)
        if hasattr(self, 'color_detector'):
            initial_config = self.control_widget.get_config()
            self._on_config_changed(initial_config)

    def process_frame(self, frame: np.ndarray, timestamp: float) -> List[Dict]:
        """
        Process a frame for color detection.

        Args:
            frame: Input frame (BGR format)
            timestamp: Frame timestamp

        Returns:
            List of detection dictionaries
        """
        try:
            # Detect colors
            detections = self.color_detector.detect_colors(frame, timestamp)

            # Convert to standard format
            detection_dicts = []
            for detection in detections:
                color_id = detection.color_id if detection.color_id is not None else 0
                detection_dicts.append({
                    'bbox': detection.bbox,
                    'area': detection.area,
                    'confidence': detection.confidence,
                    'class_name': f"Color_{color_id}",
                    'color_id': color_id,
                    'mean_color': detection.mean_color
                })

            self.detection_count += len(detections)

            # Emit detections
            self.detectionsReady.emit(detection_dicts)

            # Create and emit annotated frame
            annotated_frame = self.color_detector.create_annotated_frame(frame, detections)
            self.logger.debug(f"Emitting frameProcessed signal (frame shape: {annotated_frame.shape})")
            self.frameProcessed.emit(annotated_frame)

            return detection_dicts

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            # Still emit the original frame so video display doesn't freeze
            self.frameProcessed.emit(frame.copy())
            return []

    @Slot(list, float, np.ndarray)
    def _on_detections_ready(self, detections: List[Detection], timestamp: float, annotated_frame: np.ndarray):
        """Handle detection results from service."""
        # Already handled in process_frame
        pass

    @Slot(dict)
    def _on_performance_update(self, metrics: dict):
        """Handle performance metrics update."""
        fps = metrics.get('fps', 0)
        processing_time = metrics.get('avg_processing_time_ms', 0)
        self._emit_status(f"FPS: {fps:.1f} | Processing: {processing_time:.1f}ms")

    @Slot(dict)
    def _on_config_changed(self, config: dict):
        """Handle configuration change from HSV controls."""
        hsv_config = self._convert_to_hsv_config(config)
        self.color_detector.update_config(hsv_config)
        self._emit_config_changed()

    def _convert_to_hsv_config(self, ui_config: dict) -> HSVConfig:
        """Convert UI config to HSVConfig object."""
        # Get target_color_rgb from first color range if available
        color_ranges = ui_config.get('color_ranges', [])
        if color_ranges and len(color_ranges) > 0:
            first_color = color_ranges[0]['color']
            if isinstance(first_color, QColor):
                target_color_rgb = (first_color.red(), first_color.green(), first_color.blue())
            else:
                target_color_rgb = (255, 0, 0)
        else:
            target_color_rgb = (255, 0, 0)

        # Create HSVConfig with required parameter
        config = HSVConfig(
            target_color_rgb=target_color_rgb,
            min_area=ui_config.get('min_area', 100),
            max_area=ui_config.get('max_area', 100000),
            processing_resolution=ui_config.get('processing_resolution', None),
            confidence_threshold=ui_config.get('confidence_threshold', 0.5),
            show_labels=ui_config.get('render_text', False),  # Map render_text to show_labels
            show_detections=ui_config.get('render_shape', 1) != 3  # Map render_shape != Off to show_detections
        )

        # Set optional parameters if provided
        if color_ranges and len(color_ranges) > 0:
            first_range = color_ranges[0]
            config.hue_threshold = first_range.get('hue_plus', 20)
            config.saturation_threshold = first_range.get('sat_plus', 50)
            config.value_threshold = first_range.get('val_plus', 50)

            # Convert all color ranges to hsv_ranges_list format for multi-color detection
            # The service expects hsv_ranges_list with normalized values (0-1)
            hsv_ranges_list = []
            for color_range in color_ranges:
                color = color_range.get('color', QColor(255, 0, 0))
                if isinstance(color, QColor):
                    # Convert QColor to HSV (0-1 normalized)
                    # getHsvF() returns (h, s, v, alpha) - we only need h, s, v
                    h, s, v, _ = color.getHsvF()
                else:
                    # Fallback if color is not QColor
                    h, s, v = 0.0, 1.0, 1.0

                # Convert thresholds from OpenCV format to normalized format
                # hue_minus/hue_plus are in 0-179 range, convert to normalized 0-1
                h_minus = color_range.get('hue_minus', 20) / 179.0
                h_plus = color_range.get('hue_plus', 20) / 179.0
                # sat_minus/sat_plus are in 0-255 range, convert to normalized 0-1
                s_minus = color_range.get('sat_minus', 50) / 255.0
                s_plus = color_range.get('sat_plus', 50) / 255.0
                # val_minus/val_plus are in 0-255 range, convert to normalized 0-1
                v_minus = color_range.get('val_minus', 50) / 255.0
                v_plus = color_range.get('val_plus', 50) / 255.0

                hsv_ranges_list.append({
                    'h': h,
                    's': s,
                    'v': v,
                    'h_minus': h_minus,
                    'h_plus': h_plus,
                    's_minus': s_minus,
                    's_plus': s_plus,
                    'v_minus': v_minus,
                    'v_plus': v_plus
                })

            config.hsv_ranges_list = hsv_ranges_list

        return config

    # Required interface methods

    def get_config(self) -> Dict[str, Any]:
        """Get current algorithm configuration."""
        return self.control_widget.get_config()

    def set_config(self, config: Dict[str, Any]):
        """Apply algorithm configuration."""
        # Update processing resolution in InputProcessingTab
        if ('processing_width' in config and 'processing_height' in config and
                hasattr(self.control_widget, 'input_processing_tab')):
            width = config['processing_width']
            height = config['processing_height']
            self.control_widget.input_processing_tab.set_processing_resolution(width, height)

        # Update rendering config in RenderingTab
        if hasattr(self.control_widget, 'rendering_tab'):
            rendering_config = {}
            for key in ['render_shape', 'render_text', 'render_contours', 
                       'use_detection_color_for_rendering', 'max_detections_to_render']:
                if key in config:
                    rendering_config[key] = config[key]
            if rendering_config:
                self.control_widget.rendering_tab.set_config(rendering_config)

        # Update control widget with config
        if 'color_ranges' in config:
            self.control_widget.color_ranges = config['color_ranges']
            if hasattr(self.control_widget, '_update_color_ranges_display'):
                self.control_widget._update_color_ranges_display()

        # Set min_area and max_area on spinboxes if provided
        if 'min_area' in config and hasattr(self.control_widget, 'min_area_spinbox'):
            self.control_widget.min_area_spinbox.setValue(config['min_area'])
        if 'max_area' in config and hasattr(self.control_widget, 'max_area_spinbox'):
            self.control_widget.max_area_spinbox.setValue(config['max_area'])
        if 'confidence_threshold' in config and hasattr(self.control_widget, 'confidence_spinbox'):
            self.control_widget.confidence_spinbox.setValue(config['confidence_threshold'])

        # Apply other config as needed
        self._on_config_changed(config)

    def get_stats(self) -> Dict[str, str]:
        """Get algorithm-specific statistics."""
        return {
            'Total Detections': str(self.detection_count)
        }

    def reset(self):
        """Reset algorithm state."""
        self.color_detector.reset()
        self.detection_count = 0

    def cleanup(self):
        """Clean up algorithm resources."""
        # ColorDetectionService doesn't have a cleanup method - resources are managed automatically
        # If cleanup is needed in the future, it can be added to the service
        if hasattr(self.color_detector, 'cleanup'):
            self.color_detector.cleanup()
        self.logger.info("ColorDetectionController cleaned up")
