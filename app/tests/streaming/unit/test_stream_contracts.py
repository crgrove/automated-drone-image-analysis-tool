"""Unit tests for streaming contracts."""

from core.services.streaming.StreamingUtils import StageTimings
from core.services.streaming.contracts import StreamDetection, StreamProcessResult


def test_stream_detection_to_dict_includes_optional_fields():
    """to_dict should include optional fields when provided."""
    detection = StreamDetection(
        bbox=(10, 20, 30, 40),
        confidence=0.9,
        class_name="Person",
        centroid=(25, 40),
        area=1200.0,
        detection_type="person",
        timestamp=1.23,
        metadata={"model": "onnx"},
    )

    payload = detection.to_dict()

    assert payload["bbox"] == (10, 20, 30, 40)
    assert payload["confidence"] == 0.9
    assert payload["class_name"] == "Person"
    assert payload["centroid"] == (25, 40)
    assert payload["area"] == 1200.0
    assert payload["detection_type"] == "person"
    assert payload["timestamp"] == 1.23
    assert payload["metadata"] == {"model": "onnx"}


def test_stream_detection_to_dict_omits_missing_optional_fields():
    """to_dict should omit optional fields when not provided."""
    detection = StreamDetection(
        bbox=(1, 2, 3, 4),
        confidence=0.4,
        class_name="Detection",
    )

    payload = detection.to_dict()

    assert "centroid" not in payload
    assert "area" not in payload


def test_stream_process_result_reports_was_skipped():
    """was_skipped should reflect timings.was_skipped."""
    timings = StageTimings(was_skipped=True)
    result = StreamProcessResult(timings=timings)

    assert result.was_skipped is True


def test_stream_process_result_detection_dicts_maps_detections():
    """detection_dicts should convert all detection objects."""
    detections = [
        StreamDetection(bbox=(1, 1, 10, 10), confidence=0.7, class_name="A"),
        StreamDetection(bbox=(2, 2, 20, 20), confidence=0.8, class_name="B"),
    ]
    result = StreamProcessResult(detections=detections)

    payloads = result.detection_dicts()

    assert len(payloads) == 2
    assert payloads[0]["class_name"] == "A"
    assert payloads[1]["class_name"] == "B"
