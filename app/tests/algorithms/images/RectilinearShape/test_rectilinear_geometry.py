"""Tests for the pure geometry behind the Rectilinear Shape detector.

Every fixture is synthesised with numpy/cv2, so the expected values follow
from the construction: a square's two edge families are equal (C2 -> 0), a
1.5:1 rectangle leaves C2 = (L - W) / (L + W) = 0.2, and a single straight
edge is one family (C2 -> 1).
"""

import math

import cv2
import numpy as np
import pytest

from algorithms.Shared.services import RectilinearGeometry as geometry
from algorithms.Shared.services.RectilinearGeometry import RotRect


def _frame(length, width, angle_deg, size=200, inside=180, outside=100):
    """A flat frame holding one anti-aliased filled rectangle at its centre."""
    img = np.full((size, size), outside, np.uint8)
    corners = cv2.boxPoints(((size / 2, size / 2), (length, width), angle_deg))
    cv2.fillPoly(img, [np.rint(corners * 16).astype(np.int32)], inside, lineType=cv2.LINE_AA, shift=4)
    return cv2.GaussianBlur(img, (0, 0), 0.8)


def _centre_boxiness(img, window_px):
    mag, ang = geometry.compute_gradients(img)
    boxiness, c4, c2, theta, _ = geometry.boxiness_map(mag, ang, window_px, 0.05, 1)
    centre = img.shape[0] // 2
    return boxiness[centre, centre], c4[centre, centre], c2[centre, centre], theta[centre, centre]


# --- boxiness_map -----------------------------------------------------------

@pytest.mark.parametrize('angle', [0, 20, 30, 45, 70])
def test_a_square_is_maximally_boxy(angle):
    boxiness, c4, c2, _ = _centre_boxiness(_frame(40, 40, angle), 50)
    assert boxiness > 0.9
    assert c2 < 0.05


@pytest.mark.parametrize('angle', [0, 30, 45])
def test_a_one_and_a_half_to_one_rectangle_scores_about_point_eight(angle):
    boxiness, c4, c2, _ = _centre_boxiness(_frame(60, 40, angle), 75)
    assert c2 == pytest.approx(0.2, abs=0.03)
    assert boxiness == pytest.approx(0.8 * c4, abs=0.02)
    assert 0.7 < boxiness < 0.85


@pytest.mark.parametrize('angle', [0, 25, 60])
def test_the_dominant_orientation_follows_the_rectangle(angle):
    _, _, _, theta = _centre_boxiness(_frame(60, 40, angle), 75)
    offset = abs(((theta - angle) + 45.0) % 90.0 - 45.0)
    assert offset < 2.0


def test_a_single_straight_edge_is_not_boxy():
    img = np.full((200, 200), 100, np.uint8)
    cv2.line(img, (0, 40), (200, 160), 180, 6)
    mag, ang = geometry.compute_gradients(cv2.GaussianBlur(img, (0, 0), 0.8))
    boxiness = geometry.boxiness_map(mag, ang, 75, 0.05, 1)[0]
    assert boxiness.max() < 0.1


@pytest.mark.parametrize('sigma', [3, 10, 25])
def test_isotropic_noise_is_not_boxy(sigma):
    rng = np.random.default_rng(1)
    img = np.clip(rng.normal(110, sigma, (300, 300)), 0, 255).astype(np.uint8)
    mag, ang = geometry.compute_gradients(cv2.GaussianBlur(img, (0, 0), 0.8))
    floor = max(0.05, 0.05 * float(np.median(mag)))
    boxiness = geometry.boxiness_map(geometry.boxiness_weights(mag), ang, 75, floor, 1)[0]
    assert float(np.percentile(boxiness, 99)) < 0.2


def test_a_flat_frame_has_no_boxiness():
    img = np.full((120, 120), 90, np.uint8)
    mag, ang = geometry.compute_gradients(img)
    boxiness = geometry.boxiness_map(mag, ang, 40, 0.05, 1)[0]
    assert not boxiness.any()


def test_decimation_shrinks_the_grid_but_keeps_the_answer():
    img = _frame(60, 40, 30)
    mag, ang = geometry.compute_gradients(img)
    full = geometry.boxiness_map(mag, ang, 75, 0.05, 1)[0]
    reduced = geometry.boxiness_map(mag, ang, 75, 0.05, 4)[0]
    assert reduced.shape == (50, 50)
    assert reduced[25, 25] == pytest.approx(full[100, 100], abs=0.05)


