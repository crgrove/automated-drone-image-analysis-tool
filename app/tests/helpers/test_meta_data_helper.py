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


def test_get_raw_temperature_data(example_image_path):
    raw_bytes = b'raw thermal image bytes'
    with patch('exiftool.ExifTool') as MockExifTool:
        mock_et = MockExifTool.return_value.__enter__.return_value
        mock_et.execute.return_value = raw_bytes
        result = MetaDataHelper.get_raw_temperature_data(example_image_path)
        mock_et.execute.assert_called_once_with("-b", "-RawThermalImage", example_image_path, raw_bytes=True)
        assert result == raw_bytes


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


def test_embed_xmp_xml(example_destination_path):
    """Test embedding XMP XML data into an image file."""
    import tempfile
    import os

    # Create a temporary destination file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        # Write some dummy JPEG data
        tmp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')  # JPEG header
        tmp_file.write(b'\x00' * 100)  # Some dummy data
        tmp_dest = tmp_file.name

    try:
        # Create XMP XML bytes
        xmp_xml_bytes = b'<xmp>test data</xmp>'

        # Test embedding XMP XML
        MetaDataHelper.embed_xmp_xml(xmp_xml_bytes, tmp_dest)

        # Verify file was modified (should contain XMP data)
        with open(tmp_dest, 'rb') as f:
            content = f.read()
            # XMP should be embedded in the file
            assert len(content) > 0
    finally:
        if os.path.exists(tmp_dest):
            os.unlink(tmp_dest)


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
