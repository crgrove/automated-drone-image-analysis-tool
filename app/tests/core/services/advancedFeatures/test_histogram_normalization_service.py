import pytest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from PIL import Image, UnidentifiedImageError
from skimage import exposure
from core.services.advancedFeatures.HistogramNormalizationService import HistogramNormalizationService
from core.services.LoggerService import LoggerService


@pytest.fixture
def mock_reference_image():
    return "app/tests/data/rgb/input/DJI_0082.JPG"


@pytest.fixture
def mock_source_image():
    return "app/tests/data/rgb/input/DJI_0083.JPG"


def test_histogram_normalization_service_initialization(mock_reference_image):
    mock_path = "app/tests/data/rgb/input/DJI_0084.JPG"
    mock_image_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    with patch("PIL.Image.open") as mock_open, \
            patch("numpy.fromfile", return_value=mock_image_array.tobytes()), \
            patch("cv2.imdecode", return_value=mock_image_array):

        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img  # Simulate context manager
        service = HistogramNormalizationService(mock_path)

        assert np.array_equal(service.hist_ref_img, mock_image_array)


def test_histogram_normalization_service_initialization_invalid_image():
    mock_path = "/path/to/invalid/image.xyz"

    # Patch PIL.Image.open to raise an UnidentifiedImageError
    with patch("PIL.Image.open", side_effect=UnidentifiedImageError):
        with pytest.raises(Exception, match="The reference image path is not a valid image file."):
            HistogramNormalizationService(mock_path)


def test_matchHistograms(mock_reference_image, mock_source_image):
    mock_path = "app/tests/data/rgb/input/DJI_0084.JPG"
    mock_image_array_ref = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    mock_image_array_src = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    with patch("PIL.Image.open") as mock_open, \
            patch("numpy.fromfile", return_value=mock_image_array_ref.tobytes()), \
            patch("cv2.imdecode", return_value=mock_image_array_ref):

        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        service = HistogramNormalizationService(mock_path)

    with patch("skimage.exposure.match_histograms", return_value=mock_image_array_src) as mock_match_histograms:
        result = service.match_histograms(mock_image_array_src)
        mock_match_histograms.assert_called_once_with(mock_image_array_src, mock_image_array_ref, channel_axis=-1)
        assert np.array_equal(result, mock_image_array_src)
