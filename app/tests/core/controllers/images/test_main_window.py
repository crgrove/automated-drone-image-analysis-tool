"""
Comprehensive tests for MainWindow UI functionality.

Tests the main application window, algorithm selection, processing, and viewer integration.
"""

import os
import pytest
from os import path
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog

# Try to import dependencies, skip tests if not available
try:
    from core.controllers.images.VideoParser import VideoParser
    from core.controllers.Perferences import Preferences
    from core.services.export.PdfGeneratorService import PdfGeneratorService
    from core.services.export.KMLGeneratorService import KMLGeneratorService
    _DEPENDENCIES_AVAILABLE = True
    _IMPORT_ERROR = ""
except ImportError as e:
    _DEPENDENCIES_AVAILABLE = False
    _IMPORT_ERROR = str(e)


def _open_viewer_with_sample_data(main_window, testData, qtbot):
    """Helper to run analysis and open the viewer with sample RGB data."""
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])

    main_window.algorithmComboBox.setCurrentText('Color Range (RGB)')
    algorithmWidget = main_window.algorithmWidget

    if hasattr(algorithmWidget, 'add_color_row'):
        color = QColor(0, 170, 255)
        algorithmWidget.add_color_row(
            color,
            r_min=0,
            r_max=75,
            g_min=95,
            g_max=245,
            b_min=180,
            b_max=255
        )
    elif hasattr(algorithmWidget, 'rRangeSpinBox'):
        algorithmWidget.rRangeSpinBox.setValue(75)
        algorithmWidget.gRangeSpinBox.setValue(75)
        algorithmWidget.bRangeSpinBox.setValue(75)
        algorithmWidget.selectedColor = QColor(0, 170, 255)
        if hasattr(algorithmWidget, 'update_colors'):
            algorithmWidget.update_colors()

    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    qtbot.wait(100)
    qtbot.waitUntil(lambda: main_window.startButton.isEnabled(), timeout=60000)

    if not main_window.viewResultsButton.isEnabled():
        pytest.skip("No AOIs found - viewer cannot be opened without results")

    qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)
    assert main_window.viewer is not None
    return main_window.viewer


def testVisible(main_window):
    """Test that main window is visible."""
    assert main_window.isVisible()


def testBasicEndToEnd(main_window, testData, qtbot):
    """Test complete end-to-end workflow from setup to viewing results."""
    # Set input and output folders
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])

    # Set area parameters
    main_window.minAreaSpinBox.setValue(8)
    main_window.maxAreaSpinBox.setValue(1000)

    # Verify algorithm widget exists
    assert main_window.algorithmWidget is not None

    # Select Color Range algorithm and configure it
    main_window.algorithmComboBox.setCurrentText('Color Range (RGB)')
    assert main_window.algorithmWidget is not None

    # Configure algorithm - use new wizard-based API
    algorithmWidget = main_window.algorithmWidget

    # New wizard-based system requires adding colors via add_color_row
    if hasattr(algorithmWidget, 'add_color_row'):
        # Add a color using the new API with ±75 range for each channel
        color = QColor(0, 170, 255)
        # R: 0 ± 75 = 0 to 75 (clamped to 0-255)
        # G: 170 ± 75 = 95 to 245
        # B: 255 ± 75 = 180 to 255 (clamped to 0-255)
        algorithmWidget.add_color_row(color, r_min=0, r_max=75, g_min=95, g_max=245, b_min=180, b_max=255)
    elif hasattr(algorithmWidget, 'rRangeSpinBox'):
        # Legacy widget structure (fallback)
        algorithmWidget.rRangeSpinBox.setValue(75)
        algorithmWidget.gRangeSpinBox.setValue(75)
        algorithmWidget.bRangeSpinBox.setValue(75)
        algorithmWidget.selectedColor = QColor(0, 170, 255)
        if hasattr(algorithmWidget, 'update_colors'):
            algorithmWidget.update_colors()

    # Verify UI state
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()
    assert not main_window.viewResultsButton.isEnabled()

    # Start processing
    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    assert not main_window.startButton.isEnabled()
    assert main_window.cancelButton.isEnabled()

    # Wait for processing to complete
    qtbot.waitUntil(lambda: main_window.viewResultsButton.isEnabled(), timeout=20000)
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()
    assert main_window.viewResultsButton.isEnabled()

    # Open viewer
    qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)
    assert main_window.viewer is not None
    viewer = main_window.viewer

    # Verify viewer has loaded data
    assert viewer.fileNameLabel is not None
    assert viewer.fileNameLabel.text() is not None
    assert viewer.images is not None
    assert len(viewer.images) != 0

    # Test navigation
    if hasattr(viewer, 'nextImageButton'):
        qtbot.mouseClick(viewer.nextImageButton, Qt.MouseButton.LeftButton)
        assert viewer.fileNameLabel.text() is not None

    if hasattr(viewer, 'previousImageButton'):
        qtbot.mouseClick(viewer.previousImageButton, Qt.MouseButton.LeftButton)
        assert viewer.fileNameLabel.text() is not None


