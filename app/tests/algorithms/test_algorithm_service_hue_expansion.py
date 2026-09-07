"""Tests for AlgorithmService.apply_hue_expansion.

This function had no coverage at all: its only callers (RXAnomalyService and
MatchedFilterService) gate it behind ``hue_expansion_enabled`` /
``hue_expansion_range``, which default to False/0 and which no test set - so
the whole body, including all three hue-wraparound branches, was never
executed by the suite even while it was being rewritten.

Hues are built by constructing HSV at full saturation and value and
converting to BGR, which round-trips exactly through cv2 for all 180 hues,
so a test can name the hue it means.
"""

import cv2
import numpy as np
import pytest

from algorithms.AlgorithmService import AlgorithmService


@pytest.fixture
def service():
    return AlgorithmService(
        name='HueExpansionProbe',
        identifier_color=(0, 0, 255),
        min_area=1,
        max_area=None,
        aoi_radius=5,
        combine_aois=False,
        options={},
    )


def bgr_image(hue_grid):
    """Build a BGR image whose per-pixel hues are exactly ``hue_grid``."""
    hue_grid = np.asarray(hue_grid, dtype=np.uint8)
    hsv = np.zeros(hue_grid.shape + (3,), dtype=np.uint8)
    hsv[..., 0] = hue_grid
    hsv[..., 1] = 255
    hsv[..., 2] = 255
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    # the premise of every assertion below
    assert np.array_equal(cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[..., 0], hue_grid)
    return bgr


# ---------------------------------------------------------------------------
# guards
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("areas_of_interest", [None, []])
def test_no_aois_returns_the_mask_untouched(service, areas_of_interest):
    img = bgr_image(np.full((6, 6), 60))
    mask = np.zeros((6, 6), np.uint8)
    mask[0, 0] = 255

    result = service.apply_hue_expansion(img, mask, areas_of_interest, 10)

    assert result is mask


def test_original_mask_pixels_are_preserved(service):
    """Expansion adds pixels; it never clears what the algorithm found."""
    img = bgr_image(np.full((10, 10), 60))
    mask = np.zeros((10, 10), np.uint8)
    mask[9, 9] = 255  # far from the AOI, and not a hue match target
    aois = [{'center': (2, 2), 'radius': 1, 'detected_pixels': [(2, 2)]}]

    result = service.apply_hue_expansion(img, mask, aois, 5)

    assert result[9, 9] == 255


def test_input_mask_is_not_mutated(service):
    img = bgr_image(np.full((10, 10), 60))
    mask = np.zeros((10, 10), np.uint8)
    aois = [{'center': (5, 5), 'radius': 2, 'detected_pixels': [(5, 5)]}]

    result = service.apply_hue_expansion(img, mask, aois, 5)

    assert result is not mask
    assert mask.sum() == 0


def test_aoi_without_detected_pixels_is_skipped(service):
    img = bgr_image(np.full((10, 10), 60))
    mask = np.zeros((10, 10), np.uint8)
    aois = [{'center': (5, 5), 'radius': 3, 'detected_pixels': []}]

    result = service.apply_hue_expansion(img, mask, aois, 90)

    assert result.sum() == 0


def test_aoi_with_only_out_of_bounds_pixels_is_skipped(service):
    """No in-bounds pixel means no average hue, so nothing to expand from."""
    img = bgr_image(np.full((10, 10), 60))
    mask = np.zeros((10, 10), np.uint8)
    aois = [{'center': (5, 5), 'radius': 3, 'detected_pixels': [(99, 99), (-4, -4)]}]

    result = service.apply_hue_expansion(img, mask, aois, 90)

    assert result.sum() == 0


# ---------------------------------------------------------------------------
# the three hue branches
# ---------------------------------------------------------------------------

def test_no_wraparound_selects_only_similar_hues(service):
    """avg hue 60, range 10 -> 50..70 inclusive, no wraparound."""
    hues = np.full((11, 11), 100)   # far from 60: must not match
    hues[5, 5] = 60                 # the detected pixel
    hues[5, 6] = 68                 # inside the range
    hues[5, 7] = 71                 # just outside the range
    img = bgr_image(hues)
    mask = np.zeros((11, 11), np.uint8)
    aois = [{'center': (5, 5), 'radius': 4, 'detected_pixels': [(5, 5)]}]

    result = service.apply_hue_expansion(img, mask, aois, 10)

    assert result[5, 5] == 255
    assert result[5, 6] == 255
    assert result[5, 7] == 0
    assert result[5, 2] == 0        # hue 100, inside the circle, no match


