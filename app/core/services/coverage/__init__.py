"""
Coverage / Probability-of-Detection (POD) module.

Per-frame POD grids (terrain visibility x canopy transmittance x GSD adequacy)
accumulated onto a mission-wide EPSG:3857 grid. See the module design spec.
"""

from .params import PodParams
from .contracts import (
    CoverageResult,
    FrameIndex,
    SKIP_HIDDEN,
    SKIP_NO_POSE,
    SKIP_PITCH_TOO_SHALLOW,
    SKIP_NO_DEM,
    SKIP_NO_DEM_AT_NADIR,
    SKIP_EMPTY_FOOTPRINT,
    SKIP_OUTSIDE_BUDGET,
    SKIP_ERROR,
    LIMIT_NO_LOOKS,
    LIMIT_TERRAIN,
    LIMIT_CANOPY,
    LIMIT_GSD,
    LIMIT_NONE,
)
from .kernel import (
    build_camera_rotation,
    project_footprint_corners,
    compute_frame_spec,
    compute_target_mask_and_gsd,
    frame_pod_kernel,
)
from .accumulator import MissionAccumulator
from .colormap import pod_to_rgba, look_count_to_rgba
from .writers import (
    write_pod_geotiff,
    write_looks_geotiff,
    compute_gap_polygons,
    write_gaps_geojson,
    build_stats,
    write_all_outputs,
)
from .CoveragePodService import CoveragePodService
from .CoverageResultCache import CoverageResultCache
from .aoi import (
    estimate_download_aoi,
    compute_mission_gps_bounds,
    suggest_buffer_m,
    pad_bounds,
)

__all__ = [
    'PodParams',
    'CoverageResult',
    'FrameIndex',
    'SKIP_HIDDEN',
    'SKIP_NO_POSE',
    'SKIP_PITCH_TOO_SHALLOW',
    'SKIP_NO_DEM',
    'SKIP_NO_DEM_AT_NADIR',
    'SKIP_EMPTY_FOOTPRINT',
    'SKIP_OUTSIDE_BUDGET',
    'SKIP_ERROR',
    'LIMIT_NO_LOOKS',
    'LIMIT_TERRAIN',
    'LIMIT_CANOPY',
    'LIMIT_GSD',
    'LIMIT_NONE',
    'build_camera_rotation',
    'project_footprint_corners',
    'compute_frame_spec',
    'compute_target_mask_and_gsd',
    'frame_pod_kernel',
    'MissionAccumulator',
    'pod_to_rgba',
    'look_count_to_rgba',
    'write_pod_geotiff',
    'write_looks_geotiff',
    'compute_gap_polygons',
    'write_gaps_geojson',
    'build_stats',
    'write_all_outputs',
    'CoveragePodService',
    'CoverageResultCache',
    'estimate_download_aoi',
    'compute_mission_gps_bounds',
    'suggest_buffer_m',
    'pad_bounds',
]
