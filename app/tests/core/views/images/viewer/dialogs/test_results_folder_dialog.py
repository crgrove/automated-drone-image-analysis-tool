"""
Comprehensive tests for ResultsFolderDialog and related components.

Tests for:
- ResultsFolderDialog initialization and UI
- Table population and data display
- Button interactions
- ScanWorker background scanning
- ScanProgressDialog progress display
"""

from core.services.ResultsScannerService import ResultsScanResult
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
import pytest
import sys
from unittest.mock import patch, MagicMock

# Mock qtawesome before importing modules that depend on it
sys.modules['qtawesome'] = MagicMock()


# Mock IconHelper to avoid qtawesome dependency
with patch('helpers.IconHelper.IconHelper') as MockIconHelper:
    MockIconHelper.create_icon.return_value = QIcon()
    from core.views.images.viewer.dialogs.ResultsFolderDialog import (
        ResultsFolderDialog,
        ScanWorker,
        ScanProgressDialog
    )


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def sample_results():
    """Create sample scan results for testing."""
    return [
        ResultsScanResult(
            xml_path='/path/to/Flight1/ADIAT_Results/ADIAT_DATA.XML',
            folder_name='Flight1',
            algorithm='Color Range',
            image_count=10,
            aoi_count=25,
            missing_images=0,
            first_image_path='/path/to/Flight1/image1.jpg',
            gps_coordinates=(37.7749, -122.4194)
        ),
        ResultsScanResult(
            xml_path='/path/to/Flight2/ADIAT_Results/ADIAT_DATA.XML',
            folder_name='Flight2',
            algorithm='RX Anomaly',
            image_count=5,
            aoi_count=3,
            missing_images=2,
            first_image_path='/path/to/Flight2/image1.jpg',
            gps_coordinates=(40.7128, -74.0060)
        ),
        ResultsScanResult(
            xml_path='/path/to/Flight3/ADIAT_Results/ADIAT_DATA.XML',
            folder_name='Flight3',
            algorithm='Thermal Range',
            image_count=8,
            aoi_count=15,
            missing_images=8,  # All missing
            first_image_path=None,
            gps_coordinates=None
        )
    ]


@pytest.fixture
def mock_callback():
    """Create a mock callback for viewer opening."""
    return MagicMock()


# ============================================================================
# Test ScanProgressDialog
# ============================================================================

class TestScanProgressDialog:
    """Tests for ScanProgressDialog."""

    def test_initialization(self, app):
        """Test ScanProgressDialog initialization."""
        dialog = ScanProgressDialog()

        assert dialog is not None
        assert dialog.windowTitle() == "Scanning for Results"
        assert dialog._results_found == 0

    def test_update_progress(self, app):
        """Test progress update method."""
        dialog = ScanProgressDialog()

        dialog.update_progress(5, 20, '/path/to/current/folder')

        assert dialog.maximum() == 20
        assert dialog.value() == 5

    def test_update_progress_truncates_long_path(self, app):
        """Test that long paths are truncated."""
        dialog = ScanProgressDialog()

        long_path = '/very/long/path' + '/segment' * 20
        dialog.update_progress(1, 10, long_path)

        label_text = dialog.labelText()
        assert '...' in label_text or len(label_text) < len(long_path)

    def test_increment_results_found(self, app):
        """Test incrementing results count."""
        dialog = ScanProgressDialog()

        assert dialog._results_found == 0

        dialog.increment_results_found()
        assert dialog._results_found == 1

        dialog.increment_results_found()
        assert dialog._results_found == 2

    def test_minimum_width(self, app):
        """Test dialog has minimum width."""
        dialog = ScanProgressDialog()

        assert dialog.minimumWidth() == 500


# ============================================================================
# Test ScanWorker
# ============================================================================

class TestScanWorker:
    """Tests for ScanWorker background thread."""

    def test_initialization(self, app):
        """Test ScanWorker initialization."""
        worker = ScanWorker('/path/to/folder')

        assert worker.folder_path == '/path/to/folder'
        assert worker.scanner is not None

    def test_run_success(self, app, sample_results):
        """Test successful scan execution."""
        worker = ScanWorker('/test/path')

        results_received = []
        worker.finished.connect(lambda r: results_received.extend(r))

        with patch.object(worker.scanner, 'scan_folder') as mock_scan:
            mock_scan.return_value = sample_results

            worker.run()

            assert len(results_received) == 3
            mock_scan.assert_called_once()

    def test_run_with_error(self, app):
        """Test scan execution with error."""
        worker = ScanWorker('/test/path')

        errors_received = []
        worker.error.connect(lambda e: errors_received.append(e))

        with patch.object(worker.scanner, 'scan_folder') as mock_scan:
            mock_scan.side_effect = Exception("Scan failed")

            worker.run()

            assert len(errors_received) == 1
            assert "Scan failed" in errors_received[0]

    def test_progress_signal(self, app):
        """Test that progress signals are emitted."""
        worker = ScanWorker('/test/path')

        progress_calls = []
        worker.progress.connect(lambda c, t, d: progress_calls.append((c, t, d)))

        # Call the internal progress callback
        worker._on_progress(5, 10, '/current/dir')

        assert len(progress_calls) == 1
        assert progress_calls[0] == (5, 10, '/current/dir')


