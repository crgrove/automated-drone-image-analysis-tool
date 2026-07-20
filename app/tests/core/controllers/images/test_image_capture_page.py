"""Tests for ImageCapturePage camera detection defaults.

Regression coverage for the "Air" auto-selection bug: when the camera in the
first image's EXIF couldn't be matched against the drone database, a
make-only fuzzy match selected that manufacturer's alphabetically-first
model (e.g. "Air") instead of leaving the dropdown on the
"Select Drone/Camera" placeholder.
"""

import pandas as pd
import piexif
import pytest
from unittest.mock import MagicMock, patch

from core.controllers.images.guidePages.ImageCapturePage import ImageCapturePage


class FakeComboBox:
    """Minimal stand-in for QComboBox backed by a list of item data."""

    def __init__(self, items):
        self._items = list(items)
        self.current_index = 0
        self.set_index_calls = []

    def count(self):
        return len(self._items)

    def itemData(self, index):
        return self._items[index]

    def setCurrentIndex(self, index):
        self.current_index = index
        self.set_index_calls.append(index)


def _sensor_row(make, model):
    return pd.Series({'Make': make, 'Model': model, 'sensor_w': 6.3, 'sensor_h': 4.7})


@pytest.fixture
def page():
    with patch('core.controllers.images.guidePages.ImageCapturePage.LoggerService'):
        page = ImageCapturePage({}, MagicMock(), MagicMock())
    page.dialog.droneComboBox = FakeComboBox([
        None,                                # 0: "Select Drone/Camera"
        "__SECTION__",                       # 1: manufacturer header
        _sensor_row('DJI', 'Air 2S'),        # 2
        _sensor_row('DJI', 'Mavic 3'),       # 3
        "__SECTION__",                       # 4
        _sensor_row('Autel Robotics', 'EVO II'),  # 5
        None,                                # 6: "Other"
    ])
    return page


def test_fallback_match_exact_make_and_model(page):
    assert page._find_fallback_camera_index('DJI', 'Mavic 3') == 3


def test_fallback_match_substring_make_and_model(page):
    assert page._find_fallback_camera_index('SZ DJI Technology', 'Mavic 3 Classic') == 3


def test_fallback_make_only_match_returns_none(page):
    """Regression: exact make with an unknown model must NOT select the
    manufacturer's first model ("Air 2S")."""
    assert page._find_fallback_camera_index('DJI', 'FC9999') is None


def test_fallback_no_match_returns_none(page):
    assert page._find_fallback_camera_index('GoPro', 'HERO12') is None


def _make_image_dir(tmp_path):
    (tmp_path / 'IMG_0001.jpg').write_bytes(b'\xff\xd8\xff\xd9')
    return str(tmp_path)


def test_scan_defaults_to_placeholder_when_camera_unmatched(page, tmp_path):
    """Undetectable camera (EXIF present but not in database) -> index 0."""
    page.wizard_data['input_directory'] = _make_image_dir(tmp_path)
    page.wizard_data['altitude_unit'] = 'ft'

    image_service = MagicMock()
    image_service.get_relative_altitude.return_value = None
    image_service._get_camera_info.return_value = None
    image_service.drone_make = 'GoPro'
    image_service.exif_data = {"0th": {piexif.ImageIFD.Model: b'HERO12'}}

    with patch(
        'core.controllers.images.guidePages.ImageCapturePage.ImageService',
        return_value=image_service,
    ):
        page._scan_input_directory()

    assert page.dialog.droneComboBox.current_index == 0


def test_scan_defaults_to_placeholder_when_metadata_extraction_fails(page, tmp_path):
    """If EXIF can't be read at all, the placeholder must be selected."""
    page.wizard_data['input_directory'] = _make_image_dir(tmp_path)
    page.wizard_data['altitude_unit'] = 'ft'

    with patch(
        'core.controllers.images.guidePages.ImageCapturePage.ImageService',
        side_effect=RuntimeError('unreadable EXIF'),
    ):
        page._scan_input_directory()

    assert page.dialog.droneComboBox.current_index == 0


def test_scan_selects_camera_on_confident_match(page, tmp_path):
    """A make+model match still auto-selects the camera."""
    page.wizard_data['input_directory'] = _make_image_dir(tmp_path)
    page.wizard_data['altitude_unit'] = 'ft'

    image_service = MagicMock()
    image_service.get_relative_altitude.return_value = None
    image_service._get_camera_info.return_value = None
    image_service.drone_make = 'DJI'
    image_service.exif_data = {"0th": {piexif.ImageIFD.Model: b'Mavic 3'}}

    with patch(
        'core.controllers.images.guidePages.ImageCapturePage.ImageService',
        return_value=image_service,
    ):
        page._scan_input_directory()

    assert page.dialog.droneComboBox.current_index == 3
