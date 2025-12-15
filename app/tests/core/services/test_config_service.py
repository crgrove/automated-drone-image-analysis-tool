import pytest
import json
import os
from unittest.mock import patch, mock_open
from core.services.ConfigService import ConfigService


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        "algorithms": [
            {
                "name": "ColorRange",
                "label": "Color Range (RGB)",
                "controller": "ColorRangeController",
                "wizard_controller": "ColorRangeWizardController",
                "service": "ColorRangeService",
                "combine_overlapping_aois": True,
                "platforms": ["Windows", "Darwin"],
                "type": "RGB"
            },
            {
                "name": "ThermalRange",
                "label": "Temperature Range",
                "controller": "ThermalRangeController",
                "wizard_controller": "ThermalRangeWizardController",
                "service": "ThermalRangeService",
                "combine_overlapping_aois": True,
                "platforms": ["Windows"],
                "type": "Thermal"
            }
        ]
    }


def test_config_service_initialization(sample_config_data):
    """Test that ConfigService initializes correctly with valid config data."""
    mock_path = "/path/to/config.json"

    with patch("builtins.open", mock_open(read_data=json.dumps(sample_config_data))):
        config_service = ConfigService(mock_path)
        assert config_service.config == sample_config_data


def test_get_algorithms(sample_config_data):
    """Test retrieving the list of algorithms from configuration."""
    mock_path = "/path/to/config.json"

    with patch("builtins.open", mock_open(read_data=json.dumps(sample_config_data))):
        config_service = ConfigService(mock_path)
        algorithms = config_service.get_algorithms()

        assert algorithms == sample_config_data["algorithms"]
        assert len(algorithms) == 2
        assert algorithms[0]["name"] == "ColorRange"
        assert algorithms[1]["name"] == "ThermalRange"
        assert algorithms[0]["label"] == "Color Range (RGB)"
        assert algorithms[1]["label"] == "Temperature Range"


def test_get_algorithms_empty_config():
    """Test behavior with empty algorithms list."""
    empty_config = {"algorithms": []}
    mock_path = "/path/to/config.json"

    with patch("builtins.open", mock_open(read_data=json.dumps(empty_config))):
        config_service = ConfigService(mock_path)
        algorithms = config_service.get_algorithms()

        assert algorithms == []
        assert len(algorithms) == 0


def test_config_service_with_real_file_path():
    """Test ConfigService with the actual algorithms.conf file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                               'algorithms.conf')

    if os.path.exists(config_path):
        config_service = ConfigService(config_path)
        algorithms = config_service.get_algorithms()

        assert len(algorithms) > 0
        assert all("name" in alg for alg in algorithms)
        assert all("label" in alg for alg in algorithms)
        assert all("service" in alg for alg in algorithms)


def test_config_service_algorithm_structure(sample_config_data):
    """Test that algorithm entries have the expected structure."""
    mock_path = "/path/to/config.json"

    with patch("builtins.open", mock_open(read_data=json.dumps(sample_config_data))):
        config_service = ConfigService(mock_path)
        algorithms = config_service.get_algorithms()

        for algorithm in algorithms:
            assert "name" in algorithm
            assert "label" in algorithm
            assert "controller" in algorithm
            assert "wizard_controller" in algorithm
            assert "service" in algorithm
            assert "type" in algorithm
            assert algorithm["type"] in ["RGB", "Thermal"]
