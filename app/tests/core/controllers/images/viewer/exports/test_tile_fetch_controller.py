"""Tests for TileFetchThread + TileFetchController wiring."""

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from core.controllers.images.viewer.exports.TileFetchController import (
    TileFetchThread,
    TileFetchController,
)
from core.services.terrain.TileFetchService import FetchResult


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def test_thread_runs_both_products(app, tmp_path):
    service = MagicMock()
    service.fetch_3dep_dem.return_value = FetchResult('usgs_3dep_dem', str(tmp_path / "dem"), None)
    service.fetch_meta_canopy.return_value = FetchResult('meta_chm', str(tmp_path / "chm"), None)
    thread = TileFetchThread(service, (-120.5, 38.7, -120.4, 38.8), str(tmp_path),
                             want_dem=True, want_canopy=True)
    results = []
    thread.finished.connect(lambda r: results.append(r))
    thread.run()
    assert service.fetch_3dep_dem.called
    assert service.fetch_meta_canopy.called
    assert results and 'dem' in results[0] and 'canopy' in results[0]


def test_thread_dem_only(app, tmp_path):
    service = MagicMock()
    service.fetch_3dep_dem.return_value = FetchResult('usgs_3dep_dem', str(tmp_path), None)
    thread = TileFetchThread(service, (-120.5, 38.7, -120.4, 38.8), str(tmp_path),
                             want_dem=True, want_canopy=False)
    thread.run()
    assert service.fetch_3dep_dem.called
    assert not service.fetch_meta_canopy.called


def test_thread_emits_error(app, tmp_path):
    service = MagicMock()
    service.fetch_3dep_dem.side_effect = RuntimeError("net down")
    thread = TileFetchThread(service, (-120.5, 38.7, -120.4, 38.8), str(tmp_path),
                             want_dem=True, want_canopy=False)
    errors = []
    thread.errorOccurred.connect(lambda m: errors.append(m))
    thread.run()
    assert errors and "net down" in errors[0]


def test_register_results_writes_settings(app, tmp_path):
    settings = MagicMock()
    stored = {}
    settings.set_setting.side_effect = lambda k, v: stored.__setitem__(k, v)
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl._register = True

    dem = FetchResult('usgs_3dep_dem', str(tmp_path / "dem"),
                      str(tmp_path / "dem" / "dem_manifest.csv"))
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"),
                         str(tmp_path / "chm" / "chm_manifest.csv"))
    ctrl._register_results({'dem': dem, 'canopy': canopy})

    assert stored['Terrain3DEPManifestPath'] == dem.manifest_path
    assert stored['Terrain3DEPTilesDir'] == dem.out_dir
    assert stored['TerrainProviderId'] == 'usgs_3dep_local'
    assert stored['CanopyManifestPath'] == canopy.manifest_path
    assert stored['CanopyTilesDir'] == canopy.out_dir
    assert stored['CanopyKind'] == 'meta'


def test_register_disabled_writes_nothing(app):
    settings = MagicMock()
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl._register = False
    ctrl._register_results({'dem': FetchResult('usgs_3dep_dem', "d", "m.csv")})
    settings.set_setting.assert_not_called()


def test_fill_aoi_fills_dialog_from_mission(app):
    from unittest.mock import patch
    from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog(has_mission=True)
    images = [{"path": "a.jpg"}, {"path": "b.jpg"}]

    with patch("core.services.coverage.aoi.compute_mission_gps_bounds",
               return_value=(-120.50, 38.70, -120.46, 38.72)), \
         patch("core.services.coverage.aoi.suggest_buffer_m", return_value=400.0):
        ctrl._fill_aoi(dialog, images, "loaded mission")

    assert dialog.get_buffer() == 400.0
    b = dialog.get_bounds()
    # Padded outward from the raw camera-position box.
    assert b is not None and b[0] < -120.50 and b[2] > -120.46


def test_fill_aoi_warns_when_no_gps(app):
    from unittest.mock import patch
    from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog(has_mission=True)
    with patch("core.services.coverage.aoi.compute_mission_gps_bounds", return_value=None), \
         patch("core.controllers.images.viewer.exports.TileFetchController.QMessageBox") as mock_mb:
        ctrl._fill_aoi(dialog, [{"path": "a.jpg"}], "loaded mission")
    mock_mb.warning.assert_called_once()


def test_fill_aoi_respects_existing_buffer(app):
    from unittest.mock import patch
    from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog(has_mission=True)
    dialog.set_buffer(900.0)   # user-set buffer must be kept
    with patch("core.services.coverage.aoi.compute_mission_gps_bounds",
               return_value=(-120.50, 38.70, -120.46, 38.72)), \
         patch("core.services.coverage.aoi.suggest_buffer_m", return_value=100.0) as mock_suggest:
        ctrl._fill_aoi(dialog, [{"path": "a.jpg"}], "loaded mission")
    mock_suggest.assert_not_called()
    assert dialog.get_buffer() == 900.0


