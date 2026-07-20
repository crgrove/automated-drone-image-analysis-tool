"""Unit tests for AOIController — focused on pure business logic."""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch


def _mock_parent(is_thermal=False, images=None):
    parent = MagicMock()
    parent.is_thermal = is_thermal
    parent.images = images or []
    parent.current_image = 0
    parent.temperature_unit = "C"
    parent.gallery_mode = False
    return parent


@pytest.fixture
def controller():
    """AOIController with UI component mocked."""
    with patch(
        "core.controllers.images.viewer.aoi.AOIController.AOIUIComponent"
    ):
        from core.controllers.images.viewer.aoi.AOIController import AOIController
        return AOIController(_mock_parent())


def _aoi(center=(50, 50), radius=10, area=100, **extra):
    a = {"center": center, "radius": radius, "area": area}
    a.update(extra)
    return a


# ---------------------------------------------------------------------------
# calculate_hue_distance
# ---------------------------------------------------------------------------

def test_hue_distance_same(controller):
    assert controller.calculate_hue_distance(90, 90) == 0


def test_hue_distance_simple(controller):
    assert controller.calculate_hue_distance(10, 30) == 20


def test_hue_distance_wraparound(controller):
    # 350° to 10° is 20° the short way
    assert controller.calculate_hue_distance(350, 10) == 20


def test_hue_distance_maximum_is_180(controller):
    assert controller.calculate_hue_distance(0, 180) == 180


# ---------------------------------------------------------------------------
# initialize_from_xml
# ---------------------------------------------------------------------------

def test_initialize_from_xml_empty(controller):
    controller.initialize_from_xml([])
    assert controller.flagged_aois == {}


def test_initialize_from_xml_reads_flags(controller):
    images = [
        {"areas_of_interest": [
            {"flagged": True, "center": (10, 10)},
            {"flagged": False, "center": (20, 20)},
        ]},
        {"areas_of_interest": [
            {"flagged": True, "center": (30, 30)},
        ]},
    ]
    controller.initialize_from_xml(images)
    assert controller.flagged_aois == {0: {0}, 1: {0}}


def test_initialize_from_xml_none_images(controller):
    controller.initialize_from_xml(None)
    assert controller.flagged_aois == {}


# ---------------------------------------------------------------------------
# find_aoi_at_position
# ---------------------------------------------------------------------------

def test_find_aoi_negative_coords(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi()]}]
    assert controller.find_aoi_at_position(-1, 5) == (-1, -1)
    assert controller.find_aoi_at_position(5, -1) == (-1, -1)


def test_find_aoi_at_center(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(center=(50, 50), radius=10)]}]
    controller.aoi_index_to_visible_index = {0: 0}
    assert controller.find_aoi_at_position(50, 50) == (0, 0)


def test_find_aoi_outside_all_radii(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(center=(10, 10), radius=5)]}]
    assert controller.find_aoi_at_position(200, 200) == (-1, -1)


def test_find_aoi_hidden_returns_visible_minus_one(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(center=(50, 50), radius=10)]}]
    # Don't map visibility: AOI is geometrically there but not in visible list
    controller.aoi_index_to_visible_index = {}
    result = controller.find_aoi_at_position(50, 50)
    assert result == (0, -1)


def test_find_aoi_no_images(controller):
    controller.parent.images = []
    # Access pattern: self.parent.images[0] would IndexError, but check happens first
    controller.parent.current_image = 0
    # Simulate no images attr path
    parent = MagicMock(spec=[])
    controller.parent = parent
    assert controller.find_aoi_at_position(10, 10) == (-1, -1)


# ---------------------------------------------------------------------------
# sort_aois_with_indices
# ---------------------------------------------------------------------------

def test_sort_none_returns_input_order(controller):
    aois = [_aoi(area=30), _aoi(area=10), _aoi(area=20)]
    controller.sort_method = None
    result = controller.sort_aois_with_indices(aois)
    assert [idx for idx, _ in result] == [0, 1, 2]


def test_sort_by_area_asc(controller):
    aois = [_aoi(area=30), _aoi(area=10), _aoi(area=20)]
    controller.sort_method = "area_asc"
    result = controller.sort_aois_with_indices(aois)
    assert [a["area"] for _, a in result] == [10, 20, 30]


