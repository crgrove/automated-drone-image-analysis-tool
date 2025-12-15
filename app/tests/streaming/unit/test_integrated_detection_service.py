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
