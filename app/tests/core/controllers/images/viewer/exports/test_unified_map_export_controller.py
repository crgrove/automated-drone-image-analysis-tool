"""Unit tests for UnifiedMapExportController."""

import pytest
from unittest.mock import MagicMock, patch, call
from PySide6.QtWidgets import QDialog

from core.controllers.images.viewer.exports.UnifiedMapExportController import (
    UnifiedMapExportController,
    UnifiedMapExportThread,
    CoveragePodExportThread,
)


def _parent():
    parent = MagicMock()
    parent.images = [
        {"path": "a.jpg", "hidden": False, "areas_of_interest": [{"id": 1}], "name": "A"},
        {"path": "b.jpg", "hidden": False, "areas_of_interest": [{"id": 2}], "name": "B"},
    ]
    parent.aoi_controller.flagged_aois = {0: {0}}
    parent.altitude_controller.get_effective_altitude.return_value = None
    parent.use_terrain_elevation = True
    parent.status_controller = MagicMock()
    return parent


@pytest.fixture
def controller():
    return UnifiedMapExportController(_parent())


# ---------------------------------------------------------------------------
# Thread behavior
# ---------------------------------------------------------------------------

def test_thread_cancel_sets_flag():
    thread = UnifiedMapExportThread(
        MagicMock(), MagicMock(), [], {},
        include_locations=False,
        include_images_without_flagged_aois=False,
        include_flagged_aois=False,
        include_coverage=False,
        output_path="/out.kml",
    )
    assert thread.is_cancelled() is False
    thread.cancel()
    assert thread.is_cancelled() is True


def test_thread_emits_finished_when_nothing_to_do():
    kml_service = MagicMock()
    thread = UnifiedMapExportThread(
        kml_service, MagicMock(),
        [{"path": "a.jpg", "hidden": False}],
        {},
        include_locations=False,
        include_images_without_flagged_aois=False,
        include_flagged_aois=False,
        include_coverage=False,
        output_path="/out.kml",
    )
    received = []
    thread.finished.connect(lambda: received.append(True))
    thread.run()
    assert received == [True]
    kml_service.save_kml.assert_called_once_with("/out.kml")


def test_thread_emits_error_on_exception():
    kml_service = MagicMock()
    kml_service.generate_image_locations_kml.side_effect = RuntimeError("fail")
    thread = UnifiedMapExportThread(
        kml_service, MagicMock(),
        [{"path": "a.jpg", "hidden": False}],
        {},
        include_locations=True,
        include_images_without_flagged_aois=True,
        include_flagged_aois=False,
        include_coverage=False,
        output_path="/out.kml",
    )
    errors = []
    thread.errorOccurred.connect(lambda msg: errors.append(msg))
    thread.run()
    assert len(errors) == 1
    assert "fail" in errors[0]


def test_thread_location_filter_skips_hidden_images():
    kml_service = MagicMock()
    thread = UnifiedMapExportThread(
        kml_service, MagicMock(),
        [
            {"path": "a.jpg", "hidden": True},
            {"path": "b.jpg", "hidden": False},
        ],
        {1: {0}},
        include_locations=True,
        include_images_without_flagged_aois=False,
        include_flagged_aois=False,
        include_coverage=False,
        output_path="/out.kml",
    )
    thread.run()
    # Only non-hidden image with flagged aoi should have been passed
    call_images = kml_service.generate_image_locations_kml.call_args[0][0]
    assert all(not img.get("hidden") for img in call_images)


# ---------------------------------------------------------------------------
# Controller callbacks
# ---------------------------------------------------------------------------

def test_on_progress_updated_forwards(controller):
    controller.progress_dialog = MagicMock()
    controller._on_progress_updated(1, 10, "msg")
    controller.progress_dialog.update_progress.assert_called_once_with(1, 10, "msg")


def test_on_export_finished_shows_toast(controller):
    controller.progress_dialog = MagicMock()
    controller._on_export_finished()
    controller.progress_dialog.accept.assert_called_once()
    controller.parent.status_controller.show_toast.assert_called_once()


def test_on_export_cancelled_terminates_thread(controller):
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True
    controller.export_thread = MagicMock()
    controller.export_thread.isRunning.return_value = True

    controller._on_export_cancelled()

    controller.export_thread.terminate.assert_called_once()
    controller.export_thread.wait.assert_called_once()
    controller.progress_dialog.reject.assert_called_once()