def test_sort_by_area_desc(controller):
    aois = [_aoi(area=30), _aoi(area=10), _aoi(area=20)]
    controller.sort_method = "area_desc"
    result = controller.sort_aois_with_indices(aois)
    assert [a["area"] for _, a in result] == [30, 20, 10]


def test_sort_by_confidence_asc(controller):
    aois = [_aoi(confidence=0.5), _aoi(confidence=0.9), _aoi(confidence=0.1)]
    controller.sort_method = "confidence_asc"
    result = controller.sort_aois_with_indices(aois)
    assert [a["confidence"] for _, a in result] == [0.1, 0.5, 0.9]


def test_sort_by_confidence_puts_missing_first_asc(controller):
    # No confidence -> -1 -> goes first in asc order
    aois = [_aoi(confidence=0.5), _aoi()]
    controller.sort_method = "confidence_asc"
    result = controller.sort_aois_with_indices(aois)
    # Missing confidence AOI (treated as -1) goes first
    assert result[0][1].get("confidence") is None


def test_sort_by_x(controller):
    aois = [_aoi(center=(50, 0)), _aoi(center=(10, 0)), _aoi(center=(30, 0))]
    controller.sort_method = "x"
    result = controller.sort_aois_with_indices(aois)
    assert [a["center"][0] for _, a in result] == [10, 30, 50]


def test_sort_by_y(controller):
    aois = [_aoi(center=(0, 50)), _aoi(center=(0, 10)), _aoi(center=(0, 30))]
    controller.sort_method = "y"
    result = controller.sort_aois_with_indices(aois)
    assert [a["center"][1] for _, a in result] == [10, 30, 50]


def test_sort_by_temperature_asc(controller):
    aois = [_aoi(temperature=20.0), _aoi(temperature=None), _aoi(temperature=10.0)]
    controller.sort_method = "temperature_asc"
    result = controller.sort_aois_with_indices(aois)
    # None goes last
    temps = [a.get("temperature") for _, a in result]
    assert temps[0] == 10.0
    assert temps[1] == 20.0
    assert temps[2] is None


def test_sort_by_temperature_desc(controller):
    aois = [_aoi(temperature=20.0), _aoi(temperature=None), _aoi(temperature=10.0)]
    controller.sort_method = "temperature_desc"
    result = controller.sort_aois_with_indices(aois)
    temps = [a.get("temperature") for _, a in result]
    assert temps[0] == 20.0
    assert temps[-1] is None


# ---------------------------------------------------------------------------
# filter_aois_with_indices
# ---------------------------------------------------------------------------

def test_filter_flagged_only_includes_flagged(controller):
    aois = [_aoi() for _ in range(3)]
    aois_with_indices = list(enumerate(aois))
    controller.filter_flagged_only = True
    controller.flagged_aois = {0: {1}}  # only index 1 flagged

    result = controller.filter_aois_with_indices(aois_with_indices, img_idx=0)
    assert len(result) == 1
    assert result[0][0] == 1


def test_filter_no_filters_returns_all(controller):
    aois = [_aoi() for _ in range(3)]
    result = controller.filter_aois_with_indices(list(enumerate(aois)), img_idx=0)
    assert len(result) == 3


def test_filter_by_area_min(controller):
    aois = [_aoi(area=5), _aoi(area=50), _aoi(area=500)]
    controller.filter_area_min = 10
    result = controller.filter_aois_with_indices(list(enumerate(aois)), img_idx=0)
    assert [a["area"] for _, a in result] == [50, 500]


def test_filter_by_area_max(controller):
    aois = [_aoi(area=5), _aoi(area=50), _aoi(area=500)]
    controller.filter_area_max = 100
    result = controller.filter_aois_with_indices(list(enumerate(aois)), img_idx=0)
    assert [a["area"] for _, a in result] == [5, 50]


def test_filter_by_comment_substring(controller):
    aois = [
        _aoi(user_comment="something red"),
        _aoi(user_comment=""),
        _aoi(user_comment="blue thing"),
    ]
    controller.filter_comment_pattern = "red"
    result = controller.filter_aois_with_indices(list(enumerate(aois)), img_idx=0)
    assert len(result) == 1


