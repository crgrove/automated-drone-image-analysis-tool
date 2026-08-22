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

from core.views.images.viewer.dialogs.PDFExportDialog import PDFExportDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog

# Try to import dependencies, skip tests if not available
try:
    from core.controllers.images.VideoParser import VideoParser
    from core.controllers.Preferences import Preferences
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
        'showRulerButton': 'Show AOI Ruler button',
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


def test_flight_viewer_menu_hidden_when_feature_disabled(qtbot):
    """Flight Viewer visibility is gated: the File-menu action must be
    invisible while FeatureFlags.FLIGHT_VIEWER_ENABLED is False. A fresh
    window is built under an explicit False patch so the gated-off path
    stays covered regardless of the shipping default."""
    try:
        import qdarktheme
        from core.controllers.images.MainWindow import MainWindow
    except ImportError:
        pytest.skip("MainWindow dependencies not available")
    with patch("helpers.FeatureFlags.FLIGHT_VIEWER_ENABLED", False):
        mw = MainWindow(qdarktheme)
    qtbot.addWidget(mw)
    mw.show()
    assert hasattr(mw, 'actionFlightViewer')
    assert not mw.actionFlightViewer.isVisible()


def test_flight_viewer_menu_shown_when_feature_enabled(qtbot):
    """The File-menu action must be visible while the flag is True.

    Built under an explicit True patch (mirroring the disabled-path test above)
    rather than relying on the shared main_window fixture, so both sides of the
    gate stay covered regardless of the shipping default.
    """
    try:
        import qdarktheme
        from core.controllers.images.MainWindow import MainWindow
    except ImportError:
        pytest.skip("MainWindow dependencies not available")
    with patch("helpers.FeatureFlags.FLIGHT_VIEWER_ENABLED", True):
        mw = MainWindow(qdarktheme)
    qtbot.addWidget(mw)
    mw.show()
    assert hasattr(mw, 'actionFlightViewer')
    assert mw.actionFlightViewer.isVisible()


# --- Search Coordinator: results button + reload routing --------------------

_SEARCH_PROJECT_XML = (
    '<?xml version="1.0"?><search_project>'
    '<metadata><name>Batch Run</name></metadata>'
    '<batches/><consolidated_aois/></search_project>'
)
_SINGLE_RESULT_XML = '<?xml version="1.0"?><data><settings/><images/></data>'


def _write(tmp_path, name, contents):
    """Write contents to tmp_path/name and return the string path."""
    file_path = tmp_path / name
    file_path.write_text(contents, encoding='utf-8')
    return str(file_path)


def test_is_search_project_xml_detection(main_window, tmp_path):
    """Only a <search_project> root is recognized as a Coordinator project."""
    project = _write(tmp_path, 'ADIAT_Search_Batch.xml', _SEARCH_PROJECT_XML)
    single = _write(tmp_path, 'ADIAT_Data.xml', _SINGLE_RESULT_XML)
    junk = _write(tmp_path, 'not_xml.xml', 'this is not xml <<<')

    assert main_window._is_search_project_xml(project) is True
    assert main_window._is_search_project_xml(single) is False
    assert main_window._is_search_project_xml(junk) is False
    assert main_window._is_search_project_xml(str(tmp_path / 'missing.xml')) is False


def test_batch_done_switches_button_to_coordinator(main_window, tmp_path):
    """A batch run that produced a project repurposes the results button."""
    project = _write(tmp_path, 'ADIAT_Search_Batch.xml', _SEARCH_PROJECT_XML)

    with patch.object(main_window, '_open_coordinator') as open_coord, \
            patch('core.controllers.images.MainWindow.QMessageBox'):
        main_window._on_batch_done(2, 0, project)

        assert main_window._view_results_mode == 'coordinator'
        assert main_window._search_project_path == project
        assert main_window.viewResultsButton.isEnabled()
        assert 'Search Coordinator' in main_window.viewResultsButton.text()

        # Clicking the repurposed button opens the Coordinator on that project.
        main_window._viewResultsButton_clicked()
        open_coord.assert_called_once_with(project)


def test_batch_done_without_project_keeps_results_mode(main_window):
    """A batch run that created no project leaves the button as View Results."""
    with patch.object(main_window, '_open_coordinator'), \
            patch('core.controllers.images.MainWindow.QMessageBox'):
        main_window._on_batch_done(0, 1, '')

    assert main_window._view_results_mode == 'results'
    assert main_window._search_project_path is None
    assert not main_window.viewResultsButton.isEnabled()


def test_load_search_project_routes_to_coordinator(main_window, tmp_path):
    """Loading a Search Coordinator project XML opens the Coordinator."""
    project = _write(tmp_path, 'ADIAT_Search_Batch.xml', _SEARCH_PROJECT_XML)

    with patch.object(main_window, '_open_coordinator') as open_coord, \
            patch.object(main_window, '_get_settings_from_xml') as get_settings:
        main_window._process_xml_file(project)

    open_coord.assert_called_once_with(project)
    get_settings.assert_not_called()
    # The wizard review handler relies on this to skip the single-run Viewer.
    assert main_window._view_results_mode == 'coordinator'
    assert main_window._search_project_path == project
    assert main_window.viewResultsButton.isEnabled()


