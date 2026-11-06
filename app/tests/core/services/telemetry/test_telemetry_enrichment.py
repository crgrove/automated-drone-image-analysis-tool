"""Tests for DEM-corrected AGL.

Every test mocks :class:`TerrainService` — no network, no tile fetches
(CLAUDE.md §3.3). The worker thread is driven synchronously by calling
``_on_resolved`` directly, so the tests stay deterministic.

The central behaviour under test is the **datum-free anchoring**: AGL is
derived from the ATO reading plus a *difference* of DEM samples, never
from ``MSL − terrain``. Measured against the project's DJI test flight,
the naive subtraction reported a hovering aircraft as 0 m AGL because
``abs_alt`` is an ellipsoidal GPS height and the local geoid undulation
is −27 m.
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from core.services.telemetry.TelemetryEnrichmentService import (
    AGL_SOURCE_FLIGHT,
    AGL_SOURCE_LASER,
    AGL_SOURCE_REPORTED,
    AGL_SOURCE_TAKEOFF_REFERENCE,
    AGL_SOURCE_TERRAIN,
    AGL_SOURCE_TERRAIN_DEM,
    PUBLISHER_AGL_SOURCE_KEY,
    TERRAIN_AGL_KEY,
    TelemetryEnrichmentService,
    _cache_key,
    has_publisher_agl,
    normalise_agl_source,
    publisher_agl_source,
)


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def service():
    """A service whose DEM worker is a mock — no thread, no network.

    Without this the real ``_ElevationWorker`` spins up a live
    ``TerrainService`` and fetches elevation tiles, which would make these
    tests non-deterministic and network-dependent (CLAUDE.md §3.3).
    Tests drive resolution explicitly via ``_on_resolved``.
    """
    svc = TelemetryEnrichmentService()
    svc._worker = MagicMock()
    svc._ensure_worker = MagicMock(return_value=svc._worker)
    # Lookups are dispatched by emitting ``_lookupRequested`` (a *queued*
    # signal is what keeps the blocking DEM fetch off the caller's thread —
    # calling worker.lookup() directly would run it inline). Record the
    # emissions so throttling can be asserted on the real contract.
    svc.lookup_requests = []
    svc._lookupRequested.connect(
        lambda lat, lon: svc.lookup_requests.append((lat, lon))
    )
    yield svc
    svc.cleanup()


def envelope(lat=30.6487, lon=-97.6759, msl=207.0, agl=14.9,
             agl_terrain=None, source=None):
    """One telemetry fix. ``agl`` is the ATO reading; ``agl_terrain`` is AGL."""
    env = {
        "aircraft_latitude": lat,
        "aircraft_longitude": lon,
        "aircraft_altitude_msl_m": msl,
        "aircraft_altitude_agl_m": agl,
    }
    if agl_terrain is not None:
        env[TERRAIN_AGL_KEY] = agl_terrain
    if source is not None:
        env["agl_source"] = source
    return env


def _seed_terrain(service, lat, lon, elevation):
    """Pretend the DEM worker resolved this position."""
    service._cache[_cache_key(lat, lon)] = elevation


class TestPassthrough:
    def test_returns_immediately_with_the_ato_reading(self, service):
        """The UI thread must never wait on a DEM tile fetch."""
        out = service.enrich(envelope())
        assert out["aircraft_altitude_agl_m"] == pytest.approx(14.9)
        assert out["agl_source"] == AGL_SOURCE_REPORTED
        # No AGL exists yet, and ATO must not be passed off as one.
        assert TERRAIN_AGL_KEY not in out

    def test_does_not_mutate_the_input(self, service):
        original = envelope()
        service.enrich(original)
        assert "agl_source" not in original

    def test_non_dict_passes_through(self, service):
        assert service.enrich(None) is None
        assert service.enrich("nope") == "nope"

    def test_missing_coordinates_are_left_alone(self, service):
        out = service.enrich({"aircraft_altitude_agl_m": 10.0})
        assert out["aircraft_altitude_agl_m"] == 10.0
        assert out.get("terrain_elevation_m") is None


class TestPreferences:
    def test_disabled_preference_skips_terrain(self, service):
        with patch(
            "core.services.SettingsService.SettingsService.get_bool_setting",
            return_value=False,
        ):
            out = service.enrich(envelope())
        assert out.get("terrain_elevation_m") is None
        assert out.get(TERRAIN_AGL_KEY) is None
        assert out["agl_source"] == AGL_SOURCE_REPORTED

    def test_disabled_preference_issues_no_lookup(self, service):
        with patch(
            "core.services.SettingsService.SettingsService.get_bool_setting",
            return_value=False,
        ):
            service.enrich(envelope())
        assert service._inflight is None


class TestAnchoredCorrection:
    """AGL measured against the terrain under the first near-ground fix."""

    def test_flat_terrain_returns_the_reported_value(self, service):
        """Hovering over the takeoff point: correction is a no-op.

        This is the real-flight case that exposed the bug — the naive
        ``MSL − terrain`` gave 0.0 m for an aircraft 14.9 m up.
        """
        lat, lon = 30.6487, -97.6759
        service.enrich(envelope(lat, lon, agl=0.0))  # on the pad: the anchor
        _seed_terrain(service, lat, lon, 215.0)     # DEM at the anchor
        out = service.enrich(envelope(lat, lon))

        assert out["agl_source"] == AGL_SOURCE_TERRAIN
        assert out[TERRAIN_AGL_KEY] == pytest.approx(14.9, abs=0.01)
        assert out["terrain_elevation_m"] == pytest.approx(215.0)
        # ATO belongs to the publisher; enrichment never rewrites it.
        assert out["aircraft_altitude_agl_m"] == pytest.approx(14.9)

    def test_flying_over_lower_ground_increases_agl(self, service):
        """The whole point: terrain drop must add to height above ground."""
        service.enrich(envelope(30.0, -97.0, agl=0.0))     # on the pad
        _seed_terrain(service, 30.0, -97.0, 500.0)   # anchor terrain
        service.enrich(envelope(30.0, -97.0, agl=100.0))

        # Same reported AGL, but now over a valley 200 m lower.
        _seed_terrain(service, 30.1, -97.1, 300.0)
        out = service.enrich(envelope(30.1, -97.1, agl=100.0))

        assert out[TERRAIN_AGL_KEY] == pytest.approx(300.0)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN
        # The regression guard for the destructive overwrite: 100 m of ATO
        # stays 100 m even though AGL is now 300 m.
        assert out["aircraft_altitude_agl_m"] == pytest.approx(100.0)

    def test_flying_over_higher_ground_decreases_agl(self, service):
        service.enrich(envelope(30.0, -97.0, agl=0.0))     # on the pad
        _seed_terrain(service, 30.0, -97.0, 500.0)
        service.enrich(envelope(30.0, -97.0, agl=100.0))

        _seed_terrain(service, 30.1, -97.1, 560.0)
        out = service.enrich(envelope(30.1, -97.1, agl=100.0))

        assert out[TERRAIN_AGL_KEY] == pytest.approx(40.0)
        assert out["aircraft_altitude_agl_m"] == pytest.approx(100.0)

    def test_climbing_is_tracked(self, service):
        service.enrich(envelope(30.0, -97.0, agl=0.0))     # on the pad
        _seed_terrain(service, 30.0, -97.0, 500.0)
        out = service.enrich(envelope(30.0, -97.0, agl=150.0))
        assert out[TERRAIN_AGL_KEY] == pytest.approx(150.0)

    def test_never_reports_below_ground(self, service):
        """DEM resolution error must not produce a subterranean aircraft."""
        service.enrich(envelope(30.0, -97.0, agl=5.0))
        _seed_terrain(service, 30.0, -97.0, 500.0)
        service.enrich(envelope(30.0, -97.0, agl=5.0))

        _seed_terrain(service, 30.1, -97.1, 600.0)
        out = service.enrich(envelope(30.1, -97.1, agl=5.0))
        assert out[TERRAIN_AGL_KEY] == 0.0
        assert out["aircraft_altitude_agl_m"] == pytest.approx(5.0)

    def test_a_first_fix_without_agl_does_not_poison_the_session(self, service):
        """Telemetry fields are individually nullable on the publisher side.

        Anchoring on the first *positioned* fix latched a null reported AGL
        and silently disabled DEM correction for the whole session; the
        anchor must wait for a fix that actually carries an altitude.
        """
        lat, lon = 30.0, -97.0
        # First envelope has a position but no AGL.
        service.enrich({"aircraft_latitude": lat, "aircraft_longitude": lon,
                        "aircraft_altitude_msl_m": 207.0})
        _seed_terrain(service, lat, lon, 500.0)

        # ATO starts arriving from here on.
        service.enrich(envelope(lat, lon, agl=0.0))
        out = service.enrich(envelope(lat, lon, agl=100.0))

        assert service._anchor_reported_agl == pytest.approx(0.0)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN
        assert out[TERRAIN_AGL_KEY] == pytest.approx(100.0)

    def test_a_mid_flight_first_fix_is_not_an_anchor(self, service):
        """A DJI clip almost always starts in the air.

        Anchoring there assumed the ground under the first fix was the
        launch point, so over flat ground "AGL" was the ATO reading under
        another name - 100 ft high on a real clip that opened at 114 m ATO
        over ground 30 m above the launch. No evidence of the takeoff
        elevation means no AGL, not a borrowed ATO.
        """
        service.enrich(envelope(30.0, -97.0, agl=114.0))
        _seed_terrain(service, 30.0, -97.0, 306.0)
        out = service.enrich(envelope(30.0, -97.0, agl=114.0))

        assert service._anchor_position is None
        assert out.get(TERRAIN_AGL_KEY) is None
        assert out["agl_source"] == AGL_SOURCE_REPORTED

    def test_a_later_near_ground_fix_anchors(self, service):
        """A clip that lands, or a feed joined on the pad, anchors there."""
        service.enrich(envelope(30.1, -97.1, agl=114.0))
        service.enrich(envelope(30.0, -97.0, agl=2.0))
        assert service._anchor_position == (30.0, -97.0)

    def test_waits_for_the_anchor_elevation(self, service):
        """Until the anchor's terrain is known, AGL stays unresolved.

        ATO is shown beside it on every surface, so there is nothing to
        gain from publishing the takeoff-relative figure as an AGL in the
        meantime - and no way for it to mislead.
        """
        service.enrich(envelope(30.0, -97.0, agl=0.0))
        # Terrain known here, but NOT at the anchor... which is the same
        # point, so seed a different current position instead.
        _seed_terrain(service, 30.5, -97.5, 400.0)
        out = service.enrich(envelope(30.5, -97.5, agl=50.0))
        assert out["agl_source"] == AGL_SOURCE_REPORTED
        assert out.get(TERRAIN_AGL_KEY) is None
        assert out["aircraft_altitude_agl_m"] == pytest.approx(50.0)


class TestAbsoluteFallback:
    """No ATO reading: MSL − terrain, via the geoid.

    This path is **intentionally unreachable in production**: the DEM
    worker builds its ``TerrainService`` with ``enable_geoid=False``
    because ``GeoidService`` mutates thread-affine PROJ state and killed a
    real session (see :class:`TestTerrainServiceIsolation`), so the
    undulation cache these tests seed is always empty in the running app.
    The coverage documents the arithmetic; it is not a licence to
    re-enable the geoid on the telemetry thread to make it live.
    """

    def test_applies_the_geoid_undulation(self, service):
        """h_ellipsoidal 207.0 with N = −27.1 is 234.1 MSL, not 207.0.

        Measured on the project's DJI test flight; skipping this step put a
        flying aircraft underground.
        """
        lat, lon = 30.0, -97.0
        service.enrich(envelope(lat, lon, msl=207.0, agl=None))
        # Terrain and undulation are resolved together by the worker. These
        # are the values measured at the real test-flight location.
        service._on_resolved(lat, lon, 215.019, -27.103)
        out = service.enrich(envelope(lat, lon, msl=207.0, agl=None))

        # 207.0 − (−27.103) = 234.103 MSL; − 215.019 terrain = 19.08 AGL.
        assert out[TERRAIN_AGL_KEY] == pytest.approx(19.08, abs=0.01)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN

    def test_without_a_geoid_the_reported_value_is_kept(self, service):
        """Subtracting a raw ellipsoidal height would be worse than nothing."""
        lat, lon = 30.0, -97.0
        service.enrich(envelope(lat, lon, msl=207.0, agl=None))
        service._on_resolved(lat, lon, 215.0, None)   # DEM but no geoid
        out = service.enrich(envelope(lat, lon, msl=207.0, agl=None))

        assert out.get("agl_source") != AGL_SOURCE_TERRAIN
        assert out.get(TERRAIN_AGL_KEY) is None
        assert out.get("aircraft_altitude_agl_m") is None


class TestThrottling:
    def test_first_fix_issues_a_lookup(self, service):
        service.enrich(envelope(30.0, -97.0))
        assert len(service.lookup_requests) == 1
        assert service._inflight is not None

    def test_hovering_does_not_re_query(self, service):
        service.enrich(envelope(30.0, -97.0))
        service._on_resolved(30.0, -97.0, 200.0)
        before = len(service.lookup_requests)

        # Same spot again, well inside the movement + interval thresholds.
        service.enrich(envelope(30.0, -97.0))
        assert len(service.lookup_requests) == before

    def test_moving_far_enough_re_queries(self, service):
        service.enrich(envelope(30.0, -97.0))
        service._on_resolved(30.0, -97.0, 200.0)
        before = len(service.lookup_requests)

        service.enrich(envelope(30.01, -97.0))   # ~1.1 km away
        assert len(service.lookup_requests) == before + 1

    def test_only_one_lookup_in_flight(self, service):
        service.enrich(envelope(30.0, -97.0))
        service.enrich(envelope(31.0, -98.0))
        assert len(service.lookup_requests) == 1

    def test_cached_position_needs_no_lookup(self, service):
        _seed_terrain(service, 30.0, -97.0, 200.0)
        service.enrich(envelope(30.0, -97.0))
        assert service.lookup_requests == []

    def test_lookup_is_dispatched_by_signal_not_direct_call(self, service):
        """Regression guard for the UI-thread freeze.

        ``worker.lookup(...)`` executes on the *caller's* thread —
        ``moveToThread`` only reroutes queued signal delivery. Dispatch
        must therefore go through the signal.
        """
        service.enrich(envelope(30.0, -97.0))
        service._worker.lookup.assert_not_called()
        assert service.lookup_requests == [(30.0, -97.0)]


class TestResolution:
    def test_resolved_elevation_is_cached(self, service):
        service.enrich(envelope(30.0, -97.0))
        service._on_resolved(30.0, -97.0, 215.0)
        assert service._cache[_cache_key(30.0, -97.0)] == 215.0

    def test_resolution_re_emits_a_corrected_envelope(self, service):
        emitted = []
        service.envelopeEnriched.connect(emitted.append)

        service.enrich(envelope(30.0, -97.0, agl=5.0))
        service._on_resolved(30.0, -97.0, 400.0)

        assert len(emitted) == 1
        assert emitted[0]["agl_source"] == AGL_SOURCE_TERRAIN

    def test_stale_resolution_is_dropped(self, service):
        """A correction for a position the aircraft has long left is useless."""
        emitted = []
        service.envelopeEnriched.connect(emitted.append)

        service.enrich(envelope(30.0, -97.0))
        service.enrich(envelope(40.0, -100.0))       # far away now
        service._on_resolved(30.0, -97.0, 400.0)     # answer for the old spot

        assert emitted == []

    def test_no_coverage_emits_nothing(self, service):
        emitted = []
        service.envelopeEnriched.connect(emitted.append)
        service.enrich(envelope(30.0, -97.0))
        service._on_resolved(30.0, -97.0, None)
        assert emitted == []

    def test_cache_is_bounded(self, service):
        from core.services.telemetry.TelemetryEnrichmentService import _CACHE_MAX_ENTRIES
        for i in range(_CACHE_MAX_ENTRIES + 50):
            service._on_resolved(30.0 + i * 0.001, -97.0, 200.0)
        assert len(service._cache) <= _CACHE_MAX_ENTRIES


class TestNearbyTerrain:
    """At survey speed the aircraft crosses a ~11 m cache cell twice a second.

    Rendering AGL only from an exact cell hit blanked it on roughly half
    the frames of a real 44 mph clip, so the HUD flickered between a value
    and an em-dash. A miss beside a just-resolved sample uses that sample.
    """

    def test_an_uncached_cell_uses_the_last_resolved_terrain(self, service):
        service.enrich(envelope(30.0, -97.0, agl=2.0))           # anchor
        service._on_resolved(30.0, -97.0, 300.0)
        # ~11 m north: a different cache cell, never looked up.
        out = service.enrich(envelope(30.0001, -97.0, agl=50.0))
        assert out[TERRAIN_AGL_KEY] == pytest.approx(50.0)

    def test_a_distant_cell_does_not(self, service):
        service.enrich(envelope(30.0, -97.0, agl=2.0))
        service._on_resolved(30.0, -97.0, 300.0)
        out = service.enrich(envelope(30.001, -97.0, agl=50.0))  # ~110 m
        assert out.get(TERRAIN_AGL_KEY) is None


class TestLifecycle:
    def test_reset_clears_the_anchor(self, service):
        service.enrich(envelope(30.0, -97.0, agl=5.0))
        assert service._anchor_position is not None
        service.reset()
        assert service._anchor_position is None
        assert service._anchor_reported_agl is None

    def test_reset_keeps_the_cache(self, service):
        """Terrain doesn't move between sessions."""
        _seed_terrain(service, 30.0, -97.0, 200.0)
        service.reset()
        assert _cache_key(30.0, -97.0) in service._cache

    def test_cleanup_is_idempotent(self, service):
        service.cleanup()
        service.cleanup()


