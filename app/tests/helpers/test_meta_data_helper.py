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
    return "app/tests/data/rgb/input/DJI_0082.JPG"


@pytest.fixture
def example_destination_path():
    return "app/tests/data/rgb/output/ADIAT_Results/DJI_0082.JPG"


def test__get_exif_tool_path_windows():
    with patch('platform.system', return_value='Windows'):
        expected_path = path.abspath(path.join(path.dirname(path.dirname(path.dirname(__file__))), 'external/exiftool.exe'))
        assert MetaDataHelper._get_exif_tool_path() == expected_path


def test__transfer_exif_piexif(example_image_path, example_destination_path):
    with patch('piexif.transplant') as mock_transplant, \
            patch('app.helpers.MetaDataHelper.MetaDataHelper._transfer_exif_pil') as mock__transfer_exif_pil:
        MetaDataHelper._transfer_exif_piexif(example_image_path, example_destination_path)
        mock_transplant.assert_called_once_with(example_image_path, example_destination_path)
        mock__transfer_exif_pil.assert_not_called()


def test__transfer_exif_piexif_with_invalid_image_data(example_image_path, example_destination_path):
    with patch('piexif.transplant', side_effect=piexif._exceptions.InvalidImageDataError), \
            patch('app.helpers.MetaDataHelper.MetaDataHelper._transfer_exif_pil') as mock__transfer_exif_pil:
        MetaDataHelper._transfer_exif_piexif(example_image_path, example_destination_path)
        mock__transfer_exif_pil.assert_called_once_with(example_image_path, example_destination_path)


def test__transfer_exif_pil(example_image_path, example_destination_path):
    mock_image_origin = MagicMock(spec=Image.Image)  # Ensure it behaves like a PIL Image
    mock_image_destination = MagicMock(spec=Image.Image)

    mock_image_origin.info = {'exif': b'exifdata'}

    with patch('PIL.Image.open', side_effect=[mock_image_origin, mock_image_destination]) as mock_open_image:
        MetaDataHelper._transfer_exif_pil(example_image_path, example_destination_path)

        # Ensure both images are opened
        mock_open_image.assert_any_call(example_image_path)
        mock_open_image.assert_any_call(example_destination_path)

        # Ensure the destination image was saved with the correct EXIF data
        mock_image_destination.save.assert_called_once_with(example_destination_path, 'JPEG', exif=b'exifdata')


def test_transfer_exif_exiftool(example_image_path, example_destination_path):
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        MetaDataHelper.transfer_exif_exiftool(example_image_path, example_destination_path)
        mock_et.execute.assert_called_once_with("-tagsfromfile", example_image_path, "-exif", example_destination_path, "-overwrite_original")


def test_transfer_xmp_exiftool(example_image_path, example_destination_path):
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        MetaDataHelper.transfer_xmp_exiftool(example_image_path, example_destination_path)
        mock_et.execute.assert_called_once_with("-tagsfromfile", example_image_path, "-xmp", example_destination_path, "-overwrite_original")


def test_transfer_all_exiftool(example_image_path, example_destination_path):
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        MetaDataHelper.transfer_all_exiftool(example_image_path, example_destination_path)
        mock_et.execute.assert_called_once_with("-tagsfromfile", example_image_path, example_destination_path, "-overwrite_original", "--thumbnailimage")


def test_transfer_temperature_data(example_destination_path):
    data = np.array([1, 2, 3])
    json_data = json.dumps(data.tolist())
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        MetaDataHelper.transfer_temperature_data(data, example_destination_path)
        mock_et_helper.set_tags.assert_called_once_with(
            [example_destination_path],
            tags={"Notes": json_data},
            params=["-P", "-overwrite_original"]
        )


def test_get_raw_temperature_data(example_image_path):
    raw_bytes = b'raw thermal image bytes'
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        mock_et.execute.return_value = raw_bytes
        result = MetaDataHelper.get_raw_temperature_data(example_image_path)
        mock_et.execute.assert_called_once_with("-b", "-RawThermalImage", example_image_path, raw_bytes=True)
        assert result == raw_bytes


def test_get_temperature_data(example_image_path):
    data = [1, 2, 3]
    json_data = json.dumps(data)
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        mock_et_helper.get_tags.return_value = [{'XMP:Notes': json_data}]
        result = MetaDataHelper.get_temperature_data(example_image_path)
        mock_et_helper.get_tags.assert_called_once_with([example_image_path], tags=['Notes'])
        assert np.array_equal(result, np.asarray(data))


def test_get_meta_data_exiftool(example_image_path):
    metadata = {'EXIF:Make': 'Canon', 'EXIF:Model': '5D'}
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        mock_et_helper.get_metadata.return_value = [metadata]
        result = MetaDataHelper.get_meta_data_exiftool(example_image_path)
        mock_et_helper.get_metadata.assert_called_once_with([example_image_path])
        assert result == metadata


def test_set_tags_exiftool(example_image_path):
    tags = {"EXIF:Make": "Canon", "EXIF:Model": "5D"}
    with patch('exiftool.ExifToolHelper') as MockExifToolHelper:
        mock_et_helper = MockExifToolHelper.return_value.__enter__.return_value
        MetaDataHelper.set_tags_exiftool(example_image_path, tags)
        mock_et_helper.set_tags.assert_called_once_with([example_image_path], tags=tags, params=["-overwrite_original"])


def test_get_xmp_data(example_image_path):
    raw_xmp_data = b'<?xpacket begin<xmp>data</xmp><?xpacket end>'
    expected_xmp_data = '<xmp>data</xmp>'  # Expected parsed XMP content

    with patch('builtins.open', mock_open(read_data=raw_xmp_data)) as mock_file:
        result = MetaDataHelper.get_xmp_data(example_image_path)
        assert expected_xmp_data in result  # Ensure extracted XMP data matches
        mock_file.assert_called_once_with(example_image_path, 'rb')


def test_set_xmp_data(example_image_path, example_destination_path):
    xmp_data = MetaDataHelper.get_xmp_data(example_image_path)
    MetaDataHelper.set_xmp_data(example_destination_path, xmp_data)


def test_add_gps_data(example_image_path):
    with patch("PIL.Image.open") as mock_open_image, patch("piexif.dump") as mock_piexif_dump:
        mock_image = MagicMock()
        mock_open_image.return_value = mock_image
        mock_piexif_dump.return_value = b"mock_exif_data"  # Mock piexif.dump output

        MetaDataHelper.add_gps_data(example_image_path, 30.2672, -97.7431, 150)

        # Ensure save is called once with correct arguments
        mock_image.save.assert_called_once()
        args, kwargs = mock_image.save.call_args

        # Ensure the file path is correct
        assert args[0] == example_image_path

        # Check that EXIF data is set
        assert "exif" in kwargs
        assert kwargs["exif"] == b"mock_exif_data"

        # Format may not be explicitly set, so check only if it exists
        if "format" in kwargs:
            assert kwargs["format"].lower() in ["jpeg", "jpg"]


def test_get_exif_data_piexif(example_image_path):
    mock_exif_data = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
    with patch('piexif.load', return_value=mock_exif_data) as mock_piexif_load:
        result = MetaDataHelper.get_exif_data_piexif(example_image_path)
        assert result == mock_exif_data
        mock_piexif_load.assert_called_once_with(example_image_path)