def test_wraparound_at_the_lower_bound(service):
    """avg hue 5, range 10 -> hue_min -5, so 175..179 and 0..15 match."""
    hues = np.full((11, 11), 90)
    hues[5, 5] = 5                  # detected pixel
    hues[5, 6] = 178                # wraps around the bottom: must match
    hues[5, 4] = 14                 # inside the upper part of the range
    hues[5, 7] = 160                # below 175: must not match
    img = bgr_image(hues)
    mask = np.zeros((11, 11), np.uint8)
    aois = [{'center': (5, 5), 'radius': 4, 'detected_pixels': [(5, 5)]}]

    result = service.apply_hue_expansion(img, mask, aois, 10)

    assert result[5, 5] == 255
    assert result[5, 6] == 255
    assert result[5, 4] == 255
    assert result[5, 7] == 0


def test_wraparound_at_the_upper_bound(service):
    """avg hue 175, range 10 -> hue_max 185, so 165..179 and 0..5 match."""
    hues = np.full((11, 11), 90)
    hues[5, 5] = 175                # detected pixel
    hues[5, 6] = 3                  # wraps around the top: must match
    hues[5, 4] = 166                # inside the lower part of the range
    hues[5, 7] = 20                 # above 5: must not match
    img = bgr_image(hues)
    mask = np.zeros((11, 11), np.uint8)
    aois = [{'center': (5, 5), 'radius': 4, 'detected_pixels': [(5, 5)]}]

    result = service.apply_hue_expansion(img, mask, aois, 10)

    assert result[5, 5] == 255
    assert result[5, 6] == 255
    assert result[5, 4] == 255
    assert result[5, 7] == 0


def test_average_hue_comes_from_all_in_bounds_detected_pixels(service):
    """The centre hue is the mean of the AOI's pixels, not any one of them."""
    hues = np.full((11, 11), 90)
    hues[5, 4] = 40
    hues[5, 6] = 60
    hues[5, 5] = 50                 # the mean of 40 and 60
    hues[0, 0] = 50
    img = bgr_image(hues)
    mask = np.zeros((11, 11), np.uint8)
    aois = [{'center': (5, 5), 'radius': 3, 'detected_pixels': [(4, 5), (6, 5)]}]

    # range 1 around a mean of 50 keeps 50 and excludes 40 and 60
    result = service.apply_hue_expansion(img, mask, aois, 1)

    assert result[5, 5] == 255
    assert result[5, 4] == 0
    assert result[5, 6] == 0


# ---------------------------------------------------------------------------
# circle geometry
# ---------------------------------------------------------------------------

def test_expansion_is_confined_to_the_aoi_circle(service):
    """A matching hue outside the circle must stay unselected."""
    hues = np.full((21, 21), 60)    # every pixel matches on hue alone
    img = bgr_image(hues)
    mask = np.zeros((21, 21), np.uint8)
    aois = [{'center': (10, 10), 'radius': 3, 'detected_pixels': [(10, 10)]}]

    result = service.apply_hue_expansion(img, mask, aois, 5)

    assert result[10, 10] == 255
    assert result[10, 13] == 255    # on the circle edge
    assert result[10, 14] == 0      # one pixel beyond it
    assert result[0, 0] == 0        # far corner, same hue


def test_circle_clipped_at_the_image_edge(service):
    """An AOI centred in the corner must not raise or write out of bounds."""
    hues = np.full((12, 12), 60)
    img = bgr_image(hues)
    mask = np.zeros((12, 12), np.uint8)
    aois = [{'center': (0, 0), 'radius': 4, 'detected_pixels': [(0, 0)]}]

    result = service.apply_hue_expansion(img, mask, aois, 5)

    assert result[0, 0] == 255
    assert result[0, 4] == 255
    assert result[0, 5] == 0
    assert result.shape == mask.shape


