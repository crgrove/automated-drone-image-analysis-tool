# Set environment variable to avoid numpy._core issues - MUST be first
from os import path
import qdarktheme
import faulthandler
from core.controllers.images.ImageAnalysisGuide import ImageAnalysisGuide
from core.controllers.SelectionDialog import SelectionDialog
from core.controllers.images.MainWindow import MainWindow
from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
from multiprocessing import freeze_support
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtGui import QIcon
import traceback
import sys
import os
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'


version = '2.0.0'


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
    qdarktheme.setup_theme()
    app.setWindowIcon(QIcon(path.abspath(path.join(path.dirname(__file__), 'ADIAT.ico'))))

    # Show selection dialog first; launch MainWindow when Images is chosen
    dlg = SelectionDialog('Dark')

    wizard_shown = False

    # Connect signal to launch MainWindow when Images is selected
    def _on_selection(choice: str):
        if choice == 'images':
            # Wrap startup in a try so any init error raises to excepthook
            try:
                app._main_window = MainWindow(qdarktheme, version)
                app._main_window.show()
            except Exception:
                # Re-raise so our global excepthook handles exit
                raise
        elif choice == 'stream':
            # Launch the Real-time streaming detection window (new architecture)
            try:
                # Default to ColorAnomalyAndMotionDetection algorithm
                app._stream_viewer = StreamViewerWindow(algorithm_name='ColorAnomalyAndMotionDetection', theme='dark')
                app._stream_viewer.show()
            except Exception as e:
                QMessageBox.critical(
                    None,
                    "Error",
                    f"Failed to open Real-time Stream Detection:\n{str(e)}"
                )
                sys.exit(1)

    # Connect signal to show setup wizard when requested
    def _on_wizard_requested():
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
            app._main_window = MainWindow(qdarktheme, version)
            app._main_window.show()
            
            # Load the XML file
            try:
                app._main_window._process_xml_file(review_file_path)
                # Automatically open the Viewer
                app._main_window._viewResultsButton_clicked()
            except Exception as e:
                QMessageBox.critical(
                    app._main_window,
                    "Error Loading Results",
                    f"Failed to load results file:\n{str(e)}"
                )
        else:
            # Normal wizard flow
            app._main_window = MainWindow(qdarktheme, version)

            # Populate MainWindow with wizard data if wizard was completed (not cancelled)
            if wizard_result == QDialog.Accepted and wizard_data_from_wizard:
                # Mark for auto-start
                wizard_data_from_wizard['auto_start'] = True
                app._main_window.populate_from_wizard_data(wizard_data_from_wizard)

            app._main_window.show()
        
        dlg.accept()  # Close selection dialog (already hidden, but this ensures cleanup)

    dlg.selectionMade.connect(_on_selection)
    dlg.wizardRequested.connect(_on_wizard_requested)
    result = dlg.exec()

    # If dialog was closed without a selection (and wizard wasn't shown), exit the app
    if result != QDialog.Accepted or (dlg.selection is None and not wizard_shown):
        sys.exit(0)

    sys.exit(app.exec())


if __name__ == "__main__":
    # Enable faulthandler only if stderr is available (avoid issues in packaged apps)
    if sys.stderr is not None:
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
    main()
