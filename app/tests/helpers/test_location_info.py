import pytest
import piexif
import utm
from unittest.mock import patch, MagicMock
from PIL import Image, UnidentifiedImageError
from app.helpers.LocationInfo import LocationInfo


@pytest.fixture
def example_image_path():
    return "app/tests/data/rgb/input/DJI_0082.JPG"


@pytest.fixture
def example_gps_data():
    return {
        'GPS': {
            piexif.GPSIFD.GPSLatitude: [(37, 1), (48, 1), (20, 1)],
            piexif.GPSIFD.GPSLatitudeRef: b'N',
            piexif.GPSIFD.GPSLongitude: [(122, 1), (25, 1), (20, 1)],
            piexif.GPSIFD.GPSLongitudeRef: b'W'
        }
    }


def test_get_gps_jpg(example_image_path, example_gps_data):
    # Simulate a valid JPEG file via PIL
    with patch("PIL.Image.open") as mock_open, \
         patch("piexif.load", return_value=example_gps_data):

        mock_img = MagicMock()
        mock_img.format = "JPEG"
        mock_open.return_value.__enter__.return_value = mock_img

        result = LocationInfo.get_gps(full_path=example_image_path)
        assert result == {'latitude': 37.805556, 'longitude': -122.422222}


def test_get_gps_non_jpg(example_image_path):
    # Simulate a non-JPEG image (e.g., PNG)
    with patch("PIL.Image.open") as mock_open:
        mock_img = MagicMock()
        mock_img.format = "PNG"
        mock_open.return_value.__enter__.return_value = mock_img

        result = LocationInfo.get_gps(full_path=example_image_path)
        assert result == {}


def test_convert_degrees_to_utm():
    lat, lng = 37.805556, -122.422222
    result = LocationInfo.convert_degrees_to_utm(lat, lng)
    utm_coordinates = utm.from_latlon(lat, lng)
    expected = {
        'easting': utm_coordinates[0],
        'northing': utm_coordinates[1],
        'zone_number': utm_coordinates[2],
        'zone_letter': utm_coordinates[3]
    }
    assert result['easting'] == pytest.approx(expected['easting'], rel=1e-5)
    assert result['northing'] == pytest.approx(expected['northing'], rel=1e-5)
    assert result['zone_number'] == expected['zone_number']
    assert result['zone_letter'] == expected['zone_letter']


def test_convert_decimal_to_dms():
    lat, lng = 37.805556, -122.422222
    result = LocationInfo.convert_decimal_to_dms(lat, lng)
    expected = {
        'latitude': {'degrees': 37, 'minutes': 48, 'seconds': 20.0, 'reference': 'N'},
        'longitude': {'degrees': 122, 'minutes': 25, 'seconds': 20.0, 'reference': 'W'}
    }
    assert result == expected


def test__convert_to_degrees():
    value = [(37, 1), (48, 1), (20, 1)]
    result = LocationInfo._convert_to_degrees(value)
    assert result == pytest.approx(37.805556, rel=1e-6)
