"""Unit tests for shared streaming detection math helpers."""

from core.services.streaming.DetectionMath import bbox_iou, centroid_distance


class TestDetectionMath:
    """Test suite for detection geometry helper functions."""

    def test_bbox_iou_overlap(self):
        """IoU should be computed correctly for overlapping boxes."""
        iou = bbox_iou((0, 0, 10, 10), (5, 5, 10, 10))
        assert round(iou, 3) == round(25 / 175, 3)

    def test_bbox_iou_no_overlap(self):
        """IoU should be zero for non-overlapping boxes."""
        assert bbox_iou((0, 0, 10, 10), (20, 20, 5, 5)) == 0.0

    def test_centroid_distance(self):
        """Centroid distance should follow Euclidean metric."""
        assert centroid_distance((0, 0), (3, 4)) == 5.0
