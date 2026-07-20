"""Unit tests for core.services.shadow.PersonShadow."""

import math

import pytest

from core.services.shadow.PersonShadow import (
    compute_shadow_ground_points,
    shadow_length,
)


def test_shadow_length_at_45_degrees_equals_height():
    assert shadow_length(1.8, 45.0) == pytest.approx(1.8, rel=1e-6)


def test_shadow_length_grows_as_sun_lowers():
    assert shadow_length(1.8, 30.0) > shadow_length(1.8, 60.0)


def test_shadow_length_zero_when_sun_at_or_below_horizon():
    assert shadow_length(1.8, 0.0) == 0.0
    assert shadow_length(1.8, -5.0) == 0.0


def test_shadow_length_slope_shortens_uphill():
    flat = shadow_length(1.8, 45.0, slope=0.0)
    uphill = shadow_length(1.8, 45.0, slope=1.0)
    assert uphill < flat
    assert uphill == pytest.approx(0.9, rel=1e-6)


def test_shadow_falls_away_from_sun():
    """Sun in the north -> shadow extends south."""
    points = [(0.0, 0.0, 2.0)]  # one point 2 m up
    ground = compute_shadow_ground_points(
        points, foot_ned=(0.0, 0.0, 100.0),
        sun_elevation_deg=45.0, sun_azimuth_deg=0.0,
    )
    assert len(ground) == 1
    north, east, down = ground[0]
    assert north == pytest.approx(-2.0, abs=1e-6)  # 2 m south
    assert east == pytest.approx(0.0, abs=1e-6)
    assert down == pytest.approx(100.0, abs=1e-6)


def test_shadow_direction_follows_sun_azimuth():
    """Sun in the east -> shadow extends west."""
    points = [(0.0, 0.0, 2.0)]
    ground = compute_shadow_ground_points(
        points, foot_ned=(0.0, 0.0, 100.0),
        sun_elevation_deg=45.0, sun_azimuth_deg=90.0,
    )
    north, east, _ = ground[0]
    assert north == pytest.approx(0.0, abs=1e-6)
    assert east == pytest.approx(-2.0, abs=1e-6)  # 2 m west


def test_ground_point_at_feet_has_no_offset():
    points = [(0.5, -0.3, 0.0)]  # a point already on the ground
    ground = compute_shadow_ground_points(
        points, foot_ned=(10.0, 20.0, 100.0),
        sun_elevation_deg=30.0, sun_azimuth_deg=120.0,
    )
    north, east, _ = ground[0]
    assert north == pytest.approx(10.0 + (-0.3), abs=1e-6)
    assert east == pytest.approx(20.0 + 0.5, abs=1e-6)


def test_no_shadow_when_sun_below_horizon():
    points = [(0.0, 0.0, 2.0)]
    assert compute_shadow_ground_points(
        points, (0.0, 0.0, 100.0), -1.0, 0.0) == []