# ---------------------------------------------------------------------------
# Thread-slot handlers + run_fetch validation/wiring (uncovered lines 82-128).
# ---------------------------------------------------------------------------

_MODULE = "core.controllers.images.viewer.exports.TileFetchController"


# --- _on_finished ----------------------------------------------------------

def test_on_finished_shows_complete_and_counts(app, tmp_path):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl.progress_dialog = MagicMock()
    ctrl._register = False
    dem = FetchResult('usgs_3dep_dem', str(tmp_path / "dem"), None, tiles_written=5)
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"), None, tiles_written=3)

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_finished({'dem': dem, 'canopy': canopy})

    ctrl.progress_dialog.accept.assert_called_once()
    mb.information.assert_called_once()
    args = mb.information.call_args.args
    assert args[1] == "Download Complete"
    assert "8" in args[2]   # 5 + 3 tiles written


def test_on_finished_registers_when_requested(app, tmp_path):
    from unittest.mock import patch

    settings = MagicMock()
    stored = {}
    settings.set_setting.side_effect = lambda k, v: stored.__setitem__(k, v)
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl.progress_dialog = MagicMock()
    ctrl._register = True
    dem = FetchResult('usgs_3dep_dem', str(tmp_path / "dem"),
                      str(tmp_path / "dem" / "m.csv"), tiles_written=2)

    with patch(f"{_MODULE}.QMessageBox"):
        ctrl._on_finished({'dem': dem})

    assert stored['Terrain3DEPManifestPath'] == dem.manifest_path
    assert stored['Terrain3DEPTilesDir'] == dem.out_dir
    assert stored['TerrainProviderId'] == 'usgs_3dep_local'


def test_on_finished_handles_missing_progress_dialog(app, tmp_path):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl.progress_dialog = None
    ctrl._register = False

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_finished({'dem': FetchResult('d', 'o', None, tiles_written=1)})

    mb.information.assert_called_once()
    assert "1" in mb.information.call_args.args[2]


# --- per-product outcome surfacing (regression: silent canopy failure) -------

def test_on_finished_warns_when_canopy_wrote_nothing(app, tmp_path):
    """A requested product with zero tiles must produce a WARNING that names
    the product and states it was not registered — not a success dialog.

    Regression: a failed canopy download reported "Download Complete" while
    silently registering nothing ("CanopyServiceFactory: paths unset").
    """
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl.progress_dialog = MagicMock()
    ctrl._register = True
    dem = FetchResult('usgs_3dep_dem', str(tmp_path / "dem"),
                      str(tmp_path / "dem" / "m.csv"), tiles_written=1)
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"), None,
                         tiles_written=0, tiles_failed=1,
                         errors=[("chm_x.tif", "download failed")])

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_finished({'dem': dem, 'canopy': canopy})

    mb.information.assert_not_called()
    mb.warning.assert_called_once()
    title, body = mb.warning.call_args.args[1], mb.warning.call_args.args[2]
    assert "Problem" in title
    assert "Canopy height" in body and "failed" in body
    assert "NOT registered" in body


def test_on_finished_warns_when_area_has_no_canopy_coverage(app, tmp_path):
    """All-absent tiles (sparse coverage) warn with a no-coverage message."""
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl.progress_dialog = MagicMock()
    ctrl._register = True
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"), None,
                         tiles_written=0, tiles_skipped=2)

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_finished({'canopy': canopy})

    mb.warning.assert_called_once()
    assert "no data covers this area" in mb.warning.call_args.args[2]


def test_on_finished_success_states_registration(app, tmp_path):
    """A clean download says exactly what got registered."""
    from unittest.mock import patch

    settings = MagicMock()
    settings.get_setting.return_value = ''   # no LANDFIRE configured
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl.progress_dialog = MagicMock()
    ctrl._register = True
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"),
                         str(tmp_path / "chm" / "m.csv"), tiles_written=1)

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_finished({'canopy': canopy})

    mb.information.assert_called_once()
    body = mb.information.call_args.args[2]
    assert "registered as the active source" in body


def test_register_results_returns_registration_map(app, tmp_path):
    settings = MagicMock()
    settings.get_setting.return_value = ''
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl._register = True
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"),
                         str(tmp_path / "chm" / "m.csv"), tiles_written=1)
    registered = ctrl._register_results({'canopy': canopy})
    assert registered == {'canopy': True}


