"""
ColorAnomalyAndMotionDetectionControlWidget.py - Control widget for color anomaly and motion detection parameters.

This widget provides a tabbed interface for configuring all ColorAnomalyAndMotionDetectionOrchestrator
parameters. It matches the original implementation exactly.
"""

from typing import Dict, Any, List, Tuple
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QDoubleSpinBox, QCheckBox,
                               QComboBox, QGroupBox, QSlider, QTabWidget)

from core.services.LoggerService import LoggerService
from core.views.streaming.components import InputProcessingTab, RenderingTab, ColorWheelWidget
from algorithms.streaming.ColorAnomalyAndMotionDetection.services.shared_types import (
    MotionAlgorithm, FusionMode
)


class ColorAnomalyAndMotionDetectionControlWidget(QWidget):
    """Control widget for color anomaly and motion detection parameters."""

    configChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Setup UI structure
        self.setObjectName("ColorAnomalyAndMotionDetectionControlWidget")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        # Populate tabs with actual controls
        self._populate_tabs()

        # Connect signals
        self.connect_signals()

    def _populate_tabs(self):
        """Populate tabs with control panels."""
        # Add actual tabs - Input & Processing moved to right before Rendering
        self.tabs.addTab(self._create_color_tab(), "Color Anomaly")
        self.tabs.addTab(self._create_motion_tab(), "Motion Detection")
        self.tabs.addTab(self._create_fusion_tab(), "Fusion")
        # Use shared tabs for Input & Processing and Rendering
        self.input_processing_tab = InputProcessingTab()
        self.rendering_tab = RenderingTab(show_detection_color_option=True)
        self.tabs.addTab(self.input_processing_tab, "Input && Processing")
        self.tabs.addTab(self.rendering_tab, "Rendering && Cleanup")

    def _create_motion_tab(self) -> QWidget:
        """Create Motion Detection tab with simplified default controls and advanced options."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Motion
        self.enable_motion = QCheckBox("Enable Motion Detection")
        self.enable_motion.setChecked(False)
        self.enable_motion.setToolTip("Turn ON to highlight moving objects in the scene.\n"
                                      "Most users can leave all other settings at their defaults.\n"
                                      "Works best for stationary or slow-moving cameras and can be combined\n"
                                      "with Color-Based Anomaly Detection for more robust results.")
        layout.addWidget(self.enable_motion)

        # Container for advanced motion controls
        self.advanced_motion_container = QWidget()
        advanced_layout = QVBoxLayout(self.advanced_motion_container)
        advanced_layout.setContentsMargins(0, 0, 0, 0)

        # Algorithm Selection
        algo_group = QGroupBox("Algorithm")
        algo_layout = QGridLayout(algo_group)
        algo_layout.setColumnMinimumWidth(0, 160)
        algo_layout.setColumnStretch(1, 1)

        algo_layout.addWidget(QLabel("Type:"), 0, 0)
        self.motion_algorithm = QComboBox()
        self.motion_algorithm.addItems(["FRAME_DIFF", "MOG2", "KNN"])
        self.motion_algorithm.setCurrentText("MOG2")
        self.motion_algorithm.setToolTip("Motion detection algorithm (advanced setting):\n\n"
                                         "• FRAME_DIFF – Fast and simple; very sensitive to any motion.\n"
                                         "• MOG2 – Balanced and adaptive (recommended for most scenes).\n"
                                         "• KNN – More robust to noise and complex backgrounds.\n\n"
                                         "If you are unsure, leave this set to MOG2.")
        algo_layout.addWidget(self.motion_algorithm, 0, 1)

        advanced_layout.addWidget(algo_group)

        # Detection Parameters (advanced)
        param_group = QGroupBox("Detection Parameters")
        param_layout = QGridLayout(param_group)
        param_layout.setColumnMinimumWidth(0, 160)
        param_layout.setColumnStretch(1, 1)

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

        advanced_layout.addWidget(param_group)

        # Persistence Filter
        persist_group = QGroupBox("Persistence Filter")
        persist_layout = QGridLayout(persist_group)
        persist_layout.setColumnMinimumWidth(0, 160)
        persist_layout.setColumnStretch(1, 1)

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
                                              "Recommended: 2 (motion in 2 of last 3 frames).")
        persist_layout.addWidget(self.persistence_threshold, 1, 1)

        advanced_layout.addWidget(persist_group)

        # Background Subtraction
        bg_group = QGroupBox("Background Subtraction (MOG2/KNN)")
        bg_layout = QGridLayout(bg_group)
        bg_layout.setColumnMinimumWidth(0, 160)
        bg_layout.setColumnStretch(1, 1)

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

        advanced_layout.addWidget(bg_group)

        # Object Size Filter (always shown)
        size_group = QGroupBox("Object Size Filter")
        size_layout = QGridLayout(size_group)
        size_layout.setColumnMinimumWidth(0, 160)
        size_layout.setColumnStretch(1, 1)

        size_layout.addWidget(QLabel("Min Object Area (px):"), 0, 0)
        self.min_detection_area = QSpinBox()
        self.min_detection_area.setRange(1, 100000)
        self.min_detection_area.setValue(5)
        self.min_detection_area.setToolTip("Minimum detection area in pixels (1-100000).\n"
                                           "Filters out very small detections such as noise, insects, or raindrops.\n"
                                           "Lower values = detect smaller objects (more noise).\n"
                                           "Higher values = only larger objects (less noise).\n"
                                           "Recommended: 5-10 for person-sized motion, 50-100 for vehicles.")
        size_layout.addWidget(self.min_detection_area, 0, 1)

        size_layout.addWidget(QLabel("Max Object Area (px):"), 1, 0)
        self.max_detection_area = QSpinBox()
        self.max_detection_area.setRange(10, 1000000)
        self.max_detection_area.setValue(1000)
        self.max_detection_area.setToolTip("Maximum detection area in pixels (10-1000000).\n"
                                           "Filters out very large regions such as full-frame lighting changes or giant shadows.\n"
                                           "Lower values = only small/medium objects.\n"
                                           "Higher values = allow large objects.\n"
                                           "Recommended: 1000 for people, 10000 for vehicles, higher for very large objects.")
        size_layout.addWidget(self.max_detection_area, 1, 1)

        layout.addWidget(size_group)

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

        # Advanced toggle (placed after camera movement controls)
        self.show_advanced_motion = QCheckBox("Show Advanced Motion Settings")
        self.show_advanced_motion.setChecked(False)
        self.show_advanced_motion.setToolTip("Advanced users can expand this to adjust the motion algorithm\n"
                                             "and detailed thresholds (sensitivity, filters, background model).\n"
                                             "If you are unsure, leave this unchecked and use the defaults.")

        # Hide advanced controls by default
        self.advanced_motion_container.setVisible(False)
        layout.addWidget(self.show_advanced_motion)
        layout.addWidget(self.advanced_motion_container)
        layout.addStretch()

        return widget

    def _create_color_tab(self) -> QWidget:
        """Create Color Anomaly tab - matches original exactly."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Color
        self.enable_color_quantization = QCheckBox("Enable Color-Based Anomaly Detection")
        self.enable_color_quantization.setChecked(True)
        self.enable_color_quantization.setToolTip("Detects pixels whose colors are statistically rare in the frame.\n"
                                                  "Conceptually similar to MRMap's rarity-based detection for images.\n"
                                                  "Works well for: bright colored clothing, vehicles, equipment in natural scenes.\n"
                                                  "Can be combined with Motion Detection for more robust detection.")
        layout.addWidget(self.enable_color_quantization)

        # Color rarity / quantization settings
        quant_group = QGroupBox("Color Rarity Settings")
        quant_layout = QGridLayout(quant_group)
        quant_layout.setColumnMinimumWidth(0, 160)
        quant_layout.setColumnStretch(1, 1)

        quant_layout.addWidget(QLabel("Color Resolution (bins):"), 0, 0)
        bits_layout = QHBoxLayout()
        self.color_quantization_bits = QSlider(Qt.Horizontal)
        self.color_quantization_bits.setRange(3, 8)
        self.color_quantization_bits.setValue(4)
        self.color_quantization_bits.setToolTip("Controls how finely colors are grouped into histogram bins (3-8 bits).\n"
                                                "Analogous to MRMap's color binning.\n"
                                                "Lower values (3-4) = fewer bins → faster, more grouping, fewer but stronger detections.\n"
                                                "Higher values (6-8) = more bins → slower, less grouping, more but weaker/smaller detections.\n"
                                                "Recommended: 4-5 for a balanced number of detections; use lower for very clean results,\n"
                                                "and higher only when you need to pull out very subtle color differences.")
        bits_layout.addWidget(self.color_quantization_bits)
        self.color_bits_label = QLabel("4 bits")
        bits_layout.addWidget(self.color_bits_label)
        quant_layout.addLayout(bits_layout, 0, 1)

        quant_layout.addWidget(QLabel("Rarity Threshold (% of colors):"), 1, 0)
        percentile_layout = QHBoxLayout()
        self.color_rarity_percentile = QSlider(Qt.Horizontal)
        self.color_rarity_percentile.setRange(0, 100)
        self.color_rarity_percentile.setValue(30)  # Default 30%
        self.color_rarity_percentile.setToolTip("Sensitivity threshold for how rare a color must be to be flagged (0-100%).\n"
                                                "Computed from the distribution of color-bin counts in the frame, similar in role\n"
                                                "to MRMap's detection threshold.\n"
                                                "Lower values (10-20%) = stricter: only very rare colors (fewer detections).\n"
                                                "Medium values (25-40%) = balanced (recommended for general use).\n"
                                                "Higher values (40-60%) = more sensitive: includes more common colors (more detections).")
        percentile_layout.addWidget(self.color_rarity_percentile)
        self.color_percentile_label = QLabel("30%")
        percentile_layout.addWidget(self.color_percentile_label)
        quant_layout.addLayout(percentile_layout, 1, 1)

        quant_layout.addWidget(QLabel("Min Object Area (px):"), 2, 0)
        self.color_min_detection_area = QSpinBox()
        self.color_min_detection_area.setRange(1, 10000)
        self.color_min_detection_area.setValue(15)
        self.color_min_detection_area.setToolTip("Minimum area in pixels for a color anomaly to be treated as an object of interest.\n"
                                                 "Conceptually matches MRMap's minimum AOI area.\n"
                                                 "Lower values = detect smaller colored objects (more noise).\n"
                                                 "Higher values = only larger colored regions (less noise).\n"
                                                 "Recommended: 15 for person-sized targets, 50+ for vehicles or large objects.")
        quant_layout.addWidget(self.color_min_detection_area, 2, 1)

        quant_layout.addWidget(QLabel("Max Object Area (px):"), 3, 0)
        self.color_max_detection_area = QSpinBox()
        self.color_max_detection_area.setRange(100, 1000000)
        self.color_max_detection_area.setValue(50000)
        self.color_max_detection_area.setToolTip("Maximum area in pixels for a color anomaly to be treated as an object of interest.\n"
                                                 "Conceptually matches MRMap's maximum AOI area.\n"
                                                 "Lower values = only detect smaller colored objects.\n"
                                                 "Higher values = allow larger colored regions.\n"
                                                 "Recommended: 50000 for general use, 10000 for small-object-only searches.")
        quant_layout.addWidget(self.color_max_detection_area, 3, 1)

        layout.addWidget(quant_group)

        # Hue Expansion
        hue_group = QGroupBox("Color Match Expansion")
        hue_layout = QVBoxLayout(hue_group)

        self.enable_hue_expansion = QCheckBox("Allow Similar Colors (Hue Expansion)")
        self.enable_hue_expansion.setChecked(False)  # Default OFF
        self.enable_hue_expansion.setToolTip("Lets the detector treat similar colors as the same object.\n"
                                             "For example, a red jacket that looks slightly orange in some frames will still be grouped together.\n"
                                             "Turn this OFF if you only care about one very specific color shade.\n"
                                             "Turn this ON if you want a whole family of colors (e.g., any warm reds/oranges).")
        hue_layout.addWidget(self.enable_hue_expansion)

        hue_range_layout = QHBoxLayout()
        hue_range_layout.addWidget(QLabel("Color Match Range:"))
        self.hue_expansion_range = QSlider(Qt.Horizontal)
        self.hue_expansion_range.setRange(0, 30)
        self.hue_expansion_range.setValue(5)
        self.hue_expansion_range.setToolTip("How wide to stretch the color match around each detected color.\n"
                                            "Smaller values = stay very close to the original color (more specific).\n"
                                            "Larger values = include a wider range of similar colors (more forgiving).\n"
                                            "Recommended: low values for precise colors, higher values when lighting or camera color shifts a lot.")
        hue_range_layout.addWidget(self.hue_expansion_range)
        self.hue_range_label = QLabel("±5 (~10°)")
        hue_range_layout.addWidget(self.hue_range_label)
        hue_layout.addLayout(hue_range_layout)

        layout.addWidget(hue_group)

        # Color Exclusion (moved from False Pos. Reduction tab)
        exclusion_group = QGroupBox("Color Exclusion")
        exclusion_layout = QVBoxLayout(exclusion_group)

        self.enable_color_exclusion = QCheckBox("Enable Color Exclusion")
        self.enable_color_exclusion.setChecked(False)
        self.enable_color_exclusion.setToolTip("Exclude specific background colors from color anomaly detection.\n"
                                               "Useful for ignoring dominant scene colors such as grass, sky, or buildings.\n"
                                               "Click on the color wheel below to choose colors to ignore.\n"
                                               "Selected colors are highlighted with a dark border.")
        exclusion_layout.addWidget(self.enable_color_exclusion)

        # Color wheel for hue selection (20° steps, 0-360°)
        exclusion_layout.addWidget(QLabel("Click on color wheel to exclude colors (20° steps, 0-360°):"))

        # Create color wheel widget
        self.color_wheel = ColorWheelWidget(size=300)
        self.color_wheel.setToolTip("Click on any color segment to toggle exclusion on/off.\n"
                                    "Segments represent broad color ranges (e.g., blues, greens, reds).\n"
                                    "Use this to teach the system which background colors to ignore.")
        exclusion_layout.addWidget(self.color_wheel, alignment=Qt.AlignCenter)

        layout.addWidget(exclusion_group)
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
        layout.addStretch()

        return widget

    def connect_signals(self):
        """Connect all control signals."""
        # Processing (from shared InputProcessingTab)
        self.input_processing_tab.resolution_preset.currentTextChanged.connect(
            self.input_processing_tab.on_resolution_preset_changed)
        self.input_processing_tab.resolution_preset.currentTextChanged.connect(self.emit_config)
        self.input_processing_tab.processing_width.valueChanged.connect(self.emit_config)
        self.input_processing_tab.processing_height.valueChanged.connect(self.emit_config)
        self.input_processing_tab.render_at_processing_res.toggled.connect(self.emit_config)

        # Motion
        self.enable_motion.toggled.connect(self.emit_config)
        self.show_advanced_motion.toggled.connect(self.on_show_advanced_motion_toggled)
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

        # Temporal Voting and Cleanup (now in RenderingTab)
        self.rendering_tab.enable_temporal_voting.toggled.connect(self.emit_config)
        self.rendering_tab.temporal_window_frames.valueChanged.connect(self.emit_config)
        self.rendering_tab.temporal_threshold_frames.valueChanged.connect(self.emit_config)
        self.rendering_tab.enable_aspect_ratio_filter.toggled.connect(self.emit_config)
        self.rendering_tab.min_aspect_ratio.valueChanged.connect(self.emit_config)
        self.rendering_tab.max_aspect_ratio.valueChanged.connect(self.emit_config)
        self.rendering_tab.enable_detection_clustering.toggled.connect(self.emit_config)
        self.rendering_tab.clustering_distance.valueChanged.connect(self.emit_config)
        self.enable_color_exclusion.toggled.connect(self.emit_config)

        # Color wheel selection changes
        self.color_wheel.selectionChanged.connect(self.emit_config)

        # Rendering (from shared RenderingTab)
        self.rendering_tab.render_shape.currentTextChanged.connect(self.emit_config)
        self.rendering_tab.render_text.toggled.connect(self.emit_config)
        self.rendering_tab.render_contours.toggled.connect(self.emit_config)
        self.rendering_tab.use_detection_color.toggled.connect(self.emit_config)
        self.rendering_tab.max_detections_to_render.valueChanged.connect(self.emit_config)

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
        self.hue_range_label.setText(f"±{value} (~{value * 2}°)")
        self.emit_config()

    def on_show_advanced_motion_toggled(self, checked: bool):
        """Show or hide advanced motion controls."""
        self.advanced_motion_container.setVisible(checked)

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

        # Build excluded hue ranges from color wheel selection
        excluded_hue_ranges = []
        tolerance = 10.0  # ±10 degrees for each color (20 degree separation on 360° wheel)

        # Get selected hues from color wheel (in 360° scale)
        selected_hues = self.color_wheel.get_selected_hues()

        for hue_360 in selected_hues:
            # Convert from 360° scale to OpenCV's 0-179 scale
            # OpenCV uses hue/2 to fit in 8-bit (0-179 instead of 0-359)
            hue_cv = hue_360 / 2.0

            # Apply tolerance in OpenCV scale (convert tolerance too)
            tolerance_cv = tolerance / 2.0  # ±10° becomes ±5 in OpenCV scale
            hue_min = max(0, hue_cv - tolerance_cv)
            hue_max = min(179, hue_cv + tolerance_cv)
            excluded_hue_ranges.append((hue_min, hue_max))

        # Get processing resolution from shared InputProcessingTab
        processing_width, processing_height = self.input_processing_tab.get_processing_resolution()

        config = {
            'processing_width': processing_width,
            'processing_height': processing_height,
            'render_at_processing_res': self.input_processing_tab.render_at_processing_res.isChecked(),

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
            'enable_color_exclusion': self.enable_color_exclusion.isChecked(),
            'excluded_hue_ranges': excluded_hue_ranges,

            # Rendering & Cleanup (from shared RenderingTab - includes temporal voting and cleanup)
            **self.rendering_tab.get_config(),
        }

        return config