def test_results_button_widens_for_coordinator_label(main_window):
    """The results button grows to fit the longer coordinator label."""
    main_window._set_view_results_mode('results')
    results_width = main_window.viewResultsButton.minimumWidth()

    main_window._set_view_results_mode('coordinator', 'project.xml')
    coordinator_width = main_window.viewResultsButton.minimumWidth()

    assert results_width >= 150
    assert coordinator_width > results_width


def test_load_single_result_not_routed_to_coordinator(main_window, tmp_path):
    """A single-run ADIAT_Data.xml is not sent to the Coordinator."""
    single = _write(tmp_path, 'ADIAT_Data.xml', _SINGLE_RESULT_XML)

    with patch.object(main_window, '_open_coordinator') as open_coord, \
            patch.object(main_window, '_get_settings_from_xml', return_value=3):
        main_window._process_xml_file(single)

    open_coord.assert_not_called()
    assert main_window._view_results_mode == 'results'
    assert main_window.viewResultsButton.isEnabled()

# --------------------------------------------------------------------------- #
#  Recent results MRU: recorded on open, surfaced in the File menu             #
# --------------------------------------------------------------------------- #


class _FakeSettingsStore:
    """In-memory settings so tests never write to the real registry."""

    def __init__(self):
        self.store = {}

    def get_setting(self, name, default_value=None):
        return self.store.get(name, default_value)

    def set_setting(self, name, value):
        self.store[name] = value


def testRecentResultsRoundtripDedupeAndCap(main_window, tmp_path):
    """Recording keeps newest first, dedupes by path, and caps the list."""
    main_window.settings_service = _FakeSettingsStore()

    paths = []
    for i in range(12):
        p = tmp_path / f"batch{i}" / "ADIAT_Data.xml"
        p.parent.mkdir(parents=True)
        p.write_text("<data/>")
        paths.append(str(p))
        main_window._record_recent_result(str(p))
    # Re-opening an old one moves it back to the top instead of duplicating
    main_window._record_recent_result(paths[5])

    recents = main_window._get_recent_results()
    assert recents[0] == os.path.abspath(paths[5])
    assert len(recents) <= main_window.RECENT_RESULTS_LIMIT
    assert len(set(os.path.normcase(p) for p in recents)) == len(recents)


def testRecentResultsMenuPlaceholderWhenEmpty(main_window):
    main_window.settings_service = _FakeSettingsStore()

    main_window._populate_recent_results_menu()

    actions = main_window.menuRecentResults.actions()
    assert len(actions) == 1
    assert not actions[0].isEnabled()


def testRecentResultsMenuDisablesMissingFiles(main_window, tmp_path):
    """Entries whose files vanished stay listed but cannot be clicked."""
    import json as _json
    main_window.settings_service = _FakeSettingsStore()
    existing = tmp_path / "run1" / "ADIAT_Data.xml"
    existing.parent.mkdir(parents=True)
    existing.write_text("<data/>")
    gone = str(tmp_path / "gone" / "ADIAT_Data.xml")
    main_window.settings_service.store[main_window.RECENT_RESULTS_SETTING] = _json.dumps(
        [str(existing), gone]
    )

    main_window._populate_recent_results_menu()

    actions = main_window.menuRecentResults.actions()
    assert len(actions) == 2
    assert actions[0].isEnabled()
    assert not actions[1].isEnabled()


def testProcessXmlFileRecordsRecent(main_window, tmp_path):
    """Opening a result XML lands it at the top of the recents list."""
    main_window.settings_service = _FakeSettingsStore()
    xml_path = tmp_path / "ADIAT_Data.xml"
    xml_path.write_text("<data/>")

    with patch.object(main_window, '_is_search_project_xml', return_value=False), \
            patch.object(main_window, '_get_settings_from_xml', return_value=3), \
            patch.object(main_window, '_set_view_results_mode'), \
            patch.object(main_window, '_set_ViewResultsButton'):
        main_window._process_xml_file(str(xml_path))

    recents = main_window._get_recent_results()
    assert recents
    assert os.path.normcase(recents[0]) == os.path.normcase(os.path.abspath(str(xml_path)))


def testOpenResultsForReviewRoutesToFolderScan(main_window):
    """The Review Results tile entry point drives the folder scanner."""
    with patch.object(main_window, '_open_load_results_folder') as mock_open:
        main_window.open_results_for_review()
    mock_open.assert_called_once()


# ---------------------------------------------------------------------------
# Algorithm widget swap hygiene (field screenshot: outgoing ColorRange panel
# stayed painted under the incoming MRMap panel while a long synchronous load
# blocked the event loop; deleteLater alone does not hide the removed widget)
# ---------------------------------------------------------------------------