def test_filter_comment_strips_wildcards(controller):
    aois = [_aoi(user_comment="contains crack")]
    controller.filter_comment_pattern = "*crack*"
    result = controller.filter_aois_with_indices(list(enumerate(aois)), img_idx=0)
    assert len(result) == 1


def test_filter_by_temperature_range(controller):
    aois = [
        _aoi(temperature=5.0),
        _aoi(temperature=25.0),
        _aoi(temperature=50.0),
        _aoi(),  # no temperature
    ]
    controller.filter_temperature_min = 10.0
    controller.filter_temperature_max = 40.0
    result = controller.filter_aois_with_indices(list(enumerate(aois)), img_idx=0)
    assert len(result) == 1
    assert result[0][1]["temperature"] == 25.0


# ---------------------------------------------------------------------------
# calculate_aoi_average_info
# ---------------------------------------------------------------------------

def test_calculate_aoi_average_info_thermal_celsius(controller):
    aoi = _aoi(temperature=25.0)
    info, rgb = controller.calculate_aoi_average_info(
        aoi, is_thermal=True, temperature_data=None, temperature_unit="C"
    )
    assert "25" in info and "°C" in info
    assert rgb is None


def test_calculate_aoi_average_info_thermal_fahrenheit(controller):
    aoi = _aoi(temperature=100.0)  # 100°C = 212°F
    info, rgb = controller.calculate_aoi_average_info(
        aoi, is_thermal=True, temperature_data=None, temperature_unit="F"
    )
    assert "212" in info
    assert "°F" in info


def test_calculate_aoi_average_info_thermal_no_temp(controller):
    aoi = _aoi()
    info, rgb = controller.calculate_aoi_average_info(
        aoi, is_thermal=True, temperature_data=None, temperature_unit="C"
    )
    assert "N/A" in info


def test_calculate_aoi_average_info_prefers_stored_color_info(controller):
    """Reuse the analysis-time color_info (like the gallery) instead of recomputing.

    Regression: the widget recomputed the color live, but detected_pixels are not
    persisted for large AOIs, so the live path sampled the whole circle (background
    included) and produced a hue/swatch that disagreed with the gallery.
    """
    aoi = _aoi(color_info={'rgb': (0, 85, 255), 'hex': '#0055ff', 'hue_degrees': 220.0})

    with patch.object(controller, '_get_aoi_service') as mock_get_service:
        info, rgb = controller.calculate_aoi_average_info(
            aoi, is_thermal=False, temperature_data=None, temperature_unit="C"
        )

    # Stored values are used verbatim; hue is rendered as an integer
    assert info == "Hue: 220° #0055ff"
    assert rgb == (0, 85, 255)
    # Must not trigger the live recompute when cached color_info is present
    mock_get_service.assert_not_called()


def test_calculate_aoi_average_info_falls_back_to_live_color(controller):
    """With no cached color_info, fall back to the live representative-color calc."""
    aoi = _aoi()  # no color_info (e.g. user-created AOI or legacy result file)
    mock_service = MagicMock()
    mock_service.get_aoi_representative_color.return_value = {
        'rgb': (255, 0, 101), 'hex': '#ff0065', 'hue_degrees': 336
    }

    with patch.object(controller, '_get_aoi_service', return_value=mock_service):
        info, rgb = controller.calculate_aoi_average_info(
            aoi, is_thermal=False, temperature_data=None, temperature_unit="C"
        )

    assert info == "Hue: 336° #ff0065"
    assert rgb == (255, 0, 101)
    mock_service.get_aoi_representative_color.assert_called_once_with(aoi)


# ---------------------------------------------------------------------------
# _invalidate_mask_cache
# ---------------------------------------------------------------------------

def test_invalidate_mask_cache_clears_all(controller):
    controller._mask_image_raw = "fake"
    controller._mask_cache = {(100, 100): np.zeros((100, 100))}
    controller._mask_cache_path = "/path"
    controller._invalidate_mask_cache()
    assert controller._mask_image_raw is None
    assert controller._mask_cache == {}
    assert controller._mask_cache_path is None


