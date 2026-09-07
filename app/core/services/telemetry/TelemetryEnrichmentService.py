"""DEM-corrected AGL for live telemetry, off the UI thread.

The drone's own "AGL" is relative to the **takeoff point** — DJI's
``rel_alt``, and the equivalent field from ADIAT Flight. ADIAT calls
that reference **ATO** (above takeoff), never AGL. Fly from a ridge into
a valley and it drifts from reality by the whole terrain delta, which is
exactly the situation where a SAR crew cares most about height above
ground.

**Three references, three keys.** ATO and AGL never share a field; the
provenance of the AGL travels beside it so no surface has to guess::

    aircraft_altitude_msl_m           above mean sea level
    aircraft_altitude_agl_m           ATO — above the takeoff point
    aircraft_altitude_agl_terrain_m   AGL — above the terrain below, or absent
    agl_source                        what produced the AGL above
    terrain_elevation_m               DEM elevation under the aircraft

ADIAT Flight names its AGL source on ``aircraft_altitude_agl_source``;
that value is folded into ``agl_source`` at ingest so there is one
provenance key internally and in every recorded bundle.

``aircraft_altitude_agl_m`` keeps its wire name for compatibility with
recorded bundles and with ADIAT Flight builds already in the field; it
has always carried ATO. This service **never writes** it — see
:meth:`TelemetryEnrichmentService._apply_elevation`.

ADIAT already ships a DEM stack (:mod:`core.services.terrain`) that
image analysis uses for terrain-corrected AOI geolocation. This service
brings the same correction to live telemetry.

**Why not simply ``MSL − terrain``.** DJI's ``abs_alt`` is a GPS height
above the WGS84 *ellipsoid*, not an orthometric MSL height. Measured
against the project's own test flight, the geoid undulation in central
Texas is −27 m: ``abs_alt`` reads 207.0 m where the DEM reports 215.0 m
of terrain, so the naive subtraction yields a *negative* AGL for an
aircraft that was demonstrably 14.9 m up. Applying the correction that
way would be worse than not correcting at all.

Instead the aircraft is anchored to the terrain under its **first fix**,
which is datum-free because it only ever uses *relative* altitude and
*differences* between DEM samples::

    reference_ground = DEM(first fix)
    aircraft_elevation(t) = reference_ground + ATO(t)
    AGL(t) = aircraft_elevation(t) − DEM(lat(t), lon(t))

Over flat ground this returns the ATO figure unchanged; flying into
a valley it grows by exactly the terrain drop, which is the whole point
of the correction. This mirrors the takeoff-anchored reasoning in
:meth:`TerrainService.get_effective_altitude_agl`.

When no ATO reading exists at all, the service falls back to
``MSL − terrain`` and converts the height through
:meth:`TerrainService.convert_ellipsoidal_to_orthometric` first, so the
geoid is accounted for rather than ignored.

**The UI thread is never blocked.** A DEM lookup can hit the network for
a tile, and telemetry arrives at ~4 Hz live (or per displayed frame for
file playback), so a synchronous lookup would stutter the video. Instead:

* :meth:`enrich` returns immediately with what the publisher sent, and
* a corrected envelope is emitted later on :attr:`envelopeEnriched`.

Lookups are additionally cached and throttled so a hovering aircraft
produces one tile fetch rather than four per second.

**Three tiers, best evidence first.**

1. The publisher's own terrain-referenced AGL (``LASER`` / ``ULTRASONIC``
   / ``TERRAIN_DEM``): nothing to compute.
2. The differential anchored at the publisher's **takeoff coordinates**
   (``takeoff_latitude`` / ``takeoff_longitude``): positions are
   datum-free where elevations are not, so Desktop samples its own DEM at
   the launch point and under the aircraft and differences them - no
   geoid, no cross-app datum agreement, correct however late the viewer
   connected.
3. The first-fix anchor below, for publishers that predate the fields.

**ADIAT Flight's AGL wins.** When the publisher already sent a
terrain-referenced AGL this service passes the envelope straight
through: no anchor, no lookup, no network. Flight's chain is anchored at
the true takeoff point and may be a direct measurement (laser or the
downward sensor), so the inference here cannot beat it — and skipping
the lookups keeps a metered field connection free.

Flight's ``TAKEOFF_REFERENCE`` is the exception: it means Flight looked
for a terrain source and found none, and Desktop's on-demand DEM may
cover ground its pre-cached tiles do not, so that case still earns a
lookup. See :func:`has_publisher_agl`.
"""

