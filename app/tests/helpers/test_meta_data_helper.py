import pytest
import platform
import piexif
import json
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
from os import path
from PIL import Image
from app.helpers.MetaDataHelper import MetaDataHelper

@pytest.fixture
def example_image_path():
    return "/path/to/example/image.jpg"

@pytest.fixture
def example_destination_path():
    return "/path/to/destination/image.jpg"

def test_getEXIFToolPath_windows():
    with patch('platform.system', return_value='Windows'):
        expected_path = path.abspath(path.join(path.dirname(path.dirname(path.dirname(__file__))), 'external/exiftool.exe'))
        print(expected_path)
        assert MetaDataHelper.getEXIFToolPath() == expected_path

def test_transferExifPiexif(example_image_path, example_destination_path):
    with patch('piexif.transplant') as mock_transplant, \
         patch('app.helpers.MetaDataHelper.MetaDataHelper.transferExifPil') as mock_transferExifPil:
        MetaDataHelper.transferExifPiexif(example_image_path, example_destination_path)
        mock_transplant.assert_called_once_with(example_image_path, example_destination_path)
        mock_transferExifPil.assert_not_called()

def test_transferExifPiexif_with_invalid_image_data(example_image_path, example_destination_path):
    with patch('piexif.transplant', side_effect=piexif._exceptions.InvalidImageDataError), \
         patch('app.helpers.MetaDataHelper.MetaDataHelper.transferExifPil') as mock_transferExifPil:
        MetaDataHelper.transferExifPiexif(example_image_path, example_destination_path)
        mock_transferExifPil.assert_called_once_with(example_image_path, example_destination_path)

def test_transferExifPil(example_image_path, example_destination_path):
    with patch('PIL.Image.open') as mock_open:
        mock_image_origin = MagicMock()
        mock_image_destination = MagicMock()
        mock_image_origin.info = {'exif': b'exifdata'}
        mock_open.side_effect = [mock_image_origin, mock_image_destination]
        MetaDataHelper.transferExifPil(example_image_path, example_destination_path)
        mock_image_destination.save.assert_called_once_with(example_destination_path, 'JPEG', exif=b'exifdata')

def test_transferExifExiftool(example_image_path, example_destination_path):
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        MetaDataHelper.transferExifExiftool(example_image_path, example_destination_path)
        mock_et.execute.assert_called_once_with("-tagsfromfile", example_image_path, "-exif", example_destination_path, "-overwrite_original")

def test_transferXmpExiftool(example_image_path, example_destination_path):
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        MetaDataHelper.transferXmpExiftool(example_image_path, example_destination_path)
        mock_et.execute.assert_called_once_with("-tagsfromfile", example_image_path, "-xmp", example_destination_path, "-overwrite_original")

def test_transferAll(example_image_path, example_destination_path):
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        MetaDataHelper.transferAll(example_image_path, example_destination_path)
        mock_et.execute.assert_called_once_with("-tagsfromfile", example_image_path, example_destination_path, "-overwrite_original", "--thumbnailimage")

def test_transferTemperatureData(example_destination_path):
    data = np.array([1, 2, 3])
    json_data = json.dumps(data.tolist())
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        MetaDataHelper.transferTemperatureData(data, example_destination_path)
        mock_et_helper.set_tags.assert_called_once_with(
            [example_destination_path],
            tags={"Notes": json_data},
            params=["-P", "-overwrite_original"]
        )

def test_getRawTemperatureData(example_image_path):
    raw_bytes = b'raw thermal image bytes'
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        mock_et.execute.return_value = raw_bytes
        result = MetaDataHelper.getRawTemperatureData(example_image_path)
        mock_et.execute.assert_called_once_with("-b", "-RawThermalImage", example_image_path, raw_bytes=True)
        assert result == raw_bytes

def test_getTemperatureData(example_image_path):
    data = [1, 2, 3]
    json_data = json.dumps(data)
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        mock_et_helper.get_tags.return_value = [{'XMP:Notes': json_data}]
        result = MetaDataHelper.getTemperatureData(example_image_path)
        mock_et_helper.get_tags.assert_called_once_with([example_image_path], tags=['Notes'])
        assert np.array_equal(result, np.asarray(data))

def test_getMetaData(example_image_path):
    metadata = {'EXIF:Make': 'Canon', 'EXIF:Model': '5D'}
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        mock_et_helper.get_metadata.return_value = [metadata]
        result = MetaDataHelper.getMetaData(example_image_path)
        mock_et_helper.get_metadata.assert_called_once_with([example_image_path])
        assert result == metadata

def test_setTags(example_image_path):
    tags = {"EXIF:Make": "Canon", "EXIF:Model": "5D"}
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        MetaDataHelper.setTags(example_image_path, tags)
        mock_et_helper.set_tags.assert_called_once_with([example_image_path], tags=tags, params=["-overwrite_original"])
