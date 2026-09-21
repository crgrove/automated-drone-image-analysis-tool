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


# ---------------------------------------------------------------------------
# Results-only export mode (XML + masks, no images)
# ---------------------------------------------------------------------------
def test_thread_results_only_calls_the_results_stager():
    controller = MagicMock()
    thread = ZipExportThread(controller, [], "results_only", "/out.zip")
    successes = []
    thread.success.connect(lambda: successes.append(True))

    with patch("core.controllers.images.viewer.exports.ZipExportController.ZipBundleService"):
        thread.run()

    assert successes == [True]
    controller._export_results_only.assert_called_once()
    controller._export_native_prepare.assert_not_called()
    controller._export_augmented_one.assert_not_called()


def _results_xml(images):
    """A minimal real results XML: (path, mask_path_attr) per image."""
    blocks = []
    for path, mask in images:
        mask_attr = ' mask_path="' + mask + '"' if mask else ''
        blocks.append('<image path="' + path + '"' + mask_attr + ' hidden="False"/>')
    return ('<data><settings input_dir="in" output_dir="out" algorithm="X">'
            '<options/></settings><images>' + "".join(blocks) + '</images></data>')


def test_export_results_only_stages_xml_and_masks(tmp_path):
    # A real results layout: XML beside two mask TIFFs, one referenced twice.
    results_dir = tmp_path / "ADIAT_Results"
    results_dir.mkdir()
    (results_dir / "a_mask.tif").write_text("mask-a")
    (results_dir / "b_mask.tif").write_text("mask-b")
    xml_path = results_dir / "ADIAT_Data.xml"
    xml_path.write_text(_results_xml([
        ("C:/orig/1.jpg", "a_mask.tif"),
        ("C:/orig/2.jpg", "a_mask.tif"),      # duplicate reference
        ("C:/orig/3.jpg", "b_mask.tif"),
        ("C:/orig/4.jpg", "gone_mask.tif"),   # missing on disk
        ("C:/orig/5.jpg", ""),
    ]))

    parent = _parent()
    parent.xml_path = str(xml_path)
    parent.xml_service = None
    controller = ZipExportController(parent)

    staging = tmp_path / "staging"
    staging.mkdir()
    controller._export_results_only(str(staging))

    staged = staging / "ADIAT_Results"
    assert (staged / "a_mask.tif").read_text() == "mask-a"
    assert (staged / "b_mask.tif").read_text() == "mask-b"
    assert not (staged / "gone_mask.tif").exists()
    # In-tree references keep their relative names in the staged XML; the
    # missing mask is disclosed instead of silently dropped.
    from core.services.XmlService import XmlService
    staged_imgs = XmlService(str(staged / "ADIAT_Data.xml")).get_images()
    masks = [img['xml'].get('mask_path') for img in staged_imgs]
    assert masks[:3] == ["a_mask.tif", "a_mask.tif", "b_mask.tif"]
    missing_note = (staged / "MISSING_MASKS.txt").read_text()
    assert "gone_mask.tif" in missing_note
    # Nothing else travels: no images/ tree, original XML untouched.
    assert not (staging / "images").exists()
    assert 'mask_path="a_mask.tif"' in xml_path.read_text()


def test_export_results_only_without_xml_raises(tmp_path):
    parent = _parent()
    parent.xml_path = str(tmp_path / "missing.xml")
    controller = ZipExportController(parent)

    with pytest.raises(FileNotFoundError):
        controller._export_results_only(str(tmp_path))


# ---------------------------------------------------------------------------
# PR #149 review regression (B5): external masks must travel INSIDE the
# archive and never write outside staging.
# ---------------------------------------------------------------------------

def _tree_files(root):
    out = []
    for base, _dirs, files in os.walk(root):
        for name in files:
            out.append(os.path.join(base, name))
    return out


