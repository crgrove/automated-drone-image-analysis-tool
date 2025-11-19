"""
Streaming detection algorithms for real-time video analysis.

This module contains algorithms for detecting anomalies in live video streams:
- MotionDetection: Detects movement in static or moving cameras
- ColorDetection: Detects objects by HSV color matching
- ColorAnomalyAndMotionDetection: Combines motion and color for comprehensive anomaly detection
"""

__all__ = ['MotionDetection', 'ColorDetection', 'ColorAnomalyAndMotionDetection']
