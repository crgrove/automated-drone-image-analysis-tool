"""Tests for the Web Mercator grid contracts and lattice helpers (grid.py)."""

import math

import numpy as np
import pytest

pytest.importorskip("affine")

from core.services.terrain.grid import (  # noqa: E402
    GridSpec,
    GridSample,
    make_lattice_spec,
    spec_for_bounds_wgs84,
    integer_offset,
    lonlat_to_mercator,
    mercator_to_lonlat,
    mercator_units_per_meter,
    WEB_MERCATOR_CRS,
)
from affine import Affine  # noqa: E402


def test_mercator_roundtrip():
    for lon, lat in [(-120.5, 38.7), (0.0, 0.0), (11.25, 43.77), (-150.0, 61.2)]:
        x, y = lonlat_to_mercator(lon, lat)
        lon2, lat2 = mercator_to_lonlat(x, y)
        assert lon2 == pytest.approx(lon, abs=1e-7)
        assert lat2 == pytest.approx(lat, abs=1e-7)


def test_units_per_meter_equator_is_one():
    assert mercator_units_per_meter(0.0) == pytest.approx(1.0)
    # At 60N the inflation factor is 1/cos(60) = 2.
    assert mercator_units_per_meter(60.0) == pytest.approx(2.0, rel=1e-6)


def test_make_lattice_spec_snaps_outward_and_aligns():
    cell = 3.0
    # Bounds not aligned to the lattice.
    spec = make_lattice_spec((10.4, 20.1, 40.9, 55.2), cell)
    minx, miny, maxx, maxy = spec.bounds
    # Edges are integer multiples of the cell size from origin.
    for edge in (minx, maxx, miny, maxy):
        assert edge / cell == pytest.approx(round(edge / cell), abs=1e-9)
    # Snapped outward: contains the original bounds.
    assert minx <= 10.4 and miny <= 20.1
    assert maxx >= 40.9 and maxy >= 55.2
    assert spec.cell_size == pytest.approx(cell)
    assert spec.transform.e == pytest.approx(-cell)


def test_cell_centers_and_world_to_index_are_inverse():
    spec = make_lattice_spec((0.0, 0.0, 30.0, 30.0), 3.0)
    xs, ys = spec.cell_centers()
    assert xs.shape == (spec.width,)
    assert ys.shape == (spec.height,)
    # The center of cell (i, j) must map back to fractional index (i, j).
    rows, cols = spec.world_to_index(xs[2], ys[4])
    assert float(cols) == pytest.approx(2.0, abs=1e-9)
    assert float(rows) == pytest.approx(4.0, abs=1e-9)


def test_integer_offset_roundtrip():
    parent = make_lattice_spec((0.0, 0.0, 300.0, 300.0), 3.0)
    # A child snapped from a sub-window shares the lattice.
    child = make_lattice_spec((30.0, 60.0, 90.0, 120.0), 3.0)
    row_off, col_off = integer_offset(child, parent)
    assert isinstance(row_off, int) and isinstance(col_off, int)
    # child minx=30 -> col 10; child top(maxy) vs parent top -> row offset.
    assert col_off == 10
    # parent top = 300, child top = 120 -> (300-120)/3 = 60
    assert row_off == 60


def test_integer_offset_rejects_cell_mismatch():
    parent = make_lattice_spec((0.0, 0.0, 300.0, 300.0), 3.0)
    child = make_lattice_spec((0.0, 0.0, 300.0, 300.0), 1.0)
    with pytest.raises(ValueError):
        integer_offset(child, parent)


def test_two_specs_same_cell_are_coregistered():
    a = spec_for_bounds_wgs84((-120.60, 38.60, -120.40, 38.75), 3.0)
    # A different but overlapping bbox at the same target resolution -> same cell,
    # so integer_offset must succeed (this is the accumulation invariant).
    b_cell = a.cell_size
    minx, miny, maxx, maxy = a.bounds
    child = make_lattice_spec((minx + 30 * b_cell, miny + 15 * b_cell,
                               minx + 60 * b_cell, miny + 45 * b_cell), b_cell)
    row_off, col_off = integer_offset(child, a)
    assert col_off == 30
    assert row_off == a.height - 45  # top-anchored


