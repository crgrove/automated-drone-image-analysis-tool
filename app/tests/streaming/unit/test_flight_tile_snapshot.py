"""Unit tests for FlightTileController's snapshot wire-up (plan §18 item 2).

The DataChannel snapshot reply (which arrives after an ICE-restart
recovery) should fan out as individual ``detectionPromoted`` events on
the per-tile + gallery path, with ``thumb_bytes=None`` and idempotent
dedup by ``track_key``.
"""

from __future__ import annotations

import os
import sys
from typing import List

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.controllers.flight import FlightTileController  # noqa: E402
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _make_controller():
    controller = FlightTileController(signaling=InMemorySignalingChannel())
    controller._pairing_code = "ABC234"
    return controller


def test_snapshot_routes_through_promoted_path_with_no_thumb(qapp):
    controller = _make_controller()
    promotions: List[dict] = []
    controller.detectionPromoted.connect(lambda _code, det: promotions.append(det))

    controller._on_detection_snapshot([
        {"track_key": "person|sess|1", "class_name": "person", "confidence": 0.9},
        {"track_key": "person|sess|2", "class_name": "person", "confidence": 0.7},
    ])

    assert len(promotions) == 2
    assert all(det["thumb_bytes"] is None for det in promotions)
    assert {det["track_key"] for det in promotions} == {"person|sess|1", "person|sess|2"}


def test_snapshot_skips_already_known_track_keys(qapp):
    controller = _make_controller()
    promotions: List[dict] = []
    controller.detectionPromoted.connect(lambda _code, det: promotions.append(det))

    # Simulate a live promote arriving first.
    controller._on_detection_promoted({
        "track_key": "person|sess|1",
        "class_name": "person",
        "confidence": 0.91,
        "thumb_bytes": b"\xFFreal-thumb",
    })
    assert len(promotions) == 1

    # Snapshot reply arrives later — should NOT re-emit the known track.
    controller._on_detection_snapshot([
        {"track_key": "person|sess|1", "class_name": "person", "confidence": 0.91},
        {"track_key": "person|sess|2", "class_name": "person", "confidence": 0.55},
    ])

    assert len(promotions) == 2
    # The second event is the previously-unknown track #2.
    assert promotions[1]["track_key"] == "person|sess|2"


def test_snapshot_without_track_key_still_fires(qapp):
    """A snapshot entry missing ``track_key`` cannot dedupe — emit it anyway."""
    controller = _make_controller()
    promotions: List[dict] = []
    controller.detectionPromoted.connect(lambda _code, det: promotions.append(det))

    controller._on_detection_snapshot([
        {"class_name": "vehicle", "confidence": 0.6},
        {"class_name": "vehicle", "confidence": 0.6},  # would be a dup if we had track_keys
    ])

    assert len(promotions) == 2


def test_snapshot_skips_non_dict_entries(qapp):
    controller = _make_controller()
    promotions: List[dict] = []
    controller.detectionPromoted.connect(lambda _code, det: promotions.append(det))

    controller._on_detection_snapshot([
        {"track_key": "x|y|1", "class_name": "person"},
        "not-a-dict",
        None,
        42,
    ])
    assert len(promotions) == 1


def test_known_track_keys_clear_on_tear_down(qapp):
    controller = _make_controller()
    controller._on_detection_promoted({"track_key": "x|y|1", "class_name": "person"})
    assert "x|y|1" in controller._known_track_keys

    controller.tear_down()
    assert controller._known_track_keys == set()
