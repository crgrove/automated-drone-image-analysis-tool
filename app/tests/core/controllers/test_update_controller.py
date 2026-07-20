from unittest.mock import MagicMock, patch

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget

from core.controllers.UpdateController import UpdateController
from core.services.UpdateService import UpdateRelease


class DummyWindow(QWidget):
    def __init__(self, settings_service):
        super().__init__()
        self.settings_service = settings_service
        self.app_version = "2.1.0 Alpha"


def test_refresh_action_state_disables_updates_when_offline(qtbot):
    settings_service = MagicMock()
    settings_service.get_bool_setting.side_effect = lambda name, default=False: {
        "OfflineOnly": True,
        "AutoCheckForUpdates": True,
    }.get(name, default)

    window = DummyWindow(settings_service)
    qtbot.addWidget(window)

    controller = UpdateController(window, update_service=MagicMock(), settings_service=settings_service)
    action = QAction("Check for Updates", window)
    controller.bind_action(action)

    assert action.isEnabled() is False
    assert action.toolTip() == "Disabled while Offline Only mode is enabled."


def test_schedule_startup_check_runs_once_per_session(qtbot):
    settings_service = MagicMock()
    settings_service.get_bool_setting.side_effect = lambda name, default=False: {
        "OfflineOnly": False,
        "AutoCheckForUpdates": True,
    }.get(name, default)

    window = DummyWindow(settings_service)
    qtbot.addWidget(window)

    controller = UpdateController(window, update_service=MagicMock(), settings_service=settings_service)
    app = QApplication.instance()
    app.setProperty(UpdateController.STARTUP_CHECK_PROPERTY, False)

    try:
        with patch("core.controllers.UpdateController.QTimer.singleShot") as mock_single_shot:
            assert controller.schedule_startup_check() is True
            assert controller.schedule_startup_check() is False
    finally:
        app.setProperty(UpdateController.STARTUP_CHECK_PROPERTY, False)

    mock_single_shot.assert_called_once()


def test_check_for_updates_downloads_and_launches_installer(qtbot):
    settings_service = MagicMock()
    settings_service.get_bool_setting.side_effect = lambda name, default=False: {
        "OfflineOnly": False,
        "AutoCheckForUpdates": True,
    }.get(name, default)

    update_service = MagicMock()
    update_service.get_latest_available_release.return_value = UpdateRelease(
        version="2.1.0",
        installer_url="https://example.com/ADIAT.exe",
        platforms=("windows",),
    )

    window = DummyWindow(settings_service)
    qtbot.addWidget(window)

    controller = UpdateController(window, update_service=update_service, settings_service=settings_service)

    with patch.object(controller, "_prompt_to_install", return_value=True), \
            patch.object(controller, "_download_release", return_value="/tmp/ADIAT.exe"), \
            patch("core.controllers.UpdateController.QMessageBox.information") as mock_information:
        path = controller.check_for_updates(interactive=True)

    assert path == "/tmp/ADIAT.exe"
    update_service.launch_installer.assert_called_once_with("/tmp/ADIAT.exe")
    mock_information.assert_called_once()


def test_check_for_updates_reports_when_app_is_current(qtbot):
    settings_service = MagicMock()
    settings_service.get_bool_setting.side_effect = lambda name, default=False: {
        "OfflineOnly": False,
        "AutoCheckForUpdates": True,
    }.get(name, default)

    update_service = MagicMock()
    update_service.get_latest_available_release.return_value = None

    window = DummyWindow(settings_service)
    qtbot.addWidget(window)

    controller = UpdateController(window, update_service=update_service, settings_service=settings_service)

    with patch("core.controllers.UpdateController.QMessageBox.information") as mock_information:
        result = controller.check_for_updates(interactive=True)

    assert result is None
    mock_information.assert_called_once()


def test_menu_action_trigger_shows_no_updates_dialog(qtbot):
    """Triggering the Help-menu action runs interactively and shows the
    'No Updates Available' dialog when already on the latest version.

    Regression: QAction.triggered passes a `checked` bool, so connecting
    check_for_updates directly ran it with interactive=False and suppressed
    the dialog.
    """
    settings_service = MagicMock()
    settings_service.get_bool_setting.side_effect = lambda name, default=False: {
        "OfflineOnly": False,
        "AutoCheckForUpdates": True,
    }.get(name, default)

    update_service = MagicMock()
    update_service.get_latest_available_release.return_value = None  # on latest

    window = DummyWindow(settings_service)
    qtbot.addWidget(window)

    controller = UpdateController(window, update_service=update_service, settings_service=settings_service)
    action = QAction("Check for Updates", window)
    controller.bind_action(action)

    with patch("core.controllers.UpdateController.QMessageBox.information") as mock_information:
        action.trigger()

    mock_information.assert_called_once()
    title = mock_information.call_args.args[1]
    assert "No Updates Available" in title