from __future__ import annotations

import math
import time
from collections import OrderedDict
from typing import Dict, Optional, Tuple

from PySide6.QtCore import QObject, QThread, Signal, Slot

from core.services.LoggerService import LoggerService
from core.services.telemetry.TelemetryTrack import haversine_meters

# Cache key resolution: 1e-4 degrees is ~11 m at the equator, comfortably
# finer than the DEM's own ~38 m resolution at the default zoom, so
# rounding costs no accuracy while collapsing a hover into one entry.
_CACHE_PRECISION = 4
_CACHE_MAX_ENTRIES = 4096

# Re-query only after the aircraft has moved this far, or this long has
# passed. Terrain does not change; the aircraft's position does.
DEFAULT_MIN_MOVE_METERS = 15.0
DEFAULT_MIN_INTERVAL_SECONDS = 2.0

# The envelope key carrying terrain-referenced AGL. Separate from
# ``aircraft_altitude_agl_m``, which is ATO and belongs to the publisher.
TERRAIN_AGL_KEY = "aircraft_altitude_agl_terrain_m"
AGL_SOURCE_KEY = "agl_source"

# ADIAT Flight records its takeoff position on the takeoff rising edge and
# publishes it so the differential can anchor at the true launch point.
# Positions are datum-free where elevations are not: Desktop samples its
# own DEM at these coordinates, so no cross-app datum agreement is needed.
TAKEOFF_LAT_KEY = "takeoff_latitude"
TAKEOFF_LON_KEY = "takeoff_longitude"

# ADIAT Flight's own provenance key. Desktop keeps its historical
# ``agl_source`` as the single internal/recorded name - file parsers write
# it, ``telemetry.csv`` has a column for it and this service overwrites it
# with its own inference - and folds the wire value into it at ingest. The
# raw key is left in the envelope untouched, so ``telemetry.jsonl`` stays a
# faithful record of what arrived.
PUBLISHER_AGL_SOURCE_KEY = "aircraft_altitude_agl_source"

# ``agl_source`` names what produced ``TERRAIN_AGL_KEY`` — never what
# produced the ATO figure beside it.
#
# ``reported`` is the one value that predates that rule and is kept
# verbatim so recorded bundles stay comparable: it means *no* AGL was
# resolved and the envelope carries only the drone's ATO reading. Every
# surface therefore decides "do I have an AGL?" from the presence of
# ``TERRAIN_AGL_KEY``, not from this field.
AGL_SOURCE_TERRAIN = "terrain"        # this service's own DEM inference
AGL_SOURCE_REPORTED = "reported"      # ATO only; no AGL exists
AGL_SOURCE_FLIGHT = "flight"          # ADIAT Flight's AGL, source unnamed
# A recorded flight log whose own column was terrain-referenced - a
# Skydio-style ``Altitude (m AGL)``. The aircraft resolved it from its own
# sensors, so it outranks a DEM difference here for the same reason ADIAT
# Flight's does. Emitted by
# :meth:`~core.services.telemetry.TelemetryTrack.TelemetryPoint.to_envelope`,
# which spells the literal out rather than importing it (this module
# imports that one).
AGL_SOURCE_FLIGHT_LOG = "flight_log"
# ADIAT Flight's four source names, sent in ``UPPER_SNAKE`` on
# :data:`PUBLISHER_AGL_SOURCE_KEY`. Flight resolves AGL through
# ultrasonic -> laser -> differential DEM -> takeoff reference and names
# the winner unconditionally, so ``takeoff_reference`` arriving is
# meaningfully different from no source name at all: the first says a
# publisher looked and found no terrain source, the second says the
# publisher predates the field. Both get a DEM lookup here, but only the
# first can be reported to the operator as such.
AGL_SOURCE_LASER = "laser"
AGL_SOURCE_ULTRASONIC = "ultrasonic"
AGL_SOURCE_TERRAIN_DEM = "terrain_dem"
AGL_SOURCE_TAKEOFF_REFERENCE = "takeoff_reference"