def test_boxiness_weights_remove_the_noise_floor():
    mag = np.array([[1.0, 1.0, 1.0, 10.0]], np.float32)
    weights = geometry.boxiness_weights(mag)
    assert weights.tolist() == [[0.0, 0.0, 0.0, 8.0]]


# --- size_score ---------------------------------------------------------------

RANGES = (35.0, 80.0, 20.0, 55.0)


@pytest.mark.parametrize('length, width', [(35, 20), (60, 40), (80, 55)])
def test_size_inside_the_range_scores_one(length, width):
    assert geometry.size_score(length, width, RANGES, 0.2) == 1.0


def test_size_decay_is_symmetric_in_log_ratio():
    """Too large by a factor k must score the same as too small by 1/k."""
    too_large = geometry.size_score(80.0 * 1.3, 40.0, RANGES, 0.2)
    too_small = geometry.size_score(35.0 / 1.3, 40.0, RANGES, 0.2)
    assert too_large == pytest.approx(too_small)
    assert 0.0 < too_large < 1.0


def test_size_score_falls_with_distance():
    near = geometry.size_score(90.0, 40.0, RANGES, 0.2)
    far = geometry.size_score(140.0, 40.0, RANGES, 0.2)
    assert near > far
    assert far < 0.01


def test_a_wider_tolerance_decays_more_slowly():
    assert geometry.size_score(100.0, 40.0, RANGES, 0.4) > geometry.size_score(100.0, 40.0, RANGES, 0.2)


def test_a_degenerate_size_scores_zero():
    assert geometry.size_score(0.0, 40.0, RANGES, 0.2) == 0.0


# --- rotated_nms --------------------------------------------------------------

def test_duplicates_collapse_to_the_highest_score():
    rects = [
        RotRect(100, 100, 60, 40, 10),
        RotRect(102, 101, 58, 41, 12),
        RotRect(99, 98, 61, 39, 8),
    ]
    assert geometry.rotated_nms(rects, [60.0, 80.0, 70.0], 0.3) == [1]


def test_separate_objects_both_survive():
    rects = [RotRect(100, 100, 60, 40, 0), RotRect(200, 100, 60, 40, 0)]
    assert sorted(geometry.rotated_nms(rects, [50.0, 60.0], 0.3)) == [0, 1]


def test_kept_indices_are_highest_score_first():
    rects = [RotRect(100, 100, 60, 40, 0), RotRect(300, 100, 60, 40, 0), RotRect(500, 100, 60, 40, 0)]
    assert geometry.rotated_nms(rects, [10.0, 30.0, 20.0], 0.3) == [1, 2, 0]


# --- segments and hypotheses --------------------------------------------------

def test_detect_segments_on_a_blank_frame_is_empty_not_none():
    segments = geometry.detect_segments(np.full((100, 100), 128, np.uint8), 5, 200, 10.0)
    assert isinstance(segments, np.ndarray)
    assert segments.shape == (0, 4)


def test_detect_segments_finds_the_sides_of_a_rectangle():
    segments = geometry.detect_segments(_frame(60, 40, 0), 10, 100, 10.0)
    lengths = sorted(np.hypot(segments[:, 2] - segments[:, 0], segments[:, 3] - segments[:, 1]))
    assert len(segments) >= 4
    assert lengths[-1] == pytest.approx(60, abs=6)


def test_detect_segments_drops_low_contrast_edges():
    faint = _frame(60, 40, 0, inside=106, outside=100)
    assert len(geometry.detect_segments(faint, 10, 100, 10.0)) == 0


def test_the_segment_hash_finds_neighbours_across_a_cell_boundary():
    segments = np.array([[95, 50, 99, 50], [101, 50, 105, 50], [400, 400, 404, 400]], np.float32)
    segment_hash = geometry.build_segment_hash(segments, 100)
    found = segment_hash.query(97, 50, 10)
    assert 0 in found and 1 in found
    assert 2 not in found


def _assert_near(rect, cx, cy, length, width, angle):
    assert math.hypot(rect.cx - cx, rect.cy - cy) < 3.0
    assert rect.length == pytest.approx(length, abs=4)
    assert rect.width == pytest.approx(width, abs=4)
    offset = abs(((rect.angle_deg - angle) + 90.0) % 180.0 - 90.0)
    assert offset < 3.0


def test_two_perpendicular_sides_imply_the_whole_rectangle():
    # The bottom and left sides of a 60 x 40 rectangle centred on (100, 100).
    segments = np.array([[70, 120, 130, 120], [70, 120, 70, 80]], np.float32)
    rects = geometry.corner_hypotheses(segments, geometry.build_segment_hash(segments, 100), 12.0, 4.0, 100)
    assert len(rects) == 1
    _assert_near(rects[0], 100, 100, 60, 40, 0)


