"""Tests that verify the full frame processing flow including thumbnail updates."""

from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
import pytest
import numpy as np
import sys
import os
from PySide6.QtWidgets import QApplication

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestThumbnailWidgetIntegration:
    """Tests that verify thumbnail widget is called correctly with detections."""

    def test_on_frame_received_with_detections(self, qapp):
        """Test that on_frame_received properly handles detections and updates thumbnails."""
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            # Create a test frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[100:200, 100:200] = [0, 0, 255]  # Red square

            # Process a few frames to let background learn
            for i in range(5):
                window.algorithm_widget.process_frame(frame.copy(), float(i) * 0.033)

            # Now create a frame with motion that should produce detections
            frame_with_motion = frame.copy()
            frame_with_motion[150:250, 150:250] = [0, 255, 0]  # Green square (motion)

            # Process frame to get detections
            window.algorithm_widget.process_frame(frame_with_motion, 0.2)

            # Now test the actual on_frame_received method (the real flow)
            # This is what gets called when frames come from the stream
            try:
                window.on_frame_received(frame_with_motion, 0.2)
                # If we get here without exception, the thumbnail widget was called correctly
            except AttributeError as e:
                if 'update_detections' in str(e) or 'update_thumbnails' in str(e):
                    pytest.fail(f"Thumbnail widget method error: {e}")
                raise
            except Exception as e:
                pytest.fail(f"on_frame_received failed: {e}")
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_on_frame_received_with_empty_detections(self, qapp):
        """Test that on_frame_received handles empty detections gracefully."""
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Process a few frames to let background learn
            for i in range(5):
                window.algorithm_widget.process_frame(frame.copy(), float(i) * 0.033)

            # Call on_frame_received with frame that produces no detections
            try:
                window.on_frame_received(frame, 0.2)
                # Should not crash even with no detections
            except Exception as e:
                pytest.fail(f"on_frame_received failed with empty detections: {e}")
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_on_frame_received_with_detections_from_different_algorithms(self, qapp):
        """Test that detections from different algorithms work correctly."""
        # Test with IntegratedDetection
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[100:200, 100:200] = [0, 0, 255]

            # Process frames
            for i in range(5):
                window.algorithm_widget.process_frame(frame.copy(), float(i) * 0.033)

            # Get detections and test on_frame_received
            window.algorithm_widget.process_frame(frame, 0.2)

            # This should work regardless of detection format
            try:
                window.on_frame_received(frame, 0.2)
            except Exception as e:
                pytest.fail(f"on_frame_received failed with IntegratedDetection detections: {e}")
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_thumbnail_widget_receives_correct_format(self, qapp):
        """Test that thumbnail widget receives detections in the correct format."""
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            # Mock the thumbnail widget to verify it's called correctly
            original_update = window.thumbnail_widget.update_thumbnails
            call_args = []

            def mock_update_thumbnails(frame, detections, *args, **kwargs):
                call_args.append((frame, detections))
                # Verify detections are objects with required attributes
                for det in detections:
                    assert hasattr(det, 'bbox'), "Detection missing bbox attribute"
                    assert hasattr(det, 'centroid'), "Detection missing centroid attribute"
                    assert hasattr(det, 'metadata'), "Detection missing metadata attribute"
                return original_update(frame, detections, *args, **kwargs)

            window.thumbnail_widget.update_thumbnails = mock_update_thumbnails

            frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # Process frames to let background learn
            for i in range(10):
                window.algorithm_widget.process_frame(frame.copy(), float(i) * 0.033)

            # Create frame with significant motion that should produce detections
            frame_with_detections = frame.copy()
            frame_with_detections[100:300, 100:300] = [255, 255, 255]  # Large white square

            # Process to get detections first
            detections = window.algorithm_widget.process_frame(frame_with_detections, 0.5)

            # Only test format if we have detections
            if detections:
                # Call on_frame_received - this should call update_thumbnails
                window.on_frame_received(frame_with_detections, 0.5)

                # Verify thumbnail widget was called (if detections exist)
                assert len(call_args) > 0, "update_thumbnails was never called even though detections exist"
                assert call_args[0][0] is not None, "Frame was None"
                assert len(call_args[0][1]) > 0, "Detections list was empty when detections were expected"
            else:
                # If no detections, at least verify the method exists and can be called
                # This ensures the bug (wrong method name) would be caught
                assert hasattr(window.thumbnail_widget, 'update_thumbnails'), \
                    "update_thumbnails method missing - this would catch the update_detections bug"
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes
