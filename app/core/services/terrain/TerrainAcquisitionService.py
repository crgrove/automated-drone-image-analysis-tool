"""Keep elevation data stocked for the area a project actually covers.

One service for **every** elevation source, one place where the decision to
download is made, and one set of triggers. Before this existed each source
downloaded on its own terms — Terrarium fetched a tile at the moment an AOI
needed it, 3DEP only ever arrived through a dialog the operator had to go
find — so the same operation behaved differently depending on a preference
set weeks earlier.

**Sources are strategies, not branches.** Adding an elevation source means
adding a :class:`_Strategy` and registering its provider id; no caller and
no orchestration code learns about provider kinds
(CLAUDE.md §2.3). Each strategy answers three questions about a bounding
box — how big is the download, is it already covered, and fetch it — and
knows nothing about when or why it was asked.

**Triggers are standardized.** Acquisition is attempted at
:data:`TRIGGER_ANALYSIS` (the network is idle for exactly as long as the
analysis pass keeps the CPU busy), :data:`TRIGGER_VIEWER_OPEN` (the
operator is about to work AOIs that need terrain) and
:data:`TRIGGER_EXPORT` (a report or map is being produced, possibly from a
path that never opened a viewer). The same gates apply at all three, and an
area already attempted in this process is not attempted again, so firing
from several places costs nothing.

**Gates, in order, all from settings:**

1. ``UseTerrainElevation`` off — the operator asked for flat-terrain
   positioning, so no elevation data is wanted at all.
2. ``OfflineOnly`` on — the same floor :class:`TerrainService` honours for
   individual lookups. Never download in offline mode.
3. Nothing to derive an area from, or the area is already covered.
4. Estimated size over ``AutoAcquireTerrainMaxMB``. A download nobody is
   watching must not surprise a metered field connection; an implausible
   bounding box is refused rather than fetched.
5. No connectivity — checked once per process, and only when a download is
   otherwise about to happen.

**Failure is always tolerated.** Terrain sharpens AOI positions; it is not
part of any operation's contract. Nothing here raises, blocks or opens a
dialog: every path returns an :class:`AcquisitionOutcome` carrying the
reason, and callers report it or ignore it.
"""

from __future__ import annotations

import math
import os
import threading
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

from core.services.LoggerService import LoggerService
from core.services.terrain.TerrainProviderFactory import (
    DEFAULT_PROVIDER_ID,
    PROVIDER_TERRARIUM,
    PROVIDER_USGS_3DEP_LOCAL,
)

# ----------------------------------------------------------------------
# triggers
# ----------------------------------------------------------------------

TRIGGER_ANALYSIS = 'analysis'
TRIGGER_VIEWER_OPEN = 'viewer_open'
TRIGGER_EXPORT = 'export'

TRIGGERS = (TRIGGER_ANALYSIS, TRIGGER_VIEWER_OPEN, TRIGGER_EXPORT)

# ----------------------------------------------------------------------
# settings
# ----------------------------------------------------------------------

SETTING_ENABLED = 'AutoAcquireTerrain'
SETTING_MAX_MB = 'AutoAcquireTerrainMaxMB'
SETTING_USE_TERRAIN = 'UseTerrainElevation'
SETTING_OFFLINE_ONLY = 'OfflineOnly'
SETTING_PROVIDER = 'TerrainProviderId'

# 250 MB is roughly a 60 km² search area of 1 m 3DEP: large enough for a
# real mission, small enough that a bounding box spanning a state is
# refused rather than downloaded.
DEFAULT_MAX_MB = 250.0

_METERS_PER_DEG = 111320.0

# Skip reasons, as returned in AcquisitionOutcome.skipped_reason.
SKIP_TERRAIN_DISABLED = "terrain elevation is turned off"
SKIP_OFFLINE = "offline-only mode is on"
SKIP_ACQUISITION_DISABLED = "automatic terrain download is off"
SKIP_NO_AREA = "no GPS positions to derive an area from"
SKIP_COVERED = "elevation data already covers this area"
SKIP_ALREADY_TRIED = "already attempted for this area"
SKIP_NO_NETWORK = "no connectivity"
SKIP_UNSUPPORTED = "the selected elevation source needs no download"
SKIP_CANCELLED = "cancelled while planning"


