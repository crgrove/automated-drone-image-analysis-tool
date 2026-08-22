from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog

from core.controllers.UpdateController import UpdateController
from core.views.SelectionDialog_ui import Ui_MediaSelector
from core.services.SettingsService import SettingsService
from helpers import FeatureFlags
from helpers.IconHelper import IconHelper


class SelectionDialog(QDialog, Ui_MediaSelector):
    """Controller for the media selection dialog.

    Allows users to choose between Images and Streaming modes. Exposes a simple
    API where clicking a button records the selection and closes the dialog
    with accept(). Consumers can either connect to the selectionMade signal or
    inspect the `selection` attribute after exec(). When setup guides are not
    skipped, dedicated signals are emitted so callers can launch the guides
    after the dialog closes.

    Attributes:
        selectionMade: Signal emitted when a selection is made. Emits the
            selection string ("images" or "stream").
        wizardRequested: Signal emitted when the setup wizard should be shown
            (for Images mode).
        streamWizardRequested: Signal emitted when the streaming setup wizard
            should be shown (for Streaming mode).
        selection: The current selection string ("images" or "stream") or None.
        settings_service: Instance of SettingsService for accessing settings.
    """

    selectionMade = Signal(str)
    wizardRequested = Signal()  # Signal emitted when image setup wizard should be shown
    streamWizardRequested = Signal()  # Signal emitted when streaming setup wizard should be shown
    flightViewerRequested = Signal()  # Signal emitted when Flight Viewer should be opened
    reviewResultsRequested = Signal()  # Signal emitted when Review Results should be opened

    def __init__(self, theme: str):
        """Initialize the selection dialog.

        Args:
            theme: Theme name to use for icons ('Dark' or 'Light').
        """
        super().__init__()
        self.setupUi(self)

        self.settings_service = SettingsService()

        self.selection: str | None = None

        # Consistent tooltip styling across dialogs
        self.setStyleSheet(
            """
            QToolTip {
                background-color: lightblue;
                color: black;
                border: 1px solid #333333;
                padding: 4px;
                font-size: 11px;
            }
            """
        )

        self.imageButton.clicked.connect(self._on_image_clicked)
        self.streamButton.clicked.connect(self._on_stream_clicked)
        if hasattr(self, "resultsButton") and FeatureFlags.REVIEW_RESULTS_ENABLED:
            self.resultsButton.clicked.connect(self._on_results_clicked)
        if hasattr(self, "flightButton") and FeatureFlags.FLIGHT_VIEWER_ENABLED:
            self.flightButton.clicked.connect(self._on_flight_clicked)
        self._hide_deferred_tiles()

        self._apply_icons(theme)

        # Run the startup update check here, on the initial selection dialog,
        # so any "Update Available" prompt is shown before the user commits to
        # Images, Real-time, or Flight Viewer. The check is deferred via a timer
        # and guarded to run once per session (see UpdateController).
        self.app_version = self.settings_service.get_setting('app_version', '2.0.0') or '2.0.0'
        self.update_controller = UpdateController(self, settings_service=self.settings_service)
        self.update_controller.schedule_startup_check()

    def _tile_columns(self):
        """Return the dialog's tile columns as ``(widget, enabled)`` pairs.

        Order matches the .ui layout. ``enabled`` is the release switch for
        that tile; Images and Streaming always ship. Missing attributes are
        tolerated so a stale generated UI module cannot break startup.
        """
        return [
            (getattr(self, "imageWidget", None), True),
            (getattr(self, "resultsWidget", None), FeatureFlags.REVIEW_RESULTS_ENABLED),
            (getattr(self, "streamWidget", None), True),
            (getattr(self, "flightWidget", None), FeatureFlags.FLIGHT_VIEWER_ENABLED),
        ]

    def _hide_deferred_tiles(self) -> None:
        """Remove the tiles whose features are held back from this release and
        tighten the dialog around the options that remain.

        Hiding just a button leaves its Expanding column claiming its share of
        the width; hiding the whole column widget removes it. The surviving
        tiles are then switched from Expanding to Maximum and wrapped in a
        single pair of stretches so they stay grouped and centered under the
        heading rather than spreading to the edges (the heading label can be
        wider than the tiles and would otherwise drive them apart). Finally the
        dialog shrinks to its natural width for the tiles that are left.
        """
        from PySide6.QtWidgets import QSizePolicy

        columns = self._tile_columns()
        hidden = [w for w, enabled in columns if w is not None and not enabled]
        if not hidden:
            return

        designed_height = self.height()  # keep the .ui height (rows are unchanged)

        for tile in hidden:
            tile.setVisible(False)

        for tile, enabled in columns:
            if tile is None or not enabled:
                continue
            policy = tile.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Maximum)
            tile.setSizePolicy(policy)

        # Center what is left: [stretch] tile ... tile [stretch]. Inserted once,
        # however many columns were hidden.
        self.horizontalLayout_2.insertStretch(0, 1)
        self.horizontalLayout_2.addStretch(1)

        # Shrink to the natural width for the remaining tiles; adjustSize also
        # grows the height, so restore the designed height afterward.
        self.adjustSize()
        self.resize(self.width(), designed_height)

    def _on_image_clicked(self) -> None:
        """Handle click on the Images button.

        Sets selection to "images" and either proceeds directly (if wizard is
        skipped) or emits wizardRequested signal to show the setup wizard first.
        """
        self.selection = "images"

        # Check if setup wizard should be shown
        skip_wizard = self.settings_service.get_setting('SkipImageAnalysisGuide', 'No')
        # Ensure we're comparing strings (QSettings might return different types)
        skip_wizard_str = str(skip_wizard).strip()

        if skip_wizard_str == 'Yes':
            # Wizard is skipped, proceed normally
            self.selectionMade.emit(self.selection)
            self.accept()
        else:
            # Show setup wizard first
            # Close this dialog before showing wizard
            self.accept()  # Close the dialog
            self.wizardRequested.emit()  # Signal will be handled after dialog closes

    def _on_stream_clicked(self) -> None:
        """Handle click on the Stream button.

        Sets selection to "stream", emits the selectionMade signal, and closes
        the dialog. The viewer will be created in __main__.py via the signal handler.
        """
        self.selection = "stream"

        skip_wizard = self.settings_service.get_setting('SkipStreamingGuide', 'No')
        skip_wizard_str = str(skip_wizard).strip()

        if skip_wizard_str == 'Yes':
            self.selectionMade.emit(self.selection)
            self.accept()
        else:
            self.accept()
            self.streamWizardRequested.emit()

    def _on_results_clicked(self) -> None:
        """Handle click on the Review Results button.

        Sets selection to "results", emits both selectionMade and the
        dedicated reviewResultsRequested signal, and closes the dialog. The
        review flow (results-folder scan / recents) is driven from
        __main__.py via the signal handler.
        """
        self.selection = "results"
        self.selectionMade.emit(self.selection)
        self.accept()
        self.reviewResultsRequested.emit()

    def _on_flight_clicked(self) -> None:
        """Handle click on the Flight Viewer button.

        Sets selection to "flight", emits both selectionMade and the
        dedicated flightViewerRequested signal, and closes the dialog. The
        viewer window is constructed in __main__.py via the signal handler.
        """
        self.selection = "flight"
        self.selectionMade.emit(self.selection)
        self.accept()
        self.flightViewerRequested.emit()

    def _apply_icons(self, theme: str) -> None:
        """Apply themed icons to the dialog buttons.

        Args:
            theme: Theme name to use for icons ('Dark' or 'Light').
        """
        try:
            self.imageButton.setIcon(IconHelper.create_icon("fa6s.image", theme))
            # Use a broadly available Material icon for streaming/video
            self.streamButton.setIcon(IconHelper.create_icon("fa6s.video", theme))
            if hasattr(self, "resultsButton"):
                # Folder-with-magnifier reads as "open results for review"
                self.resultsButton.setIcon(IconHelper.create_icon("fa6s.folder-open", theme))
            if hasattr(self, "flightButton"):
                # Drone icon for the WebRTC flight viewer
                self.flightButton.setIcon(IconHelper.create_icon("mdi6.quadcopter", theme))
        except Exception:
            # Icons are non-critical; ignore if assets are not available yet
            pass