def test_register_results_skips_canopy_without_manifest(app, tmp_path):
    """manifest_path=None (nothing usable downloaded) must not register."""
    settings = MagicMock()
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl._register = True
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"), None)
    registered = ctrl._register_results({'canopy': canopy})
    assert 'canopy' not in registered
    canopy_writes = [c for c in settings.set_setting.call_args_list
                     if c.args and str(c.args[0]).startswith('Canopy')]
    assert canopy_writes == []


# --- LANDFIRE clobber guard ---------------------------------------------------

def _landfire_settings():
    settings = MagicMock()
    values = {'CanopyKind': 'landfire',
              'CanopyManifestPath': 'C:/landfire/manifest.csv',
              'CanopyTilesDir': 'C:/landfire/tiles'}
    settings.get_setting.side_effect = lambda k, default='': values.get(k, default)
    return settings


def test_landfire_source_not_silently_clobbered(app, tmp_path):
    """With LANDFIRE configured, declining the prompt keeps it untouched."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QMessageBox

    settings = _landfire_settings()
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl._register = True
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"),
                         str(tmp_path / "chm" / "m.csv"), tiles_written=1)

    with patch(f"{_MODULE}.QMessageBox") as mb:
        mb.StandardButton = QMessageBox.StandardButton
        mb.question.return_value = QMessageBox.StandardButton.No
        registered = ctrl._register_results({'canopy': canopy})

    mb.question.assert_called_once()
    assert registered == {'canopy': False}
    canopy_writes = [c for c in settings.set_setting.call_args_list
                     if c.args and str(c.args[0]).startswith('Canopy')]
    assert canopy_writes == []


def test_landfire_overwrite_confirmed_registers_meta(app, tmp_path):
    """Accepting the prompt switches the canopy source to the Meta download."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QMessageBox

    settings = _landfire_settings()
    stored = {}
    settings.set_setting.side_effect = lambda k, v: stored.__setitem__(k, v)
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl._register = True
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"),
                         str(tmp_path / "chm" / "m.csv"), tiles_written=1)

    with patch(f"{_MODULE}.QMessageBox") as mb:
        mb.StandardButton = QMessageBox.StandardButton
        mb.question.return_value = QMessageBox.StandardButton.Yes
        registered = ctrl._register_results({'canopy': canopy})

    assert registered == {'canopy': True}
    assert stored['CanopyKind'] == 'meta'


def test_no_guard_when_no_landfire_configured(app, tmp_path):
    """Meta/empty existing config registers without any prompt."""
    from unittest.mock import patch

    settings = MagicMock()
    settings.get_setting.return_value = ''
    ctrl = TileFetchController(MagicMock(), settings)
    ctrl._register = True
    canopy = FetchResult('meta_chm', str(tmp_path / "chm"),
                         str(tmp_path / "chm" / "m.csv"), tiles_written=1)

    with patch(f"{_MODULE}.QMessageBox") as mb:
        registered = ctrl._register_results({'canopy': canopy})

    mb.question.assert_not_called()
    assert registered == {'canopy': True}


# --- phase messaging in the download thread -----------------------------------

def test_thread_emits_phase_transition_messages(app, tmp_path):
    """The thread announces each phase up front so the dialog never shows a
    stale 'DEM 100%' while the canopy phase runs (the frozen-dialog bug)."""
    service = MagicMock()
    service.fetch_3dep_dem.return_value = FetchResult('usgs_3dep_dem', str(tmp_path), None)
    service.fetch_meta_canopy.return_value = FetchResult('meta_chm', str(tmp_path), None)
    thread = TileFetchThread(service, (-120.5, 38.7, -120.4, 38.8), str(tmp_path),
                             want_dem=True, want_canopy=True)
    messages = []
    thread.progressUpdated.connect(lambda c, t, m: messages.append(m))
    thread.run()

    assert any("Step 1/2" in m and "DEM" in m for m in messages)
    assert any("Step 2/2" in m and "canopy" in m.lower() for m in messages)
    # The canopy announcement resets the bar BEFORE the canopy fetch runs.
    step2 = next(i for i, m in enumerate(messages) if "Step 2/2" in m)
    assert step2 >= 1


