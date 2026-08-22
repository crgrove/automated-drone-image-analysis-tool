"""Unit tests for GalleryController — focused on pure business logic."""

import pytest
from unittest.mock import MagicMock, patch


def _mock_parent():
    parent = MagicMock()
    parent.images = []
    parent.alternative_cache_dir = None
    parent.xml_path = None
    parent.gallery_mode = False
    return parent


@pytest.fixture
def controller():
    """GalleryController with UI and model mocked to avoid Qt side-effects."""
    with patch(
        "core.controllers.images.viewer.gallery.GalleryController.GalleryUIComponent"
    ), patch(
        "core.controllers.images.viewer.gallery.GalleryController.AOIGalleryModel"
    ):
        from core.controllers.images.viewer.gallery.GalleryController import GalleryController
        return GalleryController(_mock_parent())


def _aoi(center=(50, 50), area=100, **extra):
    a = {"center": center, "radius": 10, "area": area}
    a.update(extra)
    return a


# ---------------------------------------------------------------------------
# _calculate_hue_distance
# ---------------------------------------------------------------------------

def test_hue_distance_same(controller):
    assert controller._calculate_hue_distance(45, 45) == 0


def test_hue_distance_wraparound(controller):
    assert controller._calculate_hue_distance(350, 10) == 20


def test_hue_distance_max(controller):
    assert controller._calculate_hue_distance(0, 180) == 180


# ---------------------------------------------------------------------------
# _collect_all_aois
# ---------------------------------------------------------------------------

def test_collect_aois_empty_list(controller):
    controller.parent.images = []
    assert controller._collect_all_aois() == []


def test_collect_aois_flattens_across_images(controller):
    controller.parent.images = [
        {"areas_of_interest": [_aoi(), _aoi()]},
        {"areas_of_interest": [_aoi()]},
    ]
    result = controller._collect_all_aois()
    assert len(result) == 3
    # Tuples: (img_idx, aoi_idx, aoi_data)
    assert result[0][0] == 0 and result[0][1] == 0
    assert result[1][0] == 0 and result[1][1] == 1
    assert result[2][0] == 1 and result[2][1] == 0


def test_collect_aois_skips_images_without_aois(controller):
    controller.parent.images = [
        {"areas_of_interest": []},
        {"areas_of_interest": [_aoi()]},
        {},  # no 'areas_of_interest' key
    ]
    result = controller._collect_all_aois()
    assert len(result) == 1


# ---------------------------------------------------------------------------
# _sort_aois_global
# ---------------------------------------------------------------------------

def test_sort_global_none_returns_input(controller):
    items = [(0, 0, _aoi(area=30)), (0, 1, _aoi(area=10))]
    controller.sort_method = None
    result = controller._sort_aois_global(items)
    assert result == items


def test_sort_global_by_area_asc(controller):
    items = [
        (0, 0, _aoi(area=30)),
        (0, 1, _aoi(area=10)),
        (1, 0, _aoi(area=20)),
    ]
    controller.sort_method = "area_asc"
    result = controller._sort_aois_global(items)
    assert [a["area"] for _, _, a in result] == [10, 20, 30]


def test_sort_global_by_area_desc(controller):
    items = [(0, 0, _aoi(area=1)), (0, 1, _aoi(area=100)), (1, 0, _aoi(area=50))]
    controller.sort_method = "area_desc"
    result = controller._sort_aois_global(items)
    assert [a["area"] for _, _, a in result] == [100, 50, 1]


def test_sort_global_by_confidence_desc(controller):
    items = [
        (0, 0, _aoi(confidence=0.5)),
        (0, 1, _aoi(confidence=0.9)),
        (1, 0, _aoi()),
    ]
    controller.sort_method = "confidence_desc"
    result = controller._sort_aois_global(items)
    assert result[0][2]["confidence"] == 0.9


def test_sort_global_by_x(controller):
    items = [
        (0, 0, _aoi(center=(50, 0))),
        (0, 1, _aoi(center=(10, 0))),
    ]
    controller.sort_method = "x"
    result = controller._sort_aois_global(items)
    assert result[0][2]["center"][0] == 10


def test_sort_global_by_y(controller):
    items = [
        (0, 0, _aoi(center=(0, 50))),
        (0, 1, _aoi(center=(0, 10))),
    ]
    controller.sort_method = "y"
    result = controller._sort_aois_global(items)
    assert result[0][2]["center"][1] == 10


# ---------------------------------------------------------------------------
# _filter_aois_global
# ---------------------------------------------------------------------------

def test_filter_global_no_filters_returns_all(controller):
    items = [(0, 0, _aoi()), (0, 1, _aoi())]
    result = controller._filter_aois_global(items)
    assert len(result) == 2


