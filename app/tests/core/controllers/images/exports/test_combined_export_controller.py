"""Unit tests for CombinedExportController (combined PDF / KML / CalTopo)."""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from core.controllers.images.exports.CombinedExportController import (
    CombinedExportController,
    CombinedKmlExportThread,
    CombinedRunLoadThread,
)

_MODULE = "core.controllers.images.exports.CombinedExportController"


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def _result(xml_path):
    result = MagicMock()
    result.xml_path = xml_path
    return result


def _dialog(pdf=True, kml=False, caltopo=False, photos=True, include=False):
    dialog = MagicMock()
    dialog.exec.return_value = QDialog.Accepted
    dialog.should_export_pdf.return_value = pdf
    dialog.should_export_kml.return_value = kml
    dialog.should_export_caltopo.return_value = caltopo
    dialog.should_attach_caltopo_photos.return_value = caltopo and photos
    dialog.get_include_images_without_flagged_aois.return_value = include
    return dialog


class _Flow:
    """Patch every collaborator of CombinedExportController.export.

    Records the order the outputs ran in, so tests can assert the
    least-interactive-first sequencing.
    """

    def __init__(self, dialog, runs=None, save_paths=None):
        self.dialog = dialog
        self.runs = runs if runs is not None else [MagicMock()]
        self.save_paths = list(save_paths or [])
        self.order = []

    def __enter__(self):
        self._patches = [
            patch(f"{_MODULE}.CombinedExportDialog", return_value=self.dialog),
            patch(f"{_MODULE}.CombinedDetectionsService"),
            patch(f"{_MODULE}.SettingsService"),
            patch(f"{_MODULE}.CombinedPdfExportController"),
            patch(f"{_MODULE}.QFileDialog"),
            patch(f"{_MODULE}.QMessageBox"),
            patch.object(CombinedExportController, '_load_runs', return_value=self.runs),
            patch.object(CombinedExportController, '_export_kml',
                         side_effect=lambda *a: self.order.append('kml')),
            patch.object(CombinedExportController, '_export_caltopo',
                         side_effect=lambda *a: self.order.append('caltopo')),
        ]
        (_, self.service_cls, self.settings_cls, self.pdf_controller_cls, self.file_dialog,
         self.message_box, self.load_runs, self.export_kml, self.export_caltopo) = [
            p.start() for p in self._patches]
        self.file_dialog.getSaveFileName.side_effect = [(path, "") for path in self.save_paths]
        self.pdf_controller_cls.return_value.generate_combined_pdf.side_effect = (
            lambda *a, **k: self.order.append('pdf'))
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()


# ---------------------------------------------------------------------------
# Worker threads
# ---------------------------------------------------------------------------

def test_load_thread_emits_the_runs(app):
    service = MagicMock()
    service.load_runs.return_value = ['run']
    thread = CombinedRunLoadThread(service, ["/a.xml"])
    loaded = []
    thread.loaded.connect(loaded.append)

    thread.run()

    assert loaded == [['run']]
    service.load_runs.assert_called_once_with(["/a.xml"])


def test_load_thread_reports_errors(app):
    service = MagicMock()
    service.load_runs.side_effect = RuntimeError("bad xml")
    thread = CombinedRunLoadThread(service, ["/a.xml"])
    errors = []
    thread.errorOccurred.connect(errors.append)

    thread.run()

    assert errors == ["bad xml"]


def test_kml_thread_success_carries_the_summary(app):
    service = MagicMock()
    service.generate_kml.return_value = {'exported': 2, 'unplaced': 0}
    thread = CombinedKmlExportThread(service, "/out.kml", ['run'])
    outcomes = []
    thread.success.connect(outcomes.append)

    thread.run()

    assert outcomes == [{'exported': 2, 'unplaced': 0}]
    assert service.generate_kml.call_args.args == ("/out.kml", ['run'])


def test_kml_thread_cancel(app):
    service = MagicMock()

    def generate(path, runs, progress_callback=None, cancel_check=None):
        return None if cancel_check() else {'exported': 1, 'unplaced': 0}

    service.generate_kml.side_effect = generate
    thread = CombinedKmlExportThread(service, "/out.kml", [])
    outcomes = []
    thread.success.connect(lambda summary: outcomes.append('success'))
    thread.canceled.connect(lambda: outcomes.append('canceled'))

    thread.cancel()
    thread.run()

    assert outcomes == ['canceled']


