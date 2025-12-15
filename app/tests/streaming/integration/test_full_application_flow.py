"""Full application flow tests that simulate real user interactions."""

from core.services.streaming.RTMPStreamService import StreamType
from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
import pytest
import numpy as np
import sys
import os
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Signal

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestFullApplicationFlow:
    """Test the full application flow as a user would experience it."""

    def test_window_opens_with_algorithm(self, qapp):
        """Test that window opens and algorithm loads."""
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            assert window is not None
            assert window.current_algorithm_name == 'ColorAnomalyAndMotionDetection'
            assert window.algorithm_widget is not None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_algorithm_processes_frames(self, qapp):
        """Test that algorithm can process frames when window is set up."""
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            # Create a test frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[100:200, 100:200] = [0, 0, 255]  # Red square

            # Simulate frame processing (as would happen from stream)
            # Process multiple frames to let background learn
            for i in range(5):
                try:
                    detections = window.algorithm_widget.process_frame(frame.copy(), float(i) * 0.033)
                    assert isinstance(detections, list)
                except Exception as e:
                    pytest.fail(f"Frame processing failed: {e}")

            # Test the actual on_frame_received method (the real flow from stream)
            # This is what gets called when frames come from StreamCoordinator
            # This would have caught the update_detections bug
            try:
                window.on_frame_received(frame, 0.2)
            except AttributeError as e:
                if 'update_detections' in str(e) or 'update_thumbnails' in str(e):
                    pytest.fail(f"Thumbnail widget method error (this test should catch it): {e}")
                raise
            except Exception as e:
                pytest.fail(f"on_frame_received failed: {e}")
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_stream_connection_flow(self, qapp):
        """Test the full flow of connecting to a stream and processing frames."""
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            # Mock the stream manager to simulate a file connection
            mock_stream_manager = Mock()
            mock_stream_manager.connect_to_stream = Mock(return_value=True)
            mock_stream_manager.frameReceived = Mock()
            mock_stream_manager.connectionChanged = Mock()
            mock_stream_manager.disconnect_stream = Mock()

            with patch('core.controllers.streaming.components.StreamCoordinator.StreamManager', return_value=mock_stream_manager):
                # Simulate connecting to a file
                success = window.stream_coordinator.connect_stream("test_video.mp4", StreamType.FILE)
                assert success is True

                # Simulate receiving frames
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                for i in range(3):
                    window.on_frame_received(frame.copy(), float(i) * 0.033)

                # Disconnect
                window.stream_coordinator.disconnect_stream()
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_algorithm_switching(self, qapp):
        """Test switching between different algorithms."""
        window = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
        try:
            # Mock algorithm loading
            def get_config_side_effect(name):
                return {'name': name, 'category': 'streaming'}

            class MockAlgorithmController(QWidget):
                detectionsReady = Signal(list)
                frameProcessed = Signal(np.ndarray)
                configChanged = Signal(dict)
                statusUpdate = Signal(str)
                requestRecording = Signal(bool)

                def __init__(self, algorithm_config, theme, parent=None):
                    super().__init__(parent)
                    self.algorithm_config = algorithm_config
                    self.theme = theme
                    self.is_running = False

                def setup_ui(self):
                    pass

                def process_frame(self, frame, timestamp):
                    return []

                def get_config(self):
                    return {}

                def set_config(self, config):
                    pass

                def cleanup(self):
                    """Cleanup method required by StreamViewerWindow."""
                    pass

            with patch.object(window, '_get_algorithm_config', side_effect=get_config_side_effect):
                with patch.object(window, '_import_algorithm_controller', return_value=MockAlgorithmController):
                    # Switch to MotionDetection
                    window.load_algorithm('MotionDetection')
                    assert window.current_algorithm_name == 'MotionDetection'

                    # Switch to ColorDetection
                    window.load_algorithm('ColorDetection')
                    assert window.current_algorithm_name == 'ColorDetection'
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes
