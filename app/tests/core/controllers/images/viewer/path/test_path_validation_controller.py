"""Unit tests for PathValidationController."""

import json
import os
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QMessageBox

import importlib

from core.controllers.images.viewer.path.PathValidationController import (
    PathValidationController,
)
from core.services.RecoverySessionService import RecoverySession

# The path package re-exports the class under the same name, so a plain
# "import ... as path_module" would bind the class; resolve the real module.
path_module = importlib.import_module(
    "core.controllers.images.viewer.path.PathValidationController"
)


class _FakeSettings:
    """In-memory SettingsService stand-in so tests never touch real QSettings."""

    def __init__(self):
        self.store = {}

    def get_setting(self, name, default_value=None):
        return self.store.get(name, default_value)

    def set_setting(self, name, value):
        self.store[name] = value


@pytest.fixture
def controller():
    with patch.object(path_module, 'SettingsService', side_effect=_FakeSettings):
        instance = PathValidationController(MagicMock())
    return instance


def test_validate_no_missing_paths(controller, tmp_path):
    # Create real files
    img_path = tmp_path / "real.jpg"
    img_path.write_text("fake")
    images = [{"path": str(img_path), "mask_path": ""}]
    result = controller.validate_and_fix_paths(images)
    assert result is True


def test_validate_empty_paths_treated_as_valid(controller):
    images = [{"path": "", "mask_path": ""}]
    result = controller.validate_and_fix_paths(images)
    assert result is True


def test_validate_missing_image_prompts_user(controller):
    images = [{"path": "/nonexistent/a.jpg", "mask_path": ""}]
    with patch.object(controller, "_prompt_for_source_folder", return_value=True):
        result = controller.validate_and_fix_paths(images)
    assert result is True


def test_validate_missing_mask_prompts_user(controller, tmp_path):
    img_path = tmp_path / "real.jpg"
    img_path.write_text("fake")
    images = [{"path": str(img_path), "mask_path": "/nonexistent/m.png"}]
    with patch.object(controller, "_prompt_for_mask_folder", return_value=True):
        result = controller.validate_and_fix_paths(images)
    assert result is True


def test_validate_cancelled_source_returns_false(controller):
    images = [{"path": "/nonexistent/a.jpg", "mask_path": ""}]
    with patch.object(controller, "_prompt_for_source_folder", return_value=False):
        result = controller.validate_and_fix_paths(images)
    assert result is False


def test_validate_cancelled_mask_returns_false(controller, tmp_path):
    img_path = tmp_path / "real.jpg"
    img_path.write_text("fake")
    images = [{"path": str(img_path), "mask_path": "/nonexistent/m.png"}]
    with patch.object(controller, "_prompt_for_mask_folder", return_value=False):
        result = controller.validate_and_fix_paths(images)
    assert result is False


def test_prompt_source_folder_user_cancels_at_info(controller):
    missing = [{"image": {"path": "a.jpg"}, "filename": "a.jpg"}]
    with patch(
        "core.controllers.images.viewer.path.PathValidationController.QMessageBox"
    ) as MockMsgBox:
        # Simulate user clicking Cancel on info
        mock_box = MagicMock()
        mock_box.exec.return_value = QMessageBox.Cancel
        MockMsgBox.return_value = mock_box
        MockMsgBox.Cancel = QMessageBox.Cancel
        MockMsgBox.Ok = QMessageBox.Ok
        MockMsgBox.Information = QMessageBox.Information
        result = controller._prompt_for_source_folder(missing)
    assert result is False


def test_prompt_source_folder_user_cancels_at_folder_select(controller):
    missing = [{"image": {"path": "a.jpg"}, "filename": "a.jpg"}]
    with patch(
        "core.controllers.images.viewer.path.PathValidationController.QMessageBox"
    ) as MockMsgBox, patch(
        "core.controllers.images.viewer.path.PathValidationController.QFileDialog"
    ) as MockFileDialog:
        mock_box = MagicMock()
        mock_box.exec.return_value = QMessageBox.Ok
        MockMsgBox.return_value = mock_box
        MockMsgBox.Ok = QMessageBox.Ok
        MockMsgBox.Information = QMessageBox.Information
        MockFileDialog.getExistingDirectory.return_value = ""  # cancelled

        result = controller._prompt_for_source_folder(missing)
    assert result is False


