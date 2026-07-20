"""Unit tests for ThermalDataController."""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from core.controllers.images.viewer.ThermalDataController import ThermalDataController


@pytest.fixture
def controller():
    return ThermalDataController(MagicMock())


def test_init_has_no_data(controller):
    assert controller.temperature_data is None


def test_load_thermal_data_from_xmp(controller):
    image_service = MagicMock()
    mock_data = np.ones((10, 10), dtype=np.float32) * 25.0
    image_service.get_thermal_data.return_value = mock_data

    result = controller.load_thermal_data(image_service, "/path/to/image.jpg", "C")

    assert result is mock_data
    assert controller.temperature_data is mock_data
    image_service.get_thermal_data.assert_called_once_with("C")


def test_load_thermal_data_falls_back_to_parser():
    controller = ThermalDataController(MagicMock())
    image_service = MagicMock()
    image_service.get_thermal_data.return_value = None

    mock_c = np.ones((10, 10), dtype=np.float32) * 25.0

    with patch(
        "core.controllers.images.viewer.ThermalDataController.ThermalParserService"
    ) as MockParser:
        MockParser.return_value.parse_file.return_value = (mock_c, None)
        result = controller.load_thermal_data(image_service, "/path/to/image.jpg", "C")

    assert result is not None
    assert np.array_equal(result, mock_c)


def test_load_thermal_data_converts_to_fahrenheit():
    controller = ThermalDataController(MagicMock())
    image_service = MagicMock()
    image_service.get_thermal_data.return_value = None

    mock_c = np.ones((5, 5), dtype=np.float32) * 100.0  # 100 C

    with patch(
        "core.controllers.images.viewer.ThermalDataController.ThermalParserService"
    ) as MockParser:
        MockParser.return_value.parse_file.return_value = (mock_c, None)
        result = controller.load_thermal_data(image_service, "/path/to/image.jpg", "F")

    # 100°C = 212°F
    assert result[0][0] == pytest.approx(212.0)


def test_load_thermal_data_returns_none_for_non_jpeg():
    controller = ThermalDataController(MagicMock())
    image_service = MagicMock()
    image_service.get_thermal_data.return_value = None

    result = controller.load_thermal_data(image_service, "/path/to/image.png", "C")

    assert result is None


def test_load_thermal_data_handles_parser_exception(controller):
    image_service = MagicMock()
    image_service.get_thermal_data.return_value = None

    with patch(
        "core.controllers.images.viewer.ThermalDataController.ThermalParserService"
    ) as MockParser:
        MockParser.return_value.parse_file.side_effect = RuntimeError("parse fail")
        result = controller.load_thermal_data(image_service, "/path/image.jpg", "C")

    assert result is None


def test_get_temperature_at_point_no_data_returns_none(controller):
    assert controller.get_temperature_at_point(5, 5) is None


def test_get_temperature_at_point_negative_coords_returns_none(controller):
    controller.temperature_data = np.ones((10, 10), dtype=np.float32)
    assert controller.get_temperature_at_point(-1, 5) is None
    assert controller.get_temperature_at_point(5, -1) is None


def test_get_temperature_at_point_out_of_bounds_returns_none(controller):
    controller.temperature_data = np.ones((10, 10), dtype=np.float32)
    assert controller.get_temperature_at_point(100, 5) is None
    assert controller.get_temperature_at_point(5, 100) is None


def test_get_temperature_at_point_returns_value(controller):
    data = np.arange(100, dtype=np.float32).reshape(10, 10)
    controller.temperature_data = data
    # Note: (x=3, y=2) -> data[2][3] -> 23
    assert controller.get_temperature_at_point(3, 2) == 23.0


def test_clear_temperature_data(controller):
    controller.temperature_data = np.ones((10, 10), dtype=np.float32)
    controller.clear_temperature_data()
    assert controller.temperature_data is None


# ---------------------------------------------------------------------------
# convert_temperature static method
# ---------------------------------------------------------------------------

def test_convert_temperature_identity():
    assert ThermalDataController.convert_temperature(25.0, "C", "C") == 25.0
    assert ThermalDataController.convert_temperature(25.0, "F", "F") == 25.0


def test_convert_temperature_c_to_f():
    assert ThermalDataController.convert_temperature(0.0, "C", "F") == pytest.approx(32.0)
    assert ThermalDataController.convert_temperature(100.0, "C", "F") == pytest.approx(212.0)
    assert ThermalDataController.convert_temperature(-40.0, "C", "F") == pytest.approx(-40.0)


def test_convert_temperature_f_to_c():
    assert ThermalDataController.convert_temperature(32.0, "F", "C") == pytest.approx(0.0)
    assert ThermalDataController.convert_temperature(212.0, "F", "C") == pytest.approx(100.0)
    assert ThermalDataController.convert_temperature(-40.0, "F", "C") == pytest.approx(-40.0)


def test_convert_temperature_unknown_units_returns_value():
    assert ThermalDataController.convert_temperature(50.0, "K", "C") == 50.0