# Areas attempted in this process, keyed by (provider id, rounded bounds).
# Process-wide on purpose: the point of standardizing the triggers is that
# analysis, opening a viewer and running an export can all ask without
# repeating the work, and each call site builds its own service instance.
_attempted = set()
_attempted_lock = threading.Lock()


def reset_attempt_history():
    """Forget which areas were attempted. For tests and session resets."""
    with _attempted_lock:
        _attempted.clear()


def _attempt_key(provider_id: str, bounds) -> tuple:
    return (provider_id,) + tuple(round(float(v), 4) for v in bounds)


@dataclass
class AcquisitionPlan:
    """What an acquisition would do, before it does it."""

    provider_id: str
    bounds: tuple                 # (min_lon, min_lat, max_lon, max_lat) WGS84
    estimated_mb: float
    out_dir: Optional[str] = None
    detail: str = ""

    @property
    def bounds_text(self) -> str:
        w, s, e, n = self.bounds
        return f"{w:.5f},{s:.5f} -> {e:.5f},{n:.5f}"


@dataclass
class AcquisitionOutcome:
    """What happened. Never an exception."""

    trigger: Optional[str] = None
    plan: Optional[AcquisitionPlan] = None
    skipped_reason: Optional[str] = None
    tiles_written: int = 0
    tiles_failed: int = 0
    cancelled: bool = False
    registered: bool = False
    errors: list = field(default_factory=list)

    @property
    def acquired(self) -> bool:
        return self.tiles_written > 0


# ----------------------------------------------------------------------
# strategies: one per elevation source
# ----------------------------------------------------------------------


class _Strategy:
    """How one elevation source estimates, checks and fetches an area.

    Deliberately narrow: a strategy knows about its own data and nothing
    about triggers, settings or threads. Everything shared lives in
    :class:`TerrainAcquisitionService`.
    """

    provider_id = ''
    label = ''

    def __init__(self, settings_service=None, logger=None):
        self.settings_service = settings_service
        self.logger = logger or LoggerService()

    def estimate_mb(self, bounds) -> float:
        raise NotImplementedError

    def already_covered(self, bounds) -> bool:
        raise NotImplementedError

    def acquire(self, plan: AcquisitionPlan, progress_callback=None,
                cancel_check=None) -> AcquisitionOutcome:
        raise NotImplementedError

    def out_dir(self) -> Optional[str]:
        """Where a fetch would write, when the source is file-backed."""
        return None


