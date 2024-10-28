import pytest
from unittest.mock import patch, MagicMock
from app.core.services.XmlService import XmlService


@pytest.fixture
def xml_service(testData):
    return XmlService(testData['Previous_Output'])


def test_get_settings(xml_service):
    mock_tree = MagicMock()
    mock_root = MagicMock()

    # Mocking the XML structure
    mock_tree.getroot.return_value = mock_root
    mock_settings = MagicMock()
    mock_settings.get.side_effect = lambda key: {
        'output_dir': 'output/dir',
        'input_dir': 'input/dir',
        'num_threads': '4',
        'identifier_color': '(255, 0, 0)',
        'min_area': '10',
        'hist_ref_path': 'hist/ref/path',
        'kmeans_clusters': '3',
        'algorithm': 'algorithm_name',
        'thermal': 'True',
    }.get(key, 'None')
    mock_options = MagicMock()
    mock_option = MagicMock()
    mock_option.get.side_effect = lambda key: {
        'name': 'option_name',
        'value': 'option_value',
    }.get(key)
    mock_options.__iter__.return_value = [mock_option]
    mock_settings.find.return_value = mock_options
    mock_root.find.side_effect = lambda tag: {
        'settings': mock_settings,
        'images': [MagicMock()] * 5  # Simulate 5 image elements
    }.get(tag)

    with patch('xml.etree.ElementTree.parse', return_value=mock_tree):
        settings, image_count = xml_service.getSettings()

    expected_settings = {
        'output_dir': 'output/dir',
        'input_dir': 'input/dir',
        'num_threads': 4,
        'identifier_color': (255, 0, 0),
        'min_area': 10,
        'hist_ref_path': 'hist/ref/path',
        'kmeans_clusters': 3,
        'algorithm': 'algorithm_name',
        'thermal': 'True',
        'options': {'option_name': 'option_value'}
    }
    assert settings == expected_settings
    assert image_count == 5


def test_get_images(xml_service):
    mock_tree = MagicMock()
    mock_root = MagicMock()

    # Mocking the XML structure
    mock_tree.getroot.return_value = mock_root
    mock_image = MagicMock()
    mock_image.get.side_effect = lambda key: {
        'path': 'image/path',
    }.get(key)
    mock_area_of_interest = MagicMock()
    mock_area_of_interest.get.side_effect = lambda key: {
        'area': '50.5',
        'center': '(100, 200)',
        'radius': '15',
    }.get(key)
    mock_image.__iter__.return_value = [mock_area_of_interest]
    mock_images = MagicMock()
    mock_images.__iter__.return_value = [mock_image]
    mock_root.find.return_value = mock_images

    with patch('xml.etree.ElementTree.parse', return_value=mock_tree):
        images = xml_service.getImages()

    expected_images = [{
        'path': 'image/path',
        'areas_of_interest': [{
            'area': 50.5,
            'center': (100, 200),
            'radius': 15
        }]
    }]
    assert images == expected_images
