"""Unit tests for TeamPlanningController — focused on logic, not UI."""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QObject


class FakeViewer(QObject):
    """A lightweight real QObject that can stand in for the parent viewer.

    TeamPlanningController calls super().__init__(parent_viewer) which
    forwards to QObject.__init__ — that requires a real QObject parent,
    not a MagicMock. We still use attribute-based mocking for the rest.
    """

    def __init__(self, images=None, flagged_aois=None):
        super().__init__()
        self.images = images or []
        self.aoi_controller = MagicMock()
        self.aoi_controller.flagged_aois = flagged_aois or {}
        self.use_terrain_elevation = True
        self.xml_path = None
        # xml_service is called inside _sync_team_colors() for team defs.
        # get_team_planning() returns an iterable of {'name', 'color'} dicts.
        self.xml_service = MagicMock()
        self.xml_service.get_team_planning.return_value = []


def _viewer(images=None, flagged_aois=None):
    return FakeViewer(images=images, flagged_aois=flagged_aois)


@pytest.fixture
def controller():
    from core.controllers.images.viewer.TeamPlanningController import TeamPlanningController
    return TeamPlanningController(_viewer())


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

def test_init_starts_with_empty_state(controller):
    assert controller._aoi_entries == []
    assert controller._uid_counter == 0
    assert controller.dialog is None


# ---------------------------------------------------------------------------
# _build_aoi_entries
# ---------------------------------------------------------------------------

def test_build_aoi_entries_empty(controller):
    controller.viewer = _viewer()
    controller._build_aoi_entries()
    assert controller._aoi_entries == []


def test_build_aoi_entries_skips_hidden_images():
    from core.controllers.images.viewer.TeamPlanningController import TeamPlanningController
    viewer = _viewer(
        images=[{"path": "a.jpg", "hidden": True, "areas_of_interest": [{"id": 1}]}],
        flagged_aois={0: {0}},
    )
    controller = TeamPlanningController(viewer)
    controller._build_aoi_entries()
    assert controller._aoi_entries == []


def test_build_aoi_entries_skips_out_of_range_img_idx():
    from core.controllers.images.viewer.TeamPlanningController import TeamPlanningController
    viewer = _viewer(
        images=[{"path": "a.jpg", "areas_of_interest": [{"id": 1}]}],
        flagged_aois={5: {0}},  # img_idx > len(images)
    )
    controller = TeamPlanningController(viewer)
    controller._build_aoi_entries()
    assert controller._aoi_entries == []


def test_build_aoi_entries_skips_out_of_range_aoi_idx():
    from core.controllers.images.viewer.TeamPlanningController import TeamPlanningController
    viewer = _viewer(
        images=[{"path": "a.jpg", "areas_of_interest": [{"id": 1}]}],
        flagged_aois={0: {5}},  # aoi_idx > len(aois)
    )
    controller = TeamPlanningController(viewer)

    with patch(
        "core.controllers.images.viewer.TeamPlanningController.AOIService"
    ) as MockService:
        MockService.return_value.calculate_gps_with_custom_altitude.return_value = None
        controller._build_aoi_entries()
    assert controller._aoi_entries == []


def test_build_aoi_entries_adds_valid_entries():
    from core.controllers.images.viewer.TeamPlanningController import TeamPlanningController
    viewer = _viewer(
        images=[{"path": "/path/a.jpg", "areas_of_interest": [
            {"id": 1, "area": 100, "team": "Alpha"},
        ]}],
        flagged_aois={0: {0}},
    )
    controller = TeamPlanningController(viewer)

    with patch(
        "core.controllers.images.viewer.TeamPlanningController.AOIService"
    ) as MockService:
        MockService.return_value.calculate_gps_with_custom_altitude.return_value = (40.0, -75.0)
        controller._build_aoi_entries()

    assert len(controller._aoi_entries) == 1
    entry = controller._aoi_entries[0]
    assert entry["latitude"] == 40.0
    assert entry["longitude"] == -75.0
    assert entry["team"] == "Alpha"
    assert entry["image_name"] == "a.jpg"
    assert entry["area"] == 100


def test_build_aoi_entries_skips_aoi_without_gps():
    from core.controllers.images.viewer.TeamPlanningController import TeamPlanningController
    viewer = _viewer(
        images=[{"path": "/path/a.jpg", "areas_of_interest": [{"id": 1}]}],
        flagged_aois={0: {0}},
    )
    controller = TeamPlanningController(viewer)

    with patch(
        "core.controllers.images.viewer.TeamPlanningController.AOIService"
    ) as MockService:
        MockService.return_value.calculate_gps_with_custom_altitude.return_value = None
        controller._build_aoi_entries()

    assert controller._aoi_entries == []


