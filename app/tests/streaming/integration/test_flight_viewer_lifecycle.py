"""Integration tests for the single-tile Flight Viewer lifecycle (plan §12).

These tests stub :class:`WebRTCStreamService` so no aiortc / network is
involved; the goal is to verify the controller wiring across the pairing
dialog, ICE state propagation, SAS confirmation, and clean teardown.
"""

from __future__ import annotations

import os
import sys
from typing import List
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QDialog

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# Importing the module here ensures `sys.modules` has the entry; the
# `__init__.py` re-exports the *class* under the same dotted path so we
# fetch the module object from `sys.modules` to patch its WebRTCStreamService.
import core.controllers.flight.FlightTileController  # noqa: E402,F401
ftc_module = sys.modules["core.controllers.flight.FlightTileController"]

from core.controllers.flight import (  # noqa: E402
    FlightTileController,
    FlightViewerController,
)
from core.services.streaming.signaling import (  # noqa: E402
    CodeAlreadyAnswered,
    CodeNotFound,
    InMemorySignalingChannel,
    ViewerCapReached,
)


class StubWebRTCService(QObject):
    """Drop-in stand-in for :class:`WebRTCStreamService`.

    Mirrors the public signal surface so :class:`FlightTileController`
    cannot tell the difference. Tests drive the stub directly via
    ``emit_*`` helpers.
    """

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

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.connect_calls = 0
        self.confirm_calls: List[bool] = []
        self.cleanup_calls = 0

    # ---- API mirroring WebRTCStreamService ----

    def request_connect(self) -> None:
        self.connect_calls += 1

    def confirm_sas(self, accept: bool) -> None:
        self.confirm_calls.append(accept)

    def request_disconnect(self) -> None:
        self.cleanup_calls += 1

    def reset(self) -> None:
        pass

    def cleanup(self) -> None:
        self.cleanup_calls += 1

    # ---- test helpers ----

    def emit_sas(self, words: List[str]) -> None:
        self.sasReady.emit(words)

    def emit_connected(self) -> None:
        """Stand-in for the real service reaching ``connectionStatusChanged
        (True, "connected")`` after ICE finishes. The controller treats
        this as "pairing succeeded, dismiss the dialog and materialize the
        tile" (the SAS gate is one-sided on the publisher side now)."""
        self.connectionStatusChanged.emit(True, "connected")

    def emit_error(self, msg: str) -> None:
        self.errorOccurred.emit(msg)

    def emit_cap(self, current: int, limit: int) -> None:
        self.capReached.emit(current, limit)


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def stub_service(monkeypatch):
    instances: List[StubWebRTCService] = []

    def factory(*args, **kwargs):
        svc = StubWebRTCService()
        instances.append(svc)
        return svc

    monkeypatch.setattr(ftc_module, "WebRTCStreamService", factory)
    return instances


def _exec_dialog(controller: FlightTileController) -> None:
    """Open the dialog without spinning the event loop."""
    dialog = controller.run_pairing_dialog()
    dialog.show()
    return dialog


def test_pairing_happy_path_materializes_tile(qtbot, stub_service):
    """Pairing dialog auto-dismisses + materializes the tile when the
    service reports a successful connection. No SAS-confirm step on the
    desktop side; the publisher gates its own media via its operator SAS."""
    signaling = InMemorySignalingChannel()
    controller = FlightTileController(signaling=signaling)

    tiles = []
    controller.tileReady.connect(lambda t: tiles.append(t))

    dialog = _exec_dialog(controller)
    qtbot.addWidget(dialog)

    # Simulate user typing a valid code and pressing Connect.
    dialog.codeEdit.setText("ABC234")
    dialog._on_connect_clicked()

    assert stub_service, "stub service should have been constructed"
    svc = stub_service[-1]
    assert svc.connect_calls == 1

    # Service fires the SAS phrase (display-only) then the connected event;
    # controller auto-accepts the dialog → tile materializes.
    svc.emit_sas(["acid", "acre", "atom", "axis"])
    svc.emit_connected()

    qtbot.waitUntil(lambda: bool(tiles), timeout=2000)

    assert len(tiles) == 1
    assert tiles[0].pairing_code == "ABC234"
    controller.tear_down()


def test_cap_reached_shows_failed_page(qtbot, stub_service):
    signaling = InMemorySignalingChannel()
    controller = FlightTileController(signaling=signaling)

    dialog = _exec_dialog(controller)
    qtbot.addWidget(dialog)
    dialog.codeEdit.setText("CAP234")
    dialog._on_connect_clicked()
    svc = stub_service[-1]
    svc.emit_cap(3, 3)
    qtbot.wait(20)

    assert "3" in dialog.failedDetail.text()
    assert dialog.stateStack.currentIndex() == 2  # PAGE_FAILED


def test_code_not_found_propagates_through_service_error(qtbot, stub_service):
    signaling = InMemorySignalingChannel()
    controller = FlightTileController(signaling=signaling)

    dialog = _exec_dialog(controller)
    qtbot.addWidget(dialog)
    dialog.codeEdit.setText("NTFND2")
    dialog._on_connect_clicked()
    svc = stub_service[-1]
    # Real service would convert CodeNotFound into an errorOccurred string.
    svc.emit_error(str(CodeNotFound("code not found")))
    qtbot.wait(20)

    assert "not found" in dialog.failedDetail.text().lower()


def test_code_already_answered_renders_distinct_message(qtbot, stub_service):
    signaling = InMemorySignalingChannel()
    controller = FlightTileController(signaling=signaling)

    dialog = _exec_dialog(controller)
    qtbot.addWidget(dialog)
    dialog.codeEdit.setText("DUP234")
    dialog._on_connect_clicked()
    svc = stub_service[-1]
    svc.emit_error(str(CodeAlreadyAnswered("code already used")))
    qtbot.wait(20)

    assert "already" in dialog.failedDetail.text().lower()


def test_disconnect_cleans_up_service(qtbot, stub_service):
    signaling = InMemorySignalingChannel()
    controller = FlightTileController(signaling=signaling)

    dialog = _exec_dialog(controller)
    qtbot.addWidget(dialog)
    dialog.codeEdit.setText("CKN234")
    dialog._on_connect_clicked()
    svc = stub_service[-1]
    svc.emit_sas(["aroma", "arrow", "axis", "blame"])
    svc.emit_connected()
    qtbot.wait(20)

    controller.tear_down()
    assert svc.cleanup_calls >= 1


def test_viewer_controller_opens_dialog_with_existing_window(qtbot, stub_service):
    """End-to-end smoke: FlightViewerController spawns + disposes a tile."""
    signaling = InMemorySignalingChannel()
    viewer = FlightViewerController(signaling=signaling)
    qtbot.addWidget(viewer.window)
    viewer.show()

    viewer.open_pairing_dialog()
    # The dialog is held in viewer._dialogs as (controller, dialog).
    assert viewer._dialogs, "controller should track open dialogs"
    tile_controller, dialog = viewer._dialogs[-1]
    dialog.codeEdit.setText("FVC234")
    dialog._on_connect_clicked()
    stub_service[-1].emit_sas(["band", "barn", "base", "blow"])
    stub_service[-1].emit_connected()
    qtbot.waitUntil(lambda: tile_controller.tile is not None, timeout=2000)

    # Tile registered with the gallery
    assert "FVC234" in viewer._tile_controllers

    # Close the tile programmatically
    tile_controller.tear_down()
    qtbot.wait(20)
    assert "FVC234" not in viewer._tile_controllers
    viewer.shutdown()
