"""Tests for the TileFetchDialog getters."""

import pytest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def test_defaults(app):
    from core.services.terrain.TileFetchService import library_root
    d = TileFetchDialog()
    assert d.want_dem() is True
    assert d.want_canopy() is True
    assert d.should_register() is True
    # The central library is the default destination: fixed path, no manual
    # output editing, registration implicit (checkbox hidden).
    assert d.get_destination() == "library"
    assert d.get_output_dir() == library_root()
    assert d.output_edit.isEnabled() is False
    assert d.register_checkbox.isHidden() or not d.register_checkbox.isVisible()


def test_dem_checkbox_defaults_off_when_flag_false(app):
    """The controller passes default_dem_checked=False when a usable elevation
    source already exists; the 3DEP box then starts unchecked (canopy unchanged)."""
    d = TileFetchDialog(default_dem_checked=False)
    assert d.want_dem() is False
    assert d.want_canopy() is True


def test_dem_checkbox_defaults_on_by_default(app):
    """Absent the flag, the 3DEP box is checked (preserves prior behavior)."""
    assert TileFetchDialog().want_dem() is True


def test_prefill_and_bounds(app):
    d = TileFetchDialog(default_bounds=(-120.5, 38.7, -120.4, 38.8))
    assert d.get_bounds() == pytest.approx((-120.5, 38.7, -120.4, 38.8))


def test_invalid_bounds_return_none(app):
    d = TileFetchDialog()
    assert d.get_bounds() is None            # empty fields
    d.min_lon_edit.setText("-120.4")
    d.min_lat_edit.setText("38.7")
    d.max_lon_edit.setText("-120.5")         # max < min
    d.max_lat_edit.setText("38.8")
    assert d.get_bounds() is None


def test_fill_combo_gated_on_has_mission(app):
    """The 'Loaded mission extent' option only appears when a mission is loaded;
    the image-folder option is always available."""
    no_mission = TileFetchDialog(has_mission=False)
    keys = [no_mission.fill_combo.itemData(i) for i in range(no_mission.fill_combo.count())]
    assert "mission" not in keys
    assert "folder" in keys

    with_mission = TileFetchDialog(has_mission=True)
    keys2 = [with_mission.fill_combo.itemData(i) for i in range(with_mission.fill_combo.count())]
    assert keys2 == ["mission", "folder"]


def test_fill_combo_reflects_selection(app):
    """Selecting an item updates the combo's displayed text.

    Regression: the previous menu button stayed on 'Fill area from' no matter
    what the user picked. A real combo shows the current selection.
    """
    d = TileFetchDialog(has_mission=True)
    d.fill_combo.setCurrentIndex(d.fill_combo.findData("folder"))
    assert d.fill_combo.currentText() == "Image folder..."
    assert d.fill_combo.currentData() == "folder"


def test_fill_combo_default_selection(app):
    """With a mission loaded the combo shows 'Loaded mission extent' (the AOI is
    auto-filled from it); with no mission it shows the placeholder (index -1)."""
    assert TileFetchDialog(has_mission=True).fill_combo.currentData() == "mission"
    assert TileFetchDialog(has_mission=False).fill_combo.currentIndex() == -1


def test_default_output_dir_enables_results_destination(app):
    """A results folder adds the 'Mission results folder' destination; picking
    it pins the output to that folder."""
    d = TileFetchDialog(default_output_dir="/mission/results")
    keys = [d.destination_combo.itemData(i) for i in range(d.destination_combo.count())]
    assert keys == ["library", "results", "custom"]

    d.destination_combo.setCurrentIndex(d.destination_combo.findData("results"))
    assert d.get_destination() == "results"
    assert d.get_output_dir() == "/mission/results"
    assert d.output_edit.isEnabled() is False
    assert d.should_register() is True   # checkbox visible again, still checked


def test_no_results_destination_without_mission_folder(app):
    d = TileFetchDialog()
    keys = [d.destination_combo.itemData(i) for i in range(d.destination_combo.count())]
    assert keys == ["library", "custom"]