def test_on_export_error_shows_critical(controller):
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QMessageBox"
    ) as MockQMB:
        controller._on_export_error("boom")

    MockQMB.critical.assert_called_once()


# ---------------------------------------------------------------------------
# show_export_dialog flow: selection validation
# ---------------------------------------------------------------------------

def test_show_export_dialog_cancelled_by_user(controller):
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog:
        MockDialog.return_value.exec.return_value = QDialog.Rejected
        controller.show_export_dialog()


def test_show_export_dialog_no_data_selected_warns(controller):
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QMessageBox"
    ) as MockQMB:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "kml"
        d.should_include_locations.return_value = False
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = False
        d.should_show_pod_on_map.return_value = False
        d.should_include_images.return_value = False

        controller.show_export_dialog()

    MockQMB.warning.assert_called_once()


def test_show_export_dialog_kml_export_calls_kml_method(controller):
    controller._export_to_kml = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "kml"
        d.should_include_locations.return_value = True
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = False
        d.should_show_pod_on_map.return_value = False

        controller.show_export_dialog()

    controller._export_to_kml.assert_called_once()


def test_show_export_dialog_caltopo_method_cancelled(controller):
    controller._export_to_caltopo = MagicMock()
    controller._export_to_caltopo_via_api = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.CalTopoMethodDialog"
    ) as MockMethod:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "caltopo"
        d.should_include_locations.return_value = True
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = False
        d.should_show_pod_on_map.return_value = False
        d.should_include_images.return_value = True
        MockMethod.return_value.exec.return_value = QDialog.Rejected

        controller.show_export_dialog()

    controller._export_to_caltopo.assert_not_called()
    controller._export_to_caltopo_via_api.assert_not_called()


def test_show_export_dialog_caltopo_api_path(controller):
    controller._export_to_caltopo_via_api = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.CalTopoMethodDialog"
    ) as MockMethod:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "caltopo"
        d.should_include_locations.return_value = True
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = False
        d.should_show_pod_on_map.return_value = False
        d.should_include_images.return_value = True
        MockMethod.return_value.exec.return_value = QDialog.Accepted
        MockMethod.return_value.get_selected_method.return_value = "api"

        controller.show_export_dialog()

    controller._export_to_caltopo_via_api.assert_called_once()


def test_show_export_dialog_caltopo_browser_path(controller):
    controller._export_to_caltopo = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.CalTopoMethodDialog"
    ) as MockMethod:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "caltopo"
        d.should_include_locations.return_value = True
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = False
        d.should_show_pod_on_map.return_value = False
        d.should_include_images.return_value = True
        MockMethod.return_value.exec.return_value = QDialog.Accepted
        MockMethod.return_value.get_selected_method.return_value = "browser"

        controller.show_export_dialog()

    controller._export_to_caltopo.assert_called_once()


def test_export_to_kml_file_dialog_cancelled(controller):
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QFileDialog"
    ) as MockFile:
        MockFile.getSaveFileName.return_value = ("", "")
        assert controller._export_to_kml(True, False, True, False) is None


# ---------------------------------------------------------------------------
# POD pass: standalone thread + controller wiring
# ---------------------------------------------------------------------------

def test_pod_dir_for_kml():
    import os
    d = UnifiedMapExportController._pod_dir_for_kml(os.path.join("out", "mission.kml"))
    assert d == os.path.join("out", "mission_coverage_pod")


def _make_result(cancelled=False, skipped=None, image_count=1,
                 dem_fallback_frames=0, stats=None, canopy_coverage_fraction=None):
    r = MagicMock()
    r.cancelled = cancelled
    # Real values: _pod_completion_summary iterates skipped and does arithmetic.
    r.skipped = skipped if skipped is not None else []
    r.image_count = image_count
    r.dem_fallback_frames = dem_fallback_frames
    r.canopy_coverage_fraction = canopy_coverage_fraction
    r.stats = stats if stats is not None else {}
    return r


