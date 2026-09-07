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
        ],
        "streaming_algorithms": [
            {
                "name": "ColorDetection",
                "label": "Color Detection",
                "controller": "ColorDetectionController",
                "module": "algorithms.streaming.ColorDetection.controllers.ColorDetectionController",
                "platforms": ["Windows", "Darwin", "Linux"]
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


def test_get_streaming_algorithms(sample_config_data):
    """Test retrieving the list of streaming algorithms from configuration."""
    mock_path = "/path/to/config.json"

    with patch("builtins.open", mock_open(read_data=json.dumps(sample_config_data))):
        config_service = ConfigService(mock_path)
        algorithms = config_service.get_streaming_algorithms()

        assert len(algorithms) == 1
        assert algorithms[0]["name"] == "ColorDetection"
        assert algorithms[0]["controller"] == "ColorDetectionController"


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


# ---------------------------------------------------------------------------
# resolve_image_algorithm_class
#
# The controllers used to be dispatched through module globals(), which meant
# adding an algorithm took a config entry AND an import AND a name that
# happened to match - and a config-only addition silently resolved to
# nothing. Resolution is now by dotted path, so algorithms.conf is the whole
# registry (CLAUDE.md 2.3).
# ---------------------------------------------------------------------------

def _real_algorithms():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))),
        'algorithms.conf')
    with open(config_path, encoding='utf-8') as handle:
        return json.load(handle)['algorithms']


REAL_ALGORITHMS = _real_algorithms()


def test_the_registry_was_actually_read():
    assert len(REAL_ALGORITHMS) >= 9


@pytest.mark.parametrize('algorithm', REAL_ALGORITHMS,
                         ids=lambda a: a['name'])
@pytest.mark.parametrize('key', ['controller', 'wizard_controller'])
def test_every_configured_class_resolves(algorithm, key):
    """Every entry in the shipped config must be importable by convention.

    This is the test that makes the config the registry: a new algorithm
    whose directory or class name does not match its config entry fails here
    rather than at the moment an operator selects it.
    """
    resolved = ConfigService.resolve_image_algorithm_class(algorithm, key)
    assert isinstance(resolved, type)
    assert resolved.__name__ == algorithm[key]
    assert f".{algorithm['name']}." in resolved.__module__


def test_an_explicit_module_key_overrides_the_convention():
    """The escape hatch the streaming entries already have, for an algorithm
    that cannot live at the conventional path."""
    algorithm = {
        'name': 'Nowhere',
        'controller': 'ConfigService',
        'module': 'core.services.ConfigService',
    }
    assert ConfigService.resolve_image_algorithm_class(algorithm) is ConfigService


def test_the_legacy_misspelled_name_still_resolves():
    """'AIPersonDetetor' reached shipped configs and saved results files."""
    algorithm = {
        'name': 'AIPersonDetetor',
        'controller': 'AIPersonDetectorController',
    }
    resolved = ConfigService.resolve_image_algorithm_class(algorithm)
    assert resolved.__name__ == 'AIPersonDetectorController'


def test_a_missing_field_is_reported_not_guessed():
    with pytest.raises(ValueError, match="missing required fields"):
        ConfigService.resolve_image_algorithm_class({'name': 'ColorRange'})
    with pytest.raises(ValueError, match="missing required fields"):
        ConfigService.resolve_image_algorithm_class(
            {'controller': 'ColorRangeController'})


def test_an_unresolvable_class_fails_clearly():
    """CLAUDE.md 2.3: an unknown algorithm must fail where it is named."""
    with pytest.raises(ValueError, match="Could not resolve"):
        ConfigService.resolve_image_algorithm_class(
            {'name': 'NoSuchAlgorithm', 'controller': 'NoSuchController'})


def test_a_module_that_exists_without_the_class_fails_clearly():
    with pytest.raises(ValueError, match="Could not resolve"):
        ConfigService.resolve_image_algorithm_class(
            {'name': 'Nowhere', 'controller': 'NoSuchClass',
             'module': 'core.services.ConfigService'})


def test_a_non_class_attribute_is_not_accepted():
    """getattr alone would happily return a module-level constant."""
    with pytest.raises(ValueError, match="Could not resolve"):
        ConfigService.resolve_image_algorithm_class(
            {'name': 'Nowhere', 'controller': 'ALGORITHM_NAME_ALIASES',
             'module': 'core.services.ConfigService'})
