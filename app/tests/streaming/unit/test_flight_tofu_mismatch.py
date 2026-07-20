"""Unit tests for the TOFU mismatch resolver flow (plan §19.4.3).

Exercises :meth:`FlightTileController._resolve_device_label` directly
with patched dialog helpers so we don't need a real Qt event loop or
operator input.
"""

from __future__ import annotations

import os
import sys
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.controllers.flight.FlightTileController import FlightTileController  # noqa: E402
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


class _FakePeerRecord:
    def __init__(self, label):
        self.device_label = label


def _new_controller():
    controller = FlightTileController(signaling=InMemorySignalingChannel())
    controller._pairing_code = "ABC234"
    controller._dialog = None
    return controller


def _mock_viewer(*, fp_record: Optional[_FakePeerRecord] = None,
                 known_fp: Optional[str] = None):
    """Build a stub ``viewer`` controller exposing the TOFU API surface."""
    viewer = MagicMock()
    viewer.lookup_device_by_fingerprint = MagicMock(return_value=fp_record)
    viewer.known_fingerprint = MagicMock(return_value=known_fp)
    return viewer


def test_resolve_reuses_label_when_fingerprint_already_trusted(qapp):
    """Fingerprint we've seen before — silent reuse, no prompt needed."""
    controller = _new_controller()
    viewer = _mock_viewer(fp_record=_FakePeerRecord("Tablet A"))
    label, note = controller._resolve_device_label(viewer, "sha-256 11:22")
    assert label == "Tablet A"
    assert note is None


def test_resolve_returns_placeholder_when_operator_dismisses_prompt(qapp):
    """User cancels QInputDialog → controller falls back to placeholder label."""
    controller = _new_controller()
    viewer = _mock_viewer()
    with patch(
        "PySide6.QtWidgets.QInputDialog.getText",
        return_value=("", False),
    ):
        result = controller._resolve_device_label(viewer, "sha-256 11:22")
    assert result == (None, None)


def test_resolve_stores_typed_label_for_new_device(qapp):
    controller = _new_controller()
    viewer = _mock_viewer()
    with patch(
        "PySide6.QtWidgets.QInputDialog.getText",
        return_value=("Operator A's M4E", True),
    ):
        result = controller._resolve_device_label(viewer, "sha-256 11:22")
    assert result == ("Operator A's M4E", None)


def test_resolve_warns_and_accepts_fingerprint_mismatch(qapp):
    """Operator types a known label, fingerprint differs → warning → Accept."""
    controller = _new_controller()
    viewer = _mock_viewer(known_fp="sha-256 OLD:KEY")
    with patch(
        "PySide6.QtWidgets.QInputDialog.getText",
        return_value=("Tablet A", True),
    ), patch(
        "PySide6.QtWidgets.QMessageBox.warning",
        return_value=QMessageBox.StandardButton.Yes,
    ):
        result = controller._resolve_device_label(viewer, "sha-256 NEW:KEY")
    assert result is not None
    label, note = result
    assert label == "Tablet A"
    assert note is not None
    assert "Fingerprint changed" in note


def test_resolve_warns_and_rejects_fingerprint_mismatch(qapp):
    """Operator chooses Reject on the mismatch warning — caller tears down."""
    controller = _new_controller()
    viewer = _mock_viewer(known_fp="sha-256 OLD:KEY")
    with patch(
        "PySide6.QtWidgets.QInputDialog.getText",
        return_value=("Tablet A", True),
    ), patch(
        "PySide6.QtWidgets.QMessageBox.warning",
        return_value=QMessageBox.StandardButton.No,
    ):
        result = controller._resolve_device_label(viewer, "sha-256 NEW:KEY")
    assert result is None


def test_resolve_does_not_warn_when_typed_label_matches_existing_fp(qapp):
    """Operator types a known label and the fingerprint matches — no warning."""
    controller = _new_controller()
    viewer = _mock_viewer(known_fp="sha-256 11:22:33")
    with patch(
        "PySide6.QtWidgets.QInputDialog.getText",
        return_value=("Tablet A", True),
    ), patch(
        "PySide6.QtWidgets.QMessageBox.warning",
    ) as mock_warning:
        result = controller._resolve_device_label(
            viewer, "sha-256 11:22:33"
        )
    assert result == ("Tablet A", None)
    mock_warning.assert_not_called()
