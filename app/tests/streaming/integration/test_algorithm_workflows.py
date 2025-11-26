"""Integration tests for full algorithm workflows."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import time

from algorithms.streaming.ColorDetection.services.ColorDetectionService import ColorDetectionService, HSVConfig
from algorithms.streaming.MotionDetection.services.MotionDetectionService import MotionDetectionService, MotionConfig, DetectionMode
from algorithms.streaming.ColorAnomalyAndMotionDetection.services import (
    ColorAnomalyAndMotionDetectionOrchestrator, ColorAnomalyAndMotionDetectionConfig, FusionMode
)


class TestColorDetectionWorkflow:
    """Integration tests for color detection workflow."""

    def test_full_color_detection_workflow(self, qapp):
        """Test complete color detection workflow."""
        service = ColorDetectionService()

        # Configure service
        config = HSVConfig(
            target_color_rgb=(255, 0, 0),
            hue_threshold=10,
            saturation_threshold=50,
            value_threshold=30,
            min_area=100
        )
        service.update_config(config)

        # Create test video sequence
        frames = []
        for i in range(10):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            if i >= 3:  # Add red square starting at frame 3
                frame[30:70, 30:70] = [0, 0, 255]  # Red in BGR
            frames.append(frame)

        # Process all frames
        all_detections = []
        for i, frame in enumerate(frames):
            detections = service.detect_colors(frame, float(i) * 0.033)
            all_detections.extend(detections)

        # Verify detections were made
        assert len(all_detections) > 0 or len(frames) < 3

    def test_color_detection_with_motion_filtering(self, qapp):
        """Test color detection with motion-based filtering."""
        service = ColorDetectionService()

        config = HSVConfig(
            target_color_rgb=(255, 0, 0),
            enable_motion_detection=True
        )
        service.update_config(config)

        # Create frames with motion
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [0, 0, 255]  # Red square appears

        service.detect_colors(frame1, 0.0)
        detections = service.detect_colors(frame2, 0.033)

        assert isinstance(detections, list)


class TestMotionDetectionWorkflow:
    """Integration tests for motion detection workflow."""

    def test_full_motion_detection_workflow(self, qapp):
        """Test complete motion detection workflow."""
        service = MotionDetectionService()

        # Configure service
        service.update_config(mode=DetectionMode.STATIC, sensitivity=0.5, min_area=100)

        # Create test video sequence
        frames = []
        for i in range(10):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            if i >= 3:  # Add object starting at frame 3
                frame[30:70, 30:70] = [255, 255, 255]
            frames.append(frame)

        # Process all frames
        for i, frame in enumerate(frames):
            service.process_frame(frame)

        # Verify background was learned
        assert service._prev_frame is not None

    def test_motion_detection_mode_switching(self, qapp):
        """Test switching between static and moving camera modes."""
        service = MotionDetectionService()

        # Start in static mode
        service.update_config(mode=DetectionMode.STATIC)

        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[30:70, 30:70] = [255, 255, 255]

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Switch to moving mode
        service.update_config(mode=DetectionMode.MOVING)

        service.process_frame(frame1)
        service.process_frame(frame2)

        # Should handle both modes
        assert service._current_mode == DetectionMode.MOVING


class TestIntegratedDetectionWorkflow:
    """Integration tests for integrated detection workflow."""

    def test_full_integrated_detection_workflow(self, qapp):
        """Test complete integrated detection workflow."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        # Configure for both motion and color
        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=True,
            fusion_mode=FusionMode.UNION,
            min_detection_area=100
        )
        service.update_config(config)

        # Create test video sequence
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frames = [frame1]
        for i in range(9):
            frame = frame1.copy()
            if i >= 3:
                frame[30:70, 30:70] = [255, 0, 0]  # Red square
            frames.append(frame)

        # Process frames
        all_detections = []
        for i in range(1, len(frames)):
            annotated_frame, detections, timings = service.process_frame(frames[i], float(i) * 0.033)
            all_detections.extend(detections)

        # Verify processing occurred
        assert service.metrics is not None

    def test_fusion_mode_workflows(self, qapp):
        """Test different fusion mode workflows."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        for fusion_mode in [FusionMode.UNION, FusionMode.INTERSECTION,
                            FusionMode.COLOR_PRIORITY, FusionMode.MOTION_PRIORITY]:
            config = ColorAnomalyAndMotionDetectionConfig(
                enable_motion=True,
                enable_color_quantization=True,
                fusion_mode=fusion_mode
            )
            service.update_config(config)

            frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
            frame2 = frame1.copy()
            frame2[30:70, 30:70] = [255, 0, 0]

            annotated_frame, detections, timings = service.process_frame(frame2, 0.0)
            assert isinstance(detections, list)

    def test_temporal_smoothing_workflow(self, qapp):
        """Test temporal smoothing across multiple frames."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_temporal_voting=True,
            temporal_window_frames=5
        )
        service.update_config(config)

        # Create sequence with intermittent detections
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(10):
            frame2 = frame1.copy()
            # Add motion every other frame
            if i % 2 == 0:
                frame2[30:70, 30:70] = [255, 255, 255]
            service.process_frame(frame2, float(i) * 0.033)
            frame1 = frame2

        # Temporal voting should stabilize detections
        assert hasattr(service, '_temporal_detection_history')


class TestPerformanceWorkflows:
    """Integration tests for performance-critical workflows."""

    def test_high_fps_processing(self, qapp):
        """Test processing at high frame rates."""
        service = ColorDetectionService()

        config = HSVConfig(target_color_rgb=(255, 0, 0))
        service.update_config(config)

        # Process many frames quickly
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[30:70, 30:70] = [0, 0, 255]

        start_time = time.time()
        for i in range(100):
            service.detect_colors(frame, float(i) * 0.033)
        elapsed = time.time() - start_time

        # Should process quickly (rough check)
        assert elapsed < 10.0  # Should process 100 frames in under 10 seconds

    def test_large_frame_processing(self, qapp):
        """Test processing large frames."""
        service = MotionDetectionService()

        service.update_config(mode=DetectionMode.STATIC)

        # Create large frame
        frame1 = np.zeros((1920, 1080, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[500:700, 500:700] = [255, 255, 255]

        # Should handle large frames
        service.process_frame(frame1)
        service.process_frame(frame2)

        assert service._prev_frame is not None
