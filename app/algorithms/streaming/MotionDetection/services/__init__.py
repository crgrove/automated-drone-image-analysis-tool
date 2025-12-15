"""Motion Detection services."""

from algorithms.streaming.MotionDetection.services.MotionDetectionService import (
    MotionDetectionService,
    RealtimeMotionDetector,  # Backward compatibility alias
    DetectionMode,
    MotionAlgorithm,
    MotionDetection,
    CameraMotion,
    MotionConfig
)

__all__ = [
    'MotionDetectionService',
    'RealtimeMotionDetector',
    'DetectionMode',
    'MotionAlgorithm',
    'MotionDetection',
    'CameraMotion',
    'MotionConfig'
]