def test_b5_external_masks_travel_inside_the_archive(tmp_path):
    """An XML relinked to masks OUTSIDE its results folder (path recovery
    legitimately persists such absolute paths) must still produce a complete,
    self-contained bundle: masks staged under the archive, references
    rewritten, and nothing written outside the staging tree."""
    import zipfile

    source = tmp_path / "source"
    results_dir = source / "review" / "ADIAT_Results"
    results_dir.mkdir(parents=True)
    shared = source / "shared_masks"
    shared.mkdir()
    (shared / "a.tif").write_text("external-a")
    other = source / "other_masks"
    other.mkdir()
    (other / "a.tif").write_text("external-a2")     # same basename, elsewhere
    (results_dir / "local.tif").write_text("local")

    xml_path = results_dir / "ADIAT_Data.xml"
    xml_path.write_text(_results_xml([
        ("C:/orig/1.jpg", str(shared / "a.tif").replace("\\", "/")),
        ("C:/orig/2.jpg", str(other / "a.tif").replace("\\", "/")),
        ("C:/orig/3.jpg", "local.tif"),
    ]))
    original_xml_text = xml_path.read_text()

    parent = _parent()
    parent.xml_path = str(xml_path)
    controller = ZipExportController(parent)

    staging = tmp_path / "staging"
    staging.mkdir()
    before_outside = set(_tree_files(source))
    controller._export_results_only(str(staging))

    # Nothing was written outside the staging tree, and the original XML
    # is byte-identical.
    assert set(_tree_files(source)) == before_outside
    assert xml_path.read_text() == original_xml_text

    # Zip the staging tree, extract elsewhere, and resolve every staged
    # mask reference against the extracted XML's location.
    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in _tree_files(staging):
            zf.write(f, os.path.relpath(f, staging))
    extract = tmp_path / "extracted"
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract)

    from core.services.XmlService import XmlService
    staged_xml = extract / "ADIAT_Results" / "ADIAT_Data.xml"
    contents = set()
    for img in XmlService(str(staged_xml)).get_images():
        mask = img.get('mask_path', '')
        assert mask, "every reference survived"
        assert os.path.exists(mask), f"unresolvable staged mask: {mask}"
        resolved = os.path.realpath(mask)
        assert resolved.startswith(
            os.path.realpath(str(extract)) + os.sep), "mask escaped the bundle"
        with open(mask, encoding="utf-8") as fh:
            contents.add(fh.read())
    # Both same-basename externals AND the local mask arrived intact.
    assert contents == {"external-a", "external-a2", "local"}
    assert not (extract / "ADIAT_Results" / "MISSING_MASKS.txt").exists()


def test_b5_other_drive_mask_is_contained(tmp_path, monkeypatch):
    """A mask on another Windows drive (relpath raises ValueError) lands under
    external_masks/ instead of escaping the staging tree."""
    results_dir = tmp_path / "ADIAT_Results"
    results_dir.mkdir()
    mask = tmp_path / "z_drive_mask.tif"
    mask.write_text("z-drive")
    xml_path = results_dir / "ADIAT_Data.xml"
    xml_path.write_text(_results_xml([
        ("C:/orig/1.jpg", str(mask).replace("\\", "/"))]))

    real_relpath = os.path.relpath

    def cross_drive_relpath(path, start=os.curdir):
        if os.path.normcase(str(mask)) in os.path.normcase(str(path)):
            raise ValueError("path is on mount 'Z:', start on mount 'C:'")
        return real_relpath(path, start)

    parent = _parent()
    parent.xml_path = str(xml_path)
    controller = ZipExportController(parent)
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(
        "core.controllers.images.viewer.exports.ZipExportController.os.path.relpath",
        cross_drive_relpath)
    controller._export_results_only(str(staging))

    staged = staging / "ADIAT_Results"
    assert (staged / "external_masks" / "z_drive_mask.tif").read_text() == "z-drive"
    from core.services.XmlService import XmlService
    imgs = XmlService(str(staged / "ADIAT_Data.xml")).get_images()
    assert imgs[0]['xml'].get('mask_path') == "external_masks/z_drive_mask.tif"