class TestTerrainServiceIsolation:
    """Each worker owns its TerrainService; it is never shared across threads.

    Regression guard for a hard crash: ``TerrainService`` caches a
    ``pyproj.Transformer`` inside its ``GeoidService``, and PROJ contexts
    are thread-affine. Sharing one instance between the Qt main thread and
    the DEM worker faulted the process with an access violation inside
    ``pyproj.transformer.__call__`` the moment playback and a terrain
    lookup overlapped.
    """

    def test_each_worker_builds_its_own(self):
        import sys
        mod = sys.modules["core.services.telemetry.TelemetryEnrichmentService"]

        built = []

        class FakeTerrain:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                built.append(self)

        with patch("core.services.terrain.TerrainService", FakeTerrain):
            first = mod._ElevationWorker()
            second = mod._ElevationWorker()
            a = first._get_terrain_service()
            b = second._get_terrain_service()

        assert a is not b
        assert len(built) == 2

    def test_one_worker_reuses_its_own(self):
        import sys
        mod = sys.modules["core.services.telemetry.TelemetryEnrichmentService"]
        built = []

        class FakeTerrain:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                built.append(self)

        with patch("core.services.terrain.TerrainService", FakeTerrain):
            worker = mod._ElevationWorker()
            assert worker._get_terrain_service() is worker._get_terrain_service()
        assert len(built) == 1

    def test_construction_failure_is_remembered(self):
        import sys
        mod = sys.modules["core.services.telemetry.TelemetryEnrichmentService"]
        attempts = []

        def boom(**_kwargs):
            attempts.append(1)
            raise RuntimeError("no terrain here")

        with patch("core.services.terrain.TerrainService", boom):
            worker = mod._ElevationWorker()
            assert worker._get_terrain_service() is None
            assert worker._get_terrain_service() is None

        # Retried once, then latched off rather than re-raising per fix.
        assert len(attempts) == 1

    def test_geoid_is_disabled_on_the_worker(self):
        """Regression guard for a hard crash.

        ``GeoidService`` mutates global PROJ state and caches a
        thread-affine ``pyproj.Transformer``. Reaching it from the DEM
        worker killed a real playback session with
        ``Windows fatal exception: access violation`` inside
        ``pyproj.transformer.__call__``. The anchored AGL uses differences
        of DEM samples, so the geoid buys nothing here.
        """
        import sys
        mod = sys.modules["core.services.telemetry.TelemetryEnrichmentService"]
        built = []

        class FakeTerrain:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                built.append(self)

        with patch("core.services.terrain.TerrainService", FakeTerrain):
            mod._ElevationWorker()._get_terrain_service()

        assert built[0].kwargs.get("enable_geoid") is False


