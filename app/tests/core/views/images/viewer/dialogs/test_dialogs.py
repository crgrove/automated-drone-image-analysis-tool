"""
Comprehensive tests for viewer dialogs.

Tests all dialogs used in the viewer.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QDialog

from core.views.images.viewer.dialogs.AOICommentDialog import AOICommentDialog
from core.views.images.viewer.dialogs.AOICreationDialog import AOICreationDialog
from core.views.images.viewer.dialogs.AOIFilterDialog import AOIFilterDialog
from core.views.images.viewer.dialogs.BearingRecoveryDialog import BearingRecoveryDialog
from core.views.images.viewer.dialogs.CacheLocationDialog import CacheLocationDialog
from core.views.images.viewer.dialogs.CalTopoAuthDialog import CalTopoAuthDialog
from core.views.images.viewer.dialogs.ColorHistogramDialog import ColorHistogramDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.views.images.viewer.dialogs.GPSMapDialog import GPSMapDialog
from core.views.images.viewer.dialogs.GridReviewDialog import GridReviewDialog
from core.views.images.viewer.dialogs.HelpDialog import HelpDialog
from core.views.images.viewer.dialogs.ImageAdjustmentDialog import ImageAdjustmentDialog
from core.views.images.viewer.dialogs.LoadingDialog import LoadingDialog
from core.views.images.viewer.dialogs.MapExportDialog import MapExportDialog
from core.views.images.viewer.dialogs.MeasureDialog import MeasureDialog
from core.views.images.viewer.dialogs.PDFExportDialog import PDFExportDialog
from core.views.images.viewer.dialogs.ReviewerNameDialog import ReviewerNameDialog
from core.views.images.viewer.dialogs.ThermalHistogramDialog import ThermalHistogramDialog
from core.views.images.viewer.dialogs.UpscaleDialog import UpscaleDialog
from core.views.images.viewer.dialogs.ZipExportDialog import ZipExportDialog


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_aoi_comment_dialog_initialization(app):
    """Test AOICommentDialog initialization."""
    dialog = AOICommentDialog(None, "Test comment")
    assert dialog is not None


def test_aoi_creation_dialog_initialization(app):
    """Test AOICreationDialog initialization."""
    dialog = AOICreationDialog(None)
    assert dialog is not None


def test_aoi_filter_dialog_initialization(app):
    """Test AOIFilterDialog initialization."""
    dialog = AOIFilterDialog(None)
    assert dialog is not None


def test_bearing_recovery_dialog_initialization(app):
    """Test BearingRecoveryDialog initialization."""
    # Mock QMessageBox to avoid showing dialog during test
    with patch('core.views.images.viewer.dialogs.BearingRecoveryDialog.QMessageBox'):
        # Mock QTimer to prevent automatic skip
        with patch('core.views.images.viewer.dialogs.BearingRecoveryDialog.QTimer'):
            dialog = BearingRecoveryDialog(None, [])
            assert dialog is not None


def test_cache_location_dialog_initialization(app):
    """Test CacheLocationDialog initialization."""
    dialog = CacheLocationDialog(None, "default_path")
    assert dialog is not None


def test_caltopo_auth_dialog_initialization(app):
    """Test CalTopoAuthDialog initialization."""
    dialog = CalTopoAuthDialog(None)
    assert dialog is not None

    # Return belongs to the embedded login form, not to this dialog's buttons.
    # With autoDefault left on, typing a password and pressing Enter fired
    # "I'm Logged In" and produced a spurious "No Map Selected" warning.
    assert dialog.manual_done_button.autoDefault() is False
    assert dialog.manual_done_button.isDefault() is False
    assert dialog.cancel_button.autoDefault() is False
    assert dialog.cancel_button.isDefault() is False


def test_caltopo_auth_dialog_swallows_return_key(app):
    """Return must not reach QDialog's default-button handling."""
    dialog = CalTopoAuthDialog(None)
    accepted = []
    dialog.accepted.connect(lambda: accepted.append(True))

    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier)
    dialog.keyPressEvent(event)

    assert accepted == []
    assert dialog.result() != QDialog.Accepted


def _write_chromium_cookie_db(path, rows):
    """Build a minimal Chromium-shaped Cookies database for testing."""
    import sqlite3

    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE cookies (host_key TEXT, name TEXT, value TEXT, "
        "encrypted_value BLOB, path TEXT, is_secure INTEGER, "
        "is_httponly INTEGER, expires_utc INTEGER)"
    )
    connection.executemany(
        "INSERT INTO cookies VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows
    )
    connection.commit()
    connection.close()