def test_last_results_lifecycle(app, tmp_path):
    """last_results reports only a COMPLETED run: None initially, set by
    _on_finished, reset when a new run_fetch starts (chaining contract)."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    settings = MagicMock()
    settings.get_setting.return_value = ''
    ctrl = TileFetchController(MagicMock(), settings)
    assert ctrl.last_results is None

    ctrl.progress_dialog = MagicMock()
    ctrl._register = False
    results = {'dem': FetchResult('usgs_3dep_dem', str(tmp_path), None, tiles_written=1)}
    with patch(f"{_MODULE}.QMessageBox"):
        ctrl._on_finished(results)
    assert ctrl.last_results == results

    # A new run resets it so a dismissed dialog can't reuse stale results.
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox"):
        MockDlg.return_value.exec.return_value = QDialog.Rejected
        ctrl.run_fetch()
    assert ctrl.last_results is None


def test_thread_prefixes_service_progress_with_phase(app, tmp_path):
    """Per-tile service progress carries the phase prefix."""
    def dem_with_progress(bounds, out_dir, progress_callback=None, cancel_check=None):
        if progress_callback:
            progress_callback(1, 1, "Downloading DEM tile 1/1...")
        return FetchResult('usgs_3dep_dem', out_dir, None, tiles_written=1)

    service = MagicMock()
    service.fetch_3dep_dem.side_effect = dem_with_progress
    service.fetch_meta_canopy.return_value = FetchResult('meta_chm', str(tmp_path), None)
    thread = TileFetchThread(service, (-120.5, 38.7, -120.4, 38.8), str(tmp_path),
                             want_dem=True, want_canopy=True)
    messages = []
    thread.progressUpdated.connect(lambda c, t, m: messages.append(m))
    thread.run()

    assert any(m.startswith("Step 1/2: Downloading DEM tile") for m in messages)


# --- _on_error -------------------------------------------------------------

def test_on_error_shows_critical_rejects_and_logs(app):
    from unittest.mock import patch

    logger = MagicMock()
    ctrl = TileFetchController(MagicMock(), MagicMock(), logger=logger)
    ctrl.progress_dialog = MagicMock()
    ctrl.progress_dialog.isVisible.return_value = True

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_error("boom")

    ctrl.progress_dialog.reject.assert_called_once()
    logger.error.assert_called_once()
    mb.critical.assert_called_once()
    args = mb.critical.call_args.args
    assert args[1] == "Download Error"
    assert "boom" in args[2]


def test_on_error_skips_reject_when_dialog_hidden(app):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock(), logger=MagicMock())
    ctrl.progress_dialog = MagicMock()
    ctrl.progress_dialog.isVisible.return_value = False

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_error("x")

    ctrl.progress_dialog.reject.assert_not_called()
    mb.critical.assert_called_once()


def test_on_error_handles_no_progress_dialog(app):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock(), logger=MagicMock())
    ctrl.progress_dialog = None

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_error("x")   # must not raise

    mb.critical.assert_called_once()


# --- _on_cancelled ---------------------------------------------------------

def test_on_cancelled_terminates_thread_rejects_and_warns(app):
    """Cancel tears down the transfer AND says nothing was registered —
    a silently closing dialog was being read as a successful download."""
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl.thread = MagicMock()
    ctrl.thread.isRunning.return_value = True
    ctrl.progress_dialog = MagicMock()
    ctrl.progress_dialog.isVisible.return_value = True

    with patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._on_cancelled()

    ctrl.thread.terminate.assert_called_once()
    ctrl.thread.wait.assert_called_once()
    ctrl.progress_dialog.reject.assert_called_once()
    mb.warning.assert_called_once()
    assert "Cancelled" in mb.warning.call_args.args[1]
    assert "No tiles were registered" in mb.warning.call_args.args[2]


def test_on_cancelled_skips_when_thread_idle_and_dialog_hidden(app):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl.thread = MagicMock()
    ctrl.thread.isRunning.return_value = False
    ctrl.progress_dialog = MagicMock()
    ctrl.progress_dialog.isVisible.return_value = False

    with patch(f"{_MODULE}.QMessageBox"):
        ctrl._on_cancelled()

    ctrl.thread.terminate.assert_not_called()
    ctrl.progress_dialog.reject.assert_not_called()


def test_on_cancelled_handles_none_state(app):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl.thread = None
    ctrl.progress_dialog = None

    with patch(f"{_MODULE}.QMessageBox"):
        ctrl._on_cancelled()   # must not raise


# --- _fill_from_folder -----------------------------------------------------

def test_fill_from_folder_cancelled_is_noop(app):
    from unittest.mock import patch
    from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog()

    with patch(f"{_MODULE}.QFileDialog.getExistingDirectory", return_value=""), \
         patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._fill_from_folder(dialog)

    mb.warning.assert_not_called()


def test_fill_from_folder_no_images_warns(app, tmp_path):
    from unittest.mock import patch
    from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog()
    empty = tmp_path / "empty"
    empty.mkdir()

    with patch(f"{_MODULE}.QFileDialog.getExistingDirectory", return_value=str(empty)), \
         patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._fill_from_folder(dialog)

    mb.warning.assert_called_once()
    assert mb.warning.call_args.args[1] == "No Images"


def test_fill_from_folder_no_gps_warns(app, tmp_path):
    from unittest.mock import patch
    from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog()
    folder = tmp_path / "imgs"
    folder.mkdir()
    (folder / "a.jpg").write_bytes(b"x")
    (folder / "b.jpg").write_bytes(b"x")

    with patch(f"{_MODULE}.QFileDialog.getExistingDirectory", return_value=str(folder)), \
         patch("core.services.coverage.aoi.compute_mission_gps_bounds", return_value=None), \
         patch(f"{_MODULE}.QMessageBox") as mb:
        ctrl._fill_from_folder(dialog)

    mb.warning.assert_called_once()
    assert mb.warning.call_args.args[1] == "No GPS Found"


def test_fill_from_folder_with_gps_fills_aoi(app, tmp_path):
    from unittest.mock import patch
    from core.views.images.viewer.dialogs.TileFetchDialog import TileFetchDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog()
    dialog.set_buffer(999.0)   # a fresh folder must clear + re-suggest the buffer
    folder = tmp_path / "imgs"
    folder.mkdir()
    (folder / "a.jpg").write_bytes(b"x")

    with patch(f"{_MODULE}.QFileDialog.getExistingDirectory", return_value=str(folder)), \
         patch("core.services.coverage.aoi.compute_mission_gps_bounds",
               return_value=(-120.50, 38.70, -120.46, 38.72)), \
         patch("core.services.coverage.aoi.suggest_buffer_m", return_value=250.0):
        ctrl._fill_from_folder(dialog)

    assert dialog.get_buffer() == 250.0
    b = dialog.get_bounds()
    assert b is not None and b[0] < -120.50 and b[2] > -120.46


# --- run_fetch validation --------------------------------------------------

def _accepted_dialog_mock(mock_dialog_cls):
    """Return the instance mock of a patched TileFetchDialog set to 'accepted'."""
    from PySide6.QtWidgets import QDialog
    dlg = mock_dialog_cls.return_value
    dlg.exec.return_value = QDialog.Accepted
    return dlg


def test_run_fetch_returns_when_dialog_cancelled(app):
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox") as mb:
        MockDlg.return_value.exec.return_value = QDialog.Rejected
        ctrl.run_fetch()

    mb.warning.assert_not_called()
    assert ctrl.thread is None


def test_run_fetch_invalid_area_warns(app):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox") as mb:
        dlg = _accepted_dialog_mock(MockDlg)
        dlg.get_bounds.return_value = None
        ctrl.run_fetch()

    mb.warning.assert_called_once()
    assert mb.warning.call_args.args[1] == "Invalid Area"
    assert ctrl.thread is None


def test_run_fetch_no_output_folder_warns(app):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox") as mb:
        dlg = _accepted_dialog_mock(MockDlg)
        dlg.get_bounds.return_value = (-120.5, 38.7, -120.4, 38.8)
        dlg.get_output_dir.return_value = ""
        ctrl.run_fetch()

    mb.warning.assert_called_once()
    assert mb.warning.call_args.args[1] == "No Output Folder"
    assert ctrl.thread is None


def test_run_fetch_no_dataset_warns(app):
    from unittest.mock import patch

    ctrl = TileFetchController(MagicMock(), MagicMock())
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox") as mb:
        dlg = _accepted_dialog_mock(MockDlg)
        dlg.get_bounds.return_value = (-120.5, 38.7, -120.4, 38.8)
        dlg.get_output_dir.return_value = "/out"
        dlg.want_dem.return_value = False
        dlg.want_canopy.return_value = False
        ctrl.run_fetch()

    mb.warning.assert_called_once()
    assert mb.warning.call_args.args[1] == "No Dataset"
    assert ctrl.thread is None


# --- run_fetch success wiring ----------------------------------------------

def test_run_fetch_success_starts_thread_and_wires_slots(app):
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.TileFetchService") as MockSvc, \
         patch(f"{_MODULE}.ExportProgressDialog") as MockProg, \
         patch(f"{_MODULE}.TileFetchThread") as MockThread, \
         patch(f"{_MODULE}.QApplication"), \
         patch(f"{_MODULE}.QMessageBox") as mb:
        dlg = _accepted_dialog_mock(MockDlg)
        dlg.get_bounds.return_value = (-120.5, 38.7, -120.4, 38.8)
        dlg.get_output_dir.return_value = "/out"
        dlg.want_dem.return_value = True
        dlg.want_canopy.return_value = False
        dlg.should_register.return_value = True
        prog = MockProg.return_value
        prog.exec.return_value = QDialog.Accepted   # not rejected -> no cancel
        thread = MockThread.return_value

        ctrl.run_fetch()

    assert MockSvc.called
    assert ctrl._register is True
    thread.start.assert_called_once()
    prog.show.assert_called_once()
    thread.finished.connect.assert_called_once_with(ctrl._on_finished)
    thread.errorOccurred.connect.assert_called_once_with(ctrl._on_error)
    thread.progressUpdated.connect.assert_called_once_with(ctrl._on_progress)
    thread.canceled.connect.assert_called_once_with(ctrl._on_cancelled)
    prog.cancel_requested.connect.assert_called_once_with(thread.cancel)
    thread.cancel.assert_not_called()
    mb.warning.assert_not_called()


def test_run_fetch_cancels_thread_when_progress_rejected(app):
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.TileFetchService"), \
         patch(f"{_MODULE}.ExportProgressDialog") as MockProg, \
         patch(f"{_MODULE}.TileFetchThread") as MockThread, \
         patch(f"{_MODULE}.QApplication"), \
         patch(f"{_MODULE}.QMessageBox"):
        dlg = _accepted_dialog_mock(MockDlg)
        dlg.get_bounds.return_value = (-120.5, 38.7, -120.4, 38.8)
        dlg.get_output_dir.return_value = "/out"
        dlg.want_dem.return_value = True
        dlg.want_canopy.return_value = True
        dlg.should_register.return_value = False
        MockProg.return_value.exec.return_value = QDialog.Rejected
        thread = MockThread.return_value

        ctrl.run_fetch()

    assert ctrl._register is False
    thread.start.assert_called_once()
    thread.cancel.assert_called_once()


def test_run_fetch_passes_default_output_dir_to_dialog(app):
    """The results folder is forwarded to the dialog as the output-field default."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    ctrl = TileFetchController(MagicMock(), MagicMock())
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox"):
        MockDlg.return_value.exec.return_value = QDialog.Rejected  # bail out early
        ctrl.run_fetch(default_output_dir="/results/mission1")

    _args, kwargs = MockDlg.call_args
    assert kwargs.get("default_output_dir") == "/results/mission1"