class TestPublisherSuppliedAgl:
    """ADIAT Flight's AGL is measured; Desktop's is inferred. Flight wins.

    Flight anchors its differential DEM at the true takeoff point and may
    instead be reading a laser or the downward sensor, so there is nothing
    for this service to add — and every lookup it skips is a tile it does
    not fetch over a metered field connection.
    """

    def test_publisher_agl_is_kept_and_labelled(self, service):
        out = service.enrich(envelope(30.0, -97.0, agl=100.0, agl_terrain=87.5))
        assert out[TERRAIN_AGL_KEY] == pytest.approx(87.5)
        assert out["agl_source"] == AGL_SOURCE_FLIGHT
        assert out["aircraft_altitude_agl_m"] == pytest.approx(100.0)

    def test_publisher_agl_issues_no_dem_lookup(self, service):
        service.enrich(envelope(30.0, -97.0, agl=100.0, agl_terrain=87.5))
        assert service.lookup_requests == []
        assert service._inflight is None

    def test_named_measurement_sources_are_trusted(self, service):
        out = service.enrich(envelope(
            30.0, -97.0, agl=100.0, agl_terrain=87.5, source="LASER",
        ))
        assert out["agl_source"] == AGL_SOURCE_LASER
        assert out[TERRAIN_AGL_KEY] == pytest.approx(87.5)
        assert service.lookup_requests == []

    def test_takeoff_reference_still_enriches(self, service):
        """The publisher found no terrain source — ours may still cover it.

        Desktop's DEM is fetched on demand; Flight's tiles are pre-cached,
        so the two disagree about coverage in both directions.
        """
        service.enrich(envelope(
            30.0, -97.0, agl=100.0, agl_terrain=100.0,
            source="TAKEOFF_REFERENCE",
        ))
        assert service.lookup_requests == [(30.0, -97.0)]

    def test_takeoff_reference_agl_is_replaced_by_ours(self, service):
        env = dict(agl=100.0, agl_terrain=100.0, source="TAKEOFF_REFERENCE")
        service.enrich(envelope(30.0, -97.0, agl=0.0, agl_terrain=0.0,
                                source="TAKEOFF_REFERENCE"))   # on the pad
        _seed_terrain(service, 30.0, -97.0, 500.0)
        service.enrich(envelope(30.0, -97.0, **env))

        _seed_terrain(service, 30.1, -97.1, 300.0)
        out = service.enrich(envelope(30.1, -97.1, **env))
        assert out[TERRAIN_AGL_KEY] == pytest.approx(300.0)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN

    def test_missing_publisher_agl_falls_through(self, service):
        """Flight sends the key as null outside its DEM coverage."""
        env = envelope(30.0, -97.0, agl=100.0)
        env[TERRAIN_AGL_KEY] = None
        service.enrich(env)
        assert service.lookup_requests == [(30.0, -97.0)]

    def test_our_own_output_stays_correctable(self, service):
        """``terrain`` must never count as trusted.

        The aircraft moves over new ground constantly; treating this
        service's own last answer as authoritative would freeze the AGL at
        whatever the first corrected fix said.
        """
        service.enrich(envelope(30.0, -97.0, agl=0.0))     # on the pad
        _seed_terrain(service, 30.0, -97.0, 500.0)
        first = service.enrich(envelope(30.0, -97.0, agl=100.0))
        assert first["agl_source"] == AGL_SOURCE_TERRAIN

        _seed_terrain(service, 30.1, -97.1, 400.0)
        second = service.enrich(envelope(30.1, -97.1, agl=100.0))
        assert second[TERRAIN_AGL_KEY] == pytest.approx(200.0)

    def test_in_flight_correction_never_overwrites_a_publisher_agl(self, service):
        """A lookup started before the publisher's AGL arrived must not win."""
        emitted = []
        service.envelopeEnriched.connect(emitted.append)

        service.enrich(envelope(30.0, -97.0, agl=100.0))       # issues a lookup
        service.enrich(envelope(30.0, -97.0, agl=100.0, agl_terrain=87.5))
        service._on_resolved(30.0, -97.0, 400.0)

        assert emitted == []

    def test_the_anchor_is_recorded_during_pass_through(self, service):
        """The takeoff point is the only anchor worth having.

        Deferring anchor bookkeeping until the first fix that needs a DEM
        lookup would anchor wherever the aircraft was when the publisher
        stopped resolving AGL — mid-flight, possibly over a ridge, which is
        the exact failure the anchored path exists to avoid.
        """
        service.enrich(envelope(30.0, -97.0, agl=0.0, agl_terrain=0.0))
        service.enrich(envelope(30.1, -97.1, agl=120.0, agl_terrain=95.0))

        assert service._anchor_position == (30.0, -97.0)
        assert service._anchor_reported_agl == pytest.approx(0.0)

    def test_the_anchor_tile_is_fetched_when_the_publisher_drops_out(self, service):
        """Losing the publisher's AGL mid-flight must not lose AGL entirely.

        No lookup happens while Flight supplies AGL, so the anchor's own
        elevation is unknown when the fallback is first needed; without
        fetching it the anchored path could never resolve and the HUD would
        show no AGL for the rest of the session.
        """
        service.enrich(envelope(30.0, -97.0, agl=0.0, agl_terrain=0.0))
        assert service.lookup_requests == []

        # Publisher leaves its DEM coverage: AGL stops arriving.
        service.enrich(envelope(30.1, -97.1, agl=120.0))
        assert service.lookup_requests == [(30.0, -97.0)]   # the anchor

        service._on_resolved(30.0, -97.0, 500.0)
        _seed_terrain(service, 30.1, -97.1, 380.0)
        out = service.enrich(envelope(30.1, -97.1, agl=120.0))
        assert out[TERRAIN_AGL_KEY] == pytest.approx(240.0)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN


