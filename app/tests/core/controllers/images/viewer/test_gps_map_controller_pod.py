"""Tests for the POD overlay orchestration + cell inspect on GPSMapController."""

import os
import pathlib
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication, QMessageBox

from core.controllers.images.viewer.GPSMapController import GPSMapController
from core.services.coverage.params import PodParams
from core.services.coverage.contracts import CoverageResult, LIMIT_CANOPY
from core.services.terrain.grid import make_lattice_spec, lonlat_to_mercator


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def _controller(app):
    parent = MagicMock()
    parent.images = [{"name": "A"}, {"name": "B"}]
    return GPSMapController(parent)


def _real_result(rows=40, cols=30):
    minx, miny = lonlat_to_mercator(-120.50, 38.70)
    spec = make_lattice_spec((minx, miny, minx + cols * 3.0, miny + rows * 3.0), 3.0)
    pod = np.full((spec.height, spec.width), 0.6, dtype=np.float32)
    look = np.full((spec.height, spec.width), 2, dtype=np.uint16)
    return CoverageResult(pod=pod, look_count=look, transform=spec.transform,
                          image_count=2, skipped=[], stats={}, gap_polygons=[],
                          cancelled=False, params=PodParams())


def _controller_with_result(app, result):
    ctrl = _controller(app)
    ctrl.parent.distance_unit = 'ft'
    cache = MagicMock()
    cache.has_result.return_value = result is not None
    cache.get_result.return_value = result
    ctrl.parent.pod_result_cache = cache
    return ctrl


def test_altitude_basis_reports_takeoff_elevation_in_viewer_units(app):
    """The inspect menu outlives the completion toast, so the takeoff elevation
    stays checkable against the known launch point while the overlay is up."""
    result = _real_result()
    result.altitude_anchor_m = 900.0
    result.altitude_source_counts = {'anchor': 12}

    label = _controller_with_result(app, result)._altitude_basis_label()

    assert label == "Altitude basis: takeoff elevation 2953 ft"


def test_altitude_basis_reports_takeoff_elevation_in_metres(app):
    result = _real_result()
    result.altitude_anchor_m = 900.0
    result.altitude_source_counts = {'anchor': 12}
    ctrl = _controller_with_result(app, result)
    ctrl.parent.distance_unit = 'm'

    assert ctrl._altitude_basis_label() == "Altitude basis: takeoff elevation 900 m"


def test_altitude_basis_flags_the_reported_agl_fallback(app):
    result = _real_result()
    result.altitude_source_counts = {'agl_nadir': 12}

    label = _controller_with_result(app, result)._altitude_basis_label()

    assert label == "Altitude basis: reported AGL (approximate over terrain)"


def test_altitude_basis_is_absent_for_an_all_override_run(app):
    result = _real_result()
    result.altitude_source_counts = {'agl_override': 12}

    assert _controller_with_result(app, result)._altitude_basis_label() is None


def test_altitude_basis_is_absent_without_a_cached_result(app):
    assert _controller_with_result(app, None)._altitude_basis_label() is None


def test_altitude_basis_tolerates_a_legacy_result(app):
    """Back-compat: results cached before the anchor existed lack both fields."""
    ctrl = _controller_with_result(app, _real_result())

    assert ctrl._altitude_basis_label() is None


def test_inspect_menu_includes_the_altitude_basis(app):
    result = _real_result()
    result.altitude_anchor_m = 900.0
    result.altitude_source_counts = {'anchor': 12}
    ctrl = _controller_with_result(app, result)
    ctrl.map_dialog = None
    sample = {'pod': 0.6, 'looks': 2, 'limiting_factor': LIMIT_CANOPY, 'frames': []}

    with patch('core.controllers.images.viewer.GPSMapController.QMenu') as menu_cls:
        ctrl._show_pod_inspect_menu(sample, 38.71, -120.49)

    labels = [c.args[0] for c in menu_cls.return_value.addAction.call_args_list]
    assert any("takeoff elevation 2953 ft" in text for text in labels)


def test_click_with_overlay_shows_inspect_menu(app):
    ctrl = _controller(app)
    ctrl._pod_overlay_enabled = True
    ctrl._show_pod_inspect_menu = MagicMock()
    ctrl._reverse_locate = MagicMock()

    result = MagicMock()
    result.sample.return_value = {'pod': 0.6, 'looks': 2, 'limiting_factor': LIMIT_CANOPY, 'frames': [0]}
    cache = MagicMock()
    cache.has_result.return_value = True
    cache.get_result.return_value = result
    ctrl.parent.pod_result_cache = cache

    ctrl.on_map_gps_clicked(38.71, -120.49)
    ctrl._show_pod_inspect_menu.assert_called_once()
    ctrl._reverse_locate.assert_not_called()


def test_click_off_coverage_falls_back_to_reverse_locate(app):
    ctrl = _controller(app)
    ctrl._pod_overlay_enabled = True
    ctrl._show_pod_inspect_menu = MagicMock()
    ctrl._reverse_locate = MagicMock()

    result = MagicMock()
    result.sample.return_value = None
    cache = MagicMock()
    cache.has_result.return_value = True
    cache.get_result.return_value = result
    ctrl.parent.pod_result_cache = cache

    ctrl.on_map_gps_clicked(0.0, 0.0)
    ctrl._show_pod_inspect_menu.assert_not_called()
    ctrl._reverse_locate.assert_called_once()


