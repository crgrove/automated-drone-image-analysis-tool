"""
MotionDetectionController.py - Motion detection algorithm controller for ADIAT

Provides motion detection algorithm controls integrated into StreamViewerWindow.
Now follows the StreamAlgorithmController pattern matching image analysis algorithms.
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QComboBox, QSlider, QSpinBox, QCheckBox, QPushButton

from core.controllers.streaming.base import StreamAlgorithmController
from core.services.LoggerService import LoggerService
from algorithms.streaming.MotionDetection.services import (
    MotionDetectionService, DetectionMode, MotionAlgorithm,
    MotionDetection, CameraMotion
)


class MotionDetectionController(StreamAlgorithmController):
    """
    Motion detection algorithm controller.

    Provides controls for real-time motion detection with support for:
    - Dual-mode detection (static/moving camera)
    - Multiple detection algorithms
    - Camera motion compensation for drones
    - Real-time visualization
    - Adjustable detection parameters
    """

    def __init__(self, algorithm_config: Dict[str, Any], theme: str, parent=None):
        """Initialize motion detection controller."""
        super().__init__(algorithm_config, theme, parent)

        self.logger = LoggerService()
        self.provides_custom_rendering = True

        # Initialize motion detector service
        self.motion_detector = MotionDetectionService()

        # State tracking
        self._detection_count = 0
        self._last_detection_time = None

        # Connect motion detector signals
        self.motion_detector.detectionsReady.connect(self._on_detections_ready)
        self.motion_detector.performanceUpdate.connect(self._on_performance_update)
        self.motion_detector.modeChanged.connect(self._on_mode_auto_changed)

        # self.logger.info("MotionDetectionController initialized")

    def setup_ui(self):
        """Setup the algorithm-specific UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Detection Mode Group
        mode_group = QGroupBox("Detection Mode")
        mode_layout = QVBoxLayout(mode_group)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Auto', 'Static Camera', 'Moving Camera'])
        self.mode_combo.setCurrentText('Auto')
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(QLabel("Mode:"))
        mode_layout.addWidget(self.mode_combo)

        self.mode_status_label = QLabel("Auto Mode: Detecting...")
        mode_layout.addWidget(self.mode_status_label)

        layout.addWidget(mode_group)

        # Algorithm Group
        algorithm_group = QGroupBox("Algorithm")
        algorithm_layout = QVBoxLayout(algorithm_group)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            'Frame Difference',
            'MOG2 Background',
            'KNN Background',
            'Optical Flow',
            'Feature Matching'
        ])
        self.algorithm_combo.setCurrentText('MOG2 Background')
        self.algorithm_combo.currentTextChanged.connect(self._on_algorithm_changed)
        algorithm_layout.addWidget(QLabel("Algorithm:"))
        algorithm_layout.addWidget(self.algorithm_combo)

        layout.addWidget(algorithm_group)

        # Parameters Group
        params_group = QGroupBox("Detection Parameters")
        params_layout = QVBoxLayout(params_group)

        # Sensitivity
        self.sensitivity_label = QLabel("Sensitivity: 50%")
        params_layout.addWidget(self.sensitivity_label)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(0, 100)
        self.sensitivity_slider.setValue(50)
        self.sensitivity_slider.valueChanged.connect(self._on_sensitivity_changed)
        params_layout.addWidget(self.sensitivity_slider)

        # Min Area
        min_area_layout = QHBoxLayout()
        min_area_layout.addWidget(QLabel("Min Area:"))
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setRange(10, 50000)
        self.min_area_spinbox.setValue(500)
        self.min_area_spinbox.valueChanged.connect(self._on_min_area_changed)
        min_area_layout.addWidget(self.min_area_spinbox)
        params_layout.addLayout(min_area_layout)

        # Max Area
        max_area_layout = QHBoxLayout()
        max_area_layout.addWidget(QLabel("Max Area:"))
        self.max_area_spinbox = QSpinBox()
        self.max_area_spinbox.setRange(100, 500000)
        self.max_area_spinbox.setValue(100000)
        self.max_area_spinbox.valueChanged.connect(self._on_max_area_changed)
        max_area_layout.addWidget(self.max_area_spinbox)
        params_layout.addLayout(max_area_layout)

        # Threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(1, 100)
        self.threshold_spinbox.setValue(25)
        self.threshold_spinbox.valueChanged.connect(self._on_threshold_changed)
        threshold_layout.addWidget(self.threshold_spinbox)
        params_layout.addLayout(threshold_layout)

        # Compensation Strength
        self.compensation_label = QLabel("Compensation: 80%")
        params_layout.addWidget(self.compensation_label)
        self.compensation_slider = QSlider(Qt.Horizontal)
        self.compensation_slider.setRange(0, 100)
        self.compensation_slider.setValue(80)
        self.compensation_slider.valueChanged.connect(self._on_compensation_changed)
        params_layout.addWidget(self.compensation_slider)

        layout.addWidget(params_group)

        # Visualization Group
        viz_group = QGroupBox("Visualization")
        viz_layout = QVBoxLayout(viz_group)

        self.show_vectors_checkbox = QCheckBox("Show Motion Vectors")
        self.show_vectors_checkbox.setChecked(True)
        self.show_vectors_checkbox.toggled.connect(self._on_show_vectors_changed)
        viz_layout.addWidget(self.show_vectors_checkbox)

        self.show_camera_checkbox = QCheckBox("Show Camera Motion")
        self.show_camera_checkbox.setChecked(True)
        self.show_camera_checkbox.toggled.connect(self._on_show_camera_changed)
        viz_layout.addWidget(self.show_camera_checkbox)

        layout.addWidget(viz_group)

        # Stats Group
        stats_group = QGroupBox("Detection Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.detection_count_label = QLabel("Detections: 0")
        stats_layout.addWidget(self.detection_count_label)

        self.camera_motion_label = QLabel("Camera Motion: None")
        stats_layout.addWidget(self.camera_motion_label)

        self.fps_label = QLabel("FPS: 0.0")
        stats_layout.addWidget(self.fps_label)

        self.processing_time_label = QLabel("Processing: 0.0ms")
        stats_layout.addWidget(self.processing_time_label)

        layout.addWidget(stats_group)

        layout.addStretch()

    def process_frame(self, frame: np.ndarray, timestamp: float) -> List[Dict]:
        """
        Process a frame for motion detection.

        Args:
            frame: Input frame (BGR format)
            timestamp: Frame timestamp

        Returns:
            List of detection dictionaries
        """
        # Process frame through motion detector
        self.motion_detector.process_frame(frame)

        # Return empty list for now (detections come via signal)
        # This will be updated when detections are ready
        return []

    @Slot(list, object, np.ndarray)
    def _on_detections_ready(self, detections: List[MotionDetection],
                             camera_motion: Optional[CameraMotion],
                             annotated_frame: np.ndarray):
        """Handle motion detection results."""
        # Update detection count
        if detections:
            self._detection_count += len(detections)
            self._last_detection_time = datetime.now()

        # Convert to standard detection format
        detection_dicts = []
        for detection in detections:
            # Handle both MotionDetection objects and dicts
            if isinstance(detection, dict):
                detection_dicts.append(detection)
            else:
                detection_dicts.append({
                    'bbox': detection.bbox,
                    'area': detection.area,
                    'confidence': 1.0,  # Motion detection doesn't have confidence
                    'class_name': 'Motion',
                    'velocity': getattr(detection, 'velocity', None),
                    'is_compensated': getattr(detection, 'is_compensated', False)
                })

        # Emit detections
        self.detectionsReady.emit(detection_dicts)

        # Emit processed frame
        self.frameProcessed.emit(annotated_frame)

        # Update UI
        self._update_detection_display(detections, camera_motion)

    def _update_detection_display(self, detections: List[MotionDetection],
                                  camera_motion: Optional[CameraMotion]):
        """Update detection information display."""
        # Update detection count
        total_area = sum(d.area for d in detections)
        avg_area = total_area / len(detections) if detections else 0
        self.detection_count_label.setText(
            f"Detections: {len(detections)} | Total Area: {int(total_area)} | Avg: {int(avg_area)}"
        )

        # Update camera motion info
        if camera_motion:
            motion_text = f"Camera Motion: ({camera_motion.global_velocity[0]:.1f}, "
            motion_text += f"{camera_motion.global_velocity[1]:.1f}) "
            motion_text += f"Confidence: {camera_motion.confidence:.2f}"
            self.camera_motion_label.setText(motion_text)
        else:
            self.camera_motion_label.setText("Camera Motion: None")

    @Slot(dict)
    def _on_performance_update(self, metrics: dict):
        """Handle performance metrics update."""
        fps = metrics.get('fps', 0)
        processing_time = metrics.get('avg_processing_time_ms', 0)
        mode = metrics.get('mode', 'unknown')
        confidence = metrics.get('mode_confidence', 0)
        gpu_enabled = metrics.get('gpu_enabled', False)

        # Update performance labels
        gpu_text = " (GPU)" if gpu_enabled else " (CPU)"
        self.fps_label.setText(f"FPS: {fps:.1f}{gpu_text}")
        self.processing_time_label.setText(f"Processing: {processing_time:.1f}ms")

        # Update mode info if in auto mode
        if self.mode_combo.currentText() == 'Auto':
            self.mode_status_label.setText(f"Auto Mode: {mode.title()} ({confidence:.0%})")

    @Slot(str)
    def _on_mode_auto_changed(self, new_mode: str):
        """Handle automatic mode change."""
        # self.logger.info(f"Motion detector auto-switched to {new_mode} mode")
        self.mode_status_label.setText(f"Auto Mode: {new_mode.title()}")

    # Parameter change handlers

    @Slot(str)
    def _on_mode_changed(self, mode_text: str):
        """Handle detection mode change."""
        mode_map = {
            'Auto': DetectionMode.AUTO,
            'Static Camera': DetectionMode.STATIC,
            'Moving Camera': DetectionMode.MOVING
        }
        mode = mode_map.get(mode_text, DetectionMode.AUTO)
        self.motion_detector.update_config(mode=mode)

        # Enable/disable compensation based on mode
        self.compensation_slider.setEnabled(mode != DetectionMode.STATIC)
        self.compensation_label.setEnabled(mode != DetectionMode.STATIC)

        self._emit_config_changed()

    @Slot(str)
    def _on_algorithm_changed(self, algorithm_text: str):
        """Handle algorithm change."""
        algorithm_map = {
            'Frame Difference': MotionAlgorithm.FRAME_DIFF,
            'MOG2 Background': MotionAlgorithm.MOG2,
            'KNN Background': MotionAlgorithm.KNN,
            'Optical Flow': MotionAlgorithm.OPTICAL_FLOW,
            'Feature Matching': MotionAlgorithm.FEATURE_MATCH
        }
        algorithm = algorithm_map.get(algorithm_text, MotionAlgorithm.MOG2)
        self.motion_detector.update_config(algorithm=algorithm)
        self._emit_config_changed()

    @Slot(int)
    def _on_sensitivity_changed(self, value: int):
        """Handle sensitivity change."""
        self.sensitivity_label.setText(f"Sensitivity: {value}%")
        sensitivity = value / 100.0
        self.motion_detector.update_config(sensitivity=sensitivity)
        self._emit_config_changed()

    @Slot(int)
    def _on_min_area_changed(self, value: int):
        """Handle minimum area change."""
        self.motion_detector.update_config(min_area=value)
        self._emit_config_changed()

    @Slot(int)
    def _on_max_area_changed(self, value: int):
        """Handle maximum area change."""
        self.motion_detector.update_config(max_area=value)
        self._emit_config_changed()

    @Slot(int)
    def _on_threshold_changed(self, value: int):
        """Handle threshold change."""
        self.motion_detector.update_config(motion_threshold=value)
        self._emit_config_changed()

    @Slot(int)
    def _on_compensation_changed(self, value: int):
        """Handle compensation strength change."""
        self.compensation_label.setText(f"Compensation: {value}%")
        compensation = value / 100.0
        self.motion_detector.update_config(compensation_strength=compensation)
        self._emit_config_changed()

    @Slot(bool)
    def _on_show_vectors_changed(self, checked: bool):
        """Handle show vectors checkbox."""
        self.motion_detector.update_config(show_vectors=checked)

    @Slot(bool)
    def _on_show_camera_changed(self, checked: bool):
        """Handle show camera motion checkbox."""
        self.motion_detector.update_config(show_camera_motion=checked)

    # Required interface methods

    def get_config(self) -> Dict[str, Any]:
        """Get current algorithm configuration."""
        return {
            'mode': self.mode_combo.currentText(),
            'algorithm': self.algorithm_combo.currentText(),
            'sensitivity': self.sensitivity_slider.value(),
            'min_area': self.min_area_spinbox.value(),
            'max_area': self.max_area_spinbox.value(),
            'threshold': self.threshold_spinbox.value(),
            'compensation': self.compensation_slider.value(),
            'show_vectors': self.show_vectors_checkbox.isChecked(),
            'show_camera_motion': self.show_camera_checkbox.isChecked()
        }

    def set_config(self, config: Dict[str, Any]):
        """Apply algorithm configuration."""
        if 'mode' in config:
            self.mode_combo.setCurrentText(config['mode'])
        if 'algorithm' in config:
            self.algorithm_combo.setCurrentText(config['algorithm'])
        if 'sensitivity' in config:
            self.sensitivity_slider.setValue(config['sensitivity'])
        if 'min_area' in config:
            self.min_area_spinbox.setValue(config['min_area'])
        if 'max_area' in config:
            self.max_area_spinbox.setValue(config['max_area'])
        if 'threshold' in config:
            self.threshold_spinbox.setValue(config['threshold'])
        if 'compensation' in config:
            self.compensation_slider.setValue(config['compensation'])
        if 'show_vectors' in config:
            self.show_vectors_checkbox.setChecked(config['show_vectors'])
        if 'show_camera_motion' in config:
            self.show_camera_checkbox.setChecked(config['show_camera_motion'])

    def get_stats(self) -> Dict[str, str]:
        """Get algorithm-specific statistics."""
        return {
            'Total Detections': str(self._detection_count),
            'Last Detection': self._format_last_detection_time()
        }

    def _format_last_detection_time(self) -> str:
        """Format last detection time."""
        if self._last_detection_time:
            time_since = (datetime.now() - self._last_detection_time).total_seconds()
            return f"{time_since:.1f}s ago"
        return "Never"

    def reset(self):
        """Reset algorithm state."""
        self.motion_detector.reset()
        self._detection_count = 0
        self._last_detection_time = None
        self.detection_count_label.setText("Detections: 0")

    def cleanup(self):
        """Clean up algorithm resources."""
        # MotionDetectionService doesn't have a cleanup method - resources are managed automatically
        # If cleanup is needed in the future, it can be added to the service
        if hasattr(self.motion_detector, 'cleanup'):
            self.motion_detector.cleanup()
        # self.logger.info("MotionDetectionController cleaned up")
