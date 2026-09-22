"""Unit tests for BearingRecoveryController."""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QDialog

from core.controllers.images.viewer.bearing.BearingRecoveryController import (
    BearingRecoveryController,
)


@pytest.fixture
def controller():
    return BearingRecoveryController(MagicMock())


def test_xml_bearings_exist_returns_zero(controller):
    images = [
        {"path": "img1.jpg", "bearing": 90.0},
        {"path": "img2.jpg", "bearing": None},
    ]
    assert controller.check_and_recover_bearings(images, MagicMock(), "/x.xml") == 0


def test_exif_gimbal_bearing_returns_zero(controller):
    images = [{"path": "img1.jpg", "bearing": None}]

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService:
        MockService.return_value.get_camera_yaw.return_value = 90.0
        result = controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    assert result == 0


def test_exif_check_raises_exception_continues_to_dialog(controller):
    images = [{"path": "img1.jpg", "bearing": None}]

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService, patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog"
    ) as MockDialog:
        MockService.side_effect = RuntimeError("EXIF error")
        MockDialog.return_value.exec.return_value = QDialog.Rejected

        result = controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    # Dialog was shown (EXIF check failed but recovery path continued)
    assert result == 0
    MockDialog.assert_called_once()


def test_dialog_accepted_saves_bearings(controller):
    images = [
        {"path": "img1.jpg", "bearing": None},
        {"path": "img2.jpg", "bearing": None},
    ]
    xml_service = MagicMock()
    xml_service.set_multiple_bearings.return_value = 2

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService, patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog"
    ) as MockDialog:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.return_value = QDialog.Accepted
        MockDialog.return_value.get_results.return_value = {"img1.jpg": 90.0, "img2.jpg": 180.0}

        result = controller.check_and_recover_bearings(images, xml_service, "/x.xml")

    assert result == 2
    xml_service.set_multiple_bearings.assert_called_once()
    xml_service.save_xml_file.assert_called_once_with("/x.xml")


def test_dialog_rejected_returns_zero(controller):
    images = [{"path": "img1.jpg", "bearing": None}]

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService, patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog"
    ) as MockDialog:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.return_value = QDialog.Rejected

        result = controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    assert result == 0


def test_empty_image_list_returns_zero(controller):
    assert controller.check_and_recover_bearings([], MagicMock(), "/x.xml") == 0


def test_loading_dialog_hidden_while_recovery_dialog_is_up(controller):
    """Regression: the always-on-top ResultsLoadingDialog must be hidden
    before the modal recovery dialog opens and restored afterwards,
    otherwise the recovery dialog is buried under the heartbeat."""
    images = [{"path": "img1.jpg", "bearing": None}]
    call_order = []

    loading_dialog = MagicMock()
    loading_dialog.hide.side_effect = lambda: call_order.append("hide")
    loading_dialog.show.side_effect = lambda: call_order.append("show")
    controller.parent._loading_dialog = loading_dialog

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService, patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog"
    ) as MockDialog:
        MockService.return_value.get_camera_yaw.return_value = None

        def exec_dialog():
            call_order.append("exec")
            return QDialog.Rejected
        MockDialog.return_value.exec.side_effect = exec_dialog

        controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    assert call_order == ["hide", "exec", "show"]


def test_loading_dialog_restored_when_dialog_exec_raises(controller):
    """The heartbeat dialog is restored even if the recovery dialog errors."""
    images = [{"path": "img1.jpg", "bearing": None}]

    loading_dialog = MagicMock()
    controller.parent._loading_dialog = loading_dialog

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService, patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog"
    ) as MockDialog:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError):
            controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    loading_dialog.show.assert_called_once()


def test_no_loading_dialog_attribute_is_tolerated(controller):
    """A parent without _loading_dialog (or with it already cleared) is fine."""
    images = [{"path": "img1.jpg", "bearing": None}]
    controller.parent = object()  # no _loading_dialog attribute at all

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService, patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog"
    ) as MockDialog:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.return_value = QDialog.Rejected

        result = controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    assert result == 0


def test_dialog_accepted_with_empty_results(controller):
    images = [{"path": "img1.jpg", "bearing": None}]
    xml_service = MagicMock()

    with patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.ImageService"
    ) as MockService, patch(
        "core.controllers.images.viewer.bearing.BearingRecoveryController.BearingRecoveryDialog"
    ) as MockDialog:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.return_value = QDialog.Accepted
        MockDialog.return_value.get_results.return_value = {}

        result = controller.check_and_recover_bearings(images, xml_service, "/x.xml")

    assert result == 0
    xml_service.set_multiple_bearings.assert_not_called()


# ---------------------------------------------------------------------------
# Session track discovery: a track log found in the results-scan tree is
# offered to the dialog so the user is not sent browsing for it.
# ---------------------------------------------------------------------------

_MODULE = "core.controllers.images.viewer.bearing.BearingRecoveryController"


def test_session_track_suggestion_reaches_dialog(controller, tmp_path):
    from core.services.RecoverySessionService import RecoverySession
    session = RecoverySession(str(tmp_path))
    (tmp_path / "tracklog.gpx").write_text("x")
    controller.parent.recovery_session = session

    images = [{"path": "img1.jpg", "bearing": None}]
    with patch(f"{_MODULE}.ImageService") as MockService, \
            patch(f"{_MODULE}.BearingRecoveryDialog") as MockDialog, \
            patch(f"{_MODULE}.TrackDiscoveryService") as MockDiscovery:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.return_value = QDialog.Rejected
        MockDiscovery.return_value.discover_track.return_value = str(tmp_path / "tracklog.gpx")

        controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    assert MockDialog.call_args.kwargs["suggested_track"] == str(tmp_path / "tracklog.gpx")
    candidate_arg = MockDiscovery.return_value.discover_track.call_args.args[1]
    assert str(tmp_path / "tracklog.gpx") in candidate_arg


def test_no_session_means_no_suggestion_and_no_discovery(controller):
    # The MagicMock parent's auto-attribute is not a real RecoverySession
    images = [{"path": "img1.jpg", "bearing": None}]
    with patch(f"{_MODULE}.ImageService") as MockService, \
            patch(f"{_MODULE}.BearingRecoveryDialog") as MockDialog, \
            patch(f"{_MODULE}.TrackDiscoveryService") as MockDiscovery:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.return_value = QDialog.Rejected

        controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    assert MockDialog.call_args.kwargs["suggested_track"] is None
    MockDiscovery.assert_not_called()


def test_discovery_failure_degrades_to_no_suggestion(controller, tmp_path):
    from core.services.RecoverySessionService import RecoverySession
    session = RecoverySession(str(tmp_path))
    (tmp_path / "tracklog.gpx").write_text("x")
    controller.parent.recovery_session = session

    images = [{"path": "img1.jpg", "bearing": None}]
    with patch(f"{_MODULE}.ImageService") as MockService, \
            patch(f"{_MODULE}.BearingRecoveryDialog") as MockDialog, \
            patch(f"{_MODULE}.TrackDiscoveryService") as MockDiscovery:
        MockService.return_value.get_camera_yaw.return_value = None
        MockDialog.return_value.exec.return_value = QDialog.Rejected
        MockDiscovery.return_value.discover_track.side_effect = RuntimeError("boom")

        result = controller.check_and_recover_bearings(images, MagicMock(), "/x.xml")

    assert result == 0
    assert MockDialog.call_args.kwargs["suggested_track"] is None