def test_filter_global_flagged_only(controller):
    items = [
        (0, 0, _aoi(flagged=True)),
        (0, 1, _aoi(flagged=False)),
        (0, 2, _aoi()),  # no flagged key
    ]
    controller.filter_flagged_only = True
    result = controller._filter_aois_global(items)
    assert len(result) == 1


def test_filter_global_by_area_min_max(controller):
    items = [
        (0, 0, _aoi(area=5)),
        (0, 1, _aoi(area=50)),
        (0, 2, _aoi(area=500)),
    ]
    controller.filter_area_min = 10
    controller.filter_area_max = 100
    result = controller._filter_aois_global(items)
    assert len(result) == 1
    assert result[0][2]["area"] == 50


def test_filter_global_by_comment(controller):
    items = [
        (0, 0, _aoi(user_comment="red thing")),
        (0, 1, _aoi(user_comment="")),
        (0, 2, _aoi(user_comment="nothing here")),
    ]
    controller.filter_comment_pattern = "red"
    result = controller._filter_aois_global(items)
    assert len(result) == 1


def test_filter_global_by_temperature_range(controller):
    # Gallery's filter calls _get_aoi_temperature(img_idx, aoi_idx) which
    # reads from a cache rather than the AOI dict directly.
    items = [
        (0, 0, _aoi(temperature=20.0)),
        (0, 1, _aoi(temperature=50.0)),
        (0, 2, _aoi()),
    ]
    controller.filter_temperature_min = 10.0
    controller.filter_temperature_max = 30.0

    def fake_temp(img_idx, aoi_idx):
        return {(0, 0): 20.0, (0, 1): 50.0, (0, 2): None}[(img_idx, aoi_idx)]

    with patch.object(controller, "_get_aoi_temperature", side_effect=fake_temp):
        result = controller._filter_aois_global(items)
    assert len(result) == 1
    # Original AOI dict still has temperature=20.0
    assert result[0][2].get("temperature") == 20.0


# ---------------------------------------------------------------------------
# set_sort_method / set_filters
# ---------------------------------------------------------------------------

def test_set_sort_method(controller):
    controller.refresh_gallery = MagicMock()
    controller.set_sort_method("area_desc")
    assert controller.sort_method == "area_desc"


def test_set_sort_method_with_hue(controller):
    controller.refresh_gallery = MagicMock()
    controller.set_sort_method("color", color_hue=120)
    assert controller.sort_method == "color"
    assert controller.sort_color_hue == 120


def test_set_filters_updates_state(controller):
    controller.refresh_gallery = MagicMock()
    controller.set_filters({
        "flagged_only": True,
        "color_hue": 90,
        "color_range": 20,
        "color_mode": "include",
        "area_min": 10,
        "area_max": 1000,
        "comment_pattern": "foo",
        "temperature_min": 5.0,
        "temperature_max": 50.0,
        "heatmap_mode": "display",
        "heatmap_threshold": 85,
    })
    assert controller.filter_flagged_only is True
    assert controller.filter_area_min == 10
    assert controller.filter_temperature_min == 5.0
    assert controller.filter_heatmap_mode == "display"


# ---------------------------------------------------------------------------
# Gallery column width computations
# ---------------------------------------------------------------------------

def test_gallery_column_width_constants(controller):
    assert controller.GALLERY_COLUMN_WIDTH == 200
    assert controller.GALLERY_OVERHEAD == 35


# ---------------------------------------------------------------------------
# clear_gallery / clear_cache
# ---------------------------------------------------------------------------

def test_clear_cache_clears_aoi_cache(controller):
    controller._aoi_service_cache = {0: MagicMock(), 1: MagicMock()}
    controller.clear_cache()
    assert controller._aoi_service_cache == {}


# ---------------------------------------------------------------------------
# go_to_aoi
# ---------------------------------------------------------------------------

def test_go_to_aoi_found(controller):
    controller.model.aoi_to_row = {(0, 0): 5, (1, 2): 9}
    controller.load_all_aois = MagicMock()
    controller._select_and_activate_aoi = MagicMock()

    assert controller.go_to_aoi(1, 2) is True
    controller._select_and_activate_aoi.assert_called_once_with(9)
    controller.load_all_aois.assert_not_called()


def test_go_to_aoi_not_in_gallery(controller):
    controller.model.aoi_to_row = {(0, 0): 5}
    controller.load_all_aois = MagicMock()
    controller._select_and_activate_aoi = MagicMock()

    assert controller.go_to_aoi(3, 3) is False
    controller._select_and_activate_aoi.assert_not_called()