# --- 3DEP default gating (elevation already available) ---------------------

def _settings_with(values):
    """A settings mock whose get_setting reads from ``values`` (with defaults)."""
    settings = MagicMock()
    settings.get_setting.side_effect = lambda k, default='': values.get(k, default)
    return settings


def test_elevation_available_for_aws_terrain_tiles(app):
    """AWS Terrain Tiles (terrarium) is online -> elevation already available."""
    ctrl = TileFetchController(MagicMock(), _settings_with({'TerrainProviderId': 'terrarium'}))
    assert ctrl._elevation_already_available() is True


def test_elevation_available_when_provider_unset_defaults_to_terrarium(app):
    """Unset provider resolves to the Terrarium default -> available."""
    ctrl = TileFetchController(MagicMock(), _settings_with({}))
    assert ctrl._elevation_already_available() is True


def test_elevation_available_for_registered_local_3dep(app, tmp_path):
    """Local 3DEP with valid manifest+tiles paths (existing on disk) is usable."""
    manifest = tmp_path / "dem_manifest.csv"
    manifest.write_text("filename,minX,minY,maxX,maxY\n")
    ctrl = TileFetchController(MagicMock(), _settings_with({
        'TerrainProviderId': 'usgs_3dep_local',
        'Terrain3DEPManifestPath': str(manifest),
        'Terrain3DEPTilesDir': str(tmp_path)}))
    assert ctrl._elevation_already_available() is True


