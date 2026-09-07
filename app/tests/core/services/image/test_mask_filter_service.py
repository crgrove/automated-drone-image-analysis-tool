"""Sampling an operator-supplied filter mask.

An unusable mask is the case worth being careful about: returning False for
"not in the mask" when the file could not be read would hide every AOI in the
mission and look exactly like a mask that excluded everything. None means "no
opinion" and the callers must treat it that way.
"""

import cv2
import numpy as np
import pytest

from core.services.image.MaskFilterService import MaskFilterService


@pytest.fixture
def mask_file(tmp_path):
    """A 200x100 mask: white on the left half, black on the right."""
    mask = np.zeros((100, 200), dtype=np.uint8)
    mask[:, :100] = 255
    path = tmp_path / "mask.png"
    cv2.imwrite(str(path), mask)
    return str(path)


@pytest.fixture
def service():
    return MaskFilterService(logger=None)


def test_no_mask_means_no_opinion(service):
    assert service.get_scaled_mask(50, 50) is None
    assert service.contains((10, 10), 50, 50) is None


def test_the_mask_is_scaled_to_the_image(service, mask_file):
    service.set_mask_path(mask_file)

    scaled = service.get_scaled_mask(400, 200)

    assert scaled.shape == (200, 400)
    assert set(np.unique(scaled)) <= {0, 255}


def test_a_point_inside_and_outside_the_mask(service, mask_file):
    service.set_mask_path(mask_file)

    assert service.contains((100, 100), 400, 200) is True    # left half
    assert service.contains((300, 100), 400, 200) is False   # right half


def test_a_centre_outside_the_frame_is_clamped_not_an_error(service, mask_file):
    """An AOI's centre can land a pixel outside the image after expansion."""
    service.set_mask_path(mask_file)

    assert service.contains((-5, -5), 400, 200) is True
    assert service.contains((999, 999), 400, 200) is False


def test_an_unreadable_mask_is_no_opinion_not_exclusion(service, tmp_path):
    """The dangerous failure: reading False here would silently hide every
    AOI in the mission and look like a mask that excluded everything."""
    service.set_mask_path(str(tmp_path / "does-not-exist.png"))

    assert service.get_scaled_mask(400, 200) is None
    assert service.contains((10, 10), 400, 200) is None


def test_scaled_masks_are_cached_per_size(service, mask_file):
    """One mask against many same-sized images; re-resizing a
    full-resolution mask per AOI stalled the viewer."""
    service.set_mask_path(mask_file)

    first = service.get_scaled_mask(400, 200)
    assert service.get_scaled_mask(400, 200) is first
    assert service.get_scaled_mask(800, 400) is not first
    assert len(service._scaled) == 2


def test_setting_the_same_path_keeps_the_cache(service, mask_file):
    """set_mask_path runs on every filter pass, so it must not throw the
    cache away when nothing changed."""
    service.set_mask_path(mask_file)
    first = service.get_scaled_mask(400, 200)

    service.set_mask_path(mask_file)

    assert service.get_scaled_mask(400, 200) is first


def test_a_new_path_drops_the_previous_mask(service, mask_file, tmp_path):
    service.set_mask_path(mask_file)
    service.get_scaled_mask(400, 200)

    inverted = np.zeros((100, 200), dtype=np.uint8)
    inverted[:, 100:] = 255
    other = tmp_path / "other.png"
    cv2.imwrite(str(other), inverted)
    service.set_mask_path(str(other))

    assert service._scaled == {}
    assert service.contains((100, 100), 400, 200) is False   # now the dark half


def test_clearing_the_path_stops_filtering(service, mask_file):
    service.set_mask_path(mask_file)
    assert service.contains((100, 100), 400, 200) is True

    service.set_mask_path(None)

    assert service.contains((100, 100), 400, 200) is None


def test_the_threshold_is_binary(service, tmp_path):
    """Mid-greys must resolve one way or the other; a mask sampled at 137
    is not 'slightly inside'."""
    grey = np.full((10, 10), 137, dtype=np.uint8)
    grey[:, :5] = 100
    path = tmp_path / "grey.png"
    cv2.imwrite(str(path), grey)
    service.set_mask_path(str(path))

    scaled = service.get_scaled_mask(10, 10)

    assert set(np.unique(scaled)) <= {0, 255}
    assert service.contains((7, 5), 10, 10) is True    # 137 > 127
    assert service.contains((2, 5), 10, 10) is False   # 100 <= 127
