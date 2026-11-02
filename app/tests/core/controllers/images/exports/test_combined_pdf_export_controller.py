"""Unit tests for CombinedPdfExportController."""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from core.controllers.images.exports.CombinedPdfExportController import (
    CombinedPdfExportController,
    CombinedPdfGenerationThread,
)

_MODULE = "core.controllers.images.exports.CombinedPdfExportController"


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def _result(xml_path):
    result = MagicMock()
    result.xml_path = xml_path
    return result


# ---------------------------------------------------------------------------
# Worker thread
# ---------------------------------------------------------------------------

def test_thread_success_runs_service(app):
    service = MagicMock()
    thread = CombinedPdfGenerationThread(service, "/out.pdf", ["/a.xml"])
    outcomes = []
    thread.success.connect(lambda: outcomes.append('success'))
    thread.errorOccurred.connect(lambda m: outcomes.append(('error', m)))

    thread.run()

    assert outcomes == ['success']
    kwargs = service.generate_combined_report.call_args
    assert kwargs.args[0] == "/out.pdf"
    assert kwargs.args[1] == ["/a.xml"]


def test_thread_error_is_reported(app):
    service = MagicMock()
    service.generate_combined_report.side_effect = RuntimeError("boom")
    thread = CombinedPdfGenerationThread(service, "/out.pdf", ["/a.xml"])
    errors = []
    thread.errorOccurred.connect(errors.append)

    thread.run()

    assert errors == ["boom"]


def test_thread_cancel_emits_canceled(app):
    service = MagicMock()
    thread = CombinedPdfGenerationThread(service, "/out.pdf", ["/a.xml"])
    outcomes = []
    thread.success.connect(lambda: outcomes.append('success'))
    thread.canceled.connect(lambda: outcomes.append('canceled'))

    thread.cancel()
    thread.run()

    assert outcomes == ['canceled']


# ---------------------------------------------------------------------------
# Controller flow
# ---------------------------------------------------------------------------

def test_generate_runs_the_build_behind_a_progress_dialog(app):
    controller = CombinedPdfExportController(None)
    options = MagicMock()
    session = MagicMock()
    with patch(f"{_MODULE}.ExportProgressDialog") as MockProgress, \
            patch(f"{_MODULE}.CombinedPdfGenerationThread") as MockThread, \
            patch(f"{_MODULE}.SettingsService"), \
            patch(f"{_MODULE}.CombinedPdfReportService") as MockService:
        MockProgress.return_value.exec.return_value = QDialog.Accepted
        started = controller.generate_combined_pdf(
            "/out.pdf", ["/a.xml"], options, recovery_session=session)

    assert started is True
    assert MockThread.call_args.args[1:] == ("/out.pdf", ["/a.xml"])
    MockThread.return_value.start.assert_called_once()
    MockThread.return_value.cancel.assert_not_called()
    assert MockService.call_args.kwargs['recovery_session'] is session


def test_generate_cancel_stops_the_build(app):
    controller = CombinedPdfExportController(None)
    with patch(f"{_MODULE}.ExportProgressDialog") as MockProgress, \
            patch(f"{_MODULE}.CombinedPdfGenerationThread") as MockThread, \
            patch(f"{_MODULE}.SettingsService"), \
            patch(f"{_MODULE}.CombinedPdfReportService"):
        MockProgress.return_value.exec.return_value = QDialog.Rejected
        controller.generate_combined_pdf("/out.pdf", ["/a.xml"], MagicMock())

    MockThread.return_value.cancel.assert_called_once()


def test_generate_reports_a_failure_to_start(app):
    controller = CombinedPdfExportController(None)
    with patch(f"{_MODULE}.SettingsService", side_effect=RuntimeError("no settings")), \
            patch(f"{_MODULE}.QMessageBox") as MockBox:
        assert controller.generate_combined_pdf("/out.pdf", ["/a.xml"], MagicMock()) is False
    MockBox.critical.assert_called_once()


def test_build_service_reads_preferences(app):
    controller = CombinedPdfExportController(None)
    dialog = MagicMock()
    dialog.get_organization.return_value = "TEXSAR"
    dialog.get_search_name.return_value = "Search 1"
    dialog.get_include_images_without_flagged_aois.return_value = True
    dialog.get_map_tile_source.return_value = "satellite"

    fake_settings = MagicMock()
    fake_settings.get_setting.side_effect = lambda key, default=None: {
        'DistanceUnit': 'Meters',
        'PositionFormat': 'UTM',
    }.get(key, default)
    fake_settings.get_bool_setting.return_value = False

    with patch(f"{_MODULE}.SettingsService", return_value=fake_settings):
        service = controller._build_service(dialog)

    assert service.organization == "TEXSAR"
    assert service.search_name == "Search 1"
    assert service.include_images_without_flagged_aois is True
    assert service.map_tile_source == "satellite"
    assert service.distance_unit == 'm'
    assert service.position_format == 'UTM'
    assert service.use_terrain_elevation is False
