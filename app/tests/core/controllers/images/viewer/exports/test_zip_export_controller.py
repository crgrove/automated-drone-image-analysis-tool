"""Unit tests for ZipExportController."""

import os
import tempfile
from pathlib import Path

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QDialog

from core.controllers.images.viewer.exports.ZipExportController import (
    ZipExportController,
    ZipExportThread,
)


def _parent():
    parent = MagicMock()
    parent.aoi_controller.flagged_aois = {}
    parent.xml_path = None
    parent.xml_service = None
    parent.settings = {"identifier_color": (255, 0, 0)}
    parent.showAOIsButton.isChecked.return_value = True
    parent.showPOIsButton.isChecked.return_value = False
    return parent


@pytest.fixture
def controller():
    return ZipExportController(_parent())


# ---------------------------------------------------------------------------
# ZipExportThread behavior
# ---------------------------------------------------------------------------

def test_thread_cancel_sets_flag():
    thread = ZipExportThread(MagicMock(), [], "native", "/out.zip")
    assert thread._cancel is False
    thread.cancel()
    assert thread._cancel is True


def test_thread_emits_canceled_when_native_cancelled():
    controller = MagicMock()
    thread = ZipExportThread(controller, [{"path": "a.jpg"}], "native", "/out.zip")
    thread._cancel = True  # pre-cancel

    cancelled = []
    thread.canceled.connect(lambda: cancelled.append(True))

    with patch("core.controllers.images.viewer.exports.ZipExportController.tempfile.mkdtemp") as mock_mkdtemp:
        mock_mkdtemp.return_value = tempfile.mkdtemp(prefix="test_zip_")
        thread.run()

    assert cancelled == [True]


def test_thread_success_on_native_export():
    controller = MagicMock()
    thread = ZipExportThread(controller, [{"path": "a.jpg"}], "native", "/out.zip")
    successes = []
    thread.success.connect(lambda: successes.append(True))

    with patch("core.controllers.images.viewer.exports.ZipExportController.ZipBundleService"):
        thread.run()

    assert successes == [True]
    controller._export_native_prepare.assert_called_once()
    controller._export_native_copy_one.assert_called_once()
    controller._export_native_finalize.assert_called_once()


def test_thread_success_on_augmented_export():
    controller = MagicMock()
    thread = ZipExportThread(controller, [{"path": "a.jpg"}], "augmented", "/out.zip")
    successes = []
    thread.success.connect(lambda: successes.append(True))

    with patch("core.controllers.images.viewer.exports.ZipExportController.ZipBundleService"):
        thread.run()

    assert successes == [True]
    controller._export_augmented_one.assert_called_once()


def test_thread_error_on_exception():
    controller = MagicMock()
    controller._export_native_prepare.side_effect = RuntimeError("fail")
    thread = ZipExportThread(controller, [{"path": "a.jpg"}], "native", "/out.zip")
    errors = []
    thread.errorOccurred.connect(lambda msg: errors.append(msg))

    thread.run()
    assert errors == ["fail"]


# ---------------------------------------------------------------------------
# Controller callbacks
# ---------------------------------------------------------------------------

def test_on_zip_success_shows_toast(controller):
    controller.progress_dialog = MagicMock()
    controller.parent._show_toast = MagicMock()
    controller._on_zip_success()
    controller.progress_dialog.accept.assert_called_once()
    controller.parent._show_toast.assert_called_once()


def test_on_zip_error_rejects_dialog(controller):
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True
    controller._show_error = MagicMock()
    controller._on_zip_error("fail")
    controller.progress_dialog.reject.assert_called_once()
    controller._show_error.assert_called_once()


def test_on_zip_cancelled_terminates_thread(controller):
    controller.zip_thread = MagicMock()
    controller.zip_thread.isRunning.return_value = True
    controller.progress_dialog = MagicMock()
    controller.progress_dialog.isVisible.return_value = True

    controller._on_zip_cancelled()

    controller.zip_thread.terminate.assert_called_once()
    controller.zip_thread.wait.assert_called_once()
    controller.progress_dialog.reject.assert_called_once()


def test_on_progress_updated_forwards(controller):
    controller.progress_dialog = MagicMock()
    controller._on_progress_updated(5, 10, "Copying a.jpg")
    controller.progress_dialog.update_progress.assert_called_once_with(5, 10, "Copying a.jpg")


# ---------------------------------------------------------------------------
# export_zip flow — dialog cancelled
# ---------------------------------------------------------------------------

def test_export_zip_dialog_cancelled_returns_false(controller):
    with patch(
        "core.controllers.images.viewer.exports.ZipExportController.ZipExportDialog"
    ) as MockDialog:
        MockDialog.return_value.exec.return_value = QDialog.Rejected
        assert controller.export_zip([]) is False