def test_segments_that_do_not_meet_form_no_corner():
    segments = np.array([[70, 120, 130, 120], [70, 100, 70, 60]], np.float32)
    rects = geometry.corner_hypotheses(segments, geometry.build_segment_hash(segments, 100), 12.0, 4.0, 100)
    assert rects == []


def test_two_parallel_sides_imply_the_whole_rectangle():
    segments = np.array([[70, 80, 130, 80], [70, 120, 130, 120]], np.float32)
    rects = geometry.parallel_hypotheses(segments, geometry.build_segment_hash(segments, 100), 12.0, (16, 96), 100)
    assert len(rects) == 1
    _assert_near(rects[0], 100, 100, 60, 40, 0)


def test_parallels_outside_the_separation_range_are_ignored():
    segments = np.array([[70, 80, 130, 80], [70, 90, 130, 90]], np.float32)
    rects = geometry.parallel_hypotheses(segments, geometry.build_segment_hash(segments, 100), 12.0, (16, 96), 100)
    assert rects == []


def test_a_fragmented_side_also_yields_the_union_hypothesis():
    """One side broken by LSD: the overlap closes short, the union closes true."""
    segments = np.array([[70, 80, 130, 80], [70, 120, 105, 120]], np.float32)
    rects = geometry.parallel_hypotheses(segments, geometry.build_segment_hash(segments, 100), 12.0, (16, 96), 100)
    assert len(rects) == 2
    assert max(r.length for r in rects) == pytest.approx(60, abs=1)


def test_boxiness_hypotheses_fit_a_rectangle_without_segments():
    img = _frame(60, 40, 30)
    mag, ang = geometry.compute_gradients(img)
    boxiness, _, _, theta, _ = geometry.boxiness_map(mag, ang, 75, 0.05, 2)
    rects = geometry.boxiness_hypotheses(boxiness, theta, mag, ang, 0.35, 20, 75, 2, 12.0)
    assert rects
    best = min(rects, key=lambda r: math.hypot(r.cx - 100, r.cy - 100))
    _assert_near(best, 100, 100, 60, 40, 30)


def test_boxiness_peaks_inside_a_line_hypothesis_are_skipped():
    img = _frame(60, 40, 30)
    mag, ang = geometry.compute_gradients(img)
    boxiness, _, _, theta, _ = geometry.boxiness_map(mag, ang, 75, 0.05, 2)
    covering = [RotRect(100, 100, 60, 40, 30)]
    rects = geometry.boxiness_hypotheses(boxiness, theta, mag, ang, 0.35, 20, 75, 2, 12.0, existing=covering)
    assert all(math.hypot(r.cx - 100, r.cy - 100) > 10 for r in rects)


# --- scoring terms ------------------------------------------------------------

def test_edge_support_is_high_on_the_true_outline_and_low_off_it():
    img = _frame(60, 40, 20)
    mag, ang = geometry.compute_gradients(img)
    on_target = geometry.edge_support(RotRect(100, 100, 60, 40, 20), mag, ang, 12.0, 5.0)
    rotated_wrong = geometry.edge_support(RotRect(100, 100, 60, 40, 65), mag, ang, 12.0, 5.0)
    elsewhere = geometry.edge_support(RotRect(40, 40, 60, 40, 20), mag, ang, 12.0, 5.0)
    assert on_target > 0.9
    assert rotated_wrong < 0.3
    assert elsewhere == 0.0


def test_ring_contrast_measures_the_step_in_delta_e():
    grey = cv2.cvtColor(_frame(60, 40, 0, inside=180, outside=100), cv2.COLOR_GRAY2BGR)
    lab = cv2.cvtColor(grey, cv2.COLOR_BGR2LAB)
    delta_e = geometry.ring_contrast_lab(lab, RotRect(100, 100, 60, 40, 0), 0.3)
    expected = (lab[100, 100, 0] - lab[5, 5, 0]) * 100.0 / 255.0
    assert delta_e == pytest.approx(expected, abs=1.0)


def test_ring_contrast_is_zero_on_a_flat_frame():
    lab = cv2.cvtColor(np.full((120, 120, 3), 90, np.uint8), cv2.COLOR_BGR2LAB)
    assert geometry.ring_contrast_lab(lab, RotRect(60, 60, 40, 30, 15), 0.3) == 0.0
