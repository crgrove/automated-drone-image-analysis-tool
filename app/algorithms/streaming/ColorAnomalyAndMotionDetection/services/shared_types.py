"""
shared_types.py - Shared types and enums for color anomaly and motion detection

Contains common data structures, enums, and types used across all detection services.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


@dataclass
class Detection:
    """Generic detection result."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    centroid: Tuple[int, int]
    area: float
    confidence: float
    detection_type: str  # 'motion', 'color', 'rx_anomaly', 'fused'
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    contour: Optional[np.ndarray] = None


class MotionAlgorithm(Enum):
    """Motion detection algorithms."""
    FRAME_DIFF = "frame_diff"      # Simple frame differencing
    MOG2 = "mog2"                  # Gaussian mixture model (best for static camera)
    KNN = "knn"                    # K-nearest neighbors (alternative)


class FusionMode(Enum):
    """Fusion modes for combining motion and color detections."""
    UNION = "union"                      # Detect if EITHER motion OR color (most detections)
    INTERSECTION = "intersection"        # Detect only if BOTH motion AND color agree (high confidence)
    COLOR_PRIORITY = "color_priority"    # Use color, add motion if color misses it
    MOTION_PRIORITY = "motion_priority"  # Use motion, add color if motion misses it


@dataclass
class ColorAnomalyAndMotionDetectionConfig:
    """Configuration for color anomaly and motion detection."""
    # Processing resolution
    processing_width: int = 1280
    processing_height: int = 720

    # Detection toggles
    enable_motion: bool = True
    enable_color_quantization: bool = False
    enable_rx_anomaly: bool = False

    # Performance settings
    max_fps: Optional[int] = None
    use_threaded_capture: bool = False

    # Motion algorithm selection
    motion_algorithm: MotionAlgorithm = MotionAlgorithm.MOG2

    # Detection parameters
    min_detection_area: int = 100
    max_detection_area: int = 50000
    motion_threshold: int = 25
    blur_kernel_size: int = 5
    morphology_kernel_size: int = 3
    enable_morphology: bool = True

    # Persistence filter parameters
    persistence_frames: int = 3
    persistence_threshold: int = 2

    # Background subtraction parameters
    bg_history: int = 100
    bg_var_threshold: float = 25.0
    bg_detect_shadows: bool = False

    # Display options
    show_timing_overlay: bool = True
    show_detections: bool = True
    max_detections_to_render: int = 20

    # Rendering options
    render_shape: int = 1  # 0=box, 1=circle, 2=dot, 3=off
    render_text: bool = False
    render_contours: bool = False
    render_at_processing_res: bool = False
    use_detection_color_for_rendering: bool = False

    # Camera movement detection
    pause_on_camera_movement: bool = True
    camera_movement_threshold: float = 0.15

    # Color quantization anomaly detection
    color_quantization_bits: int = 4
    color_rarity_percentile: float = 30.0
    color_min_detection_area: int = 15
    color_max_detection_area: int = 50000
    use_tile_analysis: bool = False

    # Hue expansion for color detections
    enable_hue_expansion: bool = False
    hue_expansion_range: int = 5

    # Mask fusion and temporal smoothing
    enable_fusion: bool = True
    fusion_mode: FusionMode = FusionMode.UNION
    enable_temporal_voting: bool = True
    temporal_window_frames: int = 3
    temporal_threshold_frames: int = 2

    # False Positive Reduction
    enable_aspect_ratio_filter: bool = True
    min_aspect_ratio: float = 0.2
    max_aspect_ratio: float = 5.0

    # Detection clustering
    enable_detection_clustering: bool = False
    clustering_distance: float = 50.0

    # Color exclusion (background learning)
    enable_color_exclusion: bool = False
    excluded_hue_ranges: List[Tuple[float, float]] = field(default_factory=list)