def test_prompt_long_list_truncates_message(controller):
    # >10 missing files triggers the "and N more" suffix
    missing = [
        {"image": {"path": f"img{i}.jpg"}, "filename": f"img{i}.jpg"}
        for i in range(15)
    ]
    with patch(
        "core.controllers.images.viewer.path.PathValidationController.QMessageBox"
    ) as MockMsgBox:
        mock_box = MagicMock()
        mock_box.exec.return_value = QMessageBox.Cancel
        MockMsgBox.return_value = mock_box
        MockMsgBox.Cancel = QMessageBox.Cancel
        MockMsgBox.Ok = QMessageBox.Ok
        MockMsgBox.Information = QMessageBox.Information
        controller._prompt_for_source_folder(missing)
    # Check that setText was called with message including "... and"
    call_args = mock_box.setText.call_args
    message = call_args[0][0]
    assert "5 more" in message or "... and" in message


# --------------------------------------------------------------------------- #
#  Path recovery: choosing a correct folder must actually recover the images.  #
#                                                                             #
#  Reported bug: after picking the right folder, the load still reported the   #
#  images as missing. Root cause was os.path.basename() on a Windows-authored  #
#  stored path -- on POSIX it does not split backslashes, so the derived       #
#  "filename" was the entire path and could never be found in any folder.      #
#  That made the failure macOS/Linux-only; ntpath.basename splits both.        #
# --------------------------------------------------------------------------- #

_MODULE = "core.controllers.images.viewer.path.PathValidationController"


def _mock_msgbox(MockMsgBox, info_result=QMessageBox.Ok, buttons=None, clicked_index=None):
    """Wire up a mocked QMessageBox class.

    Args:
        info_result: What the initial "not found" confirmation returns.
        buttons: Sentinels returned by successive addButton() calls.
        clicked_index: Index into *buttons* that clickedButton() reports.
    """
    mock_box = MagicMock()
    mock_box.exec.return_value = info_result
    MockMsgBox.return_value = mock_box
    for name in ("Ok", "Cancel", "Information", "Warning",
                 "AcceptRole", "DestructiveRole"):
        setattr(MockMsgBox, name, getattr(QMessageBox, name))
    if buttons is not None:
        mock_box.addButton.side_effect = list(buttons)
        mock_box.clickedButton.return_value = (
            buttons[clicked_index] if clicked_index is not None else None
        )
    return mock_box


def test_windows_authored_path_recovers_from_chosen_folder(controller, tmp_path):
    """The headline regression: a Windows-written path, recovered on POSIX."""
    (tmp_path / "DJI_0042.JPG").write_text("x")
    image = {"path": r"C:\Users\pilot\Flight1\DJI_0042.JPG", "mask_path": ""}

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths([image]) is True

    assert image["path"] == str(tmp_path / "DJI_0042.JPG")


def test_same_named_images_relink_to_their_own_sortie(controller, tmp_path):
    """The wrong-photo regression, end to end.

    WALDO restarts its counter per sortie, so the same filename exists in
    every sortie folder. Recovery used to collapse them onto whichever copy
    the walk reached first AND persist that into the result XML, so an AOI
    kept its correct coordinates but was reattached to another photo - a
    circle on empty ground beside a gallery thumbnail of the real detection.
    """
    for sortie in ("Sortie1", "Sortie2"):
        folder = tmp_path / sortie
        folder.mkdir()
        (folder / "0_000_00_022.jpg").write_text(sortie)

    images = [
        {"path": r"D:\Capture\Sortie1\0_000_00_022.jpg", "mask_path": ""},
        {"path": r"D:\Capture\Sortie2\0_000_00_022.jpg", "mask_path": ""},
    ]

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths(images) is True

    assert images[0]["path"] == str(tmp_path / "Sortie1" / "0_000_00_022.jpg")
    assert images[1]["path"] == str(tmp_path / "Sortie2" / "0_000_00_022.jpg")
    # The collapse fingerprint the audit script looks for: two entries on one
    # path. It must not be reintroduced.
    assert images[0]["path"] != images[1]["path"]


