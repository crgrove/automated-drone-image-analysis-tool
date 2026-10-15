"""Tests for BearingRecoveryDialog's discovered-track offering."""

from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from core.views.images.viewer.dialogs.BearingRecoveryDialog import BearingRecoveryDialog


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


# Two images: a single image schedules the skip-recovery path instead.
_IMAGES = [{"path": "a.jpg"}, {"path": "b.jpg"}]


def test_no_suggestion_means_no_found_button(app):
    dialog = BearingRecoveryDialog(None, list(_IMAGES))
    assert dialog.found_track_button is None


def test_found_button_shows_name_and_full_path(app):
    track = r"C:\scan\flight\foreflight_tracklog.gpx"
    dialog = BearingRecoveryDialog(None, list(_IMAGES), suggested_track=track)
    assert dialog.found_track_button is not None
    assert "foreflight_tracklog.gpx" in dialog.found_track_button.text()
    assert dialog.found_track_button.toolTip() == track


def test_found_button_runs_track_calculation_with_suggested_file(app):
    track = "/scan/tracklog.kml"
    dialog = BearingRecoveryDialog(None, list(_IMAGES), suggested_track=track)
    with patch.object(dialog, "_start_calculation") as mock_start:
        dialog.found_track_button.click()
    mock_start.assert_called_once_with("track", track_file=track)


def test_found_button_follows_busy_state(app):
    track = "/scan/tracklog.kml"
    dialog = BearingRecoveryDialog(None, list(_IMAGES), suggested_track=track)
    # Drive the UI-state transitions directly (no worker thread involved)
    with patch(
        "core.views.images.viewer.dialogs.BearingRecoveryDialog.BearingCalculationWorker"
    ) as MockWorker:
        MockWorker.return_value.start.return_value = None
        dialog._start_calculation("track", track_file=track)
    assert not dialog.found_track_button.isEnabled()
    dialog._on_calculation_cancelled()
    assert dialog.found_track_button.isEnabled()


def test_empty_results_are_reported_and_dialog_stays_open(app):
    """Zero calculated bearings must be told to the user like an error, with
    the dialog left open for another attempt - the summary path used to run
    max() over the empty source tally and raise instead."""
    dialog = BearingRecoveryDialog(None, list(_IMAGES))
    accepted = []
    dialog.accepted.connect(lambda: accepted.append(True))

    with patch(
        "core.views.images.viewer.dialogs.BearingRecoveryDialog.QMessageBox"
    ) as MockBox:
        dialog._on_calculation_complete({})

    MockBox.critical.assert_called_once()
    MockBox.information.assert_not_called()
    assert accepted == []
    assert dialog.track_button.isEnabled()
    assert dialog.auto_button.isEnabled()