def test_pod_thread_completes_and_writes(tmp_path):
    pod_service = MagicMock()
    result = _make_result(cancelled=False)
    pod_service.calculate.return_value = result
    thread = CoveragePodExportThread(pod_service, [{"path": "a"}], str(tmp_path))

    completed, finished = [], []
    thread.podCompleted.connect(lambda r: completed.append(r))
    thread.finished.connect(lambda: finished.append(True))
    with patch(
        "core.services.coverage.writers.write_all_outputs"
    ) as mock_write:
        thread.run()

    # calculate was driven with progress + cancel plumbing.
    assert pod_service.calculate.called
    _, kwargs = pod_service.calculate.call_args
    assert "progress_callback" in kwargs and "cancel_check" in kwargs
    mock_write.assert_called_once()
    assert completed == [result]
    assert finished == [True]


def test_pod_thread_cancelled_result_does_not_write(tmp_path):
    pod_service = MagicMock()
    pod_service.calculate.return_value = _make_result(cancelled=True)
    thread = CoveragePodExportThread(pod_service, [], str(tmp_path))

    canceled, completed = [], []
    thread.canceled.connect(lambda: canceled.append(True))
    thread.podCompleted.connect(lambda r: completed.append(r))
    with patch("core.services.coverage.writers.write_all_outputs") as mock_write:
        thread.run()

    assert canceled == [True]
    assert completed == []
    mock_write.assert_not_called()


def test_pod_thread_emits_error(tmp_path):
    pod_service = MagicMock()
    pod_service.calculate.side_effect = RuntimeError("kaboom")
    thread = CoveragePodExportThread(pod_service, [], str(tmp_path))
    errors = []
    thread.errorOccurred.connect(lambda m: errors.append(m))
    thread.run()
    assert len(errors) == 1 and "kaboom" in errors[0]


def test_on_pod_completed_populates_cache_with_fingerprint(controller):
    """The cached result carries the terrain/canopy config fingerprint so a
    later source change can mark it stale."""
    controller.parent.pod_result_cache = MagicMock()
    controller.parent.settings_service.get_setting.side_effect = \
        lambda k, default='': {'TerrainProviderId': 'usgs_3dep_local'}.get(k, '')
    result = _make_result()
    controller._on_pod_completed(result)
    args = controller.parent.pod_result_cache.set_result.call_args.args
    assert args[0] is result
    assert isinstance(args[1], str) and 'usgs_3dep_local' in args[1]


def test_run_pod_public_wrapper_delegates(controller):
    """run_pod (the GPS-map entry point) drives the same POD flow as Map Export."""
    controller._run_pod_export = MagicMock()
    controller.run_pod("C:/results/coverage_pod")
    controller._run_pod_export.assert_called_once_with("C:/results/coverage_pod", True)
    controller._run_pod_export.reset_mock()
    controller.run_pod("C:/results/coverage_pod", show_on_map=False)
    controller._run_pod_export.assert_called_once_with("C:/results/coverage_pod", False)


def test_pod_only_export_is_valid(controller):
    """A POD-only selection must pass validation and trigger the POD pass."""
    controller._export_to_kml = MagicMock(return_value="C:/tmp/mission.kml")
    controller._run_pod_export = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QMessageBox"
    ) as MockQMB:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "kml"
        d.should_include_locations.return_value = False
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = True
        d.should_show_pod_on_map.return_value = True

        controller.show_export_dialog()

    MockQMB.warning.assert_not_called()
    controller._run_pod_export.assert_called_once()


# ---------------------------------------------------------------------------
# POD controller slots: error / cancel / finished-show-on-map
# ---------------------------------------------------------------------------

def test_on_pod_error_rejects_dialog_logs_and_shows_critical(controller):
    """_on_pod_error rejects the visible dialog, logs, and shows a critical box."""
    controller.logger = MagicMock()
    controller.pod_progress_dialog = MagicMock()
    controller.pod_progress_dialog.isVisible.return_value = True
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QMessageBox"
    ) as MockQMB:
        controller._on_pod_error("boom")

    controller.pod_progress_dialog.reject.assert_called_once()
    controller.logger.error.assert_called_once()
    assert "boom" in controller.logger.error.call_args[0][0]
    MockQMB.critical.assert_called_once()