def test_recovery_finds_images_in_subfolders(controller, tmp_path):
    """Drone media is normally nested; the old flat join never looked deeper."""
    nested = tmp_path / "DCIM" / "100MEDIA"
    nested.mkdir(parents=True)
    (nested / "DJI_0007.JPG").write_text("x")
    image = {"path": "/old/place/DJI_0007.JPG", "mask_path": ""}

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths([image]) is True

    assert image["path"] == str(nested / "DJI_0007.JPG")


def test_recovery_matches_extension_case_difference(controller, tmp_path):
    (tmp_path / "DJI_0009.jpg").write_text("x")
    image = {"path": "/old/DJI_0009.JPG", "mask_path": ""}

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths([image]) is True

    assert image["path"] == str(tmp_path / "DJI_0009.jpg")


def test_partial_recovery_continue_anyway_loads(controller, tmp_path):
    """One deleted capture must not cost the whole review."""
    (tmp_path / "a.jpg").write_text("x")
    found = {"path": "/old/a.jpg", "mask_path": ""}
    lost = {"path": "/old/gone.jpg", "mask_path": ""}
    retry, cont, cancel = MagicMock(name="retry"), MagicMock(name="cont"), MagicMock(name="cancel")

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox, buttons=[retry, cont, cancel], clicked_index=1)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths([found, lost]) is True

    assert found["path"] == str(tmp_path / "a.jpg"), "found file must still be repaired"
    assert lost["path"] == "/old/gone.jpg", "unresolved file is left alone"


def test_partial_recovery_cancel_aborts_load(controller, tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    images = [{"path": "/old/a.jpg", "mask_path": ""},
              {"path": "/old/gone.jpg", "mask_path": ""}]
    retry, cont, cancel = MagicMock(name="retry"), MagicMock(name="cont"), MagicMock(name="cancel")

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox, buttons=[retry, cont, cancel], clicked_index=2)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths(images) is False


def test_dismissing_partial_dialog_does_not_silently_continue(controller, tmp_path):
    """clickedButton() can be None on Esc; that must not read as "continue"."""
    (tmp_path / "a.jpg").write_text("x")
    images = [{"path": "/old/a.jpg", "mask_path": ""},
              {"path": "/old/gone.jpg", "mask_path": ""}]
    retry, cont, cancel = MagicMock(name="retry"), MagicMock(name="cont"), MagicMock(name="cancel")

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox, buttons=[retry, cont, cancel], clicked_index=None)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths(images) is False


def test_recovery_can_retry_with_a_different_folder(controller, tmp_path):
    """Picking the wrong folder first must not end the load."""
    wrong = tmp_path / "wrong"
    right = tmp_path / "right"
    wrong.mkdir()
    right.mkdir()
    (right / "a.jpg").write_text("x")
    image = {"path": "/old/a.jpg", "mask_path": ""}
    retry, cancel = MagicMock(name="retry"), MagicMock(name="cancel")

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        # No file found in `wrong`, so no "Continue Anyway" button is offered:
        # addButton is called twice (retry, cancel). User clicks retry.
        _mock_msgbox(MockMsgBox, buttons=[retry, cancel], clicked_index=0)
        MockFileDialog.getExistingDirectory.side_effect = [str(wrong), str(right)]
        assert controller.validate_and_fix_paths([image]) is True

    assert image["path"] == str(right / "a.jpg")
    assert MockFileDialog.getExistingDirectory.call_count == 2


def test_recovery_persists_paths_and_updates_input_dir(controller, tmp_path):
    """Without persistence the same folder is re-requested on every open."""
    import xml.etree.ElementTree as ET
    (tmp_path / "a.jpg").write_text("x")
    element = ET.Element("image", {"path": r"C:\old\a.jpg"})
    image = {"path": r"C:\old\a.jpg", "mask_path": "", "xml": element}

    controller.parent.settings = {"input_dir": r"C:\old"}
    controller.parent.xml_path = str(tmp_path / "ADIAT_Data.xml")

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths([image]) is True

    assert element.get("path") == str(tmp_path / "a.jpg"), "repair must reach the XML"
    assert controller.parent.settings["input_dir"] == str(tmp_path)
    controller.parent.xml_service.save_xml_file.assert_called_once_with(
        str(tmp_path / "ADIAT_Data.xml")
    )


