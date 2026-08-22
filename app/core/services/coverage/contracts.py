"""
Coverage/POD result contracts: CoverageResult, FrameIndex, and stable
skip-reason / limiting-factor constants.

Pure data + numpy/pyproj/affine only (service layer — no Qt). The mission raster
and its metadata cross the worker->GUI boundary as a single ``CoverageResult``.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

# --- skip-reason keys (stable; recorded in stats.json/logs, translated at display) ---
SKIP_HIDDEN = "hidden"
SKIP_NO_POSE = "no_pose"                 # missing GPS / intrinsics / AGL
SKIP_PITCH_TOO_SHALLOW = "pitch_too_shallow"
SKIP_NO_DEM = "no_dem"                   # no DEM coverage for the footprint
SKIP_NO_DEM_AT_NADIR = "no_dem_at_nadir"
SKIP_EMPTY_FOOTPRINT = "empty_footprint"
SKIP_OUTSIDE_BUDGET = "outside_mission_grid_budget"
SKIP_ERROR = "error"

# --- limiting-factor codes (uint8 grid produced by the accumulator) ---
LIMIT_NO_LOOKS = 0    # never seen -> fly it
LIMIT_TERRAIN = 1     # hard occlusion dominated
LIMIT_CANOPY = 2      # canopy transmittance dominated
LIMIT_GSD = 3         # resolution/adequacy dominated
LIMIT_NONE = 4        # near cap; nothing actionable


class FrameIndex:
    """Coarse per-cell contributing-frame index.

    Buckets ``block_cells x block_cells`` blocks of the mission grid to a list of
    contributing frame ids (positions in the ``images`` list == viewer indices),
    capped at ``max_per_block``. Memory is O(covered blocks), not O(cells).
    """

    def __init__(self, block_cells: int, max_per_block: int):
        self.block_cells = int(block_cells)
        self.max_per_block = int(max_per_block)
        self._blocks = {}  # (block_row, block_col) -> list[int]

    def _add_to_block(self, frame_idx: int, br: int, bc: int):
        lst = self._blocks.get((br, bc))
        if lst is None:
            self._blocks[(br, bc)] = [frame_idx]
            return
        if frame_idx not in lst and len(lst) < self.max_per_block:
            lst.append(frame_idx)

    def add(self, frame_idx: int, row0: int, col0: int, any_pod_mask: np.ndarray):
        """Record ``frame_idx`` for every block touched by ``any_pod_mask``.

        ``row0``/``col0`` are the mission-grid indices of ``any_pod_mask[0, 0]``.
        """
        ys, xs = np.nonzero(any_pod_mask)
        if ys.size == 0:
            return
        brs = (row0 + ys) // self.block_cells
        bcs = (col0 + xs) // self.block_cells
        for br, bc in set(zip(brs.tolist(), bcs.tolist())):
            self._add_to_block(frame_idx, int(br), int(bc))

    def shift_origin(self, row_delta_blocks: int, col_delta_blocks: int):
        """Re-key all blocks after the mission grid grows (origin moves)."""
        if not (row_delta_blocks or col_delta_blocks):
            return
        self._blocks = {
            (br + row_delta_blocks, bc + col_delta_blocks): v
            for (br, bc), v in self._blocks.items()
        }

    def frames_at(self, row: int, col: int) -> List[int]:
        block = (int(row) // self.block_cells, int(col) // self.block_cells)
        return sorted(self._blocks.get(block, []))


@dataclass
class CoverageResult:
    """Mission-wide POD product (spec section 3.4 + additive UI fields)."""

    pod: np.ndarray                        # float32 (rows, cols) 0-1; 0 where look_count == 0
    look_count: np.ndarray                 # uint16
    transform: object                      # affine.Affine, EPSG:3857 (b=d=0, a=-e)
    image_count: int
    skipped: List[Tuple[str, str]]         # (image_name, reason_key)
    stats: dict
    gap_polygons: list                     # shapely Polygons, EPSG:3857
    cancelled: bool
    crs: str = "EPSG:3857"
    limiting_factor: Optional[np.ndarray] = None    # uint8, same shape as pod
    frame_index: Optional[FrameIndex] = None
    params: object = None
    # Frames whose DEM came from the online Terrarium fallback because the
    # configured local tiles had no coverage there (0 when N/A).
    dem_fallback_frames: int = 0
    # Fraction (0-1) of the searched footprint cells the configured canopy
    # source actually covered; None when no canopy source was configured.
    # Ground the canopy tiles didn't reach is treated as bare (no attenuation),
    # so a value < 1 means POD is optimistic over that fraction.
    canopy_coverage_fraction: Optional[float] = None
    # Processed frames whose footprint the canopy tiles did not cover at all.
    canopy_frames_missing: int = 0
    # Identity of each input frame, indexed by frame id (== the position of the
    # image in the list passed to calculate()). Lets consumers resolve a
    # FrameIndex id back to an image without assuming any particular ordering
    # of the caller's own image list. Each entry: {'path', 'name'}.
    frame_sources: Optional[List[dict]] = None
    # Processed-frame counts by camera-elevation source: 'anchor' (mission
    # takeoff elevation + reported AGL, correct across relief), 'agl_nadir'
    # (fallback DEM(nadir) + reported AGL, correct only where the ground under
    # the drone is at takeoff elevation), 'agl_override' (explicit user or
    # flight-log AGL). None when the calculation produced no frames.
    altitude_source_counts: Optional[dict] = None
    # Mission takeoff elevation in the DEM's datum, or None when none could be
    # validated (``altitude_anchor_reason`` says why - see
    # ``CoveragePodService._resolve_altitude_anchor``).
    altitude_anchor_m: Optional[float] = None
    altitude_anchor_reason: Optional[str] = None
    _transformer: object = field(default=None, repr=False, compare=False)

    def sample(self, lat: float, lon: float) -> Optional[dict]:
        """Return {'pod', 'looks', 'limiting_factor', 'frames'} at a WGS84 point.

        Returns None when the point lies outside the mission grid.
        """
        if self._transformer is None:
            from pyproj import Transformer
            self._transformer = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
        x, y = self._transformer.transform(lon, lat)
        col, row = (~self.transform) * (x, y)
        r, c = int(row), int(col)
        if not (0 <= r < self.pod.shape[0] and 0 <= c < self.pod.shape[1]):
            return None
        frames = self.frame_index.frames_at(r, c) if self.frame_index is not None else []
        lf = int(self.limiting_factor[r, c]) if self.limiting_factor is not None else LIMIT_NO_LOOKS
        return {
            "pod": float(self.pod[r, c]),
            "looks": int(self.look_count[r, c]),
            "limiting_factor": lf,
            "frames": frames,
        }