def test_on_pod_error_skips_reject_when_not_visible(controller):
    """When the dialog is not visible, no reject() is issued but critical still shows."""
    controller.logger = MagicMock()
    controller.pod_progress_dialog = MagicMock()
    controller.pod_progress_dialog.isVisible.return_value = False
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QMessageBox"
    ) as MockQMB:
        controller._on_pod_error("boom")

    controller.pod_progress_dialog.reject.assert_not_called()
    MockQMB.critical.assert_called_once()


def test_on_pod_cancelled_terminates_thread_rejects_and_toasts(controller):
    """_on_pod_cancelled terminates+waits the running thread, rejects, and toasts."""
    controller.pod_thread = MagicMock()
    controller.pod_thread.isRunning.return_value = True
    controller.pod_progress_dialog = MagicMock()
    controller.pod_progress_dialog.isVisible.return_value = True

    controller._on_pod_cancelled()

    controller.pod_thread.terminate.assert_called_once()
    controller.pod_thread.wait.assert_called_once()
    controller.pod_progress_dialog.reject.assert_called_once()
    controller.parent.status_controller.show_toast.assert_called_once()


def test_on_pod_cancelled_no_terminate_when_thread_not_running(controller):
    """A non-running thread is not terminated, but the dialog/toast still resolve."""
    controller.pod_thread = MagicMock()
    controller.pod_thread.isRunning.return_value = False
    controller.pod_progress_dialog = MagicMock()
    controller.pod_progress_dialog.isVisible.return_value = True

    controller._on_pod_cancelled()

    controller.pod_thread.terminate.assert_not_called()
    controller.pod_thread.wait.assert_not_called()
    controller.pod_progress_dialog.reject.assert_called_once()
    controller.parent.status_controller.show_toast.assert_called_once()


def test_on_pod_finished_shows_on_map_when_requested(controller):
    """When a pending result exists and show-on-map was requested, the overlay is shown."""
    controller.pod_progress_dialog = MagicMock()
    controller._pending_pod_result = _make_result()
    controller._show_pod_on_map_requested = True

    gmc = MagicMock()
    controller.parent.gps_map_controller = gmc

    controller._on_pod_finished()

    controller.pod_progress_dialog.accept.assert_called_once()
    controller.parent.status_controller.show_toast.assert_called_once()
    # show_map() must be called before enable_pod_overlay().
    assert gmc.mock_calls == [call.show_map(), call.enable_pod_overlay()]
    # Pending result is cleared after handling.
    assert controller._pending_pod_result is None


def test_on_pod_finished_no_map_when_not_requested(controller):
    """With show-on-map not requested, the overlay is left untouched."""
    controller.pod_progress_dialog = MagicMock()
    controller._pending_pod_result = _make_result()
    controller._show_pod_on_map_requested = False

    gmc = MagicMock()
    controller.parent.gps_map_controller = gmc

    controller._on_pod_finished()

    gmc.show_map.assert_not_called()
    gmc.enable_pod_overlay.assert_not_called()
    assert controller._pending_pod_result is None


def test_on_pod_finished_no_map_when_no_pending_result(controller):
    """Without a pending result, the overlay is not shown even if requested."""
    controller.pod_progress_dialog = MagicMock()
    controller._pending_pod_result = None
    controller._show_pod_on_map_requested = True

    gmc = MagicMock()
    controller.parent.gps_map_controller = gmc

    controller._on_pod_finished()

    gmc.show_map.assert_not_called()
    gmc.enable_pod_overlay.assert_not_called()


# ---------------------------------------------------------------------------
# CalTopo branch of show_export_dialog with include_pod
# ---------------------------------------------------------------------------

def test_show_export_dialog_caltopo_with_pod_folder_chosen(controller):
    """CalTopo + POD: a chosen folder starts the POD export with that directory."""
    controller._export_to_caltopo = MagicMock()
    controller._run_pod_export = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.CalTopoMethodDialog"
    ) as MockMethod, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QFileDialog"
    ) as MockFile:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "caltopo"
        d.should_include_locations.return_value = True
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = True
        d.should_show_pod_on_map.return_value = True
        d.should_include_images.return_value = True
        MockMethod.return_value.exec.return_value = QDialog.Accepted
        MockMethod.return_value.get_selected_method.return_value = "browser"
        MockFile.getExistingDirectory.return_value = "/pod/folder"

        controller.show_export_dialog()

    controller._export_to_caltopo.assert_called_once()
    controller._run_pod_export.assert_called_once_with("/pod/folder", True)


