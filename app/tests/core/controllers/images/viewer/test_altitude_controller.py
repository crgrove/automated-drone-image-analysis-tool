"""Unit tests for AltitudeController."""

import pytest
from unittest.mock import MagicMock, patch

from core.controllers.images.viewer.AltitudeController import AltitudeController


def _mock_parent(distance_unit="Feet"):
    parent = MagicMock()
    parent.settings_service.get_setting = MagicMock(
        side_effect=lambda key, default=None: distance_unit if key == "DistanceUnit" else default
    )
    return parent


@pytest.fixture
def controller():
    return AltitudeController(_mock_parent())


def test_init_starts_without_custom_altitude(controller):
    assert controller.custom_agl_altitude_ft is None


def test_get_distance_unit_feet(controller):
    controller.parent = _mock_parent(distance_unit="Feet")
    assert controller._get_distance_unit() == "ft"


def test_get_distance_unit_meters(controller):
    controller.parent = _mock_parent(distance_unit="Meters")
    assert controller._get_distance_unit() == "m"


def test_get_distance_unit_legacy_values(controller):
    controller.parent = _mock_parent(distance_unit="m")
    assert controller._get_distance_unit() == "m"

    controller.parent = _mock_parent(distance_unit="ft")
    assert controller._get_distance_unit() == "ft"


def test_get_distance_unit_falls_back_to_feet(controller):
    controller.parent = _mock_parent(distance_unit="Unknown")
    assert controller._get_distance_unit() == "ft"


def test_get_distance_unit_without_settings_service():
    parent = MagicMock(spec=[])  # no settings_service
    controller = AltitudeController(parent)
    assert controller._get_distance_unit() == "ft"


def test_convert_feet_to_feet_identity():
    parent = _mock_parent(distance_unit="Feet")
    controller = AltitudeController(parent)
    assert controller._convert_feet_to_preferred_unit(100.0) == 100.0


def test_convert_feet_to_meters():
    parent = _mock_parent(distance_unit="Meters")
    controller = AltitudeController(parent)
    # 100 ft ≈ 30.48 m
    assert controller._convert_feet_to_preferred_unit(100.0) == pytest.approx(30.48, rel=0.01)


def test_convert_meters_to_feet():
    parent = _mock_parent(distance_unit="Meters")
    controller = AltitudeController(parent)
    # 30.48 m ≈ 100 ft
    assert controller._convert_preferred_unit_to_feet(30.48) == pytest.approx(100.0, rel=0.01)


def test_convert_feet_to_preferred_unit_roundtrip():
    parent = _mock_parent(distance_unit="Meters")
    controller = AltitudeController(parent)
    feet = 250.0
    meters = controller._convert_feet_to_preferred_unit(feet)
    back_to_feet = controller._convert_preferred_unit_to_feet(meters)
    assert back_to_feet == pytest.approx(feet, rel=0.001)


def test_get_unit_label():
    parent = _mock_parent(distance_unit="Feet")
    controller = AltitudeController(parent)
    assert controller._get_unit_label() == "ft"

    parent = _mock_parent(distance_unit="Meters")
    controller = AltitudeController(parent)
    assert controller._get_unit_label() == "m"


def test_get_unit_name():
    parent = _mock_parent(distance_unit="Feet")
    controller = AltitudeController(parent)
    assert "feet" in controller._get_unit_name().lower()


def test_get_unit_name_meters():
    parent = _mock_parent(distance_unit="Meters")
    controller = AltitudeController(parent)
    assert "meters" in controller._get_unit_name().lower() or "meter" in controller._get_unit_name().lower()


def test_get_effective_altitude_none_when_unset(controller):
    assert controller.get_effective_altitude() is None


def test_get_effective_altitude_none_when_negative(controller):
    controller.custom_agl_altitude_ft = -1
    assert controller.get_effective_altitude() is None


def test_get_effective_altitude_returns_positive(controller):
    controller.custom_agl_altitude_ft = 150.0
    assert controller.get_effective_altitude() == 150.0


def test_set_custom_altitude_stores_value(controller):
    controller.set_custom_altitude(200.0)
    assert controller.custom_agl_altitude_ft == 200.0


def test_clear_custom_altitude_resets(controller):
    controller.custom_agl_altitude_ft = 150.0
    controller.clear_custom_altitude()
    assert controller.custom_agl_altitude_ft is None


def test_prompt_accepted_sets_altitude_in_feet():
    parent = _mock_parent(distance_unit="Feet")
    parent.current_image = "img1"
    parent.image_load_controller = MagicMock()
    parent.status_controller = MagicMock()
    controller = AltitudeController(parent)

    with patch(
        "core.controllers.images.viewer.AltitudeController.QInputDialog.getDouble",
        return_value=(120.0, True),
    ):
        controller.manual_altitude_override()

    assert controller.custom_agl_altitude_ft == 120.0
    parent.image_load_controller.load_image.assert_called_once()
    parent.status_controller.show_toast.assert_called_once()


def test_prompt_accepted_in_meters_converts_to_feet():
    parent = _mock_parent(distance_unit="Meters")
    parent.current_image = "img1"
    parent.image_load_controller = MagicMock()
    parent.status_controller = MagicMock()
    controller = AltitudeController(parent)

    with patch(
        "core.controllers.images.viewer.AltitudeController.QInputDialog.getDouble",
        return_value=(30.48, True),
    ):
        controller.manual_altitude_override()

    # 30.48m -> 100 ft internally
    assert controller.custom_agl_altitude_ft == pytest.approx(100.0, rel=0.01)


def test_prompt_cancelled_auto_triggered_sets_skip_flag():
    parent = _mock_parent(distance_unit="Feet")
    controller = AltitudeController(parent)

    with patch(
        "core.controllers.images.viewer.AltitudeController.QInputDialog.getDouble",
        return_value=(0.0, False),
    ):
        controller.prompt_for_custom_altitude(auto_triggered=True)

    assert controller.custom_agl_altitude_ft == -1


def test_prompt_cancelled_manual_leaves_altitude_alone():
    parent = _mock_parent(distance_unit="Feet")
    controller = AltitudeController(parent)
    controller.custom_agl_altitude_ft = None

    with patch(
        "core.controllers.images.viewer.AltitudeController.QInputDialog.getDouble",
        return_value=(0.0, False),
    ):
        controller.manual_altitude_override()

    assert controller.custom_agl_altitude_ft is None


def test_manual_override_uses_current_altitude_as_default():
    parent = _mock_parent(distance_unit="Feet")
    controller = AltitudeController(parent)
    controller.custom_agl_altitude_ft = 250.0

    with patch(
        "core.controllers.images.viewer.AltitudeController.QInputDialog.getDouble",
        return_value=(0.0, False),
    ) as mock_dialog:
        controller.manual_altitude_override()

    # Verify dialog was called with the current altitude as default
    call_kwargs = mock_dialog.call_args
    # Positional args: (parent, title, message, default, min, max, decimals)
    default_value = call_kwargs[0][3]
    assert default_value == 250.0
