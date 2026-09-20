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

def test_no_results_warns_and_returns_false(app):
    controller = CombinedPdfExportController(None)
    with patch(f"{_MODULE}.QMessageBox") as MockBox:
        assert controller.export_combined_pdf([]) is False
    MockBox.warning.assert_called_once()


def test_dialog_rejection_aborts(app):
    controller = CombinedPdfExportController(None)
    with patch(f"{_MODULE}.PDFExportDialog") as MockDialog:
        MockDialog.return_value.exec.return_value = QDialog.Rejected
        assert controller.export_combined_pdf([_result("/a.xml")]) is False


def test_save_cancel_aborts(app):
    controller = CombinedPdfExportController(None)
    with patch(f"{_MODULE}.PDFExportDialog") as MockDialog, \
            patch(f"{_MODULE}.QFileDialog") as MockFile:
        MockDialog.return_value.exec.return_value = QDialog.Accepted
        MockFile.getSaveFileName.return_value = ("", "")
        assert controller.export_combined_pdf([_result("/a.xml")]) is False


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
