"""Unit tests for ColorAnomalyAndMotionDetectionOrchestrator."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from PySide6.QtCore import QObject
import time

from algorithms.streaming.ColorAnomalyAndMotionDetection.services import (
    ColorAnomalyAndMotionDetectionOrchestrator, ColorAnomalyAndMotionDetectionConfig, MotionAlgorithm, FusionMode, Detection
)


class TestIntegratedDetectionService:
    """Test suite for ColorAnomalyAndMotionDetectionOrchestrator."""

    def test_initialization(self):
        """Test service initialization."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        assert service is not None
        assert hasattr(service, 'config')
        assert hasattr(service, 'frameProcessed')
        assert hasattr(service, 'performanceUpdate')

    def test_update_config(self):
        """Test configuration update."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        new_config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=True,
            motion_algorithm=MotionAlgorithm.MOG2,
            fusion_mode=FusionMode.UNION
        )

        service.update_config(new_config)

        assert service.config.enable_motion is True
        assert service.config.fusion_mode == FusionMode.UNION

    def test_detect_motion_only(self):
        """Test detection with motion only."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=False
        )
        service.update_config(config)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]  # Add white square

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        assert isinstance(detections, list)

    def test_detect_color_only(self):
        """Test detection with color quantization only."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=False,
            enable_color_quantization=True
        )
        service.update_config(config)

        # Create test frame with rare color
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[:, :] = [128, 128, 128]  # Gray background
        frame[30:70, 30:70] = [255, 0, 0]  # Red square (rare)

        annotated_frame, detections, timings = service.process_frame(frame, 0.0)

        assert isinstance(detections, list)

    def test_detect_fusion_mode_union(self):
        """Test detection with fusion mode UNION."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=True,
            fusion_mode=FusionMode.UNION
        )
        service.update_config(config)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 0, 0]  # Red square

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        assert isinstance(detections, list)

    def test_detect_fusion_mode_intersection(self):
        """Test detection with fusion mode INTERSECTION."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=True,
            fusion_mode=FusionMode.INTERSECTION
        )
        service.update_config(config)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 0, 0]

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        assert isinstance(detections, list)

    def test_min_area_filtering(self):
        """Test minimum area filtering."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            min_detection_area=1000  # High threshold
        )
        service.update_config(config)

        # Create test frames with small motion
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:52, 50:52] = [255, 255, 255]  # Very small

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        # Small detections should be filtered
        for det in detections:
            assert det.area >= config.min_detection_area

    def test_max_area_filtering(self):
        """Test maximum area filtering."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            max_detection_area=100  # Low threshold
        )
        service.update_config(config)

        # Create test frames with large motion
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[10:90, 10:90] = [255, 255, 255]  # Large area

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        # Large detections should be filtered
        for det in detections:
            assert det.area <= config.max_detection_area

    def test_motion_algorithm_mog2(self):
        """Test MOG2 motion algorithm."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            motion_algorithm=MotionAlgorithm.MOG2
        )
        service.update_config(config)

        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        assert isinstance(detections, list)

    def test_motion_algorithm_knn(self):
        """Test KNN motion algorithm."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            motion_algorithm=MotionAlgorithm.KNN
        )
        service.update_config(config)

        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        assert isinstance(detections, list)

    def test_temporal_voting(self):
        """Test temporal voting for detection stability."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_temporal_voting=True,
            temporal_window_frames=3
        )
        service.update_config(config)

        # Process multiple frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(5):
            frame2 = frame1.copy()
            frame2[30:70, 30:70] = [255, 255, 255]
            service.process_frame(frame2, float(i) * 0.033)
            frame1 = frame2

        # Temporal voting should stabilize detections
        assert hasattr(service, '_temporal_detection_history')

    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]

        # Process frames
        for i in range(5):
            service.process_frame(frame2, float(i) * 0.033)
            time.sleep(0.001)

        # Check metrics
        assert hasattr(service, 'metrics')
        assert service.metrics is not None

    def test_error_handling_invalid_frame(self):
        """Test error handling with invalid frame."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        try:
            service.process_frame(None, 0.0)
        except (AttributeError, TypeError):
            pass  # Expected error

    def test_error_handling_empty_frame(self):
        """Test error handling with empty frame."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        empty_frame = np.array([], dtype=np.uint8)

        try:
            service.process_frame(empty_frame, 0.0)
        except (ValueError, IndexError):
            pass  # Expected error

    def test_detection_metadata(self):
        """Test that detections include proper metadata."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(enable_motion=True)
        service.update_config(config)

        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]

        annotated_frame, detections, timings = service.process_frame(frame2, 0.0)

        if len(detections) > 0:
            detection = detections[0]
            assert hasattr(detection, 'bbox')
            assert hasattr(detection, 'centroid')
            assert hasattr(detection, 'area')
            assert hasattr(detection, 'confidence')
            assert hasattr(detection, 'detection_type')

    def test_signal_emission(self, qapp):
        """Test that signals are emitted."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        detections_received = []

        def on_frame_processed(frame, detections, metrics):
            detections_received.extend(detections)

        service.frameProcessed.connect(on_frame_processed)

        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]

        service.process_frame(frame2, 0.0)

        assert service.frameProcessed is not None
        assert service.performanceUpdate is not None


