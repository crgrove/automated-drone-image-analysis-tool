"""Integration tests using actual video files."""

from core.services.streaming.RTMPStreamService import StreamType
from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
from algorithms.streaming.ColorAnomalyAndMotionDetection.services import (
    ColorAnomalyAndMotionDetectionOrchestrator, ColorAnomalyAndMotionDetectionConfig
)
import pytest
import numpy as np
import cv2
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
import time
from PySide6.QtWidgets import QApplication

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestWithRealVideo:
    """Tests using actual video files from test data."""

    @pytest.fixture
    def test_video_path(self):
        """Get path to test video file."""
        test_data_dir = Path(__file__).parent.parent.parent / 'data' / 'video'
        video_path = test_data_dir / 'DJI_0462.MP4'

        if not video_path.exists():
            pytest.skip(f"Test video not found: {video_path}")

        return str(video_path)

    def test_process_video_frames(self, qapp, test_video_path):
        """Test processing frames from actual video file."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        # Configure service
        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=True,
            min_detection_area=100
        )
        service.update_config(config)

        # Open video file
        cap = cv2.VideoCapture(test_video_path)
        if not cap.isOpened():
            pytest.skip(f"Could not open video file: {test_video_path}")

        try:
            frame_count = 0
            max_frames = 30  # Process first 30 frames for testing

            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                # Process frame
                timestamp = frame_count / 30.0  # Assume 30 FPS
                annotated, detections, timings = service.process_frame(frame, timestamp)

                assert annotated is not None
                assert isinstance(detections, list)
                assert timings is not None

                frame_count += 1

            assert frame_count > 0, "No frames were processed"

        finally:
            cap.release()

    def test_stream_viewer_with_video_file(self, qapp, test_video_path):
        """Test StreamViewerWindow with actual video file connection."""
        window = StreamViewerWindow(algorithm_name='IntegratedDetection', theme='dark')
        try:
            # Mock stream manager to simulate file connection
            mock_stream_manager = Mock()
            mock_stream_manager.connect_to_stream = Mock(return_value=True)
            mock_stream_manager.frameReceived = Mock()
            mock_stream_manager.connectionChanged = Mock()
            mock_stream_manager.disconnect_stream = Mock()

            # Simulate frames from video
            cap = cv2.VideoCapture(test_video_path)
            if not cap.isOpened():
                pytest.skip(f"Could not open video file: {test_video_path}")

            try:
                with patch('core.controllers.streaming.components.StreamCoordinator.StreamManager', return_value=mock_stream_manager):
                    # Connect to video file
                    success = window.stream_coordinator.connect_stream(test_video_path, StreamType.FILE)
                    assert success is True

                    # Process first 10 frames
                    frame_count = 0
                    while frame_count < 10:
                        ret, frame = cap.read()
                        if not ret:
                            break

                        # Simulate frame received from stream
                        timestamp = frame_count / 30.0
                        window.on_frame_received(frame, timestamp)

                        frame_count += 1

                    # Disconnect
                    window.stream_coordinator.disconnect_stream()

            finally:
                cap.release()
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_video_processing_performance(self, qapp, test_video_path):
        """Test processing performance with real video."""
        service = ColorAnomalyAndMotionDetectionOrchestrator()

        config = ColorAnomalyAndMotionDetectionConfig(
            enable_motion=True,
            enable_color_quantization=True,
            processing_width=640,
            processing_height=480
        )
        service.update_config(config)

        cap = cv2.VideoCapture(test_video_path)
        if not cap.isOpened():
            pytest.skip(f"Could not open video file: {test_video_path}")

        try:
            start_time = time.time()
            frame_count = 0
            max_frames = 100

            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                timestamp = frame_count / 30.0
                annotated, detections, timings = service.process_frame(frame, timestamp)

                frame_count += 1

            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0

            # Should process at reasonable speed (at least 5 FPS for 640x480)
            assert fps >= 5.0, f"Processing too slow: {fps:.2f} FPS"

        finally:
            cap.release()
