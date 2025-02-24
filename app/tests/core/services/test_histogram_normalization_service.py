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
    return "app/tests/data/rgb/input/DJI_0082.JPG"


@pytest.fixture
def mock_source_image():
    return "app/tests/data/rgb/input/DJI_0083.JPG"


def test_histogram_normalization_service_initialization(mock_reference_image):
    mock_path = "app/tests/data/rgb/input/DJI_0084.JPG"
    mock_image_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)  # Mock image

    with patch("imghdr.what", return_value="jpeg"), \
            patch("numpy.fromfile", return_value=mock_image_array.tobytes()), \
            patch("cv2.imdecode", return_value=mock_image_array):
        service = HistogramNormalizationService(mock_path)
        assert np.array_equal(service.hist_ref_img, mock_image_array)


def test_histogram_normalization_service_initialization_invalid_image():
    mock_path = "/path/to/invalid/image.xyz"

    with patch("imghdr.what", return_value=None):
        with pytest.raises(Exception, match="The reference image path is not a valid image file."):
            HistogramNormalizationService(mock_path)


def test_matchHistograms(mock_reference_image, mock_source_image):
    mock_path = "app/tests/data/rgb/input/DJI_0084.JPG"
    mock_image_array_ref = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)  # Mock reference image
    mock_image_array_src = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)  # Mock source image

    with patch("imghdr.what", return_value="jpeg"), \
            patch("numpy.fromfile", return_value=mock_image_array_ref.tobytes()), \
            patch("cv2.imdecode", return_value=mock_image_array_ref):
        service = HistogramNormalizationService(mock_path)

    with patch("skimage.exposure.match_histograms", return_value=mock_image_array_src) as mock_match_histograms:
        result = service.match_histograms(mock_image_array_src)
        mock_match_histograms.assert_called_once_with(mock_image_array_src, mock_image_array_ref, channel_axis=-1)
        assert np.array_equal(result, mock_image_array_src)