def test_go_to_aoi_rebuilds_stale_model(controller):
    """A stale gallery model is rebuilt once before the AOI is reported missing."""
    controller.model.aoi_to_row = {}

    def populate():
        controller.model.aoi_to_row = {(2, 1): 7}
    controller.load_all_aois = MagicMock(side_effect=populate)
    controller._select_and_activate_aoi = MagicMock()

    assert controller.go_to_aoi(2, 1) is True
    controller.load_all_aois.assert_called_once()
    controller._select_and_activate_aoi.assert_called_once_with(7)


# ---------------------------------------------------------------------------
# on_splitter_moved — the handler wired to QSplitter.splitterMoved. It is the
# only resize path the signal reaches, so it must keep the AOI header aligned
# with the AOI pane (regression: header stayed put when the gallery was
# resized because the sync lived only on the unused Viewer._on_splitter_moved).
# ---------------------------------------------------------------------------

def _splitter(sizes):
    splitter = MagicMock()
    splitter.sizes.return_value = list(sizes)
    splitter.handleWidth.return_value = 4
    return splitter


def test_on_splitter_moved_syncs_header_in_gallery_mode(controller):
    controller.parent.gallery_mode = True
    controller.update_gallery_geometry = MagicMock()
    controller.save_splitter_position = MagicMock()

    controller.on_splitter_moved(0, 1, _splitter([1400, 435]), MagicMock())

    controller.parent._sync_aoi_header_width.assert_called_once()


def test_on_splitter_moved_syncs_header_in_single_image_mode(controller):
    controller.parent.gallery_mode = False
    controller.set_splitter_to_single_column = MagicMock()

    controller.on_splitter_moved(0, 1, _splitter([1600, 250]), MagicMock())

    controller.parent._sync_aoi_header_width.assert_called_once()


# ---------------------------------------------------------------------------
# color-calc signal lifecycle — regression: opening the gallery logged Qt
# RuntimeWarnings because _disconnect_color_calc_signals tried to disconnect
# slots that were never connected (color_calc_progress/message, and complete on
# the first open). Only disconnect what we actually connected.
# ---------------------------------------------------------------------------

def test_disconnect_color_calc_skips_when_not_connected(controller):
    controller._color_calc_complete_connected = False
    controller.color_calc_progress_dialog = None

    controller._disconnect_color_calc_signals()

    controller.model.color_calc_complete.disconnect.assert_not_called()


def test_disconnect_color_calc_disconnects_complete_and_clears_flag(controller):
    controller._color_calc_complete_connected = True
    controller.color_calc_progress_dialog = None

    controller._disconnect_color_calc_signals()

    controller.model.color_calc_complete.disconnect.assert_called_once()
    assert controller._color_calc_complete_connected is False
    # The overlay-only signals are never wired here, so must never be disconnected
    controller.model.color_calc_progress.disconnect.assert_not_called()
    controller.model.color_calc_message.disconnect.assert_not_called()


def test_start_color_calc_connects_complete_and_sets_flag(controller):
    controller._color_calc_complete_connected = False
    controller.color_calc_progress_dialog = None
    controller._finalize_gallery_load = MagicMock()

    controller._start_color_calculation_with_progress([])

    controller.model.color_calc_complete.connect.assert_called_once_with(
        controller._on_color_calc_complete
    )
    assert controller._color_calc_complete_connected is True


# ---------------------------------------------------------------------------
# on_aoi_clicked must sync the single-image AOI selection (GPS-map marker,
# on-image overlay). Field report: selecting AOIs in the gallery never
# showed the marker in the map window.
# ---------------------------------------------------------------------------

def test_gallery_click_syncs_aoi_controller_selection(controller):
    parent = controller.parent
    parent.current_image = 3  # same image: no load path needed
    parent.aoi_controller.aoi_index_to_visible_index = {2: 1}
    controller._zoom_to_aoi = MagicMock()

    controller.on_aoi_clicked(3, 2, _aoi())

    parent.aoi_controller.select_aoi.assert_called_once_with(2, 1)
    controller._zoom_to_aoi.assert_called_once()


def test_gallery_click_syncs_selection_with_unmapped_visible_index(controller):
    parent = controller.parent
    parent.current_image = 0
    parent.aoi_controller.aoi_index_to_visible_index = {}
    controller._zoom_to_aoi = MagicMock()

    controller.on_aoi_clicked(0, 5, _aoi())

    parent.aoi_controller.select_aoi.assert_called_once_with(5, -1)


# ---------------------------------------------------------------------------
# Event-driven zoom-after-load: a cross-image gallery click navigates via
# parent.load_image_with_zoom and the load pipeline applies the zoom as its
# final step. No transient viewChanged handlers, no settle-window timers
# (field report lineage: first click landed un-zoomed).
# ---------------------------------------------------------------------------