# ---------------------------------------------------------------------------
# set_sort_method / set_filters
# ---------------------------------------------------------------------------

def test_set_sort_method_stores_value(controller):
    controller.refresh_aoi_display = MagicMock()
    controller._update_combo_selection = MagicMock()
    controller.set_sort_method("area_asc")
    assert controller.sort_method == "area_asc"


def test_set_sort_method_with_color_hue(controller):
    controller.refresh_aoi_display = MagicMock()
    controller._update_combo_selection = MagicMock()
    controller.set_sort_method("color", color_hue=180)
    assert controller.sort_method == "color"
    assert controller.sort_color_hue == 180


def test_set_filters_updates_fields(controller):
    controller.refresh_aoi_display = MagicMock()
    # Key names match AOIController.set_filters: 'comment_filter',
    # 'color_filter_mode', 'mask_filter_path', 'mask_filter_mode'.
    filters = {
        "flagged_only": True,
        "color_hue": 90,
        "color_range": 10,
        "color_filter_mode": "include",
        "area_min": 5,
        "area_max": 100,
        "comment_filter": "red",
        "temperature_min": 10.0,
        "temperature_max": 50.0,
        "heatmap_mode": "filter",
        "heatmap_threshold": 80,
        "mask_filter_path": "/m.png",
        "mask_filter_mode": "exclude",
    }
    # parent is a MagicMock; gallery_controller.set_filters is auto-mocked
    controller.set_filters(filters)
    assert controller.filter_flagged_only is True
    assert controller.filter_color_hue == 90
    assert controller.filter_area_min == 5
    assert controller.filter_comment_pattern == "red"
    assert controller.filter_temperature_min == 10.0
    assert controller.filter_heatmap_mode == "filter"
    assert controller.filter_mask_path == "/m.png"


# ---------------------------------------------------------------------------
# toggle_aoi_flag_by_index
# ---------------------------------------------------------------------------

def test_toggle_flag_adds_flag_when_unflagged(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi()]}]
    controller.parent.current_image = 0
    controller.parent.gps_map_controller.map_dialog = None  # no dialog to update
    controller.save_flagged_aoi_to_xml = MagicMock()
    controller.flagged_aois = {}

    controller.toggle_aoi_flag_by_index(0)

    assert 0 in controller.flagged_aois.get(0, set())
    controller.save_flagged_aoi_to_xml.assert_called_once()


def test_toggle_flag_removes_existing_flag(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi()]}]
    controller.parent.current_image = 0
    controller.parent.gps_map_controller.map_dialog = None
    controller.save_flagged_aoi_to_xml = MagicMock()
    controller.flagged_aois = {0: {0}}

    controller.toggle_aoi_flag_by_index(0)

    assert 0 not in controller.flagged_aois.get(0, set())


def test_toggle_flag_ignores_invalid_index(controller):
    controller.flagged_aois = {}
    controller.save_flagged_aoi_to_xml = MagicMock()
    controller.toggle_aoi_flag_by_index(-1)
    controller.toggle_aoi_flag_by_index(None)
    controller.save_flagged_aoi_to_xml.assert_not_called()


# ---------------------------------------------------------------------------
# find_aoi_by_number / go_to_aoi_number
# ---------------------------------------------------------------------------

def test_find_aoi_by_number_found(controller):
    controller.parent.images = [
        {"areas_of_interest": [_aoi(number=1), _aoi(number=2)]},
        {"areas_of_interest": [_aoi(number=3)]},
    ]
    assert controller.find_aoi_by_number(1) == (0, 0)
    assert controller.find_aoi_by_number(2) == (0, 1)
    assert controller.find_aoi_by_number(3) == (1, 0)


def test_find_aoi_by_number_missing(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(number=1)]}]
    assert controller.find_aoi_by_number(99) is None


def test_find_aoi_by_number_no_images(controller):
    controller.parent.images = []
    assert controller.find_aoi_by_number(1) is None


def test_go_to_aoi_number_not_found(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(number=1)]}]
    assert controller.go_to_aoi_number(999) is False