def test_custom_destination_enables_manual_output(app):
    d = TileFetchDialog()
    d.destination_combo.setCurrentIndex(d.destination_combo.findData("custom"))
    assert d.output_edit.isEnabled() is True
    assert d.output_button.isEnabled() is True
    d.output_edit.setText("C:/tiles/here")
    assert d.get_output_dir() == "C:/tiles/here"


def test_library_destination_forces_registration(app):
    """Unchecking register in custom mode does not survive a switch back to
    the library (library downloads are always registered)."""
    d = TileFetchDialog()
    d.destination_combo.setCurrentIndex(d.destination_combo.findData("custom"))
    d.register_checkbox.setChecked(False)
    d.destination_combo.setCurrentIndex(d.destination_combo.findData("library"))
    assert d.should_register() is True


def test_set_aoi_and_buffer(app):
    d = TileFetchDialog()
    d.set_aoi((-120.51, 38.69, -120.45, 38.73))
    assert d.get_bounds() == pytest.approx((-120.51, 38.69, -120.45, 38.73))
    d.set_buffer(650.0)
    assert d.get_buffer() == pytest.approx(650.0)


def test_get_buffer_empty_is_none(app):
    d = TileFetchDialog()
    assert d.get_buffer() is None


# ---------------------------------------------------------------------------
# qtbot-driven interaction tests (button clicks, signals, gating)
# ---------------------------------------------------------------------------


def _shown_dialog(qtbot, **kwargs):
    """Create, register and expose a TileFetchDialog for mouse interaction."""
    d = TileFetchDialog(**kwargs)
    qtbot.addWidget(d)
    with qtbot.waitExposed(d):
        d.show()
    return d


def test_fill_combo_activation_emits_source_key(app, qtbot):
    """Activating an item emits fill_source_activated with the stable key.

    The dialog owns no fill logic; the controller connects this signal (see
    TileFetchController.run_fetch) and fills the AOI from the chosen source.
    """
    d = _shown_dialog(qtbot, has_mission=True)
    received = []
    d.fill_source_activated.connect(received.append)
    d.fill_combo.activated.emit(d.fill_combo.findData("folder"))
    assert received == ["folder"]


def test_fill_combo_placeholder_activation_is_noop(app, qtbot):
    """Activating an index with no source key (placeholder) emits nothing."""
    d = _shown_dialog(qtbot, has_mission=False)
    received = []
    d.fill_source_activated.connect(received.append)
    d._on_fill_source_activated(-1)
    assert received == []


def test_browse_button_updates_output_edit(app, qtbot, tmp_path):
    """Clicking Browse... writes the chosen folder into the output edit
    (custom destination — the browse button is disabled for library/results)."""
    d = _shown_dialog(qtbot)
    d.destination_combo.setCurrentIndex(d.destination_combo.findData("custom"))
    target = str(tmp_path)
    with patch("core.views.images.viewer.dialogs.TileFetchDialog.QFileDialog") as MockFile:
        MockFile.getExistingDirectory.return_value = target
        qtbot.mouseClick(d.output_button, Qt.LeftButton)
        MockFile.getExistingDirectory.assert_called_once()
    assert d.output_edit.text() == target
    assert d.get_output_dir() == target


def test_browse_button_cancel_leaves_output_unchanged(app, qtbot):
    """A cancelled folder picker (empty string) must not clear the output edit."""
    d = _shown_dialog(qtbot)
    d.destination_combo.setCurrentIndex(d.destination_combo.findData("custom"))
    d.output_edit.setText("C:/existing/output")
    with patch("core.views.images.viewer.dialogs.TileFetchDialog.QFileDialog") as MockFile:
        MockFile.getExistingDirectory.return_value = ""  # user cancelled
        qtbot.mouseClick(d.output_button, Qt.LeftButton)
    assert d.output_edit.text() == "C:/existing/output"


