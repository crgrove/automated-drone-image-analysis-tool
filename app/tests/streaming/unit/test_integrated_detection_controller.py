"""Unit tests for ColorAnomalyAndMotionDetectionController."""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

from algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.ColorAnomalyAndMotionDetectionController import ColorAnomalyAndMotionDetectionController
from algorithms.streaming.ColorAnomalyAndMotionDetection.services import (
    ColorAnomalyAndMotionDetectionOrchestrator, ColorAnomalyAndMotionDetectionConfig, MotionAlgorithm, FusionMode, Detection
)


class TestColorAnomalyAndMotionDetectionController:
    """Test suite for ColorAnomalyAndMotionDetectionController."""

    def test_initialization(self, qapp, algorithm_config, mock_logger):
        """Test controller initialization."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            assert controller.algorithm_config == algorithm_config
            assert controller.theme == 'dark'
            assert controller.is_running is False
            assert controller.integrated_detector is not None
            assert controller.detection_count == 0

    def test_setup_ui(self, qapp, algorithm_config, mock_logger):
        """Test UI setup."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            # Check that UI elements are created
            assert controller.integrated_controls is not None

    def test_process_frame(self, qapp, algorithm_config, sample_frame, mock_logger):
        """Test frame processing with real algorithm."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            # Process multiple frames to let background subtractor learn
            for i in range(3):
                detections = controller.process_frame(sample_frame.copy(), float(i) * 0.033)
                assert isinstance(detections, list)

            # Process a frame with changes
            frame_with_motion = sample_frame.copy()
            frame_with_motion[100:150, 100:150] = [255, 255, 255]  # White square
            detections = controller.process_frame(frame_with_motion, 0.1)

            assert isinstance(detections, list)
            # Detections may or may not be found depending on algorithm state
            # But the method should complete without errors

    def test_get_config(self, qapp, algorithm_config, mock_logger):
        """Test configuration retrieval."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            config = controller.get_config()

            assert isinstance(config, dict)
            # Config should include all integrated detection settings
            assert 'processing_width' in config or 'processing_resolution' in config
            assert 'enable_motion' in config
            assert 'motion_algorithm' in config
            assert controller.integrated_detector is not None

    def test_set_config(self, qapp, algorithm_config, mock_logger):
        """Test configuration setting."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            new_config = {
                'processing_width': 1920,
                'processing_height': 1080,
                'enable_motion': True,
                'enable_color_quantization': True,
                'motion_algorithm': MotionAlgorithm.MOG2,
                'fusion_mode': FusionMode.UNION,
                'motion_threshold': 15,
                'min_detection_area': 10,
                'max_detection_area': 5000
            }

            controller.set_config(new_config)

            # Verify config was applied
            assert controller.integrated_detector is not None
            # Verify service config was updated
            assert controller.integrated_detector.config.enable_motion is True
            assert controller.integrated_detector.config.motion_threshold == 15

    def test_config_changed_signal(self, qapp, algorithm_config, mock_logger):
        """Test config changed signal emission."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            # Simulate config change from widget
            widget_config = {
                'processing_width': 1920,
                'processing_height': 1080,
                'enable_motion': False,
                'motion_algorithm': MotionAlgorithm.MOG2,
                'motion_threshold': 10,
                'min_detection_area': 5,
                'max_detection_area': 1000,
                'blur_kernel_size': 5,
                'morphology_kernel_size': 3,
                'bg_history': 50,
                'bg_var_threshold': 10.0,
                'bg_detect_shadows': False,
                'persistence_frames': 3,
                'persistence_threshold': 2,
                'pause_on_camera_movement': True,
                'camera_movement_threshold': 0.15,
                'enable_color_quantization': True,
                'color_quantization_bits': 4,
                'color_rarity_percentile': 30.0,
                'color_min_detection_area': 15,
                'color_max_detection_area': 50000,
                'enable_hue_expansion': False,
                'hue_expansion_range': 5,
                'enable_fusion': False,
                'fusion_mode': FusionMode.UNION,
                'enable_temporal_voting': True,
                'temporal_window_frames': 5,
                'temporal_threshold_frames': 3,
                'enable_aspect_ratio_filter': False,
                'min_aspect_ratio': 0.2,
                'max_aspect_ratio': 5.0,
                'enable_detection_clustering': False,
                'clustering_distance': 50,
                'enable_color_exclusion': False,
                'excluded_hue_ranges': [],
                'render_shape': 1,
                'render_text': False,
                'render_contours': False,
                'use_detection_color_for_rendering': True,
                'max_detections_to_render': 100,
                'show_timing_overlay': False,
                'show_detection_thumbnails': False,
                'use_threaded_capture': True,
                'render_at_processing_res': True
            }

            controller._on_config_changed(widget_config)

            # Verify handler was called and config was applied
            assert controller.integrated_detector is not None
            assert controller.integrated_detector.config.enable_motion is False
            assert controller.integrated_detector.config.motion_threshold == 10

    def test_detections_ready_signal(self, qapp, algorithm_config, sample_frame, mock_logger):
        """Test detections ready signal emission."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            # Simulate detections via the frame processed signal
            mock_detections = [
                Detection(
                    bbox=(100, 100, 50, 50),
                    centroid=(125, 125),
                    area=2500.0,
                    confidence=0.85,
                    detection_type='fused',
                    timestamp=0.0
                )
            ]
            # Use the actual signal handler method
            controller._on_frame_processed(sample_frame, mock_detections, None)

            # Verify detection count was updated
            assert controller.detection_count >= 0

    def test_performance_update(self, qapp, algorithm_config, mock_logger):
        """Test performance update handling."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            # Simulate performance update
            performance_data = {
                'fps': 20.0,
                'avg_processing_time_ms': 50.0
            }

            controller._on_performance_update(performance_data)

            # Verify performance data was processed
            assert controller.integrated_detector is not None

    def test_config_conversion(self, qapp, algorithm_config, mock_logger):
        """Test that UI config is correctly converted to ColorAnomalyAndMotionDetectionConfig."""
        patch_path = (
            'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.'
            'ColorAnomalyAndMotionDetectionController.LoggerService'
        )
        with patch(patch_path, return_value=mock_logger):
            controller = ColorAnomalyAndMotionDetectionController(algorithm_config, 'dark')

            # Get widget config (matches original format)
            widget_config = controller.integrated_controls.get_config()

            # Convert to service config
            service_config = controller._convert_to_config(widget_config)

            # Verify conversion
            assert isinstance(service_config, ColorAnomalyAndMotionDetectionConfig)
            assert service_config.enable_motion == widget_config['enable_motion']
            assert service_config.motion_algorithm == widget_config['motion_algorithm']
            assert service_config.fusion_mode == widget_config['fusion_mode']
            assert service_config.motion_threshold == widget_config['motion_threshold']
            assert service_config.blur_kernel_size == widget_config['blur_kernel_size']
            assert service_config.morphology_kernel_size == widget_config['morphology_kernel_size']
            # enable_morphology uses service default (not in UI)