def test_click_overlay_disabled_uses_reverse_locate(app):
    ctrl = _controller(app)
    ctrl._pod_overlay_enabled = False
    ctrl._reverse_locate = MagicMock()
    ctrl.on_map_gps_clicked(38.71, -120.49)
    ctrl._reverse_locate.assert_called_once()


def test_build_pod_pixmap_downsamples_and_rescales(app):
    ctrl = _controller(app)
    result = _real_result(rows=2100, cols=40)   # > 2048 -> shrinks
    pixmap, transform6 = ctrl._build_pod_pixmap(result, 'pod')
    assert pixmap.width() <= 2048 and pixmap.height() <= 2048
    a0 = tuple(result.transform)[0]
    # Cell size grows because the raster was downsampled.
    assert transform6[0] > a0


class _FakeCanopySample:
    def __init__(self, chm):
        self.chm = chm


def _fake_canopy(chm_value=12.0):
    svc = MagicMock()

    def sample(spec):
        chm = np.full((spec.height, spec.width), chm_value, dtype=np.float32)
        return _FakeCanopySample(chm)

    svc.sample_grid_spec.side_effect = sample
    return svc


def _canopy_controller(app, canopy=None, result=None):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl.map_dialog.map_view = MagicMock()
    cache = MagicMock()
    cache.has_result.return_value = result is not None
    cache.get_result.return_value = result
    ctrl.parent.pod_result_cache = cache
    ctrl._canopy_svc = canopy
    ctrl._canopy_svc_loaded = True
    return ctrl


def _run_canopy_workers_synchronously():
    """Patch the overlay worker so start() runs its body inline (the repo's
    established pattern for testing QThread-backed flows without racing)."""
    from core.controllers.images.viewer.GPSMapController import _CanopyOverlayWorker
    return patch.object(_CanopyOverlayWorker, 'start', lambda self: self.run(),
                        create=False)


def test_canopy_mode_sets_overlay_from_canopy_service(app):
    """The canopy overlay is built on a worker and delivered to the view."""
    ctrl = _canopy_controller(app, canopy=_fake_canopy(), result=_real_result())
    with _run_canopy_workers_synchronously():
        ctrl.on_pod_display_changed(True, 'canopy', 50)
    assert ctrl._pod_overlay_enabled is True
    assert ctrl._pod_overlay_mode == 'canopy'
    ctrl.map_dialog.map_view.set_pod_overlay.assert_called_once()
    ctrl.map_dialog.map_view.set_pod_overlay_opacity.assert_called_with(0.5)


def test_canopy_mode_without_source_clears_and_toasts(app):
    ctrl = _canopy_controller(app, canopy=None, result=_real_result())
    with _run_canopy_workers_synchronously():
        ctrl.on_pod_display_changed(True, 'canopy', 50)
    assert ctrl._pod_overlay_enabled is False
    ctrl.map_dialog.map_view.clear_pod_overlay.assert_called_once()
    ctrl.parent.status_controller.show_toast.assert_called_once()


def test_canopy_overlay_build_happens_off_gui_thread_contract(app):
    """_build_canopy_rgba (the worker body) returns plain numpy — no QPixmap.

    QPixmap must only be created on the GUI thread; the worker/GUI split relies
    on the worker emitting an ndarray that the delivery slot converts.
    """
    canopy = _fake_canopy()
    ctrl = _canopy_controller(app, canopy=canopy, result=_real_result())
    spec = ctrl._canopy_extent_spec()
    rgba = ctrl._build_canopy_rgba(canopy, spec, ctrl.logger)
    assert isinstance(rgba, np.ndarray)
    assert rgba.ndim == 3 and rgba.shape[2] == 4  # RGBA


def test_canopy_delivery_dropped_if_overlay_toggled_off(app):
    """A worker result arriving after the overlay was disabled is discarded."""
    ctrl = _canopy_controller(app, canopy=_fake_canopy(), result=_real_result())
    spec = ctrl._canopy_extent_spec()
    ctrl._pod_overlay_enabled = False  # toggled off while the worker ran
    ctrl._on_canopy_overlay_built(np.zeros((4, 4, 4), dtype=np.uint8), spec)
    ctrl.map_dialog.map_view.set_pod_overlay.assert_not_called()


def test_canopy_second_request_uses_cache_without_new_worker(app):
    """Once built, re-enabling the canopy overlay hits the pixmap cache."""
    canopy = _fake_canopy()
    ctrl = _canopy_controller(app, canopy=canopy, result=_real_result())
    with _run_canopy_workers_synchronously():
        ctrl.on_pod_display_changed(True, 'canopy', 50)
        ctrl.on_pod_display_changed(True, 'canopy', 70)
    assert canopy.sample_grid_spec.call_count == 1
    assert ctrl.map_dialog.map_view.set_pod_overlay.call_count == 2


def test_map_dialog_close_releases_canopy_datasets(app):
    """Closing the map deterministically closes the canopy service (open
    Meta/WRI COGs hold large mappings and block re-downloads on Windows)."""
    canopy = _fake_canopy()
    ctrl = _canopy_controller(app, canopy=canopy, result=_real_result())
    ctrl.on_map_dialog_closed()
    canopy.close.assert_called_once()
    assert ctrl._canopy_svc is None
    assert ctrl._canopy_svc_loaded is False