def test_circle_centred_outside_the_image_still_expands_its_visible_part(service):
    hues = np.full((12, 12), 60)
    img = bgr_image(hues)
    mask = np.zeros((12, 12), np.uint8)
    # centre off the left edge, radius reaches back into the image
    aois = [{'center': (-2, 5), 'radius': 4, 'detected_pixels': [(1, 5)]}]

    result = service.apply_hue_expansion(img, mask, aois, 5)

    assert result[5, 0] == 255
    assert result[5, 2] == 255       # dx = 4, dx^2 == radius^2, so on the edge
    assert result[5, 3] == 0         # dx = 5, dx^2 = 25 > 16


def test_multiple_aois_each_expand_independently(service):
    hues = np.full((21, 21), 90)
    hues[5, 5] = 30
    hues[5, 6] = 31
    hues[15, 15] = 120
    hues[15, 16] = 121
    img = bgr_image(hues)
    mask = np.zeros((21, 21), np.uint8)
    aois = [
        {'center': (5, 5), 'radius': 2, 'detected_pixels': [(5, 5)]},
        {'center': (15, 15), 'radius': 2, 'detected_pixels': [(15, 15)]},
    ]

    result = service.apply_hue_expansion(img, mask, aois, 3)

    assert result[5, 5] == 255 and result[5, 6] == 255
    assert result[15, 15] == 255 and result[15, 16] == 255


# ---------------------------------------------------------------------------
# differential: the vectorized body against the per-pixel logic it replaced
# ---------------------------------------------------------------------------

def _reference_hue_expansion(img, mask, areas_of_interest, hue_range):
    """The pre-vectorization implementation, kept as an oracle."""
    if areas_of_interest is None or len(areas_of_interest) == 0:
        return mask
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    expanded_mask = mask.copy()
    for aoi in areas_of_interest:
        detected_pixels = aoi.get('detected_pixels', [])
        if len(detected_pixels) == 0:
            continue
        hue_values = []
        for px, py in detected_pixels:
            if 0 <= py < hsv_img.shape[0] and 0 <= px < hsv_img.shape[1]:
                hue_values.append(hsv_img[py, px, 0])
        if len(hue_values) == 0:
            continue
        avg_hue = int(np.mean(hue_values))
        hue_min, hue_max = avg_hue - hue_range, avg_hue + hue_range
        roi_mask = np.zeros(mask.shape[:2], dtype=np.uint8)
        cv2.circle(roi_mask, aoi['center'], aoi['radius'], 255, -1)
        roi_y, roi_x = np.where(roi_mask == 255)
        for py, px in zip(roi_y, roi_x):
            pixel_hue = hsv_img[py, px, 0]
            if hue_min < 0:
                if pixel_hue >= (180 + hue_min) or pixel_hue <= hue_max:
                    expanded_mask[py, px] = 255
            elif hue_max >= 180:
                if pixel_hue >= hue_min or pixel_hue <= (hue_max - 180):
                    expanded_mask[py, px] = 255
            else:
                if hue_min <= pixel_hue <= hue_max:
                    expanded_mask[py, px] = 255
    return expanded_mask


def test_matches_the_pre_vectorization_implementation(service):
    """Randomized differential, weighted toward the edge cases.

    Centres are allowed off-image and detected pixels out of bounds, since
    those are the cases where a bounding-box optimization is most likely to
    diverge from a full-image circle mask.
    """
    rng = np.random.default_rng(31)

    for trial in range(120):
        height, width = int(rng.integers(12, 40)), int(rng.integers(12, 40))
        hues = rng.integers(0, 180, size=(height, width), dtype=np.uint8)
        img = bgr_image(hues)
        mask = np.where(
            rng.random((height, width)) < 0.05, 255, 0
        ).astype(np.uint8)

        aois = []
        for _ in range(int(rng.integers(1, 4))):
            aois.append({
                'center': (
                    int(rng.integers(-4, width + 4)),
                    int(rng.integers(-4, height + 4)),
                ),
                'radius': int(rng.integers(0, 12)),
                'detected_pixels': [
                    (
                        int(rng.integers(-3, width + 3)),
                        int(rng.integers(-3, height + 3)),
                    )
                    for _ in range(int(rng.integers(1, 7)))
                ],
            })
        hue_range = int(rng.integers(0, 30))

        expected = _reference_hue_expansion(img, mask, aois, hue_range)
        actual = service.apply_hue_expansion(img, mask, aois, hue_range)

        assert np.array_equal(expected, actual), f"trial {trial}: {aois}"
