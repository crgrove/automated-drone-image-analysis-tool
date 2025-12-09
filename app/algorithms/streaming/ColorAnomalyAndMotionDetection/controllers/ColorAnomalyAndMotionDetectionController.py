"""
ColorAnomalyAndMotionDetectionController.py - Color anomaly and motion detection algorithm controller

Combines motion detection, color quantization, fusion, and temporal smoothing
for comprehensive anomaly detection. Integrated into StreamViewerWindow following
the StreamAlgorithmController pattern.
"""

# Set environment variables
from algorithms.streaming.ColorAnomalyAndMotionDetection.views.ColorAnomalyAndMotionDetectionControlWidget import ColorAnomalyAndMotionDetectionControlWidget
from algorithms.streaming.ColorAnomalyAndMotionDetection.services import (
    ColorAnomalyAndMotionDetectionOrchestrator,
    ColorAnomalyAndMotionDetectionConfig,
    MotionAlgorithm,
    FusionMode,
    Detection
)
from core.services.LoggerService import LoggerService
from core.controllers.streaming.base import StreamAlgorithmController
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget,
                               QLabel, QSpinBox, QDoubleSpinBox, QCheckBox,
                               QComboBox, QHBoxLayout, QGridLayout)
from PySide6.QtCore import Qt, Slot, Signal
from typing import Dict, List, Any
import numpy as np
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')