def test_elevation_not_available_when_3dep_files_missing(app, tmp_path):
    """Registered paths that dangle (moved/deleted results folder) are NOT a
    usable elevation source - the DEM download should default back on."""
    ctrl = TileFetchController(MagicMock(), _settings_with({
        'TerrainProviderId': 'usgs_3dep_local',
        'Terrain3DEPManifestPath': str(tmp_path / "gone" / "dem_manifest.csv"),
        'Terrain3DEPTilesDir': str(tmp_path / "gone")}))
    assert ctrl._elevation_already_available() is False


def test_elevation_not_available_for_3dep_without_paths(app):
    """Provider is 3DEP-local but paths unset: chosen, not yet obtained -> the
    download should default ON, so this reports not-available."""
    ctrl = TileFetchController(MagicMock(), _settings_with({
        'TerrainProviderId': 'usgs_3dep_local'}))
    assert ctrl._elevation_already_available() is False


def test_elevation_not_available_without_settings_service(app):
    """No settings service -> can't tell -> offer the download (default on)."""
    ctrl = TileFetchController(MagicMock(), None)
    assert ctrl._elevation_already_available() is False


def test_run_fetch_defaults_dem_off_when_elevation_available(app):
    """With AWS Terrain Tiles active, the dialog opens with 3DEP unchecked."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    ctrl = TileFetchController(MagicMock(), _settings_with({'TerrainProviderId': 'terrarium'}))
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox"):
        MockDlg.return_value.exec.return_value = QDialog.Rejected  # bail out early
        ctrl.run_fetch()

    assert MockDlg.call_args.kwargs.get("default_dem_checked") is False


def test_run_fetch_defaults_dem_on_when_no_usable_elevation(app):
    """Provider chosen as local 3DEP but not yet downloaded -> 3DEP checked."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    ctrl = TileFetchController(MagicMock(), _settings_with({
        'TerrainProviderId': 'usgs_3dep_local'}))
    with patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox"):
        MockDlg.return_value.exec.return_value = QDialog.Rejected
        ctrl.run_fetch()

    assert MockDlg.call_args.kwargs.get("default_dem_checked") is True


