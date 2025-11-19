"""Color Anomaly and Motion Detection services."""

# Import shared types from shared_types module
from .shared_types import (
    Detection,
    MotionAlgorithm,
    FusionMode,
    ColorAnomalyAndMotionDetectionConfig
)

# Import utilities from StreamingUtils
from core.services.streaming.StreamingUtils import (
    StageTimings,
    PerformanceMetrics
)

# Import utilities
from .utils import format_timing_summary

# Import new services
from .MotionDetectionService import MotionDetectionService
from .ColorAnomalyService import ColorAnomalyService
from .ColorAnomalyAndMotionDetectionOrchestrator import ColorAnomalyAndMotionDetectionOrchestrator

__all__ = [
    # New architecture (preferred)
    'ColorAnomalyAndMotionDetectionOrchestrator',
    'MotionDetectionService',
    'ColorAnomalyService',
    # Shared types and enums
    'MotionAlgorithm',
    'FusionMode',
    'StageTimings',
    'PerformanceMetrics',
    'Detection',
    'ColorAnomalyAndMotionDetectionConfig',
    'format_timing_summary',
]