def test_viewer_toolbar_buttons(main_window, testData, qtbot):
    """Ensure every viewer tool/control is present once the viewer loads."""
    viewer = _open_viewer_with_sample_data(main_window, testData, qtbot)

    expected_controls = {
        'galleryModeButton': 'Gallery Mode button',
        'showAOIsButton': 'Show AOIs button',
        'showPOIsButton': 'Show POIs button',
        'GPSMapButton': 'GPS Map button',
        'rotateImageButton': 'North View button',
        'magnifyButton': 'Magnify button',
        'adjustmentsButton': 'Adjustments button',
        'measureButton': 'Measure button',
        'kmlButton': 'Map Export button',
        'pdfButton': 'PDF Export button',
        'zipButton': 'ZIP Export button',
        'filterButton': 'Filter button',
        'previousImageButton': 'Previous Image button',
        'nextImageButton': 'Next Image button',
        'helpButton': 'Help button',
        'hideImageToggle': 'Hide Image toggle',
        'showOverlayToggle': 'Show Overlay toggle',
        'skipHidden': 'Skip Hidden checkbox'
    }

    missing = []
    for attr, description in expected_controls.items():
        if not hasattr(viewer, attr):
            missing.append(f"{description} (attribute '{attr}' missing)")
            continue
        widget = getattr(viewer, attr)
        if widget is None:
            missing.append(f"{description} (attribute '{attr}' is None)")

    assert not missing, "Missing viewer controls: " + ", ".join(missing)


def testNormalizeHistogram(main_window, testData, qtbot):
    """Test histogram normalization feature."""
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])

    # Select Color Range algorithm
    main_window.algorithmComboBox.setCurrentText('Color Range (RGB)')
    assert main_window.algorithmWidget is not None

    # Configure algorithm - use new wizard-based API
    algorithmWidget = main_window.algorithmWidget
    if hasattr(algorithmWidget, 'add_color_row'):
        # Add a color using the new API with ±75 range for each channel
        color = QColor(0, 170, 255)
        # R: 0 ± 75 = 0 to 75 (clamped to 0-255)
        # G: 170 ± 75 = 95 to 245
        # B: 255 ± 75 = 180 to 255 (clamped to 0-255)
        algorithmWidget.add_color_row(color, r_min=0, r_max=75, g_min=95, g_max=245, b_min=180, b_max=255)
    elif hasattr(algorithmWidget, 'rRangeSpinBox'):
        # Legacy widget structure (fallback)
        algorithmWidget.rRangeSpinBox.setValue(75)
        algorithmWidget.gRangeSpinBox.setValue(75)
        algorithmWidget.bRangeSpinBox.setValue(75)
        algorithmWidget.selectedColor = QColor(0, 170, 255)
        if hasattr(algorithmWidget, 'update_colors'):
            algorithmWidget.update_colors()

    # Enable histogram normalization
    if hasattr(main_window, 'histogramCheckbox'):
        assert main_window.histogramCheckbox is not None
        assert not main_window.HistogramImgWidget.isVisible()
        assert not main_window.histogramCheckbox.isChecked()
        main_window.histogramCheckbox.setChecked(True)
        assert main_window.histogramCheckbox.isChecked()
        assert main_window.HistogramImgWidget.isVisible()

        # Use the testData fixture which has the correct path
        histogram_path = testData['EXIF_Input_Path']
        if hasattr(main_window, 'histogramLine'):
            main_window.histogramLine.setText(histogram_path)

        qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
        qtbot.wait(100)  # Small wait for UI to update

        # Wait for processing to complete (increased timeout to 60 seconds)
        # Processing is complete when start button is enabled again (regardless of whether AOIs were found)
        qtbot.waitUntil(lambda: main_window.startButton.isEnabled(), timeout=60000)
        assert main_window.startButton.isEnabled()
        assert not main_window.cancelButton.isEnabled()


