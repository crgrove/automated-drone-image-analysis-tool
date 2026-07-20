"""
CoveragePodService - orchestrate the per-frame POD pipeline onto a mission grid.

For each image: collect FrameGeometry, sample the DEM (and canopy) to the frame's
lattice-snapped EPSG:3857 grid, resolve camera elevation by the datum rule
(DEM(nadir) + AGL), ray-march the per-frame POD, and accumulate. Finalize
combines angular bins, polygonizes coverage gaps, and assembles stats.

Return conventions mirror ``CoverageExtentService.calculate_coverage_extents``
(progress_callback(current, total, message), cancel_check() -> bool, a
``cancelled`` result) so the existing coordinator-worker/export wiring carries
over unchanged.
"""

import math
import time
from typing import Any, Dict, List, Optional

import numpy as np

from core.services.LoggerService import LoggerService
from core.services.image.ImageService import ImageService
from core.services.terrain.grid import lonlat_to_mercator, mercator_units_per_meter
from core.services.coverage.params import PodParams
from core.services.coverage.accumulator import MissionAccumulator
from core.services.coverage.kernel import compute_frame_spec, compute_target_mask_and_gsd, frame_pod_kernel
from core.services.coverage.writers import compute_gap_polygons, build_stats
from core.services.coverage.contracts import (
    CoverageResult,
    SKIP_HIDDEN,
    SKIP_NO_POSE,
    SKIP_PITCH_TOO_SHALLOW,
    SKIP_NO_DEM,
    SKIP_NO_DEM_AT_NADIR,
    SKIP_EMPTY_FOOTPRINT,
    SKIP_OUTSIDE_BUDGET,
    SKIP_ERROR,
)

_DUMMY_IMG = np.zeros((1, 1, 3), dtype=np.uint8)
_FINALIZE_TICKS = 2


