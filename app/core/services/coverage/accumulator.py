"""
MissionAccumulator - combine per-frame POD grids onto a mission-wide grid.

Holds one running-max POD grid per angular bin (looks from the same view
direction do not compound), a uint16 look-count, a coarse frame index, and a
best-look limiting-factor grid. The mission grid grows lazily on the shared
EPSG:3857 lattice (frames are integer-offset co-registered), clamped by a memory
budget. ``finalize`` combines the bins:

    POD = C * (1 - prod_b (1 - bin_b))

The mission grid is snapped to a coarse ``cell_size * frame_index_block`` lattice
so growth always shifts the origin by whole frame-index blocks, keeping the
coarse frame index exactly re-keyable.
"""

import math

import numpy as np

from core.services.LoggerService import LoggerService
from core.services.terrain.grid import (
    GridSpec,
    make_lattice_spec,
    integer_offset,
    WEB_MERCATOR_CRS,
)
from core.services.coverage.contracts import FrameIndex, LIMIT_NO_LOOKS

# float32 bins (n) + uint16 look + uint8 factor + float32 best_pod per cell.
_BYTES_PER_CELL_BASE = 2 + 1 + 4  # look + factor + best_pod


class MissionAccumulator:
    def __init__(self, cell_size_3857: float, params, logger=None):
        self.cell_size = float(cell_size_3857)
        self.params = params
        self.logger = logger or LoggerService()
        self.n_bins = int(params.angle_bins)
        self.block = int(params.frame_index_block)
        self._spec = None
        self._bins = None          # (n_bins, H, W) float32
        self._look = None          # (H, W) uint16
        self._best_pod = None      # (H, W) float32
        self._best_factor = None   # (H, W) uint8
        self._frame_index = FrameIndex(self.block, params.frame_index_max_per_block)

    @staticmethod
    def bin_for_frame(yaw_deg: float, pitch_deg: float, params) -> int:
        """Angular bin: 4 azimuth quadrants x {nadir, oblique}."""
        off_nadir = 90.0 + pitch_deg              # 0 at nadir (pitch -90)
        ring = 0 if off_nadir <= params.nadir_split_deg else 1
        quad = int((((yaw_deg % 360.0) + 45.0) % 360.0) // 90.0)
        return ring * 4 + quad

    def _bytes_per_cell(self) -> int:
        return self.n_bins * 4 + _BYTES_PER_CELL_BASE

    def _budget_ok(self, spec: GridSpec) -> bool:
        need = spec.width * spec.height * self._bytes_per_cell()
        return need <= self.params.mem_budget_mb * 1_000_000

    def _snap_mission(self, bounds) -> GridSpec:
        """Snap bounds outward to the coarse cell*block lattice, as a cell-sized spec."""
        coarse = self.cell_size * self.block
        minx, miny, maxx, maxy = bounds
        left = math.floor(minx / coarse) * coarse
        right = math.ceil(maxx / coarse) * coarse
        bottom = math.floor(miny / coarse) * coarse
        top = math.ceil(maxy / coarse) * coarse
        return make_lattice_spec((left, bottom, right, top), self.cell_size,
                                 crs=WEB_MERCATOR_CRS)

    def _allocate(self, spec: GridSpec):
        H, W = spec.height, spec.width
        self._spec = spec
        self._bins = np.zeros((self.n_bins, H, W), dtype=np.float32)
        self._look = np.zeros((H, W), dtype=np.uint16)
        self._best_pod = np.zeros((H, W), dtype=np.float32)
        self._best_factor = np.zeros((H, W), dtype=np.uint8)

    def _contains(self, frame_spec: GridSpec) -> bool:
        try:
            r0, c0 = integer_offset(frame_spec, self._spec)
        except ValueError:
            return False
        return (r0 >= 0 and c0 >= 0
                and r0 + frame_spec.height <= self._spec.height
                and c0 + frame_spec.width <= self._spec.width)

    def _grow_to_union(self, frame_spec: GridSpec) -> bool:
        """Grow to cover ``frame_spec`` (+ a one-frame margin in each growing
        direction). Returns False if that would exceed the memory budget."""
        ominx, ominy, omaxx, omaxy = self._spec.bounds
        fminx, fminy, fmaxx, fmaxy = frame_spec.bounds
        mx = fmaxx - fminx
        my = fmaxy - fminy
        new_minx = min(ominx, fminx - mx)
        new_miny = min(ominy, fminy - my)
        new_maxx = max(omaxx, fmaxx + mx)
        new_maxy = max(omaxy, fmaxy + my)
        new_spec = self._snap_mission((new_minx, new_miny, new_maxx, new_maxy))
        if not self._budget_ok(new_spec):
            self.logger.warning(
                f"MissionAccumulator: growth to {new_spec.width}x{new_spec.height} "
                f"exceeds {self.params.mem_budget_mb} MB budget; frame skipped."
            )
            return False

        r0, c0 = integer_offset(self._spec, new_spec)  # block-aligned by construction
        H, W = new_spec.height, new_spec.width
        oh, ow = self._spec.height, self._spec.width

        bins = np.zeros((self.n_bins, H, W), dtype=np.float32)
        look = np.zeros((H, W), dtype=np.uint16)
        best_pod = np.zeros((H, W), dtype=np.float32)
        best_factor = np.zeros((H, W), dtype=np.uint8)
        bins[:, r0:r0 + oh, c0:c0 + ow] = self._bins
        look[r0:r0 + oh, c0:c0 + ow] = self._look
        best_pod[r0:r0 + oh, c0:c0 + ow] = self._best_pod
        best_factor[r0:r0 + oh, c0:c0 + ow] = self._best_factor

        # r0/c0 are whole blocks (coarse-lattice mission origins), so the coarse
        # frame index re-keys by an exact block shift.
        self._frame_index.shift_origin(r0 // self.block, c0 // self.block)

        self._spec = new_spec
        self._bins = bins
        self._look = look
        self._best_pod = best_pod
        self._best_factor = best_factor
        return True

    def add_frame(self, frame_idx: int, frame_pod: np.ndarray, frame_spec: GridSpec,
                  yaw_deg: float, pitch_deg: float, bearing_confidence: float,
                  frame_factor=None) -> bool:
        """Apply per-frame policy (cap + low-confidence haircut) and accumulate.

        Returns False when the frame falls outside the memory-budget-clamped grid.
        """
        capped = np.minimum(frame_pod, self.params.pod_frame_cap)
        if bearing_confidence < 0.5:
            capped = capped * self.params.low_confidence_haircut

        if self._spec is None:
            self._allocate(self._snap_mission(frame_spec.bounds))
        if not self._contains(frame_spec):
            if not self._grow_to_union(frame_spec):
                return False

        r0, c0 = integer_offset(frame_spec, self._spec)
        h, w = frame_pod.shape
        b = self.bin_for_frame(yaw_deg, pitch_deg, self.params)

        bin_view = self._bins[b, r0:r0 + h, c0:c0 + w]
        np.maximum(bin_view, capped, out=bin_view)

        pos = frame_pod > 0
        look_view = self._look[r0:r0 + h, c0:c0 + w]
        look_view[pos] += 1

        best_view = self._best_pod[r0:r0 + h, c0:c0 + w]
        better = capped > best_view
        best_view[better] = capped[better]
        if frame_factor is not None:
            fac_view = self._best_factor[r0:r0 + h, c0:c0 + w]
            fac_view[better] = frame_factor[better]

        self._frame_index.add(frame_idx, r0, c0, pos)
        return True

    def finalize(self):
        """Combine bins into the mission POD product.

        Returns (pod float32, look_count uint16, limiting_factor uint8,
        frame_index, transform). Empty 0x0 arrays if nothing accumulated.
        """
        if self._spec is None:
            from affine import Affine
            empty = np.zeros((0, 0), dtype=np.float32)
            return (empty, empty.astype(np.uint16), empty.astype(np.uint8),
                    self._frame_index, Affine.identity())

        acc = np.ones(self._bins.shape[1:], dtype=np.float64)
        for b in range(self.n_bins):
            acc *= (1.0 - self._bins[b])
        pod = (self.params.common_mode_ceiling * (1.0 - acc)).astype(np.float32)

        limiting = self._best_factor.copy()
        limiting[self._look == 0] = LIMIT_NO_LOOKS

        return pod, self._look, limiting, self._frame_index, self._spec.transform