# Sources Desktop will not try to improve on. ``AGL_SOURCE_TERRAIN`` is
# deliberately absent: this service's own output must stay correctable as
# the aircraft moves over new terrain. ``AGL_SOURCE_TAKEOFF_REFERENCE`` is
# absent because it means the publisher found no terrain source at all —
# Desktop's on-demand DEM may cover where the publisher's cached tiles do
# not, so it is worth a lookup.
TRUSTED_AGL_SOURCES = frozenset({
    AGL_SOURCE_FLIGHT,
    AGL_SOURCE_FLIGHT_LOG,
    AGL_SOURCE_LASER,
    AGL_SOURCE_ULTRASONIC,
    AGL_SOURCE_TERRAIN_DEM,
})


def normalise_agl_source(value):
    """Fold a wire provenance value into Desktop's vocabulary.

    ADIAT Flight names its sources in ``UPPER_SNAKE`` (``TERRAIN_DEM``);
    Desktop records ``lower_snake``. Anything unrecognised passes through
    verbatim rather than being dropped, so a source name added by a
    future Flight build degrades to "recorded and shown, but not
    specially rendered" instead of vanishing.

    Args:
        value: Raw source name from an envelope, either key; any type.

    Returns:
        str or None: Normalised source name, or None when absent/blank.
    """
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    return text or None


def has_publisher_agl(envelope) -> bool:
    """True when the publisher already supplied a terrain-referenced AGL.

    The source name decides whenever there is one: ``laser``,
    ``ultrasonic`` and ``terrain_dem`` are measurements or DEM
    differences that this service cannot improve on, while
    ``takeoff_reference`` means the publisher looked for a terrain source
    and found none - so Desktop's on-demand DEM is worth a try, since it
    covers where the publisher's pre-cached tiles do not.

    With no source name the AGL key's presence decides. ADIAT Flight
    publishes that key only when a terrain source actually backed it, and
    null otherwise, so on a publisher too old to name its sources the
    presence of a value is still trustworthy provenance.

    Args:
        envelope (dict): Telemetry envelope, before or after enrichment.

    Returns:
        bool: True to leave the envelope's AGL alone.
    """
    if not isinstance(envelope, dict):
        return False
    if not _is_coord(envelope.get(TERRAIN_AGL_KEY)):
        return False
    source = publisher_agl_source(envelope)
    if source is None:
        return True
    return source in TRUSTED_AGL_SOURCES


def publisher_agl_source(envelope):
    """Return an envelope's AGL provenance, from either key.

    Reads Desktop's own ``agl_source`` first - it is what every recorded
    bundle and file parser writes, and what this service overwrites with
    its own inference - then ADIAT Flight's wire key. Callers therefore
    get one answer whether the envelope has been through :meth:`enrich`
    or not.

    Args:
        envelope (dict): Telemetry envelope, before or after enrichment.

    Returns:
        str or None: Normalised source name, or None when neither key
        carries one.
    """
    if not isinstance(envelope, dict):
        return None
    return (normalise_agl_source(envelope.get(AGL_SOURCE_KEY))
            or normalise_agl_source(envelope.get(PUBLISHER_AGL_SOURCE_KEY)))