class CoveragePodService:
    def __init__(self, terrain, canopy=None, params: Optional[PodParams] = None,
                 custom_altitude_ft: Optional[float] = None,
                 logger: Optional[LoggerService] = None):
        self.terrain = terrain
        self.canopy = canopy
        self.params = params or PodParams()
        self.custom_altitude_ft = custom_altitude_ft
        self.logger = logger or LoggerService()

    def calculate(self, images: List[Dict[str, Any]], progress_callback=None,
                  cancel_check=None) -> CoverageResult:
        total = len(images)
        skipped = []
        accumulator = None
        cam_points = []
        meters_per_unit = 1.0
        cell_size_3857 = self.params.grid_res_m
        processed = 0
        dem_fallback = 0
        # Canopy coverage of the searched footprints (only meaningful when a
        # canopy source is configured). Cells are counted per frame, so the
        # ratio is look-weighted (areas searched by more frames count more).
        canopy_searched = 0
        canopy_covered_cells = 0
        canopy_frames_missing = 0
        timings = {'geom': 0.0, 'dem': 0.0, 'canopy': 0.0, 'kernel': 0.0}
        # Frame-id -> image identity, so the result can resolve FrameIndex ids
        # back to images regardless of the caller's list ordering. Indexed by
        # the same enumerate() position used as the frame id below.
        frame_sources = [
            {'path': im.get('path', ''), 'name': im.get('name', str(i))}
            for i, im in enumerate(images)
        ]

        for idx, image in enumerate(images):
            if cancel_check and cancel_check():
                return self._cancelled_result(processed, skipped)
            if progress_callback:
                name = image.get('name', f"Image {idx + 1}")
                progress_callback(idx, total + _FINALIZE_TICKS,
                                  f"Calculating POD for {name}...")

            name = image.get('name', str(idx))
            if image.get('hidden', False):
                skipped.append((name, SKIP_HIDDEN))
                continue

            try:
                t0 = time.perf_counter()
                fg = self._frame_geometry(image)
                t_geom = time.perf_counter() - t0
                if fg is None:
                    skipped.append((name, SKIP_NO_POSE))
                    continue
                if fg.pitch_deg > self.params.min_pitch_deg:
                    skipped.append((name, SKIP_PITCH_TOO_SHALLOW))
                    continue

                if accumulator is None:
                    meters_per_unit = math.cos(math.radians(fg.lat))
                    cell_size_3857 = self.params.grid_res_m * mercator_units_per_meter(fg.lat)
                    accumulator = MissionAccumulator(cell_size_3857, self.params, self.logger)

                spec = compute_frame_spec(fg, self.params, cell_size_3857)
                t0 = time.perf_counter()
                dem_sample = self.terrain.sample_grid_spec(spec)
                t_dem = time.perf_counter() - t0
                if dem_sample is None:
                    skipped.append((name, SKIP_NO_DEM))
                    continue
                if getattr(dem_sample, 'source', None) == 'terrarium_fallback':
                    dem_fallback += 1
                dem = dem_sample.data

                cam_x, cam_y = lonlat_to_mercator(fg.lon, fg.lat)
                nadir_elev = dem_sample.sample_bilinear(cam_x, cam_y)
                if nadir_elev is None or math.isnan(nadir_elev):
                    finite = dem[np.isfinite(dem)]
                    if finite.size == 0:
                        skipped.append((name, SKIP_NO_DEM_AT_NADIR))
                        continue
                    nadir_elev = float(np.median(finite))
                cam_z = nadir_elev + fg.agl_m
                fg.cam_elev_m = cam_z
                cam_xyz = (cam_x, cam_y, cam_z)

                t0 = time.perf_counter()
                mask, gsd = compute_target_mask_and_gsd(
                    dem, spec, fg, cam_xyz, self.params, meters_per_unit)
                if not mask.any():
                    skipped.append((name, SKIP_EMPTY_FOOTPRINT))
                    continue

                # Sample canopy only for frames that actually search cells, and
                # measure how much of THIS frame's searched footprint the canopy
                # tiles covered — cells with no canopy data get no attenuation
                # (transmittance 1), silently overstating POD there.
                t0c = time.perf_counter()
                chm, cover, canopy_covered = self._sample_canopy(spec)
                t_canopy = time.perf_counter() - t0c
                if self.canopy is not None:
                    searched = int(mask.sum())
                    canopy_searched += searched
                    if canopy_covered is not None:
                        with_canopy = int(np.count_nonzero(mask & canopy_covered))
                    else:
                        with_canopy = 0
                    canopy_covered_cells += with_canopy
                    if with_canopy == 0:
                        canopy_frames_missing += 1

                pod, factor = frame_pod_kernel(
                    dem, chm, cover, spec.transform, cam_xyz, mask, gsd,
                    self.params, meters_per_unit=meters_per_unit, return_factors=True)
                # t0 was set before the mask; exclude the separately-timed canopy.
                t_kernel = time.perf_counter() - t0 - t_canopy

                placed = accumulator.add_frame(
                    idx, pod, spec, fg.yaw_deg, fg.pitch_deg, fg.bearing_confidence,
                    frame_factor=factor)
                if not placed:
                    skipped.append((name, SKIP_OUTSIDE_BUDGET))
                    continue

                cam_points.append((cam_x, cam_y))
                processed += 1

                timings['geom'] += t_geom
                timings['dem'] += t_dem
                timings['canopy'] += t_canopy
                timings['kernel'] += t_kernel
                if processed <= 3 or processed % 25 == 0:
                    self.logger.info(
                        f"POD frame '{name}' ({dem.shape[1]}x{dem.shape[0]} cells): "
                        f"geom={t_geom * 1000:.0f}ms dem={t_dem * 1000:.0f}ms "
                        f"canopy={t_canopy * 1000:.0f}ms kernel={t_kernel * 1000:.0f}ms")
            except Exception as e:
                self.logger.error(f"POD frame '{name}' failed: {e}")
                skipped.append((name, SKIP_ERROR))

        if processed:
            self.logger.info(
                f"POD timing totals over {processed} frames: "
                f"geom={timings['geom']:.1f}s dem={timings['dem']:.1f}s "
                f"canopy={timings['canopy']:.1f}s kernel={timings['kernel']:.1f}s")

        if accumulator is None:
            return self._empty_result(processed, skipped)

        if progress_callback:
            progress_callback(total, total + _FINALIZE_TICKS,
                              "Combining looks across angles...")
        pod, look_count, limiting, frame_index, transform = accumulator.finalize()
        if cancel_check and cancel_check():
            return self._cancelled_result(processed, skipped)

        if progress_callback:
            progress_callback(total + 1, total + _FINALIZE_TICKS,
                              "Finding coverage gaps...")
        hull = self._flight_hull(cam_points)
        gaps = compute_gap_polygons(pod, look_count, transform, hull,
                                    self.params.gap_threshold)
        stats = build_stats(
            pod, look_count, transform, skipped, gaps, self.params,
            canopy_source=self._canopy_source_name(),
            terrain_info=self._terrain_info(),
            generated_at=self._now_iso())
        stats['dem_fallback_frames'] = dem_fallback
        if dem_fallback:
            self.logger.info(
                f"POD: {dem_fallback} frame(s) outside the local DEM used the "
                "online elevation fallback.")

        # Canopy coverage of the searched area (only when a source is configured).
        canopy_fraction = None
        if self.canopy is not None and canopy_searched > 0:
            canopy_fraction = canopy_covered_cells / canopy_searched
            stats['canopy_coverage'] = {
                'fraction': canopy_fraction,
                'frames_missing': canopy_frames_missing,
                'frames_total': processed,
            }
            if canopy_fraction < 0.999:
                self.logger.info(
                    f"POD: canopy data covered {canopy_fraction * 100:.0f}% of the "
                    f"searched area ({canopy_frames_missing} frame(s) had none); "
                    "uncovered ground was treated as bare (no attenuation).")

        return CoverageResult(
            pod=pod, look_count=look_count, transform=transform,
            image_count=processed, skipped=skipped, stats=stats,
            gap_polygons=gaps, cancelled=False, limiting_factor=limiting,
            frame_index=frame_index, params=self.params,
            dem_fallback_frames=dem_fallback, frame_sources=frame_sources,
            canopy_coverage_fraction=canopy_fraction,
            canopy_frames_missing=canopy_frames_missing)

    # ---- helpers ----

    def _frame_geometry(self, image):
        path = image.get('path', '')
        if not path:
            return None
        # Read metadata cheaply: piexif for EXIF and the direct byte-parser for
        # XMP, so we never spawn one ExifTool process per image (the dominant
        # per-frame cost over a large mission).
        from helpers.MetaDataHelper import MetaDataHelper
        from helpers.LocationInfo import LocationInfo
        exif_data = MetaDataHelper.get_exif_data_piexif(path)
        fg = self._build_frame_geometry(image, path, exif_data,
                                        MetaDataHelper.get_xmp_data_direct(path))
        # Safety net: if the fast XMP parse missed pose/AGL for a GPS-tagged image,
        # retry that one image with the full (ExifTool) reader before giving up.
        if fg is None and LocationInfo.get_gps(exif_data=exif_data):
            fg = self._build_frame_geometry(image, path, exif_data,
                                            MetaDataHelper.get_xmp_data_merged(path))
        return fg

    def _build_frame_geometry(self, image, path, exif_data, xmp_data):
        svc = ImageService(path, image.get('mask_path', ''),
                           img_array=_DUMMY_IMG,
                           calculated_bearing=image.get('bearing'),
                           exif_data=exif_data, xmp_data=xmp_data)
        # Drop the dummy pixels so FrameGeometry reads image size from EXIF
        # (frames never need the decoded pixels -> skip the 20 MP decode cost).
        svc.img_array = None
        return svc.get_frame_geometry(
            custom_altitude_ft=self.custom_altitude_ft,
            bearing_quality=image.get('bearing_quality'),
            agl_override_ft=image.get('wingtra_agl_ft'))

    def _sample_canopy(self, spec):
        """(chm, cover, covered) for the frame grid. ``covered`` is a bool grid
        marking cells the canopy tiles actually provided data for (None when no
        canopy is configured or nothing covered the footprint)."""
        if self.canopy is None:
            return None, None, None
        try:
            sample = self.canopy.sample_grid_spec(spec)
        except Exception as e:
            self.logger.warning(f"Canopy sample failed: {e}")
            return None, None, None
        if sample is None:
            return None, None, None
        return (getattr(sample, 'chm', None), getattr(sample, 'cover', None),
                getattr(sample, 'covered', None))

    def _flight_hull(self, cam_points):
        if len(cam_points) < 3:
            return None
        try:
            from shapely.geometry import MultiPoint
            return MultiPoint(cam_points).convex_hull
        except Exception:
            return None

    def _canopy_source_name(self):
        if self.canopy is None:
            return "none"
        return getattr(self.canopy, 'source_name', 'canopy')

    def _terrain_info(self):
        try:
            return self.terrain.provider.get_datum_info()
        except Exception:
            return {}

    @staticmethod
    def _now_iso():
        import datetime
        return datetime.datetime.now().isoformat(timespec="seconds")

    def _empty_result(self, processed, skipped):
        from affine import Affine
        empty = np.zeros((0, 0), dtype=np.float32)
        return CoverageResult(
            pod=empty, look_count=empty.astype(np.uint16), transform=Affine.identity(),
            image_count=processed, skipped=skipped,
            stats={"skipped_counts": self._reason_counts(skipped)},
            gap_polygons=[], cancelled=False, params=self.params)

    def _cancelled_result(self, processed, skipped):
        from affine import Affine
        empty = np.zeros((0, 0), dtype=np.float32)
        return CoverageResult(
            pod=empty, look_count=empty.astype(np.uint16), transform=Affine.identity(),
            image_count=processed, skipped=skipped, stats={}, gap_polygons=[],
            cancelled=True, params=self.params)

    @staticmethod
    def _reason_counts(skipped):
        counts = {}
        for _, r in skipped:
            counts[r] = counts.get(r, 0) + 1
        return counts