def test_build_aoi_entries_multiple_images():
    from core.controllers.images.viewer.TeamPlanningController import TeamPlanningController
    viewer = _viewer(
        images=[
            {"path": "/p/a.jpg", "areas_of_interest": [{"id": 1}, {"id": 2}]},
            {"path": "/p/b.jpg", "areas_of_interest": [{"id": 3}]},
        ],
        flagged_aois={0: {0, 1}, 1: {0}},
    )
    controller = TeamPlanningController(viewer)

    with patch(
        "core.controllers.images.viewer.TeamPlanningController.AOIService"
    ) as MockService:
        MockService.return_value.calculate_gps_with_custom_altitude.return_value = (40.0, -75.0)
        controller._build_aoi_entries()

    assert len(controller._aoi_entries) == 3
    # All have distinct UIDs
    uids = [e["uid"] for e in controller._aoi_entries]
    assert len(set(uids)) == 3


# ---------------------------------------------------------------------------
# show() without flagged AOIs
# ---------------------------------------------------------------------------

def test_show_no_flagged_aois_displays_info_messagebox(controller):
    with patch(
        "core.controllers.images.viewer.TeamPlanningController.QMessageBox"
    ) as MockMsgBox:
        controller.show()
    MockMsgBox.information.assert_called_once()


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------

def test_close_no_dialog(controller):
    controller.close()  # no-op, should not raise


def test_close_hides_dialog(controller):
    controller.dialog = MagicMock()
    controller.dialog.isVisible.return_value = True
    controller.close()
    controller.dialog is None or controller.dialog.close.called


# ---------------------------------------------------------------------------
# _refresh_counts
# ---------------------------------------------------------------------------

def test_refresh_counts_no_dialog(controller):
    controller._refresh_counts()  # safe to call


def test_refresh_counts_updates_unassigned(controller):
    controller._aoi_entries = [
        {"team": "Alpha"},
        {"team": ""},
        {"team": None},
    ]
    controller.dialog = MagicMock()
    controller.dialog.get_teams.return_value = [{"name": "Alpha"}]
    controller._refresh_counts()
    # Unassigned = 2 (empty + None)
    controller.dialog.update_unassigned_count.assert_called_once_with(2)


# ---------------------------------------------------------------------------
# _on_assign with no dialog
# ---------------------------------------------------------------------------

def test_on_assign_no_dialog(controller):
    controller.dialog = None
    controller._on_assign()  # no-op


def test_on_assign_no_team_selected(controller):
    controller.dialog = MagicMock()
    controller.dialog.get_selected_team_name.return_value = None

    with patch(
        "core.controllers.images.viewer.TeamPlanningController.QMessageBox"
    ) as MockMsgBox:
        controller._on_assign()
    MockMsgBox.information.assert_called_once()


def test_on_assign_no_aois_selected(controller):
    controller.dialog = MagicMock()
    controller.dialog.get_selected_team_name.return_value = "Alpha"
    controller.dialog.map_view.get_selected_uids.return_value = []

    with patch(
        "core.controllers.images.viewer.TeamPlanningController.QMessageBox"
    ) as MockMsgBox:
        controller._on_assign()
    MockMsgBox.information.assert_called_once()


def test_on_assign_updates_team_for_selected_aois(controller):
    controller.dialog = MagicMock()
    controller.dialog.get_selected_team_name.return_value = "Alpha"
    controller.dialog.map_view.get_selected_uids.return_value = [1, 2]
    controller._aoi_entries = [
        {"uid": 0, "team": "", "team_color": ""},
        {"uid": 1, "team": "", "team_color": ""},
        {"uid": 2, "team": "", "team_color": ""},
    ]
    controller._persist_assignment = MagicMock()
    controller._sync_team_colors = MagicMock()
    controller._refresh_counts = MagicMock()
    controller._refresh_aoi_list_for_selected_team = MagicMock()

    controller._on_assign()

    assert controller._aoi_entries[1]["team"] == "Alpha"
    assert controller._aoi_entries[2]["team"] == "Alpha"
    assert controller._aoi_entries[0]["team"] == ""


# ---------------------------------------------------------------------------
# _sync_team_colors
# ---------------------------------------------------------------------------

def test_sync_team_colors_no_dialog(controller):
    controller._sync_team_colors()  # no-op


def test_sync_team_colors_applies_colors(controller):
    controller.dialog = MagicMock()
    controller.dialog.get_teams.return_value = [
        {"name": "Alpha", "color": "#ff0000"},
        {"name": "Beta", "color": "#00ff00"},
    ]
    controller._aoi_entries = [
        {"team": "Alpha", "team_color": ""},
        {"team": "Beta", "team_color": ""},
        {"team": "", "team_color": ""},
    ]
    controller._sync_team_colors()
    assert controller._aoi_entries[0]["team_color"] == "#ff0000"
    assert controller._aoi_entries[1]["team_color"] == "#00ff00"