def test_algorithm_swap_hides_the_outgoing_widget(main_window):
    outgoing = main_window.algorithmWidget
    assert outgoing is not None

    current = main_window.algorithmComboBox.currentText()
    other = next(a['label'] for a in main_window.algorithms if a['label'] != current)
    main_window.algorithmComboBox.setCurrentText(other)

    assert main_window.algorithmWidget is not outgoing
    # The outgoing widget must be invisible immediately - not merely queued
    # for deletion - so a blocked event loop can never paint both panels.
    assert outgoing.isHidden()


def test_algorithm_swap_ignores_unknown_label(main_window):
    """A label that matches no algorithm (group header, stale text) must not
    tear down the current widget; the old unguarded next() raised
    StopIteration after the removal, leaving the swap half-done."""
    before = main_window.algorithmWidget
    with patch.object(main_window.algorithmComboBox, 'currentText', return_value='No Such Algorithm'):
        main_window._algorithmComboBox_changed()

    assert main_window.algorithmWidget is before
    assert not before.isHidden()


def test_startup_leaves_algorithm_state_consistent(main_window):
    """activeAlgorithm and algorithmWidget always agree after construction.

    The swap derives activeAlgorithm from the combobox, so the two cannot
    drift; the startup check in __init__ guarantees both are set (a corrupt
    or fully platform-filtered algorithms.conf raises there instead of
    failing later at Start with an AttributeError)."""
    assert main_window.activeAlgorithm is not None
    assert main_window.algorithmWidget is not None
    assert main_window.activeAlgorithm['label'] == main_window.algorithmComboBox.currentText()


def test_algorithm_combobox_is_managed_by_a_layout(main_window):
    """The grouped selector must be laid out, not floating.

    replaceWidget silently no-ops when the placeholder is missing from the
    layout, and an unmanaged widget floats at its parent's top-left over
    whatever is there (field screenshot: stray dropdown over the Input
    Folder row). The fallback adds it to the layout regardless."""
    layout = main_window.algorithmSelectorlLayout
    assert layout.indexOf(main_window.algorithmComboBox) != -1


# ---------------------------------------------------------------------------
# populate_from_wizard_data: the combobox is the single source of truth for
# activeAlgorithm, so an algorithm the wizard names but this platform cannot
# select must not half-apply (options landing on the previous widget, or
# auto-start running one algorithm with another's parameters).
# ---------------------------------------------------------------------------

def test_wizard_applies_an_available_algorithm(main_window):
    current = main_window.algorithmComboBox.currentText()
    target = next(a['label'] for a in main_window.algorithms
                  if a['label'] != current
                  and main_window.algorithmComboBox.findText(a['label']) != -1)

    main_window.populate_from_wizard_data({'algorithm': target})

    assert main_window.algorithmComboBox.currentText() == target
    assert main_window.activeAlgorithm['label'] == target


def test_wizard_unavailable_algorithm_does_not_half_apply(main_window):
    """The regression: a label in self.algorithms but NOT selectable here.

    self.algorithms is unfiltered while the combobox holds only labels for
    this platform (algorithms.conf marks the Temperature algorithms
    Windows-only), so on the other platform setCurrentText silently no-ops on
    the non-editable combobox. Windows cannot produce that state naturally,
    so the no-op is simulated - patching setCurrentText is exactly what an
    absent label does.

    Previously activeAlgorithm was assigned from self.algorithms BEFORE
    setCurrentText, so it drifted to an algorithm whose widget was never
    built: load_options wrote to the previous widget and auto-start ran one
    algorithm with another's parameters.
    """
    before_label = main_window.algorithmComboBox.currentText()
    before_widget = main_window.algorithmWidget
    unavailable = next(a['label'] for a in main_window.algorithms
                       if a['label'] != before_label)
    loaded = []
    before_widget.load_options = lambda opts: loaded.append(opts)

    with patch.object(main_window.algorithmComboBox, 'setCurrentText'):
        main_window.populate_from_wizard_data({
            'algorithm': unavailable,
            'algorithm_options': {'some': 'value'},
        })

    # activeAlgorithm tracked the combobox, not the wizard's request.
    assert main_window.algorithmComboBox.currentText() == before_label
    assert main_window.activeAlgorithm['label'] == before_label
    assert main_window.algorithmWidget is before_widget
    # And nothing was written into the wrong algorithm's widget.
    assert loaded == []


def test_wizard_options_load_into_the_selected_algorithms_widget(main_window):
    current = main_window.algorithmComboBox.currentText()
    target = next(a['label'] for a in main_window.algorithms
                  if a['label'] != current
                  and main_window.algorithmComboBox.findText(a['label']) != -1)

    main_window.populate_from_wizard_data({
        'algorithm': target,
        'algorithm_options': {'some': 'value'},
    })

    # The widget that received the options is the one for the selected
    # algorithm - the pairing the old manual activeAlgorithm assignment
    # could break.
    assert main_window.activeAlgorithm['label'] == target
    assert main_window.algorithmWidget is not None
