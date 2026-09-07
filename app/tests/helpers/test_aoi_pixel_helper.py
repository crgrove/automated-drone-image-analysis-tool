"""Tests for AOIPixelHelper.

The helper replaced six independently vectorized copies of the same two
operations. These tests pin the behaviour all six had to agree on, and in
particular the two places the copies did *not* agree: what happens to ragged
``detected_pixels``, and whether the analytic circle matches the drawn one.
"""

import cv2
import numpy as np
import pytest

from helpers.AOIPixelHelper import CircleBox, circle_box, in_bounds_coordinates


# ---------------------------------------------------------------------------
# in_bounds_coordinates - well-formed input
# ---------------------------------------------------------------------------

def test_returns_xs_then_ys_for_indexing_rows_by_ys():
    """(x, y) pairs come back as x-first arrays that index as [ys, xs]."""
    img = np.arange(20).reshape(4, 5)
    xs, ys = in_bounds_coordinates([(3, 1), (0, 2)], img.shape)

    assert xs.tolist() == [3, 0]
    assert ys.tolist() == [1, 2]
    # the whole point of the order: this must read the intended pixels
    assert img[ys, xs].tolist() == [img[1, 3], img[2, 0]]


def test_drops_out_of_bounds_and_keeps_the_rest():
    xs, ys = in_bounds_coordinates(
        [(-1, 0), (0, -1), (5, 0), (0, 4), (2, 2)], (4, 5)
    )
    assert xs.tolist() == [2]
    assert ys.tolist() == [2]


def test_bounds_are_checked_against_the_right_axes():
    """x is compared to width (shape[1]) and y to height (shape[0])."""
    # in a 2-row, 9-column array, (8, 1) is inside but (1, 8) is not
    xs, ys = in_bounds_coordinates([(8, 1), (1, 8)], (2, 9))
    assert list(zip(xs.tolist(), ys.tolist())) == [(8, 1)]


@pytest.mark.parametrize("detected_pixels", [None, [], ()])
def test_empty_input_yields_none(detected_pixels):
    assert in_bounds_coordinates(detected_pixels, (5, 5)) == (None, None)


def test_all_out_of_bounds_yields_none():
    assert in_bounds_coordinates([(99, 99), (-5, -5)], (5, 5)) == (None, None)


def test_extra_columns_are_ignored():
    """A pixel carrying more than (x, y) keeps working - only [:2] is read."""
    xs, ys = in_bounds_coordinates([(1, 2, 999), (3, 0, 7)], (5, 5))
    assert xs.tolist() == [1, 3]
    assert ys.tolist() == [2, 0]


def test_shape_with_channels_reads_only_height_and_width():
    xs, ys = in_bounds_coordinates([(2, 1)], (4, 5, 3))
    assert (xs.tolist(), ys.tolist()) == ([2], [1])


# ---------------------------------------------------------------------------
# in_bounds_coordinates - coordinate coercion
# ---------------------------------------------------------------------------

def test_float_coordinates_truncate_toward_zero_like_int():
    """Matches the ``int(pixel[0])`` the per-pixel loops used."""
    xs, ys = in_bounds_coordinates([(1.9, 2.9)], (5, 5))
    assert (xs.tolist(), ys.tolist()) == ([1], [2])


def test_string_coordinates_are_accepted():
    """ADIAT_Data.xml round-trips through literal_eval; be forgiving."""
    xs, ys = in_bounds_coordinates([("1", "2")], (5, 5))
    assert (xs.tolist(), ys.tolist()) == ([1], [2])


# ---------------------------------------------------------------------------
# in_bounds_coordinates - the ragged path (CLAUDE.md 2.5)
# ---------------------------------------------------------------------------

def test_ragged_pixels_are_salvaged_not_raised():
    """np.asarray raises on inhomogeneous input; the loops it replaced did not.

    A malformed row must cost its own row, not the whole image.
    """
    ragged = [(1, 2), (3, 4, 5), (7, 8)]

    # confirm the premise: the vectorized fast path really does raise here
    with pytest.raises(ValueError):
        np.asarray(ragged, dtype=np.int64)

    xs, ys = in_bounds_coordinates(ragged, (50, 50))
    assert xs.tolist() == [1, 3, 7]
    assert ys.tolist() == [2, 4, 8]


def test_ragged_path_matches_a_per_pixel_loop_exactly():
    entries = [(1, 2), (3, 4, 5), "zz", None, (7, 8), [9, 10, 11], np.array([2, 3])]

    expected_x, expected_y = [], []
    for pixel in entries:
        try:
            x, y = int(pixel[0]), int(pixel[1])
        except (TypeError, ValueError, IndexError, KeyError):
            continue
        if 0 <= x < 50 and 0 <= y < 50:
            expected_x.append(x)
            expected_y.append(y)

    xs, ys = in_bounds_coordinates(entries, (50, 50))
    assert xs.tolist() == expected_x
    assert ys.tolist() == expected_y


def test_unusable_entries_only_yields_none():
    assert in_bounds_coordinates(["a", None, 3], (5, 5)) == (None, None)


def test_flat_sequence_is_not_read_as_pairs():
    """[1, 2, 3, 4] is not two pixels - refuse rather than guess."""
    assert in_bounds_coordinates([1, 2, 3, 4], (5, 5)) == (None, None)


