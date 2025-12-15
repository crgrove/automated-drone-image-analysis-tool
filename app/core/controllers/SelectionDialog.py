from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog

from core.views.SelectionDialog_ui import Ui_MediaSelector
from core.services.SettingsService import SettingsService
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

        self._apply_icons(theme)

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

    def _apply_icons(self, theme: str) -> None:
        """Apply themed icons to the dialog buttons.

        Args:
            theme: Theme name to use for icons ('Dark' or 'Light').
        """
        try:
            self.imageButton.setIcon(IconHelper.create_icon("fa6s.image", theme))
            # Use a broadly available Material icon for streaming/video
            self.streamButton.setIcon(IconHelper.create_icon("fa6s.video", theme))
        except Exception:
            # Icons are non-critical; ignore if assets are not available yet
            pass
