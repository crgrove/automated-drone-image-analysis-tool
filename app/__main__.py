# Set environment variable to avoid numpy._core issues - MUST be first
import traceback
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from multiprocessing import freeze_support
from helpers.PickleHelper import PickleHelper
from helpers.TranslationHelper import install_translator
from helpers.ThemeHelper import apply_theme
from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.controllers.streaming.StreamingGuide import StreamingGuide
from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
from core.controllers.images.MainWindow import MainWindow
from core.controllers.SelectionDialog import SelectionDialog
from core.controllers.images.ImageAnalysisGuide import ImageAnalysisGuide
import faulthandler
import qdarktheme
from os import path
import sys
import os
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'


version = '2.1.0'


def update_app_version(app_version):
    """Update the app version setting if necessary.

    Updates the version setting if:
    1. No version is stored (first run)
    2. New app version is greater than stored version
    3. App version is full (release) and stored version is Beta

    Args:
        app_version (str): The current application version string.
    """
    logger = LoggerService()
    settings_service = SettingsService()

    try:
        current_version = settings_service.get_setting('app_version')

        # Update version if not set (first run)
        if current_version is None:
            settings_service.set_setting('app_version', app_version)
            # logger.info(f"Set app version to {app_version} (first run)")
            return

        # Parse versions to check for Beta -> Full upgrade
        try:
            current_tuple = PickleHelper._version_to_tuple(current_version)
            app_tuple = PickleHelper._version_to_tuple(app_version)

            # Check if app version is full (label_val = 0) and current is Beta (label_val = 2)
            is_app_full = app_tuple[3] == 0  # label_val = 0 means release/full
            is_current_beta = current_tuple[3] == 2  # label_val = 2 means Beta

            # Update if: numeric version is greater OR (app is full AND current is Beta)
            current_version_int = PickleHelper.version_to_int(current_version)
            new_version_int = PickleHelper.version_to_int(app_version)

            if new_version_int > current_version_int or (is_app_full and is_current_beta):
                settings_service.set_setting('app_version', app_version)
                if is_app_full and is_current_beta:
                    # logger.info(f"Updated app version from Beta to full release: {current_version} -> {app_version}")
                    pass
                else:
                    # logger.info(f"Updated app version: {current_version} -> {app_version}")
                    pass
        except (ValueError, AttributeError) as e:
            # If version parsing fails, update to current version
            logger.warning(f"Failed to parse version strings, updating to {app_version}: {e}")
            settings_service.set_setting('app_version', app_version)

    except Exception as e:
        logger.error(f"Error updating app version: {e}")


def initialize_default_settings():
    """Initialize default application settings if they don't exist.

    This should be called early in application startup, before any windows
    are created, to ensure settings are available throughout the application.
    """
    logger = LoggerService()
    settings_service = SettingsService()

    try:
        # MaxAOIs
        max_aois = settings_service.get_setting('MaxAOIs')
        if not isinstance(max_aois, int):
            settings_service.set_setting('MaxAOIs', 100)

        # AOIRadius
        aoi_radius = settings_service.get_setting('AOIRadius')
        if not isinstance(aoi_radius, int):
            settings_service.set_setting('AOIRadius', 15)

        # PositionFormat
        position_format = settings_service.get_setting('PositionFormat')
        if not isinstance(position_format, str):
            settings_service.set_setting('PositionFormat', 'Lat/Long - Decimal Degrees')

        # TemperatureUnit
        temperature_unit = settings_service.get_setting('TemperatureUnit')
        if not isinstance(temperature_unit, str):
            settings_service.set_setting('TemperatureUnit', 'Fahrenheit')

        # DistanceUnit
        distance_unit = settings_service.get_setting('DistanceUnit')
        # logger.info(f"initialize_default_settings: DistanceUnit = {repr(distance_unit)}")
        # Set default if not set, is None, empty, or not a valid value
        if distance_unit is None or (isinstance(distance_unit, str) and distance_unit == ''):
            # Setting doesn't exist or is empty - set default to 'Feet'
            # logger.info("initialize_default_settings: Setting DistanceUnit to 'Feet' (was None or empty)")
            settings_service.set_setting('DistanceUnit', 'Feet')
        elif isinstance(distance_unit, str):
            # Check if it's a legacy value that needs migration
            if distance_unit in ('ft', 'm'):
                settings_service.set_setting('DistanceUnit', 'Feet' if distance_unit == 'ft' else 'Meters')
            elif distance_unit not in ('Feet', 'Meters'):
                # Invalid value - set default to 'Feet'
                settings_service.set_setting('DistanceUnit', 'Feet')
        else:
            # Not a string (unexpected type) - set default to 'Feet'
            settings_service.set_setting('DistanceUnit', 'Feet')

        # Theme
        theme = settings_service.get_setting('Theme')
        if theme is None:
            settings_service.set_setting('Theme', 'Dark')

        # Update checks
        auto_check_updates = settings_service.get_setting('AutoCheckForUpdates')
        if not isinstance(auto_check_updates, bool):
            settings_service.set_setting('AutoCheckForUpdates', True)

    except Exception as e:
        logger.error(f"Error initializing default settings: {e}")
        logger.error(traceback.format_exc())


