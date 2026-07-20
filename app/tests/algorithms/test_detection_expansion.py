"""Unit tests for the DetectionExpansion pure-math helpers."""

import numpy as np
import pytest

from algorithms.DetectionExpansion import (
    DEFAULT_HUE_EXPANSION,
    DEFAULT_HUE_EXPANSION_SAT_FLOOR_PCT,
    DEFAULT_HUE_EXPANSION_VAL_FLOOR_PCT,
    DEFAULT_THRESHOLD_EXPANSION,
    HUE_MAX,
    circular_mean_hue,
    compute_safety_cap,
    convex_hull_area_from_mask,
    expand_hue_flood,
    expand_threshold_mrmap,
    hue_distance_mask,
)


# ---------------------------------------------------------------------------
# circular_mean_hue
# ---------------------------------------------------------------------------

def test_circular_mean_hue_empty_returns_none():
    assert circular_mean_hue([]) is None


def test_circular_mean_hue_single_value():
    result = circular_mean_hue([45.0])
    assert result == pytest.approx(45.0, abs=0.5)


def test_circular_mean_hue_simple_average():
    result = circular_mean_hue([30, 40])
    assert result == pytest.approx(35.0, abs=0.5)


def test_circular_mean_hue_handles_wraparound():
    # Mean of 175 and 5 (both near 0/180 boundary) should be ~0, not ~90
    result = circular_mean_hue([175, 5])
    assert (result <= 2.0) or (result >= 178.0)


def test_circular_mean_hue_uniform_range():
    result = circular_mean_hue([80, 90, 100])
    assert result == pytest.approx(90.0, abs=1.0)


# ---------------------------------------------------------------------------
# hue_distance_mask
# ---------------------------------------------------------------------------

def test_hue_distance_mask_matches_center():
    hsv = np.zeros((10, 10, 3), dtype=np.uint8)
    hsv[:, :, 0] = 90  # all pixels hue=90
    mask = hue_distance_mask(hsv, mean_hue=90, hue_expansion=5)
    assert mask.all()


def test_hue_distance_mask_rejects_far_hues():
    hsv = np.zeros((10, 10, 3), dtype=np.uint8)
    hsv[:, :, 0] = 90
    mask = hue_distance_mask(hsv, mean_hue=30, hue_expansion=5)
    assert not mask.any()


def test_hue_distance_mask_circular_distance():
    # hue=175 should match mean_hue=5 with expansion=10 (circular distance = 10)
    hsv = np.zeros((5, 5, 3), dtype=np.uint8)
    hsv[:, :, 0] = 175
    mask = hue_distance_mask(hsv, mean_hue=5, hue_expansion=10)
    assert mask.all()


def test_hue_distance_mask_saturation_floor():
    hsv = np.zeros((5, 5, 3), dtype=np.uint8)
    hsv[:, :, 0] = 90
    hsv[:, :, 1] = 50  # below floor
    mask = hue_distance_mask(hsv, mean_hue=90, hue_expansion=10, sat_floor=100)
    assert not mask.any()


def test_hue_distance_mask_value_floor():
    hsv = np.zeros((5, 5, 3), dtype=np.uint8)
    hsv[:, :, 0] = 90
    hsv[:, :, 1] = 200  # above sat floor
    hsv[:, :, 2] = 50   # below value floor
    mask = hue_distance_mask(hsv, mean_hue=90, hue_expansion=10, sat_floor=100, val_floor=100)
    assert not mask.any()


# ---------------------------------------------------------------------------
# expand_threshold_mrmap
# ---------------------------------------------------------------------------

def test_expand_threshold_empty_selection_returns_empty():
    expanded = np.zeros((20, 20), dtype=bool)
    rect = [5, 5, 10, 10]
    result = expand_threshold_mrmap(expanded, rect, (20, 20))
    assert not result.any()


def test_expand_threshold_selects_within_rectangle():
    expanded = np.zeros((20, 20), dtype=bool)
    expanded[5:10, 5:10] = True
    rect = [5, 5, 9, 9]
    result = expand_threshold_mrmap(expanded, rect, (20, 20))
    assert result[5:10, 5:10].all()


def test_expand_threshold_floods_connected_outside_rect():
    expanded = np.zeros((20, 20), dtype=bool)
    # Inside rect region (Phase A)
    expanded[5:8, 5:8] = True
    # Connected extension outside rect
    expanded[5:8, 8:12] = True
    rect = [5, 5, 7, 7]
    result = expand_threshold_mrmap(expanded, rect, (20, 20))
    # All connected pixels should now be selected (8-way)
    assert result[5:8, 5:12].all()


def test_expand_threshold_ignores_disconnected_expansion():
    expanded = np.zeros((20, 20), dtype=bool)
    expanded[5:8, 5:8] = True  # Phase-A region
    # Disconnected island elsewhere
    expanded[15:18, 15:18] = True
    rect = [5, 5, 7, 7]
    result = expand_threshold_mrmap(expanded, rect, (20, 20))
    assert result[5:8, 5:8].all()
    assert not result[15:18, 15:18].any()


