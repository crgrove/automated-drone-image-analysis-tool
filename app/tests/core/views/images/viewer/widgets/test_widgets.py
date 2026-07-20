"""
Comprehensive tests for viewer widgets.

Tests QtImageViewer, OverlayWidget, ScaleBarWidget, GPSMapView, etc.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF, QRectF, QEvent, QObject, Qt
from PySide6.QtGui import QPixmap

from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer
from core.views.images.viewer.widgets.OverlayWidget import OverlayWidget
from core.views.images.viewer.widgets.ScaleBarWidget import ScaleBarWidget
from core.views.images.viewer.widgets.GPSMapView import GPSMapView
from core.views.images.viewer.widgets.MapTileLoader import MapTileLoader
from core.views.images.viewer.widgets.ThermalHistogramChart import ThermalHistogramChart
from core.views.images.viewer.widgets.ThermalRangeSlider import ThermalRangeSlider


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_qt_image_viewer_initialization(app):
    """Test QtImageViewer initialization."""
    # QtImageViewer requires window parameter
    mock_window = MagicMock()
    viewer = QtImageViewer(mock_window)
    assert viewer is not None


def test_overlay_widget_initialization(app):
    """Test OverlayWidget initialization."""
    # OverlayWidget requires main_image_widget, scale_bar_widget, and theme
    mock_window = MagicMock()
    main_image_widget = QtImageViewer(mock_window)
    scale_bar_widget = ScaleBarWidget()
    widget = OverlayWidget(main_image_widget, scale_bar_widget, 'Dark')
    assert widget is not None


def test_scale_bar_widget_initialization(app):
    """Test ScaleBarWidget initialization."""
    widget = ScaleBarWidget()
    assert widget is not None


def test_scale_bar_widget_update(app):
    """Test ScaleBarWidget update functionality."""
    widget = ScaleBarWidget()

    # ScaleBarWidget uses setLabel() method, not update_scale_bar
    widget.setLabel("5.0 m")
    assert widget is not None


def test_gps_map_view_initialization(app):
    """Test GPSMapView initialization."""
    view = GPSMapView()
    assert view is not None


def test_map_tile_loader_initialization(app):
    """Test MapTileLoader initialization."""
    loader = MapTileLoader()
    assert loader is not None


def test_thermal_histogram_chart_initialization(app):
    """Test ThermalHistogramChart initialization."""
    chart = ThermalHistogramChart()
    assert chart is not None


def test_thermal_histogram_chart_view_range_updates(app):
    """Histogram chart should support independent x-axis zoom ranges."""
    chart = ThermalHistogramChart()
    chart.set_histogram_data(
        {
            'bin_edges': np.array([10.0, 11.0, 12.0, 13.0], dtype=np.float32),
            'bin_centers': np.array([10.5, 11.5, 12.5], dtype=np.float32),
            'counts': np.array([2, 4, 1], dtype=np.int32),
            'anomaly_counts': np.array([0, 2, 1], dtype=np.int32),
            'min_temperature': 10.0,
            'max_temperature': 13.0,
            'total_pixels': 7,
            'anomaly_pixels': 3,
        }
    )

    chart.set_view_range(11.0, 12.5)
    assert chart.view_range() == (11.0, 12.5)

    chart.reset_view_range()
    assert chart.view_range() == (10.0, 13.0)


def test_thermal_histogram_chart_zoom_around_temperature(app):
    """Wheel-zoom helper should zoom around the requested temperature anchor."""
    chart = ThermalHistogramChart()
    chart.set_histogram_data(
        {
            'bin_edges': np.array([10.0, 11.0, 12.0, 13.0], dtype=np.float32),
            'bin_centers': np.array([10.5, 11.5, 12.5], dtype=np.float32),
            'counts': np.array([2, 4, 1], dtype=np.int32),
            'anomaly_counts': np.array([0, 2, 1], dtype=np.int32),
            'min_temperature': 10.0,
            'max_temperature': 13.0,
            'total_pixels': 7,
            'anomaly_pixels': 3,
        }
    )

    chart.zoom_around_temperature(11.5, zoom_in=True)
    zoomed_min, zoomed_max = chart.view_range()
    assert zoomed_min > 10.0
    assert zoomed_max < 13.0
    assert zoomed_min <= 11.5 <= zoomed_max

    chart.zoom_around_temperature(11.5, zoom_in=False)
    reset_min, reset_max = chart.view_range()
    assert reset_min <= zoomed_min
    assert reset_max >= zoomed_max


def test_thermal_histogram_chart_overlay_count_modes(app):
    """Overlay height should be configurable between full-bin and anomaly-count modes."""
    counts = np.array([10, 20, 30], dtype=np.int32)
    anomaly_counts = np.array([1, 4, 2], dtype=np.int32)

    assert ThermalHistogramChart._overlay_count_for_index(1, counts, anomaly_counts, 'full_bin') == 20.0
    assert ThermalHistogramChart._overlay_count_for_index(1, counts, anomaly_counts, 'anomaly_count') == 4.0


def test_thermal_histogram_chart_sparse_aoi_bar_stays_visible(app):
    """AOI overlay bars in sparse bins should clamp to a minimum height, not vanish."""
    chart = ThermalHistogramChart()
    chart.resize(600, 300)
    chart.set_histogram_data(
        {
            'bin_edges': np.array([10.0, 11.0, 12.0, 13.0], dtype=np.float32),
            'bin_centers': np.array([10.5, 11.5, 12.5], dtype=np.float32),
            'counts': np.array([1, 100000, 3], dtype=np.int32),
            'anomaly_counts': np.array([1, 0, 0], dtype=np.int32),
            'min_temperature': 10.0,
            'max_temperature': 13.0,
            'total_pixels': 100004,
            'anomaly_pixels': 1,
        }
    )
    plot_rect = chart._plot_rect()
    max_count = chart._max_visible_count()

    # Without clamping, a 1-in-100k bin is sub-pixel and disappears.
    unclamped = chart._bar_rect_for_index(0, 1.0, max_count, plot_rect, width_ratio=0.55)
    assert unclamped.isEmpty()

    clamped = chart._bar_rect_for_index(
        0, 1.0, max_count, plot_rect,
        width_ratio=0.55,
        min_height=ThermalHistogramChart.MIN_AOI_BAR_HEIGHT
    )
    assert not clamped.isEmpty()
    assert clamped.height() >= ThermalHistogramChart.MIN_AOI_BAR_HEIGHT

    # Bins outside the zoomed view range must still be culled.
    chart.set_view_range(11.0, 13.0)
    off_screen = chart._bar_rect_for_index(
        0, 1.0, max_count, plot_rect,
        width_ratio=0.55,
        min_height=ThermalHistogramChart.MIN_AOI_BAR_HEIGHT
    )
    assert off_screen.isEmpty()


# --------------------------------------------------------------------------- #
#  Wheel-zoom freeze regression: the per-tick overlay/refit paths must not    #
#  feed the resize -> fitInView -> emit -> re-layout -> resize livelock.      #
# --------------------------------------------------------------------------- #

class _EventCounter(QObject):
    """Counts deliveries of a single event type to the filtered object."""

    def __init__(self, event_type):
        super().__init__()
        self.event_type = event_type
        self.count = 0

    def eventFilter(self, obj, event):
        if event.type() == self.event_type:
            self.count += 1
        return False


def _viewer_with_image(qtbot, width=400, height=300):
    viewer = QtImageViewer(MagicMock())
    qtbot.addWidget(viewer)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.darkGray)
    viewer.setImage(pixmap)
    return viewer


GSD_MESSAGES = {"Estimated Average GSD": "3.2cm/px"}


def test_zoom_tick_path_posts_no_layout_request(app, qtbot):
    """Regression: zoom/pan emissions must not invalidate viewport layout.

    _place_overlay used to call adjustSize()+updateGeometry() on every
    viewChanged/zoomChanged emission; updateGeometry() posts a LayoutRequest
    to the viewport, which re-runs QAbstractScrollArea layout and can resize
    the view, refit, and re-emit — an event-loop livelock that froze the app
    during wheel zoom.
    """
    viewer = _viewer_with_image(qtbot)
    scale_bar = ScaleBarWidget()
    overlay = OverlayWidget(viewer, scale_bar, 'Dark')
    viewer.show()
    qtbot.waitExposed(viewer)

    # Drive the one-time content transitions (scale bar appears) first.
    overlay.update_scale_bar(2.0, GSD_MESSAGES, 'm')
    QApplication.processEvents()

    counter = _EventCounter(QEvent.LayoutRequest)
    viewer.viewport().installEventFilter(counter)
    try:
        for _ in range(25):
            viewer.viewChanged.emit()
            viewer.zoomChanged.emit(2.0)
            overlay.update_scale_bar(2.0, GSD_MESSAGES, 'm')
        QApplication.processEvents()
    finally:
        viewer.viewport().removeEventFilter(counter)

    assert counter.count == 0


def test_resize_refits_synchronously(app, qtbot):
    """Regression (zoom jitter): resizeEvent must refit synchronously.

    Deferring the refit to a timer moves it outside updateViewer's
    _recursion_guard, so a scrollbar flip that fitInView provokes restarts the
    timer and drives a resize<->fit oscillation across event-loop turns —
    visible as the view jittering in and out at the one-click zoom threshold.
    """
    from PySide6.QtGui import QResizeEvent
    from PySide6.QtCore import QSize

    viewer = _viewer_with_image(qtbot)
    viewer.show()
    qtbot.waitExposed(viewer)
    qtbot.wait(30)

    calls = []
    viewer.updateViewer = lambda *a, **k: calls.append(1)

    ev = QResizeEvent(QSize(viewer.width() + 40, viewer.height() + 20), viewer.size())
    viewer.resizeEvent(ev)

    assert calls, "resizeEvent must refit synchronously (no deferred timer)"


def test_scrollbars_disabled(app, qtbot):
    """Regression (hard lock): the main viewer must disable both scrollbars.

    With ScrollBarAsNeeded, fitInView on a zoomed sub-rect makes the scene
    overflow -> a scrollbar appears -> the viewport shrinks -> resizeEvent ->
    updateViewer -> fitInView flips it back, oscillating forever inside Qt's
    C++ layout (GUI hard-lock at the one-click zoom threshold). Turning the
    bars off removes the toggle entirely; panning does not need them (drag-pan
    translates the zoom rect from the raw mouse delta).
    """
    viewer = _viewer_with_image(qtbot)
    assert viewer.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert viewer.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOff


def test_drag_pan_translates_zoom_rect_without_scrollbars(app, qtbot):
    """Right-button drag pans by translating the zoom rect (no scrollbars).

    Since the fix disables scrollbars, panning must not rely on ScrollHandDrag.
    Dragging right reveals content to the left, so the zoom rect moves left,
    and its size (zoom level) stays constant.
    """
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent

    win = MagicMock()
    win.aoi_creation_mode = False
    viewer = QtImageViewer(win)
    qtbot.addWidget(viewer)
    pm = QPixmap(4000, 3000)
    pm.fill(Qt.darkGray)
    viewer.setImage(pm)
    viewer.resize(600, 400)
    viewer.show()
    qtbot.waitExposed(viewer)
    qtbot.wait(20)

    viewer.zoomToArea((2000, 1500), 4)
    assert viewer.zoomStack, "zoomToArea should push a zoom rect"
    before = QRectF(viewer.zoomStack[-1])

    def _ev(kind, x, y, button, buttons):
        return QMouseEvent(kind, QPointF(x, y), QPointF(x, y),
                           button, buttons, Qt.NoModifier)

    viewer.mousePressEvent(_ev(QEvent.MouseButtonPress, 300, 200,
                               Qt.RightButton, Qt.RightButton))
    assert viewer._isPanning
    viewer.mouseMoveEvent(_ev(QEvent.MouseMove, 360, 200,
                              Qt.NoButton, Qt.RightButton))   # drag right
    viewer.mouseReleaseEvent(_ev(QEvent.MouseButtonRelease, 360, 200,
                                 Qt.RightButton, Qt.NoButton))
    assert not viewer._isPanning

    after = viewer.zoomStack[-1]
    assert after.left() < before.left(), "drag-right must move the zoom rect left"
    assert abs(after.width() - before.width()) < 1e-6, "pan must not change zoom"
    assert abs(after.height() - before.height()) < 1e-6


# --------------------------------------------------------------------------- #
#  Trackpad / wheel routing: mouse wheel zooms; a trackpad two-finger scroll   #
#  pans; Ctrl/Cmd + trackpad scroll zooms — so a laptop user with no mouse     #
#  can always both pan and zoom (never depends on a wheel that isn't there).   #
# --------------------------------------------------------------------------- #

def _wheel_event(pos, pixel_delta, angle_delta, modifier=Qt.NoModifier):
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtCore import QPoint
    p = QPointF(*pos)
    return QWheelEvent(p, p, QPoint(*pixel_delta), QPoint(*angle_delta),
                       Qt.NoButton, modifier, Qt.NoScrollPhase, False)


def _zoomed_viewer(qtbot):
    viewer = _viewer_with_image(qtbot, 4000, 3000)
    viewer.resize(600, 400)
    viewer.show()
    qtbot.waitExposed(viewer)
    qtbot.wait(20)
    return viewer


def test_mouse_wheel_zooms(app, qtbot):
    viewer = _zoomed_viewer(qtbot)
    assert not viewer.zoomStack
    # Mouse wheel: angleDelta only, no pixelDelta -> zoom in.
    viewer.wheelEvent(_wheel_event((300, 200), (0, 0), (0, 120)))
    assert viewer.zoomStack, "mouse wheel up should zoom in"
    assert viewer.zoomStack[-1].width() < viewer.sceneRect().width()


def test_trackpad_two_finger_scroll_pans(app, qtbot):
    viewer = _zoomed_viewer(qtbot)
    viewer.zoomToArea((2000, 1500), 4)
    assert viewer.zoomStack
    before = QRectF(viewer.zoomStack[-1])
    # Trackpad scroll: pixelDelta present, no modifier -> pan (not zoom).
    viewer.wheelEvent(_wheel_event((300, 200), (40, 0), (0, 0)))
    after = viewer.zoomStack[-1]
    assert after.left() < before.left(), "two-finger scroll should pan"
    assert abs(after.width() - before.width()) < 1e-6, "pan must not change zoom"


def test_ctrl_trackpad_scroll_zooms(app, qtbot):
    viewer = _zoomed_viewer(qtbot)
    viewer.zoomToArea((2000, 1500), 4)
    before_w = viewer.zoomStack[-1].width()
    # Trackpad scroll WITH Ctrl -> zoom, even though pixelDelta is present.
    viewer.wheelEvent(_wheel_event((300, 200), (0, 40), (0, 0), Qt.ControlModifier))
    assert viewer.zoomStack[-1].width() < before_w, "Ctrl+two-finger scroll should zoom in"


# --------------------------------------------------------------------------- #
#  Spacebar pan (Photoshop/Figma fallback): hold Space + left-drag pans;       #
#  without Space the left button still does region-zoom. Works on any device.  #
# --------------------------------------------------------------------------- #

def _mouse_event(kind, x, y, button, buttons):
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent
    p = QPointF(x, y)
    return QMouseEvent(kind, p, p, button, buttons, Qt.NoModifier)


def test_spacebar_left_drag_pans(app, qtbot):
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent

    win = MagicMock()
    win.aoi_creation_mode = False
    viewer = QtImageViewer(win)
    qtbot.addWidget(viewer)
    pm = QPixmap(4000, 3000)
    pm.fill(Qt.darkGray)
    viewer.setImage(pm)
    viewer.resize(600, 400)
    viewer.show()
    qtbot.waitExposed(viewer)
    qtbot.wait(20)
    viewer.zoomToArea((2000, 1500), 4)
    before = QRectF(viewer.zoomStack[-1])

    viewer.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Space, Qt.NoModifier))
    assert viewer._space_held

    viewer.mousePressEvent(_mouse_event(QEvent.MouseButtonPress, 300, 200,
                                        Qt.LeftButton, Qt.LeftButton))
    assert viewer._isPanning, "Space + left press should pan, not region-zoom"
    viewer.mouseMoveEvent(_mouse_event(QEvent.MouseMove, 360, 200,
                                       Qt.NoButton, Qt.LeftButton))
    viewer.mouseReleaseEvent(_mouse_event(QEvent.MouseButtonRelease, 360, 200,
                                          Qt.LeftButton, Qt.NoButton))
    assert not viewer._isPanning

    after = viewer.zoomStack[-1]
    assert after.left() < before.left(), "Space+drag-right must pan left"
    assert abs(after.width() - before.width()) < 1e-6, "pan must not change zoom"

    viewer.keyReleaseEvent(QKeyEvent(QEvent.KeyRelease, Qt.Key_Space, Qt.NoModifier))
    assert not viewer._space_held


def test_left_drag_without_space_does_not_pan(app, qtbot):
    from PySide6.QtCore import QEvent

    win = MagicMock()
    win.aoi_creation_mode = False
    viewer = QtImageViewer(win)
    qtbot.addWidget(viewer)
    pm = QPixmap(4000, 3000)
    pm.fill(Qt.darkGray)
    viewer.setImage(pm)
    viewer.resize(600, 400)
    viewer.show()
    qtbot.waitExposed(viewer)
    qtbot.wait(20)
    viewer.zoomToArea((2000, 1500), 4)

    viewer.mousePressEvent(_mouse_event(QEvent.MouseButtonPress, 300, 200,
                                        Qt.LeftButton, Qt.LeftButton))
    assert not viewer._isPanning, "left-drag without Space must not pan (region-zoom)"
    viewer.mouseReleaseEvent(_mouse_event(QEvent.MouseButtonRelease, 300, 200,
                                          Qt.LeftButton, Qt.NoButton))


def test_focus_out_resets_space_state(app, qtbot):
    from PySide6.QtGui import QKeyEvent, QFocusEvent
    from PySide6.QtCore import QEvent

    viewer = _viewer_with_image(qtbot)
    viewer.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Space, Qt.NoModifier))
    assert viewer._space_held
    viewer.focusOutEvent(QFocusEvent(QEvent.FocusOut))
    assert not viewer._space_held, "losing focus must not strand the viewer in pan mode"


def test_recursion_guard_blocks_reentrant_refit(app, qtbot):
    """The guard must absorb a fit-provoked resize so it cannot oscillate.

    While _recursion_guard is set (updateViewer already running), a re-entrant
    updateViewer — e.g. from a scrollbar-toggle resizeEvent fired inside
    fitInView — must be a no-op and never reach fitInView again.
    """
    viewer = _viewer_with_image(qtbot)
    viewer.show()
    qtbot.waitExposed(viewer)
    qtbot.wait(30)

    fit_calls = []
    viewer.fitInView = lambda rect, mode: fit_calls.append(1)

    viewer._recursion_guard = True
    viewer.updateViewer()

    assert fit_calls == [], "updateViewer must no-op while the recursion guard is set"


def test_place_overlay_only_moves_and_raises(app, qtbot):
    """_place_overlay must not resize the overlay on the per-tick path."""
    viewer = _viewer_with_image(qtbot)
    scale_bar = ScaleBarWidget()
    overlay = OverlayWidget(viewer, scale_bar, 'Dark')
    viewer.show()
    qtbot.waitExposed(viewer)
    overlay.update_scale_bar(2.0, GSD_MESSAGES, 'm')
    QApplication.processEvents()

    size_before = overlay.size()
    for _ in range(10):
        overlay._place_overlay()
    assert overlay.size() == size_before


def test_scale_bar_visibility_flip_resizes_overlay(app, qtbot):
    """Overlay size must track scale-bar visibility flips (and only flips)."""
    viewer = _viewer_with_image(qtbot)
    scale_bar = ScaleBarWidget()
    overlay = OverlayWidget(viewer, scale_bar, 'Dark')

    overlay.adjustSize()
    width_without_bar = overlay.width()

    overlay._set_scale_bar_visible(True)
    width_with_bar = overlay.width()
    assert width_with_bar > width_without_bar

    # Same-state call must be a no-op.
    overlay._set_scale_bar_visible(True)
    assert overlay.width() == width_with_bar

    overlay._set_scale_bar_visible(False)
    assert overlay.width() < width_with_bar


def test_scale_bar_flip_detected_while_overlay_hidden(app, qtbot):
    """Flip detection must use the explicit flag, not effective visibility.

    While the overlay is auto-hidden, isVisible() is False for the scale bar
    regardless of its own state; a naive check would miss the hide flip and
    leave a stale scale bar armed for the next show.
    """
    viewer = _viewer_with_image(qtbot)
    scale_bar = ScaleBarWidget()
    overlay = OverlayWidget(viewer, scale_bar, 'Dark')
    overlay.hide()

    overlay._set_scale_bar_visible(True)
    assert not scale_bar.isHidden()

    overlay._set_scale_bar_visible(False)
    assert scale_bar.isHidden()


# --------------------------------------------------------------------------- #
#  Freeze regression: the GPS zoom-FOV redraw runs on the GUI thread for every #
#  viewChanged (pan/zoom). Its per-edge terrain refinement must use cached     #
#  tiles only, so a cache miss falls back to flat instantly instead of         #
#  blocking on a network download.                                            #
# --------------------------------------------------------------------------- #

def test_zoom_fov_terrain_lookup_is_offline_only(app, monkeypatch):
    import core.views.images.viewer.widgets.GPSMapView as gpsmod
    from core.services.terrain.TerrainService import ElevationResult

    view = GPSMapView()
    view._fov_cache = {
        'mode': 'raycast',
        'gsd_m': 0.05,
        'width': 4000,
        'height': 3000,
        'bearing': 90.0,
        'image_lat': 38.0,
        'image_lon': -121.0,
        'has_raycast': True,
        'terrain_res_m': 38.0,
        'roll': 0.0,
        'cx': 2000.0,
        'cy': 1500.0,
        'focal_mm': 8.8,
        'sensor_w_mm': 13.2,
        'sensor_h_mm': 8.8,
        'effective_agl': 100.0,
        'pitch': -90.0,
        'yaw': 90.0,
        'drone_absolute_elev': 200.0,
    }

    calls = []

    class _RecordingTerrain:
        enabled = True

        def get_elevation(self, lat, lon, offline_only=False):
            calls.append(offline_only)
            return ElevationResult(
                elevation_m=50.0, source='terrain', geoid_undulation_m=None,
                provider='test', zoom_level=12, resolution_m=38, from_cache=True,
            )

    monkeypatch.setattr(gpsmod, '_get_terrain_service', lambda: _RecordingTerrain())
    monkeypatch.setattr(gpsmod.AOIService, '_calculate_ground_position',
                        staticmethod(lambda *a, **k: (38.0, -121.0)))
    monkeypatch.setattr(view, '_use_terrain_enabled', lambda: True)
    monkeypatch.setattr(view, '_generate_edge_pixels', lambda *a, **k: [(0, 0)])
    monkeypatch.setattr(view, 'lat_lon_to_scene', lambda lat, lon: QPointF(0.0, 0.0))
    monkeypatch.setattr(view, '_add_zoom_fov_polygon', lambda *a, **k: None)

    view.update_zoom_fov_box(QRectF(100.0, 100.0, 500.0, 500.0))

    assert calls, "terrain refinement did not run"
    assert all(flag is True for flag in calls)


def test_thermal_histogram_chart_can_show_aoi_only(app):
    """Chart should track AOI-only display state."""
    chart = ThermalHistogramChart()
    assert not chart.show_aoi_only()

    chart.set_show_aoi_only(True)
    assert chart.show_aoi_only()


def test_thermal_range_slider_initialization(app):
    """Test ThermalRangeSlider initialization."""
    slider = ThermalRangeSlider()
    assert slider is not None


def test_thermal_range_slider_track_visual_updates(app):
    """Slider should support alternate track visuals for hue ranges."""
    slider = ThermalRangeSlider()
    assert slider.track_visual() == 'neutral'

    slider.set_track_visual('hue_wheel')
    assert slider.track_visual() == 'hue_wheel'


def test_thermal_range_slider_wrap_updates(app):
    """Slider should track wrap-mode state for hue selections."""
    slider = ThermalRangeSlider()
    assert not slider.selection_wrap()

    slider.set_selection_wrap(True)
    assert slider.selection_wrap()