def test_canopy_download_closes_datasets_before_fetch(app):
    """Re-downloading must close open tile handles first (Windows can't
    overwrite an open file) and drop the stale overlay cache."""
    canopy = _fake_canopy()
    ctrl = _canopy_controller(app, canopy=canopy, result=_real_result())
    ctrl._canopy_overlay_cache = ("stale", None, None)
    ctrl._is_offline_only = lambda: False
    ctrl._run_tile_fetch = MagicMock(return_value=True)
    ctrl._refresh_overlay_availability = MagicMock()
    ctrl.on_canopy_download_requested()
    canopy.close.assert_called_once()
    assert ctrl._canopy_overlay_cache is None


def test_canopy_extent_uses_gps_bounds_without_result(app):
    ctrl = _controller(app)
    ctrl.parent.pod_result_cache = None
    ctrl.gps_data = [
        {'latitude': 38.70, 'longitude': -120.50},
        {'latitude': 38.71, 'longitude': -120.49},
    ]
    spec = ctrl._canopy_extent_spec()
    assert spec is not None
    assert spec.crs == "EPSG:3857"
    min_lon, min_lat, max_lon, max_lat = spec.wgs84_bounds()
    # Padded outward beyond the raw GPS bounding box.
    assert min_lon < -120.50 and max_lon > -120.49
    assert min_lat < 38.70 and max_lat > 38.71
    assert max(spec.width, spec.height) <= ctrl._max_overlay_dim + 2


def test_canopy_extent_matches_pod_grid_when_result_cached(app):
    result = _real_result()
    ctrl = _canopy_controller(app, canopy=_fake_canopy(), result=result)
    spec = ctrl._canopy_extent_spec()
    assert spec.transform == result.transform
    assert (spec.height, spec.width) == result.pod.shape


def test_canopy_pixmap_cached_per_extent(app):
    canopy = _fake_canopy()
    ctrl = _canopy_controller(app, canopy=canopy, result=_real_result())
    first = ctrl._build_canopy_pixmap()
    second = ctrl._build_canopy_pixmap()
    assert first is not None and second is not None
    assert canopy.sample_grid_spec.call_count == 1


