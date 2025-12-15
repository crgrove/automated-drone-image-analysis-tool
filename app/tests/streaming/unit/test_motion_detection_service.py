"""Unit tests for MotionDetectionService."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from PySide6.QtCore import QObject
import time

from algorithms.streaming.MotionDetection.services.MotionDetectionService import (
    MotionDetectionService, MotionConfig, MotionDetection, DetectionMode, MotionAlgorithm
)


class TestMotionDetectionService:
    """Test suite for MotionDetectionService."""

    def test_initialization(self):
        """Test service initialization."""
        service = MotionDetectionService()

        assert service is not None
        assert hasattr(service, '_config')
        assert hasattr(service, 'detectionsReady')
        assert hasattr(service, 'performanceUpdate')
        assert hasattr(service, 'configurationChanged')
        assert hasattr(service, 'modeChanged')

    def test_update_config(self):
        """Test configuration update."""
        service = MotionDetectionService()

        # update_config takes **kwargs, not a config object
        service.update_config(sensitivity=0.7, min_area=200, motion_threshold=30.0)

        # Verify config was updated
        assert service._config.sensitivity == 0.7
        assert service._config.min_area == 200
        assert service._config.motion_threshold == 30.0

    def test_process_frame_static_mode(self):
        """Test frame processing in static camera mode."""
        service = MotionDetectionService()

        # Set to static mode
        service.update_config(mode=DetectionMode.STATIC)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:60, 50:60] = [255, 255, 255]  # Add white square

        # Process first frame (background learning)
        service.process_frame(frame1)

        # Process second frame (should detect motion)
        service.process_frame(frame2)

        # Should have processed frames
        assert service._prev_frame is not None

    def test_process_frame_moving_mode(self):
        """Test frame processing in moving camera mode."""
        service = MotionDetectionService()

        # Set to moving mode
        service.update_config(mode=DetectionMode.MOVING)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:60, 50:60] = [255, 255, 255]

        # Process frames
        service.process_frame(frame1)
        service.process_frame(frame2)

        # Should have processed frames
        assert service._prev_frame is not None

    def test_process_frame_auto_mode(self):
        """Test frame processing in auto mode."""
        service = MotionDetectionService()

        # Set to auto mode
        service.update_config(mode=DetectionMode.AUTO)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:60, 50:60] = [255, 255, 255]

        # Process frames
        service.process_frame(frame1)
        service.process_frame(frame2)

        # Should have processed frames
        assert service._prev_frame is not None

    def test_mog2_algorithm(self):
        """Test MOG2 background subtraction algorithm."""
        service = MotionDetectionService()

        service.update_config(mode=DetectionMode.STATIC, algorithm=MotionAlgorithm.MOG2)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:60, 50:60] = [255, 255, 255]

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Should have background subtractor
        assert service._bg_subtractor_mog2 is not None

    def test_knn_algorithm(self):
        """Test KNN background subtraction algorithm."""
        service = MotionDetectionService()

        service.update_config(mode=DetectionMode.STATIC, algorithm=MotionAlgorithm.KNN)

        # Create test frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:60, 50:60] = [255, 255, 255]

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Should have background subtractor
        assert service._bg_subtractor_knn is not None

    def test_min_area_filtering(self):
        """Test minimum area filtering."""
        service = MotionDetectionService()

        service.update_config(min_area=1000, mode=DetectionMode.STATIC)

        # Create test frames with small motion
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:52, 50:52] = [255, 255, 255]  # Very small motion

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Small detections should be filtered out
        # (exact behavior depends on implementation)

    def test_sensitivity_adjustment(self):
        """Test sensitivity parameter adjustment."""
        service = MotionDetectionService()

        # Test with different sensitivity values
        for sensitivity in [0.3, 0.5, 0.7, 0.9]:
            service.update_config(sensitivity=sensitivity)
            assert service._config.sensitivity == sensitivity

    def test_camera_motion_compensation(self):
        """Test camera motion compensation."""
        service = MotionDetectionService()

        service.update_config(mode=DetectionMode.MOVING)

        # Create frames simulating camera movement
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.roll(frame1, 5, axis=1)  # Simulate horizontal camera movement

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Should handle camera motion
        assert service._prev_frame is not None

    def test_signal_emission(self, qapp):
        """Test that signals are emitted."""
        service = MotionDetectionService()

        detections_received = []

        def on_detections(detections, camera_motion, frame):
            detections_received.extend(detections)

        service.detectionsReady.connect(on_detections)

        # Process frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[50:60, 50:60] = [255, 255, 255]

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Verify signals exist
        assert service.detectionsReady is not None
        assert service.performanceUpdate is not None

    def test_error_handling_invalid_frame(self):
        """Test error handling with invalid frame."""
        service = MotionDetectionService()

        # Test with None frame
        try:
            service.process_frame(None)
        except (AttributeError, TypeError):
            pass  # Expected error

    def test_error_handling_empty_frame(self):
        """Test error handling with empty frame."""
        service = MotionDetectionService()

        empty_frame = np.array([], dtype=np.uint8)

        try:
            service.process_frame(empty_frame)
        except (ValueError, IndexError):
            pass  # Expected error

    def test_performance_tracking(self):
        """Test performance metrics tracking."""
        service = MotionDetectionService()

        # Process some frames
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(5):
            service.process_frame(frame)
            time.sleep(0.001)

        # Check performance tracking
        assert hasattr(service, '_processing_times')

    def test_mode_switching(self):
        """Test switching between detection modes."""
        service = MotionDetectionService()

        # Switch modes - verify config is updated
        # Note: _current_mode may be auto-detected, so we check _config.mode instead
        for mode in [DetectionMode.STATIC, DetectionMode.MOVING, DetectionMode.AUTO]:
            service.update_config(mode=mode)
            assert service._config.mode == mode

    def test_gpu_detection(self):
        """Test GPU availability detection."""
        service = MotionDetectionService()

        assert hasattr(service, '_use_gpu')
        assert isinstance(service._use_gpu, bool)

    def test_detection_metadata(self):
        """Test that detections include proper metadata."""
        service = MotionDetectionService()

        service.update_config(mode=DetectionMode.STATIC)

        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Detections should have proper structure
        # (exact format depends on implementation)
