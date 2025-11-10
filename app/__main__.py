# Set environment variable to avoid numpy._core issues - MUST be first
import os
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'

import sys
import traceback
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog
from multiprocessing import freeze_support
from core.controllers.images.MainWindow import MainWindow
from core.controllers.SelectionDialog import SelectionDialog
from core.controllers.images.ImageAnalysisGuide import ImageAnalysisGuide
import faulthandler
import qdarktheme
from os import path

version = '2.0.0'


def main():
    """
    Initialize the application, set the theme, icon, and launch the main window.

    The function sets up the QApplication, applies the dark theme, sets the application icon,
    and displays the MainWindow with the specified version. Ends the application on window close.
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
            # Launch the Real-time anomaly detector (Integrated Detection Viewer)
            try:
                from core.controllers.streaming.IntegratedDetectionViewer import IntegratedDetectionViewer
                app._integrated_viewer = IntegratedDetectionViewer()
                app._integrated_viewer.show()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    None,
                    "Error",
                    f"Failed to open Real-time Anomaly Detector:\n{str(e)}"
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
        def _on_wizard_completed(wizard_data):
            nonlocal wizard_data_from_wizard
            wizard_data_from_wizard = wizard_data
        
        wizard.wizardCompleted.connect(_on_wizard_completed)
        wizard_result = wizard.exec()
        
        # After wizard completes (or is cancelled), proceed with MainWindow
        # Whether accepted or cancelled, open MainWindow
        dlg.selection = "images"  # Set selection so dialog knows what was chosen
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
        # Print full traceback to stderr for debugging
        traceback.print_exception(exctype, value, tb)
        # Try to stop a running Qt event loop cleanly
        try:
            from PySide6.QtWidgets import QApplication
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