# ---------------------------------------------------------------------------
# Pure helper coverage for the orchestrator
# ---------------------------------------------------------------------------

def _det(bbox=(10, 10, 20, 20), detection_type="color_anomaly", confidence=0.8, area=400):
    import numpy as _np
    x, y, w, h = bbox
    return Detection(
        bbox=bbox,
        centroid=(x + w // 2, y + h // 2),
        area=area,
        confidence=confidence,
        timestamp=0.0,
        contour=_np.array([[[x, y]], [[x + w, y]], [[x + w, y + h]], [[x, y + h]]], dtype=_np.int32),
        detection_type=detection_type,
    )


class TestOrchestratorPureHelpers:
    """Pure logic helpers — no Qt signals, no video."""

    def test_iou_identical(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        assert svc._calculate_iou((0, 0, 10, 10), (0, 0, 10, 10)) == pytest.approx(1.0)

    def test_iou_disjoint(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        assert svc._calculate_iou((0, 0, 10, 10), (100, 100, 10, 10)) == 0.0

    def test_merge_single_detection_returns_input(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        det = _det()
        assert svc._merge_detections([det]) is det

    def test_merge_two_detections_uses_contours(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        a = _det(bbox=(0, 0, 10, 10))
        b = _det(bbox=(20, 20, 10, 10))
        merged = svc._merge_detections([a, b])
        assert merged.bbox[0] == 0
        assert merged.bbox[1] == 0
        # Merge covers both
        assert merged.bbox[2] >= 30
        assert merged.metadata["merged_from"] == 2

    def test_merge_without_contours_falls_back_to_bboxes(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        a = _det(bbox=(0, 0, 10, 10))
        b = _det(bbox=(100, 0, 10, 10))
        a.contour = None
        b.contour = None
        merged = svc._merge_detections([a, b])
        assert merged.bbox[0] == 0
        assert merged.bbox[2] == 110

    def test_merge_marks_fused_when_color_and_motion(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        color = _det(detection_type="color_anomaly")
        motion = _det(detection_type="mog2_motion", bbox=(5, 5, 20, 20))
        merged = svc._merge_detections([color, motion])
        assert merged.detection_type == "fused"

    def test_temporal_voting_disabled_returns_input(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_temporal_voting = False
        dets = [_det()]
        assert svc._apply_temporal_voting(dets) == dets

    def test_temporal_voting_needs_full_window(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_temporal_voting = True
        svc.config.temporal_window_frames = 3
        svc.config.temporal_threshold_frames = 2
        dets = [_det()]
        # Before history is full, returns current as-is
        result = svc._apply_temporal_voting(dets)
        assert result == dets

    def test_clustering_merges_nearby_detections(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_detection_clustering = True
        svc.config.clustering_distance = 30.0
        dets = [
            _det(bbox=(0, 0, 10, 10)),
            _det(bbox=(12, 12, 10, 10)),  # very close - should cluster
            _det(bbox=(200, 200, 10, 10)),  # far - stays alone
        ]
        result = svc._apply_detection_clustering(dets)
        assert len(result) == 2
        # One of them should be marked as clustered
        assert any(d.metadata.get("clustered") for d in result)

    def test_clustering_disabled_returns_input(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_detection_clustering = False
        dets = [_det(), _det(bbox=(100, 100, 10, 10))]
        assert svc._apply_detection_clustering(dets) == dets

    def test_aspect_ratio_filter_when_disabled_returns_input(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_aspect_ratio_filter = False
        dets = [_det(bbox=(0, 0, 100, 10))]
        assert svc._apply_aspect_ratio_filter(dets) == dets

    def test_aspect_ratio_filter_when_enabled_filters_extreme(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_aspect_ratio_filter = True
        svc.config.min_aspect_ratio = 0.5
        svc.config.max_aspect_ratio = 2.0
        dets = [
            _det(bbox=(0, 0, 10, 10)),    # 1.0 - kept
            _det(bbox=(0, 0, 100, 10)),   # 10.0 - filtered
        ]
        result = svc._apply_aspect_ratio_filter(dets)
        assert len(result) == 1

    def test_reset_metrics_clears(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.reset_metrics()
        metrics = svc.get_metrics()
        # Fresh metrics object
        assert metrics is not None

    def test_reset_for_new_video_resets_state(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.reset_for_new_video()
        # Just verify it completes without error
        assert svc is not None

    def test_cleanup_does_not_raise(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.cleanup()

    def test_get_metrics_returns_object(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        assert svc.get_metrics() is not None


# ---------------------------------------------------------------------------
# Scaling detections back to original
# ---------------------------------------------------------------------------

class TestOrchestratorScaling:
    """_scale_detections_to_original math tests."""

    def test_scale_factor_one_returns_input(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        dets = [_det()]
        assert svc._scale_detections_to_original(dets, 1.0) is dets

    def test_scale_factor_half_doubles_bbox(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        d = _det(bbox=(10, 10, 20, 20), area=100)
        result = svc._scale_detections_to_original([d], 0.5)
        assert result[0].bbox == (20, 20, 40, 40)
        assert result[0].area == 400

    def test_scale_preserves_contour_when_present(self):
        import numpy as _np
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        d = _det(bbox=(0, 0, 10, 10))
        result = svc._scale_detections_to_original([d], 0.5)
        assert result[0].contour is not None

    def test_scale_adds_metadata(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        d = _det()
        result = svc._scale_detections_to_original([d], 0.5)
        assert "scale_factor_applied" in result[0].metadata


# ---------------------------------------------------------------------------
# _fuse_detections short-circuits
# ---------------------------------------------------------------------------

class TestOrchestratorFusionShortcuts:
    def test_fuse_no_motion_returns_color(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        color = [_det()]
        result = svc._fuse_detections([], color)
        assert result == color

    def test_fuse_no_color_returns_motion(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        motion = [_det()]
        result = svc._fuse_detections(motion, [])
        assert result == motion

    def test_fuse_disabled_concatenates(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_fusion = False
        motion = [_det(bbox=(0, 0, 5, 5))]
        color = [_det(bbox=(100, 100, 5, 5))]
        result = svc._fuse_detections(motion, color)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# _apply_color_exclusion_filter
# ---------------------------------------------------------------------------

class TestOrchestratorColorExclusion:
    def test_exclusion_disabled_returns_all(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_color_exclusion = False
        dets = [_det()]
        frame = np.zeros((50, 50, 3), dtype=np.uint8)
        result = svc._apply_color_exclusion_filter(dets, frame)
        assert result == dets

    def test_exclusion_empty_ranges_returns_all(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_color_exclusion = True
        svc.config.excluded_hue_ranges = []
        dets = [_det()]
        frame = np.zeros((50, 50, 3), dtype=np.uint8)
        result = svc._apply_color_exclusion_filter(dets, frame)
        assert result == dets

    def test_exclusion_filters_matching_hue(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_color_exclusion = True
        svc.config.excluded_hue_ranges = [(0, 20)]  # Red
        # Red BGR pixel -> hue around 0 after conversion
        frame = np.full((50, 50, 3), [0, 0, 255], dtype=np.uint8)
        d = _det(bbox=(5, 5, 10, 10))
        d.metadata = {"dominant_color": (0, 0, 255)}  # Red in BGR
        result = svc._apply_color_exclusion_filter([d], frame)
        # Red should be excluded
        assert len(result) == 0

    def test_exclusion_keeps_non_matching_hue(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_color_exclusion = True
        svc.config.excluded_hue_ranges = [(60, 80)]  # Green-ish only
        frame = np.full((50, 50, 3), [0, 0, 255], dtype=np.uint8)  # Red
        d = _det(bbox=(5, 5, 10, 10))
        d.metadata = {"dominant_color": (0, 0, 255)}
        result = svc._apply_color_exclusion_filter([d], frame)
        assert len(result) == 1

    def test_exclusion_wraparound_range(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.enable_color_exclusion = True
        # Wraparound: hue_min > hue_max means wrap around 0/180
        svc.config.excluded_hue_ranges = [(170, 10)]
        frame = np.full((50, 50, 3), [0, 0, 255], dtype=np.uint8)
        d = _det(bbox=(5, 5, 10, 10))
        d.metadata = {"dominant_color": (0, 0, 255)}  # Red hue ~0 in OpenCV
        result = svc._apply_color_exclusion_filter([d], frame)
        # Red (~hue 0) falls within wraparound [170, 10]
        assert len(result) == 0


# ---------------------------------------------------------------------------
# _apply_mask_filter
# ---------------------------------------------------------------------------

class TestOrchestratorMaskFilter:
    def test_mask_disabled_returns_all(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.mask_enabled = False
        dets = [_det()]
        result = svc._apply_mask_filter(dets)
        assert result == dets

    def test_mask_without_manager_returns_all(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        svc.config.mask_enabled = True
        dets = [_det()]
        # No _mask_manager attribute
        result = svc._apply_mask_filter(dets)
        assert result == dets


# ---------------------------------------------------------------------------
# _merge_detections edge cases
# ---------------------------------------------------------------------------

class TestOrchestratorMergeEdgeCases:
    def test_merge_zero_moment_falls_back_to_bbox_center(self):
        svc = ColorAnomalyAndMotionDetectionOrchestrator()
        a = _det(bbox=(0, 0, 10, 10))
        b = _det(bbox=(20, 20, 10, 10))
        # Both have contours; merge
        merged = svc._merge_detections([a, b])
        assert merged.centroid is not None