def test_caltopo_auth_dialog_reads_session_cookie_from_disk(app, tmp_path):
    """The HttpOnly session cookie must be recoverable from the profile store.

    QWebEngineCookieStore announces cookies only as they are SET, and
    loadAllCookies() delivers nothing for cookies restored from disk (measured:
    0 of 35 on a real profile). CalTopo's SESSION cookie is HttpOnly, so
    document.cookie cannot see it either - a returning, already-logged-in user
    was left with nothing but analytics cookies.
    """
    _write_chromium_cookie_db(str(tmp_path / "Cookies"), [
        # Chromium epoch: microseconds since 1601-01-01.
        ('caltopo.com', 'SESSION', 'the-real-session', None, '/', 1, 1, 0),
        ('.caltopo.com', '_ssid', 'incidental', None, '/', 1, 1, 13000000000000000),
        ('caltopo.com', '_pk_id.7.62df', 'analytics', None, '/', 0, 0, 0),
        ('accounts.google.com', 'LSID', 'unrelated', None, '/', 1, 1, 0),
        ('caltopo.com', 'ENCRYPTED', '', b'\x01\x02\x03', '/', 1, 1, 0),
    ])

    cookies = CalTopoAuthDialog._read_persisted_cookies(str(tmp_path))
    by_name = {c['name']: c for c in cookies.values()}

    # Only caltopo.com cookies, and the Google ones are left alone.
    assert set(by_name) == {'SESSION', '_ssid', '_pk_id.7.62df'}

    session = by_name['SESSION']
    assert session['value'] == 'the-real-session'
    assert session['rest'] == {'HttpOnly': True}
    assert session['secure'] is True
    assert session['expires'] is None      # session cookie
    assert session['discard'] is True

    # Leading dot is normalised the same way the live store path does it.
    assert by_name['_ssid']['domain'] == 'caltopo.com'
    assert by_name['_ssid']['domain_initial_dot'] is True
    assert by_name['_ssid']['expires'] is not None

    # An encrypted value cannot be used, so it is skipped rather than guessed.
    assert 'ENCRYPTED' not in by_name


def test_caltopo_auth_dialog_disk_read_survives_a_missing_store(app, tmp_path):
    """A profile with no cookie database must not raise."""
    assert CalTopoAuthDialog._read_persisted_cookies(str(tmp_path / "nope")) == {}
    assert CalTopoAuthDialog._read_persisted_cookies("") == {}


def test_caltopo_auth_dialog_captures_a_newly_set_httponly_cookie(app):
    """A sign-in performed in this window must be captured.

    cookieAdded DOES report HttpOnly cookies as they are set - verified against
    a fresh profile visiting caltopo.com, which delivered the HttpOnly SESSION
    cookie. Only cookies RESTORED from a previous run go unreported, which is
    what the disk snapshot covers. A first login therefore needs no restart.
    """
    from PySide6.QtNetwork import QNetworkCookie

    dialog = CalTopoAuthDialog.__new__(CalTopoAuthDialog)
    CalTopoAuthDialog._cookies_from_store = {}
    try:
        cookie = QNetworkCookie(b"SESSION", b"freshly-set")
        cookie.setDomain("caltopo.com")
        cookie.setPath("/")
        cookie.setHttpOnly(True)

        dialog._on_cookie_added(cookie)

        captured = CalTopoAuthDialog._cookies_from_store
        assert [c['name'] for c in captured.values()] == ['SESSION']
        assert list(captured.values())[0]['rest'] == {'HttpOnly': True}
    finally:
        CalTopoAuthDialog._cookies_from_store = {}


