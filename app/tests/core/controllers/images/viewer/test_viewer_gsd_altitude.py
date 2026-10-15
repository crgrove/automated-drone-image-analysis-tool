"""The Viewer's GSD services take their altitude from the altitude controller's
per-image answer: the operator override, else a Wingtra per-image AGL.
Wingtra imagery has no RelativeAltitude, so without that fallback the
measure tool and the person-size reference had no GSD for it."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from core.controllers.images.viewer.AltitudeController import AltitudeController
from core.controllers.images.viewer.Viewer import Viewer


def _stub(image):
    stub = SimpleNamespace(
        images=[image],
        current_image=0,
        current_image_service=MagicMock(),
        use_terrain_elevation=True,
    )
    stub.altitude_controller = AltitudeController(stub)
    return stub


def test_the_measure_tools_gsd_service_uses_a_wingtra_agl():
    stub = _stub({'name': 'W.JPG', 'wingtra_agl_ft': 318.0})

    Viewer._refresh_current_gsd_service(stub)

    stub.current_image_service.get_gsd_service.assert_called_once_with(
        custom_altitude_ft=318.0)


def test_the_per_pixel_gsd_uses_a_wingtra_agl():
    stub = _stub({'name': 'W.JPG', 'wingtra_agl_ft': 318.0})

    provider = Viewer._build_gsd_at_pixel_provider(stub)
    provider(10, 20)

    stub.current_image_service.compute_gsd_at_pixel.assert_called_once_with(
        10, 20, use_terrain=True, custom_altitude_ft=318.0)


def test_other_imagery_keeps_its_own_altitude():
    stub = _stub({'name': 'DJI_0001.JPG'})

    Viewer._refresh_current_gsd_service(stub)

    stub.current_image_service.get_gsd_service.assert_called_once_with(
        custom_altitude_ft=None)