def test_unwritable_result_file_does_not_fail_the_load(controller, tmp_path):
    """A result file on read-only media still loads with an in-memory repair."""
    (tmp_path / "a.jpg").write_text("x")
    image = {"path": "/old/a.jpg", "mask_path": ""}
    controller.parent.xml_path = str(tmp_path / "ADIAT_Data.xml")
    controller.parent.xml_service.save_xml_file.side_effect = OSError("read-only")

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(tmp_path)
        assert controller.validate_and_fix_paths([image]) is True

    assert image["path"] == str(tmp_path / "a.jpg")


def test_mask_recovery_repairs_mask_path_only(controller, tmp_path):
    """Masks recover through the same matcher but must not touch 'path'."""
    img = tmp_path / "a.jpg"
    img.write_text("x")
    masks = tmp_path / "masks"
    masks.mkdir()
    (masks / "a_mask.tif").write_text("x")
    image = {"path": str(img), "mask_path": r"C:\old\results\a_mask.tif"}
    controller.parent.settings = {"input_dir": r"C:\old"}

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(masks)
        assert controller.validate_and_fix_paths([image]) is True

    assert image["mask_path"] == str(masks / "a_mask.tif")
    assert image["path"] == str(img), "image path must be untouched"
    assert controller.parent.settings["input_dir"] == r"C:\old", \
        "mask recovery must not repoint the source image folder"

# --------------------------------------------------------------------------- #
#  Remembered recovery folders: batch 2..N must not re-prompt on this machine #
# --------------------------------------------------------------------------- #


def _remember(controller, *folders):
    controller.settings_service.store[
        PathValidationController.RECOVERY_FOLDERS_SETTING
    ] = json.dumps(list(folders))


def test_remembered_folder_auto_resolves_without_prompt(controller, tmp_path):
    """A folder that fixed a previous batch fixes this one silently."""
    flight = tmp_path / "copied" / "flight2"
    flight.mkdir(parents=True)
    (flight / "DJI_0042.JPG").write_text("fake")
    _remember(controller, str(tmp_path / "copied"))

    images = [{"path": r"C:\old\flight2\DJI_0042.JPG", "mask_path": ""}]

    with patch.object(controller, "_prompt_for_source_folder") as mock_prompt:
        result = controller.validate_and_fix_paths(images)

    assert result is True
    mock_prompt.assert_not_called()
    assert images[0]["path"] == str(flight / "DJI_0042.JPG")


def test_partial_auto_resolve_prompts_only_for_remainder(controller, tmp_path):
    """Auto-relink applies what it finds; only the rest goes to the prompt."""
    folder = tmp_path / "root"
    (folder / "batch").mkdir(parents=True)
    (folder / "batch" / "found.jpg").write_text("fake")
    _remember(controller, str(folder))

    images = [
        {"path": r"C:\old\batch\found.jpg", "mask_path": ""},
        {"path": r"C:\old\batch\gone.jpg", "mask_path": ""},
    ]

    with patch.object(controller, "_prompt_for_source_folder", return_value=True) as mock_prompt:
        result = controller.validate_and_fix_paths(images)

    assert result is True
    assert images[0]["path"] == str(folder / "batch" / "found.jpg")
    remaining = mock_prompt.call_args.args[0]
    assert [item["filename"] for item in remaining] == ["gone.jpg"]


def test_unattended_relink_will_not_take_a_lone_unrelated_match(controller, tmp_path):
    """Silent relink must not move a result set onto another flight line.

    This branch shows no dialog. A remembered folder holding one same-named
    file from a different capture is not evidence that it is the same photo,
    so it goes to the prompt instead of being taken on trust.
    """
    other = tmp_path / "Road1 North-South"
    other.mkdir()
    (other / "0_000_00_022.jpg").write_text("wrong flight line")
    _remember(controller, str(tmp_path))

    images = [{"path": r"E:\Cap\Road2 South-North\0_000_00_022.jpg", "mask_path": ""}]

    with patch.object(controller, "_prompt_for_source_folder", return_value=True) as mock_prompt:
        assert controller.validate_and_fix_paths(images) is True

    assert images[0]["path"] == r"E:\Cap\Road2 South-North\0_000_00_022.jpg"
    assert [i["filename"] for i in mock_prompt.call_args.args[0]] == ["0_000_00_022.jpg"]