def test_caltopo_auth_dialog_snapshots_cookies_before_opening_the_profile(app, tmp_path):
    """The store must be read before a profile locks it.

    While a QWebEngineProfile is live the cookie file cannot be opened by any
    means on Windows - copy, plain read, sqlite read-only and a full-sharing
    Win32 CreateFileW all fail with a sharing violation. The snapshot taken at
    profile-creation time is therefore the only source for a restored session.
    """
    _write_chromium_cookie_db(str(tmp_path / "Cookies"), [
        ('caltopo.com', 'SESSION', 'restored', None, '/', 1, 1, 0),
    ])

    snapshot = CalTopoAuthDialog._read_persisted_cookies(str(tmp_path))
    CalTopoAuthDialog._disk_cookies = snapshot
    try:
        reader = CalTopoAuthDialog.__new__(CalTopoAuthDialog)
        recovered = reader._cookies_from_disk()
        assert [c['name'] for c in recovered.values()] == ['SESSION']
        # A copy, so a caller cannot corrupt the shared snapshot.
        recovered.clear()
        assert CalTopoAuthDialog._disk_cookies
    finally:
        CalTopoAuthDialog._disk_cookies = {}


def test_caltopo_auth_dialog_stays_open_until_done_is_called(app, qtbot):
    """The dialog must not end its own wait before the user acts.

    Attaching a QWebEngineView forces native-window re-creation, which delivers
    a Hide event; QDialog::setVisible(False) exits a modal loop. exec() was
    therefore returning Rejected a fraction of a second after being called,
    before the user had logged in, and the export was silently abandoned while
    the login window stayed on screen.
    """
    from PySide6.QtCore import QEventLoop, QTimer

    dialog = CalTopoAuthDialog(None)
    qtbot.addWidget(dialog)

    finished = []
    dialog.finished.connect(finished.append)

    # Give the dialog a full second of event processing with no user action.
    loop = QEventLoop()
    QTimer.singleShot(1000, loop.quit)
    loop.exec()

    assert finished == [], "the dialog ended its own wait without done() being called"
    assert dialog.result() != QDialog.Accepted

    # And it still finishes properly when something actually accepts it.
    dialog.accept()
    assert finished == [QDialog.Accepted]


def test_caltopo_auth_dialog_web_view_is_attached_before_any_wait(app):
    """The web view must exist by the time the caller starts waiting."""
    dialog = CalTopoAuthDialog(None)

    assert dialog.web_view is not None
    assert dialog.profile is not None


def test_caltopo_auth_dialog_rereads_url_for_map_id_on_export(app):
    """The map ID must be re-derived when the user clicks, not only on urlChanged.

    A map that was already open, or reached by a route that emitted no
    urlChanged, otherwise leaves map_id unset and the export refuses with
    "No Map Selected" while the user is looking straight at their map.
    """
    from PySide6.QtCore import QUrl

    dialog = CalTopoAuthDialog(None)
    dialog.web_view = MagicMock()
    dialog.web_view.url.return_value = QUrl("https://caltopo.com/map.html#ll=30.6,-97.9&z=15&id=ABC123")

    assert dialog.map_id is None  # no urlChanged was ever delivered

    with patch.object(dialog, 'extract_all_cookies'):
        dialog.on_manual_done_clicked()

    assert dialog.map_id == 'ABC123'


def test_caltopo_auth_dialog_keeps_dialog_open_when_no_map_id(app):
    """Refusing a payload must not close the dialog silently."""
    dialog = CalTopoAuthDialog(None)
    dialog.web_view = MagicMock()
    dialog.web_view.url.return_value = MagicMock(toString=lambda: "https://caltopo.com/map.html")
    dialog.manual_done_button.setEnabled(True)  # as it is once the page has loaded

    with patch('core.views.images.viewer.dialogs.CalTopoAuthDialog.QMessageBox') as mock_msgbox:
        dialog.on_manual_done_clicked()

    mock_msgbox.warning.assert_called_once()
    assert dialog.result() != QDialog.Accepted
    # Still usable: the user can navigate to a map and click again.
    assert dialog.manual_done_button.isEnabled()


def test_caltopo_auth_dialog_defers_cookie_extraction_off_the_js_callback(app):
    """Cookie capture must not run on a runJavaScript reply stack.

    While that stack is live the browser process runs no further tasks:
    cookieAdded is never delivered and the fetch that forces HttpOnly cookie
    processing never reaches the network. Any real work done there deadlocks.
    """
    dialog = CalTopoAuthDialog(None)
    dialog.profile = MagicMock()
    dialog.web_view = MagicMock()

    captured = {}

    def fake_run_javascript(js, callback=None):
        captured['callback'] = callback

    dialog.web_view.page.return_value.runJavaScript.side_effect = fake_run_javascript

    with patch.object(CalTopoAuthDialog, '_extract_cookies_from_store') as extract, \
         patch('core.views.images.viewer.dialogs.CalTopoAuthDialog.QTimer') as mock_timer:
        dialog.extract_all_cookies()
        captured['callback']('{"cookies": {}, "isLoggedIn": true}')

        # Deferred to a later event-loop turn, not called inline.
        extract.assert_not_called()
        mock_timer.singleShot.assert_called_once()
        assert mock_timer.singleShot.call_args[0][0] == 0


