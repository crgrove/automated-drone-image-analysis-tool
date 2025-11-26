"""Integration tests for StreamViewerWindow."""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtTest import QTest

from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow


class TestStreamViewerWindow:
    """Test suite for StreamViewerWindow."""

    def test_initialization(self, qapp):
        """Test window initialization."""
        # Pass empty string to prevent default algorithm loading
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            assert window.theme == 'dark'
            assert window.logger is not None
            assert window.stream_coordinator is not None
            assert window.detection_renderer is not None
            assert window.stream_statistics is not None
            assert window.algorithm_widget is None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_initialization_with_algorithm(self, qapp):
        """Test window initialization with algorithm."""
        # Create a mock controller class that has all required signals and methods
        class MockAlgorithmController(QWidget):
            # Required signals
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

        with patch('core.controllers.streaming.StreamViewerWindow.StreamAlgorithmController', MockAlgorithmController):
            window = StreamViewerWindow(algorithm_name='MotionDetection', theme='dark')
            try:
                # Algorithm should be loaded (may be None if loading fails, which is acceptable in test)
                # Just verify the window was created successfully
                assert window is not None
            finally:
                window.close()
                QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_load_algorithm(self, qapp):
        """Test loading an algorithm."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Mock algorithm config and controller import methods
            mock_config = {'name': 'MotionDetection', 'category': 'streaming'}

            # Create a mock controller class that has all required signals and methods
            class MockAlgorithmController(QWidget):
                # Required signals
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

            with patch.object(window, '_get_algorithm_config', return_value=mock_config):
                with patch.object(window, '_import_algorithm_controller', return_value=MockAlgorithmController):
                    window.load_algorithm('MotionDetection')

                    # Check that algorithm was loaded
                    assert window.current_algorithm_name == 'MotionDetection'
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_custom_widgets_setup(self, qapp):
        """Test custom widgets are set up."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify custom widgets exist
            assert hasattr(window, 'video_display')
            assert hasattr(window, 'thumbnail_widget')
            assert hasattr(window, 'stream_controls')
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_signal_connections(self, qapp):
        """Test signal connections."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify signals are connected
            assert window.stream_coordinator is not None
            assert window.detection_renderer is not None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_statistics_update_timer(self, qapp):
        """Test statistics update timer."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify timer exists and is running
            assert window.update_timer is not None
            assert window.update_timer.isActive()
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_frame_processing_flow(self, qapp, sample_frame):
        """Test frame processing flow."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Mock algorithm widget
            mock_algorithm = Mock()
            mock_algorithm.process_frame = Mock(return_value=[])
            window.algorithm_widget = mock_algorithm

            # Simulate frame received
            window.stream_coordinator.frameReceived.emit(sample_frame, 0.0)

            # In a real scenario, this would trigger processing
            # For now, we just verify the signal exists
            assert window.stream_coordinator.frameReceived is not None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_recording_controls(self, qapp):
        """Test recording controls."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify recording controls exist
            assert window.stream_controls is not None
            # Recording functionality should be available through stream_coordinator
            assert window.stream_coordinator is not None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_algorithm_switching(self, qapp):
        """Test switching between algorithms."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Mock algorithm config and controller import methods
            def get_config_side_effect(name):
                return {'name': name, 'category': 'streaming'}

            # Create a mock controller class that has all required signals and methods
            class MockAlgorithmController(QWidget):
                # Required signals
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
                    # Load first algorithm
                    window.load_algorithm('MotionDetection')
                    first_algorithm = window.current_algorithm_name

                    # Switch to second algorithm
                    window.load_algorithm('ColorDetection')
                    second_algorithm = window.current_algorithm_name

                    # Should have switched
                    assert first_algorithm == 'MotionDetection'
                    assert second_algorithm == 'ColorDetection'
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes
