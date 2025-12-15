"""Real integration tests that actually run the algorithms without mocks."""

from algorithms.streaming.ColorAnomalyAndMotionDetection.services import (
    ColorAnomalyAndMotionDetectionOrchestrator, ColorAnomalyAndMotionDetectionConfig
)
from algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.ColorAnomalyAndMotionDetectionController import ColorAnomalyAndMotionDetectionController
import pytest
import numpy as np
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestRealIntegratedDetection:
    """Real integration tests that actually execute the algorithm."""

    def test_real_controller_initialization(self, qapp):
        """Test that controller can actually be initialized with real service."""
        algorithm_config = {
            'name': 'ColorAnomalyAndMotionDetection',
            'category': 'streaming'
        }

        controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

        # Verify real service was created
        assert controller.integrated_detector is not None
        assert isinstance(controller.integrated_detector, ColorAnomalyAndMotionDetectionOrchestrator)

    def test_real_frame_processing(self, qapp):
        """Test processing real frames through the actual algorithm."""
        algorithm_config = {
            'name': 'ColorAnomalyAndMotionDetection',
            'category': 'streaming'
        }

        controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

        # Create a real test frame with actual content
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add a colored rectangle to detect
        frame[100:200, 100:200] = [0, 0, 255]  # Red in BGR

        # Process multiple frames to let background subtractor learn
        for i in range(5):
            detections = controller.process_frame(frame.copy(), float(i) * 0.033)
            assert isinstance(detections, list)

        # After background learning, add motion
        frame2 = frame.copy()
        frame2[150:250, 150:250] = [0, 255, 0]  # Green square moved
        detections = controller.process_frame(frame2, 0.2)

        # Should be able to process without errors
        assert isinstance(detections, list)

    def test_real_service_direct(self, qapp):
        """Test the service directly without controller."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        # Create test frames
        frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        frame2[100:200, 100:200] = [255, 255, 255]  # White square

        # Process first frame (background learning)
        annotated1, detections1, timings1 = service.process_frame(frame1, 0.0)
        assert annotated1 is not None
        assert isinstance(detections1, list)
        assert timings1 is not None

        # Process second frame (should detect motion)
        annotated2, detections2, timings2 = service.process_frame(frame2, 0.033)
        assert annotated2 is not None
        assert isinstance(detections2, list)
        assert timings2 is not None

    def test_real_config_update(self, qapp):
        """Test updating configuration on real service."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        # Update config with real values
        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=True,
            min_detection_area=100
        )
        service.update_config(config)

        # Process a frame to verify config was applied
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[100:200, 100:200] = [0, 0, 255]

        annotated, detections, timings = service.process_frame(frame, 0.0)
        assert annotated is not None