def test_caltopo_auth_dialog_shares_one_browser_profile(app):
    """Every dialog reuses one profile so a login survives the dialog closing.

    A per-dialog profile died with its dialog, forcing re-authentication for a
    second export in the same run.
    """
    first = CalTopoAuthDialog._get_shared_profile()
    second = CalTopoAuthDialog._get_shared_profile()

    assert first is second
    assert first.persistentStoragePath() != first.cachePath()
    assert first.persistentCookiesPolicy() == (
        first.PersistentCookiesPolicy.ForcePersistentCookies
    )


def test_color_histogram_dialog_initialization(app):
    """Test ColorHistogramDialog initialization."""
    dialog = ColorHistogramDialog(None)
    assert dialog is not None
    assert dialog.chartWidget.empty_state_text() == "No hue histogram data available"


def test_color_histogram_dialog_updates_range_from_hue_wheel(app, qtbot):
    """Hue wheel edits should update the chart selection and emit range changes."""
    dialog = ColorHistogramDialog(None)
    qtbot.addWidget(dialog)
    dialog.set_histogram_context(
        {
            'color_space': 'HSV',
            'component': 'H',
            'display_suffix': '°',
            'component_matrix': np.array([[0.0, 180.0]], dtype=np.float32),
            'histogram_data': {
                'color_space': 'HSV',
                'component': 'H',
                'bin_edges': np.array([0.0, 120.0, 240.0, 360.0], dtype=np.float32),
                'bin_centers': np.array([60.0, 180.0, 300.0], dtype=np.float32),
                'counts': np.array([1, 1, 0], dtype=np.int32),
                'anomaly_counts': np.array([0, 1, 0], dtype=np.int32),
                'value_precision': 0,
                'min_temperature': 0.0,
                'max_temperature': 360.0,
                'total_pixels': 2,
                'anomaly_pixels': 1,
            }
        }
    )

    # The shared HueRingSelector emits a centre + range (h, h_minus, h_plus);
    # the dialog converts it back to absolute degrees. Drive that signal for a
    # range equivalent to [30, 200].
    h, h_minus, h_plus = dialog._range_to_hsv(30.0, 200.0)
    with qtbot.waitSignal(dialog.rangeChanged):
        dialog.hueWheelSelector.valueChanged.emit(h, h_minus, h_plus)

    minimum, maximum = dialog.chartWidget.selection_range()
    assert minimum == pytest.approx(30.0)
    assert maximum == pytest.approx(200.0)


def test_color_histogram_dialog_toggles_aoi_only_mode(app, qtbot):
    """AOI-only toggle should switch the chart into anomaly-only display mode."""
    dialog = ColorHistogramDialog(None)
    qtbot.addWidget(dialog)
    dialog.set_histogram_context(
        {
            'color_space': 'HSV',
            'component': 'H',
            'display_suffix': '°',
            'component_matrix': np.array([[0.0, 180.0]], dtype=np.float32),
            'histogram_data': {
                'color_space': 'HSV',
                'component': 'H',
                'bin_edges': np.array([0.0, 120.0, 240.0, 360.0], dtype=np.float32),
                'bin_centers': np.array([60.0, 180.0, 300.0], dtype=np.float32),
                'counts': np.array([10, 2, 0], dtype=np.int32),
                'anomaly_counts': np.array([1, 2, 0], dtype=np.int32),
                'anomaly_overlay_mode': 'anomaly_count',
                'value_precision': 0,
                'min_temperature': 0.0,
                'max_temperature': 360.0,
                'total_pixels': 12,
                'anomaly_pixels': 3,
            }
        }
    )

    assert not dialog.chartWidget.show_aoi_only()

    with qtbot.waitSignal(dialog.aoiOnlyModeChanged):
        dialog.showAoiOnlyCheckBox.setChecked(True)

    assert dialog.chartWidget.show_aoi_only()


