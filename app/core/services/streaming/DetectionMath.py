"""
DetectionMath.py - Shared geometry helpers for streaming detections.

This module centralizes common bbox/centroid math used across streaming
algorithms to reduce duplicated implementations.
"""

from typing import Tuple
import math


def bbox_iou(bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
    """
    Compute IoU between two bounding boxes.

    Args:
        bbox1: (x, y, w, h)
        bbox2: (x, y, w, h)

    Returns:
        IoU in [0.0, 1.0].
    """
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2

    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection = (x_right - x_left) * (y_bottom - y_top)
    area1 = w1 * h1
    area2 = w2 * h2
    union = area1 + area2 - intersection
    if union <= 0:
        return 0.0
    return intersection / union


def centroid_distance(c1: Tuple[int, int], c2: Tuple[int, int]) -> float:
    """Compute Euclidean distance between two centroid points."""
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1])