# ============================================================================
# Test ResultsFolderDialog Initialization
# ============================================================================

class TestResultsFolderDialogInit:
    """Tests for ResultsFolderDialog initialization."""

    def test_initialization_with_results(self, app, sample_results, mock_callback):
        """Test dialog initialization with results."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog is not None
        assert dialog.results == sample_results
        assert dialog.theme == 'Dark'
        assert dialog.open_viewer_callback == mock_callback

    def test_initialization_empty_results(self, app, mock_callback):
        """Test dialog initialization with empty results."""
        dialog = ResultsFolderDialog(None, [], 'Light', mock_callback)

        assert dialog is not None
        assert dialog.results == []

    def test_window_title(self, app, sample_results, mock_callback):
        """Test dialog window title."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog.windowTitle() == "Load Results Folder"

    def test_dialog_is_modal(self, app, sample_results, mock_callback):
        """Test that dialog is modal."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog.isModal()

    def test_minimum_size(self, app, sample_results, mock_callback):
        """Test dialog minimum size."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog.minimumWidth() == 900
        assert dialog.minimumHeight() == 500


# ============================================================================
# Test ResultsFolderDialog UI Components
# ============================================================================

class TestResultsFolderDialogUI:
    """Tests for ResultsFolderDialog UI components."""

    def test_header_label_shows_count(self, app, sample_results, mock_callback):
        """Test header label shows correct result count."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        # Find header label - it's the first QLabel in the layout
        header_text = None
        for i in range(dialog.layout().count()):
            widget = dialog.layout().itemAt(i).widget()
            if hasattr(widget, 'text') and 'result' in widget.text().lower():
                header_text = widget.text()
                break

        assert header_text is not None
        assert '3' in header_text

    def test_table_column_count(self, app, sample_results, mock_callback):
        """Test table has correct number of columns."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog.table.columnCount() == 7

    def test_table_row_count(self, app, sample_results, mock_callback):
        """Test table has correct number of rows."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog.table.rowCount() == 3

    def test_table_headers(self, app, sample_results, mock_callback):
        """Test table has correct headers."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        expected_headers = ["Folder", "Algorithm", "Images", "Missing", "AOIs", "Map", "View"]
        for i, expected in enumerate(expected_headers):
            actual = dialog.table.horizontalHeaderItem(i).text()
            assert actual == expected

    def test_close_button_exists(self, app, sample_results, mock_callback):
        """Test close button exists."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog.close_button is not None
        assert dialog.close_button.text() == "Close"


# ============================================================================
# Test Table Population
# ============================================================================

class TestTablePopulation:
    """Tests for table data population."""

    def test_folder_name_column(self, app, sample_results, mock_callback):
        """Test folder name is displayed correctly."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row, result in enumerate(sample_results):
            item = dialog.table.item(row, ResultsFolderDialog.COL_FOLDER)
            assert item.text() == result.folder_name

    def test_folder_tooltip_shows_path(self, app, sample_results, mock_callback):
        """Test folder cell tooltip shows full XML path."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row, result in enumerate(sample_results):
            item = dialog.table.item(row, ResultsFolderDialog.COL_FOLDER)
            assert item.toolTip() == result.xml_path

    def test_algorithm_column(self, app, sample_results, mock_callback):
        """Test algorithm is displayed correctly."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row, result in enumerate(sample_results):
            item = dialog.table.item(row, ResultsFolderDialog.COL_ALGORITHM)
            assert item.text() == result.algorithm

    def test_image_count_column(self, app, sample_results, mock_callback):
        """Test image count is displayed correctly."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row, result in enumerate(sample_results):
            item = dialog.table.item(row, ResultsFolderDialog.COL_IMAGES)
            assert item.text() == str(result.image_count)

    def test_missing_count_column(self, app, sample_results, mock_callback):
        """Test missing count is displayed correctly."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row, result in enumerate(sample_results):
            item = dialog.table.item(row, ResultsFolderDialog.COL_MISSING)
            assert item.text() == str(result.missing_images)

    def test_aoi_count_column(self, app, sample_results, mock_callback):
        """Test AOI count is displayed correctly."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row, result in enumerate(sample_results):
            item = dialog.table.item(row, ResultsFolderDialog.COL_AOIS)
            assert item.text() == str(result.aoi_count)

    def test_map_button_exists(self, app, sample_results, mock_callback):
        """Test map button cell widget exists."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row in range(len(sample_results)):
            widget = dialog.table.cellWidget(row, ResultsFolderDialog.COL_MAP)
            assert widget is not None

    def test_view_button_exists(self, app, sample_results, mock_callback):
        """Test view button cell widget exists."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row in range(len(sample_results)):
            widget = dialog.table.cellWidget(row, ResultsFolderDialog.COL_VIEW)
            assert widget is not None


# ============================================================================
# Test Button States
# ============================================================================

class TestButtonStates:
    """Tests for button enabled/disabled states."""

    def test_map_button_disabled_when_all_missing(self, app, mock_callback):
        """Test map button is disabled when all images are missing."""
        results = [
            ResultsScanResult(
                xml_path='/path/to/ADIAT_DATA.XML',
                folder_name='AllMissing',
                algorithm='Test',
                image_count=5,
                aoi_count=0,
                missing_images=5,  # All missing
                first_image_path=None,
                gps_coordinates=None
            )
        ]

        dialog = ResultsFolderDialog(None, results, 'Dark', mock_callback)

        # Get the map button from the container widget
        map_container = dialog.table.cellWidget(0, ResultsFolderDialog.COL_MAP)
        map_button = map_container.layout().itemAt(0).widget()

        assert not map_button.isEnabled()

    def test_map_button_disabled_when_no_gps(self, app, mock_callback):
        """Test map button is disabled when no GPS coordinates."""
        results = [
            ResultsScanResult(
                xml_path='/path/to/ADIAT_DATA.XML',
                folder_name='NoGPS',
                algorithm='Test',
                image_count=5,
                aoi_count=0,
                missing_images=0,
                first_image_path='/path/to/image.jpg',
                gps_coordinates=None  # No GPS
            )
        ]

        dialog = ResultsFolderDialog(None, results, 'Dark', mock_callback)

        map_container = dialog.table.cellWidget(0, ResultsFolderDialog.COL_MAP)
        map_button = map_container.layout().itemAt(0).widget()

        assert not map_button.isEnabled()

    def test_map_button_enabled_with_gps(self, app, mock_callback):
        """Test map button is enabled when GPS is available."""
        results = [
            ResultsScanResult(
                xml_path='/path/to/ADIAT_DATA.XML',
                folder_name='WithGPS',
                algorithm='Test',
                image_count=5,
                aoi_count=0,
                missing_images=0,
                first_image_path='/path/to/image.jpg',
                gps_coordinates=(37.7749, -122.4194)
            )
        ]

        dialog = ResultsFolderDialog(None, results, 'Dark', mock_callback)

        map_container = dialog.table.cellWidget(0, ResultsFolderDialog.COL_MAP)
        map_button = map_container.layout().itemAt(0).widget()

        assert map_button.isEnabled()

    def test_view_button_always_enabled(self, app, sample_results, mock_callback):
        """Test view button is always enabled."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        for row in range(len(sample_results)):
            view_container = dialog.table.cellWidget(row, ResultsFolderDialog.COL_VIEW)
            view_button = view_container.layout().itemAt(0).widget()
            assert view_button.isEnabled()


