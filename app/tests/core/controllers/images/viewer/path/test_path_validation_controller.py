"""Unit tests for PathValidationController."""

import os
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QMessageBox

from core.controllers.images.viewer.path.PathValidationController import (
    PathValidationController,
)


@pytest.fixture
def controller():
    return PathValidationController(MagicMock())


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