def test_show_export_dialog_caltopo_with_pod_folder_cancelled(controller):
    """CalTopo + POD: an empty folder selection does not start the POD export."""
    controller._export_to_caltopo = MagicMock()
    controller._run_pod_export = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.CalTopoMethodDialog"
    ) as MockMethod, patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.QFileDialog"
    ) as MockFile:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "caltopo"
        d.should_include_locations.return_value = True
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = True
        d.should_show_pod_on_map.return_value = False
        d.should_include_images.return_value = True
        MockMethod.return_value.exec.return_value = QDialog.Accepted
        MockMethod.return_value.get_selected_method.return_value = "browser"
        MockFile.getExistingDirectory.return_value = ""

        controller.show_export_dialog()

    controller._export_to_caltopo.assert_called_once()
    controller._run_pod_export.assert_not_called()


# ---------------------------------------------------------------------------
# POD overlay embedding in the exported KML/KMZ
# ---------------------------------------------------------------------------

_BOX = {"north": 30.66, "south": 30.65, "east": -97.95, "west": -97.96}


def _controller_with_kml_context(tmp_path, target_name="export.kml"):
    ctrl = UnifiedMapExportController(_parent())
    ctrl._kml_pod_target = str(tmp_path / target_name)
    ctrl._last_kml_service = MagicMock()
    ctrl._pod_last_output_dir = str(tmp_path / "export_coverage_pod")
    return ctrl


def test_on_pod_finished_embeds_overlay_for_kml_export(tmp_path):
    """A KML export with POD gets the heatmap embedded and the file re-saved."""
    ctrl = _controller_with_kml_context(tmp_path)
    kml_service = ctrl._last_kml_service
    kml_path = ctrl._kml_pod_target
    ctrl.pod_progress_dialog = MagicMock()
    result = _make_result()
    result.stats = {"mean_pod_covered": 0.62}
    ctrl._pending_pod_result = result
    ctrl._show_pod_on_map_requested = False

    with patch("core.services.coverage.writers.write_pod_overlay_png",
               return_value=_BOX) as mock_png:
        ctrl._on_pod_finished()

    mock_png.assert_called_once()
    png_path = mock_png.call_args.args[1]
    assert png_path.endswith("pod_overlay.png")
    kml_service.add_pod_overlay.assert_called_once()
    kwargs = kml_service.add_pod_overlay.call_args.kwargs
    assert kwargs["packed"] is False
    # Relative sidecar href, forward slashes, pointing into the POD folder.
    assert kwargs["href"] == "export_coverage_pod/pod_overlay.png"
    assert "62" in kwargs["description"]
    kml_service.save_kml.assert_called_once_with(kml_path)
    assert ctrl._kml_pod_target is None   # one-shot


def test_on_pod_finished_packs_overlay_for_kmz_export(tmp_path):
    """A .kmz target packs the PNG into the archive instead of a sidecar href."""
    ctrl = _controller_with_kml_context(tmp_path, target_name="export.kmz")
    kml_service = ctrl._last_kml_service
    ctrl.pod_progress_dialog = MagicMock()
    ctrl._pending_pod_result = _make_result()
    ctrl._show_pod_on_map_requested = False

    with patch("core.services.coverage.writers.write_pod_overlay_png",
               return_value=_BOX):
        ctrl._on_pod_finished()

    kwargs = kml_service.add_pod_overlay.call_args.kwargs
    assert kwargs["packed"] is True
    assert kwargs["href"] is None


def test_on_pod_finished_no_embed_without_kml_context(controller):
    """POD runs launched outside a KML export (map button, CalTopo) do not embed."""
    controller.pod_progress_dialog = MagicMock()
    controller._pending_pod_result = _make_result()
    controller._show_pod_on_map_requested = False
    controller._kml_pod_target = None
    controller._last_kml_service = MagicMock()

    with patch("core.services.coverage.writers.write_pod_overlay_png") as mock_png:
        controller._on_pod_finished()

    mock_png.assert_not_called()
    controller._last_kml_service.add_pod_overlay.assert_not_called()


