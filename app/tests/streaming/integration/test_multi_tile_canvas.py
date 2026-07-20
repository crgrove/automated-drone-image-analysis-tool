"""Integration tests for the multi-tile canvas (plan §12).

Verifies that multiple tiles can be added and removed independently and
that the Mission Gallery merges detections from active feeds in
monotonic timestamp order while excluding closed/muted feeds.
"""

from __future__ import annotations

import os
import sys
from typing import List
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import core.controllers.flight.FlightTileController  # noqa: E402,F401
ftc_module = sys.modules["core.controllers.flight.FlightTileController"]

from core.controllers.flight import FlightViewerController  # noqa: E402
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402


class StubWebRTCService(QObject):
    """Same shape as the lifecycle test's stub."""

    frameReady = Signal(object, float, int)
    connectionStatusChanged = Signal(bool, str)
    streamStatsChanged = Signal(dict)
    errorOccurred = Signal(str)
    iceStateChanged = Signal(str)
    peerFingerprintReceived = Signal(str)
    sasReady = Signal(list)
    dataChannelOpened = Signal(str)
    dataChannelMessage = Signal(str, bytes)
    capReached = Signal(int, int)
    snapshotRequested = Signal()

    def __init__(self, *_a, **_k):
        super().__init__()

    def request_connect(self):
        pass

    def confirm_sas(self, _accept):
        pass

    def request_disconnect(self):
        pass

    def reset(self):
        pass

    def cleanup(self):
        pass


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def stub_service(monkeypatch):
    monkeypatch.setattr(ftc_module, "WebRTCStreamService", StubWebRTCService)


def _add_tile(viewer: FlightViewerController, code: str, qtbot) -> object:
    viewer.open_pairing_dialog()
    tile_controller, dialog = viewer._dialogs[-1]
    dialog.codeEdit.setText(code)
    dialog._on_connect_clicked()
    # The stub WebRTCStreamService is `tile_controller._service`. The
    # controller auto-materializes the tile when the service reports a
    # successful connection (the SAS step is no longer a blocking gate
    # on the desktop side).
    tile_controller._service.sasReady.emit(["beach", "beam", "blow", "blot"])
    tile_controller._service.connectionStatusChanged.emit(True, "connected")
    qtbot.waitUntil(lambda: tile_controller.tile is not None, timeout=2000)
    return tile_controller


def test_two_tiles_visible_concurrently(qtbot, stub_service):
    viewer = FlightViewerController(signaling=InMemorySignalingChannel())
    qtbot.addWidget(viewer.window)
    viewer.show()

    a = _add_tile(viewer, "AAAA22", qtbot)
    b = _add_tile(viewer, "BBBB22", qtbot)

    assert "AAAA22" in viewer._tile_controllers
    assert "BBBB22" in viewer._tile_controllers
    assert a.tile is not None
    assert b.tile is not None

    viewer.shutdown()


def test_close_one_tile_leaves_other_intact(qtbot, stub_service):
    viewer = FlightViewerController(signaling=InMemorySignalingChannel())
    qtbot.addWidget(viewer.window)
    viewer.show()

    a = _add_tile(viewer, "AAAA23", qtbot)
    _add_tile(viewer, "BBBB23", qtbot)

    a.tear_down()
    qtbot.wait(50)

    assert "AAAA23" not in viewer._tile_controllers
    assert "BBBB23" in viewer._tile_controllers

    viewer.shutdown()


def test_aggregate_gallery_merges_in_timestamp_order(qtbot, stub_service):
    viewer = FlightViewerController(signaling=InMemorySignalingChannel())
    qtbot.addWidget(viewer.window)
    viewer.show()

    _add_tile(viewer, "AAAA24", qtbot)
    _add_tile(viewer, "BBBB24", qtbot)

    # Push detections out of order by timestamp.
    viewer.gallery.add_detection("AAAA24", {
        "feed_id": "AAAA24",
        "feed_label": "Tile-AAAA24",
        "class_name": "person",
        "confidence": 0.91,
        "captured_at_ms": 2000,
    })
    viewer.gallery.add_detection("BBBB24", {
        "feed_id": "BBBB24",
        "feed_label": "Tile-BBBB24",
        "class_name": "person",
        "confidence": 0.83,
        "captured_at_ms": 1000,
    })
    viewer.gallery.add_detection("AAAA24", {
        "feed_id": "AAAA24",
        "feed_label": "Tile-AAAA24",
        "class_name": "vehicle",
        "confidence": 0.77,
        "captured_at_ms": 1500,
    })

    # The gallery list should now have three rows.
    list_widget = viewer.window.mission_gallery.list_widget
    assert list_widget.count() == 3

    # Rows render newest-first (descending captured_at_ms) so the
    # operator's eyes naturally land on the latest detection.
    timestamps = []
    for i in range(list_widget.count()):
        widget = list_widget.itemWidget(list_widget.item(i))
        timestamps.append(widget.detection["captured_at_ms"])
    assert timestamps == sorted(timestamps, reverse=True)

    viewer.shutdown()


def test_muted_tile_excluded_from_aggregate_gallery(qtbot, stub_service):
    viewer = FlightViewerController(signaling=InMemorySignalingChannel())
    qtbot.addWidget(viewer.window)
    viewer.show()

    a = _add_tile(viewer, "MUT222", qtbot)
    _add_tile(viewer, "UNM222", qtbot)

    viewer.gallery.add_detection("MUT222", {
        "feed_id": "MUT222", "class_name": "person",
        "confidence": 0.6, "captured_at_ms": 100,
    })
    viewer.gallery.add_detection("UNM222", {
        "feed_id": "UNM222", "class_name": "person",
        "confidence": 0.6, "captured_at_ms": 200,
    })
    list_widget = viewer.window.mission_gallery.list_widget
    assert list_widget.count() == 2

    # Mute MUT222
    a.tile.muteGalleryToggled.emit(a.tile, True)
    qtbot.wait(20)
    # Only UNM222 row should remain after re-render.
    assert list_widget.count() == 1

    viewer.shutdown()


def test_deregister_feed_drops_its_rows(qtbot, stub_service):
    viewer = FlightViewerController(signaling=InMemorySignalingChannel())
    qtbot.addWidget(viewer.window)
    viewer.show()

    a = _add_tile(viewer, "DRP222", qtbot)
    _add_tile(viewer, "KEEP22", qtbot)

    viewer.gallery.add_detection("DRP222", {
        "feed_id": "DRP222", "class_name": "person",
        "confidence": 0.8, "captured_at_ms": 100,
    })
    viewer.gallery.add_detection("KEEP22", {
        "feed_id": "KEEP22", "class_name": "vehicle",
        "confidence": 0.8, "captured_at_ms": 200,
    })
    list_widget = viewer.window.mission_gallery.list_widget
    assert list_widget.count() == 2

    a.tear_down()
    qtbot.wait(50)
    assert list_widget.count() == 1
    remaining = list_widget.itemWidget(list_widget.item(0)).detection
    assert remaining["feed_id"] == "KEEP22"

    viewer.shutdown()
