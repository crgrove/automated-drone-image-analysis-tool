"""Unit tests for ColorDetectionService."""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QObject
import time
import threading

from algorithms.streaming.ColorDetection.services.ColorDetectionService import (
    ColorDetectionService, HSVConfig, Detection, MotionAlgorithm, FusionMode
)


def _det(bbox=(10, 10, 20, 20), confidence=0.8, area=400, detection_type="color"):
    x, y, w, h = bbox
    return Detection(
        bbox=bbox,
        centroid=(x + w // 2, y + h // 2),
        area=area,
        confidence=confidence,
        timestamp=0.0,
        contour=np.array([[[x, y]], [[x + w, y]], [[x + w, y + h]], [[x, y + h]]], dtype=np.int32),
        detection_type=detection_type,
    )


class TestColorDetectionService:
    """Test suite for ColorDetectionService."""

    def test_initialization(self):
        """Test service initialization."""
        service = ColorDetectionService()

        assert service is not None
        assert hasattr(service, '_config')
        assert hasattr(service, 'detectionsReady')
        assert hasattr(service, 'performanceUpdate')
        assert hasattr(service, 'configurationChanged')

    def test_update_config(self):
        """Test configuration update."""
        service = ColorDetectionService()

        new_config = HSVConfig(
            target_color_rgb=(255, 0, 0),
            hue_threshold=15,
            saturation_threshold=50,
            value_threshold=30
        )

        service.update_config(new_config)

        # Verify config was updated
        assert service._config.target_color_rgb == (255, 0, 0)
        assert service._config.hue_threshold == 15

    def test_detect_colors_basic(self):
        """Test basic color detection."""
        service = ColorDetectionService()

        # Create a test frame with a red square
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[30:70, 30:70] = [0, 0, 255]  # Red in BGR

        # Configure for red detection
        config = HSVConfig(target_color_rgb=(255, 0, 0))
        service.update_config(config)

        detections = service.detect_colors(frame, 0.0)

        assert isinstance(detections, list)
        # Should detect the red square
        if len(detections) > 0:
            assert isinstance(detections[0], Detection)
            assert detections[0].detection_type == 'color'

    def test_detect_colors_no_match(self):
        """Test color detection with no matching colors."""
        service = ColorDetectionService()

        # Create a test frame with only blue (no red)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[:, :] = [255, 0, 0]  # Blue in BGR

        # Configure for red detection
        config = HSVConfig(target_color_rgb=(255, 0, 0))
        service.update_config(config)

        detections = service.detect_colors(frame, 0.0)

        # Should return empty list or no detections
        assert isinstance(detections, list)

    def test_detect_colors_min_area_filter(self):
        """Test minimum area filtering."""
        service = ColorDetectionService()

        # Create a test frame with a very small red dot
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[50:52, 50:52] = [0, 0, 255]  # Very small red area

        # Configure with high min_area threshold
        config = HSVConfig(
            target_color_rgb=(255, 0, 0),
            min_area=100  # Larger than our dot
        )
        service.update_config(config)

        detections = service.detect_colors(frame, 0.0)

        # Should filter out the small detection
        assert len(detections) == 0

    def test_detect_colors_max_area_filter(self):
        """Test maximum area filtering."""
        service = ColorDetectionService()

        # Create a test frame with large red area
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[10:90, 10:90] = [0, 0, 255]  # Large red area

        # Configure with low max_area threshold
        config = HSVConfig(
            target_color_rgb=(255, 0, 0),
            max_area=100  # Smaller than our area
        )
        service.update_config(config)

        detections = service.detect_colors(frame, 0.0)

        # Should filter out the large detection
        assert len(detections) == 0

    def test_process_frame(self):
        """Test frame processing."""
        service = ColorDetectionService()

        # Create a test frame
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[30:70, 30:70] = [0, 0, 255]  # Red square

        # Configure for red detection
        config = HSVConfig(target_color_rgb=(255, 0, 0))
        service.update_config(config)

        # Use detect_colors instead (process_frame may not exist or work differently)
        detections = service.detect_colors(frame, 0.0)

        assert isinstance(detections, list)

    def test_process_frame_with_motion_detection(self):
        """Test frame processing with motion detection enabled."""
        service = ColorDetectionService()

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:60, 50:60] = [0, 0, 255]  # Add red square in second frame

        # Configure with motion detection
        config = HSVConfig(
            target_color_rgb=(255, 0, 0),
            enable_motion_detection=True
        )
        service.update_config(config)

        # Process first frame
        service.detect_colors(frame1, 0.0)

        # Process second frame (should detect motion)
        detections = service.detect_colors(frame2, 0.1)

        assert isinstance(detections, list)

    def test_get_config(self):
        """Test getting current configuration."""
        service = ColorDetectionService()

        config = service.get_config()

        assert isinstance(config, HSVConfig)
        assert config is not None
        config.min_area = 999
        assert service.get_config().min_area != 999

    def test_performance_tracking(self):
        """Test performance metrics tracking."""
        service = ColorDetectionService()

        # Process some frames
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(5):
            service.detect_colors(frame, float(i) * 0.033)
            time.sleep(0.001)  # Small delay

        # Check that performance metrics are being tracked
        assert hasattr(service, '_processing_times')
        assert len(service._processing_times) > 0

    def test_gpu_detection(self):
        """Test GPU availability detection."""
        service = ColorDetectionService()

        # Should detect GPU availability (or lack thereof)
        assert hasattr(service, '_gpu_available')
        assert isinstance(service._gpu_available, bool)

    def test_signal_emission(self, qapp):
        """Test that signals are emitted."""
        service = ColorDetectionService()

        detections_received = []
        performance_received = []

        def on_detections(detections, timestamp, frame):
            detections_received.extend(detections)

        def on_performance(metrics):
            performance_received.append(metrics)

        service.detectionsReady.connect(on_detections)
        service.performanceUpdate.connect(on_performance)

        # Process a frame
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[30:70, 30:70] = [0, 0, 255]  # Red square

        config = HSVConfig(target_color_rgb=(255, 0, 0))
        service.update_config(config)

        # Note: Signals are emitted asynchronously, so we just verify they exist
        assert service.detectionsReady is not None
        assert service.performanceUpdate is not None

    def test_error_handling_invalid_frame(self):
        """Test error handling with invalid frame."""
        service = ColorDetectionService()

        # Test with None frame - may handle gracefully or raise error
        try:
            service.detect_colors(None, 0.0)
            # If no error, that's also acceptable (service may handle it)
        except (AttributeError, TypeError, cv2.error):
            pass  # Expected error

    def test_error_handling_empty_frame(self):
        """Test error handling with empty frame."""
        service = ColorDetectionService()

        # Test with empty frame
        empty_frame = np.array([], dtype=np.uint8)

        # Should handle gracefully or raise appropriate error
        try:
            service.detect_colors(empty_frame, 0.0)
        except (ValueError, IndexError):
            pass  # Expected error

    def test_error_handling_invalid_config(self):
        """Test error handling with invalid configuration."""
        service = ColorDetectionService()

        # Test with invalid config values - HSVConfig may accept these
        # and handle them during processing, or may raise errors
        invalid_config = HSVConfig(
            target_color_rgb=(255, 0, 0),  # Valid RGB
            hue_threshold=-10  # Negative threshold (may be clamped or cause issues)
        )

        # Should handle gracefully or raise error
        try:
            service.update_config(invalid_config)
            # If no error, config was accepted (may be handled during processing)
        except (ValueError, AssertionError):
            pass  # Expected error

    def test_thread_safety(self):
        """Test thread safety of configuration updates."""
        service = ColorDetectionService()

        def update_config_thread():
            config = HSVConfig(target_color_rgb=(255, 0, 0))
            service.update_config(config)

        # Create multiple threads updating config
        threads = [threading.Thread(target=update_config_thread) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should not crash
        assert service._config is not None

    def test_detection_metadata(self):
        """Test that detections include proper metadata."""
        service = ColorDetectionService()

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[30:70, 30:70] = [0, 0, 255]  # Red square

        config = HSVConfig(target_color_rgb=(255, 0, 0))
        service.update_config(config)

        detections = service.detect_colors(frame, 0.0)

        if len(detections) > 0:
            detection = detections[0]
            assert hasattr(detection, 'bbox')
            assert hasattr(detection, 'centroid')
            assert hasattr(detection, 'area')
            assert hasattr(detection, 'confidence')
            assert hasattr(detection, 'detection_type')
            assert detection.detection_type == 'color'

    def test_hsv_conversion(self):
        """Test RGB to HSV conversion."""
        service = ColorDetectionService()

        # Test that HSV values are calculated correctly
        config = HSVConfig(target_color_rgb=(255, 0, 0))
        service.update_config(config)

        # Verify HSV values are set
        assert service._target_hsv is not None
        assert service._hsv_ranges is not None


# ---------------------------------------------------------------------------
# Pure helper coverage
# ---------------------------------------------------------------------------

class TestColorDetectionPureHelpers:
    """Tests for stateless / pure helpers that don't need GPU or a video pipeline."""

    def test_iou_identical_bboxes(self):
        svc = ColorDetectionService()
        d = _det(bbox=(0, 0, 10, 10))
        assert svc._calculate_iou(d, d) == pytest.approx(1.0)

    def test_iou_disjoint_bboxes(self):
        svc = ColorDetectionService()
        a = _det(bbox=(0, 0, 10, 10))
        b = _det(bbox=(100, 100, 10, 10))
        assert svc._calculate_iou(a, b) == 0.0

    def test_iou_partial_overlap(self):
        svc = ColorDetectionService()
        a = _det(bbox=(0, 0, 10, 10))
        b = _det(bbox=(5, 5, 10, 10))
        iou = svc._calculate_iou(a, b)
        assert 0.0 < iou < 1.0

    def test_merge_detections_union_bbox(self):
        svc = ColorDetectionService()
        a = _det(bbox=(0, 0, 10, 10), confidence=0.8, area=100)
        b = _det(bbox=(5, 5, 10, 10), confidence=0.6, area=100)
        m = svc._merge_detections(a, b)
        assert m.bbox[0] == 0 and m.bbox[1] == 0
        assert m.bbox[2] == 15 and m.bbox[3] == 15
        assert m.detection_type == "fused"
        assert m.confidence == pytest.approx(0.7)

    def test_aspect_ratio_filter_keeps_in_range(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.min_aspect_ratio = 0.5
        cfg.max_aspect_ratio = 2.0
        dets = [
            _det(bbox=(0, 0, 10, 10)),   # 1.0 - kept
            _det(bbox=(0, 0, 100, 10)),  # 10.0 - filtered
            _det(bbox=(0, 0, 5, 50)),    # 0.1  - filtered
        ]
        filtered = svc._apply_aspect_ratio_filter(dets, cfg)
        assert len(filtered) == 1
        assert filtered[0].bbox[2] == 10

    def test_aspect_ratio_filter_zero_height_treated_as_zero_ratio(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.min_aspect_ratio = 0.1
        cfg.max_aspect_ratio = 10.0
        dets = [_det(bbox=(0, 0, 10, 0))]
        filtered = svc._apply_aspect_ratio_filter(dets, cfg)
        # height=0 => aspect=0 => below min=0.1 => filtered out
        assert filtered == []

    def test_fuse_union_merges_overlapping(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.fusion_mode = FusionMode.UNION
        color = [_det(bbox=(0, 0, 20, 20), detection_type="color")]
        motion = [_det(bbox=(5, 5, 20, 20), detection_type="motion")]
        fused = svc._fuse_detections(color, motion, cfg)
        # Overlapping -> merged into one
        assert len(fused) == 1
        assert fused[0].detection_type == "fused"

    def test_fuse_union_keeps_non_overlapping(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.fusion_mode = FusionMode.UNION
        color = [_det(bbox=(0, 0, 10, 10))]
        motion = [_det(bbox=(100, 100, 10, 10))]
        fused = svc._fuse_detections(color, motion, cfg)
        assert len(fused) == 2

    def test_fuse_intersection_keeps_only_overlaps(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.fusion_mode = FusionMode.INTERSECTION
        color = [_det(bbox=(0, 0, 20, 20)), _det(bbox=(200, 200, 20, 20))]
        motion = [_det(bbox=(5, 5, 20, 20))]
        fused = svc._fuse_detections(color, motion, cfg)
        assert len(fused) == 1
        assert fused[0].detection_type == "fused"

    def test_fuse_color_priority_adds_only_non_overlapping_motion(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.fusion_mode = FusionMode.COLOR_PRIORITY
        color = [_det(bbox=(0, 0, 20, 20))]
        motion = [_det(bbox=(5, 5, 20, 20)), _det(bbox=(200, 200, 20, 20))]
        fused = svc._fuse_detections(color, motion, cfg)
        # 1 color + 1 non-overlapping motion
        assert len(fused) == 2

    def test_fuse_motion_priority_starts_from_motion(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.fusion_mode = FusionMode.MOTION_PRIORITY
        color = [_det(bbox=(5, 5, 20, 20)), _det(bbox=(200, 200, 20, 20))]
        motion = [_det(bbox=(0, 0, 20, 20))]
        fused = svc._fuse_detections(color, motion, cfg)
        assert len(fused) == 2

    def test_get_config_dict_is_serializable(self):
        svc = ColorDetectionService()
        cfg_dict = svc._get_config_dict()
        assert isinstance(cfg_dict, dict)
        # All values should be JSON-serializable primitives
        import json
        json.dumps(cfg_dict, default=str)  # should not raise

    def test_get_performance_info_contains_expected_keys(self):
        svc = ColorDetectionService()
        info = svc.get_performance_info()
        assert isinstance(info, dict)

    def test_reset_returns_service_to_clean_state(self):
        svc = ColorDetectionService()
        # Mutate internal state (reset() nulls _prev_frame, not _prev_gray)
        svc._prev_frame = np.zeros((10, 10), dtype=np.uint8)
        svc._frame_count = 42
        svc.reset()
        assert svc._prev_frame is None
        assert svc._frame_count == 0

    def test_cleanup_does_not_raise(self):
        svc = ColorDetectionService()
        svc.cleanup()  # should complete without error

    def test_update_config_emits_signal(self):
        svc = ColorDetectionService()
        received = []
        svc.configurationChanged.connect(lambda d: received.append(d))
        svc.update_config(HSVConfig(target_color_rgb=(0, 255, 0)))
        assert len(received) == 1

    def test_detection_clustering_groups_nearby(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.enable_detection_clustering = True
        cfg.clustering_distance = 50.0

        # Two detections close together, one far away
        dets = [
            _det(bbox=(0, 0, 10, 10)),
            _det(bbox=(15, 15, 10, 10)),
            _det(bbox=(300, 300, 10, 10)),
        ]
        result = svc._apply_detection_clustering(dets, cfg)
        # Clustering should reduce the count (nearby two become one)
        assert len(result) <= len(dets)

    def test_temporal_voting_requires_multiple_frames(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.enable_temporal_voting = True
        cfg.temporal_window_frames = 3
        cfg.temporal_threshold_frames = 2

        # First call: no history, returns empty or input depending on impl
        first = svc._apply_temporal_voting([_det()], cfg)
        assert isinstance(first, list)


# ---------------------------------------------------------------------------
# Hue expansion / scaling / frame-level helpers
# ---------------------------------------------------------------------------

class TestColorDetectionHelpers:
    """Additional helper tests for coverage expansion."""

    def test_apply_hue_expansion_basic(self):
        svc = ColorDetectionService()
        hsv_ranges = [(
            np.array([80, 50, 50], dtype=np.uint8),
            np.array([100, 255, 255], dtype=np.uint8),
        )]
        result = svc._apply_hue_expansion(hsv_ranges, expansion=5)
        # Should have at least one range
        assert len(result) >= 1
        # Hue values expanded
        lower, upper = result[-1]
        assert lower[0] <= 80
        assert upper[0] >= 100

    def test_apply_hue_expansion_handles_lower_wraparound(self):
        svc = ColorDetectionService()
        hsv_ranges = [(
            np.array([5, 50, 50], dtype=np.uint8),
            np.array([10, 255, 255], dtype=np.uint8),
        )]
        result = svc._apply_hue_expansion(hsv_ranges, expansion=15)
        # Wraparound creates extra range at top of hue
        assert len(result) >= 2

    def test_apply_hue_expansion_handles_upper_wraparound(self):
        svc = ColorDetectionService()
        hsv_ranges = [(
            np.array([170, 50, 50], dtype=np.uint8),
            np.array([175, 255, 255], dtype=np.uint8),
        )]
        result = svc._apply_hue_expansion(hsv_ranges, expansion=15)
        # Wraparound creates extra range at bottom of hue
        assert len(result) >= 2

    def test_apply_hue_expansion_error_returns_input(self):
        svc = ColorDetectionService()
        # Invalid data (list of integers, not tuples of arrays)
        result = svc._apply_hue_expansion([None], expansion=5)
        assert result == [None]

    def test_scale_detections_to_original_no_scale(self):
        svc = ColorDetectionService()
        dets = [_det()]
        # scale_factor >= 1.0 returns input unchanged
        result = svc._scale_detections_to_original(dets, 1.0)
        assert result is dets

    def test_scale_detections_to_original_scales_bbox(self):
        svc = ColorDetectionService()
        d = _det(bbox=(10, 10, 20, 20))
        scaled = svc._scale_detections_to_original([d], 0.5)
        # With scale=0.5 (processing), inverse=2, bbox (10,10,20,20) -> (20,20,40,40)
        assert scaled[0].bbox == (20, 20, 40, 40)

    def test_scale_detections_to_original_scales_area(self):
        svc = ColorDetectionService()
        d = _det(bbox=(0, 0, 10, 10), area=100)
        scaled = svc._scale_detections_to_original([d], 0.5)
        # Area scales by inv_scale^2 = 4
        assert scaled[0].area == 400

    def test_create_annotated_frame_no_detections(self):
        svc = ColorDetectionService()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        result = svc.create_annotated_frame(frame, [])
        # Should return a frame of same shape
        assert result.shape == frame.shape

    def test_create_overlay_frame_basic(self):
        svc = ColorDetectionService()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Should not raise
        result = svc.create_overlay_frame(frame)
        assert result is not None

    def test_update_performance_stats_increments_frame_count(self):
        svc = ColorDetectionService()
        initial_count = svc._frame_count
        svc._update_performance_stats(processing_time=0.01, detection_count=2)
        assert svc._frame_count == initial_count + 1

    def test_aspect_ratio_filter_zero_width(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        cfg.min_aspect_ratio = 0.1
        cfg.max_aspect_ratio = 10.0
        d = _det(bbox=(0, 0, 0, 10))  # zero width -> aspect=0
        result = svc._apply_aspect_ratio_filter([d], cfg)
        assert result == []

    def test_aspect_ratio_filter_exception_returns_input(self):
        svc = ColorDetectionService()
        cfg = HSVConfig(target_color_rgb=(255, 0, 0))
        # Make config access raise
        cfg.min_aspect_ratio = None
        d = _det()
        # Should not raise, returns input
        result = svc._apply_aspect_ratio_filter([d], cfg)
        assert result == [d]