def test_export_zip_file_dialog_cancelled_returns_false(controller):
    with patch(
        "core.controllers.images.viewer.exports.ZipExportController.ZipExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.ZipExportController.QFileDialog"
    ) as MockFile:
        MockDialog.return_value.exec.return_value = QDialog.Accepted
        MockDialog.return_value.get_export_mode.return_value = "native"
        MockDialog.return_value.should_include_images_without_flagged_aois.return_value = True
        MockFile.getSaveFileName.return_value = ("", "")
        assert controller.export_zip([]) is False


def test_export_zip_no_visible_images_shows_toast():
    parent = _parent()
    parent._show_toast = MagicMock()
    controller = ZipExportController(parent)
    images = [{"path": "a.jpg", "hidden": True}]  # all hidden

    with patch(
        "core.controllers.images.viewer.exports.ZipExportController.ZipExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.ZipExportController.QFileDialog"
    ) as MockFile:
        MockDialog.return_value.exec.return_value = QDialog.Accepted
        MockDialog.return_value.get_export_mode.return_value = "native"
        MockDialog.return_value.should_include_images_without_flagged_aois.return_value = True
        MockFile.getSaveFileName.return_value = ("/out.zip", "*.zip")

        result = controller.export_zip(images)

    assert result is False
    parent._show_toast.assert_called_once()


def test_export_zip_filters_by_flagged_when_checkbox_unchecked():
    parent = _parent()
    parent._show_toast = MagicMock()
    parent.aoi_controller.flagged_aois = {0: {0}}  # only image 0 has a flagged AOI
    controller = ZipExportController(parent)

    images = [
        {"path": "a.jpg", "hidden": False, "areas_of_interest": [{"id": 1}]},
        {"path": "b.jpg", "hidden": False, "areas_of_interest": [{"id": 2}]},
    ]

    with patch(
        "core.controllers.images.viewer.exports.ZipExportController.ZipExportDialog"
    ) as MockDialog, patch(
        "core.controllers.images.viewer.exports.ZipExportController.QFileDialog"
    ) as MockFile, patch(
        "core.controllers.images.viewer.exports.ZipExportController.ExportProgressDialog"
    ) as MockProgressDialog, patch(
        "core.controllers.images.viewer.exports.ZipExportController.ZipExportThread"
    ):
        MockDialog.return_value.exec.return_value = QDialog.Accepted
        MockDialog.return_value.get_export_mode.return_value = "native"
        MockDialog.return_value.should_include_images_without_flagged_aois.return_value = False
        MockFile.getSaveFileName.return_value = ("/out.zip", "*.zip")
        MockProgressDialog.return_value.exec.return_value = QDialog.Accepted

        result = controller.export_zip(images)

    assert result is True


# ---------------------------------------------------------------------------
# Native export path logic
# ---------------------------------------------------------------------------

def test_export_native_prepare_builds_context():
    controller = ZipExportController(_parent())
    with tempfile.TemporaryDirectory() as staging:
        images = [{"path": "/tmp/some.jpg"}]
        controller._export_native_prepare(images, staging)
        ctx = controller._native_ctx
        assert ctx["staging_root"] == staging
        assert os.path.exists(ctx["images_root"])
        assert os.path.exists(ctx["results_root"])


def test_export_native_copy_one_skips_missing_file():
    controller = ZipExportController(_parent())
    with tempfile.TemporaryDirectory() as staging:
        controller._native_ctx = {
            "images_root": os.path.join(staging, "images"),
            "input_dir": staging,
        }
        os.makedirs(controller._native_ctx["images_root"], exist_ok=True)
        # Path doesn't exist
        controller._export_native_copy_one({"path": "/nonexistent.jpg"}, staging)
        # No crash, no files copied
        assert not any(Path(controller._native_ctx["images_root"]).iterdir())


def test_export_native_copy_one_copies_existing_file():
    controller = ZipExportController(_parent())
    with tempfile.TemporaryDirectory() as staging:
        # Create a real source file
        src_path = os.path.join(staging, "src_image.jpg")
        Path(src_path).write_bytes(b"fake image")

        controller._native_ctx = {
            "images_root": os.path.join(staging, "images"),
            "input_dir": staging,
        }
        os.makedirs(controller._native_ctx["images_root"], exist_ok=True)

        controller._export_native_copy_one({"path": src_path}, staging)
        # File should have been copied
        expected = os.path.join(controller._native_ctx["images_root"], "src_image.jpg")
        assert os.path.exists(expected)


# ---------------------------------------------------------------------------
# _show_toast and _show_error
# ---------------------------------------------------------------------------

def test_show_toast_forwards_to_parent():
    parent = _parent()
    parent._show_toast = MagicMock()
    controller = ZipExportController(parent)
    controller._show_toast("hi", 1000, "#ff0000")
    parent._show_toast.assert_called_once_with("hi", 1000, "#ff0000")


def test_show_toast_no_handler_doesnt_crash():
    parent = MagicMock(spec=[])
    controller = ZipExportController(parent)
    controller._show_toast("hi")  # should not raise
