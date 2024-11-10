import pytest
import numpy as np
import cv2
import imghdr
from unittest.mock import patch, MagicMock, call
from skimage import exposure
from app.core.services.HistogramNormalizationService import HistogramNormalizationService  # Adjust the import according to your project structure
from app.core.services.LoggerService import LoggerService  # Adjust the import according to your project structure


@pytest.fixture
def mock_reference_image():
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def mock_source_image():
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


def test_histogram_normalization_service_initialization(mock_reference_image):
    mock_path = "/path/to/reference/image.jpg"

    with patch("imghdr.what", return_value="jpeg"), \
            patch("numpy.fromfile", return_value=mock_reference_image.tobytes()), \
            patch("cv2.imdecode", return_value=mock_reference_image):
        service = HistogramNormalizationService(mock_path)
        assert np.array_equal(service.hist_ref_img, mock_reference_image)


def test_histogram_normalization_service_initialization_invalid_image():
    mock_path = "/path/to/invalid/image.xyz"

    with patch("imghdr.what", return_value=None):
        service = HistogramNormalizationService(mock_path)
        assert not hasattr(service, 'hist_ref_img')


def test_matchHistograms(mock_reference_image, mock_source_image):
    mock_path = "/path/to/reference/image.jpg"

    with patch("imghdr.what", return_value="jpeg"), \
            patch("numpy.fromfile", return_value=mock_reference_image.tobytes()), \
            patch("cv2.imdecode", return_value=mock_reference_image):
        service = HistogramNormalizationService(mock_path)

    with patch("skimage.exposure.match_histograms", return_value=mock_source_image) as mock_match_histograms:
        result = service.matchHistograms(mock_source_image)
        mock_match_histograms.assert_called_once_with(mock_source_image, mock_reference_image, channel_axis=-1)
        assert np.array_equal(result, mock_source_image)
