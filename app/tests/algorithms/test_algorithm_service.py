import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.algorithms.Algorithm import AlgorithmService
import cv2
import numpy as np
from pathlib import Path
import platform


class TestAlgorithmService(AlgorithmService):
    def process_image(self, img, full_path, input_dir, output_dir):
        pass


@pytest.fixture
def algorithm_service():
    return TestAlgorithmService(
        name='TestAlgorithm',
        identifier_color=(255, 0, 0),
        min_area=100,
        aoi_radius=5,
        combine_aois=True,
        options={'option1': 'value1'},
        is_thermal=False
    )


@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('cv2.imencode', return_value=(True, MagicMock()))
@patch('platform.system', return_value='Windows')
@patch('app.helpers.MetaDataHelper.MetaDataHelper.transfer_exif_piexif')
@patch('pathlib.Path.parents', new_callable=MagicMock)
@patch('builtins.open', new_callable=mock_open)
@patch('PIL.Image.open', return_value=MagicMock())
def test_store_image(mock_image_open, mock_open, mock_path_parents, mock_transfer_exif_piexif,
                     mock_platform, mock_imencode, mock_exists, mock_makedirs, algorithm_service):
    mock_input_file = 'input/file/path.jpg'
    mock_output_file = 'output/file/path.jpg'
    mock_augmented_image = MagicMock()
    mock_temperature_data = None

    algorithm_service.store_image(mock_input_file, mock_output_file, mock_augmented_image, mock_temperature_data)

    mock_exists.assert_called_once_with(Path(mock_output_file).parents[0])
    mock_makedirs.assert_called_once_with(Path(mock_output_file).parents[0])


def test_circle_areas_of_interest(algorithm_service):
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    contours = [np.array([[10, 10], [10, 20], [20, 20], [20, 10]], dtype=np.int32)]

    with patch('cv2.circle', return_value=img) as mock_circle, \
            patch('cv2.findContours', return_value=(contours, None)):
        result_img, areas_of_interest, base_contour_count = algorithm_service.circle_areas_of_interest(img, contours)

        assert result_img is not None
        assert len(areas_of_interest) > 0
        assert base_contour_count == len(contours)
        mock_circle.assert_called()


def test_circle_areas_of_interest_no_contours(algorithm_service):
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    contours = []

    result_img, areas_of_interest, base_contour_count = algorithm_service.circle_areas_of_interest(img, contours)

    assert result_img is None
    assert areas_of_interest is None
    assert base_contour_count is None