def test_kml_thread_error(app):
    service = MagicMock()
    service.generate_kml.side_effect = OSError("disk full")
    thread = CombinedKmlExportThread(service, "/out.kml", [])
    errors = []
    thread.errorOccurred.connect(errors.append)

    thread.run()

    assert errors == ["disk full"]


# ---------------------------------------------------------------------------
# Export flow
# ---------------------------------------------------------------------------

def test_no_results_warns_and_returns_false(app):
    controller = CombinedExportController(None)
    with patch(f"{_MODULE}.QMessageBox") as MockBox, \
            patch(f"{_MODULE}.CombinedExportDialog") as MockDialog:
        assert controller.export([]) is False
    MockBox.warning.assert_called_once()
    MockDialog.assert_not_called()


def test_dialog_rejection_aborts(app):
    dialog = _dialog()
    dialog.exec.return_value = QDialog.Rejected
    with _Flow(dialog) as flow:
        assert CombinedExportController(None).export([_result("/a.xml")]) is False
    flow.load_runs.assert_not_called()
    flow.file_dialog.getSaveFileName.assert_not_called()


def test_pdf_only_skips_loading_and_builds_the_report(app):
    dialog = _dialog(pdf=True)
    session = MagicMock()
    with _Flow(dialog, save_paths=["/out/report.pdf"]) as flow:
        assert CombinedExportController(None).export(
            [_result("/a.xml")], recovery_session=session) is True

    flow.load_runs.assert_not_called()
    args = flow.pdf_controller_cls.return_value.generate_combined_pdf.call_args
    assert args.args == ("/out/report.pdf", ["/a.xml"], dialog)
    assert args.kwargs['recovery_session'] is session
    assert flow.order == ['pdf']


def test_pdf_save_cancel_aborts_when_nothing_else_is_chosen(app):
    with _Flow(_dialog(pdf=True), save_paths=[""]) as flow:
        assert CombinedExportController(None).export([_result("/a.xml")]) is False
    assert flow.order == []


def test_all_outputs_run_least_interactive_first(app):
    dialog = _dialog(pdf=True, kml=True, caltopo=True)
    with _Flow(dialog, save_paths=["/out/report.pdf", "/out/report.kml"]) as flow:
        assert CombinedExportController(None).export([_result("/a.xml")]) is True

    assert flow.order == ['kml', 'caltopo', 'pdf']
    # Both save locations are asked for before anything runs
    assert flow.file_dialog.getSaveFileName.call_count == 2


def test_kml_save_location_is_offered_beside_the_report(app):
    dialog = _dialog(pdf=True, kml=True)
    with _Flow(dialog, save_paths=["/out/report.pdf", "/out/report.kml"]) as flow:
        CombinedExportController(None).export([_result("/a.xml")])

    kml_prompt = flow.file_dialog.getSaveFileName.call_args_list[1]
    assert kml_prompt.args[2] == "/out/report.kml"
    assert "*.kmz" in kml_prompt.args[3]
    assert flow.export_kml.call_args.args[1] == "/out/report.kml"


def test_map_outputs_share_one_load_with_the_dialog_scope(app):
    dialog = _dialog(pdf=False, kml=True, caltopo=True, include=True)
    session = MagicMock()
    with _Flow(dialog, save_paths=["/out/d.kml"]) as flow:
        flow.settings_cls.return_value.get_bool_setting.return_value = False
        CombinedExportController(None).export([_result("/a.xml")], recovery_session=session)

    flow.load_runs.assert_called_once()
    kwargs = flow.service_cls.call_args.kwargs
    assert kwargs['include_images_without_flagged_aois'] is True
    assert kwargs['use_terrain_elevation'] is False
    assert kwargs['recovery_session'] is session
    caltopo_args = flow.export_caltopo.call_args.args
    assert caltopo_args[0] is flow.runs
    assert caltopo_args[1] is True  # attach the report photo


def test_nothing_in_scope_stops_before_any_save_prompt(app):
    dialog = _dialog(pdf=True, kml=True)
    with _Flow(dialog, runs=[]) as flow:
        assert CombinedExportController(None).export([_result("/a.xml")]) is False

    flow.message_box.information.assert_called_once()
    flow.file_dialog.getSaveFileName.assert_not_called()
    assert flow.order == []


