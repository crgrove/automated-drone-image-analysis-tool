"""
CoveragePodService - orchestrate the per-frame POD pipeline onto a mission grid.

For each image: collect FrameGeometry, sample the DEM (and canopy) to the frame's
lattice-snapped EPSG:3857 grid, resolve the camera's true orthometric elevation
(see ``_resolve_cam_elev``), ray-march the per-frame POD, and accumulate.
Finalize combines angular bins, polygonizes coverage gaps, and assembles stats.

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

# Camera-elevation resolution (see CoveragePodService._resolve_cam_elev).
_MIN_AGL_M = 1.0                  # a camera resolved at/below ground is bad data
_AGL_RESPEC_TOL_M = 5.0           # re-size the frame grid past this AGL correction...
_AGL_RESPEC_TOL_FRAC = 0.05       # ...and past this fraction of the sizing AGL
_AGL_DISAGREE_LOG_M = 25.0        # report frames whose true height differs by this much

# Mission takeoff anchor (see CoveragePodService._resolve_altitude_anchor).
_ANCHOR_MIN_SAMPLES = 3           # below this the estimate cannot be cross-checked
_ANCHOR_SAMPLE_FRAMES = 40        # bounded pre-pass; a median over this many is plenty
_ANCHOR_MAX_MAD_M = 15.0          # spread above which the ASL/baro chains disagree


class CoveragePodService:
    def __init__(self, terrain, canopy=None, params: Optional[PodParams] = None,
                 custom_altitude_ft: Optional[float] = None,
                 logger: Optional[LoggerService] = None):
        self.terrain = terrain
        self.canopy = canopy
        self.params = params or PodParams()
        self.custom_altitude_ft = custom_altitude_ft
        self.logger = logger or LoggerService()
        self._geoid_memo = {}

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
        # Which rule supplied each processed frame's camera elevation, and how
        # many frames the terrain-aware rule moved materially (see
        # _resolve_cam_elev).
        alt_sources = {}
        agl_disagree = 0
        timings = {'geom': 0.0, 'dem': 0.0, 'canopy': 0.0, 'kernel': 0.0}
        # Frame-id -> image identity, so the result can resolve FrameIndex ids
        # back to images regardless of the caller's list ordering. Indexed by
        # the same enumerate() position used as the frame id below.
        frame_sources = [
            {'path': im.get('path', ''), 'name': im.get('name', str(i))}
            for i, im in enumerate(images)
        ]

        # Camera elevation is anchored to one mission-wide takeoff elevation, so
        # it has to be resolved (and validated) before any frame is projected.
        if progress_callback:
            progress_callback(0, total + _FINALIZE_TICKS,
                              "Resolving flight altitude datum...")
        anchor, anchor_reason = self._resolve_altitude_anchor(images)
        if anchor is not None:
            self.logger.info(
                f"POD: takeoff elevation resolved to {anchor:.0f} m; camera "
                "elevation is anchored there rather than to the ground under "
                "each frame.")

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

                agl_override = self._agl_is_override(image)
                reported_agl = fg.agl_m     # height above takeoff, or an override

                # ``compute_frame_spec`` sizes the frame grid from fg.agl_m, so it
                # needs the TRUE height above the ground below - sizing from the
                # height above takeoff truncates the real footprint. A cache-backed
                # point lookup gets that right on the first sample; without one the
                # re-sample below is the safety net.
                if anchor is not None and not agl_override:
                    nadir_pt = self._point_elevation(fg.lat, fg.lon)
                    if nadir_pt is not None:
                        fg.agl_m = max(anchor + reported_agl - nadir_pt, _MIN_AGL_M)

                cam_x, cam_y = lonlat_to_mercator(fg.lon, fg.lat)
                payload, skip_reason, t_dem = self._sample_frame_dem(
                    fg, cell_size_3857, cam_x, cam_y)
                if payload is None:
                    skipped.append((name, skip_reason))
                    continue
                spec, dem_sample, dem, nadir_elev = payload

                cam_z, alt_source = self._resolve_cam_elev(
                    nadir_elev, reported_agl, agl_override, anchor)
                alt_sources[alt_source] = alt_sources.get(alt_source, 0) + 1

                effective_agl = cam_z - nadir_elev
                if abs(effective_agl - reported_agl) > _AGL_DISAGREE_LOG_M:
                    agl_disagree += 1

                # Safety net: with no point lookup the grid was sized from the
                # reported AGL, so a material correction still needs a re-sample.
                if self._agl_differs(effective_agl, fg.agl_m):
                    fg.agl_m = effective_agl
                    payload, skip_reason, t_dem_2 = self._sample_frame_dem(
                        fg, cell_size_3857, cam_x, cam_y)
                    t_dem += t_dem_2
                    if payload is None:
                        skipped.append((name, skip_reason))
                        continue
                    # cam_z is an absolute elevation on the 'anchor' path (the only
                    # path that can trip this), so re-sampling does not move it.
                    spec, dem_sample, dem, nadir_elev = payload

                if getattr(dem_sample, 'source', None) == 'terrarium_fallback':
                    dem_fallback += 1

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

        # Where each frame's camera elevation came from (see _resolve_cam_elev).
        stats['altitude_sources'] = dict(alt_sources)
        stats['altitude_anchor'] = {'elevation_m': anchor, 'reason': anchor_reason}
        anchored = alt_sources.get('anchor', 0)
        nadir_frames = alt_sources.get('agl_nadir', 0)
        if anchored:
            self.logger.info(
                f"POD: {anchored}/{processed} frame(s) used takeoff-anchored camera "
                f"elevation; {nadir_frames} fell back to DEM(nadir)+reported AGL, "
                f"{alt_sources.get('agl_override', 0)} used an explicit AGL override.")
        elif nadir_frames:
            self.logger.warning(
                f"POD: no validated takeoff elevation ({anchor_reason}) - all "
                f"{nadir_frames} frame(s) used DEM(nadir)+reported AGL, which assumes "
                "the ground under the drone sits at takeoff elevation. POD is "
                "optimistic over ground below launch elevation and pessimistic above "
                "it.")
        if agl_disagree:
            self.logger.info(
                f"POD: {agl_disagree} frame(s) had a true height above the ground "
                f"below differing from the reported AGL by more than "
                f"{_AGL_DISAGREE_LOG_M:.0f} m (relief between takeoff and the frame).")

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
            canopy_frames_missing=canopy_frames_missing,
            altitude_source_counts=dict(alt_sources),
            altitude_anchor_m=anchor, altitude_anchor_reason=anchor_reason)

    # ---- helpers ----

    def _sample_frame_dem(self, fg, cell_size_3857, cam_x, cam_y):
        """Size the frame grid from ``fg`` and sample the DEM onto it.

        Returns ``(payload, skip_reason, elapsed_s)`` where ``payload`` is
        ``(spec, dem_sample, dem, nadir_elev)``, or ``None`` with a skip reason.
        """
        spec = compute_frame_spec(fg, self.params, cell_size_3857)
        t0 = time.perf_counter()
        dem_sample = self.terrain.sample_grid_spec(spec)
        elapsed = time.perf_counter() - t0
        if dem_sample is None:
            return None, SKIP_NO_DEM, elapsed

        dem = dem_sample.data
        nadir_elev = dem_sample.sample_bilinear(cam_x, cam_y)
        if nadir_elev is None or math.isnan(nadir_elev):
            finite = dem[np.isfinite(dem)]
            if finite.size == 0:
                return None, SKIP_NO_DEM_AT_NADIR, elapsed
            nadir_elev = float(np.median(finite))
        return (spec, dem_sample, dem, float(nadir_elev)), None, elapsed

    def _agl_is_override(self, image) -> bool:
        """True when an explicit AGL was supplied for this frame.

        Mirrors ``FrameGeometry._resolve_agl_m``: a Wingtra per-image AGL or the
        viewer's custom altitude are assertions of true height above the ground
        below, so they are honoured against DEM(nadir) rather than overridden by
        a GPS fix.
        """
        if self.custom_altitude_ft is not None and self.custom_altitude_ft > 0:
            return True
        wingtra = image.get('wingtra_agl_ft')
        return wingtra is not None and wingtra > 0

    def _resolve_cam_elev(self, nadir_elev, reported_agl, agl_is_override, anchor):
        """``(camera orthometric elevation, source key)`` for one frame.

        The reported "AGL" (``drone-dji:RelativeAltitude``) is height above the
        TAKEOFF point, not above the ground currently below the aircraft. Taking
        it as ``DEM(nadir) + AGL`` therefore places the camera too high over
        ground above launch elevation (understating POD) and too low over ground
        below it (overstating POD - the dangerous direction, since it paints
        ground as searched that was not). Resolution order:

        1. ``agl_override`` - the user or flight log asserted a true AGL, so it
           is honoured against the ground directly below.
        2. ``anchor`` - ``takeoff_elevation + reported AGL``, with the takeoff
           elevation resolved once per mission (``_resolve_altitude_anchor``).
           This is what the reported altitude actually means, so it stays correct
           across relief while keeping the barometric per-frame precision.
        3. ``agl_nadir`` - historical flat-terrain rule, used when no anchor
           could be validated.
        """
        if agl_is_override:
            return nadir_elev + reported_agl, 'agl_override'
        if anchor is not None:
            cam_z = anchor + reported_agl
            # A frame resolving at or under the terrain means the anchor or the
            # DEM is wrong here; fall back rather than project from underground.
            if math.isfinite(cam_z) and (cam_z - nadir_elev) >= _MIN_AGL_M:
                return cam_z, 'anchor'
        return nadir_elev + reported_agl, 'agl_nadir'

    def _resolve_altitude_anchor(self, images):
        """``(takeoff elevation in the DEM's datum, reason key)`` for the mission.

        Each frame implies a takeoff elevation independently::

            implied(i) = (GPS_ASL(i) - geoid_N(i)) - reported_AGL(i)

        which is a constant when the GPS-altitude datum and the barometric AGL
        agree, so the median over a bounded sample is a far better estimate than
        any single frame (GPS vertical noise averages down) and the spread is a
        direct coherence test.

        Validated two ways, both chosen so real terrain cannot trip them - a
        valley launch under a ridge search is the case this exists to fix, and
        a check that rejects it is worse than no check (the trap
        ``AOIService._select_effective_agl`` hits from the other side, where a
        per-frame comparison reads real relief as a datum error):

        * **coherence** - the spread of ``implied`` across the flight. Wide
          spread means GPS altitude and the barometer are not tracking each
          other, so neither can be trusted.
        * **physical plausibility** - the anchor must leave the aircraft above
          ground and within sensor range of it over the terrain actually flown.

        Known limitation: a datum mismatch (GPS altitude that is already
        orthometric, or a wrong geoid) is a CONSTANT offset. It leaves the
        spread untouched and is indistinguishable from a genuine launch-point
        elevation, so only an offset large enough to fail the physical check is
        caught. The resolved anchor is therefore reported in stats and the log
        so it can be checked against the known launch elevation. For the fleet
        this serves, EXIF GPS altitude is ellipsoidal (see
        ``WaldoMetadataService``), and where the geoid is negative - all of
        CONUS - an undetected mismatch biases POD low, the conservative
        direction.
        """
        samples = []
        implied_agl_inputs = []
        for image in self._anchor_sample(images):
            # An explicit AGL is not height above takeoff, so it cannot inform
            # the anchor (and such frames bypass it anyway).
            if self._agl_is_override(image):
                continue
            try:
                fg = self._frame_geometry(image)
            except Exception:
                continue
            if fg is None or not fg.agl_m or fg.agl_m <= 0:
                continue

            elev = self._point_elevation(fg.lat, fg.lon)
            if elev is not None:
                implied_agl_inputs.append((fg.agl_m, elev))

            if fg.asl_alt_m is None:
                continue
            undulation = self._geoid_undulation(fg.lat, fg.lon)
            if undulation is None:
                continue
            implied = (fg.asl_alt_m - undulation) - fg.agl_m
            if math.isfinite(implied):
                samples.append(implied)

        if len(samples) < _ANCHOR_MIN_SAMPLES:
            return None, 'insufficient_samples'

        arr = np.asarray(samples, dtype=np.float64)
        anchor = float(np.median(arr))
        mad = float(np.median(np.abs(arr - anchor)))
        if mad > _ANCHOR_MAX_MAD_M:
            self.logger.warning(
                f"POD: GPS-altitude and barometric-AGL chains disagree across the "
                f"flight (spread {mad:.1f} m > {_ANCHOR_MAX_MAD_M:.0f} m); "
                "cannot trust a takeoff elevation from them.")
            return None, 'incoherent'

        if implied_agl_inputs:
            implied_agls = [anchor + agl - elev for agl, elev in implied_agl_inputs]
            median_agl = float(np.median(implied_agls))
            if median_agl < _MIN_AGL_M or median_agl > self.params.max_range_m:
                self.logger.warning(
                    f"POD: a takeoff elevation of {anchor:.0f} m puts the aircraft at "
                    f"{median_agl:.0f} m above the terrain flown, which is not a real "
                    "flight; the GPS-altitude datum does not match the DEM. Using "
                    "reported AGL instead.")
                return None, 'implausible_agl'

        return anchor, 'ok'

    @staticmethod
    def _anchor_sample(images):
        """Evenly spaced, bounded subset of ``images`` for the anchor pre-pass.

        Bounded so the cost is O(1) in mission size, and spread across the flight
        so barometric drift shows up in the spread rather than hiding at one end.
        """
        candidates = [im for im in images
                      if not im.get('hidden', False) and im.get('path', '') != '']
        if not candidates:
            return []
        step = max(1, len(candidates) // _ANCHOR_SAMPLE_FRAMES)
        return candidates[::step][:_ANCHOR_SAMPLE_FRAMES]

    def _point_elevation(self, lat, lon):
        """Cache-backed DEM elevation at a point, or None when unavailable."""
        getter = getattr(self.terrain, 'get_elevation', None)
        if getter is None:
            return None
        try:
            result = getter(lat, lon)
        except Exception:
            return None
        if getattr(result, 'source', None) != 'terrain':
            return None
        elev = getattr(result, 'elevation_m', None)
        if elev is None or not math.isfinite(elev):
            return None
        return float(elev)

    def _geoid_undulation(self, lat, lon):
        """EGM96 undulation at (lat, lon), memoised on a ~1 km key.

        The undulation field is smooth (well under 0.1 m of change across a
        single mission), so rounding costs no accuracy and keeps the pyproj
        transform off the per-frame path. ``None`` when no geoid is available -
        callers must then fall back rather than assume 0 m.

        Only successful lookups are memoised: the EGM96 grid loads lazily and a
        first-call failure must not poison the rest of the mission.
        """
        getter = getattr(self.terrain, 'get_geoid_undulation', None)
        if getter is None:
            return None
        key = (round(lat, 2), round(lon, 2))
        if key in self._geoid_memo:
            return self._geoid_memo[key]
        try:
            value = getter(lat, lon)
        except Exception as e:
            self.logger.warning(
                f"POD: geoid lookup failed at {lat:.5f},{lon:.5f}: {e}")
            return None
        if value is None:
            return None
        self._geoid_memo[key] = value
        return value

    @staticmethod
    def _agl_differs(effective_agl, sizing_agl):
        """True when the frame grid was sized from a materially wrong AGL."""
        delta = abs(effective_agl - sizing_agl)
        return (delta > _AGL_RESPEC_TOL_M
                and delta > _AGL_RESPEC_TOL_FRAC * max(abs(sizing_agl), 1.0))

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