def check_and_update_pickle_files(app_version):
    """Ensure the bundled drones.csv / xmp.csv lookup tables are present and current.

    Runs at startup. Re-copies the bundled file when the stored app version
    advances; PickleHelper itself also auto-refreshes when the bundled
    file's version header advertises a newer revision.

    Args:
        app_version (str): The current application version string.
    """
    logger = LoggerService()
    settings_service = SettingsService()

    try:
        current_version = settings_service.get_setting('app_version')

        # Copy drones.csv if:
        # 1. No app version is stored (first run)
        # 2. No drone sensor file exists in AppData
        # 3. New app version is greater than stored version
        if current_version is None or PickleHelper.get_drone_sensor_file_version() is None:
            PickleHelper.copy_pickle('drones.csv')
        else:
            current_version_int = PickleHelper.version_to_int(current_version)
            new_version_int = PickleHelper.version_to_int(app_version)
            if new_version_int > current_version_int:
                PickleHelper.copy_pickle('drones.csv')

        # Ensure xmp.csv exists
        if PickleHelper.get_xmp_mapping() is None:
            PickleHelper.copy_pickle('xmp.csv')

    except Exception as e:
        logger.error(f"Error checking/updating data files: {e}")


def main():
    """Initialize the application and launch the appropriate window.

    Sets up the QApplication, applies the dark theme, sets the application icon,
    and displays either the MainWindow (for image analysis) or StreamViewerWindow
    (for streaming) based on user selection. Ends the application on window close.

    The function first shows a SelectionDialog to allow the user to choose between
    Images and Streaming modes. For Images mode, it may optionally show an
    ImageAnalysisGuide wizard before opening the MainWindow.
    """
    app = QApplication(sys.argv)

    # Load translation. Priority: the saved Language preference, then the OS
    # locale, then English. Resolves the .qm location via sys._MEIPASS so it
    # works identically from source and from a PyInstaller build on Windows
    # and macOS (see helpers.TranslationHelper).
    settings_service = SettingsService()
    install_translator(app, settings_service.get_setting('Language', None))

    # Apply the stylesheet AND the full palette (see helpers.ThemeHelper): the
    # palette must be pinned to the theme so custom-painted widgets don't pick
    # up the OS light/dark text colour.
    apply_theme('Dark')
    app.setWindowIcon(QIcon(path.abspath(path.join(path.dirname(__file__), 'ADIAT.ico'))))

    # Initialize default settings early (before any windows are created)
    initialize_default_settings()

    # Check and update pickle files on every startup (must be before version update)
    check_and_update_pickle_files(version)

    # Update app version setting (independent of pickle operations)
    update_app_version(version)

    # Show selection dialog first; launch MainWindow when Images is chosen
    dlg = SelectionDialog('Dark')

    wizard_shown = False

    def _launch_stream_viewer(wizard_data=None):
        """
        Launch the stream viewer window with optional wizard data.

        Args:
            wizard_data: Optional dictionary containing wizard configuration data.
                If provided, the algorithm name will be extracted from this data.
        """
        algorithm_name = 'ColorAnomalyAndMotionDetection'
        if wizard_data and wizard_data.get('algorithm'):
            algorithm_name = wizard_data.get('algorithm')
        try:
            app._stream_viewer = StreamViewerWindow(algorithm_name=algorithm_name, theme='dark')
            if wizard_data:
                app._stream_viewer.apply_wizard_data(wizard_data)
            app._stream_viewer.show()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to open Real-time Stream Detection:\n{str(e)}"
            )
            sys.exit(1)

    def _launch_flight_viewer():
        """Launch the Flight Viewer window (WebRTC pairing with ADIAT Mobile)."""
        try:
            from core.controllers.flight import FlightViewerController
            app._flight_controller = FlightViewerController()
            app._flight_controller.show()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to open Flight Viewer:\n{str(e)}"
            )
            sys.exit(1)

    # Connect signal to launch MainWindow when Images is selected
    def _on_selection(choice: str):
        """
        Handle selection choice from the initial dialog.

        Args:
            choice: String indicating the selected option ('images', 'stream',
                or 'flight').
        """
        if choice == 'images':
            # Wrap startup in a try so any init error raises to excepthook
            try:
                app._main_window = MainWindow(qdarktheme)
                app._main_window.show()
            except Exception:
                # Re-raise so our global excepthook handles exit
                raise
        elif choice == 'stream':
            _launch_stream_viewer()
        elif choice == 'flight':
            _launch_flight_viewer()

    # Connect signal to show setup wizard when requested
    def _on_wizard_requested():
        """
        Handle request to show the image analysis guide wizard.

        Sets the wizard_shown flag and launches the ImageAnalysisGuide.
        """
        nonlocal wizard_shown
        wizard_shown = True
        # Dialog is already hidden, now show wizard
        wizard = ImageAnalysisGuide()

        # Connect to wizard completion signal to populate MainWindow
        wizard_data_from_wizard = None
        review_file_path = None

        def _on_wizard_completed(wizard_data):
            nonlocal wizard_data_from_wizard
            wizard_data_from_wizard = wizard_data

        def _on_review_requested(file_path):
            nonlocal review_file_path
            review_file_path = file_path

        wizard.wizardCompleted.connect(_on_wizard_completed)
        wizard.reviewRequested.connect(_on_review_requested)
        wizard_result = wizard.exec()

        # After wizard completes (or is cancelled), proceed with MainWindow
        # Whether accepted or cancelled, open MainWindow
        dlg.selection = "images"  # Set selection so dialog knows what was chosen

        # Check if review was requested
        if review_file_path:
            # Review mode: open MainWindow, load XML, and open Viewer
            app._main_window = MainWindow(qdarktheme)
            app._main_window.show()

            # Load the XML file
            try:
                app._main_window._process_xml_file(review_file_path)
                # A Search Coordinator project is already opened by
                # _process_xml_file; otherwise open the single-run Viewer.
                if app._main_window._view_results_mode != 'coordinator':
                    app._main_window._viewResultsButton_clicked()
            except Exception as e:
                QMessageBox.critical(
                    app._main_window,
                    "Error Loading Results",
                    f"Failed to load results file:\n{str(e)}"
                )
        else:
            # Normal wizard flow
            app._main_window = MainWindow(qdarktheme)

            # Populate MainWindow with wizard data if wizard was completed (not cancelled)
            if wizard_result == QDialog.Accepted and wizard_data_from_wizard:
                # Mark for auto-start
                wizard_data_from_wizard['auto_start'] = True
                app._main_window.populate_from_wizard_data(wizard_data_from_wizard)

            app._main_window.show()

        dlg.accept()  # Close selection dialog (already hidden, but this ensures cleanup)

    def _on_stream_wizard_requested():
        """
        Handle request to show the streaming guide wizard.

        Creates and shows the StreamingGuide dialog, then launches the stream
        viewer with the wizard data if the wizard is accepted.
        """
        wizard = StreamingGuide()
        wizard_data_from_wizard = None

        def _on_wizard_completed(wizard_data):
            nonlocal wizard_data_from_wizard
            wizard_data_from_wizard = wizard_data

        wizard.wizardCompleted.connect(_on_wizard_completed)
        wizard_result = wizard.exec()
        dlg.selection = "stream"

        if wizard_result == QDialog.Accepted and wizard_data_from_wizard:
            _launch_stream_viewer(wizard_data_from_wizard)
        else:
            _launch_stream_viewer()

    dlg.selectionMade.connect(_on_selection)
    dlg.wizardRequested.connect(_on_wizard_requested)
    dlg.streamWizardRequested.connect(_on_stream_wizard_requested)
    # `flightViewerRequested` is emitted alongside selectionMade('flight');
    # the launch already happens via _on_selection. Connect anyway so the
    # signal has at least one consumer for callers that watch it directly.
    dlg.flightViewerRequested.connect(lambda: None)
    result = dlg.exec()

    # If dialog was closed without a selection (and wizard wasn't shown), exit the app
    if result != QDialog.Accepted or (dlg.selection is None and not wizard_shown):
        sys.exit(0)

    sys.exit(app.exec())