def test_go_to_aoi_number_single_image_selects(controller):
    controller.parent.images = [
        {"areas_of_interest": [_aoi(number=1)]},
        {"areas_of_interest": [_aoi(number=2, center=(40, 60))]},
    ]
    controller.parent.gallery_mode = False
    controller.parent.current_image = 0
    controller.aoi_index_to_visible_index = {0: 0}
    controller.select_aoi = MagicMock()

    result = controller.go_to_aoi_number(2)

    assert result is True
    # The parent image is loaded and the AOI selected.
    assert controller.parent.current_image == 1
    controller.parent._load_image.assert_called_once()
    controller.select_aoi.assert_called_once_with(0, 0)


def test_go_to_aoi_number_single_image_filtered_out(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(number=1)]}]
    controller.parent.gallery_mode = False
    controller.parent.current_image = 0
    controller.aoi_index_to_visible_index = {}  # AOI hidden by the active filter
    controller.select_aoi = MagicMock()

    assert controller.go_to_aoi_number(1) is False
    controller.select_aoi.assert_not_called()


def test_go_to_aoi_number_gallery_delegates(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(number=5)]}]
    controller.parent.gallery_mode = True
    controller.parent.gallery_controller.go_to_aoi.return_value = True

    assert controller.go_to_aoi_number(5) is True
    controller.parent.gallery_controller.go_to_aoi.assert_called_once_with(0, 0)


def test_go_to_aoi_number_gallery_filtered_out(controller):
    controller.parent.images = [{"areas_of_interest": [_aoi(number=5)]}]
    controller.parent.gallery_mode = True
    controller.parent.gallery_controller.go_to_aoi.return_value = False

    assert controller.go_to_aoi_number(5) is False


def test_go_to_aoi_number_single_image_rebuilds_stale_map(controller):
    """A freshly created AOI is found after the stale visible-index map rebuilds."""
    controller.parent.images = [{"areas_of_interest": [_aoi(number=1)]}]
    controller.parent.gallery_mode = False
    controller.parent.current_image = 0
    controller.aoi_index_to_visible_index = {}  # stale: missing the new AOI
    controller.select_aoi = MagicMock()

    def rebuild():
        controller.aoi_index_to_visible_index = {0: 0}
    controller.ui_component.refresh_aoi_display = MagicMock(side_effect=rebuild)

    assert controller.go_to_aoi_number(1) is True
    controller.ui_component.refresh_aoi_display.assert_called_once()
    controller.select_aoi.assert_called_once_with(0, 0)


# ---------------------------------------------------------------------------
# show_aoi_context_menu — Find Similar AOIs action
# ---------------------------------------------------------------------------

def _open_context_menu(controller, aoi_index, image_idx):
    """Open the AOI context menu with QMenu mocked; returns the added action mocks.

    Shiboken methods cannot be monkeypatched on the class, so the whole QMenu
    class is replaced in the controller module and the action mocks inspected.
    """
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QPoint
    QApplication.instance() or QApplication([])

    actions = {}

    def make_action(text):
        action = MagicMock()
        actions[text] = action
        return action

    with patch("core.controllers.images.viewer.aoi.AOIController.QMenu") as menu_cls:
        menu_cls.return_value.addAction.side_effect = make_action
        controller.show_aoi_context_menu(
            QPoint(0, 0), MagicMock(), (10, 10), 100, None,
            aoi_index=aoi_index, image_idx=image_idx,
        )
    menu_cls.return_value.exec.assert_called_once()
    return actions


def test_context_menu_find_similar_triggers_controller(controller):
    actions = _open_context_menu(controller, aoi_index=0, image_idx=1)

    assert "Find Similar AOIs" in actions
    action = actions["Find Similar AOIs"]
    action.setEnabled.assert_called_once_with(True)

    triggered_handler = action.triggered.connect.call_args[0][0]
    triggered_handler()
    controller.parent.similarity_controller.find_similar_for_selected.assert_called_once_with(
        image_idx=1, aoi_idx=0)


def test_context_menu_find_similar_disabled_without_index(controller):
    actions = _open_context_menu(controller, aoi_index=None, image_idx=None)

    actions["Find Similar AOIs"].setEnabled.assert_called_once_with(False)


