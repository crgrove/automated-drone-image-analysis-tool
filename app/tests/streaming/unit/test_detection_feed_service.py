"""Unit tests for :class:`DetectionFeedService` (plan §12)."""

from __future__ import annotations

import hashlib
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.services.streaming.DetectionFeedService import (  # noqa: E402
    META_LABEL,
    SNAPSHOT_LABEL,
    THUMB_LABEL,
    DetectionFeedService,
)


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _envelope(sha256: str | None, *, track_key: str = "person|sess|1", confidence: float = 0.87) -> bytes:
    body = {
        "event": "promote",
        "track_key": track_key,
        "detector_id": "person",
        "class_name": "person",
        "confidence": confidence,
        "captured_at_ms": 1737310912345,
        "location": {"lat": 30.2672, "lon": -97.7431},
    }
    if sha256 is not None:
        body["thumb"] = {"channel": THUMB_LABEL, "bytes": 4, "sha256": sha256}
    return json.dumps(body).encode("utf-8")


def test_meta_only_promotion_surfaces_with_thumb_none(qapp) -> None:
    svc = DetectionFeedService()
    promotions = []
    svc.detectionPromoted.connect(lambda d: promotions.append(d))

    svc.handle_message(META_LABEL, _envelope(sha256=None))
    assert len(promotions) == 1
    assert promotions[0]["thumb_bytes"] is None
    assert promotions[0]["class_name"] == "person"


def test_meta_then_thumb_pair_emits_combined_event(qapp) -> None:
    svc = DetectionFeedService()
    promotions = []
    svc.detectionPromoted.connect(lambda d: promotions.append(d))

    thumb_bytes = b"\xFF\xD8\xFF\xE0"
    sha = hashlib.sha256(thumb_bytes).hexdigest()
    svc.handle_message(META_LABEL, _envelope(sha256=sha))
    assert promotions == []  # buffered awaiting thumb

    svc.handle_message(THUMB_LABEL, thumb_bytes)
    assert len(promotions) == 1
    assert promotions[0]["thumb_bytes"] == thumb_bytes


def test_thumb_before_meta_is_buffered_and_matched(qapp) -> None:
    svc = DetectionFeedService()
    promotions = []
    svc.detectionPromoted.connect(lambda d: promotions.append(d))

    thumb_bytes = b"\xFF\xD8\xFF\xE1"
    sha = hashlib.sha256(thumb_bytes).hexdigest()
    svc.handle_message(THUMB_LABEL, thumb_bytes)
    assert promotions == []
    svc.handle_message(META_LABEL, _envelope(sha256=sha))
    assert len(promotions) == 1
    assert promotions[0]["thumb_bytes"] == thumb_bytes


def test_malformed_envelope_emits_feed_error_without_crash(qapp) -> None:
    svc = DetectionFeedService()
    errors = []
    svc.feedError.connect(lambda msg: errors.append(msg))
    svc.handle_message(META_LABEL, b"not-json{{{{")
    assert errors, "feedError should fire on malformed JSON"
    # Service should remain usable afterwards
    svc.handle_message(META_LABEL, _envelope(sha256=None))


def test_byte_count_mismatch_drops_row_and_emits_feed_error(qapp) -> None:
    svc = DetectionFeedService()
    promotions = []
    errors = []
    svc.detectionPromoted.connect(lambda d: promotions.append(d))
    svc.feedError.connect(lambda msg: errors.append(msg))

    thumb_bytes = b"\x00\x01\x02\x03"
    sha = hashlib.sha256(thumb_bytes).hexdigest()
    # Envelope declares bytes=99 but thumb arrives as 4 bytes.
    envelope = json.dumps(
        {
            "event": "promote",
            "track_key": "x",
            "thumb": {"channel": THUMB_LABEL, "bytes": 99, "sha256": sha},
        }
    ).encode("utf-8")
    svc.handle_message(META_LABEL, envelope)
    svc.handle_message(THUMB_LABEL, thumb_bytes)
    assert not promotions
    assert errors


def test_snapshot_channel_emits_bulk_list(qapp) -> None:
    svc = DetectionFeedService()
    snapshots = []
    svc.detectionSnapshot.connect(lambda items: snapshots.append(items))
    payload = json.dumps(
        [
            {"event": "promote", "class_name": "person"},
            {"event": "promote", "class_name": "vehicle"},
        ]
    ).encode("utf-8")
    svc.handle_message(SNAPSHOT_LABEL, payload)
    assert len(snapshots) == 1
    assert len(snapshots[0]) == 2


def test_update_event_routes_to_update_signal(qapp) -> None:
    svc = DetectionFeedService()
    promoted = []
    updated = []
    svc.detectionPromoted.connect(lambda d: promoted.append(d))
    svc.detectionUpdated.connect(lambda d: updated.append(d))
    payload = _envelope(sha256=None)
    payload_obj = json.loads(payload.decode("utf-8"))
    payload_obj["event"] = "update"
    svc.handle_message(META_LABEL, json.dumps(payload_obj).encode("utf-8"))
    assert promoted == []
    assert len(updated) == 1