def test_failed_load_stops_the_export(app):
    dialog = _dialog(pdf=True, caltopo=True)
    with _Flow(dialog, runs=None) as flow:
        flow.load_runs.return_value = None
        assert CombinedExportController(None).export([_result("/a.xml")]) is False
    assert flow.order == []


def test_caltopo_only_needs_no_save_location(app):
    with _Flow(_dialog(pdf=False, caltopo=True, photos=False)) as flow:
        assert CombinedExportController(None).export([_result("/a.xml")]) is True

    flow.file_dialog.getSaveFileName.assert_not_called()
    assert flow.order == ['caltopo']
    assert flow.export_caltopo.call_args.args[1] is False


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def _run_step_with_progress(controller, step, *args, emit=None):
    """Run a threaded step with the dialog and thread stubbed.

    Args:
        emit: callable(thread_mock) that fires the thread's outcome signal
            handler, standing in for the worker finishing.
    """
    with patch(f"{_MODULE}.ExportProgressDialog"), \
            patch(f"{_MODULE}.CombinedKmlExportThread") as MockKmlThread, \
            patch(f"{_MODULE}.CombinedRunLoadThread") as MockLoadThread, \
            patch(f"{_MODULE}.QMessageBox") as MockBox:
        for thread_cls in (MockKmlThread, MockLoadThread):
            thread_cls.return_value.start.side_effect = (
                lambda cls=thread_cls: emit(cls.return_value))
        return step(*args), MockBox


def _fire(signal_mock, *values):
    """Invoke the handler connected to a mocked signal."""
    handler = signal_mock.connect.call_args.args[0]
    handler(*values)


def test_load_runs_returns_the_loaded_runs(app):
    controller = CombinedExportController(None)
    result, box = _run_step_with_progress(
        controller, controller._load_runs, MagicMock(), ["/a.xml"],
        emit=lambda thread: _fire(thread.loaded, ['run']))
    assert result == ['run']
    box.critical.assert_not_called()


def test_load_runs_reports_errors(app):
    controller = CombinedExportController(None, logger=MagicMock())
    result, box = _run_step_with_progress(
        controller, controller._load_runs, MagicMock(), ["/a.xml"],
        emit=lambda thread: _fire(thread.errorOccurred, "bad xml"))
    assert result is None
    box.critical.assert_called_once()


def test_export_kml_reports_what_was_written(app):
    controller = CombinedExportController(None)
    result, box = _run_step_with_progress(
        controller, controller._export_kml, MagicMock(), "/out.kml", ['run'],
        emit=lambda thread: _fire(thread.success, {'exported': 4, 'unplaced': 1}))
    assert result is True
    message = box.information.call_args.args[2]
    assert "4" in message and "/out.kml" in message
    assert "1 AOI(s) were left out" in message


def test_export_kml_cancel_reports_nothing(app):
    controller = CombinedExportController(None)
    result, box = _run_step_with_progress(
        controller, controller._export_kml, MagicMock(), "/out.kml", ['run'],
        emit=lambda thread: None)
    assert result is False
    box.information.assert_not_called()
    box.critical.assert_not_called()


def test_export_caltopo_uses_the_chosen_sign_in_method(app):
    controller = CombinedExportController(None)
    with patch(f"{_MODULE}.CalTopoMethodDialog") as MockMethod, \
            patch(f"{_MODULE}.CombinedCalTopoExportController") as MockCalTopo:
        MockMethod.return_value.exec.return_value = QDialog.Accepted
        MockMethod.return_value.get_selected_method.return_value = 'api'
        MockCalTopo.return_value.export_detections.return_value = True

        assert controller._export_caltopo(['run'], True, False) is True

    assert MockCalTopo.call_args.args[1] == ['run']
    assert MockCalTopo.call_args.kwargs['use_terrain_elevation'] is False
    MockCalTopo.return_value.export_detections.assert_called_once_with('api', True)


def test_export_caltopo_method_cancel_exports_nothing(app):
    controller = CombinedExportController(None)
    with patch(f"{_MODULE}.CalTopoMethodDialog") as MockMethod, \
            patch(f"{_MODULE}.CombinedCalTopoExportController") as MockCalTopo:
        MockMethod.return_value.exec.return_value = QDialog.Rejected
        assert controller._export_caltopo(['run'], True, True) is False
    MockCalTopo.assert_not_called()
