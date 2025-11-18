"""Color Detection services."""

from algorithms.streaming.ColorDetection.services.ColorDetectionService import (
    ColorDetectionService,
    RealtimeColorDetector,  # Backward compatibility alias
    MotionAlgorithm,
    FusionMode,
    Detection,
    HSVConfig,
    FrameQueue,
    ThreadedCaptureWorker
)

__all__ = [
    'ColorDetectionService',
    'RealtimeColorDetector',
    'MotionAlgorithm',
    'FusionMode',
    'Detection',
    'HSVConfig',
    'FrameQueue',
    'ThreadedCaptureWorker'
]
