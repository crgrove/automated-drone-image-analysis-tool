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


def _build_dialog(qtbot, *, review=True, flight=True):
    """Construct the dialog with both release flags pinned explicitly.

    Every layout assertion below depends on which tiles are showing, so no
    test may inherit the shipping defaults - flipping a flag in
    helpers/FeatureFlags.py must not silently change what a test covers.
    """
    with patch.object(selection_module.FeatureFlags, "REVIEW_RESULTS_ENABLED", review), \
            patch.object(selection_module.FeatureFlags, "FLIGHT_VIEWER_ENABLED", flight), \
            patch.object(selection_module, "UpdateController"), \
            patch.object(selection_module, "SettingsService"):
        dialog = SelectionDialog("Dark")
        qtbot.addWidget(dialog)
    return dialog


def test_flight_viewer_button_hidden_when_feature_disabled(qtbot):
    """Flight Viewer visibility is gated: when
    FeatureFlags.FLIGHT_VIEWER_ENABLED is False the Selection dialog must
    hide its button so the feature is unreachable. The flag is patched
    explicitly so the gated-off path stays covered regardless of the
    shipping default."""
    dialog = _build_dialog(qtbot, review=True, flight=False)

    # The whole fourth column is hidden (not just the button), so it stops
    # consuming layout width. isHidden() reflects the explicit hide flag even
    # before the dialog is shown (isVisible() would be False either way).
    assert dialog.flightWidget.isHidden()
    assert dialog.streamWidget.isVisible() or not dialog.streamWidget.isHidden()
    # Dialog shrinks below the full design width (770). The exact width is
    # font/DPI-dependent (the heading label can set the floor), so assert the
    # relationship rather than a pixel value.
    assert dialog.width() < 770
    # Height is unchanged from the .ui design (two rows are identical).
    assert dialog.height() == 290


def test_flight_viewer_button_shown_when_feature_enabled(qtbot):
    """With the flag enabled the button is restored (the shipping path)."""
    dialog = _build_dialog(qtbot, review=True, flight=True)

    assert not dialog.flightWidget.isHidden()
    # Full four-tile layout keeps its designed size (Image / Review Results /
    # Stream / Flight Viewer).
    assert dialog.width() == 770


def test_flight_viewer_disabled_by_default():
    """Flight Viewer is held back from the current release build.

    This guards the shipping default in the same way the previous assertion
    guarded the enabled state: it catches an accidental flip, so re-enabling
    has to be a deliberate edit here and in helpers/FeatureFlags.py.
    """
    assert selection_module.FeatureFlags.FLIGHT_VIEWER_ENABLED is False


def test_review_results_tile_hidden_when_feature_disabled(qtbot):
    """Review Results is gated the same way Flight Viewer is.

    With FeatureFlags.REVIEW_RESULTS_ENABLED False the whole column is
    hidden and the click handler is left unconnected, so the review entry
    point is unreachable from the dialog even programmatically.
    """
    dialog = _build_dialog(qtbot, review=False, flight=True)

    assert dialog.resultsWidget.isHidden()
    assert not dialog.imageWidget.isHidden()
    assert not dialog.streamWidget.isHidden()
    assert dialog.width() < 770
    assert dialog.height() == 290

    # Unconnected: clicking the hidden button (click() works regardless of
    # visibility) must not select or signal anything.
    requested = []
    dialog.reviewResultsRequested.connect(lambda: requested.append(True))
    dialog.resultsButton.click()
    assert dialog.selection is None
    assert requested == []


def test_both_deferred_tiles_hidden_leaves_two_centered(qtbot):
    """Hiding both deferred tiles collapses to Image / Stream only.

    The centering stretches are inserted once, not once per hidden tile, so
    the surviving pair stays grouped under the heading.
    """
    dialog = _build_dialog(qtbot, review=False, flight=False)

    assert dialog.resultsWidget.isHidden()
    assert dialog.flightWidget.isHidden()
    assert not dialog.imageWidget.isHidden()
    assert not dialog.streamWidget.isHidden()

    layout = dialog.horizontalLayout_2
    # 4 tile columns + exactly one leading and one trailing stretch.
    assert layout.count() == 6
    assert layout.itemAt(0).spacerItem() is not None
    assert layout.itemAt(layout.count() - 1).spacerItem() is not None
    assert all(layout.itemAt(i).spacerItem() is None for i in range(1, layout.count() - 1))

    # Narrower than the three-tile layout, designed height preserved.
    assert dialog.width() < 770
    assert dialog.height() == 290


def test_review_results_disabled_by_default():
    """Review Results is held back from the current release build.

    Guards the shipping default so re-enabling has to be a deliberate edit
    here and in helpers/FeatureFlags.py.
    """
    assert selection_module.FeatureFlags.REVIEW_RESULTS_ENABLED is False


def test_review_results_tile_emits_selection(qtbot):
    """The Review Results tile records the choice and signals __main__.

    The dedicated signal fires after accept() so the handler constructs the
    MainWindow with the dialog already dismissed, mirroring the flight tile.
    Covers the path that ships when REVIEW_RESULTS_ENABLED is flipped back on.
    """
    dialog = _build_dialog(qtbot, review=True, flight=True)

    selections = []
    requested = []
    dialog.selectionMade.connect(selections.append)
    dialog.reviewResultsRequested.connect(lambda: requested.append(True))

    dialog.resultsButton.click()

    assert dialog.selection == "results"
    assert selections == ["results"]
    assert requested == [True]