def test_on_pod_display_changed_sets_and_clears_overlay(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    view = MagicMock()
    ctrl.map_dialog.map_view = view
    cache = MagicMock()
    cache.has_result.return_value = True
    cache.get_result.return_value = _real_result()
    ctrl.parent.pod_result_cache = cache

    ctrl.on_pod_display_changed(True, 'pod', 60)
    assert ctrl._pod_overlay_enabled is True
    view.set_pod_overlay.assert_called_once()
    view.set_pod_overlay_opacity.assert_called_with(0.6)

    ctrl.on_pod_display_changed(False, 'pod', 60)
    assert ctrl._pod_overlay_enabled is False
    view.clear_pod_overlay.assert_called_once()


# ---------------- _show_pod_inspect_menu ----------------


def _capture_inspect_menu(ctrl, sample, lat=38.71, lon=-120.49):
    """Invoke _show_pod_inspect_menu with a non-modal QMenu and return the menu
    it built.

    The real ``QMenu.exec`` opens a blocking modal popup, which would hang a
    headless test run. Monkeypatching ``QMenu.exec`` on the C++ class does not
    take effect (Shiboken does not dispatch through it), so instead we swap the
    module-level ``QMenu`` name the controller imports for a real QMenu subclass
    whose ``exec`` is a no-op and which records each instance it creates. That
    keeps addAction/addSeparator/actions() behaving exactly like the real menu.

    map_dialog is left at its default None so the menu parent is None; a
    MagicMock map_view is not a valid QWidget parent for QMenu.
    """
    from unittest.mock import patch
    from PySide6.QtWidgets import QMenu

    built = []

    class _NoExecMenu(QMenu):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            built.append(self)

        def exec(self, *a, **k):
            return None

        exec_ = exec

    target = 'core.controllers.images.viewer.GPSMapController.QMenu'
    with patch(target, _NoExecMenu):
        ctrl._show_pod_inspect_menu(sample, lat, lon)
    assert built, "expected the controller to build a QMenu"
    return built[-1]


def _menu_texts(menu):
    return [a.text() for a in menu.actions() if not a.isSeparator()]


def test_show_pod_inspect_menu_builds_header_limit_and_frame_actions(app):
    ctrl = _controller(app)  # parent.images = [{"name": "A"}, {"name": "B"}]
    sample = {'pod': 0.6, 'looks': 2, 'limiting_factor': LIMIT_CANOPY, 'frames': [0, 1]}

    menu = _capture_inspect_menu(ctrl, sample)
    assert menu is not None
    texts = _menu_texts(menu)

    # Header: POD percent (0.6 -> 60) and look count.
    assert any('POD' in t and '60' in t and '2' in t for t in texts)

    # Limiting-factor line rendered via _limit_label (LIMIT_CANOPY -> "Canopy").
    label = ctrl._limit_label(LIMIT_CANOPY)
    assert any(label in t for t in texts)

    # Both frames map to valid image slots -> two "View" actions, in order.
    view_texts = [t for t in texts if t.startswith('View')]
    assert view_texts == ['View A', 'View B']


def test_show_pod_inspect_menu_caps_frame_actions_at_eight(app):
    ctrl = _controller(app)
    ctrl.parent.images = [{"name": f"img{i}"} for i in range(12)]
    sample = {'pod': 0.9, 'looks': 5, 'limiting_factor': LIMIT_CANOPY,
              'frames': list(range(12))}

    menu = _capture_inspect_menu(ctrl, sample)
    view_texts = [t for t in _menu_texts(menu) if t.startswith('View')]

    # frames[:8] -> exactly eight View actions even though 12 frames were given.
    assert len(view_texts) == 8
    assert view_texts[0] == 'View img0'
    assert view_texts[-1] == 'View img7'


def test_show_pod_inspect_menu_skips_out_of_range_frames(app):
    ctrl = _controller(app)  # only 2 images: A, B
    sample = {'pod': 0.3, 'looks': 1, 'limiting_factor': LIMIT_CANOPY,
              'frames': [0, 1, 5, 99, -3]}

    menu = _capture_inspect_menu(ctrl, sample)
    view_texts = [t for t in _menu_texts(menu) if t.startswith('View')]

    # Only indices within [0, image_count) become View actions.
    assert view_texts == ['View A', 'View B']


def _cache_with_frame_sources(ctrl, frame_sources):
    result = MagicMock()
    result.frame_sources = frame_sources
    cache = MagicMock()
    cache.has_result.return_value = True
    cache.get_result.return_value = result
    ctrl.parent.pod_result_cache = cache


def test_inspect_menu_resolves_frames_via_frame_sources(app):
    """With a full-flight result, frame ids resolve through frame_sources
    (not viewer indices): AOI frames open, source-only frames are shown but
    disabled."""
    ctrl = _controller(app)
    # Viewer has only the AOI image 'b.jpg' (at viewer index 0).
    ctrl.parent.images = [{'name': 'B', 'path': '/f/b.jpg', 'areas_of_interest': [{}]}]
    # POD ran over the full flight: a (source-only), b (AOI), c (source-only).
    _cache_with_frame_sources(ctrl, [
        {'name': 'A', 'path': '/f/a.jpg'},
        {'name': 'B', 'path': '/f/b.jpg'},
        {'name': 'C', 'path': '/f/c.jpg'},
    ])
    sample = {'pod': 0.7, 'looks': 3, 'limiting_factor': LIMIT_CANOPY, 'frames': [0, 1, 2]}

    menu = _capture_inspect_menu(ctrl, sample)
    texts = _menu_texts(menu)

    # Only the AOI frame is openable; source-only frames are shown for context.
    assert 'View B' in texts
    assert 'A (no flagged AOIs)' in texts
    assert 'C (no flagged AOIs)' in texts
    # The disabled entries are genuinely non-clickable.
    disabled = [a for a in menu.actions()
                if a.text().endswith('(no flagged AOIs)')]
    assert disabled and all(not a.isEnabled() for a in disabled)


def test_inspect_menu_aoi_frame_navigates_to_viewer_index(app):
    """Clicking an AOI frame navigates to its viewer slot resolved by path,
    not by the (full-flight) frame id."""
    ctrl = _controller(app)
    ctrl.parent.images = [
        {'name': 'X', 'path': '/f/x.jpg'},
        {'name': 'B', 'path': '/f/b.jpg'},
    ]
    ctrl.on_map_image_selected = MagicMock()
    # Frame id 2 == 'b.jpg', which is viewer index 1 (NOT 2).
    _cache_with_frame_sources(ctrl, [
        {'name': 'A', 'path': '/f/a.jpg'},
        {'name': 'C', 'path': '/f/c.jpg'},
        {'name': 'B', 'path': '/f/b.jpg'},
    ])
    sample = {'pod': 0.7, 'looks': 1, 'limiting_factor': LIMIT_CANOPY, 'frames': [2]}

    menu = _capture_inspect_menu(ctrl, sample)
    view_actions = [a for a in menu.actions() if a.text() == 'View B']
    assert len(view_actions) == 1
    view_actions[0].trigger()
    ctrl.on_map_image_selected.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# Overlay-availability refresh
# ---------------------------------------------------------------------------


def test_refresh_overlay_availability_reports_pod_and_canopy(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    cache = MagicMock()
    cache.has_result.return_value = True
    cache.is_stale.return_value = False
    ctrl.parent.pod_result_cache = cache
    ctrl._canopy_service = MagicMock(return_value=MagicMock())  # configured
    ctrl._refresh_overlay_availability()
    ctrl.map_dialog.set_overlay_availability.assert_called_once_with(True, True)


def test_refresh_overlay_availability_no_canopy_no_pod(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    cache = MagicMock()
    cache.has_result.return_value = False
    cache.is_stale.return_value = False
    ctrl.parent.pod_result_cache = cache
    ctrl._canopy_service = MagicMock(return_value=None)  # unconfigured
    ctrl._refresh_overlay_availability()
    ctrl.map_dialog.set_overlay_availability.assert_called_once_with(False, False)


def test_refresh_overlay_availability_drops_stale_pod_result(app):
    """A cached POD result computed under a different terrain/canopy config is
    invalidated (with a toast) instead of being silently re-rendered."""
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    cache = MagicMock()
    cache.is_stale.return_value = True
    cache.has_result.return_value = False   # post-invalidate state
    ctrl.parent.pod_result_cache = cache
    ctrl._canopy_service = MagicMock(return_value=None)

    ctrl._refresh_overlay_availability()

    cache.invalidate.assert_called_once()
    ctrl.parent.status_controller.show_toast.assert_called_once()
    ctrl.map_dialog.set_overlay_availability.assert_called_once_with(False, False)


def test_refresh_overlay_availability_noop_without_dialog(app):
    ctrl = _controller(app)
    ctrl.map_dialog = None
    # Must not raise when there is no dialog to gate.
    ctrl._refresh_overlay_availability()


# ---------------------------------------------------------------------------
# Canopy tile download (button handler + fetch wiring)
# ---------------------------------------------------------------------------


def test_canopy_download_blocked_offline(app):
    ctrl = _controller(app)
    ctrl._is_offline_only = lambda: True
    ctrl._run_tile_fetch = MagicMock()
    ctrl.on_canopy_download_requested()
    ctrl._run_tile_fetch.assert_not_called()
    ctrl.parent.status_controller.show_toast.assert_called_once()


def test_canopy_download_runs_fetch_then_refreshes(app):
    ctrl = _controller(app)
    ctrl._is_offline_only = lambda: False
    ctrl._run_tile_fetch = MagicMock(return_value=True)
    ctrl._refresh_overlay_availability = MagicMock()
    ctrl._canopy_svc_loaded = True
    ctrl.on_canopy_download_requested()
    ctrl._run_tile_fetch.assert_called_once()
    ctrl._refresh_overlay_availability.assert_called_once()
    # The cached canopy service is invalidated so a freshly registered source loads.
    assert ctrl._canopy_svc_loaded is False


def test_canopy_download_aborts_when_downloader_unavailable(app):
    ctrl = _controller(app)
    ctrl._is_offline_only = lambda: False
    ctrl._run_tile_fetch = MagicMock(return_value=False)
    ctrl._refresh_overlay_availability = MagicMock()
    ctrl.on_canopy_download_requested()
    ctrl._refresh_overlay_availability.assert_not_called()


def test_run_tile_fetch_seeds_mission_images(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl.parent.source_images = None
    ctrl.parent.images = [{"path": "a.jpg"}, {"path": "b.jpg"}]
    ctrl.parent.settings_service = MagicMock()
    ctrl.parent.xml_path = None  # no results path -> no output default here

    fake_instance = MagicMock()
    fake_ctor = MagicMock(return_value=fake_instance)
    target = 'core.controllers.images.viewer.exports.TileFetchController.TileFetchController'
    with patch(target, fake_ctor):
        assert ctrl._run_tile_fetch() is True

    fake_ctor.assert_called_once()
    _args, kwargs = fake_instance.run_fetch.call_args
    # The loaded mission's images are handed over so the AOI auto-fills.
    assert kwargs['mission_images'] == ctrl.parent.images


def test_run_tile_fetch_defaults_output_to_results_folder(app):
    """The download destination defaults to the results folder (dir of xml_path).

    Regression: Viewer.xml_path is a pathlib.Path, not a str, so the default was
    silently dropped by an ``isinstance(..., str)`` guard and the output folder
    came up empty. A path-like xml_path must resolve to its parent directory.
    """
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl.parent.source_images = None
    ctrl.parent.images = [{"path": "a.jpg"}]
    ctrl.parent.settings_service = MagicMock()
    ctrl.parent.xml_path = pathlib.Path("C:/results/mission1/ADIAT_Data.xml")

    fake_instance = MagicMock()
    target = 'core.controllers.images.viewer.exports.TileFetchController.TileFetchController'
    with patch(target, MagicMock(return_value=fake_instance)):
        assert ctrl._run_tile_fetch() is True

    _args, kwargs = fake_instance.run_fetch.call_args
    assert kwargs['default_output_dir'] == os.path.dirname(os.fspath(ctrl.parent.xml_path))


def test_run_tile_fetch_handles_unavailable_downloader(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    mod = 'core.controllers.images.viewer.exports.TileFetchController'
    # A None entry in sys.modules makes the in-method import raise ImportError.
    with patch.dict('sys.modules', {mod: None}):
        assert ctrl._run_tile_fetch() is False
    ctrl.parent.status_controller.show_toast.assert_called_once()


# ---------------------------------------------------------------------------
# One-time "download canopy?" prompt on map open
# ---------------------------------------------------------------------------

_QMSGBOX = 'core.controllers.images.viewer.GPSMapController.QMessageBox'


def test_prompt_skipped_when_offline(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._is_offline_only = lambda: True
    ctrl._canopy_service = lambda: None
    with patch(_QMSGBOX) as mb:
        ctrl._maybe_prompt_canopy_download()
    mb.question.assert_not_called()
    assert ctrl._canopy_prompt_shown is False  # not consumed; can ask later


def test_prompt_skipped_when_canopy_already_configured(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._is_offline_only = lambda: False
    ctrl._canopy_service = lambda: MagicMock()  # configured
    with patch(_QMSGBOX) as mb:
        ctrl._maybe_prompt_canopy_download()
    mb.question.assert_not_called()


def test_prompt_yes_triggers_download_and_is_one_time(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._is_offline_only = lambda: False
    ctrl._canopy_service = lambda: None  # unconfigured
    ctrl.on_canopy_download_requested = MagicMock()

    with patch(_QMSGBOX) as mb:
        mb.StandardButton = QMessageBox.StandardButton
        mb.question.return_value = QMessageBox.StandardButton.Yes
        ctrl._maybe_prompt_canopy_download()
    ctrl.on_canopy_download_requested.assert_called_once()
    assert ctrl._canopy_prompt_shown is True

    # Second open in the same session must not prompt again.
    ctrl.on_canopy_download_requested.reset_mock()
    with patch(_QMSGBOX) as mb2:
        ctrl._maybe_prompt_canopy_download()
    mb2.question.assert_not_called()
    ctrl.on_canopy_download_requested.assert_not_called()


def test_prompt_no_does_not_download_but_is_consumed(app):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._is_offline_only = lambda: False
    ctrl._canopy_service = lambda: None
    ctrl.on_canopy_download_requested = MagicMock()

    with patch(_QMSGBOX) as mb:
        mb.StandardButton = QMessageBox.StandardButton
        mb.question.return_value = QMessageBox.StandardButton.No
        ctrl._maybe_prompt_canopy_download()
    ctrl.on_canopy_download_requested.assert_not_called()
    assert ctrl._canopy_prompt_shown is True  # answered; won't nag again


def test_pod_calculate_delegates_to_export_controller(app):
    """The map's Calculate POD request reuses the viewer's export controller
    (same flow as Map Export) with the results-folder output dir."""
    ctrl = _controller(app)
    ctrl.parent.xml_path = pathlib.Path("C:/results/mission1/ADIAT_Data.xml")
    export = MagicMock()
    ctrl.parent.unified_map_export = export

    ctrl.on_pod_calculate_requested()

    expected = os.path.join(os.path.dirname(os.fspath(ctrl.parent.xml_path)), "coverage_pod")
    export.run_pod.assert_called_once_with(expected, show_on_map=True)


def test_pod_calculate_creates_controller_when_missing(app):
    """A viewer without a live export controller gets one created and kept."""
    ctrl = _controller(app)
    ctrl.parent.xml_path = pathlib.Path("C:/results/mission1/ADIAT_Data.xml")
    ctrl.parent.unified_map_export = None

    fake = MagicMock()
    target = ('core.controllers.images.viewer.exports.UnifiedMapExportController.'
              'UnifiedMapExportController')
    with patch(target, MagicMock(return_value=fake)):
        ctrl.on_pod_calculate_requested()

    fake.run_pod.assert_called_once()
    assert ctrl.parent.unified_map_export is fake


# ---------------------------------------------------------------------------
# Download -> POD chaining
# ---------------------------------------------------------------------------


def test_download_offers_pod_calculation_on_completion(app):
    """A completed download offers to compute POD immediately; Yes runs it."""
    from PySide6.QtWidgets import QMessageBox as _QMB

    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._tile_fetch_controller = MagicMock()
    ctrl._tile_fetch_controller.last_results = {'canopy': MagicMock()}
    cache = MagicMock()
    cache.has_result.return_value = False   # no POD yet
    ctrl.parent.pod_result_cache = cache
    ctrl.on_pod_calculate_requested = MagicMock()

    with patch(_QMSGBOX) as mb:
        mb.StandardButton = _QMB.StandardButton
        mb.question.return_value = _QMB.StandardButton.Yes
        ctrl._maybe_offer_pod_calculation()

    mb.question.assert_called_once()
    ctrl.on_pod_calculate_requested.assert_called_once()


def test_no_pod_offer_when_download_did_not_complete(app):
    """A dismissed/cancelled download (last_results None) must not prompt."""
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._tile_fetch_controller = MagicMock()
    ctrl._tile_fetch_controller.last_results = None

    with patch(_QMSGBOX) as mb:
        ctrl._maybe_offer_pod_calculation()

    mb.question.assert_not_called()


def test_no_pod_offer_when_result_already_cached(app):
    """An existing POD result suppresses the offer (nothing new to compute)."""
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._tile_fetch_controller = MagicMock()
    ctrl._tile_fetch_controller.last_results = {'dem': MagicMock()}
    cache = MagicMock()
    cache.has_result.return_value = True
    ctrl.parent.pod_result_cache = cache

    with patch(_QMSGBOX) as mb:
        ctrl._maybe_offer_pod_calculation()

    mb.question.assert_not_called()


def test_pod_offer_declined_does_not_calculate(app):
    from PySide6.QtWidgets import QMessageBox as _QMB

    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._tile_fetch_controller = MagicMock()
    ctrl._tile_fetch_controller.last_results = {'canopy': MagicMock()}
    cache = MagicMock()
    cache.has_result.return_value = False
    ctrl.parent.pod_result_cache = cache
    ctrl.on_pod_calculate_requested = MagicMock()

    with patch(_QMSGBOX) as mb:
        mb.StandardButton = _QMB.StandardButton
        mb.question.return_value = _QMB.StandardButton.No
        ctrl._maybe_offer_pod_calculation()

    ctrl.on_pod_calculate_requested.assert_not_called()


def test_prompt_body_warns_about_meta_wri_override(app):
    """The prompt must tell the user the built-in download fetches Meta/WRI and
    replaces any LANDFIRE selection (LANDFIRE stays bring-your-own)."""
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl._is_offline_only = lambda: False
    ctrl._canopy_service = lambda: None
    ctrl.on_canopy_download_requested = MagicMock()
    with patch(_QMSGBOX) as mb:
        mb.StandardButton = QMessageBox.StandardButton
        mb.question.return_value = QMessageBox.StandardButton.No
        ctrl._maybe_prompt_canopy_download()
    body = mb.question.call_args.args[2]
    assert "Meta/WRI" in body
    assert "LANDFIRE" in body


# ---------------------------------------------------------------------------
# Pre-POD local-DEM coverage confirmation
# ---------------------------------------------------------------------------

_GPS = [{'latitude': 38.70, 'longitude': -120.50},
        {'latitude': 38.72, 'longitude': -120.46}]


def _local_3dep_values(tmp_path):
    """Settings for a local-3DEP registration whose files exist on disk
    (the coverage check validates existence before probing)."""
    manifest = tmp_path / "dem_manifest.csv"
    manifest.write_text("filename,minX,minY,maxX,maxY\n")
    return {'TerrainProviderId': 'usgs_3dep_local',
            'Terrain3DEPManifestPath': str(manifest),
            'Terrain3DEPTilesDir': str(tmp_path)}


def _ctrl_with_settings(app, values):
    ctrl = _controller(app)
    ctrl.map_dialog = MagicMock()
    ctrl.gps_data = list(_GPS)
    ctrl.parent.settings_service.get_setting.side_effect = \
        lambda k, default='': values.get(k, default)
    return ctrl


def _probe_ctx(coverage):
    probe = MagicMock()
    probe.covers.return_value = coverage
    return patch("core.services.terrain.USGS3DEPProvider.USGS3DEPProvider",
                 return_value=probe), probe


def test_pod_coverage_check_passes_for_online_provider(app):
    ctrl = _ctrl_with_settings(app, {'TerrainProviderId': 'terrarium'})
    with patch("core.services.terrain.USGS3DEPProvider.USGS3DEPProvider") as MockP:
        assert ctrl._confirm_local_dem_coverage() is True
    MockP.assert_not_called()


def test_pod_coverage_check_passes_on_full_coverage(app, tmp_path):
    ctrl = _ctrl_with_settings(app, _local_3dep_values(tmp_path))
    ctx, probe = _probe_ctx('full')
    with ctx, patch(
            "core.controllers.images.viewer.GPSMapController.QMessageBox") as mb:
        assert ctrl._confirm_local_dem_coverage() is True
    probe.covers.assert_called_once()
    probe.close.assert_called_once()
    mb.assert_not_called()
    # Full coverage never consumes the one-per-session prompt.
    assert ctrl._dem_coverage_prompt_shown is False


def test_pod_coverage_partial_continue_proceeds(app, tmp_path):
    ctrl = _ctrl_with_settings(app, _local_3dep_values(tmp_path))
    ctx, _ = _probe_ctx('partial')
    with ctx, patch(
            "core.controllers.images.viewer.GPSMapController.QMessageBox") as MockBox:
        box = MockBox.return_value
        download_btn, continue_btn = MagicMock(), MagicMock()
        box.addButton.side_effect = [download_btn, continue_btn]
        box.clickedButton.return_value = continue_btn

        assert ctrl._confirm_local_dem_coverage() is True

    box.exec.assert_called_once()
    assert ctrl._dem_coverage_prompt_shown is True


def test_pod_coverage_none_download_defers(app, tmp_path):
    ctrl = _ctrl_with_settings(app, _local_3dep_values(tmp_path))
    ctrl.on_canopy_download_requested = MagicMock()
    ctx, _ = _probe_ctx('none')
    with ctx, patch(
            "core.controllers.images.viewer.GPSMapController.QMessageBox") as MockBox:
        box = MockBox.return_value
        download_btn, continue_btn = MagicMock(), MagicMock()
        box.addButton.side_effect = [download_btn, continue_btn]
        box.clickedButton.return_value = download_btn

        assert ctrl._confirm_local_dem_coverage() is False

    ctrl.on_canopy_download_requested.assert_called_once()


def test_pod_coverage_prompt_only_once_per_session(app, tmp_path):
    ctrl = _ctrl_with_settings(app, _local_3dep_values(tmp_path))
    ctrl._dem_coverage_prompt_shown = True
    with patch("core.services.terrain.USGS3DEPProvider.USGS3DEPProvider") as MockP:
        assert ctrl._confirm_local_dem_coverage() is True
    MockP.assert_not_called()


def test_pod_coverage_probe_failure_does_not_block(app, tmp_path):
    ctrl = _ctrl_with_settings(app, _local_3dep_values(tmp_path))
    with patch("core.services.terrain.USGS3DEPProvider.USGS3DEPProvider",
               side_effect=RuntimeError("pandas missing")):
        assert ctrl._confirm_local_dem_coverage() is True


def test_pod_calculate_defers_when_user_downloads_first(app):
    ctrl = _controller(app)
    ctrl._confirm_local_dem_coverage = MagicMock(return_value=False)
    ctrl.parent.unified_map_export = MagicMock()

    ctrl.on_pod_calculate_requested()

    ctrl.parent.unified_map_export.run_pod.assert_not_called()


# ---------------------------------------------------------------------------
# Canopy service staleness-on-access (Preferences changed while map open)
# ---------------------------------------------------------------------------

def test_canopy_service_rebuilds_when_settings_change(app):
    """Changing the canopy source in Preferences while the map is open must
    rebuild the cached service on next access, not keep serving the old one."""
    ctrl = _controller(app)
    old_svc = MagicMock()
    ctrl._canopy_svc = old_svc
    ctrl._canopy_svc_loaded = True
    ctrl._canopy_svc_fp = 'meta|C:/old/m.csv|C:/old/tiles'
    ctrl._canopy_overlay_cache = ('spec', 'pixmap', 'transform')

    new_svc = MagicMock()
    with patch.object(GPSMapController, '_canopy_config_fingerprint',
                      return_value='landfire|C:/new/m.csv|C:/new/tiles'), \
         patch("core.services.terrain.CanopyServiceFactory.create_canopy_service",
               return_value=new_svc):
        result = ctrl._canopy_service()

    assert result is new_svc
    old_svc.close.assert_called_once()          # old datasets released
    assert ctrl._canopy_overlay_cache is None   # stale pixels dropped
    assert ctrl._canopy_svc_fp == 'landfire|C:/new/m.csv|C:/new/tiles'


def test_canopy_service_kept_when_settings_unchanged(app):
    ctrl = _controller(app)
    svc = MagicMock()
    ctrl._canopy_svc = svc
    ctrl._canopy_svc_loaded = True
    ctrl._canopy_svc_fp = 'meta|C:/m.csv|C:/tiles'

    with patch.object(GPSMapController, '_canopy_config_fingerprint',
                      return_value='meta|C:/m.csv|C:/tiles'), \
         patch("core.services.terrain.CanopyServiceFactory.create_canopy_service") as factory:
        result = ctrl._canopy_service()

    assert result is svc
    factory.assert_not_called()


def test_canopy_service_unfingerprinted_cache_is_trusted(app):
    """A service injected without provenance (tests, tooling) is never
    invalidated by the fingerprint check."""
    ctrl = _controller(app)
    svc = MagicMock()
    ctrl._canopy_svc = svc
    ctrl._canopy_svc_loaded = True
    ctrl._canopy_svc_fp = ''

    with patch.object(GPSMapController, '_canopy_config_fingerprint',
                      return_value='meta|C:/m.csv|C:/tiles'):
        assert ctrl._canopy_service() is svc


def test_pod_coverage_check_skips_dangling_registration(app, tmp_path):
    """Registered 3DEP paths missing on disk: the factory falls back to the
    online baseline, so no 3DEP-coverage prompt is shown."""
    values = {'TerrainProviderId': 'usgs_3dep_local',
              'Terrain3DEPManifestPath': str(tmp_path / "gone" / "m.csv"),
              'Terrain3DEPTilesDir': str(tmp_path / "gone")}
    ctrl = _ctrl_with_settings(app, values)
    with patch("core.services.terrain.USGS3DEPProvider.USGS3DEPProvider") as MockP:
        assert ctrl._confirm_local_dem_coverage() is True
    MockP.assert_not_called()


# ---------------------------------------------------------------------------
# enable_pod_overlay drives the dialog controls (regression: inert controls)
# ---------------------------------------------------------------------------

def test_enable_pod_overlay_activates_dialog_controls(app):
    """After a Calculate POD run, enable_pod_overlay must drive the dialog's
    activate_pod_overlay so the button/dropdown reflect the active overlay —
    not paint the map directly while the controls stay inert."""
    ctrl = _controller(app)
    cache = MagicMock()
    cache.has_result.return_value = True
    ctrl.parent.pod_result_cache = cache
    ctrl.map_dialog = MagicMock()

    ctrl.enable_pod_overlay('pod')

    ctrl.map_dialog.activate_pod_overlay.assert_called_once_with('pod')


def test_enable_pod_overlay_noop_without_cached_result(app):
    ctrl = _controller(app)
    cache = MagicMock()
    cache.has_result.return_value = False
    ctrl.parent.pod_result_cache = cache
    ctrl.map_dialog = MagicMock()

    ctrl.enable_pod_overlay('pod')

    ctrl.map_dialog.activate_pod_overlay.assert_not_called()


def test_enable_pod_overlay_end_to_end_checks_button(app, qtbot):
    """Integration: a real dialog ends up with the POD button checked and the
    dropdown enabled after enable_pod_overlay (the reported bug, end to end)."""
    from core.views.images.viewer.dialogs.GPSMapDialog import GPSMapDialog

    ctrl = _controller(app)
    cache = MagicMock()
    cache.has_result.return_value = True
    cache.get_result.return_value = _real_result()
    ctrl.parent.pod_result_cache = cache

    dlg = GPSMapDialog(None, [], None, offline_only=True)
    qtbot.addWidget(dlg)
    dlg.map_view = MagicMock()
    dlg.map_view._pod_opacity = 0.7
    dlg.pod_display_changed.connect(ctrl.on_pod_display_changed)
    ctrl.map_dialog = dlg

    ctrl.enable_pod_overlay('pod')

    assert dlg.pod_toggle_btn.isChecked() is True
    assert dlg.pod_mode_combo.isEnabled() is True
    assert dlg.pod_mode_combo.currentData() == "pod"
    dlg.map_view.set_pod_overlay.assert_called_once()
    dlg.close()
    dlg.deleteLater()