class ColorAnomalyAndMotionDetectionController(StreamAlgorithmController):
    """
    Color anomaly and motion detection algorithm controller.

    Provides comprehensive anomaly detection by combining:
    - Motion detection with multiple algorithms
    - Color quantization and anomaly detection
    - Multi-modal fusion
    - Temporal smoothing and tracking
    - False positive reduction
    """

    def __init__(self, algorithm_config: Dict[str, Any], theme: str, parent=None):
        """Initialize color anomaly and motion detection controller."""
        super().__init__(algorithm_config, theme, parent)

        self.logger = LoggerService()
        self.provides_custom_rendering = True

        # Initialize color anomaly and motion detector orchestrator
        self.integrated_detector = ColorAnomalyAndMotionDetectionOrchestrator()

        # State
        self.detection_count = 0

        # Connect detector signals
        self.integrated_detector.frameProcessed.connect(self._on_frame_processed)
        self.integrated_detector.performanceUpdate.connect(self._on_performance_update)

        # Apply initial config from widget to service (setup_ui was called in super().__init__)
        if hasattr(self, 'integrated_controls'):
            initial_config = self.integrated_controls.get_config()
            self._on_config_changed(initial_config)

        # self.logger.info("ColorAnomalyAndMotionDetectionController initialized")

    def setup_ui(self):
        """Setup the algorithm-specific UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Color Anomaly and Motion Detection Control Widget (algorithm-specific)
        self.integrated_controls = ColorAnomalyAndMotionDetectionControlWidget()
        self.integrated_controls.configChanged.connect(self._on_config_changed)
        layout.addWidget(self.integrated_controls)

        # Apply initial config from widget to service (if detector is initialized)
        if hasattr(self, 'integrated_detector'):
            initial_config = self.integrated_controls.get_config()
            self._on_config_changed(initial_config)

    def process_frame(self, frame: np.ndarray, timestamp: float) -> List[Dict]:
        """
        Process a frame for integrated detection.

        Args:
            frame: Input frame (BGR format)
            timestamp: Frame timestamp

        Returns:
            List of detection dictionaries
        """
        try:
            # Perform integrated detection - returns (annotated_frame, detections, timings)
            annotated_frame, detections, timings = self.integrated_detector.process_frame(frame, timestamp)

            # Convert to standard format
            detection_dicts = []
            for detection in detections:
                detection_dicts.append({
                    'bbox': detection.bbox,
                    'centroid': detection.centroid,
                    'area': detection.area,
                    'confidence': detection.confidence,
                    'class_name': detection.detection_type,
                    'detection_type': detection.detection_type,
                    'timestamp': detection.timestamp,
                    'metadata': detection.metadata
                })

            self.detection_count += len(detections)

            # Emit detections
            self.detectionsReady.emit(detection_dicts)

            # Emit annotated frame (already annotated by process_frame)
            self.frameProcessed.emit(annotated_frame)

            return detection_dicts

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return []

    @Slot(np.ndarray, list, object)
    def _on_frame_processed(self, annotated_frame: np.ndarray, detections: List[Detection], metrics: object):
        """Handle frame processed signal from service."""
        # Convert detections to standard format
        detection_dicts = []
        for detection in detections:
            detection_dicts.append({
                'bbox': detection.bbox,
                'area': detection.area,
                'confidence': detection.confidence,
                'class_name': detection.detection_type,
                'centroid': detection.centroid
            })

        self.detection_count += len(detections)

        # Emit detections
        self.detectionsReady.emit(detection_dicts)

        # Emit processed frame
        self.frameProcessed.emit(annotated_frame)

    @Slot(dict)
    def _on_performance_update(self, metrics: dict):
        """Handle performance metrics update."""
        fps = metrics.get('fps', 0)
        processing_time = metrics.get('avg_processing_time_ms', 0)
        self._emit_status(f"FPS: {fps:.1f} | Processing: {processing_time:.1f}ms")

    @Slot(dict)
    def _on_config_changed(self, config: dict):
        """Handle configuration change from controls."""
        integrated_config = self._convert_to_config(config)
        self.integrated_detector.update_config(integrated_config)
        self._emit_config_changed()

    def _convert_to_config(self, ui_config: dict) -> ColorAnomalyAndMotionDetectionConfig:
        """Convert UI config to ColorAnomalyAndMotionDetectionConfig object."""
        # Get existing config as base
        base_config = self.integrated_detector.config

        # Handle processing resolution - widget now returns processing_width/height directly
        processing_width = ui_config.get('processing_width', base_config.processing_width)
        processing_height = ui_config.get('processing_height', base_config.processing_height)

        # Handle "Original" resolution (99999 means no downsampling)
        if processing_width >= 99999 or processing_height >= 99999:
            # Use very large values - service will handle this as "no downsampling"
            processing_width = base_config.processing_width
            processing_height = base_config.processing_height

        # Map motion algorithm (widget returns enum)
        motion_algorithm = ui_config.get('motion_algorithm', base_config.motion_algorithm)
        if not isinstance(motion_algorithm, MotionAlgorithm):
            motion_algorithm = base_config.motion_algorithm

        # Map fusion mode (widget returns enum)
        fusion_mode = ui_config.get('fusion_mode', base_config.fusion_mode)
        if not isinstance(fusion_mode, FusionMode):
            fusion_mode = base_config.fusion_mode

        return ColorAnomalyAndMotionDetectionConfig(
            processing_width=processing_width,
            processing_height=processing_height,
            target_fps=ui_config.get('target_fps', base_config.target_fps),
            enable_motion=ui_config.get('enable_motion', base_config.enable_motion),
            enable_color_quantization=ui_config.get('enable_color_quantization', base_config.enable_color_quantization),
            motion_algorithm=motion_algorithm,
            min_detection_area=ui_config.get('min_detection_area', base_config.min_detection_area),
            max_detection_area=ui_config.get('max_detection_area', base_config.max_detection_area),
            motion_threshold=ui_config.get('motion_threshold', base_config.motion_threshold),
            blur_kernel_size=ui_config.get('blur_kernel_size', base_config.blur_kernel_size),
            morphology_kernel_size=ui_config.get('morphology_kernel_size', base_config.morphology_kernel_size),
            enable_morphology=base_config.enable_morphology,  # Keep default (not in UI)
            bg_history=ui_config.get('bg_history', base_config.bg_history),
            bg_var_threshold=ui_config.get('bg_var_threshold', base_config.bg_var_threshold),
            bg_detect_shadows=ui_config.get('bg_detect_shadows', base_config.bg_detect_shadows),
            persistence_frames=ui_config.get('persistence_frames', base_config.persistence_frames),
            persistence_threshold=ui_config.get('persistence_threshold', base_config.persistence_threshold),
            pause_on_camera_movement=ui_config.get('pause_on_camera_movement', base_config.pause_on_camera_movement),
            camera_movement_threshold=ui_config.get('camera_movement_threshold', base_config.camera_movement_threshold),
            color_quantization_bits=ui_config.get('color_quantization_bits', base_config.color_quantization_bits),
            color_rarity_percentile=ui_config.get('color_rarity_percentile', base_config.color_rarity_percentile),
            color_min_detection_area=ui_config.get('color_min_detection_area', base_config.color_min_detection_area),
            color_max_detection_area=ui_config.get('color_max_detection_area', base_config.color_max_detection_area),
            enable_hue_expansion=ui_config.get('enable_hue_expansion', base_config.enable_hue_expansion),
            hue_expansion_range=ui_config.get('hue_expansion_range', base_config.hue_expansion_range),
            enable_fusion=ui_config.get('enable_fusion', base_config.enable_fusion),
            fusion_mode=fusion_mode,
            enable_temporal_voting=ui_config.get('enable_temporal_voting', base_config.enable_temporal_voting),
            temporal_window_frames=ui_config.get('temporal_window_frames', base_config.temporal_window_frames),
            temporal_threshold_frames=ui_config.get('temporal_threshold_frames', base_config.temporal_threshold_frames),
            enable_aspect_ratio_filter=ui_config.get('enable_aspect_ratio_filter', base_config.enable_aspect_ratio_filter),
            min_aspect_ratio=ui_config.get('min_aspect_ratio', base_config.min_aspect_ratio),
            max_aspect_ratio=ui_config.get('max_aspect_ratio', base_config.max_aspect_ratio),
            enable_detection_clustering=ui_config.get('enable_detection_clustering', base_config.enable_detection_clustering),
            clustering_distance=ui_config.get('clustering_distance', base_config.clustering_distance),
            enable_color_exclusion=ui_config.get('enable_color_exclusion', base_config.enable_color_exclusion),
            excluded_hue_ranges=ui_config.get('excluded_hue_ranges', base_config.excluded_hue_ranges),
            show_detections=ui_config.get('show_detections', base_config.show_detections),
            max_detections_to_render=ui_config.get('max_detections_to_render', base_config.max_detections_to_render),
            render_shape=ui_config.get('render_shape', base_config.render_shape),
            render_text=ui_config.get('render_text', base_config.render_text),
            render_contours=ui_config.get('render_contours', base_config.render_contours),
            render_at_processing_res=ui_config.get('render_at_processing_res', base_config.render_at_processing_res),
            use_detection_color_for_rendering=ui_config.get('use_detection_color_for_rendering', base_config.use_detection_color_for_rendering),
            # Processing mask parameters (from shared FrameTab)
            mask_enabled=ui_config.get('mask_enabled', base_config.mask_enabled),
            frame_mask_enabled=ui_config.get('frame_mask_enabled', base_config.frame_mask_enabled),
            image_mask_enabled=ui_config.get('image_mask_enabled', base_config.image_mask_enabled),
            frame_buffer_pixels=ui_config.get('frame_buffer_pixels', base_config.frame_buffer_pixels),
            mask_image_path=ui_config.get('mask_image_path', base_config.mask_image_path),
            show_mask_overlay=ui_config.get('show_mask_overlay', base_config.show_mask_overlay)
        )

    # Required interface methods

    def get_config(self) -> Dict[str, Any]:
        """Get current algorithm configuration."""
        return self.integrated_controls.get_config()

    def set_config(self, config: Dict[str, Any]):
        """Apply algorithm configuration."""
        if not hasattr(self, 'integrated_controls'):
            self._on_config_changed(config)
            return

        # Update processing resolution in InputProcessingTab
        if ('processing_width' in config and 'processing_height' in config and
                hasattr(self.integrated_controls, 'input_processing_tab')):
            width = config['processing_width']
            height = config['processing_height']
            self.integrated_controls.input_processing_tab.set_processing_resolution(width, height)

        # Update rendering config in RenderingTab
        if hasattr(self.integrated_controls, 'rendering_tab'):
            rendering_config = {}
            for key in ['render_shape', 'render_text', 'render_contours',
                        'use_detection_color_for_rendering', 'max_detections_to_render']:
                if key in config:
                    rendering_config[key] = config[key]
            if rendering_config:
                self.integrated_controls.rendering_tab.set_config(rendering_config)

        # Update frame/mask config in FrameTab
        if hasattr(self.integrated_controls, 'frame_tab'):
            frame_config = {}
            for key in ['mask_enabled', 'frame_mask_enabled', 'image_mask_enabled',
                        'frame_buffer_pixels', 'mask_image_path', 'show_mask_overlay']:
                if key in config:
                    frame_config[key] = config[key]
            if frame_config:
                self.integrated_controls.frame_tab.set_config(frame_config)

        # Update motion detection checkbox
        if 'enable_motion' in config and hasattr(self.integrated_controls, 'enable_motion'):
            self.integrated_controls.enable_motion.setChecked(bool(config['enable_motion']))

        # Update motion algorithm combo box
        if 'motion_algorithm' in config and hasattr(self.integrated_controls, 'motion_algorithm'):
            motion_algo = config['motion_algorithm']
            # Handle both string and enum values
            if isinstance(motion_algo, str):
                # Map "MOG2 Background" to "MOG2" for combo box
                if motion_algo == "MOG2 Background":
                    motion_algo = "MOG2"
                if motion_algo in ["FRAME_DIFF", "MOG2", "KNN"]:
                    self.integrated_controls.motion_algorithm.setCurrentText(motion_algo)
            else:
                # If it's an enum, convert to string
                algo_str = str(motion_algo).split('.')[-1]  # Get enum name
                if algo_str in ["FRAME_DIFF", "MOG2", "KNN"]:
                    self.integrated_controls.motion_algorithm.setCurrentText(algo_str)

        # Update motion threshold
        if 'motion_threshold' in config and hasattr(self.integrated_controls, 'motion_threshold'):
            self.integrated_controls.motion_threshold.setValue(config['motion_threshold'])

        # Update color quantization checkbox
        if 'enable_color_quantization' in config and hasattr(self.integrated_controls, 'enable_color_quantization'):
            self.integrated_controls.enable_color_quantization.setChecked(bool(config['enable_color_quantization']))

        # Update color rarity percentile slider
        if 'color_rarity_percentile' in config and hasattr(self.integrated_controls, 'color_rarity_percentile'):
            percentile = float(config['color_rarity_percentile'])
            # Clamp to slider range (0-100)
            percentile = max(0, min(100, int(percentile)))
            self.integrated_controls.color_rarity_percentile.setValue(percentile)
            # Update the label if the method exists
            if hasattr(self.integrated_controls, 'update_color_percentile_label'):
                self.integrated_controls.update_color_percentile_label()

        # Update detection area spinboxes
        if 'min_detection_area' in config and hasattr(self.integrated_controls, 'min_detection_area'):
            self.integrated_controls.min_detection_area.setValue(config['min_detection_area'])
        if 'max_detection_area' in config and hasattr(self.integrated_controls, 'max_detection_area'):
            self.integrated_controls.max_detection_area.setValue(config['max_detection_area'])
        if 'color_min_detection_area' in config and hasattr(self.integrated_controls, 'color_min_detection_area'):
            self.integrated_controls.color_min_detection_area.setValue(config['color_min_detection_area'])
        if 'color_max_detection_area' in config and hasattr(self.integrated_controls, 'color_max_detection_area'):
            self.integrated_controls.color_max_detection_area.setValue(config['color_max_detection_area'])
        # Also handle min_area/max_area for compatibility
        if 'min_area' in config and 'min_detection_area' not in config:
            if hasattr(self.integrated_controls, 'min_detection_area'):
                self.integrated_controls.min_detection_area.setValue(config['min_area'])
        if 'max_area' in config and 'max_detection_area' not in config:
            if hasattr(self.integrated_controls, 'max_detection_area'):
                self.integrated_controls.max_detection_area.setValue(config['max_area'])

        # Get the updated config from the controls (includes all defaults)
        # This ensures we have a complete config with all fields, not just wizard fields
        updated_config = self.integrated_controls.get_config()

        # Apply the config to update the detector
        self._on_config_changed(updated_config)

    def get_stats(self) -> Dict[str, str]:
        """Get algorithm-specific statistics."""
        return {
            'Total Detections': str(self.detection_count)
        }

    def reset(self):
        """Reset algorithm state."""
        # Reset orchestrator metrics
        if hasattr(self.integrated_detector, 'reset_metrics'):
            self.integrated_detector.reset_metrics()
        self.detection_count = 0

    def cleanup(self):
        """Clean up algorithm resources for new video session.

        Resets all internal state including:
        - Background subtractor models (MOG2/KNN)
        - Temporal detection history
        - Performance metrics
        """
        if hasattr(self, 'integrated_detector') and self.integrated_detector:
            self.integrated_detector.reset_for_new_video()
        self.detection_count = 0
