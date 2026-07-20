"""Unit tests for streaming service adapters."""

from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QObject

from core.services.streaming.StreamingUtils import StageTimings
from core.services.streaming.adapters import (
    AIPersonStreamAdapter,
    ColorAnomalyMotionStreamAdapter,
    ColorDetectionStreamAdapter,
)


@dataclass
class FakeAIPersonConfig:
    confidence_threshold: float = 0.5
    cpu_only: bool = False
    max_detections: int = 25


class FakeAIPersonService(QObject):
    """Minimal AIPerson-compatible service for adapter tests."""

    def __init__(self):
        super().__init__(None)
        self._config = FakeAIPersonConfig()
        self.reset_called = False
        self.cleanup_called = False

    def get_config(self):
        return FakeAIPersonConfig(**self._config.__dict__)

    def update_config(self, config):
        self._config = config

    def process_frame(self, frame, timestamp):
        detection = SimpleNamespace(
            bbox=(10, 20, 30, 40),
            centroid=(25, 40),
            area=1200.0,
            confidence=0.92,
            timestamp=timestamp,
            detection_type="person",
            metadata={"source": "fake_ai"},
        )
        return frame.copy(), [detection], StageTimings(total_ms=3.0)

    def reset(self):
        self.reset_called = True

    def cleanup(self):
        self.cleanup_called = True


@dataclass
class FakeColorConfig:
    min_area: int = 100
    max_area: int = 10000
    render_shape: int = 0


class FakeColorService(QObject):
    """Minimal ColorDetection-compatible service for adapter tests."""

    def __init__(self):
        super().__init__(None)
        self._current_config = FakeColorConfig()
        self.reset_called = False
        self.cleanup_called = False

    def update_config(self, config):
        self._current_config = config

    def get_config(self):
        return FakeColorConfig(**self._current_config.__dict__)

    def detect_colors(self, frame, timestamp):
        return [
            SimpleNamespace(
                bbox=(1, 2, 3, 4),
                centroid=(2, 4),
                area=12.0,
                confidence=0.8,
                timestamp=timestamp,
                detection_type="color",
                metadata={"foo": "bar"},
                color_id=3,
                mean_color=(10, 20, 30),
            )
        ]

    def create_annotated_frame(self, frame, detections):
        _ = detections
        return frame.copy()

    def reset(self):
        self.reset_called = True

    def cleanup(self):
        self.cleanup_called = True


@dataclass
class FakeIntegratedConfig:
    processing_width: int = 640
    processing_height: int = 480
    target_fps: int = 0


class FakeIntegratedService(QObject):
    """Minimal integrated-orchestrator-compatible service for adapter tests."""

    def __init__(self):
        super().__init__(None)
        self.config = FakeIntegratedConfig()
        self.reset_called = False
        self.cleanup_called = False

    def update_config(self, config):
        self.config = config

    def process_frame(self, frame, timestamp):
        detection = SimpleNamespace(
            bbox=(5, 6, 7, 8),
            centroid=(8, 10),
            area=56.0,
            confidence=0.66,
            timestamp=timestamp,
            detection_type="motion",
            metadata={"mode": "fake"},
        )
        return frame.copy(), [detection], StageTimings(total_ms=4.0)

    def reset(self):
        self.reset_called = True

    def cleanup(self):
        self.cleanup_called = True


def test_ai_person_adapter_merges_config_and_normalizes_output():
    """AIPerson adapter should merge config updates and normalize detections."""
    service = FakeAIPersonService()
    adapter = AIPersonStreamAdapter(service)

    assert service.parent() is adapter

    adapter.update_config({"cpu_only": True})
    cfg = adapter.get_config()
    assert cfg["cpu_only"] is True
    assert cfg["confidence_threshold"] == 0.5

    result = adapter.process_frame(np.zeros((10, 10, 3), dtype=np.uint8), 1.5)
    assert len(result.detections) == 1
    assert result.detections[0].class_name == "Person"
    assert result.detections[0].metadata["source"] == "fake_ai"
    assert result.detections[0].metadata["render_shape"] == 0
    assert result.detections[0].metadata["original_resolution"] == (10, 10)
    assert "processing_resolution" not in result.detections[0].metadata

    adapter.reset()
    adapter.cleanup()
    assert service.reset_called is True
    assert service.cleanup_called is True


def test_adapter_logs_warning_when_service_already_has_parent():
    """Adapters should warn instead of silently changing existing Qt ownership."""
    existing_parent = QObject()
    service = FakeAIPersonService()
    service.setParent(existing_parent)

    with patch("core.services.streaming.adapters.LoggerService") as logger_cls:
        adapter = AIPersonStreamAdapter(service)

    assert service.parent() is existing_parent
    assert adapter.parent() is None
    logger_cls.return_value.warning.assert_called_once()
    warning_message = logger_cls.return_value.warning.call_args[0][0]
    assert "existing parent" in warning_message
    assert "FakeAIPersonService" in warning_message


def test_color_detection_adapter_merges_config_and_normalizes_output():
    """Color adapter should merge config updates and carry color metadata."""
    service = FakeColorService()
    adapter = ColorDetectionStreamAdapter(service)

    assert service.parent() is adapter

    adapter.update_config({"min_area": 250})
    cfg = adapter.get_config()
    assert cfg["min_area"] == 250
    assert cfg["max_area"] == 10000

    result = adapter.process_frame(np.zeros((8, 8, 3), dtype=np.uint8), 2.0)
    assert len(result.detections) == 1
    assert result.detections[0].class_name == "Color_3"
    assert result.detections[0].metadata["color_id"] == 3
    assert result.detections[0].metadata["mean_color"] == (10, 20, 30)
    assert result.detections[0].metadata["render_shape"] == 0
    assert result.detections[0].metadata["original_resolution"] == (8, 8)

    adapter.reset()
    adapter.cleanup()
    assert service.reset_called is True
    assert service.cleanup_called is True


def test_color_anomaly_motion_adapter_merges_config_and_normalizes_output():
    """Integrated adapter should merge config updates and normalize detections."""
    service = FakeIntegratedService()
    adapter = ColorAnomalyMotionStreamAdapter(service)

    assert service.parent() is adapter

    adapter.update_config({"target_fps": 12})
    cfg = adapter.get_config()
    assert cfg["target_fps"] == 12
    assert cfg["processing_width"] == 640

    result = adapter.process_frame(np.zeros((8, 8, 3), dtype=np.uint8), 0.25)
    assert len(result.detections) == 1
    assert result.detections[0].class_name == "motion"
    assert result.detections[0].detection_type == "motion"
    assert result.timings.total_ms == 4.0
    assert result.detections[0].metadata["render_shape"] == 0

    adapter.reset()
    adapter.cleanup()
    assert service.reset_called is True
    assert service.cleanup_called is True
