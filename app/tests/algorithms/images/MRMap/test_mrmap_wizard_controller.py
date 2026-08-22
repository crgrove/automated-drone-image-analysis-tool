"""Tests for the MRMap wizard's aggressiveness -> threshold mapping.

MRMapService flags a pixel when its (size-normalized) bin count falls *below*
the threshold, so a higher threshold must mean more detections. These tests pin
that direction down in both the forward map (get_options) and the legacy reverse
map (load_options).
"""

import os
import tempfile

import numpy as np
import pytest

from algorithms.images.MRMap.controllers.MRMapWizardController import MRMapWizardController
from algorithms.images.MRMap.services.MRMapService import MRMapService

VERY_CONSERVATIVE = 0
VERY_AGGRESSIVE = 4


def _config():
    return {
        'name': 'MRMap',
        'label': 'MRMap',
        'controller': 'MRMapController',
        'wizard_controller': 'MRMapWizardController',
        'service': 'MRMapService',
        'combine_overlapping_aois': True,
        'platforms': ['Windows', 'Linux', 'Darwin'],
        'type': 'RGB'
    }


def _wizard(qtbot):
    wizard = MRMapWizardController(_config(), 'Dark')
    qtbot.addWidget(wizard)
    return wizard


def _threshold_for_index(qtbot, index):
    wizard = _wizard(qtbot)
    wizard.aggressivenessSlider.setValue(index)
    return wizard.get_options()['threshold']


def test_threshold_increases_with_aggressiveness(app, qtbot):
    """Each step toward 'Very Aggressive' must raise the threshold."""
    thresholds = [_threshold_for_index(qtbot, index) for index in range(5)]

    assert thresholds == sorted(thresholds), thresholds
    assert len(set(thresholds)) == len(thresholds), thresholds
    assert thresholds[VERY_AGGRESSIVE] > thresholds[VERY_CONSERVATIVE]


def test_aggressiveness_round_trips_through_index(app, qtbot):
    """Saving and reloading a wizard config must restore the same preset."""
    for index in range(5):
        source = _wizard(qtbot)
        source.aggressivenessSlider.setValue(index)
        options = source.get_options()

        target = _wizard(qtbot)
        target.load_options(options)

        assert target.aggressivenessSlider.value() == index


def test_aggressiveness_round_trips_through_threshold_only(app, qtbot):
    """Configs predating 'aggressiveness_index' reload via the threshold map."""
    for index in range(5):
        source = _wizard(qtbot)
        source.aggressivenessSlider.setValue(index)
        options = source.get_options()
        legacy = {'threshold': options['threshold']}

        target = _wizard(qtbot)
        target.load_options(legacy)

        assert target.aggressivenessSlider.value() == index, legacy


@pytest.fixture
def rare_color_image():
    """A frame of one common color plus small patches of rare colors.

    Sized so that MRMapService's normalization to an 8000x6000 reference leaves
    the rare patches inside the 'Very Aggressive' cutoff but outside the 'Very
    Conservative' one.
    """
    height, width = 1500, 2000
    img = np.full((height, width, 3), 128, dtype=np.uint8)
    patch_colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255)]
    for offset, color in enumerate(patch_colors):
        y = 100 + offset * 100
        x = 100 + offset * 100
        img[y:y + 3, x:x + 3] = color
    return img


def _detected_pixels(threshold, img):
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=3,
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options={'threshold': threshold, 'segments': 1, 'window': 5, 'colorspace': 'RGB'},
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        full_path = os.path.join(tmpdir, "test.jpg")
        result = service.process_image(img, full_path, tmpdir, tmpdir)

    assert result.error_message is None
    return len(result.areas_of_interest or [])


def test_very_aggressive_finds_more_than_very_conservative(app, qtbot, rare_color_image):
    """The wizard's labels must match what the service actually does."""
    conservative = _threshold_for_index(qtbot, VERY_CONSERVATIVE)
    aggressive = _threshold_for_index(qtbot, VERY_AGGRESSIVE)

    conservative_hits = _detected_pixels(conservative, rare_color_image)
    aggressive_hits = _detected_pixels(aggressive, rare_color_image)

    assert aggressive_hits > conservative_hits