def _build_terrain_service(logger=None):
    """Construct a :class:`TerrainService` for this module's DEM worker.

    Two deliberate choices, both of which exist to stop the process
    crashing — do not "optimize" either away:

    **1. Geoid support is OFF.** :class:`GeoidService` mutates *global*
    PROJ state (``pyproj.datadir.append_data_dir``,
    ``pyproj.network.set_network_enabled``) and caches a
    ``pyproj.Transformer``. PROJ contexts are thread-affine, so doing
    that from a background thread while the Qt main thread also uses
    PROJ faults hard: a real playback session died with
    ``Windows fatal exception: access violation`` inside
    ``pyproj.transformer.__call__``, reached via
    ``TerrainService.get_elevation`` -> ``GeoidService.get_undulation``.
    The undulation is only carried as metadata on the result, and the
    anchored AGL this service computes uses *differences* of DEM samples
    (``anchor_elev + ato - terrain_here``), so a constant datum
    offset cancels out exactly. Turning the geoid off costs nothing here
    and removes pyproj from the worker thread entirely.

    **2. Not shared between threads.** Each :class:`_ElevationWorker`
    builds its own instance, on its own thread. The duplication is only
    in-memory — the DEM tile cache lives on disk and is still shared.
    """
    try:
        from core.services.terrain import TerrainService
        return TerrainService(enable_geoid=False)
    except Exception as exc:  # noqa: BLE001 - degrade, never crash
        if logger is not None:
            logger.warning(f"Terrain service unavailable for telemetry: {exc}")
        return None


class _ElevationWorker(QObject):
    """Runs blocking DEM lookups on a dedicated thread.

    Owns its own :class:`TerrainService`, built on first use so it lives
    entirely on this worker's thread — see :func:`_build_terrain_service`
    for why sharing one across threads is unsafe.
    """

    # lat, lon, terrain elevation | None, geoid undulation | None. Both are
    # resolved in one trip so the fallback path never needs a second
    # blocking call from the UI thread.
    resolved = Signal(float, float, object, object)

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()
        self._terrain = None
        self._terrain_failed = False

    def _get_terrain_service(self):
        """Build (once) and return this worker's own terrain service.

        Constructed lazily so it is created on the worker thread that will
        use it — see :func:`_build_terrain_service` for why it must not be
        shared. Refreshes the offline floor from preferences on every call,
        mirroring :func:`core.services.image.AOIService._get_terrain_service`,
        so toggling "Offline Only" takes effect mid-flight.
        """
        if self._terrain_failed:
            return None
        if self._terrain is None:
            self._terrain = _build_terrain_service(self.logger)
            if self._terrain is None:
                self._terrain_failed = True
                return None
        try:
            from core.services.SettingsService import SettingsService
            self._terrain.offline_only = SettingsService().get_bool_setting(
                "OfflineOnly", False
            )
        except Exception:  # noqa: BLE001 - leave the existing flag alone
            pass
        return self._terrain

    @Slot(float, float)
    def lookup(self, lat: float, lon: float) -> None:
        """Resolve terrain elevation and geoid undulation for one position.

        Runs on the worker thread. Both values are fetched together and
        cached by the caller, so neither the anchored path nor the
        absolute fallback ever blocks the UI thread later.
        """
        terrain = self._get_terrain_service()
        if terrain is None:
            self.resolved.emit(lat, lon, None, None)
            return

        elevation = None
        undulation = None
        try:
            result = terrain.get_elevation(lat, lon)
            if result is not None and getattr(result, "source", None) == "terrain":
                elevation = result.elevation_m
        except Exception as exc:  # noqa: BLE001 - a DEM miss is not fatal
            self.logger.debug(f"Terrain lookup failed at {lat:.5f},{lon:.5f}: {exc}")

        # No geoid undulation is fetched: the service is built with the
        # geoid disabled to keep pyproj (and its global, thread-affine PROJ
        # state) off this thread. See _build_terrain_service. The anchored
        # AGL path does not need it; the absolute fallback simply stays
        # inactive and the drone's own ATO reading stands alone.
        self.resolved.emit(lat, lon, elevation, undulation)


