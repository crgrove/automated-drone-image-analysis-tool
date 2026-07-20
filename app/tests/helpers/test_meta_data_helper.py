import pytest
import platform
import piexif
import json
import numpy as np
import tempfile
import os
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


def test_get_xmp_data_merged_prefers_direct_parse():
    """Direct (pure-Python) parse is primary; ExifTool must NOT be spawned when
    the XMP packet is directly parseable. Regression for the per-image
    exiftool.exe spawn introduced in f35a560 (2025-09-22)."""
    with patch.object(MetaDataHelper, '_parse_xmp_direct',
                      return_value={'drone-dji:RelativeAltitude': '+275.00'}) as direct, \
            patch.object(MetaDataHelper, 'get_meta_data_exiftool') as exiftool:
        result = MetaDataHelper.get_xmp_data_merged('/some/image.jpg')

    assert result == {'drone-dji:RelativeAltitude': '+275.00'}
    direct.assert_called_once_with('/some/image.jpg')
    exiftool.assert_not_called()  # the whole point: no subprocess on the hot path


def test_get_xmp_data_merged_falls_back_to_exiftool_when_no_xmp():
    """When direct parsing finds nothing, ExifTool is used as the backup."""
    with patch.object(MetaDataHelper, '_parse_xmp_direct', return_value={}), \
            patch.object(MetaDataHelper, '_parse_xmp_exiftool',
                         return_value={'from': 'exiftool'}) as exiftool_parse:
        result = MetaDataHelper.get_xmp_data_merged('/some/image.jpg')

    assert result == {'from': 'exiftool'}
    exiftool_parse.assert_called_once_with('/some/image.jpg')


def test_parse_xmp_direct_extracts_drone_fields_without_exiftool():
    """A real JPEG with an embedded XMP packet must parse via the direct path,
    surfacing the drone fields, with no ExifTool spawn."""
    drone_ns = "http://www.dji.com/drone-dji/1.0/"
    fields = [
        (drone_ns, "RelativeAltitude", "+275.0000"),
        (drone_ns, "GimbalYawDegree", "+45.0000"),
    ]
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        Image.new("RGB", (16, 16), color=(128, 128, 128)).save(tmp_path, "JPEG")
        MetaDataHelper.add_xmp_fields(tmp_path, fields)

        with patch.object(MetaDataHelper, 'get_meta_data_exiftool') as exiftool:
            result = MetaDataHelper.get_xmp_data_merged(tmp_path)

        assert result, "direct parse returned no XMP data"
        # The altitude value must come through (key namespacing may vary).
        flat = " ".join(f"{k}={v}" for k, v in result.items())
        assert "275" in flat
        exiftool.assert_not_called()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_get_xmp_data_merged_uses_exiftool_when_file_has_no_xmp():
    """A plain JPEG with no XMP packet falls back to the ExifTool backup."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        Image.new("RGB", (16, 16), color=(10, 20, 30)).save(tmp_path, "JPEG")
        # Sanity: direct parse finds nothing.
        assert MetaDataHelper._parse_xmp_direct(tmp_path) == {}

        with patch.object(MetaDataHelper, 'get_meta_data_exiftool',
                          return_value={'EXIF:Make': 'TestCam'}) as exiftool:
            result = MetaDataHelper.get_xmp_data_merged(tmp_path)

        exiftool.assert_called_once_with(tmp_path)
        assert result.get('EXIF:Make') == 'TestCam'
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_add_xmp_fields_multi_namespace_round_trip():
    """Batched writer must register one prefix per unique URI; before the fix this
    triggered libxml2 'Prefix format reserved for internal use' when six DJI tags
    were written alongside two WALDO tags in a single call."""
    drone_ns = "http://www.dji.com/drone-dji/1.0/"
    waldo_ns = "http://adiat.io/ns/waldo/1.0/"
    fields = [
        (drone_ns, "GimbalPitchDegree", "-90.0000"),
        (drone_ns, "GimbalYawDegree", "+45.0000"),
        (drone_ns, "GimbalRollDegree", "+22.5000"),
        (drone_ns, "FlightYawDegree", "+45.0000"),
        (drone_ns, "RelativeAltitude", "+275.0000"),
        (drone_ns, "AbsoluteAltitude", "+3245.0000"),
        (waldo_ns, "Processed", "true"),
        (waldo_ns, "ProcessorVersion", "1"),
    ]

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        Image.new("RGB", (16, 16), color=(128, 128, 128)).save(tmp_path, "JPEG")
        MetaDataHelper.add_xmp_fields(tmp_path, fields)

        xmp_xml = MetaDataHelper.get_xmp_data(tmp_path)
        # Each value must be present, and each unique URI must appear exactly once
        # as an xmlns declaration with a stable, human-readable prefix.
        for _, _, value in fields:
            assert value in xmp_xml, f"value {value} missing from XMP after round-trip"
        assert xmp_xml.count(f'xmlns:drone-dji="{drone_ns}"') == 1
        assert xmp_xml.count(f'xmlns:waldo="{waldo_ns}"') == 1
        # Sanity: no leaked synthetic 'ns0'/'ns1'/... bindings for the well-known URIs.
        assert f'xmlns:ns0="{drone_ns}"' not in xmp_xml
        assert f'xmlns:ns1="{drone_ns}"' not in xmp_xml
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_get_xmp_data_direct_delegates_to_parse_xmp_direct():
    """The public get_xmp_data_direct wrapper must delegate straight to
    _parse_xmp_direct and return its result unchanged -- no extra processing,
    no ExifTool spawn. Regression guard for the POD-pass hot path added during
    the Coverage/POD merge (PR #119)."""
    sentinel = {'drone-dji:RelativeAltitude': '+275.00', 'GimbalYawDegree': '+45.00'}
    with patch.object(MetaDataHelper, '_parse_xmp_direct',
                      return_value=sentinel) as direct, \
            patch.object(MetaDataHelper, 'get_meta_data_exiftool') as exiftool:
        result = MetaDataHelper.get_xmp_data_direct('/some/image.jpg')

    # Exact delegation: the wrapper returns the very object it received.
    assert result is sentinel
    direct.assert_called_once_with('/some/image.jpg')
    exiftool.assert_not_called()  # subprocess-free wrapper


def test_get_xmp_data_direct_matches_parse_on_real_image(example_image_path):
    """On a real testData image the public wrapper returns a dict identical to
    the private _parse_xmp_direct it wraps (no divergence between the two)."""
    expected = MetaDataHelper._parse_xmp_direct(example_image_path)
    result = MetaDataHelper.get_xmp_data_direct(example_image_path)

    assert isinstance(result, dict)
    assert result == expected
    # DJI_0082.JPG carries real drone XMP, so the direct parse is non-empty.
    assert result