def test_unplugged_remembered_folder_is_skipped_but_kept(controller, tmp_path):
    """A disconnected drive is skipped for now but not forgotten."""
    gone = r"E:\unplugged\flight"
    _remember(controller, gone)

    images = [{"path": r"C:\old\a.jpg", "mask_path": ""}]
    with patch.object(controller, "_prompt_for_source_folder", return_value=True):
        controller.validate_and_fix_paths(images)

    stored = json.loads(
        controller.settings_service.store[PathValidationController.RECOVERY_FOLDERS_SETTING]
    )
    assert gone in stored


def test_remember_folder_stores_folder_and_parent(controller, tmp_path):
    picked = tmp_path / "copied" / "flight1"
    picked.mkdir(parents=True)

    controller._remember_folder(str(picked))

    stored = json.loads(
        controller.settings_service.store[PathValidationController.RECOVERY_FOLDERS_SETTING]
    )
    # Picked folder first (most specific), then its parent for sibling batches
    assert stored[0] == str(picked)
    assert stored[1] == str(tmp_path / "copied")


def test_remember_folder_dedupes_and_caps(controller, tmp_path):
    for i in range(12):
        folder = tmp_path / f"batch{i}" / "images"
        folder.mkdir(parents=True)
        controller._remember_folder(str(folder))
    controller._remember_folder(str(tmp_path / "batch0" / "images"))  # re-pick

    stored = json.loads(
        controller.settings_service.store[PathValidationController.RECOVERY_FOLDERS_SETTING]
    )
    assert len(stored) <= PathValidationController.RECOVERY_FOLDERS_LIMIT
    assert stored[0] == str(tmp_path / "batch0" / "images")
    assert len(set(os.path.normcase(f) for f in stored)) == len(stored)


def test_filesystem_roots_are_never_remembered(controller):
    controller._remember_folder(os.path.abspath(os.sep))

    stored = json.loads(
        controller.settings_service.store.get(
            PathValidationController.RECOVERY_FOLDERS_SETTING, "[]"
        )
    )
    assert stored == []


# --------------------------------------------------------------------------- #
#  Scan-session recovery: runs opened from one folder scan resolve silently   #
#  from the scanned tree, and only prompt when the images are truly absent.   #
# --------------------------------------------------------------------------- #


def _with_session(controller, session):
    """Attach a real RecoverySession to the mocked parent viewer."""
    controller.parent.recovery_session = session
    return session


def test_scan_session_resolves_from_scan_root_without_prompt(controller, tmp_path):
    """Images living inside the scanned tree relink with no dialog at all."""
    flight = tmp_path / "mission" / "flight1"
    flight.mkdir(parents=True)
    (flight / "DJI_0042.JPG").write_text("fake")
    _with_session(controller, RecoverySession(str(tmp_path)))

    images = [{"path": r"C:\old\flight1\DJI_0042.JPG", "mask_path": ""}]

    with patch.object(controller, "_prompt_for_source_folder") as mock_prompt:
        assert controller.validate_and_fix_paths(images) is True

    mock_prompt.assert_not_called()
    assert images[0]["path"] == str(flight / "DJI_0042.JPG")


def test_scan_session_lone_unrelated_match_still_prompts(controller, tmp_path):
    """The silent branch keeps require_folder_agreement: a same-named file
    from another flight line under the scan root must not be taken on trust."""
    other = tmp_path / "Road1 North-South"
    other.mkdir()
    (other / "0_000_00_022.jpg").write_text("wrong flight line")
    _with_session(controller, RecoverySession(str(tmp_path)))

    images = [{"path": r"E:\Cap\Road2 South-North\0_000_00_022.jpg", "mask_path": ""}]

    with patch.object(controller, "_prompt_for_source_folder", return_value=True) as mock_prompt:
        assert controller.validate_and_fix_paths(images) is True

    assert images[0]["path"] == r"E:\Cap\Road2 South-North\0_000_00_022.jpg"
    assert [i["filename"] for i in mock_prompt.call_args.args[0]] == ["0_000_00_022.jpg"]