class TestSourceVocabulary:
    """Provenance names normalise at the ingest boundary, in one place."""

    @pytest.mark.parametrize("wire,expected", [
        ("LASER", "laser"),
        ("ULTRASONIC", "ultrasonic"),
        ("TERRAIN_DEM", "terrain_dem"),
        ("TAKEOFF_REFERENCE", AGL_SOURCE_TAKEOFF_REFERENCE),
        ("terrain", AGL_SOURCE_TERRAIN),
        ("  Laser  ", "laser"),
    ])
    def test_known_sources_normalise(self, wire, expected):
        assert normalise_agl_source(wire) == expected

    def test_unknown_source_passes_through(self):
        """A source name from a future Flight build must not vanish.

        Dropping it would erase the provenance of a value still being
        shown; passing it through degrades to "recorded and displayed, but
        not specially rendered".
        """
        assert normalise_agl_source("RADAR_ALTIMETER") == "radar_altimeter"

    @pytest.mark.parametrize("value", [None, 42, True, "", "   ", object()])
    def test_junk_is_dropped(self, value):
        assert normalise_agl_source(value) is None

    def test_unknown_source_is_still_enriched(self, service):
        """Unrecognised provenance is not a licence to trust the value."""
        service.enrich(envelope(
            30.0, -97.0, agl=100.0, agl_terrain=90.0, source="RADAR",
        ))
        assert service.lookup_requests == [(30.0, -97.0)]

    def test_publisher_source_is_not_overwritten(self, service):
        out = service.enrich(envelope(
            30.0, -97.0, agl=100.0, agl_terrain=90.0, source="ULTRASONIC",
        ))
        assert out["agl_source"] == "ultrasonic"