# ---------------------------------------------------------------------------
# Bulk flag / comment setters
# ---------------------------------------------------------------------------

def _bulk_parent():
    """Parent mock with two images, real AOI dicts, and XML elements attached."""
    import xml.etree.ElementTree as ET
    parent = _mock_parent(images=[
        {"areas_of_interest": [
            _aoi(center=(10, 10), xml=ET.Element("area_of_interest")),
            _aoi(center=(20, 20), xml=ET.Element("area_of_interest")),
        ]},
        {"areas_of_interest": [
            _aoi(center=(30, 30), xml=ET.Element("area_of_interest")),
        ]},
    ])
    parent.xml_path = "results.xml"
    parent.xml_service = MagicMock()
    parent.gallery_controller = MagicMock()
    return parent


@pytest.fixture
def bulk_controller():
    with patch("core.controllers.images.viewer.aoi.AOIController.AOIUIComponent"):
        from core.controllers.images.viewer.aoi.AOIController import AOIController
        return AOIController(_bulk_parent())


def test_set_aoi_flags_bulk_flags_and_saves_once(bulk_controller):
    applied = bulk_controller.set_aoi_flags_bulk([(0, 0), (0, 1), (1, 0), (9, 9)], True)

    assert applied == 3
    images = bulk_controller.parent.images
    assert images[0]["areas_of_interest"][0]["flagged"] is True
    assert images[0]["areas_of_interest"][1]["flagged"] is True
    assert images[1]["areas_of_interest"][0]["flagged"] is True
    assert images[0]["areas_of_interest"][0]["xml"].get("flagged") == "True"
    assert bulk_controller.flagged_aois == {0: {0, 1}, 1: {0}}
    bulk_controller.parent.xml_service.save_xml_file.assert_called_once_with("results.xml")
    bulk_controller.parent.gallery_controller.refresh_gallery.assert_called_once()
    # Current image (0) was touched -> single-image display refreshed
    bulk_controller.ui_component.refresh_aoi_display.assert_called_once()


def test_set_aoi_flags_bulk_unflag(bulk_controller):
    bulk_controller.set_aoi_flags_bulk([(0, 0), (1, 0)], True)
    bulk_controller.parent.xml_service.reset_mock()

    applied = bulk_controller.set_aoi_flags_bulk([(0, 0), (1, 0)], False)

    assert applied == 2
    images = bulk_controller.parent.images
    assert images[0]["areas_of_interest"][0]["flagged"] is False
    assert images[0]["areas_of_interest"][0]["xml"].get("flagged") == "False"
    assert bulk_controller.flagged_aois == {0: set(), 1: set()}
    bulk_controller.parent.xml_service.save_xml_file.assert_called_once()


def test_set_aoi_flags_bulk_empty_and_invalid(bulk_controller):
    assert bulk_controller.set_aoi_flags_bulk([], True) == 0
    assert bulk_controller.set_aoi_flags_bulk([(9, 9), (None, 0)], True) == 0
    bulk_controller.parent.xml_service.save_xml_file.assert_not_called()


def test_set_aoi_comments_bulk_sets_text(bulk_controller):
    applied = bulk_controller.set_aoi_comments_bulk([(0, 0), (1, 0)], "orange tarp")

    assert applied == 2
    images = bulk_controller.parent.images
    assert images[0]["areas_of_interest"][0]["user_comment"] == "orange tarp"
    assert images[1]["areas_of_interest"][0]["user_comment"] == "orange tarp"
    assert images[0]["areas_of_interest"][0]["xml"].get("user_comment") == "orange tarp"
    bulk_controller.parent.xml_service.save_xml_file.assert_called_once_with("results.xml")


def test_set_aoi_comments_bulk_empty_clears_attribute(bulk_controller):
    bulk_controller.set_aoi_comments_bulk([(0, 0)], "note")
    assert bulk_controller.parent.images[0]["areas_of_interest"][0]["xml"].get("user_comment") == "note"

    bulk_controller.set_aoi_comments_bulk([(0, 0)], "")

    aoi = bulk_controller.parent.images[0]["areas_of_interest"][0]
    assert aoi["user_comment"] == ""
    assert "user_comment" not in aoi["xml"].attrib
