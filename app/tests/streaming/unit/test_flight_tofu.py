"""Unit tests for the TOFU integration in FlightViewerController (plan §19.4.3)."""

from __future__ import annotations

import os
import sys

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.controllers.flight import FlightViewerController  # noqa: E402
from core.services.streaming.FingerprintStore import FingerprintStore  # noqa: E402
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _new_controller(tmp_path):
    """Construct a controller whose TOFU store points at a scratch DB."""
    controller = FlightViewerController(signaling=InMemorySignalingChannel())
    controller._fingerprint_store = FingerprintStore(
        db_path=tmp_path / "peers.sqlite"
    )
    return controller


def test_fingerprint_id_truncates_to_16_chars(qapp) -> None:
    key = FlightViewerController._fingerprint_id("sha-256 AB:CD:EF")
    assert isinstance(key, str)
    assert len(key) == 16
    assert key == FlightViewerController._fingerprint_id("sha-256 ab:cd:ef")
    assert key == FlightViewerController._fingerprint_id("sha-256 ABCDEF")


def test_remember_with_explicit_label_persists(qapp, tmp_path) -> None:
    controller = _new_controller(tmp_path)
    controller.remember_fingerprint(
        "sha-256 11:22:33:44", device_label="Operator A's M4E"
    )
    devices = controller.fingerprint_store.list_devices()
    assert len(devices) == 1
    assert devices[0].device_label == "Operator A's M4E"
    assert devices[0].sha256 == "sha-256 11:22:33:44"


def test_remember_without_label_mints_placeholder(qapp, tmp_path) -> None:
    """Plan §19.4.3 — placeholder fallback keeps TOFU populated when no
    operator label is supplied (e.g. tests / smoke runs)."""
    controller = _new_controller(tmp_path)
    controller.remember_fingerprint("sha-256 11:22:33:44")
    devices = controller.fingerprint_store.list_devices()
    assert len(devices) == 1
    assert devices[0].device_label.startswith("unlabeled-")
    assert devices[0].sha256 == "sha-256 11:22:33:44"


def test_is_fingerprint_trusted_round_trip(qapp, tmp_path) -> None:
    controller = _new_controller(tmp_path)
    fp = "sha-256 AA:BB:CC:DD"
    assert controller.is_fingerprint_trusted(fp) is False
    controller.remember_fingerprint(fp, device_label="Tablet A")
    assert controller.is_fingerprint_trusted(fp) is True
    assert controller.is_fingerprint_trusted("sha-256 99:88") is False


def test_lookup_device_returns_existing_record(qapp, tmp_path) -> None:
    controller = _new_controller(tmp_path)
    controller.remember_fingerprint(
        "sha-256 AA:BB:CC:DD", device_label="Tablet A"
    )
    record = controller.lookup_device_by_fingerprint("sha-256 AA:BB:CC:DD")
    assert record is not None
    assert record.device_label == "Tablet A"
    assert controller.lookup_device_by_fingerprint("sha-256 missing") is None


def test_remember_fingerprint_ignores_empty_input(qapp, tmp_path) -> None:
    controller = _new_controller(tmp_path)
    controller.remember_fingerprint("")
    controller.remember_fingerprint(None)  # type: ignore[arg-type]
    assert controller.fingerprint_store.list_devices() == []


def test_remember_fingerprint_persists_notes(qapp, tmp_path) -> None:
    """The ``notes`` arg surfaces in the stored record so an audit can tell
    a fingerprint swap apart from a clean first pair (plan §19.4.3)."""
    controller = _new_controller(tmp_path)
    controller.remember_fingerprint(
        "sha-256 AA:BB",
        device_label="Tablet A",
        notes="initial pair",
    )
    record = controller.fingerprint_store.get("Tablet A")
    assert record is not None
    assert record.notes == "initial pair"


def test_remember_fingerprint_updates_notes_on_overwrite(qapp, tmp_path) -> None:
    """Re-recording the same label with a new fingerprint + note
    overwrites — used by the TOFU mismatch warning's Accept path."""
    controller = _new_controller(tmp_path)
    controller.remember_fingerprint(
        "sha-256 AA:BB", device_label="Tablet A", notes="first"
    )
    controller.remember_fingerprint(
        "sha-256 99:88",
        device_label="Tablet A",
        notes="Fingerprint changed on 2026-05-21T12:00:00",
    )
    record = controller.fingerprint_store.get("Tablet A")
    assert record.sha256 == "sha-256 99:88"
    assert "Fingerprint changed" in record.notes


def test_fingerprints_match_normalises_form(qapp) -> None:
    """The mismatch guard treats colons/whitespace/case as cosmetic."""
    from core.controllers.flight.FlightTileController import FlightTileController

    assert FlightTileController._fingerprints_match(
        "sha-256 AB:CD:EF", "sha-256 ab:cd:ef"
    )
    assert FlightTileController._fingerprints_match(
        "sha-256 AB:CD:EF", "sha-256ABCDEF"
    )
    assert not FlightTileController._fingerprints_match(
        "sha-256 AB:CD:EF", "sha-256 99:88:77"
    )
    assert not FlightTileController._fingerprints_match("", "sha-256 AB")
    assert not FlightTileController._fingerprints_match("sha-256 AB", "")