class TerrariumStrategy(_Strategy):
    """AWS Terrain Tiles: the global online default, ~38 m at zoom 12.

    Tiles were always downloaded on demand — one at a time, in the middle
    of whatever operation needed the elevation. Fetching the whole working
    area up front moves that cost off the operator's critical path; it is
    the same tiles, in the same on-disk cache, fetched sooner.
    """

    provider_id = PROVIDER_TERRARIUM
    label = 'AWS Terrain Tiles'

    # A 256x256 terrarium PNG is ~50-120 KB depending on relief.
    _MB_PER_TILE = 0.1

    def __init__(self, settings_service=None, logger=None, cache_service=None,
                 zoom: Optional[int] = None):
        super().__init__(settings_service, logger)
        self._cache = cache_service
        self._zoom = zoom

    @property
    def zoom(self) -> int:
        if self._zoom is None:
            from core.services.terrain.TerrainService import TerrainService
            self._zoom = TerrainService.DEFAULT_ZOOM
        return self._zoom

    @property
    def cache(self):
        if self._cache is None:
            from core.services.terrain.TerrainCacheService import TerrainCacheService
            self._cache = TerrainCacheService()
        return self._cache

    def estimate_mb(self, bounds) -> float:
        return self._tile_count(bounds) * self._MB_PER_TILE

    def _tile_count(self, bounds) -> int:
        from core.services.terrain.ElevationProvider import TerrariumProvider
        min_lon, min_lat, max_lon, max_lat = bounds
        min_x, max_y = TerrariumProvider.lat_lon_to_tile(max_lat, min_lon, self.zoom)
        max_x, min_y = TerrariumProvider.lat_lon_to_tile(min_lat, max_lon, self.zoom)
        return max(1, (max_x - min_x + 1) * (max_y - min_y + 1))

    def already_covered(self, bounds) -> bool:
        try:
            return self.cache.count_missing_tiles(bounds, self.zoom) == 0
        except Exception as exc:  # noqa: BLE001 - unknown == not covered
            self.logger.warning(f"TerrainAcquisition: cache probe failed: {exc}")
            return False

    def acquire(self, plan, progress_callback=None, cancel_check=None):
        outcome = AcquisitionOutcome(plan=plan)
        try:
            written = self.cache.prefetch_bounds(
                plan.bounds, zoom=self.zoom,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
        except Exception as exc:  # noqa: BLE001
            outcome.skipped_reason = str(exc)
            return outcome
        outcome.tiles_written = written
        outcome.cancelled = bool(cancel_check and cancel_check())
        # Tiles land in the shared on-disk cache the online path already
        # reads, so there is nothing to register.
        outcome.registered = written > 0
        return outcome


class Usgs3depStrategy(_Strategy):
    """USGS 3DEP: 1 m over most of CONUS, downloaded as GeoTIFF tiles.

    Selecting 3DEP as the provider *is* the request for this data, so
    acquisition keeps the source the operator chose stocked rather than
    leaving them to find a download dialog. Resolution matches the manual
    path's 1 m deliberately: ``USGS3DEPProvider.lookup_tile`` returns the
    first manifest row containing a point with no notion of which is
    finer, so a coarser second copy of an area could shadow a finer one.
    Mixed resolutions need resolution-aware selection first.
    """

    provider_id = PROVIDER_USGS_3DEP_LOCAL
    label = 'USGS 3DEP'

    NATIVE_RES_M = 1.0
    _BYTES_PER_SAMPLE = 4

    # US + territories. A box wholly outside answers NoData for every tile.
    _US_BBOX = (-179.9, 15.0, -64.0, 72.0)

    def __init__(self, settings_service=None, logger=None, fetch_service=None):
        super().__init__(settings_service, logger)
        self._fetch = fetch_service

    @property
    def fetch(self):
        if self._fetch is None:
            from core.services.terrain.TileFetchService import TileFetchService
            self._fetch = TileFetchService(logger=self.logger)
        return self._fetch

    def out_dir(self) -> Optional[str]:
        from core.services.terrain.TileFetchService import library_root
        # The central library, so acquisitions accumulate across missions
        # instead of each one stranding the last.
        return library_root()

    def estimate_mb(self, bounds) -> float:
        min_lon, min_lat, max_lon, max_lat = bounds
        mid_lat = (min_lat + max_lat) / 2.0
        m_per_deg_lon = _METERS_PER_DEG * max(0.05, math.cos(math.radians(mid_lat)))
        cols = max(1.0, (max_lon - min_lon) * m_per_deg_lon / self.NATIVE_RES_M)
        rows = max(1.0, (max_lat - min_lat) * _METERS_PER_DEG / self.NATIVE_RES_M)
        return cols * rows * self._BYTES_PER_SAMPLE / (1024.0 * 1024.0)

    def in_coverage(self, bounds) -> bool:
        min_lon, min_lat, max_lon, max_lat = bounds
        w, s, e, n = self._US_BBOX
        return not (max_lon < w or min_lon > e or max_lat < s or min_lat > n)

    def already_covered(self, bounds) -> bool:
        if not self.in_coverage(bounds):
            # Nothing to fetch here, ever: treat as covered so the caller
            # reports "needs no download" rather than retrying forever.
            return True
        if self.settings_service is None:
            return False
        manifest = self.settings_service.get_setting('Terrain3DEPManifestPath', '') or ''
        tiles = self.settings_service.get_setting('Terrain3DEPTilesDir', '') or ''
        if not (manifest and tiles
                and os.path.isfile(manifest) and os.path.isdir(tiles)):
            return False
        try:
            import sys
            module = sys.modules.get('core.services.terrain.USGS3DEPProvider')
            if module is None:
                import importlib
                module = importlib.import_module(
                    'core.services.terrain.USGS3DEPProvider')
            provider = module.USGS3DEPProvider(manifest, tiles)
        except Exception as exc:  # noqa: BLE001 - unreadable == not covered
            self.logger.warning(f"TerrainAcquisition: manifest unreadable: {exc}")
            return False

        # Corners plus centre: a manifest holding all five covers the area
        # for every practical purpose, without loading mosaic geometry.
        min_lon, min_lat, max_lon, max_lat = bounds
        mid_lon, mid_lat = (min_lon + max_lon) / 2.0, (min_lat + max_lat) / 2.0
        probes = ((min_lat, min_lon), (min_lat, max_lon), (max_lat, min_lon),
                  (max_lat, max_lon), (mid_lat, mid_lon))
        try:
            return all(provider.lookup_tile(lat, lon) is not None
                       for lat, lon in probes)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(f"TerrainAcquisition: coverage probe failed: {exc}")
            return False

    def acquire(self, plan, progress_callback=None, cancel_check=None):
        outcome = AcquisitionOutcome(plan=plan)
        try:
            result = self.fetch.fetch_3dep_dem(
                plan.bounds, plan.out_dir,
                native_res_m=self.NATIVE_RES_M,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
        except Exception as exc:  # noqa: BLE001
            outcome.skipped_reason = str(exc)
            return outcome

        outcome.tiles_written = result.tiles_written
        outcome.tiles_failed = result.tiles_failed
        outcome.cancelled = result.cancelled
        outcome.errors = list(result.errors)
        if result.cancelled:
            return outcome
        if not result.tiles_written or not result.manifest_path:
            reason = "no tiles were written"
            if result.errors:
                reason = f"{reason}: {result.errors[0][1]}"
            outcome.skipped_reason = reason
            return outcome
        outcome.registered = self._register(result.manifest_path, plan.out_dir)
        return outcome

    def _register(self, manifest_path: str, tiles_dir: str) -> bool:
        """Point Preferences at what was downloaded.

        Only the paths: the provider is not switched. Choosing the source
        is the operator's decision and this service exists to serve that
        choice, not to override it. Registering paths is harmless for any
        other provider, which only ever reads them when 3DEP is selected.
        """
        if self.settings_service is None:
            return False
        try:
            self.settings_service.set_setting('Terrain3DEPManifestPath', manifest_path)
            self.settings_service.set_setting('Terrain3DEPTilesDir', tiles_dir)
            return True
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(f"TerrainAcquisition: registration failed: {exc}")
            return False


# Provider id -> strategy. A new elevation source is one entry here plus a
# _Strategy; nothing else in the app changes (CLAUDE.md §2.3).
_STRATEGIES = {
    TerrariumStrategy.provider_id: TerrariumStrategy,
    Usgs3depStrategy.provider_id: Usgs3depStrategy,
}


# ----------------------------------------------------------------------
# the service
# ----------------------------------------------------------------------


class TerrainAcquisitionService:
    """Decide whether to stock elevation data, and do it.

    No Qt: callers own the thread. :meth:`plan` reads settings and image
    EXIF and is cheap enough for the UI thread; :meth:`acquire` performs
    network I/O and must not run there.
    """

    # Connectivity is probed at most once per process: the probe is itself a
    # network round trip, and every trigger would otherwise repeat it.
    _online_checked = False
    _online = True

    def __init__(self, settings_service=None, logger=None, strategy=None,
                 fetch_service=None, cache_service=None):
        self.logger = logger or LoggerService()
        self.settings_service = settings_service
        self._strategy = strategy
        self._fetch_service = fetch_service
        self._cache_service = cache_service

    # ------------------------------------------------------------------
    # settings gates
    # ------------------------------------------------------------------

    def _bool_setting(self, name, default):
        if self.settings_service is None:
            return default
        try:
            return bool(self.settings_service.get_bool_setting(name, default))
        except Exception:  # noqa: BLE001 - an unreadable setting is its default
            return default

    def terrain_enabled(self) -> bool:
        return self._bool_setting(SETTING_USE_TERRAIN, True)

    def offline_only(self) -> bool:
        return self._bool_setting(SETTING_OFFLINE_ONLY, False)

    def enabled(self) -> bool:
        """Whether automatic acquisition is allowed at all.

        Three settings, in the order a reader would expect: elevation must
        be wanted, the app must not be in offline mode, and automatic
        downloading must not have been switched off.
        """
        return (self.terrain_enabled()
                and not self.offline_only()
                and self._bool_setting(SETTING_ENABLED, True))

    def max_mb(self) -> float:
        if self.settings_service is None:
            return DEFAULT_MAX_MB
        try:
            value = float(self.settings_service.get_setting(
                SETTING_MAX_MB, DEFAULT_MAX_MB) or DEFAULT_MAX_MB)
            return value if value > 0 else DEFAULT_MAX_MB
        except Exception:  # noqa: BLE001 - a bad value or an unreadable
            # store both mean "use the documented default" rather than
            # failing whatever triggered this.
            return DEFAULT_MAX_MB

    def provider_id(self) -> str:
        if self.settings_service is None:
            return DEFAULT_PROVIDER_ID
        try:
            return (self.settings_service.get_setting(
                SETTING_PROVIDER, DEFAULT_PROVIDER_ID) or DEFAULT_PROVIDER_ID)
        except Exception:  # noqa: BLE001 - unreadable == the default source
            return DEFAULT_PROVIDER_ID

    def strategy(self):
        """The strategy for the selected provider, or None if it needs none."""
        if self._strategy is not None:
            return self._strategy
        factory = _STRATEGIES.get(self.provider_id())
        if factory is None:
            return None
        if factory is TerrariumStrategy:
            self._strategy = factory(
                settings_service=self.settings_service, logger=self.logger,
                cache_service=self._cache_service)
        else:
            self._strategy = factory(
                settings_service=self.settings_service, logger=self.logger,
                fetch_service=self._fetch_service)
        return self._strategy

    # ------------------------------------------------------------------
    # planning
    # ------------------------------------------------------------------

    def plan(self, images: Optional[Sequence[dict]] = None, bounds=None,
             trigger: str = TRIGGER_ANALYSIS,
             cancel_check: Optional[Callable] = None):
        """Decide what to acquire, or why not to.

        Args:
            images (list[dict], optional): Records carrying ``path``; the
                area is derived from their GPS. Ignored when ``bounds`` is
                given.
            bounds (tuple, optional): Explicit ``(min_lon, min_lat, max_lon,
                max_lat)`` in WGS84.
            trigger (str): One of :data:`TRIGGERS`, for the log line.
            cancel_check (callable, optional): Returns True to stop deriving
                the area, between images.

        Returns:
            tuple[AcquisitionPlan | None, str | None]: The plan, or None
            and the reason nothing will be attempted.
        """
        if not self.terrain_enabled():
            return None, SKIP_TERRAIN_DISABLED
        if self.offline_only():
            return None, SKIP_OFFLINE
        if not self._bool_setting(SETTING_ENABLED, True):
            return None, SKIP_ACQUISITION_DISABLED

        strategy = self.strategy()
        if strategy is None:
            return None, SKIP_UNSUPPORTED

        if bounds is not None:
            area = bounds
        else:
            area = self._bounds_for(images, cancel_check)
            if cancel_check and cancel_check():
                return None, SKIP_CANCELLED
        if area is None:
            return None, SKIP_NO_AREA

        key = _attempt_key(strategy.provider_id, area)
        with _attempted_lock:
            if key in _attempted:
                return None, SKIP_ALREADY_TRIED

        if strategy.already_covered(area):
            return None, SKIP_COVERED

        size_mb = strategy.estimate_mb(area)
        cap = self.max_mb()
        if size_mb > cap:
            return None, (f"estimated {size_mb:.0f} MB exceeds the "
                          f"{cap:.0f} MB automatic-download limit")

        return AcquisitionPlan(
            provider_id=strategy.provider_id,
            bounds=area,
            estimated_mb=size_mb,
            out_dir=strategy.out_dir(),
            detail=strategy.label,
        ), None

    def _bounds_for(self, images, cancel_check=None):
        """Padded GPS bounding box of ``images``, or None without GPS.

        Reuses the helpers the manual download dialog fills its area from,
        so an automatic acquisition covers what a manual one would have.
        """
        if not images:
            return None
        try:
            from core.services.coverage.aoi import (
                compute_mission_gps_bounds, suggest_buffer_m, pad_bounds)
            raw = compute_mission_gps_bounds(images, cancel_check=cancel_check)
            if raw is None:
                return None
            return pad_bounds(raw, suggest_buffer_m(images, cancel_check=cancel_check))
        except Exception as exc:  # noqa: BLE001 - degrade, never crash a caller
            self.logger.warning(f"TerrainAcquisition: could not derive bounds: {exc}")
            return None

    # ------------------------------------------------------------------
    # connectivity
    # ------------------------------------------------------------------

    def online(self) -> bool:
        """Whether the elevation service is reachable.

        Probed at most once per process and only when a download is
        otherwise about to happen: the probe is itself a request, and a
        false negative would disable acquisition for the session, so a
        failure to probe counts as online and lets the real fetch decide.
        """
        cls = TerrainAcquisitionService
        if cls._online_checked:
            return cls._online
        cls._online_checked = True
        try:
            from core.services.terrain.TerrainCacheService import TerrainCacheService
            cache = self._cache_service or TerrainCacheService()
            cls._online = bool(cache.is_online())
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(f"TerrainAcquisition: connectivity check failed: {exc}")
            cls._online = True
        return cls._online

    @classmethod
    def reset_connectivity(cls):
        """Forget the cached probe result. For tests and session resets."""
        cls._online_checked = False
        cls._online = True

    # ------------------------------------------------------------------
    # acquisition
    # ------------------------------------------------------------------

    def acquire(self, plan: AcquisitionPlan, progress_callback=None,
                cancel_check=None) -> AcquisitionOutcome:
        """Execute ``plan``. Never raises."""
        strategy = self.strategy()
        if strategy is None:
            return AcquisitionOutcome(plan=plan, skipped_reason=SKIP_UNSUPPORTED)

        with _attempted_lock:
            _attempted.add(_attempt_key(plan.provider_id, plan.bounds))

        if not self.online():
            self.logger.info("TerrainAcquisition: skipped - no connectivity")
            return AcquisitionOutcome(plan=plan, skipped_reason=SKIP_NO_NETWORK)

        self.logger.info(
            f"TerrainAcquisition: fetching {plan.detail} for {plan.bounds_text} "
            f"(~{plan.estimated_mb:.1f} MB)"
        )
        try:
            outcome = strategy.acquire(
                plan, progress_callback=progress_callback,
                cancel_check=cancel_check)
        except Exception as exc:  # noqa: BLE001 - callers must never fail on this
            self.logger.warning(f"TerrainAcquisition: {plan.detail} failed: {exc}")
            return AcquisitionOutcome(plan=plan, skipped_reason=str(exc))

        if outcome.cancelled:
            # A cancel is not an attempt: leave the area to the next trigger.
            with _attempted_lock:
                _attempted.discard(_attempt_key(plan.provider_id, plan.bounds))
            self.logger.info("TerrainAcquisition: cancelled")
        elif outcome.acquired:
            self.logger.info(
                f"TerrainAcquisition: {outcome.tiles_written} {plan.detail} "
                f"tile(s) stored, {outcome.tiles_failed} failed"
            )
        elif outcome.skipped_reason:
            self.logger.warning(f"TerrainAcquisition: {outcome.skipped_reason}")
        return outcome

    def run(self, images=None, bounds=None, trigger: str = TRIGGER_ANALYSIS,
            progress_callback: Optional[Callable] = None,
            cancel_check: Optional[Callable] = None) -> AcquisitionOutcome:
        """Plan and acquire in one call. Never raises."""
        try:
            plan, reason = self.plan(images=images, bounds=bounds, trigger=trigger,
                                     cancel_check=cancel_check)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(f"TerrainAcquisition: planning failed: {exc}")
            return AcquisitionOutcome(trigger=trigger, skipped_reason=str(exc))

        if plan is None:
            self.logger.info(f"TerrainAcquisition[{trigger}]: skipped - {reason}")
            return AcquisitionOutcome(trigger=trigger, skipped_reason=reason,
                                      cancelled=reason == SKIP_CANCELLED)

        outcome = self.acquire(plan, progress_callback=progress_callback,
                               cancel_check=cancel_check)
        outcome.trigger = trigger
        return outcome