# ---------------------------------------------------------------------------
# in_bounds_coordinates - scale factor
# ---------------------------------------------------------------------------

def test_scale_factor_of_one_is_a_no_op():
    xs, ys = in_bounds_coordinates([(4, 3)], (10, 10), scale_factor=1.0)
    assert (xs.tolist(), ys.tolist()) == ([4], [3])


def test_scale_factor_multiplies_then_truncates():
    """Order matters: multiply, then truncate - as the loops did."""
    xs, ys = in_bounds_coordinates([(7, 5)], (10, 10), scale_factor=0.5)
    assert (xs.tolist(), ys.tolist()) == ([3], [2])  # int(3.5), int(2.5)


def test_scale_factor_applies_before_the_bounds_check():
    """A coordinate outside the target becomes inside it once scaled down."""
    # (18, 18) is outside a 10x10 array, but 18 * 0.25 = 4 is inside
    xs, ys = in_bounds_coordinates([(18, 18)], (10, 10), scale_factor=0.25)
    assert (xs.tolist(), ys.tolist()) == ([4], [4])


def test_scale_factor_matches_the_loop_it_replaced_over_many_inputs():
    rng = np.random.default_rng(4)
    height, width = 40, 50
    for _ in range(300):
        scale = float(rng.choice([1.0, 0.5, 0.25, 1.0 / 3.0, 0.7]))
        pixels = [
            (int(rng.integers(-5, 200)), int(rng.integers(-5, 200)))
            for _ in range(int(rng.integers(1, 8)))
        ]

        expected = []
        for pixel in pixels:
            x_orig, y_orig = int(pixel[0]), int(pixel[1])
            if scale != 1.0:
                x, y = int(x_orig * scale), int(y_orig * scale)
            else:
                x, y = x_orig, y_orig
            if 0 <= y < height and 0 <= x < width:
                expected.append((x, y))

        xs, ys = in_bounds_coordinates(pixels, (height, width), scale_factor=scale)
        got = [] if xs is None else list(zip(xs.tolist(), ys.tolist()))
        assert got == expected, (pixels, scale)


# ---------------------------------------------------------------------------
# circle_box
# ---------------------------------------------------------------------------

def test_circle_box_returns_slices_and_a_box_sized_mask():
    box = circle_box((5, 6), 2, (20, 20))

    assert isinstance(box, CircleBox)
    assert box.y_slice == slice(4, 9)
    assert box.x_slice == slice(3, 8)
    # mask covers the bounding box only, not the whole image
    assert box.inside.shape == (5, 5)


def test_circle_box_mask_is_the_analytic_disc():
    box = circle_box((2, 2), 1, (5, 5))
    assert box.inside.tolist() == [
        [False, True, False],
        [True, True, True],
        [False, True, False],
    ]


def test_circle_box_matches_cv2_filled_circle():
    """The analytic disc is not an approximation of the drawn one."""
    rng = np.random.default_rng(9)
    for _ in range(200):
        height, width = int(rng.integers(5, 60)), int(rng.integers(5, 60))
        cx, cy = int(rng.integers(-8, width + 8)), int(rng.integers(-8, height + 8))
        radius = int(rng.integers(0, 18))

        drawn = np.zeros((height, width), np.uint8)
        cv2.circle(drawn, (cx, cy), radius, 255, -1)

        analytic = np.zeros((height, width), bool)
        box = circle_box((cx, cy), radius, (height, width))
        if box is not None:
            analytic[box.y_slice, box.x_slice] |= box.inside

        assert np.array_equal(drawn == 255, analytic), (height, width, cx, cy, radius)


def test_circle_box_clips_to_the_array():
    box = circle_box((0, 0), 5, (10, 10))
    assert box.y_slice == slice(0, 6)
    assert box.x_slice == slice(0, 6)
    assert box.inside.shape == (6, 6)


def test_circle_box_writes_through_the_slices():
    """Chained indexing through a basic slice is a view, so this must stick."""
    target = np.zeros((10, 10), np.uint8)
    box = circle_box((5, 5), 2, target.shape)
    target[box.y_slice, box.x_slice][box.inside] = 255

    assert target[5, 5] == 255
    assert target[5, 3] == 255
    assert target[3, 3] == 0  # corner of the box, outside the disc


def test_circle_box_radius_zero_is_a_single_pixel():
    box = circle_box((4, 4), 0, (10, 10))
    assert box.inside.shape == (1, 1)
    assert bool(box.inside[0, 0]) is True


@pytest.mark.parametrize("center,radius", [((99, 99), 2), ((-9, -9), 3)])
def test_circle_box_entirely_outside_yields_none(center, radius):
    assert circle_box(center, radius, (10, 10)) is None


def test_circle_box_negative_radius_yields_none():
    assert circle_box((5, 5), -1, (10, 10)) is None


@pytest.mark.parametrize("center,radius", [(None, 3), ((5, 5), None), ("xx", 3)])
def test_circle_box_rejects_unusable_geometry(center, radius):
    assert circle_box(center, radius, (10, 10)) is None


def test_circle_box_coerces_a_float_centre():
    """A float centre must not become a float slice (TypeError on index)."""
    box = circle_box((2.7, 2.2), 1, (10, 10))
    assert box.y_slice == slice(1, 4)
    assert box.x_slice == slice(1, 4)
