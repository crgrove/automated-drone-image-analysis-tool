import pytest
import json
from unittest.mock import patch, mock_open
from app.core.services.ConfigService import ConfigService  # Adjust the import according to your project structure


def test_config_service_initialization():
    mock_config_data = {
        "algorithms": [
            {"name": "Algorithm1", "params": {"param1": "value1"}},
            {"name": "Algorithm2", "params": {"param1": "value2"}}
        ]
    }

    mock_path = "/path/to/config.json"

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_config_data))):
        config_service = ConfigService(mock_path)
        assert config_service.config == mock_config_data


def test_get_algorithms():
    mock_config_data = {
        "algorithms": [
            {"name": "Algorithm1", "params": {"param1": "value1"}},
            {"name": "Algorithm2", "params": {"param1": "value2"}}
        ]
    }

    mock_path = "/path/to/config.json"

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_config_data))):
        config_service = ConfigService(mock_path)
        algorithms = config_service.get_algorithms()
        assert algorithms == mock_config_data["algorithms"]
        assert len(algorithms) == 2
        assert algorithms[0]["name"] == "Algorithm1"
        assert algorithms[1]["name"] == "Algorithm2"
