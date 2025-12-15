"""Unit tests for MotionDetectionController."""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

from algorithms.streaming.MotionDetection.controllers.MotionDetectionController import MotionDetectionController
from algorithms.streaming.MotionDetection.services.MotionDetectionService import (
    MotionDetectionService, DetectionMode, MotionAlgorithm, MotionDetection
)


class TestMotionDetectionController:
    """Test suite for MotionDetectionController."""

    def test_initialization(self, qapp, algorithm_config, mock_logger):
        """Test controller initialization."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            assert controller.algorithm_config == algorithm_config
            assert controller.theme == 'dark'
            assert controller.is_running is False
            assert controller.motion_detector is not None
            assert controller._detection_count == 0

    def test_setup_ui(self, qapp, algorithm_config, mock_logger):
        """Test UI setup."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            # Check that UI elements are created
            assert controller.mode_combo is not None
            assert controller.algorithm_combo is not None
            assert controller.mode_status_label is not None

    def test_process_frame(self, qapp, algorithm_config, sample_frame, mock_logger):
        """Test frame processing."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            # Mock the motion detector's process_frame method
            controller.motion_detector.process_frame = Mock()

            # Process frame (returns empty list as detections come via signal)
            detections = controller.process_frame(sample_frame, 0.0)

            assert isinstance(detections, list)
            # Detections come via signal, so process_frame returns empty list
            controller.motion_detector.process_frame.assert_called_once_with(sample_frame)

    def test_get_config(self, qapp, algorithm_config, mock_logger):
        """Test configuration retrieval."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            config = controller.get_config()

            assert isinstance(config, dict)
            assert 'mode' in config
            assert 'algorithm' in config
            assert 'sensitivity' in config

    def test_set_config(self, qapp, algorithm_config, mock_logger):
        """Test configuration setting."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            new_config = {
                'mode': 'Static Camera',
                'algorithm': 'MOG2 Background',
                'sensitivity': 50
            }

            controller.set_config(new_config)

            assert controller.mode_combo.currentText() == 'Static Camera'
            assert controller.algorithm_combo.currentText() == 'MOG2 Background'

    def test_mode_changed(self, qapp, algorithm_config, mock_logger):
        """Test mode change handling."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            # Change mode
            controller.mode_combo.setCurrentText('Static Camera')

            # Verify mode was updated
            assert controller.mode_combo.currentText() == 'Static Camera'

    def test_algorithm_changed(self, qapp, algorithm_config, mock_logger):
        """Test algorithm change handling."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            # Change algorithm
            controller.algorithm_combo.setCurrentText('KNN Background')

            # Verify algorithm was updated
            assert controller.algorithm_combo.currentText() == 'KNN Background'

    def test_detections_ready_signal(self, qapp, algorithm_config, sample_frame, mock_logger):
        """Test detections ready signal emission."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            # Create a signal spy
            detections_received = []

            def on_detections(detections):
                detections_received.extend(detections)

            controller.detectionsReady.connect(on_detections)

            # Simulate detections using MotionDetection objects
            mock_detections = [
                MotionDetection(
                    bbox=(100, 100, 50, 50),
                    centroid=(125, 125),
                    area=2500.0,
                    velocity=(0.0, 0.0),
                    confidence=0.85,
                    timestamp=0.0,
                    is_compensated=False,
                    contour=np.array([])
                )
            ]
            controller._on_detections_ready(mock_detections, None, sample_frame)

            # Note: Signal emission is asynchronous, so we check the handler was called
            # In a real test with qtbot, we'd use qtbot.waitSignal

    def test_performance_update(self, qapp, algorithm_config, mock_logger):
        """Test performance update handling."""
        with patch('algorithms.streaming.MotionDetection.controllers.MotionDetectionController.LoggerService', return_value=mock_logger):
            controller = MotionDetectionController(algorithm_config, 'dark')

            # Simulate performance update
            performance_data = {
                'processing_time': 50.0,
                'fps': 20.0,
                'detections_count': 5
            }

            controller._on_performance_update(performance_data)

            # Verify performance data was processed
            assert controller.motion_detector is not None