class TestHasPublisherAgl:
    """The predicate every surface uses to decide whose AGL is on screen."""

    def test_no_agl_key_is_false(self):
        assert has_publisher_agl({"aircraft_altitude_agl_m": 100.0}) is False

    def test_null_agl_is_false(self):
        assert has_publisher_agl({TERRAIN_AGL_KEY: None}) is False

    def test_bare_agl_is_true(self):
        """Flight publishes no source name; the key's presence is the marker."""
        assert has_publisher_agl({TERRAIN_AGL_KEY: 42.0}) is True

    @pytest.mark.parametrize("source,expected", [
        ("flight", True),
        ("laser", True),
        ("ultrasonic", True),
        ("terrain_dem", True),
        ("takeoff_reference", False),
        ("terrain", False),
        ("reported", False),
        ("something_new", False),
    ])
    def test_source_decides_when_present(self, source, expected):
        env = {TERRAIN_AGL_KEY: 42.0, "agl_source": source}
        assert has_publisher_agl(env) is expected

    def test_non_dict_is_false(self):
        assert has_publisher_agl(None) is False
        assert has_publisher_agl("nope") is False


class TestPublisherSourceKey:
    """ADIAT Flight names its AGL source on ``aircraft_altitude_agl_source``.

    Desktop folds that into its own ``agl_source`` at ingest so there is
    one provenance name internally, in ``telemetry.csv`` and in the HUD -
    rather than two keys meaning the same thing.
    """

    def test_the_wire_key_is_folded_into_agl_source(self, service):
        env = envelope(30.0, -97.0, agl=100.0, agl_terrain=87.5)
        env[PUBLISHER_AGL_SOURCE_KEY] = "TERRAIN_DEM"
        out = service.enrich(env)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN_DEM

    def test_the_raw_wire_key_is_left_in_the_envelope(self, service):
        """``telemetry.jsonl`` stays a faithful record of what arrived."""
        env = envelope(30.0, -97.0, agl=100.0, agl_terrain=87.5)
        env[PUBLISHER_AGL_SOURCE_KEY] = "LASER"
        out = service.enrich(env)
        assert out[PUBLISHER_AGL_SOURCE_KEY] == "LASER"

    @pytest.mark.parametrize("wire", ["LASER", "ULTRASONIC", "TERRAIN_DEM"])
    def test_measured_sources_skip_the_dem_lookup(self, service, wire):
        env = envelope(30.0, -97.0, agl=100.0, agl_terrain=87.5)
        env[PUBLISHER_AGL_SOURCE_KEY] = wire
        out = service.enrich(env)
        assert out[TERRAIN_AGL_KEY] == pytest.approx(87.5)
        assert service.lookup_requests == []

    def test_takeoff_reference_with_a_null_agl_still_enriches(self, service):
        """Flight looked for a terrain source and found none.

        Its DEM tiles are pre-cached and Desktop's are fetched on demand,
        so this is exactly the case where Desktop can cover ground Flight
        cannot - the reason the source is sent unconditionally rather than
        inferred from a null AGL.
        """
        env = envelope(30.0, -97.0, agl=100.0)
        env[TERRAIN_AGL_KEY] = None
        env[PUBLISHER_AGL_SOURCE_KEY] = "TAKEOFF_REFERENCE"
        out = service.enrich(env)

        assert out["agl_source"] == AGL_SOURCE_TAKEOFF_REFERENCE
        assert service.lookup_requests == [(30.0, -97.0)]

    def test_an_older_publisher_stays_distinguishable(self, service):
        """No source key at all is a different state from TAKEOFF_REFERENCE.

        Both carry a null AGL and both get a lookup, so the behaviour is
        the same - but only one of them can be reported to the operator as
        "the aircraft looked and there was no terrain source".
        """
        env = envelope(30.0, -97.0, agl=100.0)
        env[TERRAIN_AGL_KEY] = None
        out = service.enrich(env)

        assert out["agl_source"] == AGL_SOURCE_REPORTED
        assert service.lookup_requests == [(30.0, -97.0)]

    def test_desktops_own_source_wins_over_the_wire_key(self, service):
        """Once enrichment resolves an AGL, it owns the provenance.

        The wire key describes the publisher's attempt, which Desktop has
        just superseded; reading it back afterwards would relabel a
        desktop-DEM value as the publisher's.
        """
        env = dict(agl=100.0)
        first = envelope(30.0, -97.0, agl=0.0)                  # on the pad
        first[PUBLISHER_AGL_SOURCE_KEY] = "TAKEOFF_REFERENCE"
        service.enrich(first)
        _seed_terrain(service, 30.0, -97.0, 500.0)

        second = envelope(30.0, -97.0, **env)
        second[PUBLISHER_AGL_SOURCE_KEY] = "TAKEOFF_REFERENCE"
        out = service.enrich(second)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN
        assert out[TERRAIN_AGL_KEY] == pytest.approx(100.0)

    def test_an_unknown_wire_source_is_recorded_but_not_trusted(self, service):
        env = envelope(30.0, -97.0, agl=100.0, agl_terrain=90.0)
        env[PUBLISHER_AGL_SOURCE_KEY] = "RADAR_ALTIMETER"
        out = service.enrich(env)
        assert out["agl_source"] == "radar_altimeter"
        assert service.lookup_requests == [(30.0, -97.0)]

    def test_publisher_agl_source_reads_either_key(self):
        assert publisher_agl_source({"agl_source": "TERRAIN"}) == "terrain"
        assert publisher_agl_source(
            {PUBLISHER_AGL_SOURCE_KEY: "LASER"}) == AGL_SOURCE_LASER
        assert publisher_agl_source({}) is None
        assert publisher_agl_source(None) is None

    def test_desktop_key_takes_precedence(self):
        env = {"agl_source": "terrain", PUBLISHER_AGL_SOURCE_KEY: "LASER"}
        assert publisher_agl_source(env) == AGL_SOURCE_TERRAIN


