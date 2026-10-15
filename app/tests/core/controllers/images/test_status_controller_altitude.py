"""Status-bar altitude labelling.

Covers the viewer's review path: the altitude an operator reads while
working through images names the plane it was measured from, and shows the
DEM-derived height above the ground being flown over beside it.

The controller does no altitude reasoning of its own - it asks
``ImageService.get_altitude_readings`` and hands the result to
``FormatHelper`` - so these tests assert that delegation rather than
re-deriving the numbers.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from core.controllers.images.viewer.image.ImageLoadController import ImageLoadController
from core.controllers.images.viewer.status.StatusController import StatusController
from core.services.image.ImageService import AltitudeReadings
from helpers.FormatHelper import FormatHelper


def _run(readings, use_terrain=True):
    """Run the metadata strip and return (message, service, viewer)."""
    service = MagicMock()
    service.get_altitude_readings.return_value = readings

    viewer = MagicMock()
    viewer.messages = {}
    viewer.distance_unit = 'ft'
    viewer.use_terrain_elevation = use_terrain
    viewer.images = [{'path': 'a.jpg', 'name': 'a.jpg'}]
    viewer.current_image = 0

    ImageLoadController._update_metadata_displays(
        SimpleNamespace(parent=viewer), service)
    return viewer.messages['Relative Altitude'], service, viewer


class TestReferenceIsShown:
    def test_dji_imagery_reads_ato(self):
        message, _, _ = _run(AltitudeReadings(
            value=171.0, reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF,
            unit='ft'))
        assert message == "171.0 ft ATO"

    def test_terrain_referenced_imagery_reads_agl(self):
        """A WALDO-prepassed image really is height above the terrain."""
        message, _, _ = _run(AltitudeReadings(
            value=171.0, reference=FormatHelper.ALTITUDE_REFERENCE_TERRAIN,
            unit='ft'))
        assert message == "171.0 ft AGL"

    def test_the_label_asserts_no_reference(self):
        """The value names the plane, so the label must not contradict it."""
        controller = StatusController.__new__(StatusController)
        assert controller.tr("Altitude") == "Altitude"


class TestBothPlanes:
    """ATO is what the aircraft reported; AGL is clearance over the ground.

    Over relief they are different numbers and the searcher needs the
    second, so both are shown whenever the DEM can supply it.
    """

    def test_agl_leads_with_ato_beside_it(self):
        """AGL first: it is the figure clearance and image scale depend on."""
        message, _, _ = _run(AltitudeReadings(
            value=171.0, reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF,
            unit='ft', terrain_agl=141.2))
        assert message == "141.2 ft AGL · 171.0 ft ATO"

    def test_ato_alone_when_the_dem_cannot_answer(self):
        """No tile cached yet, or no coverage: ATO must not be relabelled."""
        message, _, _ = _run(AltitudeReadings(
            value=171.0, reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF,
            unit='ft', terrain_agl=None))
        assert message == "171.0 ft ATO"

    def test_the_terrain_preference_reaches_the_service(self):
        """Flat-terrain positioning was asked for; do not consult the DEM."""
        _message, service, _ = _run(AltitudeReadings(
            value=171.0, unit='ft'), use_terrain=False)
        assert service.get_altitude_readings.call_args.kwargs['use_terrain'] is False

    def test_the_display_read_stays_off_the_network(self):
        """Image navigation must not stall on a DEM tile fetch.

        get_altitude_readings defaults to cached-elevation-only, so the strip
        shows ATO now and gains AGL once acquisition has stocked the area.
        """
        _message, service, _ = _run(AltitudeReadings(value=171.0, unit='ft'))
        assert 'offline_only' not in service.get_altitude_readings.call_args.kwargs

    def test_the_unit_preference_is_passed_through(self):
        _message, service, _ = _run(AltitudeReadings(value=171.0, unit='ft'))
        assert service.get_altitude_readings.call_args.args[0] == 'ft'


class TestAltitudeTooltip:
    """The pair is explained where it is shown."""

    def test_the_bar_explains_both_planes(self, qtbot):
        from core.controllers.images.viewer.status.StatusController import (
            StatusController)
        from PySide6.QtWidgets import QLabel

        parent = MagicMock()
        parent.statusBar = QLabel()
        qtbot.addWidget(parent.statusBar)
        parent.messages = {'Relative Altitude': '141.2 ft AGL · 171.0 ft ATO'}
        controller = StatusController.__new__(StatusController)
        controller.parent = parent

        controller.message_listener('Relative Altitude', 'x')

        tooltip = parent.statusBar.toolTip()
        assert "AGL" in tooltip and "ATO" in tooltip
        assert "takeoff point" in tooltip

    def test_no_altitude_means_no_altitude_tooltip(self, qtbot):
        """A tip about altitudes on a bar showing none would only confuse."""
        from core.controllers.images.viewer.status.StatusController import (
            StatusController)
        from PySide6.QtWidgets import QLabel

        parent = MagicMock()
        parent.statusBar = QLabel()
        qtbot.addWidget(parent.statusBar)
        parent.messages = {'Temperature': '21 C'}
        controller = StatusController.__new__(StatusController)
        controller.parent = parent

        controller.message_listener('Temperature', 'x')

        assert parent.statusBar.toolTip() == ""


class TestNegativeAltitudePrompt:
    def test_a_negative_altitude_offers_the_override(self):
        """Unusable metadata: the operator is asked once for a real height."""
        service = MagicMock()
        service.get_altitude_readings.return_value = AltitudeReadings(
            value=-5.0, unit='ft')
        viewer = MagicMock()
        viewer.messages = {}
        viewer.distance_unit = 'ft'
        viewer.images = [{'path': 'a.jpg', 'name': 'a.jpg'}]
        viewer.current_image = 0
        # No override set yet: that is the state the prompt exists for.
        viewer.altitude_controller.custom_agl_altitude_ft = None

        ImageLoadController._update_metadata_displays(
            SimpleNamespace(parent=viewer), service)

        viewer.altitude_controller.prompt_for_custom_altitude.assert_called_once()

    def test_an_existing_override_is_not_re_prompted(self):
        service = MagicMock()
        service.get_altitude_readings.return_value = AltitudeReadings(
            value=-5.0, unit='ft')
        viewer = MagicMock()
        viewer.messages = {}
        viewer.distance_unit = 'ft'
        viewer.images = [{'path': 'a.jpg', 'name': 'a.jpg'}]
        viewer.current_image = 0
        viewer.altitude_controller.custom_agl_altitude_ft = 250.0

        ImageLoadController._update_metadata_displays(
            SimpleNamespace(parent=viewer), service)

        viewer.altitude_controller.prompt_for_custom_altitude.assert_not_called()

    def test_a_missing_altitude_prompts_nothing(self):
        """None is an absence, not a negative reading."""
        service = MagicMock()
        service.get_altitude_readings.return_value = AltitudeReadings(
            value=None, unit='ft')
        viewer = MagicMock()
        viewer.messages = {}
        viewer.distance_unit = 'ft'
        viewer.images = [{'path': 'a.jpg', 'name': 'a.jpg'}]
        viewer.current_image = 0

        ImageLoadController._update_metadata_displays(
            SimpleNamespace(parent=viewer), service)

        viewer.altitude_controller.prompt_for_custom_altitude.assert_not_called()
        assert viewer.messages['Relative Altitude'] is None


class TestWingtraAltitude:
    """Wingtra imagery carries no altitude; its geotags CSV supplies a
    terrain-referenced AGL, which the readout must show as AGL."""

    def test_the_wingtra_agl_is_handed_to_the_service(self):
        service = MagicMock()
        service.get_altitude_readings.return_value = AltitudeReadings(
            value=318.0, reference=FormatHelper.ALTITUDE_REFERENCE_TERRAIN, unit='ft')
        viewer = MagicMock()
        viewer.messages = {}
        viewer.distance_unit = 'ft'
        viewer.images = [{'path': 'w.jpg', 'name': 'w.jpg', 'wingtra_agl_ft': 318.0}]
        viewer.current_image = 0

        ImageLoadController._update_metadata_displays(
            SimpleNamespace(parent=viewer), service)

        assert service.get_altitude_readings.call_args.kwargs['terrain_agl_ft'] == 318.0
        assert viewer.messages['Relative Altitude'] == "318.0 ft AGL"

    def test_other_imagery_supplies_none(self):
        _, service, _ = _run(AltitudeReadings(
            value=171.0, reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF, unit='ft'))
        assert service.get_altitude_readings.call_args.kwargs['terrain_agl_ft'] is None
