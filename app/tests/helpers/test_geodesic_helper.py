"""Direct unit tests for GeodesicHelper (bearing / circular geometry)."""

import pytest

from helpers.GeodesicHelper import GeodesicHelper as G


def test_circular_mean_empty_and_wraparound():
    assert G.circular_mean([]) == 0.0
    assert G.circular_mean([350.0, 10.0]) == pytest.approx(0.0, abs=1e-6)


def test_circular_median_empty_single_small_and_large():
    assert G.circular_median([]) == 0.0
    assert G.circular_median([405.0]) == pytest.approx(45.0)
    assert G.circular_median([10.0, 20.0, 30.0]) == pytest.approx(20.0)
    # len > 5 uses the normalized-candidate branch
    median = G.circular_median([10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
    assert 10.0 <= median <= 60.0


@pytest.mark.parametrize(
    "angle, expected",
    [(-90.0, 270.0), (360.0, 0.0), (725.0, 5.0)],
)
def test_normalize_angle_deg(angle, expected):
    assert G.normalize_angle_deg(angle) == pytest.approx(expected)


def test_angle_difference_deg_wraparound():
    assert G.angle_difference_deg(350.0, 10.0) == pytest.approx(20.0)
    assert G.angle_difference_deg(10.0, 350.0) == pytest.approx(-20.0)


def test_point_to_segment_distance_degenerate_and_normal():
    # Identical endpoints → distance to that point
    d0 = G.point_to_segment_distance(30.001, -97.0, 30.0, -97.0, 30.0, -97.0)
    assert d0 == pytest.approx(G.haversine_distance(30.001, -97.0, 30.0, -97.0), rel=0.05)

    # Point near midpoint of a short N–S segment
    d = G.point_to_segment_distance(30.005, -97.001, 30.0, -97.0, 30.01, -97.0)
    assert d > 0.0


def test_smooth_bearings_circular_short_even_window_and_savgol():
    short = [1.0, 2.0, 3.0]
    out = G.smooth_bearings_circular(short, window=5)
    assert out == short
    assert out is not short

    long_flat = [10.0] * 7
    even = G.smooth_bearings_circular(long_flat, window=4, use_savgol=False)
    assert len(even) == 7
    assert all(0.0 <= b < 360.0 for b in even)

    no_sg = G.smooth_bearings_circular(long_flat, window=5, use_savgol=False)
    assert len(no_sg) == 7

    wrap = [350.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    with_sg = G.smooth_bearings_circular(wrap, window=5, use_savgol=True)
    assert len(with_sg) == len(wrap)
    assert all(0.0 <= b < 360.0 for b in with_sg)


def test_unwrap_angles_empty_single_and_crossing():
    assert G.unwrap_angles([]) == []
    assert G.unwrap_angles([45.0]) == [45.0]

    unwrapped = G.unwrap_angles([350.0, 10.0, 20.0])
    assert unwrapped[0] == pytest.approx(350.0)
    assert unwrapped[1] == pytest.approx(370.0)
    assert unwrapped[2] == pytest.approx(380.0)
    assert unwrapped[1] > unwrapped[0]
    assert unwrapped[2] > unwrapped[1]
