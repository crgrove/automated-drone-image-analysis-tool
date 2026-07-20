from unittest.mock import patch

from core.controllers import SelectionDialog as selection_module
from core.controllers.SelectionDialog import SelectionDialog


def test_selection_dialog_runs_startup_update_check(qtbot):
    """The automatic update check is wired on the initial selection dialog.

    The prompt must appear before the user chooses Images / Real-time / Flight
    Viewer, so the UpdateController and its startup check live here rather than
    in MainWindow / StreamViewerWindow.
    """
    with patch.object(selection_module, "UpdateController") as mock_controller_cls, \
            patch.object(selection_module, "SettingsService") as mock_settings_cls:
        mock_settings = mock_settings_cls.return_value
        mock_settings.get_setting.return_value = "2.1.0 Beta 1"

        dialog = SelectionDialog("Dark")
        qtbot.addWidget(dialog)

    # Controller constructed with the dialog as parent so prompts are modal to it.
    mock_controller_cls.assert_called_once()
    _, kwargs = mock_controller_cls.call_args
    assert mock_controller_cls.call_args.args[0] is dialog
    assert kwargs["settings_service"] is mock_settings

    # The startup check is scheduled exactly once.
    dialog.update_controller.schedule_startup_check.assert_called_once_with()

    # app_version is sourced from settings for the version comparison / User-Agent.
    assert dialog.app_version == "2.1.0 Beta 1"


def test_flight_viewer_button_hidden_when_feature_disabled(qtbot):
    """Flight Viewer is deferred to a later release: while
    FeatureFlags.FLIGHT_VIEWER_ENABLED is False the Selection dialog must
    hide its button so the feature is unreachable."""
    with patch.object(selection_module, "UpdateController"), \
            patch.object(selection_module, "SettingsService"):
        dialog = SelectionDialog("Dark")
        qtbot.addWidget(dialog)

    assert selection_module.FeatureFlags.FLIGHT_VIEWER_ENABLED is False
    # The whole third column is hidden (not just the button), so it stops
    # consuming layout width. isHidden() reflects the explicit hide flag even
    # before the dialog is shown (isVisible() would be False either way).
    assert dialog.flightWidget.isHidden()
    assert dialog.streamWidget.isVisible() or not dialog.streamWidget.isHidden()
    # Dialog shrinks below the three-button design width (600). The exact
    # width is font/DPI-dependent (the heading label can set the floor), so
    # assert the relationship rather than a pixel value.
    assert dialog.width() < 600
    # Height is unchanged from the .ui design (two rows are identical).
    assert dialog.height() == 290


def test_flight_viewer_button_shown_when_feature_enabled(qtbot):
    """Flipping the flag restores the button (the later-release path)."""
    with patch.object(selection_module.FeatureFlags, "FLIGHT_VIEWER_ENABLED", True), \
            patch.object(selection_module, "UpdateController"), \
            patch.object(selection_module, "SettingsService"):
        dialog = SelectionDialog("Dark")
        qtbot.addWidget(dialog)

    assert not dialog.flightWidget.isHidden()
    # Three-button layout keeps its designed size.
    assert dialog.width() == 600