def test_spec_for_bounds_wgs84_is_3857_and_ground_scaled():
    spec = spec_for_bounds_wgs84((-120.5, 38.7, -120.4, 38.75), 3.0)
    assert spec.crs == WEB_MERCATOR_CRS
    mid_lat = (38.7 + 38.75) / 2
    # cell in 3857 units ~= resolution_m / cos(lat)
    assert spec.cell_size == pytest.approx(3.0 * mercator_units_per_meter(mid_lat), rel=1e-6)
    # wgs84_bounds round-trips to contain the request.
    lo, la, hi, ha = spec.wgs84_bounds()
    assert lo <= -120.5 and hi >= -120.4
    assert la <= 38.7 and ha >= 38.75


def test_grid_sample_bilinear():
    spec = make_lattice_spec((0.0, 0.0, 30.0, 30.0), 3.0)
    # A ramp increasing to the east; value == x-index.
    data = np.tile(np.arange(spec.width, dtype=np.float32), (spec.height, 1))
    sample = GridSample(data=data, transform=spec.transform, crs=spec.crs,
                        datum_note="test")
    xs, ys = spec.cell_centers()
    # At cell-center of column 3 the value is exactly 3.
    v = sample.sample_bilinear(float(xs[3]), float(ys[2]))
    assert v == pytest.approx(3.0, abs=1e-6)
    # Halfway between column 3 and 4 centers -> 3.5.
    v2 = sample.sample_bilinear(float((xs[3] + xs[4]) / 2), float(ys[2]))
    assert v2 == pytest.approx(3.5, abs=1e-6)


def test_grid_sample_bilinear_out_of_bounds_and_nan():
    spec = make_lattice_spec((0.0, 0.0, 30.0, 30.0), 3.0)
    data = np.zeros((spec.height, spec.width), dtype=np.float32)
    data[0, 0] = np.nan
    sample = GridSample(data=data, transform=spec.transform, crs=spec.crs,
                        datum_note="test")
    # Far outside the grid.
    assert sample.sample_bilinear(10_000.0, 10_000.0) is None
    xs, ys = spec.cell_centers()
    # A cell touching the NaN corner returns None.
    assert sample.sample_bilinear(float(xs[0]), float(ys[0])) is None


def test_wgs84_bounds_rejects_non_3857():
    spec = GridSpec(crs="EPSG:4326", transform=Affine(1, 0, 0, 0, -1, 1),
                    width=1, height=1)
    with pytest.raises(ValueError):
        spec.wgs84_bounds()


def test_make_lattice_spec_rejects_zero_cell_size():
    with pytest.raises(ValueError):
        make_lattice_spec((0.0, 0.0, 30.0, 30.0), 0.0)


def test_make_lattice_spec_rejects_negative_cell_size():
    with pytest.raises(ValueError):
        make_lattice_spec((0.0, 0.0, 30.0, 30.0), -3.0)


def test_make_lattice_spec_rejects_degenerate_bounds_x():
    # maxx < minx is degenerate.
    with pytest.raises(ValueError):
        make_lattice_spec((40.0, 0.0, 10.0, 30.0), 3.0)


def test_make_lattice_spec_rejects_degenerate_bounds_y():
    # maxy < miny is degenerate.
    with pytest.raises(ValueError):
        make_lattice_spec((0.0, 55.0, 30.0, 20.0), 3.0)


def test_make_lattice_spec_allows_zero_extent_bounds():
    # maxx == minx and maxy == miny is NOT degenerate (only strict < is);
    # the helper always yields at least a 1x1 grid.
    spec = make_lattice_spec((30.0, 30.0, 30.0, 30.0), 3.0)
    assert spec.width >= 1
    assert spec.height >= 1
