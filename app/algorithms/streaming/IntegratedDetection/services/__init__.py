"""Integrated Detection services."""

from algorithms.streaming.IntegratedDetection.services.IntegratedDetectionService import (
    IntegratedDetectionService,
    RealtimeIntegratedDetector,  # Backward compatibility alias
    MotionAlgorithm,
    FusionMode,
    StageTimings,
    PerformanceMetrics,
    Detection,
    IntegratedDetectionConfig,
    format_timing_summary
)

__all__ = [
    'IntegratedDetectionService',
    'RealtimeIntegratedDetector',
    'MotionAlgorithm',
    'FusionMode',
    'StageTimings',
    'PerformanceMetrics',
    'Detection',
    'IntegratedDetectionConfig',
    'format_timing_summary'
]
