"""
Streaming detection algorithms for real-time video analysis.

This module contains algorithms for detecting anomalies in live video streams:
- ColorDetection: Detects objects by HSV color matching
- ColorAnomalyAndMotionDetection: Combines motion and color for comprehensive anomaly detection
- AIPersonDetector: ONNX-based person detection for live streams
"""

__all__ = ['ColorDetection', 'ColorAnomalyAndMotionDetection', 'AIPersonDetector']