def test_color_histogram_dialog_range_labels(app, qtbot):
    """Hue range labels should display integer degree values."""
    dialog = ColorHistogramDialog(None)
    qtbot.addWidget(dialog)
    dialog.set_histogram_context(
        {
            'color_space': 'HSV',
            'component': 'H',
            'display_suffix': '°',
            'component_matrix': np.array([[5.0, 25.0, 355.0]], dtype=np.float32),
            'histogram_data': {
                'color_space': 'HSV',
                'component': 'H',
                'bin_edges': np.array([0.0, 120.0, 240.0, 360.0], dtype=np.float32),
                'bin_centers': np.array([60.0, 180.0, 300.0], dtype=np.float32),
                'counts': np.array([1, 1, 1], dtype=np.int32),
                'anomaly_counts': np.array([0, 0, 1], dtype=np.int32),
                'value_precision': 0,
                'min_temperature': 0.0,
                'max_temperature': 360.0,
                'total_pixels': 3,
                'anomaly_pixels': 1,
            }
        }
    )
    dialog.set_selected_range(20.0, 350.0)

    assert "Minimum: 20°" in dialog.minValueLabel.text()
    assert "Maximum: 350°" in dialog.maxValueLabel.text()


def test_export_progress_dialog_initialization(app):
    """Test ExportProgressDialog initialization."""
    dialog = ExportProgressDialog(None, "Test Export", 100)
    assert dialog is not None
    assert dialog._completed_result is None


def test_export_progress_dialog_exec_returns_immediately_after_accept(app):
    """accept() before exec() must not strand the user in a dialog.

    Worker threads deliver completion through the event loop, and callers pump
    events before exec(). A fast failure could therefore accept the dialog
    while it was not in a modal loop; exec() then re-showed it with no worker
    left to close it and (for the CalTopo account load) a Cancel button that
    was wired to nothing.
    """
    dialog = ExportProgressDialog(None, "Test Export", 100)
    dialog.accept()

    # Would block forever before the fix.
    assert dialog.exec() == QDialog.Accepted
    assert not dialog.isVisible()


def test_export_progress_dialog_exec_returns_immediately_after_reject(app):
    """reject() before exec() is preserved too (the cancel path does this)."""
    dialog = ExportProgressDialog(None, "Test Export", 100)
    dialog.reject()

    assert dialog.exec() == QDialog.Rejected
    assert not dialog.isVisible()


def test_export_progress_dialog_can_be_reused_after_completing(app):
    """Showing the dialog again starts a fresh operation.

    Without this, the guard that remembers an early completion would make a
    reused instance permanently unshowable.
    """
    dialog = ExportProgressDialog(None, "Test Export", 100)
    dialog.accept()
    assert dialog.exec() == QDialog.Accepted

    dialog.show()
    assert dialog._completed_result is None
    dialog.hide()


def test_export_progress_dialog_cancel_button_marks_cancelled(app):
    """Cancel records the request so worker loops can stop."""
    dialog = ExportProgressDialog(None, "Test Export", 100)
    assert dialog.is_cancelled() is False

    dialog.on_cancel_clicked()

    assert dialog.is_cancelled() is True


def test_gps_map_dialog_initialization(app):
    """Test GPSMapDialog initialization."""
    # GPSMapDialog requires gps_data (list) and current_image_index
    # GPS data must have 'latitude', 'longitude', and 'index' keys
    gps_data = [
        {'latitude': 37.7749, 'longitude': -122.4194, 'name': 'Image 1', 'index': 0},
        {'latitude': 37.7750, 'longitude': -122.4195, 'name': 'Image 2', 'index': 1}
    ]
    dialog = GPSMapDialog(None, gps_data, 0)
    assert dialog is not None


def test_help_dialog_initialization(app):
    """Test HelpDialog initialization."""
    dialog = HelpDialog(None)
    assert dialog is not None


def test_image_adjustment_dialog_initialization(app):
    """Test ImageAdjustmentDialog initialization."""
    dialog = ImageAdjustmentDialog(None)
    assert dialog is not None


def test_loading_dialog_initialization(app):
    """Test LoadingDialog initialization."""
    # LoadingDialog only takes parent, not a message
    dialog = LoadingDialog(None)
    assert dialog is not None


def test_map_export_dialog_initialization(app):
    """Test MapExportDialog initialization."""
    dialog = MapExportDialog(None)
    assert dialog is not None


