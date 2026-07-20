"""Unit tests for :class:`TelemetryFeedService` (plan §19.3)."""

from __future__ import annotations

import json
import os
import sys

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.TelemetryFeedService import (  # noqa: E402
    TELEMETRY_LABEL,
    TelemetryFeedService,
)


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _envelope_bytes(**overrides) -> bytes:
    """Produce a wire-format envelope matching ADIAT_Mobile's TelemetryEnvelope."""
    payload = {
        "captured_at_ms": 1737310912345,
        "aircraft_latitude": 30.2672,
        "aircraft_longitude": -97.7431,
        "aircraft_altitude_msl_m": 312.4,
        "aircraft_altitude_agl_m": 25.6,
        "aircraft_yaw_deg": 90.5,
        "battery_percent": 82,
        "horizontal_speed_ms": 4.3,
        "vertical_speed_ms": -0.5,
        "is_flying": True,
        "flight_mode": "Normal",
    }
    payload.update(overrides)
    return json.dumps(payload).encode("utf-8")


def test_handle_message_parses_envelope_and_emits(qapp) -> None:
    svc = TelemetryFeedService()
    received = []
    svc.telemetryReceived.connect(received.append)

    svc.handle_message(TELEMETRY_LABEL, _envelope_bytes())
    assert len(received) == 1
    env = received[0]
    assert env["aircraft_latitude"] == 30.2672
    assert env["battery_percent"] == 82
    assert env["flight_mode"] == "Normal"
    assert svc.last_envelope == env


def test_handle_message_ignores_other_labels(qapp) -> None:
    svc = TelemetryFeedService()
    received = []
    svc.telemetryReceived.connect(received.append)

    svc.handle_message("detections.meta", _envelope_bytes())
    svc.handle_message("detections.thumb", b"\xff\xd8\xff\xe0")
    assert received == []


def test_handle_message_emits_feed_error_on_bad_json(qapp) -> None:
    svc = TelemetryFeedService()
    errors = []
    svc.feedError.connect(errors.append)

    svc.handle_message(TELEMETRY_LABEL, b"this is not json {")
    assert errors
    assert "malformed telemetry" in errors[0]


def test_handle_message_emits_feed_error_on_non_object_payload(qapp) -> None:
    svc = TelemetryFeedService()
    errors = []
    svc.feedError.connect(errors.append)
    svc.handle_message(TELEMETRY_LABEL, b"[1, 2, 3]")
    assert errors


def test_envelope_with_null_fields_still_emits(qapp) -> None:
    """Every field except ``captured_at_ms`` is nullable on the publisher side."""
    svc = TelemetryFeedService()
    received = []
    svc.telemetryReceived.connect(received.append)
    sparse = json.dumps({"captured_at_ms": 1737310912345}).encode("utf-8")
    svc.handle_message(TELEMETRY_LABEL, sparse)
    assert len(received) == 1
    assert received[0]["captured_at_ms"] == 1737310912345