def test_expand_threshold_clamps_rect_to_image_bounds():
    expanded = np.ones((10, 10), dtype=bool)
    # Rect partly outside image bounds
    rect = [5, 5, 50, 50]
    result = expand_threshold_mrmap(expanded, rect, (10, 10))
    # Should produce a valid mask without error
    assert result.shape == (10, 10)


# ---------------------------------------------------------------------------
# expand_hue_flood
# ---------------------------------------------------------------------------

def test_expand_hue_flood_empty_seed():
    seed = np.zeros((10, 10), dtype=bool)
    hue_ok = np.ones((10, 10), dtype=bool)
    expanded, cap_hit = expand_hue_flood(seed, hue_ok, safety_cap=1000)
    assert not expanded.any()
    assert cap_hit is False


def test_expand_hue_flood_grows_through_hue_matches():
    seed = np.zeros((10, 10), dtype=bool)
    seed[5, 5] = True
    hue_ok = np.zeros((10, 10), dtype=bool)
    # Connected path of hue-matching pixels
    hue_ok[5, 5:8] = True
    expanded, cap_hit = expand_hue_flood(seed, hue_ok, safety_cap=1000)
    assert expanded[5, 5:8].all()
    assert cap_hit is False


def test_expand_hue_flood_caps_at_safety_limit():
    seed = np.zeros((20, 20), dtype=bool)
    seed[5, 5] = True
    hue_ok = np.ones((20, 20), dtype=bool)
    # All 400 pixels would match but cap is 10
    expanded, cap_hit = expand_hue_flood(seed, hue_ok, safety_cap=10)
    assert cap_hit is True
    # Returns original seed when cap hit
    assert np.array_equal(expanded, seed)


def test_expand_hue_flood_no_cap_when_disabled():
    seed = np.zeros((10, 10), dtype=bool)
    seed[5, 5] = True
    hue_ok = np.ones((10, 10), dtype=bool)
    expanded, cap_hit = expand_hue_flood(seed, hue_ok, safety_cap=0)
    assert cap_hit is False
    assert expanded.any()


# ---------------------------------------------------------------------------
# convex_hull_area_from_mask
# ---------------------------------------------------------------------------

def test_convex_hull_area_empty_mask():
    mask = np.zeros((10, 10), dtype=bool)
    assert convex_hull_area_from_mask(mask) == 0.0


def test_convex_hull_area_single_point():
    mask = np.zeros((10, 10), dtype=bool)
    mask[5, 5] = True
    assert convex_hull_area_from_mask(mask) == 1.0


def test_convex_hull_area_two_points():
    mask = np.zeros((10, 10), dtype=bool)
    mask[5, 5] = True
    mask[6, 6] = True
    assert convex_hull_area_from_mask(mask) == 2.0


def test_convex_hull_area_square_region():
    mask = np.zeros((20, 20), dtype=bool)
    mask[5:15, 5:15] = True  # 10x10 filled square
    # Convex hull of a 10x10 square is ~81 (depends on OpenCV's hull)
    area = convex_hull_area_from_mask(mask)
    assert area > 50
    assert area < 100


def test_convex_hull_accepts_uint8():
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[5:8, 5:8] = 255
    assert convex_hull_area_from_mask(mask) > 0


def test_convex_hull_collinear_points_fallback():
    # All pixels in a single row — hull area would be 0
    mask = np.zeros((10, 10), dtype=bool)
    mask[5, 2:8] = True
    area = convex_hull_area_from_mask(mask)
    # Fallback returns pixel count
    assert area > 0


# ---------------------------------------------------------------------------
# compute_safety_cap
# ---------------------------------------------------------------------------

def test_compute_safety_cap_applies_min_floor():
    # Tiny rectangle (1x1) — cap should still be at the min_floor
    cap = compute_safety_cap([5, 5, 5, 5], min_floor=10000, multiplier=10)
    assert cap == 10000


def test_compute_safety_cap_scales_with_rect_area():
    # Large rectangle — cap = 10 * 10000 = 100000
    cap = compute_safety_cap([0, 0, 99, 99], min_floor=10000, multiplier=10)
    assert cap == 100_000


def test_compute_safety_cap_handles_zero_width_rect():
    # xmin == xmax (zero width rect)
    cap = compute_safety_cap([5, 5, 5, 10], min_floor=100, multiplier=1)
    # rect_w clamped to 1, rect_h = 6
    assert cap >= 100


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_module_constants():
    assert HUE_MAX == 180
    assert DEFAULT_THRESHOLD_EXPANSION == 400
    assert DEFAULT_HUE_EXPANSION == 5
    assert DEFAULT_HUE_EXPANSION_SAT_FLOOR_PCT == 35
    assert DEFAULT_HUE_EXPANSION_VAL_FLOOR_PCT == 20
