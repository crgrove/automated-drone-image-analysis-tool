"""Unit tests for core.services.PersonModel."""

import pytest

from core.services.PersonModel import (
    build_footprint_points,
    build_points,
    build_sitting_points,
    build_standing_points,
)


def test_standing_points_span_full_height():
    points = build_standing_points(1.8)
    zs = [p[2] for p in points]
    assert min(zs) == pytest.approx(0.0, abs=1e-9)
    assert max(zs) == pytest.approx(1.8, abs=1e-6)


def test_standing_points_shoulder_width():
    points = build_standing_points(1.8)
    max_half_width = max(abs(p[0]) for p in points)
    assert max_half_width == pytest.approx(0.130 * 1.8, rel=0.01)


def test_sitting_is_shorter_than_standing():
    standing = build_standing_points(1.8)
    sitting = build_sitting_points(1.8)
    assert max(p[2] for p in sitting) < max(p[2] for p in standing)
    assert min(p[2] for p in sitting) == pytest.approx(0.0, abs=1e-9)


def test_build_points_dispatch():
    assert build_points(1.8, "standing") == build_standing_points(1.8)
    assert build_points(1.8, "sitting") == build_sitting_points(1.8)
    with pytest.raises(ValueError):
        build_points(1.8, "recumbent")


def test_points_are_nonempty_3d_tuples():
    for pose in ("standing", "sitting"):
        points = build_points(1.8, pose)
        assert len(points) > 20
        assert all(len(p) == 3 for p in points)


def test_footprint_points_are_flat():
    """The overhead footprint has no vertical extent (all z == 0)."""
    for pose in ("standing", "sitting"):
        points = build_footprint_points(1.8, pose)
        assert points, "footprint must not be empty"
        assert all(p[2] == pytest.approx(0.0, abs=1e-9) for p in points)


def test_footprint_width_matches_standing_shoulders():
    """Standing footprint spans the shoulder ellipse, not the full height."""
    points = build_footprint_points(1.8, "standing")
    max_half_width = max(abs(p[0]) for p in points)
    assert max_half_width == pytest.approx(0.130 * 1.8, rel=0.01)


def test_footprint_rejects_recumbent():
    with pytest.raises(ValueError):
        build_footprint_points(1.8, "recumbent")