if __name__ == "__main__":
    # Enable faulthandler for crash tracebacks (skip Windows where it catches
    # benign COM exceptions like RPC_E_WRONGTHREAD 0x8001010d from Qt internals)
    if sys.stderr is not None and sys.platform != 'win32':
        faulthandler.enable()
    # Install a global exception hook that exits the app on any uncaught error

    def _fatal_excepthook(exctype, value, tb):
        """Handle uncaught exceptions by printing traceback and exiting cleanly.

        Args:
            exctype: The exception class.
            value: The exception instance.
            tb: The traceback object.
        """
        # Print full traceback to stderr for debugging
        traceback.print_exception(exctype, value, tb)
        # Try to stop a running Qt event loop cleanly
        try:
            inst = QApplication.instance()
            if inst is not None:
                inst.quit()
        except Exception:
            pass
        # Ensure process terminates with non-zero status so it doesn't hang
        os._exit(1)

    sys.excepthook = _fatal_excepthook

    freeze_support()

    # Logging policy (baked in): packaged/production builds record warnings and
    # errors only; running from source stays verbose (DEBUG). Override in the
    # field with the ADIAT_LOG_LEVEL env var (e.g. ADIAT_LOG_LEVEL=DEBUG). This
    # runs before both the GUI and the batch CLI so both honor it; see
    # LoggerService.resolve_log_level. (LoggerService also applies this by
    # default, so any earlier log line is already at the right level.)
    LoggerService.set_level()

    # Headless batch mode: "python app batch --input <parent> --output <root>"
    # (or "ADIAT.exe batch ..." in the packaged build).
    # Falls through to the normal GUI startup when no batch subcommand is given.
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        # The packaged Windows exe is windowed (console=False): attach to the
        # calling terminal so CLI progress/errors are visible. No-op for GUI
        # launches and on macOS/Linux.
        from helpers.ConsoleHelper import attach_parent_console
        attach_parent_console()
        from core.services.cli.BatchCLI import run_batch_cli
        sys.exit(run_batch_cli(sys.argv[2:]))

    main()