def test_needs_load_click_zooms_via_the_load_pipeline(controller, wire_pending_zoom):
    parent = controller.parent
    parent.current_image = 0
    parent.aoi_controller.aoi_index_to_visible_index = {}
    wire_pending_zoom(parent, loaded_idx=1)  # pipeline consumes for image 1
    controller._zoom_to_aoi = MagicMock()
    aoi = _aoi()

    controller.on_aoi_clicked(1, 0, aoi)

    controller._zoom_to_aoi.assert_called_once_with(aoi)
    assert parent._pending_view_zoom is None  # consumed, nothing armed


def test_failed_load_leaves_no_zoom_request_armed(controller, wire_pending_zoom):
    parent = controller.parent
    parent.current_image = 0
    parent.aoi_controller.aoi_index_to_visible_index = {}
    wire_pending_zoom(parent, loaded_idx=None)  # load never consumes
    controller._zoom_to_aoi = MagicMock()

    controller.on_aoi_clicked(1, 0, _aoi())

    controller._zoom_to_aoi.assert_not_called()
    # load_image_with_zoom dropped its own unconsumed request, so a later,
    # unrelated load can never fire a stale zoom.
    assert parent._pending_view_zoom is None


def test_request_for_a_different_image_is_dropped_not_applied(controller, wire_pending_zoom):
    parent = controller.parent
    parent.current_image = 0
    parent.aoi_controller.aoi_index_to_visible_index = {}
    # Pipeline ends up loading image 5, not the requested image 1 (e.g. a
    # reentrant navigation during the load).
    wire_pending_zoom(parent, loaded_idx=5)
    controller._zoom_to_aoi = MagicMock()

    controller.on_aoi_clicked(1, 0, _aoi())

    controller._zoom_to_aoi.assert_not_called()
    assert parent._pending_view_zoom is None  # dropped as stale, not left armed


# ---------------------------------------------------------------------------
# _zoom_to_aoi with the Show Overlay toggle OFF.
#
# Field report lineage: a user whose overlay toggle was off got no zoom from
# any gallery AOI click, while the same build zoomed correctly for everyone
# who left the toggle on (its default). The handler takes the new state as an
# argument and was being called without one; the resulting TypeError was
# swallowed by _zoom_to_aoi's own except, which sat ABOVE the zoom call.
#
# A bare MagicMock parent accepts any call signature, so these tests give
# _show_overlay_change the real one - that permissiveness is what let the
# original bug through the suite.
# ---------------------------------------------------------------------------

def _overlay_off_parent(controller, handler):
    """Wire the controller's parent for 'overlay toggle currently off'."""
    parent = controller.parent
    parent.showOverlayToggle.isChecked.return_value = False
    parent._show_overlay_change = handler
    return parent


def test_zoom_happens_when_overlay_toggle_is_off(controller):
    seen = []

    def _show_overlay_change(state):  # the real signature: state is required
        seen.append(state)

    parent = _overlay_off_parent(controller, _show_overlay_change)

    controller._zoom_to_aoi(_aoi(center=(50, 50)))

    parent.main_image.zoomToArea.assert_called_once_with((50, 50), 6)
    # The toggle was switched on and the handler told the new state.
    parent.showOverlayToggle.setChecked.assert_called_once_with(True)
    assert seen == [True]


def test_zoom_survives_a_failing_overlay_handler(controller):
    """Overlay work is decoration; it must not be able to cancel the zoom."""
    def _show_overlay_change(state):
        raise RuntimeError("overlay update blew up")

    parent = _overlay_off_parent(controller, _show_overlay_change)

    controller._zoom_to_aoi(_aoi(center=(12, 34)))

    parent.main_image.zoomToArea.assert_called_once_with((12, 34), 6)


def test_badge_survives_a_failing_overlay_handler(controller):
    """The AOI number badge and ruler are separate from the compass overlay.

    They shared one try/except, so a failure enabling the compass overlay
    silently cost the badge as well.
    """
    def _show_overlay_change(state):
        raise RuntimeError("overlay update blew up")

    parent = _overlay_off_parent(controller, _show_overlay_change)
    aoi = _aoi(center=(9, 9))

    controller._zoom_to_aoi(aoi)

    parent.aoi_overlay_controller.show_for_aoi.assert_called_once_with(aoi)


def test_overlay_handler_untouched_when_toggle_already_on(controller):
    parent = controller.parent
    parent.showOverlayToggle.isChecked.return_value = True
    parent._show_overlay_change = MagicMock()

    controller._zoom_to_aoi(_aoi(center=(7, 8)))

    parent.main_image.zoomToArea.assert_called_once_with((7, 8), 6)
    parent._show_overlay_change.assert_not_called()
    parent.showOverlayToggle.setChecked.assert_not_called()