def test_measure_dialog_initialization(app):
    """Test MeasureDialog initialization."""
    # MeasureDialog requires image_viewer, current_gsd, and distance_unit
    mock_image_viewer = MagicMock()
    mock_image_viewer.canZoom = True
    mock_image_viewer.canPan = True
    mock_image_viewer.regionZoomButton = MagicMock()

    dialog = MeasureDialog(None, mock_image_viewer, 5.0, 'm')
    assert dialog is not None


def test_measure_dialog_starts_in_length_mode(app):
    """Shadow checkbox is off and the length-mode groups are visible by default."""
    mock_image_viewer = MagicMock()
    mock_image_viewer.canZoom = True
    mock_image_viewer.canPan = True
    mock_image_viewer.regionZoomButton = MagicMock()

    dialog = MeasureDialog(None, mock_image_viewer, 5.0, 'm')
    assert dialog.shadow_mode is False
    assert dialog.shadow_mode_checkbox.isChecked() is False
    assert dialog.gsd_group.isVisibleTo(dialog) is True
    assert dialog.distance_group.isVisibleTo(dialog) is True
    assert dialog.shadow_group.isVisibleTo(dialog) is False


def test_measure_dialog_toggles_into_shadow_mode(app):
    """Toggling the checkbox swaps which result groups are shown."""
    mock_image_viewer = MagicMock()
    mock_image_viewer.canZoom = True
    mock_image_viewer.canPan = True
    mock_image_viewer.regionZoomButton = MagicMock()

    dialog = MeasureDialog(None, mock_image_viewer, 5.0, 'm')
    dialog.shadow_mode_checkbox.setChecked(True)

    assert dialog.shadow_mode is True
    assert dialog.gsd_group.isVisibleTo(dialog) is False
    assert dialog.distance_group.isVisibleTo(dialog) is False
    assert dialog.shadow_group.isVisibleTo(dialog) is True
    assert "Shadow" in dialog.windowTitle()


def test_measure_dialog_toggle_clears_in_flight_measurement(app):
    """Switching modes mid-measurement should reset state, not carry it across."""
    mock_image_viewer = MagicMock()
    mock_image_viewer.canZoom = True
    mock_image_viewer.canPan = True
    mock_image_viewer.regionZoomButton = MagicMock()
    mock_image_viewer.scene = MagicMock()

    dialog = MeasureDialog(None, mock_image_viewer, 5.0, 'm')
    # Simulate the first click of a length measurement.
    dialog.first_point = object()
    dialog.measuring = True

    dialog.shadow_mode_checkbox.setChecked(True)

    assert dialog.first_point is None
    assert dialog.measuring is False


def test_pdf_export_dialog_initialization(app):
    """Test PDFExportDialog initialization."""
    dialog = PDFExportDialog(None)
    assert dialog is not None


def test_reviewer_name_dialog_initialization(app):
    """Test ReviewerNameDialog initialization."""
    dialog = ReviewerNameDialog(None)
    assert dialog is not None


def test_thermal_histogram_dialog_initialization(app):
    """Test ThermalHistogramDialog initialization."""
    dialog = ThermalHistogramDialog(None)
    assert dialog is not None


def test_thermal_histogram_dialog_updates_range_from_slider(app, qtbot):
    """Slider edits should update the chart selection and emit range changes."""
    dialog = ThermalHistogramDialog(None)
    qtbot.addWidget(dialog)

    dialog.set_histogram_data(
        {
            'bin_edges': np.array([10.0, 11.0, 12.0, 13.0], dtype=np.float32),
            'bin_centers': np.array([10.5, 11.5, 12.5], dtype=np.float32),
            'counts': np.array([2, 4, 1], dtype=np.int32),
            'anomaly_counts': np.array([0, 2, 1], dtype=np.int32),
            'min_temperature': 10.0,
            'max_temperature': 13.0,
            'total_pixels': 7,
            'anomaly_pixels': 3,
        },
        'C'
    )

    with qtbot.waitSignal(dialog.rangeChanged):
        dialog.rangeSlider.set_values(11.0, 13.0, emit_signal=True)

    minimum, maximum = dialog.chartWidget.selection_range()
    assert minimum == 11.0
    assert maximum == 13.0
    assert "11.0" in dialog.minValueLabel.text()
    assert "13.0" in dialog.maxValueLabel.text()


