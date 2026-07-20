"""Unit tests for PDFExportController."""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QDialog

from core.controllers.images.viewer.exports.PDFExportController import (
    PDFExportController,
    PdfGenerationThread,
)


@pytest.fixture
def controller():
    parent = MagicMock()
    return PDFExportController(parent)


# ---------------------------------------------------------------------------
# PdfGenerationThread
# ---------------------------------------------------------------------------

def test_thread_cancel_sets_flag_and_emits():
    thread = PdfGenerationThread(MagicMock(), "/out.pdf")
    cancelled = []
    thread.canceled.connect(lambda: cancelled.append(True))
    thread.cancel()
    assert thread._is_canceled is True
    assert cancelled == [True]


def test_thread_emits_success_on_completion():
    pdf_gen = MagicMock()
    pdf_gen.generate_report.return_value = None  # No error
    thread = PdfGenerationThread(pdf_gen, "/out.pdf")
    successes = []
    thread.success.connect(lambda: successes.append(True))
    thread.run()
    assert successes == [True]


def test_thread_emits_error_on_generator_error():
    pdf_gen = MagicMock()
    pdf_gen.generate_report.return_value = "generation failed"
    thread = PdfGenerationThread(pdf_gen, "/out.pdf")
    errors = []
    thread.errorOccurred.connect(lambda msg: errors.append(msg))
    thread.run()
    assert errors == ["generation failed"]


def test_thread_emits_error_on_exception():
    pdf_gen = MagicMock()
    pdf_gen.generate_report.side_effect = RuntimeError("boom")
    thread = PdfGenerationThread(pdf_gen, "/out.pdf")
    errors = []
    thread.errorOccurred.connect(lambda msg: errors.append(msg))
    thread.run()
    assert errors == ["boom"]


def test_thread_skips_run_when_pre_cancelled():
    pdf_gen = MagicMock()
    thread = PdfGenerationThread(pdf_gen, "/out.pdf")
    thread._is_canceled = True
    thread.run()
    pdf_gen.generate_report.assert_not_called()


# ---------------------------------------------------------------------------
# Controller callbacks
# ---------------------------------------------------------------------------

def test_on_progress_updated_forwards(controller):
    controller.progress_dialog = MagicMock()
    controller._on_progress_updated(5, 10, "working")
    controller.progress_dialog.update_progress.assert_called_once_with(5, 10, "working")


def test_on_pdf_generation_finished_shows_success(controller):
    controller.progress_dialog = MagicMock()
    with patch(
        "core.controllers.images.viewer.exports.PDFExportController.QMessageBox"
    ) as MockQMB:
        controller._on_pdf_generation_finished()
    controller.progress_dialog.accept.assert_called_once()
    MockQMB.information.assert_called_once()


def test_on_pdf_generation_cancelled_rejects_dialog(controller):
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True
    controller.pdf_thread = MagicMock()
    controller.pdf_thread.isRunning.return_value = False

    controller._on_pdf_generation_cancelled()

    controller.progress_dialog.reject.assert_called_once()


def test_on_pdf_generation_error_shows_error(controller):
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True
    controller._show_error = MagicMock()
    controller._on_pdf_generation_error("bad thing")
    controller._show_error.assert_called_once()


def test_show_toast_forwards_to_parent():
    parent = MagicMock()
    controller = PDFExportController(parent)
    controller._show_toast("hello", 2000, "#fff")
    parent._show_toast.assert_called_once_with("hello", 2000, "#fff")


def test_show_error_falls_back_to_messagebox_when_parent_lacks_handler():
    parent = MagicMock(spec=[])  # parent has no _show_error method
    controller = PDFExportController(parent)
    with patch(
        "core.controllers.images.viewer.exports.PDFExportController.QMessageBox"
    ) as MockQMB:
        controller._show_error("err")
    MockQMB.critical.assert_called_once()


# ---------------------------------------------------------------------------
# Export flow: dialog cancelled → returns False
# ---------------------------------------------------------------------------

def test_export_pdf_dialog_cancelled_returns_false(controller):
    with patch(
        "core.controllers.images.viewer.exports.PDFExportController.PDFExportDialog"
    ) as MockDialog:
        MockDialog.return_value.exec.return_value = QDialog.Rejected
        result = controller.export_pdf([], {})
    assert result is False


# ---------------------------------------------------------------------------
# Image filtering
# ---------------------------------------------------------------------------

def test_export_pdf_no_flagged_no_include_returns_false(controller):
    images = [
        {"path": "a.jpg", "areas_of_interest": [{"id": 1}], "hidden": False},
        {"path": "b.jpg", "areas_of_interest": [{"id": 2}], "hidden": False},
    ]
    flagged_aois = {}  # nothing flagged

    with patch(
        "core.controllers.images.viewer.exports.PDFExportController.PDFExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.PDFExportController.QMessageBox"
    ):
        dialog = MockDialog.return_value
        dialog.exec.return_value = QDialog.Accepted
        dialog.get_organization.return_value = "Org"
        dialog.get_search_name.return_value = "Search"
        dialog.get_include_images_without_flagged_aois.return_value = False
        dialog.get_map_tile_source.return_value = "OSM"

        result = controller.export_pdf(images, flagged_aois)
    assert result is False


def test_export_pdf_no_images_include_all_returns_false(controller):
    images = []  # no images at all
    flagged_aois = {}

    with patch(
        "core.controllers.images.viewer.exports.PDFExportController.PDFExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.PDFExportController.QMessageBox"
    ):
        dialog = MockDialog.return_value
        dialog.exec.return_value = QDialog.Accepted
        dialog.get_organization.return_value = "Org"
        dialog.get_search_name.return_value = "Search"
        dialog.get_include_images_without_flagged_aois.return_value = True
        dialog.get_map_tile_source.return_value = "OSM"

        result = controller.export_pdf(images, flagged_aois)
    assert result is False


def test_export_pdf_file_dialog_cancelled_returns_false(controller):
    images = [{"path": "a.jpg", "areas_of_interest": [{"id": 1}], "hidden": False}]
    flagged_aois = {0: {0}}

    with patch(
        "core.controllers.images.viewer.exports.PDFExportController.PDFExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.PDFExportController.QFileDialog"
    ) as MockFileDialog, patch(
        "core.controllers.images.viewer.exports.PDFExportController.QMessageBox"
    ):
        dialog = MockDialog.return_value
        dialog.exec.return_value = QDialog.Accepted
        dialog.get_organization.return_value = "Org"
        dialog.get_search_name.return_value = "Search"
        dialog.get_include_images_without_flagged_aois.return_value = False
        dialog.get_map_tile_source.return_value = "OSM"

        MockFileDialog.getSaveFileName.return_value = ("", "")  # cancelled
        result = controller.export_pdf(images, flagged_aois)
    assert result is False
