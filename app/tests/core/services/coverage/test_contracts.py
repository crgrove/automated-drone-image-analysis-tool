"""Tests for FrameIndex and CoverageResult.sample."""

import numpy as np
import pytest

pytest.importorskip("pyproj")

from core.services.coverage.contracts import (
    FrameIndex,
    CoverageResult,
    LIMIT_CANOPY,
)
from core.services.terrain.grid import make_lattice_spec, lonlat_to_mercator, mercator_to_lonlat


def test_frame_index_add_and_query():
    fi = FrameIndex(block_cells=4, max_per_block=8)
    mask = np.zeros((8, 8), dtype=bool)
    mask[0, 0] = True     # block (0,0)
    mask[5, 6] = True     # block (1,1)
    fi.add(frame_idx=3, row0=0, col0=0, any_pod_mask=mask)
    assert fi.frames_at(0, 0) == [3]
    assert fi.frames_at(5, 6) == [3]
    # (2,2) shares block (0,0) with cell (0,0), so it reports the same frame.
    assert fi.frames_at(2, 2) == [3]
    # A block with no contributing cells is empty.
    assert fi.frames_at(3, 7) == []  # block (0,1): no True cells there


def test_frame_index_cap_and_dedup():
    fi = FrameIndex(block_cells=4, max_per_block=2)
    m = np.ones((1, 1), dtype=bool)
    for f in (1, 1, 2, 3):
        fi.add(f, 0, 0, m)
    assert fi.frames_at(0, 0) == [1, 2]  # deduped, capped at 2


def test_frame_index_shift_origin():
    fi = FrameIndex(block_cells=4, max_per_block=8)
    fi.add(7, 0, 0, np.ones((1, 1), dtype=bool))
    fi.shift_origin(1, 2)   # blocks move by (+1 row block, +2 col blocks)
    assert fi.frames_at(0, 0) == []
    assert fi.frames_at(4, 8) == [7]


def test_coverage_result_sample():
    # Small EPSG:3857 grid near the Sierra foothills.
    minx, miny = lonlat_to_mercator(-120.50, 38.70)
    maxx, maxy = lonlat_to_mercator(-120.48, 38.72)
    spec = make_lattice_spec((minx, miny, maxx, maxy), 30.0)
    H, W = spec.height, spec.width
    pod = np.zeros((H, W), dtype=np.float32)
    look = np.zeros((H, W), dtype=np.uint16)
    lf = np.zeros((H, W), dtype=np.uint8)
    # Mark a known interior cell.
    ri, ci = H // 2, W // 2
    pod[ri, ci] = 0.63
    look[ri, ci] = 4
    lf[ri, ci] = LIMIT_CANOPY
    fi = FrameIndex(block_cells=4, max_per_block=8)
    fi.add(11, ri, ci, np.ones((1, 1), dtype=bool))

    result = CoverageResult(
        pod=pod, look_count=look, transform=spec.transform, image_count=1,
        skipped=[], stats={}, gap_polygons=[], cancelled=False,
        limiting_factor=lf, frame_index=fi,
    )

    xs, ys = spec.cell_centers()
    lon, lat = mercator_to_lonlat(float(xs[ci]), float(ys[ri]))
    s = result.sample(lat, lon)
    assert s is not None
    assert s['pod'] == pytest.approx(0.63, abs=1e-4)
    assert s['looks'] == 4
    assert s['limiting_factor'] == LIMIT_CANOPY
    assert s['frames'] == [11]


def test_coverage_result_sample_out_of_grid():
    minx, miny = lonlat_to_mercator(-120.50, 38.70)
    maxx, maxy = lonlat_to_mercator(-120.48, 38.72)
    spec = make_lattice_spec((minx, miny, maxx, maxy), 30.0)
    pod = np.zeros((spec.height, spec.width), dtype=np.float32)
    result = CoverageResult(
        pod=pod, look_count=np.zeros_like(pod, dtype=np.uint16),
        transform=spec.transform, image_count=0, skipped=[], stats={},
        gap_polygons=[], cancelled=False,
    )
    assert result.sample(10.0, 10.0) is None
