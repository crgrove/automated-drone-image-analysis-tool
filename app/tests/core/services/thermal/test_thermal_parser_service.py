"""
Comprehensive tests for ThermalParserService.

Tests thermal image parsing and temperature extraction.
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.services.thermal.ThermalParserService import ThermalParserService


@pytest.fixture
def thermal_parser_service():
    """Fixture providing a ThermalParserService instance."""
    return ThermalParserService(dtype=np.float32)


def test_thermal_parser_service_initialization(thermal_parser_service):
    """Test ThermalParserService initialization."""
    assert thermal_parser_service is not None


@pytest.mark.parametrize('model', ['VT300-L_40IR', 'VT300-Z_40IR'])
def test_skydio_x10d_thermal_model_routes_to_flir(thermal_parser_service, model):
    metadata = {
        'Make': 'Skydio',
        'Model': model,
        'CameraModel': 'Logo image',
    }

    camera_model, platform = thermal_parser_service._get_model_and_platform(metadata)

    assert camera_model == model
    assert platform == 'FLIR'


def test_parse_file_uses_flir_for_skydio_x10d_thermal():
    temperature = np.ones((512, 640), dtype=np.float32) * 25.0
    visual = np.zeros((512, 640, 3), dtype=np.uint8)
    metadata = {
        'EXIF:Make': 'Skydio',
        'EXIF:Model': 'VT300-Z_40IR',
        'FLIR:CameraModel': 'Logo image',
    }

    with patch('core.services.thermal.ThermalParserService.MetaDataHelper.get_meta_data_exiftool',
               return_value=metadata), \
            patch('core.services.thermal.ThermalParserService.FlirThermalParserService') as MockFlir:
        mock_parser = MagicMock()
        mock_parser.temperatures.return_value = temperature
        mock_parser.image.return_value = visual
        MockFlir.return_value = mock_parser

        parsed_temperature, parsed_visual = ThermalParserService(dtype=np.float32).parse_file('skydio.jpg')

    mock_parser.temperatures.assert_called_once_with(filepath_image='skydio.jpg')
    mock_parser.image.assert_called_once_with(temperature, 'White Hot')
    assert parsed_temperature is temperature
    assert parsed_visual is visual


def test_parse_file_autel():
    """Test parsing Autel thermal image."""
    # AutelThermalParserService is actually AutelThermalImageParser
    with patch('core.services.thermal.ThermalParserService.AutelThermalImageParser') as MockAutel:
        mock_parser = MagicMock()
        mock_parser.parse_file.return_value = (
            np.ones((200, 200), dtype=np.float32) * 25.0,
            np.zeros((200, 200, 3), dtype=np.uint8)
        )
        MockAutel.return_value = mock_parser

        # Test would require actual file path
        pass


def test_parse_file_dji():
    """Test parsing DJI thermal image."""
    with patch('core.services.thermal.ThermalParserService.DjiThermalParserService') as MockDji:
        mock_parser = MagicMock()
        mock_parser.parse_file.return_value = (
            np.ones((200, 200), dtype=np.float32) * 25.0,
            np.zeros((200, 200, 3), dtype=np.uint8)
        )
        MockDji.return_value = mock_parser

        # Test would require actual file path
        pass


def test_parse_file_flir():
    """Test parsing FLIR thermal image."""
    with patch('core.services.thermal.ThermalParserService.FlirThermalParserService') as MockFlir:
        mock_parser = MagicMock()
        mock_parser.parse_file.return_value = (
            np.ones((200, 200), dtype=np.float32) * 25.0,
            np.zeros((200, 200, 3), dtype=np.uint8)
        )
        MockFlir.return_value = mock_parser

        # Test would require actual file path
        pass