def test_thermal_histogram_dialog_resets_zoom(app, qtbot):
    """Reset Zoom should restore the full histogram x-axis range."""
    dialog = ThermalHistogramDialog(None)
    qtbot.addWidget(dialog)

    dialog.set_histogram_data(
        {
            'bin_edges': np.array([10.0, 11.0, 12.0, 13.0], dtype=np.float32),
            'bin_centers': np.array([10.5, 11.5, 12.5], dtype=np.float32),
            'counts': np.array([2, 4, 1], dtype=np.int32),
            'anomaly_counts': np.array([0, 2, 1], dtype=np.int32),
            'min_temperature': 10.0,
            'max_temperature': 13.0,
            'total_pixels': 7,
            'anomaly_pixels': 3,
        },
        'C'
    )

    dialog.chartWidget.set_view_range(11.0, 12.0)
    dialog._update_zoom_button_state()
    assert dialog.resetZoomButton.isEnabled()

    dialog.reset_zoom()
    assert dialog.chartWidget.view_range() == (10.0, 13.0)
    assert not dialog.resetZoomButton.isEnabled()


def test_upscale_dialog_initialization(app):
    """Test UpscaleDialog initialization."""
    dialog = UpscaleDialog(None)
    assert dialog is not None


def test_zip_export_dialog_initialization(app):
    """Test ZipExportDialog initialization."""
    dialog = ZipExportDialog(None)
    assert dialog is not None


def test_grid_review_dialog_initialization(app):
    """Test GridReviewDialog initialization with current values."""
    dialog = GridReviewDialog(None, current_rows=6, current_cols=8,
                              auto_mark=False, sub_guide=False)
    assert dialog.rowsSpinBox.value() == 6
    assert dialog.colsSpinBox.value() == 8
    assert not dialog.autoMarkCheckBox.isChecked()
    assert not dialog.subGuideCheckBox.isChecked()
    # Spinboxes are bounded to a sane grid range.
    assert dialog.rowsSpinBox.minimum() == 1
    assert dialog.rowsSpinBox.maximum() == 12
    # No suggestion provided -> the button stays disabled.
    assert not dialog.useSuggestionButton.isEnabled()


def test_grid_review_dialog_focus_guide_defaults_on(app):
    """The focus-guide toggle defaults on."""
    dialog = GridReviewDialog(None)
    assert dialog.subGuideCheckBox.isChecked()
    assert dialog.sub_guide_enabled()


def test_grid_review_dialog_apply_to_all_defaults_off(app):
    """Apply-to-all is a one-shot action and starts unchecked."""
    dialog = GridReviewDialog(None)
    assert dialog.applyAllCheckBox.isChecked() is False
    assert dialog.apply_to_all() is False
    dialog.applyAllCheckBox.setChecked(True)
    assert dialog.apply_to_all() is True


def test_grid_review_dialog_apply_to_all_not_persisted(app):
    """Apply-to-all is never written to settings (it is not a preference)."""
    settings = MagicMock()
    dialog = GridReviewDialog(None, settings_service=settings)
    dialog.applyAllCheckBox.setChecked(True)
    dialog.accept()
    persisted_keys = [call.args[0] for call in settings.set_setting.call_args_list]
    assert "GridReviewApplyAll" not in persisted_keys
    assert "applyAll" not in persisted_keys


def test_grid_review_dialog_suggestion(app):
    """The GSD suggestion populates the label and the Use Suggestion button."""
    dialog = GridReviewDialog(None, suggestion=(6, 6), person_px=72.4)
    assert dialog.useSuggestionButton.isEnabled()
    assert "6" in dialog.suggestionLabel.text()
    assert "72" in dialog.suggestionLabel.text()

    dialog.useSuggestionButton.click()
    assert dialog.values()[:2] == (6, 6)


def test_grid_review_dialog_accept_persists_settings(app):
    """Accepting the dialog writes the chosen values to settings."""
    settings = MagicMock()
    dialog = GridReviewDialog(None, settings_service=settings,
                              current_rows=5, current_cols=7, auto_mark=True)
    dialog.accept()

    settings.set_setting.assert_any_call("GridReviewRows", 5)
    settings.set_setting.assert_any_call("GridReviewCols", 7)
    settings.set_setting.assert_any_call("GridReviewAutoMark", True)
    settings.set_setting.assert_any_call("GridReviewSubGuide", True)
