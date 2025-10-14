"""
IntegratedDetectionViewer.py - Real-time integrated anomaly detection viewer

Full-featured GUI for the integrated detection system combining motion detection,
color quantization, fusion, and temporal smoothing with comprehensive parameter controls.
"""

# Set environment variable to avoid numpy compatibility issues - MUST be first
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')

import cv2
import numpy as np
import time
from typing import Optional, List, Dict, Any

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit, QSpinBox, QFrame,
                               QGroupBox, QGridLayout, QTextEdit, QSplitter,
                               QCheckBox, QComboBox, QMessageBox, QStatusBar,
                               QSlider, QFileDialog, QTabWidget, QListWidget, QDoubleSpinBox)

from core.services.RTMPStreamService import StreamManager, StreamType
from core.services.RealtimeIntegratedDetectionService import (
    RealtimeIntegratedDetector,
    IntegratedDetectionConfig,
    MotionAlgorithm,
    FusionMode,
    Detection
)
from core.services.VideoRecordingService import RecordingManager
from core.services.LoggerService import LoggerService


class VideoDisplayWidget(QLabel):
    """Optimized video display widget for real-time streaming."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        self.setMaximumSize(16777215, 16777215)
        self.setStyleSheet("QLabel { background-color: black; border: 1px solid gray; }")
        self.setAlignment(Qt.AlignCenter)
        self.setText("No Stream Connected")
        self.setScaledContents(False)
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_frame(self, frame: np.ndarray):
        """Update display with new frame."""
        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create QImage and QPixmap
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)

            # Scale to fit widget while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"Error updating frame: {e}")


class IntegratedDetectionControlWidget(QWidget):
    """Control widget for integrated detection parameters organized in tabs."""

    configChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the control interface with tabbed organization."""
        layout = QVBoxLayout(self)

        # Create tab widget for organized controls
        self.tabs = QTabWidget()

        # Tab 1: Input & Processing
        self.tab_input = self._create_input_tab()
        self.tabs.addTab(self.tab_input, "Input & Processing")

        # Tab 2: Motion Detection
        self.tab_motion = self._create_motion_tab()
        self.tabs.addTab(self.tab_motion, "Motion Detection")

        # Tab 3: Color Anomaly
        self.tab_color = self._create_color_tab()
        self.tabs.addTab(self.tab_color, "Color Anomaly")

        # Tab 4: Fusion & Temporal
        self.tab_fusion = self._create_fusion_tab()
        self.tabs.addTab(self.tab_fusion, "Fusion & Temporal")

        # Tab 5: False Positive Reduction
        self.tab_fpr = self._create_fpr_tab()
        self.tabs.addTab(self.tab_fpr, "False Pos. Reduction")

        # Tab 6: Rendering
        self.tab_render = self._create_rendering_tab()
        self.tabs.addTab(self.tab_render, "Rendering")

        layout.addWidget(self.tabs)

    def _create_input_tab(self) -> QWidget:
        """Create Input & Processing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Processing Resolution
        res_group = QGroupBox("Processing Resolution")
        res_layout = QGridLayout(res_group)

        res_layout.addWidget(QLabel("Width:"), 0, 0)
        self.processing_width = QSpinBox()
        self.processing_width.setRange(320, 3840)
        self.processing_width.setValue(1280)
        res_layout.addWidget(self.processing_width, 0, 1)

        res_layout.addWidget(QLabel("Height:"), 1, 0)
        self.processing_height = QSpinBox()
        self.processing_height.setRange(240, 2160)
        self.processing_height.setValue(720)
        res_layout.addWidget(self.processing_height, 1, 1)

        layout.addWidget(res_group)

        # Performance Options
        perf_group = QGroupBox("Performance Options")
        perf_layout = QVBoxLayout(perf_group)

        self.threaded_capture = QCheckBox("Use Threaded Capture (30-200% FPS boost)")
        self.threaded_capture.setChecked(False)
        perf_layout.addWidget(self.threaded_capture)

        self.render_at_processing_res = QCheckBox("Render at Processing Resolution (faster for high-res)")
        self.render_at_processing_res.setChecked(False)
        perf_layout.addWidget(self.render_at_processing_res)

        layout.addWidget(perf_group)
        layout.addStretch()

        return widget

    def _create_motion_tab(self) -> QWidget:
        """Create Motion Detection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Motion
        self.enable_motion = QCheckBox("Enable Motion Detection")
        self.enable_motion.setChecked(False)
        layout.addWidget(self.enable_motion)

        # Algorithm Selection
        algo_group = QGroupBox("Algorithm")
        algo_layout = QGridLayout(algo_group)

        algo_layout.addWidget(QLabel("Type:"), 0, 0)
        self.motion_algorithm = QComboBox()
        self.motion_algorithm.addItems(["FRAME_DIFF", "MOG2", "KNN"])
        self.motion_algorithm.setCurrentText("MOG2")
        algo_layout.addWidget(self.motion_algorithm, 0, 1)

        layout.addWidget(algo_group)

        # Detection Parameters
        param_group = QGroupBox("Detection Parameters")
        param_layout = QGridLayout(param_group)

        row = 0
        param_layout.addWidget(QLabel("Motion Threshold:"), row, 0)
        self.motion_threshold = QSpinBox()
        self.motion_threshold.setRange(1, 255)
        self.motion_threshold.setValue(10)
        param_layout.addWidget(self.motion_threshold, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Min Area (px):"), row, 0)
        self.min_detection_area = QSpinBox()
        self.min_detection_area.setRange(1, 100000)
        self.min_detection_area.setValue(5)
        param_layout.addWidget(self.min_detection_area, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Max Area (px):"), row, 0)
        self.max_detection_area = QSpinBox()
        self.max_detection_area.setRange(10, 1000000)
        self.max_detection_area.setValue(1000)
        param_layout.addWidget(self.max_detection_area, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Blur Kernel (odd):"), row, 0)
        self.blur_kernel_size = QSpinBox()
        self.blur_kernel_size.setRange(1, 21)
        self.blur_kernel_size.setSingleStep(2)
        self.blur_kernel_size.setValue(5)
        param_layout.addWidget(self.blur_kernel_size, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Morphology Kernel:"), row, 0)
        self.morphology_kernel_size = QSpinBox()
        self.morphology_kernel_size.setRange(1, 21)
        self.morphology_kernel_size.setSingleStep(2)
        self.morphology_kernel_size.setValue(3)
        param_layout.addWidget(self.morphology_kernel_size, row, 1)

        layout.addWidget(param_group)

        # Persistence Filter
        persist_group = QGroupBox("Persistence Filter")
        persist_layout = QGridLayout(persist_group)

        persist_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.persistence_frames = QSpinBox()
        self.persistence_frames.setRange(2, 30)
        self.persistence_frames.setValue(3)
        persist_layout.addWidget(self.persistence_frames, 0, 1)

        persist_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.persistence_threshold = QSpinBox()
        self.persistence_threshold.setRange(1, 30)
        self.persistence_threshold.setValue(2)
        persist_layout.addWidget(self.persistence_threshold, 1, 1)

        layout.addWidget(persist_group)

        # Background Subtraction
        bg_group = QGroupBox("Background Subtraction (MOG2/KNN)")
        bg_layout = QGridLayout(bg_group)

        bg_layout.addWidget(QLabel("History Frames:"), 0, 0)
        self.bg_history = QSpinBox()
        self.bg_history.setRange(10, 500)
        self.bg_history.setValue(50)
        bg_layout.addWidget(self.bg_history, 0, 1)

        bg_layout.addWidget(QLabel("Variance Threshold:"), 1, 0)
        self.bg_var_threshold = QDoubleSpinBox()
        self.bg_var_threshold.setRange(1.0, 100.0)
        self.bg_var_threshold.setValue(10.0)
        bg_layout.addWidget(self.bg_var_threshold, 1, 1)

        self.bg_detect_shadows = QCheckBox("Detect Shadows (slower)")
        bg_layout.addWidget(self.bg_detect_shadows, 2, 0, 1, 2)

        layout.addWidget(bg_group)

        # Camera Movement
        cam_group = QGroupBox("Camera Movement Detection")
        cam_layout = QVBoxLayout(cam_group)

        self.pause_on_camera_movement = QCheckBox("Pause on Camera Movement")
        self.pause_on_camera_movement.setChecked(True)
        cam_layout.addWidget(self.pause_on_camera_movement)

        cam_thresh_layout = QHBoxLayout()
        cam_thresh_layout.addWidget(QLabel("Threshold:"))
        self.camera_movement_threshold = QSlider(Qt.Horizontal)
        self.camera_movement_threshold.setRange(1, 100)
        self.camera_movement_threshold.setValue(15)
        cam_thresh_layout.addWidget(self.camera_movement_threshold)
        self.camera_movement_label = QLabel("15%")
        cam_thresh_layout.addWidget(self.camera_movement_label)
        cam_layout.addLayout(cam_thresh_layout)

        layout.addWidget(cam_group)
        layout.addStretch()

        return widget

    def _create_color_tab(self) -> QWidget:
        """Create Color Anomaly tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Color
        self.enable_color_quantization = QCheckBox("Enable Color Quantization Detection")
        self.enable_color_quantization.setChecked(True)
        layout.addWidget(self.enable_color_quantization)

        # Quantization Parameters
        quant_group = QGroupBox("Quantization Parameters")
        quant_layout = QGridLayout(quant_group)

        quant_layout.addWidget(QLabel("Quantization Bits:"), 0, 0)
        bits_layout = QHBoxLayout()
        self.color_quantization_bits = QSlider(Qt.Horizontal)
        self.color_quantization_bits.setRange(3, 8)
        self.color_quantization_bits.setValue(4)
        bits_layout.addWidget(self.color_quantization_bits)
        self.color_bits_label = QLabel("4 bits")
        bits_layout.addWidget(self.color_bits_label)
        quant_layout.addLayout(bits_layout, 0, 1)

        quant_layout.addWidget(QLabel("Rarity Percentile:"), 1, 0)
        percentile_layout = QHBoxLayout()
        self.color_rarity_percentile = QSlider(Qt.Horizontal)
        self.color_rarity_percentile.setRange(0, 100)
        self.color_rarity_percentile.setValue(40)
        percentile_layout.addWidget(self.color_rarity_percentile)
        self.color_percentile_label = QLabel("40%")
        percentile_layout.addWidget(self.color_percentile_label)
        quant_layout.addLayout(percentile_layout, 1, 1)

        quant_layout.addWidget(QLabel("Min Area (px):"), 2, 0)
        self.color_min_detection_area = QSpinBox()
        self.color_min_detection_area.setRange(1, 10000)
        self.color_min_detection_area.setValue(15)
        quant_layout.addWidget(self.color_min_detection_area, 2, 1)

        layout.addWidget(quant_group)

        # Hue Expansion
        hue_group = QGroupBox("Hue Expansion")
        hue_layout = QVBoxLayout(hue_group)

        self.enable_hue_expansion = QCheckBox("Enable Hue Expansion")
        self.enable_hue_expansion.setChecked(False)
        hue_layout.addWidget(self.enable_hue_expansion)

        hue_range_layout = QHBoxLayout()
        hue_range_layout.addWidget(QLabel("Expansion Range:"))
        self.hue_expansion_range = QSlider(Qt.Horizontal)
        self.hue_expansion_range.setRange(0, 30)
        self.hue_expansion_range.setValue(5)
        hue_range_layout.addWidget(self.hue_expansion_range)
        self.hue_range_label = QLabel("±5 (~10°)")
        hue_range_layout.addWidget(self.hue_range_label)
        hue_layout.addLayout(hue_range_layout)

        layout.addWidget(hue_group)
        layout.addStretch()

        return widget

    def _create_fusion_tab(self) -> QWidget:
        """Create Fusion & Temporal tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Fusion
        fusion_group = QGroupBox("Detection Fusion")
        fusion_layout = QVBoxLayout(fusion_group)

        self.enable_fusion = QCheckBox("Enable Fusion (when both motion and color enabled)")
        self.enable_fusion.setChecked(False)
        fusion_layout.addWidget(self.enable_fusion)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Fusion Mode:"))
        self.fusion_mode = QComboBox()
        self.fusion_mode.addItems(["UNION", "INTERSECTION", "COLOR_PRIORITY", "MOTION_PRIORITY"])
        self.fusion_mode.setCurrentText("UNION")
        mode_layout.addWidget(self.fusion_mode)
        mode_layout.addStretch()
        fusion_layout.addLayout(mode_layout)

        layout.addWidget(fusion_group)

        # Temporal Voting
        temporal_group = QGroupBox("Temporal Voting")
        temporal_layout = QVBoxLayout(temporal_group)

        self.enable_temporal_voting = QCheckBox("Enable Temporal Voting (reduce flicker)")
        self.enable_temporal_voting.setChecked(True)
        temporal_layout.addWidget(self.enable_temporal_voting)

        window_layout = QGridLayout()
        window_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.temporal_window_frames = QSpinBox()
        self.temporal_window_frames.setRange(2, 30)
        self.temporal_window_frames.setValue(10)
        window_layout.addWidget(self.temporal_window_frames, 0, 1)

        window_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.temporal_threshold_frames = QSpinBox()
        self.temporal_threshold_frames.setRange(1, 30)
        self.temporal_threshold_frames.setValue(10)
        window_layout.addWidget(self.temporal_threshold_frames, 1, 1)

        temporal_layout.addLayout(window_layout)
        layout.addWidget(temporal_group)
        layout.addStretch()

        return widget

    def _create_fpr_tab(self) -> QWidget:
        """Create False Positive Reduction tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Aspect Ratio Filter
        aspect_group = QGroupBox("Aspect Ratio Filter")
        aspect_layout = QVBoxLayout(aspect_group)

        self.enable_aspect_ratio_filter = QCheckBox("Enable Aspect Ratio Filtering")
        self.enable_aspect_ratio_filter.setChecked(True)
        aspect_layout.addWidget(self.enable_aspect_ratio_filter)

        ratio_layout = QGridLayout()
        ratio_layout.addWidget(QLabel("Min Ratio:"), 0, 0)
        self.min_aspect_ratio = QDoubleSpinBox()
        self.min_aspect_ratio.setRange(0.1, 10.0)
        self.min_aspect_ratio.setValue(0.2)
        self.min_aspect_ratio.setSingleStep(0.1)
        ratio_layout.addWidget(self.min_aspect_ratio, 0, 1)

        ratio_layout.addWidget(QLabel("Max Ratio:"), 1, 0)
        self.max_aspect_ratio = QDoubleSpinBox()
        self.max_aspect_ratio.setRange(0.1, 20.0)
        self.max_aspect_ratio.setValue(5.0)
        self.max_aspect_ratio.setSingleStep(0.1)
        ratio_layout.addWidget(self.max_aspect_ratio, 1, 1)

        aspect_layout.addLayout(ratio_layout)
        layout.addWidget(aspect_group)

        # Color Exclusion
        exclusion_group = QGroupBox("Color Exclusion (Background Learning)")
        exclusion_layout = QVBoxLayout(exclusion_group)

        self.enable_color_exclusion = QCheckBox("Enable Color Exclusion")
        self.enable_color_exclusion.setChecked(False)
        exclusion_layout.addWidget(self.enable_color_exclusion)

        exclusion_layout.addWidget(QLabel("Excluded Hue Ranges:"))
        self.excluded_ranges_list = QListWidget()
        self.excluded_ranges_list.setMaximumHeight(100)
        exclusion_layout.addWidget(self.excluded_ranges_list)

        button_layout = QHBoxLayout()
        self.sample_region_button = QPushButton("Sample Region (draw on video)")
        button_layout.addWidget(self.sample_region_button)
        self.clear_exclusions_button = QPushButton("Clear All")
        button_layout.addWidget(self.clear_exclusions_button)
        exclusion_layout.addLayout(button_layout)

        layout.addWidget(exclusion_group)
        layout.addStretch()

        return widget

    def _create_rendering_tab(self) -> QWidget:
        """Create Rendering tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Shape Options
        shape_group = QGroupBox("Shape Options")
        shape_layout = QGridLayout(shape_group)

        shape_layout.addWidget(QLabel("Shape Mode:"), 0, 0)
        self.render_shape = QComboBox()
        self.render_shape.addItems(["Box", "Circle", "Dot", "Off"])
        self.render_shape.setCurrentText("Circle")
        shape_layout.addWidget(self.render_shape, 0, 1)

        layout.addWidget(shape_group)

        # Text & Contours
        vis_group = QGroupBox("Visual Options")
        vis_layout = QVBoxLayout(vis_group)

        self.render_text = QCheckBox("Show Text Labels (slower)")
        vis_layout.addWidget(self.render_text)

        self.render_contours = QCheckBox("Show Contours (slowest)")
        vis_layout.addWidget(self.render_contours)

        self.use_detection_color = QCheckBox("Use Detection Color (hue @ 100% sat/val for color anomalies)")
        self.use_detection_color.setChecked(False)
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
        limit_layout.addWidget(self.max_detections_to_render, 0, 1)

        layout.addWidget(limit_group)

        # Overlay Options
        overlay_group = QGroupBox("Overlay Options")
        overlay_layout = QVBoxLayout(overlay_group)

        self.show_timing_overlay = QCheckBox("Show Timing Overlay (FPS, metrics)")
        self.show_timing_overlay.setChecked(True)
        overlay_layout.addWidget(self.show_timing_overlay)

        layout.addWidget(overlay_group)
        layout.addStretch()

        return widget

    def connect_signals(self):
        """Connect all control signals."""
        # Processing
        self.processing_width.valueChanged.connect(self.emit_config)
        self.processing_height.valueChanged.connect(self.emit_config)
        self.threaded_capture.toggled.connect(self.emit_config)
        self.render_at_processing_res.toggled.connect(self.emit_config)

        # Motion
        self.enable_motion.toggled.connect(self.emit_config)
        self.motion_algorithm.currentTextChanged.connect(self.emit_config)
        self.motion_threshold.valueChanged.connect(self.emit_config)
        self.min_detection_area.valueChanged.connect(self.emit_config)
        self.max_detection_area.valueChanged.connect(self.emit_config)
        self.blur_kernel_size.valueChanged.connect(self.emit_config)
        self.morphology_kernel_size.valueChanged.connect(self.emit_config)
        self.persistence_frames.valueChanged.connect(self.emit_config)
        self.persistence_threshold.valueChanged.connect(self.emit_config)
        self.bg_history.valueChanged.connect(self.emit_config)
        self.bg_var_threshold.valueChanged.connect(self.emit_config)
        self.bg_detect_shadows.toggled.connect(self.emit_config)
        self.pause_on_camera_movement.toggled.connect(self.emit_config)
        self.camera_movement_threshold.valueChanged.connect(self.update_camera_movement_label)

        # Color
        self.enable_color_quantization.toggled.connect(self.emit_config)
        self.color_quantization_bits.valueChanged.connect(self.update_color_bits_label)
        self.color_rarity_percentile.valueChanged.connect(self.update_color_percentile_label)
        self.color_min_detection_area.valueChanged.connect(self.emit_config)
        self.enable_hue_expansion.toggled.connect(self.emit_config)
        self.hue_expansion_range.valueChanged.connect(self.update_hue_range_label)

        # Fusion
        self.enable_fusion.toggled.connect(self.emit_config)
        self.fusion_mode.currentTextChanged.connect(self.emit_config)
        self.enable_temporal_voting.toggled.connect(self.emit_config)
        self.temporal_window_frames.valueChanged.connect(self.emit_config)
        self.temporal_threshold_frames.valueChanged.connect(self.emit_config)

        # FPR
        self.enable_aspect_ratio_filter.toggled.connect(self.emit_config)
        self.min_aspect_ratio.valueChanged.connect(self.emit_config)
        self.max_aspect_ratio.valueChanged.connect(self.emit_config)
        self.enable_color_exclusion.toggled.connect(self.emit_config)

        # Rendering
        self.render_shape.currentTextChanged.connect(self.emit_config)
        self.render_text.toggled.connect(self.emit_config)
        self.render_contours.toggled.connect(self.emit_config)
        self.use_detection_color.toggled.connect(self.emit_config)
        self.max_detections_to_render.valueChanged.connect(self.emit_config)
        self.show_timing_overlay.toggled.connect(self.emit_config)

    def update_camera_movement_label(self):
        """Update camera movement threshold label."""
        value = self.camera_movement_threshold.value()
        self.camera_movement_label.setText(f"{value}%")
        self.emit_config()

    def update_color_bits_label(self):
        """Update color bits label."""
        value = self.color_quantization_bits.value()
        self.color_bits_label.setText(f"{value} bits")
        self.emit_config()

    def update_color_percentile_label(self):
        """Update color percentile label."""
        value = self.color_rarity_percentile.value()
        self.color_percentile_label.setText(f"{value}%")
        self.emit_config()

    def update_hue_range_label(self):
        """Update hue expansion range label."""
        value = self.hue_expansion_range.value()
        self.hue_range_label.setText(f"±{value} (~{value*2}°)")
        self.emit_config()

    def emit_config(self):
        """Emit current configuration."""
        config = self.get_config()
        self.configChanged.emit(config)

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        # Map string algorithm names to enum
        algo_map = {
            "FRAME_DIFF": MotionAlgorithm.FRAME_DIFF,
            "MOG2": MotionAlgorithm.MOG2,
            "KNN": MotionAlgorithm.KNN
        }

        # Map string fusion modes to enum
        fusion_map = {
            "UNION": FusionMode.UNION,
            "INTERSECTION": FusionMode.INTERSECTION,
            "COLOR_PRIORITY": FusionMode.COLOR_PRIORITY,
            "MOTION_PRIORITY": FusionMode.MOTION_PRIORITY
        }

        # Map shape names to indices
        shape_map = {"Box": 0, "Circle": 1, "Dot": 2, "Off": 3}

        config = {
            'processing_width': self.processing_width.value(),
            'processing_height': self.processing_height.value(),
            'use_threaded_capture': self.threaded_capture.isChecked(),
            'render_at_processing_res': self.render_at_processing_res.isChecked(),

            'enable_motion': self.enable_motion.isChecked(),
            'motion_algorithm': algo_map[self.motion_algorithm.currentText()],
            'motion_threshold': self.motion_threshold.value(),
            'min_detection_area': self.min_detection_area.value(),
            'max_detection_area': self.max_detection_area.value(),
            'blur_kernel_size': self.blur_kernel_size.value(),
            'morphology_kernel_size': self.morphology_kernel_size.value(),
            'persistence_frames': self.persistence_frames.value(),
            'persistence_threshold': self.persistence_threshold.value(),
            'bg_history': self.bg_history.value(),
            'bg_var_threshold': self.bg_var_threshold.value(),
            'bg_detect_shadows': self.bg_detect_shadows.isChecked(),
            'pause_on_camera_movement': self.pause_on_camera_movement.isChecked(),
            'camera_movement_threshold': self.camera_movement_threshold.value() / 100.0,

            'enable_color_quantization': self.enable_color_quantization.isChecked(),
            'color_quantization_bits': self.color_quantization_bits.value(),
            'color_rarity_percentile': float(self.color_rarity_percentile.value()),
            'color_min_detection_area': self.color_min_detection_area.value(),
            'enable_hue_expansion': self.enable_hue_expansion.isChecked(),
            'hue_expansion_range': self.hue_expansion_range.value(),

            'enable_fusion': self.enable_fusion.isChecked(),
            'fusion_mode': fusion_map[self.fusion_mode.currentText()],
            'enable_temporal_voting': self.enable_temporal_voting.isChecked(),
            'temporal_window_frames': self.temporal_window_frames.value(),
            'temporal_threshold_frames': self.temporal_threshold_frames.value(),

            'enable_aspect_ratio_filter': self.enable_aspect_ratio_filter.isChecked(),
            'min_aspect_ratio': self.min_aspect_ratio.value(),
            'max_aspect_ratio': self.max_aspect_ratio.value(),
            'enable_color_exclusion': self.enable_color_exclusion.isChecked(),

            'render_shape': shape_map[self.render_shape.currentText()],
            'render_text': self.render_text.isChecked(),
            'render_contours': self.render_contours.isChecked(),
            'use_detection_color_for_rendering': self.use_detection_color.isChecked(),
            'max_detections_to_render': self.max_detections_to_render.value(),
            'show_timing_overlay': self.show_timing_overlay.isChecked(),
        }

        return config


class StreamControlWidget(QWidget):
    """Stream connection and control widget."""

    connectRequested = Signal(str, str)
    disconnectRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup stream control interface."""
        layout = QVBoxLayout(self)

        # Connection group
        connection_group = QGroupBox("Stream Connection")
        connection_layout = QGridLayout(connection_group)

        # Stream URL with browse button for files
        connection_layout.addWidget(QLabel("Stream URL:"), 0, 0)

        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Click to browse for video file...")
        url_layout.addWidget(self.url_input, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setToolTip("Browse for video file")
        url_layout.addWidget(self.browse_button)

        connection_layout.addLayout(url_layout, 0, 1)

        # Stream type
        connection_layout.addWidget(QLabel("Stream Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["File", "HDMI Capture", "RTMP Stream"])
        connection_layout.addWidget(self.type_combo, 1, 1)

        # Connection buttons
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.disconnect_button.setEnabled(False)

        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        # Status display
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")

        # Performance display
        performance_group = QGroupBox("Performance")
        performance_layout = QGridLayout(performance_group)

        self.fps_label = QLabel("FPS: --")
        self.latency_label = QLabel("Processing: -- ms")
        self.detections_label = QLabel("Detections: --")

        performance_layout.addWidget(self.fps_label, 0, 0)
        performance_layout.addWidget(self.latency_label, 0, 1)
        performance_layout.addWidget(self.detections_label, 1, 0)

        # Add to main layout
        layout.addWidget(connection_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(performance_group)
        layout.addStretch()

    def connect_signals(self):
        """Connect UI signals."""
        self.connect_button.clicked.connect(self.request_connect)
        self.disconnect_button.clicked.connect(self.disconnectRequested.emit)
        self.type_combo.currentTextChanged.connect(self.on_stream_type_changed)
        self.browse_button.clicked.connect(self.browse_for_file)
        self.url_input.mousePressEvent = self.on_url_input_clicked

    def on_stream_type_changed(self, stream_type: str):
        """Handle stream type selection changes."""
        if stream_type == "HDMI Capture":
            self.url_input.setPlaceholderText("Device index (0, 1, 2, etc.)")
            self.url_input.setText("0")
            self.browse_button.setVisible(False)
        elif stream_type == "File":
            self.url_input.setPlaceholderText("Click to browse for video file...")
            self.url_input.setText("")
            self.browse_button.setVisible(True)
        elif stream_type == "RTMP Stream":
            self.url_input.setPlaceholderText("rtmp://server:port/app/stream")
            self.url_input.setText("")
            self.browse_button.setVisible(False)

    def request_connect(self):
        """Request stream connection."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid stream URL.")
            return

        stream_type = self.type_combo.currentText().lower()
        self.connectRequested.emit(url, stream_type)

    def update_connection_status(self, connected: bool, message: str):
        """Update connection status display."""
        if connected:
            self.status_label.setText(f"Status: {message}")
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        else:
            self.status_label.setText(f"Status: {message}")
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def update_performance(self, stats: Dict[str, Any]):
        """Update performance display."""
        fps = stats.get('fps', 0)
        processing_time = stats.get('total_ms', 0)
        detection_count = stats.get('detection_count', 0)

        self.fps_label.setText(f"FPS: {fps:.1f}")
        self.latency_label.setText(f"Processing: {processing_time:.1f} ms")
        self.detections_label.setText(f"Detections: {detection_count}")

    def browse_for_file(self):
        """Open file dialog to select video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)"
        )
        if file_path:
            self.url_input.setText(file_path)

    def on_url_input_clicked(self, event):
        """Handle clicks on URL input field."""
        if self.type_combo.currentText() == "File":
            self.browse_for_file()
        else:
            QLineEdit.mousePressEvent(self.url_input, event)


class IntegratedDetectionViewer(QMainWindow):
    """Main integrated detection viewer window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Core services
        self.stream_manager = StreamManager()
        self.integrated_detector = RealtimeIntegratedDetector()
        self.recording_manager = RecordingManager("./recordings")

        # UI components
        self.video_display = None
        self.integrated_controls = None
        self.stream_controls = None

        # State
        self.is_detecting = False
        self.is_recording = False
        self.current_detections = []
        self.current_frame = None
        self.stream_resolution = (640, 480)

        # Excluded hue ranges (for color exclusion)
        self.excluded_hue_ranges = []

        self.setup_ui()
        self.connect_signals()

        # Apply default configuration
        self.update_detection_config(self.integrated_controls.get_config())

        self.logger.info("Integrated Detection Viewer initialized")

    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("ADIAT - Real-Time Integrated Detection")
        self.setMinimumSize(1400, 900)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)

        # Video display area
        video_widget = QWidget()
        video_layout = QVBoxLayout(video_widget)

        self.video_display = VideoDisplayWidget()
        video_layout.addWidget(self.video_display, 1)

        # Detection info panel
        info_panel = QTextEdit()
        info_panel.setMaximumHeight(120)
        info_panel.setReadOnly(True)
        info_panel.setPlaceholderText("Detection information will appear here...")
        video_layout.addWidget(info_panel, 0)
        self.info_panel = info_panel

        # Control panel
        control_widget = QWidget()
        control_widget.setMaximumWidth(450)
        control_layout = QVBoxLayout(control_widget)

        # Stream controls
        self.stream_controls = StreamControlWidget()
        control_layout.addWidget(self.stream_controls)

        # Integrated detection controls
        self.integrated_controls = IntegratedDetectionControlWidget()
        control_layout.addWidget(self.integrated_controls)

        # Add to splitter
        splitter.addWidget(video_widget)
        splitter.addWidget(control_widget)
        splitter.setSizes([900, 500])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Connect to stream to begin detection")

    def connect_signals(self):
        """Connect all signals and slots."""
        # Stream manager signals
        self.stream_manager.frameReceived.connect(self.process_frame)
        self.stream_manager.connectionChanged.connect(self.on_connection_changed)

        # Integrated detector signals
        self.integrated_detector.frameProcessed.connect(self.on_frame_processed)
        self.integrated_detector.performanceUpdate.connect(self.on_performance_update)

        # UI control signals
        self.stream_controls.connectRequested.connect(self.connect_to_stream)
        self.stream_controls.disconnectRequested.connect(self.disconnect_from_stream)
        self.integrated_controls.configChanged.connect(self.update_detection_config)

        # Color exclusion buttons
        self.integrated_controls.sample_region_button.clicked.connect(self.enable_region_sampling)
        self.integrated_controls.clear_exclusions_button.clicked.connect(self.clear_color_exclusions)

    def connect_to_stream(self, url: str, stream_type_str: str):
        """Connect to stream."""
        try:
            # Convert string to enum
            stream_type = StreamType.RTMP
            if stream_type_str.lower() == 'file':
                stream_type = StreamType.FILE
            elif stream_type_str.lower() == 'hdmi capture':
                stream_type = StreamType.HDMI_CAPTURE

            success = self.stream_manager.connect_to_stream(url, stream_type)
            if success:
                self.is_detecting = True
                self.status_bar.showMessage(f"Connecting to {url}...")
            else:
                QMessageBox.critical(self, "Connection Failed", "Failed to initiate stream connection.")

        except Exception as e:
            self.logger.error(f"Error connecting to stream: {e}")
            QMessageBox.critical(self, "Connection Error", f"Error connecting to stream:\n{str(e)}")

    def disconnect_from_stream(self):
        """Disconnect from current stream."""
        self.stream_manager.disconnect_stream()
        self.is_detecting = False
        self.video_display.setText("No Stream Connected")
        self.info_panel.clear()
        self.status_bar.showMessage("Disconnected")

    def update_detection_config(self, config_dict: Dict[str, Any]):
        """Update integrated detection configuration."""
        try:
            # Create IntegratedDetectionConfig from dictionary
            config = IntegratedDetectionConfig(
                processing_width=config_dict['processing_width'],
                processing_height=config_dict['processing_height'],
                use_threaded_capture=config_dict['use_threaded_capture'],
                render_at_processing_res=config_dict['render_at_processing_res'],

                enable_motion=config_dict['enable_motion'],
                motion_algorithm=config_dict['motion_algorithm'],
                motion_threshold=config_dict['motion_threshold'],
                min_detection_area=config_dict['min_detection_area'],
                max_detection_area=config_dict['max_detection_area'],
                blur_kernel_size=config_dict['blur_kernel_size'],
                morphology_kernel_size=config_dict['morphology_kernel_size'],
                persistence_frames=config_dict['persistence_frames'],
                persistence_threshold=config_dict['persistence_threshold'],
                bg_history=config_dict['bg_history'],
                bg_var_threshold=config_dict['bg_var_threshold'],
                bg_detect_shadows=config_dict['bg_detect_shadows'],
                pause_on_camera_movement=config_dict['pause_on_camera_movement'],
                camera_movement_threshold=config_dict['camera_movement_threshold'],

                enable_color_quantization=config_dict['enable_color_quantization'],
                color_quantization_bits=config_dict['color_quantization_bits'],
                color_rarity_percentile=config_dict['color_rarity_percentile'],
                color_min_detection_area=config_dict['color_min_detection_area'],
                enable_hue_expansion=config_dict['enable_hue_expansion'],
                hue_expansion_range=config_dict['hue_expansion_range'],

                enable_fusion=config_dict['enable_fusion'],
                fusion_mode=config_dict['fusion_mode'],
                enable_temporal_voting=config_dict['enable_temporal_voting'],
                temporal_window_frames=config_dict['temporal_window_frames'],
                temporal_threshold_frames=config_dict['temporal_threshold_frames'],

                enable_aspect_ratio_filter=config_dict['enable_aspect_ratio_filter'],
                min_aspect_ratio=config_dict['min_aspect_ratio'],
                max_aspect_ratio=config_dict['max_aspect_ratio'],
                enable_color_exclusion=config_dict['enable_color_exclusion'],
                excluded_hue_ranges=self.excluded_hue_ranges,

                render_shape=config_dict['render_shape'],
                render_text=config_dict['render_text'],
                render_contours=config_dict['render_contours'],
                use_detection_color_for_rendering=config_dict['use_detection_color_for_rendering'],
                max_detections_to_render=config_dict['max_detections_to_render'],
                show_timing_overlay=config_dict['show_timing_overlay'],
            )

            self.integrated_detector.update_config(config)

        except Exception as e:
            self.logger.error(f"Error updating config: {e}")

    def process_frame(self, frame: np.ndarray, timestamp: float):
        """Process incoming frame from stream."""
        if not self.is_detecting:
            return

        try:
            if frame is None or frame.size == 0:
                return

            # Store current frame
            self.current_frame = frame.copy()

            # Process through integrated detector
            annotated_frame, detections, timings = self.integrated_detector.process_frame(frame, timestamp)

            # Update display
            self.video_display.update_frame(annotated_frame)

            # Store detections
            self.current_detections = detections

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")

    def on_frame_processed(self, annotated_frame: np.ndarray, detections: List[Detection], metrics):
        """Handle frame processing completion."""
        # Update info panel
        if detections:
            info_text = f"Detection Results ({len(detections)} found):\n"
            for i, detection in enumerate(detections[:5]):
                x, y, w, h = detection.bbox
                info_text += f"  #{i+1}: Type({detection.detection_type}) Pos({x},{y}) " \
                            f"Size({w}x{h}) Area({int(detection.area)}px) Conf({detection.confidence:.2f})\n"
        else:
            info_text = "No detections found."

        self.info_panel.setPlainText(info_text)

    def on_performance_update(self, stats: Dict[str, Any]):
        """Handle performance statistics updates."""
        self.stream_controls.update_performance(stats)

    def on_connection_changed(self, connected: bool, message: str):
        """Handle connection status changes."""
        self.stream_controls.update_connection_status(connected, message)
        if connected:
            self.status_bar.showMessage(f"Connected - {message}")
        else:
            self.status_bar.showMessage(f"Disconnected - {message}")

    def enable_region_sampling(self):
        """Enable region sampling mode (not yet implemented - placeholder)."""
        QMessageBox.information(self, "Feature Coming Soon",
                              "Interactive region sampling will be added in a future update.\n\n"
                              "For now, use the keyboard controls in the standalone script:\n"
                              "- Press 'b' to enable sampling mode\n"
                              "- Click and drag on video to sample region")

    def clear_color_exclusions(self):
        """Clear all color exclusions."""
        self.excluded_hue_ranges.clear()
        self.integrated_controls.excluded_ranges_list.clear()
        self.update_detection_config(self.integrated_controls.get_config())
        self.logger.info("Color exclusions cleared")

    def closeEvent(self, event):
        """Handle window close event."""
        self.disconnect_from_stream()
        if self.is_recording:
            self.recording_manager.stop_recording()
        event.accept()
