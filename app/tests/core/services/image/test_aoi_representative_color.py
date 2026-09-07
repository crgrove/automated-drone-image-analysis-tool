"""Tests for AOIService's representative-colour calculation.

The real implementation had no test - every existing test stubs
``get_aoi_representative_color`` on a mock service - even though it feeds the
AOI swatch, the gallery, and the KML, CalTopo and PDF exports. It is also the
function where ``if not colors:`` had to become ``if len(colors) == 0:`` when
the body was vectorized, because a numpy array raises on truth-value
testing; that is exactly the kind of edit a test should be holding down.
"""

import numpy as np
import pytest

from core.services.image.AOIService import AOIService


class FakeImageService:
    """Stands in for ImageService, which otherwise reads metadata from disk."""

    def __init__(self, img_array):
        self.img_array = img_array


@pytest.fixture
def service():
    return AOIService.__new__(AOIService)


def with_image(service, img_array):
    service.image_service = FakeImageService(img_array)
    return service


def solid(height, width, rgb):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = rgb
    return img


# ---------------------------------------------------------------------------
# detected-pixel path
# ---------------------------------------------------------------------------

def test_averages_the_detected_pixels(service):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[5, 5] = (200, 0, 0)
    img[5, 6] = (100, 0, 0)
    with_image(service, img)

    result = service.get_aoi_representative_color(
        {'center': (5, 5), 'radius': 3, 'detected_pixels': [(5, 5), (6, 5)]}
    )

    assert result['avg_rgb'] == (150, 0, 0)


def test_detected_pixels_take_priority_over_the_circle(service):
    """A red circle with one green detected pixel reports green."""
    img = solid(20, 20, (255, 0, 0))
    img[10, 10] = (0, 255, 0)
    with_image(service, img)

    result = service.get_aoi_representative_color(
        {'center': (10, 10), 'radius': 5, 'detected_pixels': [(10, 10)]}
    )

    assert result['avg_rgb'] == (0, 255, 0)


def test_out_of_bounds_detected_pixels_are_ignored(service):
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[2, 2] = (60, 120, 180)
    with_image(service, img)

    result = service.get_aoi_representative_color(
        {'center': (2, 2), 'radius': 1,
         'detected_pixels': [(2, 2), (999, 999), (-4, -4)]}
    )

    assert result['avg_rgb'] == (60, 120, 180)


def test_all_detected_pixels_out_of_bounds_returns_none(service):
    with_image(service, solid(10, 10, (10, 20, 30)))

    result = service.get_aoi_representative_color(
        {'center': (5, 5), 'radius': 2, 'detected_pixels': [(99, 99)]}
    )

    assert result is None


def test_ragged_detected_pixels_do_not_fail_the_aoi(service):
    """np.asarray raises on inhomogeneous input; an AOI must survive it.

    detected_pixels also arrive from ADIAT_Data.xml via literal_eval, so a
    malformed row in an old results file must not cost the whole colour.
    """
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[1, 1] = (90, 90, 90)
    img[3, 3] = (30, 30, 30)
    with_image(service, img)

    result = service.get_aoi_representative_color(
        {'center': (2, 2), 'radius': 3,
         'detected_pixels': [(1, 1), (3, 3, 7)]}
    )

    assert result is not None
    assert result['avg_rgb'] == (60, 60, 60)


# ---------------------------------------------------------------------------
# circle path
# ---------------------------------------------------------------------------

def test_samples_the_circle_when_there_are_no_detected_pixels(service):
    img = solid(20, 20, (10, 40, 70))
    with_image(service, img)

    result = service.get_aoi_representative_color({'center': (10, 10), 'radius': 4})

    assert result['avg_rgb'] == (10, 40, 70)


def test_circle_sampling_excludes_pixels_outside_the_disc(service):
    """The box corners are not in the circle, so their colour must not count."""
    img = solid(20, 20, (0, 0, 0))
    # fill the disc around (10, 10) r=2 with white, leave box corners black
    for y in range(8, 13):
        for x in range(8, 13):
            if (x - 10) ** 2 + (y - 10) ** 2 <= 4:
                img[y, x] = (255, 255, 255)
    with_image(service, img)

    result = service.get_aoi_representative_color({'center': (10, 10), 'radius': 2})

    assert result['avg_rgb'] == (255, 255, 255)


def test_circle_clipped_at_the_image_edge(service):
    img = solid(10, 10, (80, 80, 80))
    with_image(service, img)

    result = service.get_aoi_representative_color({'center': (0, 0), 'radius': 4})

    assert result['avg_rgb'] == (80, 80, 80)


def test_circle_entirely_off_the_image_returns_none(service):
    with_image(service, solid(10, 10, (5, 5, 5)))

    assert service.get_aoi_representative_color({'center': (99, 99), 'radius': 2}) is None


def test_empty_detected_pixels_falls_through_to_the_circle(service):
    img = solid(20, 20, (7, 8, 9))
    with_image(service, img)

    result = service.get_aoi_representative_color(
        {'center': (10, 10), 'radius': 3, 'detected_pixels': []}
    )

    assert result['avg_rgb'] == (7, 8, 9)


# ---------------------------------------------------------------------------
# returned shape
# ---------------------------------------------------------------------------

def test_returns_a_vibrant_marker_at_full_saturation(service):
    """The marker colour is the sampled hue at full saturation and value."""
    img = solid(10, 10, (128, 64, 64))   # a desaturated red
    with_image(service, img)

    result = service.get_aoi_representative_color({'center': (5, 5), 'radius': 2})

    assert result['avg_rgb'] == (128, 64, 64)
    assert result['rgb'] == (255, 0, 0)
    assert result['hex'] == '#ff0000'
    assert result['hue_degrees'] == 0


def test_result_carries_every_documented_key(service):
    with_image(service, solid(10, 10, (10, 200, 60)))

    result = service.get_aoi_representative_color({'center': (5, 5), 'radius': 2})

    assert set(result) == {'rgb', 'hex', 'hue_degrees', 'avg_rgb'}
    assert result['hex'] == '#{:02x}{:02x}{:02x}'.format(*result['rgb'])
    assert 0 <= result['hue_degrees'] <= 360


def test_hue_degrees_tracks_the_sampled_colour(service):
    with_image(service, solid(10, 10, (0, 0, 255)))   # pure blue

    result = service.get_aoi_representative_color({'center': (5, 5), 'radius': 2})

    assert result['hue_degrees'] == pytest.approx(240, abs=1)
    assert result['rgb'] == (0, 0, 255)