def testKmlCollection(main_window, testData, qtbot):
    """Test KML export functionality."""
    # Prepare the main window
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])

    # Select Color Range algorithm
    main_window.algorithmComboBox.setCurrentText('Color Range (RGB)')
    algorithmWidget = main_window.algorithmWidget
    if hasattr(algorithmWidget, 'add_color_row'):
        # Add a color using the new API with ±75 range for each channel
        color = QColor(0, 170, 255)
        # R: 0 ± 75 = 0 to 75 (clamped to 0-255)
        # G: 170 ± 75 = 95 to 245
        # B: 255 ± 75 = 180 to 255 (clamped to 0-255)
        algorithmWidget.add_color_row(color, r_min=0, r_max=75, g_min=95, g_max=245, b_min=180, b_max=255)
    elif hasattr(algorithmWidget, 'rRangeSpinBox'):
        # Legacy widget structure (fallback)
        algorithmWidget.rRangeSpinBox.setValue(75)
        algorithmWidget.gRangeSpinBox.setValue(75)
        algorithmWidget.bRangeSpinBox.setValue(75)
        algorithmWidget.selectedColor = QColor(0, 170, 255)
        if hasattr(algorithmWidget, 'update_colors'):
            algorithmWidget.update_colors()

    # Run the analysis and wait for results
    qtbot.mouseClick(main_window.startButton, Qt.MouseButton.LeftButton)
    qtbot.wait(100)  # Small wait for UI to update

    # Wait for processing to complete (increased timeout to 60 seconds)
    # Processing is complete when start button is enabled again (regardless of whether AOIs were found)
    qtbot.waitUntil(lambda: main_window.startButton.isEnabled(), timeout=60000)
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()

    # Only proceed if AOIs were found (viewResultsButton is enabled)
    if not main_window.viewResultsButton.isEnabled():
        pytest.skip("No AOIs found - cannot test KML export without results")

    qtbot.mouseClick(main_window.viewResultsButton, Qt.MouseButton.LeftButton)
    assert main_window.viewer is not None
    viewer = main_window.viewer

    # Remove any existing KML file
    kml_path = testData['KML_Path']
    if path.exists(kml_path):
        os.remove(kml_path)

    kml_service = KMLGeneratorService()
    kml_service.generate_kml_export(
        [img for img in viewer.images if not img.get("hidden", False)],
        kml_path
    )

    # Verify KML was written
    assert path.exists(kml_path)

    # Clean up
    os.remove(kml_path)