class TelemetryEnrichmentService(QObject):
    """Augments telemetry envelopes with terrain-corrected AGL.

    Used by both the streaming window and the Flight Viewer so the two
    surfaces agree on what "AGL" means.

    Usage::

        service = TelemetryEnrichmentService()
        service.envelopeEnriched.connect(hud.apply_envelope)
        hud.apply_envelope(service.enrich(envelope))   # immediate, as sent
        # ...corrected envelope arrives on envelopeEnriched shortly after
    """

    envelopeEnriched = Signal(dict)
    # Internal: crossing this signal into the worker's thread is what makes
    # the lookup asynchronous. Calling ``worker.lookup(...)`` directly would
    # run the blocking DEM fetch on the *caller's* thread — ``moveToThread``
    # only reroutes queued signal delivery, not plain method calls.
    _lookupRequested = Signal(float, float)

    def __init__(
        self,
        parent: Optional[QObject] = None,
        *,
        min_move_meters: float = DEFAULT_MIN_MOVE_METERS,
        min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    ):
        super().__init__(parent)
        self.logger = LoggerService()
        self._min_move = float(min_move_meters)
        self._min_interval = float(min_interval_seconds)

        self._cache: "OrderedDict[Tuple[float, float], Optional[float]]" = OrderedDict()
        self._geoid_cache: "OrderedDict[Tuple[float, float], float]" = OrderedDict()
        self._last_query_pos: Optional[Tuple[float, float]] = None
        self._last_query_time: float = 0.0
        self._inflight: Optional[Tuple[float, float]] = None
        self._last_envelope: Optional[dict] = None

        # Datum-free anchor. Best case: the publisher's takeoff
        # coordinates, where ATO is zero by definition - the anchor is the
        # true launch point however late this viewer connected. Fallback:
        # the first fix we see (that position's terrain + its ATO reading).
        # Every later AGL is measured against the anchor, so the
        # ellipsoidal-vs-MSL question never enters the arithmetic.
        self._anchor_position: Optional[Tuple[float, float]] = None
        self._anchor_reported_agl: Optional[float] = None
        self._anchor_elevation: Optional[float] = None
        # True when the anchor came from published takeoff coordinates; a
        # first-fix anchor never overwrites one, but fresh takeoff
        # coordinates (a new flight in the same session) re-anchor.
        self._anchor_is_takeoff: bool = False

        self._thread: Optional[QThread] = None
        self._worker: Optional[_ElevationWorker] = None
        self._enabled = self._read_preference()

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def enrich(self, envelope: dict) -> dict:
        """Return ``envelope`` immediately, scheduling a DEM correction.

        The returned dict carries whatever the publisher sent, plus a
        terrain-referenced AGL when one is already resolvable from cache.
        It never waits on the network, and it never rewrites the ATO
        reading it was handed.
        """
        if not isinstance(envelope, dict):
            return envelope

        enriched = dict(envelope)
        lat = enriched.get("aircraft_latitude")
        lon = enriched.get("aircraft_longitude")

        self._stamp_source(enriched)

        self._enabled = self._read_preference()
        if not _is_coord(lat) or not _is_coord(lon):
            self._last_envelope = enriched
            return enriched

        # Anchor bookkeeping. This runs ahead of every early return below,
        # and costs nothing but arithmetic on values already in hand: a
        # session that starts on an ADIAT Flight feed takes the
        # pass-through below on every fix, and if that feed later stops
        # resolving AGL the fallback needs an anchor that already exists.
        #
        # Best anchor: the publisher's takeoff coordinates, where ATO is
        # zero by definition. Sampling Desktop's own DEM there keeps the
        # arithmetic datum-free (both DEM terms from one DEM) and makes
        # the true launch point the anchor no matter how late this viewer
        # connected - the failure mode of the first-fix rule below.
        self._adopt_takeoff_anchor(enriched)

        # Fallback anchor: the first fix that carries BOTH a position and
        # an ATO reading. Anchoring on position alone would latch
        # ``_anchor_reported_agl = None`` when the publisher's first
        # envelope omits altitude (every telemetry field is individually
        # nullable), and the anchored path would then be disabled for the
        # rest of the session.
        ato = enriched.get("aircraft_altitude_agl_m")
        if self._anchor_position is None and _is_coord(ato):
            self._anchor_position = (float(lat), float(lon))
            self._anchor_reported_agl = float(ato)

        if not self._enabled:
            self._last_envelope = enriched
            return enriched

        # The publisher's own AGL outranks ours; don't spend a tile on it.
        if has_publisher_agl(enriched):
            self._last_envelope = enriched
            return enriched

        key = _cache_key(lat, lon)
        if key in self._cache:
            self._apply_elevation(enriched, self._cache[key])
        elif not self._request_anchor_terrain():
            self._maybe_request(float(lat), float(lon))

        self._last_envelope = enriched
        return enriched

    def _stamp_source(self, envelope: dict) -> None:
        """Fold the wire provenance into ``agl_source``, in place.

        Three cases, in order:

        * a source name on either key wins, normalised - this is what
          keeps ``TAKEOFF_REFERENCE`` (a publisher that looked and found
          no terrain source) distinguishable from a publisher too old to
          have the field at all;
        * otherwise an AGL value with no name is ADIAT Flight's, recorded
          as :data:`AGL_SOURCE_FLIGHT` so the HUD tooltip and
          ``telemetry.csv`` can still say where it came from;
        * otherwise an envelope carrying only ATO keeps the historical
          :data:`AGL_SOURCE_REPORTED`.

        Args:
            envelope (dict): Envelope to stamp, in place.
        """
        source = publisher_agl_source(envelope)
        if source is None:
            if _is_coord(envelope.get(TERRAIN_AGL_KEY)):
                source = AGL_SOURCE_FLIGHT
            elif _is_coord(envelope.get("aircraft_altitude_agl_m")):
                source = AGL_SOURCE_REPORTED
        if source is not None:
            envelope[AGL_SOURCE_KEY] = source

    def _adopt_takeoff_anchor(self, envelope: dict) -> None:
        """Anchor at the published takeoff position, when there is one.

        Adopted whenever the coordinates appear or move (a battery swap in
        the same viewing session is a new launch): the anchor position
        becomes the takeoff point and the anchor ATO becomes zero - the
        drone's barometer zeroes there, so ``camera = DEM(takeoff) + ATO``
        with no reference envelope needed. A first-fix anchor is always
        superseded; it exists only for publishers that predate the fields.
        """
        tlat = envelope.get(TAKEOFF_LAT_KEY)
        tlon = envelope.get(TAKEOFF_LON_KEY)
        if not _is_coord(tlat) or not _is_coord(tlon):
            return
        position = (float(tlat), float(tlon))
        if self._anchor_is_takeoff and self._anchor_position == position:
            return
        if not self._anchor_is_takeoff and self._anchor_position is not None:
            self.logger.info(
                "Telemetry anchor upgraded from first-fix to published "
                f"takeoff position {position[0]:.6f},{position[1]:.6f}")
        self._anchor_position = position
        self._anchor_reported_agl = 0.0
        self._anchor_elevation = None      # re-resolve at the new point
        self._anchor_is_takeoff = True

    def reset(self) -> None:
        """Drop per-session state. Caches are kept — terrain doesn't move."""
        self._last_query_pos = None
        self._last_query_time = 0.0
        self._inflight = None
        self._last_envelope = None
        self._anchor_position = None
        self._anchor_reported_agl = None
        self._anchor_elevation = None
        self._anchor_is_takeoff = False

    def cleanup(self) -> None:
        """Stop the worker thread. Safe to call more than once."""
        thread = self._thread
        self._thread = None
        self._worker = None
        if thread is not None:
            thread.quit()
            if not thread.wait(2000):
                self.logger.warning("Telemetry enrichment thread did not stop within 2s")

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _read_preference(self) -> bool:
        try:
            from core.services.SettingsService import SettingsService
            return bool(SettingsService().get_bool_setting("UseTerrainElevation", True))
        except Exception:  # noqa: BLE001 - default to on, matching image analysis
            return True

    def _ensure_worker(self) -> Optional[_ElevationWorker]:
        if self._worker is not None:
            return self._worker
        try:
            thread = QThread()
            worker = _ElevationWorker()
            worker.moveToThread(thread)
            worker.resolved.connect(self._on_resolved)
            # Queued across the thread boundary because the worker lives on
            # ``thread``; this is what actually gets the blocking lookup off
            # the caller's thread.
            self._lookupRequested.connect(worker.lookup)
            thread.start()
            self._thread = thread
            self._worker = worker
            return worker
        except Exception as exc:  # noqa: BLE001 - run without terrain
            self.logger.warning(f"Could not start terrain worker: {exc}")
            return None

    def _request_anchor_terrain(self) -> bool:
        """Fetch the anchor's own DEM tile when only it is missing.

        A session that opens on an ADIAT Flight feed passes every fix
        through untouched, so the anchor position never gets looked up. If
        that feed later stops resolving AGL, :meth:`_anchored_agl` would
        be permanently unresolvable and the aircraft would show no AGL at
        all — a silent gap exactly where terrain coverage is thin. One
        tile, once per session, keeps the fallback live.

        Returns:
            bool: True when a lookup was issued for the anchor.
        """
        anchor = self._anchor_position
        if anchor is None or self._anchor_elevation is not None:
            return False
        if _cache_key(anchor[0], anchor[1]) in self._cache:
            return False
        return self._maybe_request(anchor[0], anchor[1])

    def _maybe_request(self, lat: float, lon: float) -> bool:
        """Throttle by movement and time before spending a tile fetch.

        Returns:
            bool: True when a lookup was actually issued.
        """
        now = time.monotonic()
        if self._inflight is not None:
            return False
        if self._last_query_pos is not None:
            moved = haversine_meters(
                self._last_query_pos[0], self._last_query_pos[1], lat, lon
            )
            if moved < self._min_move and (now - self._last_query_time) < self._min_interval:
                return False

        worker = self._ensure_worker()
        if worker is None:
            return False

        self._last_query_pos = (lat, lon)
        self._last_query_time = now
        self._inflight = (lat, lon)
        # Emit rather than call: a direct call would execute the blocking
        # DEM fetch here on the UI thread.
        self._lookupRequested.emit(lat, lon)
        return True

    @Slot(float, float, object, object)
    def _on_resolved(self, lat: float, lon: float, elevation, undulation=None) -> None:
        """Cache the results and re-emit the latest envelope corrected."""
        self._inflight = None
        key = _cache_key(lat, lon)
        value = float(elevation) if isinstance(elevation, (int, float)) else None
        self._cache[key] = value
        if isinstance(undulation, (int, float)):
            self._geoid_cache[key] = float(undulation)
        while len(self._cache) > _CACHE_MAX_ENTRIES:
            self._cache.popitem(last=False)
        while len(self._geoid_cache) > _CACHE_MAX_ENTRIES:
            self._geoid_cache.popitem(last=False)

        if value is None or not isinstance(self._last_envelope, dict):
            return

        # The publisher started supplying its own AGL while this lookup
        # was in flight. Correcting on top of it would replace a measured
        # value with an inferred one.
        if has_publisher_agl(self._last_envelope):
            return

        # Only re-emit when the aircraft is still near where we queried;
        # otherwise the correction belongs to a stale position.
        current_lat = self._last_envelope.get("aircraft_latitude")
        current_lon = self._last_envelope.get("aircraft_longitude")
        if not _is_coord(current_lat) or not _is_coord(current_lon):
            return
        if haversine_meters(lat, lon, float(current_lat), float(current_lon)) > self._min_move * 2:
            return

        corrected = dict(self._last_envelope)
        if self._apply_elevation(corrected, value):
            self._last_envelope = corrected
            self.envelopeEnriched.emit(corrected)

    def _apply_elevation(self, envelope: dict, elevation) -> bool:
        """Write terrain-derived AGL into ``envelope``. True if changed.

        The AGL lands in :data:`TERRAIN_AGL_KEY`. This method must never
        assign ``aircraft_altitude_agl_m``: that key is the publisher's
        ATO reading, and overwriting it — as this service did until the
        three references were split apart — leaves one field holding
        either meaning with no way to tell which, and destroys the ATO
        value outright.
        """
        if not isinstance(elevation, (int, float)):
            return False

        terrain_here = float(elevation)
        envelope["terrain_elevation_m"] = terrain_here

        # Prefer the anchored path whenever an ATO reading exists. Do
        # NOT fall through to the absolute path when anchoring is merely
        # *not ready yet* — the anchor's own terrain lands a moment later,
        # and until then leaving AGL unresolved is better than a
        # geoid-converted absolute height.
        if _is_coord(envelope.get("aircraft_altitude_agl_m")):
            agl = self._anchored_agl(envelope, terrain_here)
        else:
            agl = self._absolute_agl(envelope, terrain_here)
        if agl is None:
            return False

        # An aircraft cannot be below ground; a small negative is DEM
        # resolution error (AWS Terrain tiles are ~30 m), not a
        # subterranean drone.
        envelope[TERRAIN_AGL_KEY] = max(0.0, agl)
        envelope[AGL_SOURCE_KEY] = AGL_SOURCE_TERRAIN
        return True

    def _anchored_agl(self, envelope: dict, terrain_here: float) -> Optional[float]:
        """Preferred path: measure against the first fix's terrain.

        Uses only the ATO reading and a *difference* of DEM samples, so
        it is immune to whether the aircraft reports ellipsoidal or
        orthometric height. Returns None until the anchor's own terrain
        elevation is known.
        """
        reported = envelope.get("aircraft_altitude_agl_m")
        if not _is_coord(reported) or self._anchor_reported_agl is None:
            return None

        if self._anchor_elevation is None:
            anchor = self._anchor_position
            if anchor is None:
                return None
            cached = self._cache.get(_cache_key(anchor[0], anchor[1]))
            if cached is None:
                # Anchor terrain not resolved yet — a later envelope will
                # pick it up once the lookup lands.
                return None
            self._anchor_elevation = float(cached)

        # Aircraft's true elevation, anchored at the first fix.
        aircraft_elevation = self._anchor_elevation + float(self._anchor_reported_agl)
        # ...advanced by however much the aircraft has climbed since then.
        aircraft_elevation += float(reported) - float(self._anchor_reported_agl)
        return aircraft_elevation - terrain_here

    def _absolute_agl(self, envelope: dict, terrain_here: float) -> Optional[float]:
        """Fallback when no ATO reading exists: MSL − terrain.

        The reported height is GPS-derived and therefore ellipsoidal, so
        the geoid undulation is applied first — skipping that step
        introduces the full undulation as error (−27 m in central Texas,
        enough to report a flying aircraft as underground).

        Uses only the cached undulation resolved alongside the terrain
        sample, so this never blocks.
        """
        msl = envelope.get("aircraft_altitude_msl_m")
        if not _is_coord(msl):
            return None
        lat = envelope.get("aircraft_latitude")
        lon = envelope.get("aircraft_longitude")
        if not _is_coord(lat) or not _is_coord(lon):
            return None

        undulation = self._geoid_cache.get(_cache_key(lat, lon))
        if undulation is None:
            # No geoid data for this spot; correcting with a raw
            # ellipsoidal height would be worse than leaving the
            # reported value alone.
            return None
        # h_ellipsoidal = H_orthometric + N  =>  H = h - N
        orthometric = float(msl) - float(undulation)
        return orthometric - terrain_here


def _cache_key(lat, lon) -> Tuple[float, float]:
    return (round(float(lat), _CACHE_PRECISION), round(float(lon), _CACHE_PRECISION))


def _is_coord(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )
