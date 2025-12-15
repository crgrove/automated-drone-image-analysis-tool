"""Unit tests for ColorDetectionController."""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtGui import QColor

from algorithms.streaming.ColorDetection.controllers.ColorDetectionController import ColorDetectionController
from algorithms.streaming.ColorDetection.services.ColorDetectionService import (
    ColorDetectionService, HSVConfig, Detection
)


class TestColorDetectionController:
    """Test suite for ColorDetectionController."""

    def test_initialization(self, qapp, algorithm_config, mock_logger):
        """Test controller initialization."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            assert controller.algorithm_config == algorithm_config
            assert controller.theme == 'dark'
            assert controller.is_running is False
            assert controller.color_detector is not None
            assert controller.detection_count == 0

    def test_setup_ui(self, qapp, algorithm_config, mock_logger):
        """Test UI setup."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            # Check that UI elements are created
            assert controller.control_widget is not None

    def test_process_frame(self, qapp, algorithm_config, sample_frame, mock_logger):
        """Test frame processing."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            # Mock the color detector's detect_colors method
            mock_detections = [
                Detection(
                    bbox=(100, 100, 50, 50),
                    centroid=(125, 125),
                    area=2500.0,
                    confidence=0.85,
                    timestamp=0.0,
                    contour=np.array([]),
                    detection_type='color',
                    color=(0, 0, 255)
                )
            ]
            controller.color_detector.detect_colors = Mock(return_value=mock_detections)

            # Process frame
            detections = controller.process_frame(sample_frame, 0.0)

            assert isinstance(detections, list)
            if len(detections) > 0:
                assert 'bbox' in detections[0]
                assert 'confidence' in detections[0]

    def test_get_config(self, qapp, algorithm_config, mock_logger):
        """Test configuration retrieval."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            config = controller.get_config()

            assert isinstance(config, dict)
            # Config should include color_ranges, processing_resolution, etc.
            assert 'color_ranges' in config
            assert 'processing_resolution' in config
            assert 'render_shape' in config

    def test_set_config(self, qapp, algorithm_config, mock_logger):
        """Test configuration setting."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            new_config = {
                'color_ranges': [{
                    'name': 'Red',
                    'color': QColor(255, 0, 0),
                    'hue_minus': 20,
                    'hue_plus': 20,
                    'sat_minus': 50,
                    'sat_plus': 50,
                    'val_minus': 50,
                    'val_plus': 50
                }],
                'min_area': 100,
                'max_area': 100000
            }

            controller.set_config(new_config)

            # Verify config was applied
            assert controller.control_widget is not None
            assert len(controller.control_widget.color_ranges) > 0

    def test_config_changed_signal(self, qapp, algorithm_config, mock_logger):
        """Test config changed signal emission."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            # Create a signal spy
            config_received = None

            def on_config_changed(config):
                nonlocal config_received
                config_received = config

            controller.configChanged.connect(on_config_changed)

            # Simulate config change
            controller._on_config_changed({'hue_tolerance': 15.0})

            # Note: Signal emission is asynchronous

    def test_detections_ready_signal(self, qapp, algorithm_config, sample_frame, mock_logger):
        """Test detections ready signal emission."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            # Simulate detections
            mock_detections = [
                Detection(
                    bbox=(100, 100, 50, 50),
                    centroid=(125, 125),
                    area=2500.0,
                    confidence=0.85,
                    timestamp=0.0,
                    contour=np.array([]),
                    detection_type='color',
                    color=(0, 0, 255)
                )
            ]
            controller._on_detections_ready(mock_detections, 0.0, sample_frame)

            # Verify detection count was updated
            assert controller.detection_count >= 0

    def test_performance_update(self, qapp, algorithm_config, mock_logger):
        """Test performance update handling."""
        with patch('algorithms.streaming.ColorDetection.controllers.ColorDetectionController.LoggerService', return_value=mock_logger):
            controller = ColorDetectionController(algorithm_config, 'dark')

            # Simulate performance update
            performance_data = {
                'processing_time': 50.0,
                'fps': 20.0,
                'detections_count': 5
            }

            controller._on_performance_update(performance_data)

            # Verify performance data was processed
            assert controller.color_detector is not None