def test_scan_session_index_is_shared_across_viewers(controller, tmp_path):
    """Run 2..N from one scan reuses the index instead of re-walking the tree."""
    # The silent branch requires folder agreement, so the files live in a
    # subfolder whose name matches the stored paths' parent folder.
    cap = tmp_path / "cap"
    cap.mkdir()
    (cap / "a.jpg").write_text("x")
    (cap / "b.jpg").write_text("x")
    session = _with_session(controller, RecoverySession(str(tmp_path)))

    import core.services.RecoverySessionService as recovery_module
    with patch.object(
        recovery_module, 'index_folder_by_filename',
        wraps=recovery_module.index_folder_by_filename
    ) as mock_index:
        first = [{"path": r"C:\old\cap\a.jpg", "mask_path": ""}]
        assert controller.validate_and_fix_paths(first) is True

        # Second viewer from the same scan shares the session object
        with patch.object(path_module, 'SettingsService', side_effect=_FakeSettings):
            second_controller = PathValidationController(MagicMock())
        second_controller.parent.recovery_session = session
        second = [{"path": r"C:\old\cap\b.jpg", "mask_path": ""}]
        assert second_controller.validate_and_fix_paths(second) is True

    assert mock_index.call_count == 1
    assert first[0]["path"] == str(cap / "a.jpg")
    assert second[0]["path"] == str(cap / "b.jpg")


def test_scan_session_user_pick_serves_the_next_run(controller, tmp_path):
    """A folder picked at a prompt is tried silently for later runs of the scan."""
    scan_root = tmp_path / "results_only"
    scan_root.mkdir()
    elsewhere = tmp_path / "on_the_nas"
    batch = elsewhere / "nas_batch"
    batch.mkdir(parents=True)
    (batch / "one.jpg").write_text("x")
    (batch / "two.jpg").write_text("x")
    session = _with_session(controller, RecoverySession(str(scan_root)))

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(elsewhere)
        first = [{"path": r"C:\old\nas_batch\one.jpg", "mask_path": ""}]
        assert controller.validate_and_fix_paths(first) is True

    with patch.object(path_module, 'SettingsService', side_effect=_FakeSettings):
        second_controller = PathValidationController(MagicMock())
    second_controller.parent.recovery_session = session

    second = [{"path": r"C:\old\nas_batch\two.jpg", "mask_path": ""}]
    with patch.object(second_controller, "_prompt_for_source_folder") as mock_prompt:
        assert second_controller.validate_and_fix_paths(second) is True

    mock_prompt.assert_not_called()
    assert second[0]["path"] == str(batch / "two.jpg")


def test_scan_session_stale_index_entry_falls_back_to_prompt(controller, tmp_path):
    """A file that vanished after indexing must not be persisted as found."""
    (tmp_path / "a.jpg").write_text("x")
    session = _with_session(controller, RecoverySession(str(tmp_path)))
    session.get_index(str(tmp_path))  # warm the cache
    os.remove(tmp_path / "a.jpg")

    images = [{"path": r"C:\old\a.jpg", "mask_path": ""}]
    with patch.object(controller, "_prompt_for_source_folder", return_value=True) as mock_prompt:
        assert controller.validate_and_fix_paths(images) is True

    mock_prompt.assert_called_once()
    assert images[0]["path"] == r"C:\old\a.jpg"


def test_non_session_attribute_on_parent_is_ignored(controller, tmp_path):
    """Anything that is not a real RecoverySession (mocks, junk) is a no-op."""
    controller.parent.recovery_session = "not a session"
    images = [{"path": r"C:\old\a.jpg", "mask_path": ""}]
    with patch.object(controller, "_prompt_for_source_folder", return_value=True) as mock_prompt:
        assert controller.validate_and_fix_paths(images) is True
    mock_prompt.assert_called_once()


def test_successful_manual_recovery_remembers_the_folder(controller, tmp_path):
    """The interactive flow records the picked folder for future batches."""
    folder = tmp_path / "relinked"
    folder.mkdir()
    (folder / "img.jpg").write_text("fake")

    image = {"path": r"C:\old\img.jpg", "mask_path": ""}

    with patch(f"{_MODULE}.QMessageBox") as MockMsgBox, \
            patch(f"{_MODULE}.QFileDialog") as MockFileDialog:
        _mock_msgbox(MockMsgBox)
        MockFileDialog.getExistingDirectory.return_value = str(folder)
        assert controller.validate_and_fix_paths([image]) is True

    stored = json.loads(
        controller.settings_service.store[PathValidationController.RECOVERY_FOLDERS_SETTING]
    )
    assert str(folder) in stored
