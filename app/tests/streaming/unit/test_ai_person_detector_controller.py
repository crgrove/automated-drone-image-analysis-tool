"""Unit tests for streaming AI person detector controller."""

import numpy as np
from unittest.mock import Mock, patch

from core.services.streaming.StreamingUtils import StageTimings
from algorithms.streaming.AIPersonDetector.services import AIPersonDetection
from algorithms.streaming.AIPersonDetector.controllers.AIPersonDetectorController import (
    AIPersonDetectorController,
)


class TestAIPersonDetectorController:
    """Test suite for AIPersonDetectorController."""

    def test_initialization(self, qapp, algorithm_config, mock_logger):
        """Controller should initialize and create service/control widget."""
        with patch(
            "algorithms.streaming.AIPersonDetector.controllers.AIPersonDetectorController.LoggerService",
            return_value=mock_logger,
        ):
            controller = AIPersonDetectorController(algorithm_config, "dark")

        assert controller.algorithm_config == algorithm_config
        assert controller.theme == "dark"
        assert controller.control_widget is not None
        assert controller.person_detector is not None
        assert controller.provides_custom_rendering is False

    def test_process_frame_emits_detection_dicts(self, qapp, algorithm_config, sample_frame, mock_logger):
        """Controller should convert service detections into stream viewer format."""
        with patch(
            "algorithms.streaming.AIPersonDetector.controllers.AIPersonDetectorController.LoggerService",
            return_value=mock_logger,
        ):
            controller = AIPersonDetectorController(algorithm_config, "dark")

        detection = AIPersonDetection(
            bbox=(10, 20, 30, 40),
            centroid=(25, 40),
            area=1200.0,
            confidence=0.88,
            timestamp=0.5,
            detection_type="person",
            metadata={"model": "onnx_ai_person"},
        )
        controller.person_detector.process_frame = Mock(
            return_value=(sample_frame.copy(), [detection], StageTimings(total_ms=1.0))
        )

        detections = controller.process_frame(sample_frame, 0.5)

        assert len(detections) == 1
        assert detections[0]["bbox"] == (10, 20, 30, 40)
        assert detections[0]["class_name"] == "Person"
        assert detections[0]["detection_type"] == "person"

    def test_set_config_updates_widget_and_service(self, qapp, algorithm_config, mock_logger):
        """Setting config should propagate to widget and service."""
        with patch(
            "algorithms.streaming.AIPersonDetector.controllers.AIPersonDetectorController.LoggerService",
            return_value=mock_logger,
        ):
            controller = AIPersonDetectorController(algorithm_config, "dark")

        controller.person_detector.update_config = Mock()
        config = {
            "person_detector_confidence": 70,
            "cpu_only": True,
            "high_resolution_model": True,
            "show_labels": False,
            "max_detections": 5,
            "target_fps": 15,
        }
        controller.set_config(config)
        widget_cfg = controller.get_config()

        assert widget_cfg["person_detector_confidence"] == 70
        assert widget_cfg["cpu_only"] is True
        assert widget_cfg["high_resolution_model"] is True
        assert widget_cfg["show_labels"] is False
        assert widget_cfg["max_detections"] == 5
        assert widget_cfg["target_fps"] == 15
        assert controller.person_detector.update_config.call_count >= 1

    def test_file_source_auto_selects_high_resolution_model(self, qapp, algorithm_config, mock_logger):
        """File sources on GPU auto-engage the 1024 model; live feeds and CPU stay 640.
        processing_width is set (not None) so only stream_type drives the choice here."""
        with patch(
            "algorithms.streaming.AIPersonDetector.controllers.AIPersonDetectorController.LoggerService",
            return_value=mock_logger,
        ):
            controller = AIPersonDetectorController(algorithm_config, "dark")

        base = {"cpu_only": False, "processing_width": 1280, "processing_height": 720}

        # File source on GPU -> 1024 (via persisted self._stream_type)
        controller._stream_type = "File"
        assert controller._to_service_config(base).high_resolution_model is True

        # Live source on GPU -> 640
        controller._stream_type = "RTMP Stream"
        assert controller._to_service_config(base).high_resolution_model is False

        # File source on CPU -> 640 (CPU runs the 640 export)
        controller._stream_type = "File"
        assert controller._to_service_config({**base, "cpu_only": True}).high_resolution_model is False

        # stream_type carried directly in the config dict also works (no persisted value)
        controller._stream_type = None
        assert controller._to_service_config({**base, "stream_type": "File"}).high_resolution_model is True

    def test_set_config_captures_stream_type_without_leaking_to_widget(self, qapp, algorithm_config, mock_logger):
        """set_config should persist stream_type for model selection and not pass it to the widget."""
        with patch(
            "algorithms.streaming.AIPersonDetector.controllers.AIPersonDetectorController.LoggerService",
            return_value=mock_logger,
        ):
            controller = AIPersonDetectorController(algorithm_config, "dark")
        controller.person_detector.update_config = Mock()

        controller.set_config({"stream_type": "File", "cpu_only": False, "person_detector_confidence": 50})

        assert controller._stream_type == "File"
        assert "stream_type" not in controller.get_config()

    def test_capabilities_hide_unsupported_shared_controls(self, qapp, algorithm_config, mock_logger):
        """AIPerson should explicitly disable unsupported shared rendering controls."""
        with patch(
            "algorithms.streaming.AIPersonDetector.controllers.AIPersonDetectorController.LoggerService",
            return_value=mock_logger,
        ):
            controller = AIPersonDetectorController(algorithm_config, "dark")

        capabilities = controller.get_stream_capabilities()

        assert capabilities.supports_mask_controls is True
        assert capabilities.supports_render_at_processing_resolution is False
        assert capabilities.supports_render_contours is False
        assert capabilities.supports_use_detection_color is False
        assert capabilities.supports_detection_clustering is False