def test_on_fill_source_dispatches_to_fill_methods(app):
    """The dropdown's source key routes to the mission / folder fill logic."""
    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl._mission_images = [{"path": "a.jpg"}]
    ctrl._fill_aoi = MagicMock()
    ctrl._fill_from_folder = MagicMock()
    dialog = MagicMock()

    ctrl._on_fill_source(dialog, "mission")
    ctrl._fill_aoi.assert_called_once()
    ctrl._fill_from_folder.assert_not_called()

    ctrl._on_fill_source(dialog, "folder")
    ctrl._fill_from_folder.assert_called_once()

    # An unknown/placeholder key is a no-op.
    ctrl._fill_aoi.reset_mock()
    ctrl._fill_from_folder.reset_mock()
    ctrl._on_fill_source(dialog, None)
    ctrl._fill_aoi.assert_not_called()
    ctrl._fill_from_folder.assert_not_called()


# --- AOI coverage captions + coverage-aware DEM default ---------------------

from core.views.images.viewer.dialogs.TileFetchDialog import (  # noqa: E402
    TileFetchDialog,
    TileFetchDialog as _D,
)

_BOUNDS = (-120.5, 38.7, -120.4, 38.8)


def _probe(covers):
    p = MagicMock()
    p.covers.return_value = covers
    return p


def test_coverage_status_maps_covers_results(app):
    ctrl = TileFetchController(MagicMock(), MagicMock())
    assert ctrl._coverage_status(None, _BOUNDS) == _D.STATUS_UNREGISTERED
    assert ctrl._coverage_status(_probe('full'), _BOUNDS) == _D.STATUS_COVERED
    assert ctrl._coverage_status(_probe('partial'), _BOUNDS) == _D.STATUS_PARTIAL
    assert ctrl._coverage_status(_probe('none'), _BOUNDS) == _D.STATUS_NONE
    broken = MagicMock()
    broken.covers.side_effect = RuntimeError("no shapely")
    assert ctrl._coverage_status(broken, _BOUNDS) == _D.STATUS_UNKNOWN


def test_refresh_coverage_unknown_without_bounds(app):
    ctrl = TileFetchController(MagicMock(), MagicMock())
    dialog = TileFetchDialog()   # empty AOI fields
    ctrl._refresh_dialog_coverage(dialog)
    assert dialog.dem_status_label.isHidden()
    assert dialog.canopy_status_label.isHidden()


def test_refresh_coverage_sets_captions_and_defaults_covered(app):
    """Fully covered AOI: caption shown, DEM defaults off on fill events."""
    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl._coverage_probes = {'dem': _probe('full'), 'canopy': _probe('partial')}
    dialog = TileFetchDialog()
    dialog.set_aoi(_BOUNDS)
    dialog.dem_checkbox.setChecked(True)

    ctrl._refresh_dialog_coverage(dialog, apply_defaults=True)

    assert dialog.dem_checkbox.isChecked() is False
    assert "already covered" in dialog.dem_status_label.text()
    assert "Partially covered" in dialog.canopy_status_label.text()


def test_refresh_coverage_gap_turns_dem_on(app):
    """Registered local DEM with a coverage gap: DEM defaults ON (fills gaps)."""
    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl._coverage_probes = {'dem': _probe('partial'), 'canopy': None}
    dialog = TileFetchDialog()
    dialog.set_aoi(_BOUNDS)
    dialog.dem_checkbox.setChecked(False)

    ctrl._refresh_dialog_coverage(dialog, apply_defaults=True)

    assert dialog.dem_checkbox.isChecked() is True


def test_refresh_coverage_no_defaults_on_manual_edit(app):
    """apply_defaults=False (manual AOI edits) never flips checkboxes."""
    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl._coverage_probes = {'dem': _probe('full'), 'canopy': None}
    dialog = TileFetchDialog()
    dialog.set_aoi(_BOUNDS)
    dialog.dem_checkbox.setChecked(True)

    ctrl._refresh_dialog_coverage(dialog, apply_defaults=False)

    assert dialog.dem_checkbox.isChecked() is True    # untouched
    assert "already covered" in dialog.dem_status_label.text()