def test_embed_failure_warns_but_leaves_export_intact(tmp_path):
    """An embedding failure warns (products still on disk) and never raises."""
    ctrl = _controller_with_kml_context(tmp_path)
    ctrl.pod_progress_dialog = MagicMock()
    ctrl._pending_pod_result = _make_result()
    ctrl._show_pod_on_map_requested = False

    with patch("core.services.coverage.writers.write_pod_overlay_png",
               side_effect=RuntimeError("reproject failed")), \
         patch("core.controllers.images.viewer.exports.UnifiedMapExportController.QMessageBox") as mb:
        ctrl._on_pod_finished()   # must not raise

    mb.warning.assert_called_once()
    assert "reproject failed" in mb.warning.call_args.args[2]
    ctrl._last_kml_service.save_kml.assert_not_called()


def test_pod_cancel_and_error_clear_kml_embed_target(tmp_path):
    """A cancelled or failed POD pass must not leave a stale embed target that
    a later, unrelated POD run would then write into the old KML."""
    for trigger in ("cancel", "error"):
        ctrl = _controller_with_kml_context(tmp_path)
        ctrl.pod_thread = MagicMock()
        ctrl.pod_thread.isRunning.return_value = False
        ctrl.pod_progress_dialog = MagicMock()
        ctrl.pod_progress_dialog.isVisible.return_value = False
        with patch("core.controllers.images.viewer.exports.UnifiedMapExportController.QMessageBox"):
            if trigger == "cancel":
                ctrl._on_pod_cancelled()
            else:
                ctrl._on_pod_error("boom")
        assert ctrl._kml_pod_target is None, trigger


def test_export_dialog_kml_with_pod_sets_embed_target(controller, tmp_path):
    """The KML+POD flow arms the embed target with the chosen file path."""
    kml_path = str(tmp_path / "out.kml")
    controller._export_to_kml = MagicMock(return_value=kml_path)
    controller._run_pod_export = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.UnifiedMapExportController.MapExportDialog"
    ) as MockDialog:
        d = MockDialog.return_value
        d.exec.return_value = QDialog.Accepted
        d.get_export_type.return_value = "kml"
        d.should_include_locations.return_value = True
        d.should_include_images_without_flagged_aois.return_value = False
        d.should_include_flagged_aois.return_value = False
        d.should_include_coverage.return_value = False
        d.should_include_pod.return_value = True
        d.should_show_pod_on_map.return_value = False

        controller.show_export_dialog()

    assert controller._kml_pod_target == kml_path
    controller._run_pod_export.assert_called_once()


# ---------------------------------------------------------------------------
# Honest POD completion summary
# ---------------------------------------------------------------------------

def test_pod_summary_clean_run_is_green(controller):
    msg, color = controller._pod_completion_summary(_make_result())
    assert msg == "POD coverage complete"
    assert color == "#00C853"


def test_pod_summary_none_result_is_generic_green(controller):
    msg, color = controller._pod_completion_summary(None)
    assert msg == "POD coverage complete"
    assert color == "#00C853"


def test_pod_summary_hidden_skips_do_not_degrade(controller):
    """User-hidden frames are a choice, not a data problem."""
    result = _make_result(skipped=[("a.jpg", "hidden")], image_count=5)
    msg, color = controller._pod_completion_summary(result)
    assert color == "#00C853"


def test_pod_summary_reports_skipped_and_no_dem_counts(controller):
    result = _make_result(
        skipped=[("a.jpg", "no_dem"), ("b.jpg", "no_dem_at_nadir"),
                 ("c.jpg", "no_pose"), ("d.jpg", "hidden")],
        image_count=7)
    msg, color = controller._pod_completion_summary(result)
    assert color == "#FFA726"
    assert "3 of 10 frames skipped" in msg
    assert "(2 without elevation data)" in msg


def test_pod_summary_mentions_fallback_on_clean_run(controller):
    result = _make_result(dem_fallback_frames=4)
    msg, color = controller._pod_completion_summary(result)
    assert color == "#00C853"
    assert "4" in msg and "online" in msg


def test_on_pod_finished_toasts_summary(controller):
    """The toast shows the computed summary, not an unconditional 'complete'."""
    controller.pod_progress_dialog = MagicMock()
    controller._pending_pod_result = _make_result(
        skipped=[("a.jpg", "no_dem")], image_count=1)
    controller._show_pod_on_map_requested = False

    controller._on_pod_finished()

    args, kwargs = controller.parent.status_controller.show_toast.call_args
    assert "skipped" in args[0]
    assert kwargs.get("color") == "#FFA726"


# ---------------------------------------------------------------------------
# POD runs over the full flight set, not just AOI images (coverage semantics)
# ---------------------------------------------------------------------------

def test_pod_image_set_uses_full_flight_when_available(controller):
    """POD coverage must consider every captured image, not just the AOI
    subset in the result XML."""
    controller.parent.images = [
        {'path': '/f/a.jpg', 'name': 'a', 'bearing': 90, 'areas_of_interest': [{}]},
    ]
    controller.parent.source_images = [
        {'path': '/f/a.jpg', 'name': 'a', 'has_aoi': True},
        {'path': '/f/b.jpg', 'name': 'b', 'has_aoi': False},
        {'path': '/f/c.jpg', 'name': 'c', 'has_aoi': False},
    ]
    pod_images = controller._pod_image_set()
    assert [im.get('path') for im in pod_images] == ['/f/a.jpg', '/f/b.jpg', '/f/c.jpg']
    # The AOI image keeps its rich dict (bearing preserved); source-only images
    # are minimal {path, name}.
    assert pod_images[0].get('bearing') == 90
    assert pod_images[1] == {'path': '/f/b.jpg', 'name': 'b'}


def test_pod_image_set_falls_back_to_aoi_subset_without_source(controller):
    controller.parent.images = [{'path': '/f/a.jpg', 'name': 'a'}]
    controller.parent.source_images = None
    assert controller._pod_image_set() == [{'path': '/f/a.jpg', 'name': 'a'}]


def test_run_pod_export_passes_full_flight_set(controller):
    """_run_pod_export hands the full flight set (not parent.images) to the
    POD thread and sizes the progress bar to it."""
    from unittest.mock import patch

    controller.parent.images = [{'path': '/f/a.jpg', 'name': 'a'}]
    controller.parent.source_images = [
        {'path': '/f/a.jpg', 'name': 'a', 'has_aoi': True},
        {'path': '/f/b.jpg', 'name': 'b', 'has_aoi': False},
    ]
    _mod = "core.controllers.images.viewer.exports.UnifiedMapExportController"
    with patch.object(controller, '_build_pod_service', return_value=MagicMock()), \
         patch(f"{_mod}.CoveragePodExportThread") as MockThread, \
         patch(f"{_mod}.ExportProgressDialog") as MockProg, \
         patch(f"{_mod}.QApplication"):
        MockProg.return_value.exec.return_value = QDialog.Accepted
        controller._run_pod_export("/out", show_on_map=False)

    passed_images = MockThread.call_args.args[1]
    assert [im.get('path') for im in passed_images] == ['/f/a.jpg', '/f/b.jpg']


# ---------------------------------------------------------------------------
# POD completion: canopy-coverage note
# ---------------------------------------------------------------------------

def test_pod_summary_notes_partial_canopy_coverage(controller):
    """A canopy source that didn't cover the whole searched area is surfaced
    (missing canopy silently overstates POD there)."""
    result = _make_result(canopy_coverage_fraction=0.78)
    msg, _color = controller._pod_completion_summary(result)
    assert "canopy data covered 78% of the searched area" in msg


def test_pod_summary_no_canopy_note_when_fully_covered(controller):
    result = _make_result(canopy_coverage_fraction=1.0)
    msg, color = controller._pod_completion_summary(result)
    assert "canopy" not in msg
    assert color == "#00C853"


def test_pod_summary_no_canopy_note_when_unconfigured(controller):
    result = _make_result(canopy_coverage_fraction=None)
    msg, _color = controller._pod_completion_summary(result)
    assert "canopy" not in msg


def test_pod_summary_canopy_note_combines_with_skips(controller):
    """The canopy note appends to an amber skip summary too."""
    result = _make_result(skipped=[("a.jpg", "no_dem")], image_count=1,
                          canopy_coverage_fraction=0.5)
    msg, color = controller._pod_completion_summary(result)
    assert color == "#FFA726"
    assert "skipped" in msg
    assert "canopy data covered 50% of the searched area" in msg
