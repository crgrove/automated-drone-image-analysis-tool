"""The PDF report's AOI coordinates must honor the saved FOV alignment.

_calculate_aoi_gps rebuilt the image dict from scratch with only 'path' and
'mask_path', silently dropping 'fov_alignment' (the operator's hand-aligned
footprint from the Align Image tool), the XML-recovered 'bearing', and the
stored dimensions. The report then recomputed every AOI position from the raw
camera metadata the operator had already corrected - and handed field teams
coordinates that disagreed with the viewer by the size of the correction.
"""

from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from core.services.export.PdfGeneratorService import PdfGeneratorService


# A 100x100 image whose aligned footprint is a rectangle centered on
# (40.001, -75.001): TL, TR, BR, BL for pixels (0,0), (W,0), (W,H), (0,H).
_ALIGNED_CORNERS = [
    (40.0015, -75.0015),
    (40.0015, -75.0005),
    (40.0005, -75.0005),
    (40.0005, -75.0015),
]


@pytest.fixture
def pdf_service():
    viewer = MagicMock()
    viewer.custom_agl_altitude_ft = None
    viewer.use_terrain_elevation = False
    return PdfGeneratorService(viewer)


def _write_plain_jpeg(tmp_path):
    """A real decodable image with no EXIF GPS: the raw-metadata path cannot
    resolve it, so only the alignment path can produce coordinates."""
    path = str(tmp_path / 'DJI_0001.JPG')
    cv2.imwrite(path, np.zeros((100, 100, 3), dtype=np.uint8))
    return path


def test_pdf_aoi_gps_honors_saved_fov_alignment(pdf_service, tmp_path, monkeypatch):
    import core.services.image.AOIService as aoi_module
    monkeypatch.setattr(aoi_module, '_get_terrain_service', lambda: None)

    img = {
        'path': _write_plain_jpeg(tmp_path),
        'mask_path': '',
        'width': 100,
        'height': 100,
        'fov_alignment': {'corners': _ALIGNED_CORNERS, 'tie_points': [], 'rotation': 0},
        'areas_of_interest': [],
    }
    aoi = {'center': (50, 50), 'radius': 10}

    result = pdf_service._calculate_aoi_gps(img, aoi)

    assert result is not None, (
        'the alignment was dropped: the raw-metadata path has no GPS to fall back on')
    assert result['latitude'] == pytest.approx(40.001, abs=5e-5)
    assert result['longitude'] == pytest.approx(-75.001, abs=5e-5)


def test_pdf_aoi_gps_matches_the_viewer_path(pdf_service, tmp_path, monkeypatch):
    """The report and the viewer must hand out the same position for the same
    AOI - the viewer resolves through the full image dict, so the PDF must
    too."""
    import core.services.image.AOIService as aoi_module
    monkeypatch.setattr(aoi_module, '_get_terrain_service', lambda: None)

    img = {
        'path': _write_plain_jpeg(tmp_path),
        'mask_path': '',
        'width': 100,
        'height': 100,
        'fov_alignment': {'corners': _ALIGNED_CORNERS, 'tie_points': [], 'rotation': 0},
        'areas_of_interest': [],
    }
    aoi = {'center': (25, 75), 'radius': 10}

    viewer_result = aoi_module.AOIService(img).calculate_gps_with_custom_altitude(
        img, aoi, None, False)
    pdf_result = pdf_service._calculate_aoi_gps(img, aoi)

    assert viewer_result is not None and pdf_result is not None
    assert pdf_result['latitude'] == pytest.approx(viewer_result[0], abs=1e-9)
    assert pdf_result['longitude'] == pytest.approx(viewer_result[1], abs=1e-9)


def test_pdf_aoi_gps_preserves_metadata_and_substitutes_original_path(pdf_service, monkeypatch):
    """The dict handed to AOIService keeps every stored field (alignment,
    recovered bearing, dimensions) and only swaps in the original image path."""
    captured = {}

    class RecordingService:
        def __init__(self, image, img_array=None, image_service=None):
            captured['constructed_with'] = image

        def calculate_gps_with_custom_altitude(self, image, aoi, custom_alt_ft, use_terrain):
            captured['calculated_with'] = image
            return (1.0, 2.0)

    import core.services.export.PdfGeneratorService as pdf_module
    monkeypatch.setattr(pdf_module, 'AOIService', RecordingService)

    img = {
        'path': 'C:/results/masks/DJI_0001_mask.JPG',
        'original_path': 'C:/mission/FlightA/DJI_0001.JPG',
        'mask_path': 'C:/results/masks/DJI_0001_mask.JPG',
        'bearing': 123.4,
        'width': 4000,
        'height': 3000,
        'fov_alignment': {'corners': _ALIGNED_CORNERS},
    }

    result = pdf_service._calculate_aoi_gps(img, {'center': (10, 10), 'radius': 5})

    assert result == {'latitude': 1.0, 'longitude': 2.0}
    for received in (captured['constructed_with'], captured['calculated_with']):
        assert received['path'] == 'C:/mission/FlightA/DJI_0001.JPG'
        assert received['fov_alignment'] == img['fov_alignment']
        assert received['bearing'] == 123.4
        assert received['width'] == 4000 and received['height'] == 3000