class TestTakeoffCoordinateAnchor:
    """Tier 2: the differential anchored at the published launch point.

    Positions are datum-free where elevations are not: Desktop samples its
    own DEM at the takeoff coordinates and under the aircraft, and any
    datum offset cancels in the difference. ADIAT Flight records the
    position on the takeoff rising edge, so the anchor is the true launch
    point however late this viewer connected.
    """

    TAKEOFF = (30.6540, -97.9530)

    def _with_takeoff(self, lat=30.1, lon=-97.1, ato=120.0):
        env = envelope(lat, lon, agl=ato)
        env["takeoff_latitude"] = self.TAKEOFF[0]
        env["takeoff_longitude"] = self.TAKEOFF[1]
        return env

    def test_the_takeoff_point_is_the_anchor_not_the_first_fix(self, service):
        """The flaw this retires: connecting mid-flight over a ridge.

        First fix arrives over a 500 m ridge; the launch point is a 311 m
        valley. The anchor must be the valley: camera = 311 + ATO.
        """
        service.enrich(self._with_takeoff(30.0, -97.0, ato=120.0))
        assert service._anchor_position == self.TAKEOFF
        assert service._anchor_reported_agl == 0.0

        _seed_terrain(service, *self.TAKEOFF, 311.0)
        _seed_terrain(service, 30.0, -97.0, 500.0)
        out = service.enrich(self._with_takeoff(30.0, -97.0, ato=120.0))

        # camera = 311 + 120 = 431; over the 500 m ridge that is below
        # ground, floored to the service's 0.0 - the honest answer for an
        # aircraft 69 m under the ridge top, not a ridge-anchored fantasy
        # of 120 m that the first-fix rule would have produced.
        assert out[TERRAIN_AGL_KEY] == pytest.approx(0.0)

    def test_agl_is_dem_takeoff_plus_ato_minus_dem_here(self, service):
        _seed_terrain(service, *self.TAKEOFF, 311.0)
        _seed_terrain(service, 30.1, -97.1, 380.0)
        service.enrich(self._with_takeoff(ato=120.0))
        out = service.enrich(self._with_takeoff(ato=120.0))
        # 311 + 120 - 380 = 51.
        assert out[TERRAIN_AGL_KEY] == pytest.approx(51.0)
        assert out["agl_source"] == AGL_SOURCE_TERRAIN

    def test_a_takeoff_anchor_supersedes_a_first_fix_anchor(self, service):
        """An old-build session upgraded mid-flight by a newer publisher."""
        service.enrich(envelope(30.0, -97.0, agl=0.0))     # near-ground anchor
        assert service._anchor_position == (30.0, -97.0)

        service.enrich(self._with_takeoff())
        assert service._anchor_position == self.TAKEOFF
        assert service._anchor_reported_agl == 0.0

    def test_a_first_fix_never_replaces_the_takeoff_anchor(self, service):
        service.enrich(self._with_takeoff())
        service.enrich(envelope(30.2, -97.2, agl=90.0))    # no takeoff keys
        assert service._anchor_position == self.TAKEOFF

    def test_moved_takeoff_coordinates_re_anchor(self, service):
        """A new launch in the same viewing session is a new anchor."""
        service.enrich(self._with_takeoff())
        _seed_terrain(service, *self.TAKEOFF, 311.0)
        # The anchor elevation resolves during a correction, which needs
        # the current position's terrain cached too.
        _seed_terrain(service, 30.1, -97.1, 380.0)
        service.enrich(self._with_takeoff())
        assert service._anchor_elevation == pytest.approx(311.0)

        moved = envelope(30.1, -97.1, agl=50.0)
        moved["takeoff_latitude"] = 30.7000
        moved["takeoff_longitude"] = -97.8000
        service.enrich(moved)
        assert service._anchor_position == (30.7000, -97.8000)
        # The old point's elevation must not describe the new one.
        assert service._anchor_elevation is None

    def test_adopted_even_while_the_publisher_supplies_agl(self, service):
        """Tier 1 active, tier 2 armed: the publisher dropping out must
        leave the fallback anchored at the launch, not at the dropout."""
        env = self._with_takeoff(ato=120.0)
        env[TERRAIN_AGL_KEY] = 95.0
        service.enrich(env)
        assert service._anchor_position == self.TAKEOFF
        assert service._anchor_reported_agl == 0.0

    def test_junk_coordinates_are_ignored(self, service):
        env = envelope(30.0, -97.0, agl=0.0)
        env["takeoff_latitude"] = "not-a-number"
        env["takeoff_longitude"] = None
        service.enrich(env)
        # Falls back to the near-ground rule.
        assert service._anchor_position == (30.0, -97.0)
        assert service._anchor_reported_agl == pytest.approx(0.0)

    def test_absent_fields_keep_legacy_behaviour(self, service):
        """Publishers that predate the fields anchor on a near-ground fix."""
        service.enrich(envelope(30.0, -97.0, agl=0.0))
        assert service._anchor_position == (30.0, -97.0)
        assert service._anchor_is_takeoff is False

    def test_reset_clears_the_takeoff_anchor(self, service):
        service.enrich(self._with_takeoff())
        service.reset()
        assert service._anchor_position is None
        assert service._anchor_is_takeoff is False
