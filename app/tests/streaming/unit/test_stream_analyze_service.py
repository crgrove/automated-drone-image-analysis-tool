"""Unit tests for StreamAnalyzeService."""

import numpy as np

from core.services.streaming.StreamAlgorithmService import StreamAlgorithmService
from core.services.streaming.StreamAnalyzeService import StreamAnalyzeService
from core.services.streaming.StreamingUtils import StageTimings
from core.services.streaming.contracts import StreamDetection, StreamProcessResult


class FakeLogger:
    """Simple logger stub for verifying analyzer diagnostics."""

    def __init__(self):
        self.errors = []

    def error(self, message):
        self.errors.append(message)


class DummyStreamService(StreamAlgorithmService):
    """Minimal test service with configurable process behavior."""

    def __init__(self, behavior):
        super().__init__()
        self._behavior = behavior

    def update_config(self, config):
        return None

    def get_config(self):
        return {}

    def process_frame(self, frame, timestamp):
        return self._behavior(frame, timestamp)

    def reset(self):
        return None

    def cleanup(self):
        return None


def test_process_frame_passthrough_stream_process_result():
    """Analyzer should pass through already normalized results."""
    expected = StreamProcessResult(
        detections=[StreamDetection(bbox=(1, 2, 3, 4), confidence=0.5, class_name="X")],
        timings=StageTimings(total_ms=1.0),
    )
    analyzer = StreamAnalyzeService(DummyStreamService(lambda _f, _t: expected))

    result = analyzer.process_frame(np.zeros((8, 8, 3), dtype=np.uint8), 0.5)

    assert result is expected


def test_process_frame_normalizes_legacy_tuple_result():
    """Analyzer should normalize tuple-style legacy outputs."""
    frame = np.zeros((16, 16, 3), dtype=np.uint8)
    annotated = frame.copy()
    timings = StageTimings(total_ms=2.0, was_skipped=True)
    detections = [{"bbox": (10, 10, 5, 5), "confidence": 0.9, "detection_type": "person"}]
    analyzer = StreamAnalyzeService(DummyStreamService(lambda _f, _t: (annotated, detections, timings)))

    result = analyzer.process_frame(frame, 1.0)

    assert result.rendered_frame is annotated
    assert result.timings.was_skipped is True
    assert result.detections[0].class_name == "person"
    worker_payload, skipped = analyzer.to_worker_output(result)
    assert skipped is True
    assert worker_payload[0]["detection_type"] == "person"


def test_process_frame_normalizes_detection_list_result():
    """Analyzer should normalize list-only detection results."""
    frame = np.zeros((12, 12, 3), dtype=np.uint8)
    detections = [{"bbox": (2, 2, 4, 4), "confidence": 0.8, "class_name": "Color_0"}]
    analyzer = StreamAnalyzeService(DummyStreamService(lambda _f, _t: detections))

    result = analyzer.process_frame(frame, 2.0)

    assert result.rendered_frame is frame
    assert result.timings.total_ms == 0.0
    assert len(result.detections) == 1
    assert result.detections[0].class_name == "Color_0"


def test_process_frame_reports_unsupported_result_type():
    """Analyzer should flag unsupported result types instead of crashing."""
    logger = FakeLogger()
    analyzer = StreamAnalyzeService(DummyStreamService(lambda _f, _t: "invalid"), logger=logger)

    result = analyzer.process_frame(np.zeros((4, 4, 3), dtype=np.uint8), 0.0)

    assert result.error_message == "Unsupported stream processing result type: str"
    assert result.detections == []
    assert logger.errors == [
        "Unsupported stream processing result from DummyStreamService: type=str"
    ]


def test_process_frame_reports_unsupported_tuple_length():
    """Analyzer should report tuple length when legacy tuple shape is invalid."""
    logger = FakeLogger()
    analyzer = StreamAnalyzeService(
        DummyStreamService(lambda _f, _t: ("frame", [])),
        logger=logger,
    )

    result = analyzer.process_frame(np.zeros((4, 4, 3), dtype=np.uint8), 0.0)

    assert result.error_message == "Unsupported stream processing result tuple length: 2"
    assert result.detections == []
    assert logger.errors == [
        "Unsupported stream processing tuple result from DummyStreamService: type=tuple length=2"
    ]


def test_process_frame_handles_service_exceptions():
    """Analyzer should convert service exceptions into error results."""

    def raise_error(_f, _t):
        raise RuntimeError("processing failed")

    frame = np.ones((6, 6, 3), dtype=np.uint8)
    analyzer = StreamAnalyzeService(DummyStreamService(raise_error))

    result = analyzer.process_frame(frame, 0.0)

    assert result.error_message == "processing failed"
    assert result.rendered_frame is not frame
    assert np.array_equal(result.rendered_frame, frame)