def test_download_button_emits_accepted_with_full_payload(app, qtbot, tmp_path):
    """Download emits accepted; getters expose the payload the caller reads."""
    d = _shown_dialog(qtbot)
    bounds = (-120.60, 38.65, -120.44, 38.79)
    out_dir = str(tmp_path)
    d.set_aoi(bounds)
    d.dem_checkbox.setChecked(True)
    d.canopy_checkbox.setChecked(False)
    d.output_edit.setText(out_dir)
    d.register_checkbox.setChecked(False)

    with qtbot.waitSignal(d.accepted, timeout=1000):
        qtbot.mouseClick(d.download_button, Qt.LeftButton)

    assert d.result() == QDialog.Accepted
    assert d.get_bounds() == pytest.approx(bounds)
    assert d.want_dem() is True
    assert d.want_canopy() is False
    assert d.get_output_dir() == out_dir
    assert d.should_register() is False


def test_cancel_button_emits_rejected(app, qtbot):
    """Cancel rejects the dialog."""
    d = _shown_dialog(qtbot)
    with qtbot.waitSignal(d.rejected, timeout=1000):
        qtbot.mouseClick(d.cancel_button, Qt.LeftButton)
    assert d.result() == QDialog.Rejected


def test_download_button_not_gated_by_bounds_validity(app, qtbot):
    """The Download button has no validity gating.

    It stays enabled and still accepts even with an empty/invalid AOI; the
    caller validates get_bounds()/get_output_dir() afterward (see
    TileFetchController.run_fetch).
    """
    d = _shown_dialog(qtbot)
    assert d.download_button.isEnabled() is True
    assert d.get_bounds() is None  # nothing entered yet

    with qtbot.waitSignal(d.accepted, timeout=1000):
        qtbot.mouseClick(d.download_button, Qt.LeftButton)

    assert d.result() == QDialog.Accepted
    assert d.get_bounds() is None


# ---------------------------------------------------------------------------
# Dataset coverage captions + aoi_changed
# ---------------------------------------------------------------------------


def test_status_labels_hidden_by_default(app):
    d = TileFetchDialog()
    assert d.dem_status_label.isHidden()
    assert d.canopy_status_label.isHidden()


def test_set_dataset_status_shows_texts(app):
    d = TileFetchDialog()
    d.set_dataset_status(TileFetchDialog.STATUS_COVERED, TileFetchDialog.STATUS_PARTIAL)
    assert not d.dem_status_label.isHidden()
    assert "already covered" in d.dem_status_label.text()
    assert not d.canopy_status_label.isHidden()
    assert "Partially covered" in d.canopy_status_label.text()


def test_set_dataset_status_unknown_hides(app):
    d = TileFetchDialog()
    d.set_dataset_status(TileFetchDialog.STATUS_COVERED, TileFetchDialog.STATUS_COVERED)
    d.set_dataset_status(TileFetchDialog.STATUS_UNKNOWN, TileFetchDialog.STATUS_UNKNOWN)
    assert d.dem_status_label.isHidden()
    assert d.canopy_status_label.isHidden()


def test_set_dataset_status_unregistered_texts_differ_by_dataset(app):
    d = TileFetchDialog()
    d.set_dataset_status(TileFetchDialog.STATUS_UNREGISTERED,
                         TileFetchDialog.STATUS_UNREGISTERED)
    assert "AWS Terrain Tiles" in d.dem_status_label.text()
    assert "canopy" in d.canopy_status_label.text().lower()


def test_set_dataset_status_none_states_the_consequence(app):
    """'Not covered' must say what actually happens, per dataset: DEM degrades
    to the online AWS baseline; canopy has no fallback at all. (Regression:
    the shared 'do not cover this area' text read as 'elevation won't work'
    even though AWS fills in automatically.)"""
    d = TileFetchDialog()
    d.set_dataset_status(TileFetchDialog.STATUS_NONE, TileFetchDialog.STATUS_NONE)
    assert "AWS Terrain Tiles" in d.dem_status_label.text()
    assert "used here instead" in d.dem_status_label.text()
    assert "no canopy attenuation" in d.canopy_status_label.text()


def test_manual_bounds_edit_emits_aoi_changed(app, qtbot):
    d = _shown_dialog(qtbot)
    received = []
    d.aoi_changed.connect(lambda: received.append(True))
    d.min_lon_edit.setText("-120.5")
    d.min_lon_edit.editingFinished.emit()
    assert received == [True]