# ============================================================================
# Test Button Interactions
# ============================================================================

class TestButtonInteractions:
    """Tests for button click interactions."""

    def test_view_button_calls_callback(self, app, sample_results, mock_callback):
        """Test view button calls the open viewer callback."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        # Get the view button for first row
        view_container = dialog.table.cellWidget(0, ResultsFolderDialog.COL_VIEW)
        view_button = view_container.layout().itemAt(0).widget()

        # Click the button
        view_button.click()

        # Verify callback was called with correct XML path
        mock_callback.assert_called_once_with(sample_results[0].xml_path)

    def test_map_button_opens_google_maps(self, app, sample_results, mock_callback):
        """Test map button opens Google Maps URL."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        with patch('core.views.images.viewer.dialogs.ResultsFolderDialog.QDesktopServices') as mock_desktop:
            # Get the map button for first row (which has GPS)
            map_container = dialog.table.cellWidget(0, ResultsFolderDialog.COL_MAP)
            map_button = map_container.layout().itemAt(0).widget()

            # Click the button
            map_button.click()

            # Verify URL was opened
            mock_desktop.openUrl.assert_called_once()
            url_arg = mock_desktop.openUrl.call_args[0][0]
            url_string = url_arg.toString()
            assert 'google.com/maps' in url_string
            assert '37.7749' in url_string
            assert '-122.4194' in url_string

    def test_close_button_accepts_dialog(self, app, sample_results, mock_callback):
        """Test close button accepts the dialog."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        # Track if accept was called
        accept_called = []
        original_accept = dialog.accept
        dialog.accept = lambda: accept_called.append(True) or original_accept()

        dialog.close_button.click()

        assert len(accept_called) == 1


# ============================================================================
# Test Theme Handling
# ============================================================================

class TestThemeHandling:
    """Tests for theme handling."""

    def test_dark_theme(self, app, sample_results, mock_callback):
        """Test dialog with dark theme."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        assert dialog.theme == 'Dark'

    def test_light_theme(self, app, sample_results, mock_callback):
        """Test dialog with light theme."""
        dialog = ResultsFolderDialog(None, sample_results, 'Light', mock_callback)

        assert dialog.theme == 'Light'


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_single_result(self, app, mock_callback):
        """Test dialog with single result."""
        results = [
            ResultsScanResult(
                xml_path='/path/to/ADIAT_DATA.XML',
                folder_name='Single',
                algorithm='Test',
                image_count=1,
                aoi_count=1,
                missing_images=0,
                first_image_path='/path/to/image.jpg',
                gps_coordinates=(0.0, 0.0)
            )
        ]

        dialog = ResultsFolderDialog(None, results, 'Dark', mock_callback)

        assert dialog.table.rowCount() == 1

    def test_result_with_zero_counts(self, app, mock_callback):
        """Test result with all zero counts."""
        results = [
            ResultsScanResult(
                xml_path='/path/to/ADIAT_DATA.XML',
                folder_name='Empty',
                algorithm='Unknown',
                image_count=0,
                aoi_count=0,
                missing_images=0,
                first_image_path=None,
                gps_coordinates=None
            )
        ]

        dialog = ResultsFolderDialog(None, results, 'Dark', mock_callback)

        images_item = dialog.table.item(0, ResultsFolderDialog.COL_IMAGES)
        assert images_item.text() == '0'

    def test_special_characters_in_folder_name(self, app, mock_callback):
        """Test folder name with special characters."""
        results = [
            ResultsScanResult(
                xml_path='/path/to/ADIAT_DATA.XML',
                folder_name='Flight 2024-01-15 (Test & Demo)',
                algorithm='Test',
                image_count=0,
                aoi_count=0,
                missing_images=0,
                first_image_path=None,
                gps_coordinates=None
            )
        ]

        dialog = ResultsFolderDialog(None, results, 'Dark', mock_callback)

        folder_item = dialog.table.item(0, ResultsFolderDialog.COL_FOLDER)
        assert folder_item.text() == 'Flight 2024-01-15 (Test & Demo)'

    def test_very_long_algorithm_name(self, app, mock_callback):
        """Test with very long algorithm name."""
        results = [
            ResultsScanResult(
                xml_path='/path/to/ADIAT_DATA.XML',
                folder_name='Test',
                algorithm='A' * 100,  # Very long name
                image_count=0,
                aoi_count=0,
                missing_images=0,
                first_image_path=None,
                gps_coordinates=None
            )
        ]

        dialog = ResultsFolderDialog(None, results, 'Dark', mock_callback)

        algo_item = dialog.table.item(0, ResultsFolderDialog.COL_ALGORITHM)
        assert algo_item.text() == 'A' * 100


# ============================================================================
# Test Integration
# ============================================================================

class TestIntegration:
    """Integration tests for the dialog."""

    def test_full_workflow(self, app, sample_results, mock_callback):
        """Test complete dialog workflow."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)
        dialog.show()

        # Verify initialization
        assert dialog.table.rowCount() == 3
        assert dialog.isVisible()

        # Click view button on second row
        view_container = dialog.table.cellWidget(1, ResultsFolderDialog.COL_VIEW)
        view_button = view_container.layout().itemAt(0).widget()
        view_button.click()

        # Verify callback was called with correct path
        mock_callback.assert_called_once_with(sample_results[1].xml_path)

    def test_table_selection(self, app, sample_results, mock_callback):
        """Test table row selection."""
        dialog = ResultsFolderDialog(None, sample_results, 'Dark', mock_callback)

        # Select a row
        dialog.table.selectRow(1)

        # Check selection
        selected_rows = dialog.table.selectedItems()
        assert len(selected_rows) > 0