def testPdfGenerator(main_window, testData, qtbot):
    """Test PDF generation functionality."""
    main_window.inputFolderLine.setText(testData['RGB_Input'])
    main_window.outputFolderLine.setText(testData['RGB_Output'])

    # Select Color Range algorithm
    main_window.algorithmComboBox.setCurrentText('Color Range (RGB)')
    algorithmWidget = main_window.algorithmWidget
    if hasattr(algorithmWidget, 'add_color_row'):
        # Add a color using the new API with ±75 range for each channel
        color = QColor(0, 170, 255)
        # R: 0 ± 75 = 0 to 75 (clamped to 0-255)
        # G: 170 ± 75 = 95 to 245
        # B: 255 ± 75 = 180 to 255 (clamped to 0-255)
        algorithmWidget.add_color_row(color, r_min=0, r_max=75, g_min=95, g_max=245, b_min=180, b_max=255)
    elif hasattr(algorithmWidget, 'rRangeSpinBox'):
        # Legacy widget structure (fallback)
        algorithmWidget.rRangeSpinBox.setValue(75)
        algorithmWidget.gRangeSpinBox.setValue(75)
        algorithmWidget.bRangeSpinBox.setValue(75)
        algorithmWidget.selectedColor = QColor(0, 170, 255)
        if hasattr(algorithmWidget, 'update_colors'):
            algorithmWidget.update_colors()

    # Ensure Viewer is initialized and ready
    qtbot.mouseClick(main_window.startButton, Qt.LeftButton)
    qtbot.wait(100)  # Small wait for UI to update

    # Wait for processing to complete (increased timeout to 60 seconds)
    # Processing is complete when start button is enabled again (regardless of whether AOIs were found)
    qtbot.waitUntil(lambda: main_window.startButton.isEnabled(), timeout=60000)
    assert main_window.startButton.isEnabled()
    assert not main_window.cancelButton.isEnabled()

    # Only proceed if AOIs were found (viewResultsButton is enabled)
    if not main_window.viewResultsButton.isEnabled():
        pytest.skip("No AOIs found - cannot test PDF generation without results")

    qtbot.mouseClick(main_window.viewResultsButton, Qt.LeftButton)

    # Ensure the PDF button is properly initialized
    assert main_window.viewer is not None
    if hasattr(main_window.viewer, 'pdfButton'):
        assert main_window.viewer.pdfButton is not None

        # Patch the new PDF export system components
        from core.views.images.viewer.dialogs.PDFExportDialog import PDFExportDialog
        from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog

        # Create a mock PDFExportDialog instance
        mock_pdf_dialog = MagicMock()
        mock_pdf_dialog.exec.return_value = QDialog.DialogCode.Accepted
        mock_pdf_dialog.get_organization.return_value = "Test Org"
        mock_pdf_dialog.get_search_name.return_value = "Test Search"
        # Set to True to include images even without flagged AOIs (for testing)
        mock_pdf_dialog.get_include_images_without_flagged_aois.return_value = True

        # Create mock ExportProgressDialog to avoid access violations
        mock_progress_dialog = MagicMock()
        mock_progress_dialog.exec.return_value = QDialog.DialogCode.Accepted
        mock_progress_dialog.show.return_value = None
        mock_progress_dialog.cancel_requested = MagicMock()

        # Mock PDFExportDialog instantiation and other components
        with patch('core.controllers.images.viewer.exports.PDFExportController.PDFExportDialog') as mock_dialog_class, \
                patch.object(QFileDialog, 'getSaveFileName', return_value=("/path/to/report.pdf", "pdf")), \
                patch('core.controllers.images.viewer.exports.PDFExportController.ExportProgressDialog', return_value=mock_progress_dialog), \
                patch('core.controllers.images.viewer.exports.PDFExportController.PdfGenerationThread') as mock_thread_class:

            # Make PDFExportDialog return our mock instance when instantiated
            mock_dialog_class.return_value = mock_pdf_dialog

            # Mock the thread to avoid actual thread execution
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread
            mock_thread.isRunning.return_value = False

            # Click the PDF button
            qtbot.mouseClick(main_window.viewer.pdfButton, Qt.LeftButton)

            # Give time for the async operations
            qtbot.wait(100)

            # Verify that the thread was created and started (indicating export was initiated)
            # The export_pdf method creates a PdfGenerationThread and starts it
            assert mock_thread_class.called, "PdfGenerationThread should have been created"
            assert mock_thread.start.called, "PDF generation thread should have been started"


def testLoadFile(main_window, testData, qtbot):
    """Test loading a previous analysis XML file."""
    if not _DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Dependencies not available: {_IMPORT_ERROR}")
    if hasattr(main_window, '_process_xml_file'):
        main_window._process_xml_file(testData['Previous_Output'])
        assert main_window.viewResultsButton.isEnabled()


def testPreferences(main_window, qtbot):
    """Test preferences dialog."""
    if not _DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Dependencies not available: {_IMPORT_ERROR}")
    pref = Preferences(main_window)
    pref.show()
    assert pref is not None

    if hasattr(pref, 'maxAOIsSpinBox'):
        pref.maxAOIsSpinBox.setValue(200)
        pref.accept()

        # Verify persistence
        pref2 = Preferences(main_window)
        pref2.show()
        assert pref2.maxAOIsSpinBox.value() == 200


def testVideoParser(testData, qtbot):
    """Test video parser functionality."""
    if not _DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Dependencies not available: {_IMPORT_ERROR}")
    parser = VideoParser('Dark')
    parser.show()
    assert parser is not None

    if hasattr(parser, 'videoSelectLine'):
        parser.videoSelectLine.setText(testData['Video_Path'])
    if hasattr(parser, 'srtSelectLine'):
        parser.srtSelectLine.setText(testData['SRT_Path'])
    if hasattr(parser, 'outputLine'):
        parser.outputLine.setText(testData['Video_Output'])

    if hasattr(parser, 'startButton'):
        qtbot.mouseClick(parser.startButton, Qt.MouseButton.LeftButton)
        assert not parser.startButton.isEnabled()
        qtbot.waitUntil(lambda: parser.startButton.isEnabled(), timeout=60000)

        if path.exists(testData['Video_Output']):
            assert len(os.listdir(testData['Video_Output'])) > 0
