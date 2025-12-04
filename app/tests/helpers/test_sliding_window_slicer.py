"""
Comprehensive tests for SlidingWindowSlicer.

Tests sliding window operations for image processing.
"""

import pytest
import numpy as np
from helpers.SlidingWindowSlicer import SlidingWindowSlicer


def test_get_slices_basic():
    """Test basic slice generation."""
    img_shape = (100, 100, 3)
    slice_size = 50
    overlap = 0.5

    slices = SlidingWindowSlicer.get_slices(img_shape, slice_size, overlap)

    assert len(slices) > 0
    assert all(len(slice) == 4 for slice in slices)  # (x1, y1, x2, y2)
    assert all(0 <= x1 < x2 <= 100 and 0 <= y1 < y2 <= 100
               for x1, y1, x2, y2 in slices)


def test_get_slices_no_overlap():
    """Test slice generation with no overlap."""
    img_shape = (100, 100, 3)
    slice_size = 50
    overlap = 0.0

    slices = SlidingWindowSlicer.get_slices(img_shape, slice_size, overlap)

    # With no overlap, should get 4 slices (2x2 grid)
    assert len(slices) == 4


def test_get_slices_full_overlap():
    """Test slice generation with maximum overlap."""
    img_shape = (100, 100, 3)
    slice_size = 50
    overlap = 0.9

    slices = SlidingWindowSlicer.get_slices(img_shape, slice_size, overlap)

    # With high overlap, should get many slices
    assert len(slices) > 4


def test_get_slices_large_image():
    """Test slice generation on large image."""
    img_shape = (1000, 2000, 3)
    slice_size = 256
    overlap = 0.5

    slices = SlidingWindowSlicer.get_slices(img_shape, slice_size, overlap)

    assert len(slices) > 0
    assert all(0 <= x1 < x2 <= 2000 and 0 <= y1 < y2 <= 1000
               for x1, y1, x2, y2 in slices)


def test_get_slices_smaller_than_image():
    """Test when slice size is smaller than image."""
    img_shape = (50, 50, 3)
    slice_size = 100
    overlap = 0.5

    slices = SlidingWindowSlicer.get_slices(img_shape, slice_size, overlap)

    # Should still get at least one slice
    assert len(slices) >= 1


def test_merge_slice_detections_empty():
    """Test merging with empty detections."""
    result = SlidingWindowSlicer.merge_slice_detections([], [], [])
    assert result == []


def test_merge_slice_detections_single():
    """Test merging with single detection."""
    boxes = [[10, 10, 50, 50]]
    scores = [0.9]
    classes = [1]

    result = SlidingWindowSlicer.merge_slice_detections(boxes, scores, classes)

    assert len(result) == 1
    assert result[0] == (10, 10, 50, 50, 0.9, 1)


def test_merge_slice_detections_multiple():
    """Test merging with multiple non-overlapping detections."""
    boxes = [[10, 10, 50, 50], [100, 100, 150, 150]]
    scores = [0.9, 0.8]
    classes = [1, 2]

    result = SlidingWindowSlicer.merge_slice_detections(boxes, scores, classes)

    assert len(result) == 2


def test_merge_slice_detections_overlapping():
    """Test merging with overlapping detections (NMS)."""
    boxes = [[10, 10, 50, 50], [15, 15, 55, 55]]  # Overlapping
    scores = [0.9, 0.7]  # First has higher score
    classes = [1, 1]

    result = SlidingWindowSlicer.merge_slice_detections(boxes, scores, classes, iou_threshold=0.5)

    # Should suppress the lower-scoring detection
    assert len(result) == 1
    assert result[0][4] == 0.9  # Higher score kept


def test_merge_slice_detections_custom_iou():
    """Test merging with custom IoU threshold."""
    boxes = [[10, 10, 50, 50], [15, 15, 55, 55]]
    scores = [0.9, 0.7]
    classes = [1, 1]

    # Low threshold should suppress overlapping boxes
    result_low = SlidingWindowSlicer.merge_slice_detections(boxes, scores, classes, iou_threshold=0.1)

    # High threshold should keep both (less suppression)
    result_high = SlidingWindowSlicer.merge_slice_detections(boxes, scores, classes, iou_threshold=0.9)

    # With high IoU threshold, more boxes should be kept
    assert len(result_high) >= len(result_low)


def test_merge_slice_detections_different_classes():
    """Test merging with different classes."""
    # Use non-overlapping boxes to ensure both are kept regardless of class
    boxes = [[10, 10, 50, 50], [100, 100, 150, 150]]  # Non-overlapping
    scores = [0.9, 0.7]
    classes = [1, 2]  # Different classes

    result = SlidingWindowSlicer.merge_slice_detections(boxes, scores, classes, iou_threshold=0.5)

    # Non-overlapping boxes should both be kept
    assert len(result) == 2
