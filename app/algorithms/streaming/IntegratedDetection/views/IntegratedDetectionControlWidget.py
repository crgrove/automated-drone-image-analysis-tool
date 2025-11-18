"""
IntegratedDetectionControlWidget.py - Control widget for integrated detection parameters.

This widget provides a tabbed interface for configuring all IntegratedDetectionService
parameters. It matches the original IntegratedDetectionViewer implementation exactly.
"""

from typing import Dict, Any, List, Tuple
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QDoubleSpinBox, QCheckBox,
                               QComboBox, QGroupBox, QSlider)

from core.services.LoggerService import LoggerService
from algorithms.streaming.IntegratedDetection.views.IntegratedDetectionControlWidget_ui import Ui_IntegratedDetectionControlWidget
from algorithms.streaming.IntegratedDetection.services.IntegratedDetectionService import (
    MotionAlgorithm, FusionMode
)


class IntegratedDetectionControlWidget(QWidget, Ui_IntegratedDetectionControlWidget):
    """Control widget for integrated detection parameters."""

    configChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Setup UI from UI file
        self.setupUi(self)

        # Get tab widget reference
        self.tabs = self.tabs  # From Ui_IntegratedDetectionControlWidget

        # Populate tabs with actual controls
        self._populate_tabs()

        # Connect signals
        self.connect_signals()

    def _populate_tabs(self):
        """Populate tabs with control panels."""
        # Clear placeholder tabs
        self.tabs.clear()

        # Add actual tabs - Input & Processing moved to right before Rendering
        self.tabs.addTab(self._create_motion_tab(), "Motion Detection")
        self.tabs.addTab(self._create_color_tab(), "Color Anomaly")
        self.tabs.addTab(self._create_fusion_tab(), "Fusion & Temporal")
        self.tabs.addTab(self._create_fpr_tab(), "False Pos. Reduction")
        self.tabs.addTab(self._create_input_tab(), "Input & Processing")
        self.tabs.addTab(self._create_rendering_tab(), "Rendering")

    def _create_input_tab(self) -> QWidget:
        """Create Input & Processing tab - matches original exactly."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Processing Resolution
        res_group = QGroupBox("Processing Resolution")
        res_layout = QVBoxLayout(res_group)

        # Dropdown for preset resolutions
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.resolution_preset = QComboBox()

        # Common 16:9 resolutions (matching original)
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

    def _create_motion_tab(self) -> QWidget:
        """Create Motion Detection tab - matches original exactly."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Motion
        self.enable_motion = QCheckBox("Enable Motion Detection")
        self.enable_motion.setChecked(False)
        self.enable_motion.setToolTip("Detect moving objects by analyzing frame-to-frame differences.\n"
                                      "Works best for stationary cameras or slow-moving cameras.\n"
                                      "Automatically pauses when excessive camera movement is detected.\n"
                                      "Can be combined with Color Detection for more robust detection.")
        layout.addWidget(self.enable_motion)

        # Algorithm Selection
        algo_group = QGroupBox("Algorithm")
        algo_layout = QGridLayout(algo_group)

        algo_layout.addWidget(QLabel("Type:"), 0, 0)
        self.motion_algorithm = QComboBox()
        self.motion_algorithm.addItems(["FRAME_DIFF", "MOG2", "KNN"])
        self.motion_algorithm.setCurrentText("MOG2")
        self.motion_algorithm.setToolTip("Motion detection algorithm:\n\n"
                                         "• FRAME_DIFF: Simple frame differencing. Fast, sensitive to all motion.\n"
                                         "  Good for: Quick tests, high-contrast scenes.\n\n"
                                         "• MOG2: Gaussian mixture model (recommended). Adapts to lighting changes.\n"
                                         "  Good for: General use, varying lighting, shadows optional.\n\n"
                                         "• KNN: K-nearest neighbors. More robust to noise than MOG2.\n"
                                         "  Good for: Noisy videos, complex backgrounds.")
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
        self.motion_threshold.setToolTip("Minimum pixel intensity change to consider as motion (1-255).\n"
                                         "Lower values = more sensitive, detects subtle motion, more false positives.\n"
                                         "Higher values = less sensitive, only strong motion, fewer false positives.\n"
                                         "Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.")
        param_layout.addWidget(self.motion_threshold, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Min Area (px):"), row, 0)
        self.min_detection_area = QSpinBox()
        self.min_detection_area.setRange(1, 100000)
        self.min_detection_area.setValue(5)
        self.min_detection_area.setToolTip("Minimum detection area in pixels (1-100000).\n"
                                           "Filters out very small detections (noise, insects, raindrops).\n"
                                           "Lower values = detect smaller objects, more noise.\n"
                                           "Higher values = only large objects, less noise.\n"
                                           "Recommended: 5-10 for person detection, 50-100 for vehicle detection.")
        param_layout.addWidget(self.min_detection_area, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Max Area (px):"), row, 0)
        self.max_detection_area = QSpinBox()
        self.max_detection_area.setRange(10, 1000000)
        self.max_detection_area.setValue(1000)
        self.max_detection_area.setToolTip("Maximum detection area in pixels (10-1000000).\n"
                                           "Filters out very large detections (shadows, clouds, global lighting changes).\n"
                                           "Lower values = only small/medium objects.\n"
                                           "Higher values = allow large objects.\n"
                                           "Recommended: 1000 for people, 10000 for vehicles, higher for large objects.")
        param_layout.addWidget(self.max_detection_area, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Blur Kernel (odd):"), row, 0)
        self.blur_kernel_size = QSpinBox()
        self.blur_kernel_size.setRange(1, 21)
        self.blur_kernel_size.setSingleStep(2)
        self.blur_kernel_size.setValue(5)
        self.blur_kernel_size.setToolTip("Gaussian blur kernel size (must be odd: 1, 3, 5, 7, etc.).\n"
                                         "Smooths the frame before motion detection to reduce noise.\n"
                                         "Larger values = more smoothing, less noise, less detail.\n"
                                         "Smaller values = less smoothing, more detail, more noise.\n"
                                         "Recommended: 5 for general use, 1 for no blur, 7-9 for noisy videos.")
        param_layout.addWidget(self.blur_kernel_size, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Morphology Kernel:"), row, 0)
        self.morphology_kernel_size = QSpinBox()
        self.morphology_kernel_size.setRange(1, 21)
        self.morphology_kernel_size.setSingleStep(2)
        self.morphology_kernel_size.setValue(3)
        self.morphology_kernel_size.setToolTip("Morphological operation kernel size (odd numbers: 1, 3, 5, etc.).\n"
                                               "Removes small noise and fills holes in detections.\n"
                                               "Larger values = remove more noise, merge nearby detections.\n"
                                               "Smaller values = preserve detail, keep detections separate.\n"
                                               "Recommended: 3 for general use, 1 for precise edges, 5-7 for noisy videos.")
        param_layout.addWidget(self.morphology_kernel_size, row, 1)

        layout.addWidget(param_group)

        # Persistence Filter
        persist_group = QGroupBox("Persistence Filter")
        persist_layout = QGridLayout(persist_group)

        persist_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.persistence_frames = QSpinBox()
        self.persistence_frames.setRange(2, 30)
        self.persistence_frames.setValue(3)
        self.persistence_frames.setToolTip("Size of temporal window for persistence filtering (2-30 frames).\n"
                                           "Motion must appear in N out of M consecutive frames to be confirmed.\n"
                                           "Larger values = longer memory, more stable, slower response.\n"
                                           "Smaller values = shorter memory, faster response, more flicker.\n"
                                           "Recommended: 3 for 30fps video (100ms window), 5 for 60fps.")
        persist_layout.addWidget(self.persistence_frames, 0, 1)

        persist_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.persistence_threshold = QSpinBox()
        self.persistence_threshold.setRange(1, 30)
        self.persistence_threshold.setValue(2)
        self.persistence_threshold.setToolTip("Number of frames within window where motion must appear (N of M).\n"
                                              "Higher values = more stringent, filters flickering false positives.\n"
                                              "Lower values = more lenient, detects brief/intermittent motion.\n"
                                              "Must be ≤ Window Frames.\n"
                                              "Recommended: 2 (motion in 2 of last 3 frames)")
        persist_layout.addWidget(self.persistence_threshold, 1, 1)

        layout.addWidget(persist_group)

        # Background Subtraction
        bg_group = QGroupBox("Background Subtraction (MOG2/KNN)")
        bg_layout = QGridLayout(bg_group)

        bg_layout.addWidget(QLabel("History Frames:"), 0, 0)
        self.bg_history = QSpinBox()
        self.bg_history.setRange(10, 500)
        self.bg_history.setValue(50)
        self.bg_history.setToolTip("Number of frames to learn background model (10-500).\n"
                                   "Only applies to MOG2 and KNN algorithms.\n"
                                   "Longer history = adapts slower to lighting changes, more stable.\n"
                                   "Shorter history = adapts faster, less stable.\n"
                                   "Recommended: 50 (~1.7 sec at 30fps) for general use.")
        bg_layout.addWidget(self.bg_history, 0, 1)

        bg_layout.addWidget(QLabel("Variance Threshold:"), 1, 0)
        self.bg_var_threshold = QDoubleSpinBox()
        self.bg_var_threshold.setRange(1.0, 100.0)
        self.bg_var_threshold.setValue(10.0)
        self.bg_var_threshold.setToolTip("Variance threshold for background/foreground classification (1.0-100.0).\n"
                                         "Only applies to MOG2 and KNN algorithms.\n"
                                         "Lower values = more sensitive, detects subtle changes, more false positives.\n"
                                         "Higher values = less sensitive, only strong foreground objects.\n"
                                         "Recommended: 10.0 for indoor, 15-20 for outdoor with varying lighting.")
        bg_layout.addWidget(self.bg_var_threshold, 1, 1)

        self.bg_detect_shadows = QCheckBox("Detect Shadows (slower)")
        self.bg_detect_shadows.setToolTip("Enables shadow detection in MOG2 background subtractor.\n"
                                          "Helps distinguish shadows from actual objects (reduces false positives).\n"
                                          "Adds ~10-20% processing overhead.\n"
                                          "Recommended: ON for outdoor scenes with strong shadows, OFF for speed.")
        bg_layout.addWidget(self.bg_detect_shadows, 2, 0, 1, 2)

        layout.addWidget(bg_group)

        # Camera Movement
        cam_group = QGroupBox("Camera Movement Detection")
        cam_layout = QVBoxLayout(cam_group)

        self.pause_on_camera_movement = QCheckBox("Pause on Camera Movement")
        self.pause_on_camera_movement.setChecked(True)
        self.pause_on_camera_movement.setToolTip("Automatically pauses motion detection when camera is moving/panning.\n"
                                                 "Prevents false positives caused by camera movement (entire scene appears to move).\n"
                                                 "Detects camera movement by measuring percentage of frame with motion.\n"
                                                 "Recommended: ON for handheld/drone footage, OFF for stationary tripod cameras.")
        cam_layout.addWidget(self.pause_on_camera_movement)

        cam_thresh_layout = QHBoxLayout()
        cam_thresh_layout.addWidget(QLabel("Threshold:"))
        self.camera_movement_threshold = QSlider(Qt.Horizontal)
        self.camera_movement_threshold.setRange(1, 100)
        self.camera_movement_threshold.setValue(15)
        self.camera_movement_threshold.setToolTip("Percentage of frame with motion to consider as camera movement (1-100%).\n"
                                                  "If more than this % of pixels show motion, pause detection.\n"
                                                  "Lower values = detect camera movement sooner (more pauses).\n"
                                                  "Higher values = tolerate more motion before pausing (fewer pauses).\n"
                                                  "Recommended: 15% for drone/handheld, 30% for shaky tripod.")
        cam_thresh_layout.addWidget(self.camera_movement_threshold)
        self.camera_movement_label = QLabel("15%")
        cam_thresh_layout.addWidget(self.camera_movement_label)
        cam_layout.addLayout(cam_thresh_layout)

        layout.addWidget(cam_group)
        layout.addStretch()

        return widget

    def _create_color_tab(self) -> QWidget:
        """Create Color Anomaly tab - matches original exactly."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Color
        self.enable_color_quantization = QCheckBox("Enable Color Quantization Detection")
        self.enable_color_quantization.setChecked(True)
        self.enable_color_quantization.setToolTip("Detect rare/unusual colors in the scene using color quantization.\n"
                                                  "Finds colors that appear infrequently (statistical anomalies).\n"
                                                  "Works well for: bright colored clothing, vehicles, equipment in natural scenes.\n"
                                                  "Can be combined with Motion Detection for more robust detection.")
        layout.addWidget(self.enable_color_quantization)

        # Quantization Parameters
        quant_group = QGroupBox("Quantization Parameters")
        quant_layout = QGridLayout(quant_group)

        quant_layout.addWidget(QLabel("Quantization Bits:"), 0, 0)
        bits_layout = QHBoxLayout()
        self.color_quantization_bits = QSlider(Qt.Horizontal)
        self.color_quantization_bits.setRange(3, 8)
        self.color_quantization_bits.setValue(4)
        self.color_quantization_bits.setToolTip("Number of bits for color quantization (3-8 bits).\n"
                                                "Controls color histogram resolution.\n"
                                                "Lower bits (3-4) = fewer bins, faster, more grouping, less precise.\n"
                                                "Higher bits (6-8) = more bins, slower, less grouping, more precise.\n"
                                                "Recommended: 4 bits (512 colors) for general use, 5 bits for detailed scenes.")
        bits_layout.addWidget(self.color_quantization_bits)
        self.color_bits_label = QLabel("4 bits")
        bits_layout.addWidget(self.color_bits_label)
        quant_layout.addLayout(bits_layout, 0, 1)

        quant_layout.addWidget(QLabel("Rarity Percentile:"), 1, 0)
        percentile_layout = QHBoxLayout()
        self.color_rarity_percentile = QSlider(Qt.Horizontal)
        self.color_rarity_percentile.setRange(0, 100)
        self.color_rarity_percentile.setValue(30)  # Default 30%
        self.color_rarity_percentile.setToolTip("Rarity threshold as percentile of color histogram (0-100%).\n"
                                                "Detects colors that appear in fewer pixels than this percentile.\n"
                                                "Lower values (10-20%) = only very rare colors (fewer detections).\n"
                                                "Higher values (40-60%) = include more common colors (more detections).\n"
                                                "Recommended: 30% for general use, 15-20% for high-specificity (bright objects only).")
        percentile_layout.addWidget(self.color_rarity_percentile)
        self.color_percentile_label = QLabel("30%")
        percentile_layout.addWidget(self.color_percentile_label)
        quant_layout.addLayout(percentile_layout, 1, 1)

        quant_layout.addWidget(QLabel("Min Area (px):"), 2, 0)
        self.color_min_detection_area = QSpinBox()
        self.color_min_detection_area.setRange(1, 10000)
        self.color_min_detection_area.setValue(15)
        self.color_min_detection_area.setToolTip("Minimum detection area for color anomalies in pixels (1-10000).\n"
                                                 "Filters out very small color patches (noise, specks).\n"
                                                 "Lower values = detect smaller colored objects, more noise.\n"
                                                 "Higher values = only larger colored regions, less noise.\n"
                                                 "Recommended: 15 for person detection, 50 for vehicles.")
        quant_layout.addWidget(self.color_min_detection_area, 2, 1)

        quant_layout.addWidget(QLabel("Max Area (px):"), 3, 0)
        self.color_max_detection_area = QSpinBox()
        self.color_max_detection_area.setRange(100, 1000000)
        self.color_max_detection_area.setValue(50000)
        self.color_max_detection_area.setToolTip("Maximum detection area for color anomalies in pixels (100-1000000).\n"
                                                 "Filters out very large color patches (false positives, large objects).\n"
                                                 "Lower values = only detect smaller colored objects.\n"
                                                 "Higher values = allow larger colored regions.\n"
                                                 "Recommended: 50000 for general use, 10000 for small objects only.")
        quant_layout.addWidget(self.color_max_detection_area, 3, 1)

        layout.addWidget(quant_group)

        # Hue Expansion
        hue_group = QGroupBox("Hue Expansion")
        hue_layout = QVBoxLayout(hue_group)

        self.enable_hue_expansion = QCheckBox("Enable Hue Expansion")
        self.enable_hue_expansion.setChecked(False)  # Default OFF
        self.enable_hue_expansion.setToolTip("Expands detected rare colors to include similar hues.\n"
                                             "Groups similar colors together (e.g., red and orange, blue and cyan).\n"
                                             "Helps detect objects even if exact color varies slightly.\n"
                                             "Recommended: OFF for specific colors (e.g., red jacket only),\n"
                                             "ON for color families (e.g., any warm colors).")
        hue_layout.addWidget(self.enable_hue_expansion)

        hue_range_layout = QHBoxLayout()
        hue_range_layout.addWidget(QLabel("Expansion Range:"))
        self.hue_expansion_range = QSlider(Qt.Horizontal)
        self.hue_expansion_range.setRange(0, 30)
        self.hue_expansion_range.setValue(5)
        self.hue_expansion_range.setToolTip("Hue expansion range in OpenCV hue units (0-30, ~0-60 degrees).\n"
                                            "Expands rare hue detection by ±N hue values.\n"
                                            "Larger values = wider color range, detect more variations.\n"
                                            "Smaller values = narrower color range, more specific.\n"
                                            "Recommended: 5 (~10°) for slight variations, 10-15 (~20-30°) for color families.")
        hue_range_layout.addWidget(self.hue_expansion_range)
        self.hue_range_label = QLabel("±5 (~10°)")
        hue_range_layout.addWidget(self.hue_range_label)
        hue_layout.addLayout(hue_range_layout)

        layout.addWidget(hue_group)
        layout.addStretch()

        return widget

    def _create_fusion_tab(self) -> QWidget:
        """Create Fusion & Temporal tab - matches original exactly."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Fusion
        fusion_group = QGroupBox("Detection Fusion")
        fusion_layout = QVBoxLayout(fusion_group)

        self.enable_fusion = QCheckBox("Enable Fusion (when both motion and color enabled)")
        self.enable_fusion.setChecked(False)  # Default OFF
        self.enable_fusion.setToolTip("Combines motion and color detections when both are enabled.\n"
                                      "Only active when both Motion and Color detection are ON.\n"
                                      "Different modes control how detections are merged.\n"
                                      "Recommended: ON for robust multi-modal detection.")
        fusion_layout.addWidget(self.enable_fusion)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Fusion Mode:"))
        self.fusion_mode = QComboBox()
        self.fusion_mode.addItems(["UNION", "INTERSECTION", "COLOR_PRIORITY", "MOTION_PRIORITY"])
        self.fusion_mode.setCurrentText("UNION")
        self.fusion_mode.setToolTip("How to combine motion and color detections:\n\n"
                                    "• UNION: Show all detections from both (most detections).\n"
                                    "  Use for: Maximum coverage, don't miss anything.\n\n"
                                    "• INTERSECTION: Only show detections found by both (fewest false positives).\n"
                                    "  Use for: High confidence, reduce false positives.\n\n"
                                    "• COLOR_PRIORITY: Show color detections + motion detections that match color.\n"
                                    "  Use for: Trust color more (e.g., bright colored objects).\n\n"
                                    "• MOTION_PRIORITY: Show motion detections + color detections that match motion.\n"
                                    "  Use for: Trust motion more (e.g., moving camouflaged objects).")
        mode_layout.addWidget(self.fusion_mode)
        mode_layout.addStretch()
        fusion_layout.addLayout(mode_layout)

        layout.addWidget(fusion_group)

        # Temporal Voting
        temporal_group = QGroupBox("Temporal Voting")
        temporal_layout = QVBoxLayout(temporal_group)

        self.enable_temporal_voting = QCheckBox("Enable Temporal Voting (reduce flicker)")
        self.enable_temporal_voting.setChecked(True)
        self.enable_temporal_voting.setToolTip("Smooths detections across frames using temporal consistency.\n"
                                               "Detections must appear in N out of M consecutive frames to be confirmed.\n"
                                               "Significantly reduces flickering false positives.\n"
                                               "Recommended: ON for all use cases (default).")
        temporal_layout.addWidget(self.enable_temporal_voting)

        window_layout = QGridLayout()
        window_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.temporal_window_frames = QSpinBox()
        self.temporal_window_frames.setRange(2, 30)
        self.temporal_window_frames.setValue(5)  # Default 5
        self.temporal_window_frames.setToolTip("Size of temporal voting window (2-30 frames).\n"
                                               "Detections must appear in N out of M consecutive frames.\n"
                                               "Larger values = longer memory, more stable, slower response to new objects.\n"
                                               "Smaller values = shorter memory, faster response, less stable.\n"
                                               "Recommended: 5 for 30fps (~167ms window), 7 for 60fps.")
        window_layout.addWidget(self.temporal_window_frames, 0, 1)

        window_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.temporal_threshold_frames = QSpinBox()
        self.temporal_threshold_frames.setRange(1, 30)
        self.temporal_threshold_frames.setValue(3)  # Default 3
        self.temporal_threshold_frames.setToolTip("Number of frames within window where detection must appear (N of M).\n"
                                                  "Higher values = more stringent, filters transient false positives.\n"
                                                  "Lower values = more lenient, faster response to new objects.\n"
                                                  "Must be ≤ Window Frames.\n"
                                                  "Recommended: 3 out of 5 (detection in 60% of frames).")
        window_layout.addWidget(self.temporal_threshold_frames, 1, 1)

        temporal_layout.addLayout(window_layout)
        layout.addWidget(temporal_group)
        layout.addStretch()

        return widget

    def _create_fpr_tab(self) -> QWidget:
        """Create False Positive Reduction tab - matches original exactly."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Aspect Ratio Filter
        aspect_group = QGroupBox("Aspect Ratio Filter")
        aspect_layout = QVBoxLayout(aspect_group)

        self.enable_aspect_ratio_filter = QCheckBox("Enable Aspect Ratio Filtering")
        self.enable_aspect_ratio_filter.setChecked(False)  # Default OFF
        self.enable_aspect_ratio_filter.setToolTip("Filters detections based on aspect ratio (width/height).\n"
                                                   "Removes very thin/elongated detections (wires, shadows, cracks).\n"
                                                   "Useful for filtering non-object shapes.\n"
                                                   "Recommended: OFF by default, ON if many thin false positives.")
        aspect_layout.addWidget(self.enable_aspect_ratio_filter)

        ratio_layout = QGridLayout()
        ratio_layout.addWidget(QLabel("Min Ratio:"), 0, 0)
        self.min_aspect_ratio = QDoubleSpinBox()
        self.min_aspect_ratio.setRange(0.1, 10.0)
        self.min_aspect_ratio.setValue(0.2)
        self.min_aspect_ratio.setSingleStep(0.1)
        self.min_aspect_ratio.setToolTip("Minimum aspect ratio (width/height) to keep (0.1-10.0).\n"
                                         "Rejects very tall/thin vertical detections.\n"
                                         "Example: 0.2 = reject if height > 5× width.\n"
                                         "Lower values = allow thinner objects.\n"
                                         "Recommended: 0.2 for filtering poles/wires, 0.5 for people.")
        ratio_layout.addWidget(self.min_aspect_ratio, 0, 1)

        ratio_layout.addWidget(QLabel("Max Ratio:"), 1, 0)
        self.max_aspect_ratio = QDoubleSpinBox()
        self.max_aspect_ratio.setRange(0.1, 20.0)
        self.max_aspect_ratio.setValue(5.0)
        self.max_aspect_ratio.setSingleStep(0.1)
        self.max_aspect_ratio.setToolTip("Maximum aspect ratio (width/height) to keep (0.1-20.0).\n"
                                         "Rejects very wide/thin horizontal detections.\n"
                                         "Example: 5.0 = reject if width > 5× height.\n"
                                         "Higher values = allow wider objects.\n"
                                         "Recommended: 5.0 for filtering shadows/lines, 10.0 for vehicles.")
        ratio_layout.addWidget(self.max_aspect_ratio, 1, 1)

        aspect_layout.addLayout(ratio_layout)
        layout.addWidget(aspect_group)

        # Detection Clustering
        cluster_group = QGroupBox("Detection Clustering")
        cluster_layout = QVBoxLayout(cluster_group)

        self.enable_detection_clustering = QCheckBox("Enable Detection Clustering")
        self.enable_detection_clustering.setChecked(False)  # Default OFF
        self.enable_detection_clustering.setToolTip("Combines nearby detections into single merged detection.\n"
                                                    "Groups detections whose centroids are within specified distance.\n"
                                                    "Merged detection encompasses all combined contours.\n"
                                                    "Useful for: Combining scattered patches of same object.\n"
                                                    "Recommended: OFF by default, ON if objects appear fragmented.")
        cluster_layout.addWidget(self.enable_detection_clustering)

        cluster_dist_layout = QGridLayout()
        cluster_dist_layout.addWidget(QLabel("Clustering Distance (px):"), 0, 0)
        self.clustering_distance = QSpinBox()
        self.clustering_distance.setRange(0, 500)
        self.clustering_distance.setValue(50)  # Default 50px
        self.clustering_distance.setToolTip("Maximum centroid distance to merge detections (0-500 pixels).\n"
                                            "Detections closer than this distance are combined into one.\n"
                                            "Lower values = only merge very close detections.\n"
                                            "Higher values = merge distant detections (may over-merge).\n"
                                            "Recommended: 50px for people, 100px for vehicles at 720p.")
        cluster_dist_layout.addWidget(self.clustering_distance, 0, 1)

        cluster_layout.addLayout(cluster_dist_layout)
        layout.addWidget(cluster_group)

        # Color Exclusion
        exclusion_group = QGroupBox("Color Exclusion")
        exclusion_layout = QVBoxLayout(exclusion_group)

        self.enable_color_exclusion = QCheckBox("Enable Color Exclusion")
        self.enable_color_exclusion.setChecked(False)
        self.enable_color_exclusion.setToolTip("Excludes specific colors from detection (background learning).\n"
                                               "Useful for ignoring known background colors (grass, sky, buildings).\n"
                                               "Select colors below to exclude from color anomaly detection.\n"
                                               "Recommended: Use to filter out dominant environmental colors.")
        exclusion_layout.addWidget(self.enable_color_exclusion)

        # Color hue toggles (separated by 20 degrees on 360° wheel)
        exclusion_layout.addWidget(QLabel("Exclude Colors (20° steps, 0-360°):"))

        # Create grid of color checkboxes
        colors_grid = QGridLayout()
        self.hue_color_toggles = []

        # Hue colors every 20 degrees on full 360° wheel (18 colors)
        # Format: (name, hue_degrees_360, hex_color_for_display)
        hue_colors = [
            ("Red", 0, "#FF0000"),
            ("Red-Orange", 20, "#FF3300"),
            ("Orange", 40, "#FF6600"),
            ("Yellow-Orange", 60, "#FF9900"),
            ("Yellow", 80, "#FFCC00"),
            ("Yellow-Green", 100, "#CCFF00"),
            ("Green", 120, "#00FF00"),
            ("Green-Cyan", 140, "#00FF66"),
            ("Cyan", 160, "#00FFCC"),
            ("Cyan-Blue", 180, "#00CCFF"),
            ("Blue", 200, "#0099FF"),
            ("Blue-Violet", 220, "#0066FF"),
            ("Violet", 240, "#0033FF"),
            ("Purple", 260, "#6600FF"),
            ("Magenta", 280, "#9900FF"),
            ("Pink-Magenta", 300, "#CC00FF"),
            ("Pink", 320, "#FF00CC"),
            ("Hot Pink", 340, "#FF0066"),
        ]

        for i, (name, hue_360, color_hex) in enumerate(hue_colors):
            checkbox = QCheckBox(name)
            checkbox.setStyleSheet(f"QCheckBox {{ color: {color_hex}; font-weight: bold; }}")
            checkbox.setChecked(False)
            checkbox.setProperty("hue_value_360", hue_360)  # Store hue in 360° scale
            self.hue_color_toggles.append(checkbox)

            row = i // 3
            col = i % 3
            colors_grid.addWidget(checkbox, row, col)

        exclusion_layout.addLayout(colors_grid)

        layout.addWidget(exclusion_group)
        layout.addStretch()

        return widget

    def _create_rendering_tab(self) -> QWidget:
        """Create Rendering tab - matches original exactly."""
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
        # Processing
        self.resolution_preset.currentTextChanged.connect(self.on_resolution_preset_changed)
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
        self.color_max_detection_area.valueChanged.connect(self.emit_config)
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
        self.enable_detection_clustering.toggled.connect(self.emit_config)
        self.clustering_distance.valueChanged.connect(self.emit_config)
        self.enable_color_exclusion.toggled.connect(self.emit_config)

        # Hue color toggles
        for toggle in self.hue_color_toggles:
            toggle.toggled.connect(self.emit_config)

        # Rendering
        self.render_shape.currentTextChanged.connect(self.emit_config)
        self.render_text.toggled.connect(self.emit_config)
        self.render_contours.toggled.connect(self.emit_config)
        self.use_detection_color.toggled.connect(self.emit_config)
        self.max_detections_to_render.valueChanged.connect(self.emit_config)
        self.show_timing_overlay.toggled.connect(self.emit_config)
        self.show_detection_thumbnails.toggled.connect(self.emit_config)

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

    def on_resolution_preset_changed(self, preset_name: str):
        """Handle resolution preset change."""
        if preset_name == "Custom":
            # Enable manual inputs
            self.processing_width.setEnabled(True)
            self.processing_height.setEnabled(True)
        else:
            # Disable manual inputs and set preset values
            self.processing_width.setEnabled(False)
            self.processing_height.setEnabled(False)

            resolution = self.resolution_presets.get(preset_name)
            # Handle "Original" (None) and other presets
            if resolution and resolution != "custom":
                self.processing_width.setValue(resolution[0])
                self.processing_height.setValue(resolution[1])
            elif preset_name == "Original":
                # "Original" means no downsampling - values don't matter, will be ignored
                pass

        self.emit_config()

    def emit_config(self):
        """Emit current configuration."""
        config = self.get_config()
        self.configChanged.emit(config)

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary - matches original format exactly."""
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

        # Build excluded hue ranges from toggles
        excluded_hue_ranges = []
        tolerance = 10.0  # ±10 degrees for each color (20 degree separation on 360° wheel)

        for toggle in self.hue_color_toggles:
            if toggle.isChecked():
                hue_360 = toggle.property("hue_value_360")

                # Convert from 360° scale to OpenCV's 0-179 scale
                # OpenCV uses hue/2 to fit in 8-bit (0-179 instead of 0-359)
                hue_cv = hue_360 / 2.0

                # Apply tolerance in OpenCV scale (convert tolerance too)
                tolerance_cv = tolerance / 2.0  # ±10° becomes ±5 in OpenCV scale
                hue_min = max(0, hue_cv - tolerance_cv)
                hue_max = min(179, hue_cv + tolerance_cv)
                excluded_hue_ranges.append((hue_min, hue_max))

        # Handle "Original" resolution preset (no downsampling)
        current_preset = self.resolution_preset.currentText()
        if current_preset == "Original":
            # Use very large values so no downsampling occurs
            processing_width = 99999
            processing_height = 99999
        else:
            processing_width = self.processing_width.value()
            processing_height = self.processing_height.value()

        config = {
            'processing_width': processing_width,
            'processing_height': processing_height,
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
            'color_max_detection_area': self.color_max_detection_area.value(),
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
            'enable_detection_clustering': self.enable_detection_clustering.isChecked(),
            'clustering_distance': self.clustering_distance.value(),
            'enable_color_exclusion': self.enable_color_exclusion.isChecked(),
            'excluded_hue_ranges': excluded_hue_ranges,

            'render_shape': shape_map[self.render_shape.currentText()],
            'render_text': self.render_text.isChecked(),
            'render_contours': self.render_contours.isChecked(),
            'use_detection_color_for_rendering': self.use_detection_color.isChecked(),
            'max_detections_to_render': self.max_detections_to_render.value(),
            'show_timing_overlay': self.show_timing_overlay.isChecked(),
            'show_detection_thumbnails': self.show_detection_thumbnails.isChecked(),
        }

        return config