def test_refresh_coverage_canopy_defaults_off_when_covered(app):
    """Canopy is coverage-aware too: a fully-covered AOI defaults it OFF so the
    dialog doesn't nudge a redundant re-download (re-downloading is a
    deliberate refresh via re-checking the box)."""
    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl._coverage_probes = {'dem': _probe('full'), 'canopy': _probe('full')}
    dialog = TileFetchDialog()
    dialog.set_aoi(_BOUNDS)
    dialog.dem_checkbox.setChecked(True)
    dialog.canopy_checkbox.setChecked(True)

    ctrl._refresh_dialog_coverage(dialog, apply_defaults=True)

    # Everything covered -> both off. run_fetch's 'select at least one dataset'
    # guard then makes Download a no-op unless the user re-checks something.
    assert dialog.dem_checkbox.isChecked() is False
    assert dialog.canopy_checkbox.isChecked() is False


def test_refresh_coverage_canopy_on_when_gap(app):
    """Canopy has no online fallback, so a gap (partial/none) keeps it ON."""
    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl._coverage_probes = {'dem': None, 'canopy': _probe('partial')}
    dialog = TileFetchDialog()
    dialog.set_aoi(_BOUNDS)
    dialog.canopy_checkbox.setChecked(False)

    ctrl._refresh_dialog_coverage(dialog, apply_defaults=True)

    assert dialog.canopy_checkbox.isChecked() is True


def test_refresh_coverage_canopy_untouched_when_unregistered(app):
    """No canopy source configured (unregistered) -> leave the constructor
    default (on) so a first-time user is still encouraged to download it."""
    ctrl = TileFetchController(MagicMock(), MagicMock())
    ctrl._coverage_probes = {'dem': _probe('full'), 'canopy': None}
    dialog = TileFetchDialog()
    dialog.set_aoi(_BOUNDS)
    assert dialog.canopy_checkbox.isChecked() is True

    ctrl._refresh_dialog_coverage(dialog, apply_defaults=True)

    assert dialog.canopy_checkbox.isChecked() is True


def test_coverage_probes_built_from_settings_and_closed(app, tmp_path):
    """Probes come from the registered paths and are closed after run_fetch."""
    from unittest.mock import patch
    from PySide6.QtWidgets import QDialog

    manifest = tmp_path / "dem_manifest.csv"
    manifest.write_text("filename,minX,minY,maxX,maxY\n")
    settings = MagicMock()
    settings.get_setting.side_effect = lambda k, default='': {
        'Terrain3DEPManifestPath': str(manifest),
        'Terrain3DEPTilesDir': str(tmp_path),
    }.get(k, default)
    ctrl = TileFetchController(MagicMock(), settings)

    dem_probe = MagicMock()
    canopy_probe = MagicMock()
    with patch("core.services.terrain.USGS3DEPProvider.USGS3DEPProvider",
               return_value=dem_probe) as MockDem, \
         patch("core.services.terrain.CanopyServiceFactory.create_canopy_service",
               return_value=canopy_probe), \
         patch(f"{_MODULE}.TileFetchDialog") as MockDlg, \
         patch(f"{_MODULE}.QMessageBox"):
        dlg = MockDlg.return_value
        dlg.exec.return_value = QDialog.Rejected
        dlg.get_bounds.return_value = _BOUNDS
        ctrl.run_fetch()

    MockDem.assert_called_once_with(str(manifest), str(tmp_path))
    dem_probe.close.assert_called_once()
    canopy_probe.close.assert_called_once()
    assert ctrl._coverage_probes is None


def test_coverage_probe_skips_dangling_dem_paths(app, tmp_path):
    """Registered-but-missing 3DEP paths read as 'nothing registered'."""
    from unittest.mock import patch

    settings = MagicMock()
    settings.get_setting.side_effect = lambda k, default='': {
        'Terrain3DEPManifestPath': str(tmp_path / "gone" / "m.csv"),
        'Terrain3DEPTilesDir': str(tmp_path / "gone"),
    }.get(k, default)
    ctrl = TileFetchController(MagicMock(), settings)

    with patch("core.services.terrain.USGS3DEPProvider.USGS3DEPProvider") as MockDem, \
         patch("core.services.terrain.CanopyServiceFactory.create_canopy_service",
               return_value=None):
        probes = ctrl._get_coverage_probes()

    MockDem.assert_not_called()
    assert probes['dem'] is None


def test_coverage_probes_none_when_unregistered(app):
    settings = MagicMock()
    settings.get_setting.return_value = ''
    ctrl = TileFetchController(MagicMock(), settings)
    from unittest.mock import patch
    with patch("core.services.terrain.CanopyServiceFactory.create_canopy_service",
               return_value=None):
        probes = ctrl._get_coverage_probes()
    assert probes == {'dem': None, 'canopy': None}
