"""Tests for automatic elevation-data acquisition.

No network: strategies are faked or their transport is (CLAUDE.md §3.3).
What is under test is the contract that makes one service safe to call from
every trigger point:

* the gates are the app's own settings, checked in one place, for every
  elevation source;
* the same call from analysis, viewer open and export does the work once;
* nothing raises into the caller, whatever the source does.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from core.services.terrain.TerrainAcquisitionService import (
    DEFAULT_MAX_MB,
    SETTING_ENABLED,
    SETTING_MAX_MB,
    SETTING_OFFLINE_ONLY,
    SETTING_PROVIDER,
    SETTING_USE_TERRAIN,
    SKIP_ALREADY_TRIED,
    SKIP_COVERED,
    SKIP_NO_AREA,
    SKIP_NO_NETWORK,
    SKIP_OFFLINE,
    SKIP_TERRAIN_DISABLED,
    SKIP_UNSUPPORTED,
    TRIGGER_ANALYSIS,
    TRIGGER_EXPORT,
    TRIGGER_VIEWER_OPEN,
    AcquisitionOutcome,
    TerrainAcquisitionService,
    TerrariumStrategy,
    Usgs3depStrategy,
    reset_attempt_history,
)
from core.services.terrain.TerrainProviderFactory import (
    PROVIDER_TERRARIUM,
    PROVIDER_USGS_3DEP_LOCAL,
)
from core.services.terrain.TileFetchService import FetchResult

BOUNDS = (-97.7505, 30.6495, -97.7395, 30.6595)


@pytest.fixture(autouse=True)
def clean_state():
    """Attempt history and the connectivity probe are process-wide."""
    reset_attempt_history()
    TerrainAcquisitionService.reset_connectivity()
    yield
    reset_attempt_history()
    TerrainAcquisitionService.reset_connectivity()


class FakeSettings:
    def __init__(self, **values):
        self.values = dict(values)
        self.writes = {}

    def get_setting(self, name, default=None):
        return self.values.get(name, default)

    def get_bool_setting(self, name, default=False):
        return bool(self.values.get(name, default))

    def set_setting(self, name, value):
        self.values[name] = value
        self.writes[name] = value


def settings(**overrides):
    """Default-on settings: terrain used, online, acquisition allowed."""
    values = {SETTING_USE_TERRAIN: True, SETTING_OFFLINE_ONLY: False,
              SETTING_ENABLED: True}
    values.update(overrides)
    return FakeSettings(**values)


class FakeStrategy:
    """A stand-in elevation source, recording what it was asked to do."""

    provider_id = 'fake_provider'
    label = 'Fake DEM'

    def __init__(self, size_mb=1.0, covered=False, written=3, boom=None):
        self.size_mb = size_mb
        self.covered = covered
        self.written = written
        self.boom = boom
        self.calls = []

    def estimate_mb(self, bounds):
        return self.size_mb

    def already_covered(self, bounds):
        return self.covered

    def out_dir(self):
        return '/tmp/library'

    def acquire(self, plan, progress_callback=None, cancel_check=None):
        self.calls.append(plan)
        if self.boom is not None:
            raise self.boom
        return AcquisitionOutcome(plan=plan, tiles_written=self.written,
                                  registered=True)


def service(strategy=None, settings_service=None, online=True):
    svc = TerrainAcquisitionService(
        settings_service=(settings_service if settings_service is not None
                          else settings()),
        logger=MagicMock(),
        strategy=strategy if strategy is not None else FakeStrategy(),
    )
    TerrainAcquisitionService._online_checked = True
    TerrainAcquisitionService._online = online
    return svc


class TestSettingGates:
    """One gate set, applied identically to every source and trigger."""

    def test_terrain_toggle_off_stops_everything(self):
        """Flat-terrain positioning was asked for; no elevation is wanted."""
        strategy = FakeStrategy()
        svc = service(strategy, settings(**{SETTING_USE_TERRAIN: False}))
        outcome = svc.run(bounds=BOUNDS)

        assert outcome.skipped_reason == SKIP_TERRAIN_DISABLED
        assert strategy.calls == []

    def test_offline_only_stops_everything(self):
        """The same floor TerrainService honours for individual lookups."""
        strategy = FakeStrategy()
        svc = service(strategy, settings(**{SETTING_OFFLINE_ONLY: True}))
        outcome = svc.run(bounds=BOUNDS)

        assert outcome.skipped_reason == SKIP_OFFLINE
        assert strategy.calls == []

    def test_acquisition_can_be_switched_off_on_its_own(self):
        strategy = FakeStrategy()
        svc = service(strategy, settings(**{SETTING_ENABLED: False}))
        assert svc.run(bounds=BOUNDS).skipped_reason is not None
        assert strategy.calls == []

    def test_enabled_needs_all_three(self):
        assert service(settings_service=settings()).enabled() is True
        assert service(settings_service=settings(
            **{SETTING_USE_TERRAIN: False})).enabled() is False
        assert service(settings_service=settings(
            **{SETTING_OFFLINE_ONLY: True})).enabled() is False
        assert service(settings_service=settings(
            **{SETTING_ENABLED: False})).enabled() is False

    def test_no_settings_service_uses_the_documented_defaults(self):
        svc = TerrainAcquisitionService(logger=MagicMock(), strategy=FakeStrategy())
        assert svc.terrain_enabled() is True
        assert svc.offline_only() is False
        assert svc.max_mb() == DEFAULT_MAX_MB

    def test_no_connectivity_stops_the_download(self):
        strategy = FakeStrategy()
        svc = service(strategy, online=False)
        assert svc.run(bounds=BOUNDS).skipped_reason == SKIP_NO_NETWORK
        assert strategy.calls == []

    def test_connectivity_is_probed_once_per_process(self):
        """The probe is itself a request; every trigger would repeat it."""
        TerrainAcquisitionService.reset_connectivity()
        cache = MagicMock()
        cache.is_online.return_value = True
        svc = TerrainAcquisitionService(settings_service=settings(),
                                        logger=MagicMock(),
                                        strategy=FakeStrategy(),
                                        cache_service=cache)
        assert svc.online() is True
        assert svc.online() is True
        assert cache.is_online.call_count == 1

    def test_a_failed_probe_counts_as_online(self):
        """A false negative would disable acquisition for the whole session."""
        TerrainAcquisitionService.reset_connectivity()
        cache = MagicMock()
        cache.is_online.side_effect = RuntimeError("dns down")
        svc = TerrainAcquisitionService(settings_service=settings(),
                                        logger=MagicMock(),
                                        strategy=FakeStrategy(),
                                        cache_service=cache)
        assert svc.online() is True


class TestPlanning:
    def test_an_explicit_bbox_needs_no_imagery(self):
        plan, reason = service().plan(bounds=BOUNDS)
        assert reason is None
        assert plan.bounds == BOUNDS
        assert plan.detail == 'Fake DEM'

    def test_imagery_bounds_are_derived_and_padded(self, monkeypatch):
        monkeypatch.setattr('core.services.coverage.aoi.compute_mission_gps_bounds',
                            lambda images, *a, **k: BOUNDS)
        monkeypatch.setattr('core.services.coverage.aoi.suggest_buffer_m',
                            lambda images, *a, **k: 50.0)
        plan, reason = service().plan(images=[{'path': 'a.jpg'}])
        assert reason is None
        assert plan.bounds[0] < BOUNDS[0]

    def test_no_area_is_a_quiet_skip(self):
        plan, reason = service().plan(images=[])
        assert plan is None
        assert reason == SKIP_NO_AREA

    def test_imagery_without_gps_is_a_quiet_skip(self, monkeypatch):
        monkeypatch.setattr('core.services.coverage.aoi.compute_mission_gps_bounds',
                            lambda images, *a, **k: None)
        plan, reason = service().plan(images=[{'path': 'a.jpg'}])
        assert plan is None
        assert reason == SKIP_NO_AREA

    def test_an_already_covered_area_is_skipped(self):
        plan, reason = service(FakeStrategy(covered=True)).plan(bounds=BOUNDS)
        assert plan is None
        assert reason == SKIP_COVERED

    def test_an_oversized_download_is_refused(self):
        """Nobody is watching an automatic download start."""
        plan, reason = service(FakeStrategy(size_mb=5000.0)).plan(bounds=BOUNDS)
        assert plan is None
        assert "exceeds" in reason

    def test_the_size_cap_is_configurable(self):
        svc = service(FakeStrategy(size_mb=10.0),
                      settings(**{SETTING_MAX_MB: 5}))
        plan, reason = svc.plan(bounds=BOUNDS)
        assert plan is None
        assert "exceeds" in reason

    def test_a_junk_size_cap_falls_back_to_the_default(self):
        svc = service(settings_service=settings(**{SETTING_MAX_MB: 'plenty'}))
        assert svc.max_mb() == DEFAULT_MAX_MB

    def test_an_unknown_provider_needs_no_download(self):
        svc = TerrainAcquisitionService(
            settings_service=settings(**{SETTING_PROVIDER: 'something_new'}),
            logger=MagicMock())
        plan, reason = svc.plan(bounds=BOUNDS)
        assert plan is None
        assert reason == SKIP_UNSUPPORTED

    def test_broken_bounds_derivation_never_raises(self, monkeypatch):
        def boom(images):
            raise RuntimeError("exif exploded")
        monkeypatch.setattr('core.services.coverage.aoi.compute_mission_gps_bounds',
                            boom)
        plan, reason = service().plan(images=[{'path': 'a.jpg'}])
        assert plan is None
        assert reason == SKIP_NO_AREA


class TestTriggerConsistency:
    """The point of standardizing the triggers: ask often, work once."""

    @pytest.mark.parametrize("trigger", [
        TRIGGER_ANALYSIS, TRIGGER_VIEWER_OPEN, TRIGGER_EXPORT])
    def test_every_trigger_behaves_identically(self, trigger):
        strategy = FakeStrategy()
        outcome = service(strategy).run(bounds=BOUNDS, trigger=trigger)
        assert outcome.acquired is True
        assert outcome.trigger == trigger
        assert len(strategy.calls) == 1

    def test_a_second_trigger_for_the_same_area_does_nothing(self):
        """Analysis, then opening the viewer, then exporting: one download."""
        strategy = FakeStrategy()
        first = service(strategy).run(bounds=BOUNDS, trigger=TRIGGER_ANALYSIS)
        second = service(strategy).run(bounds=BOUNDS, trigger=TRIGGER_VIEWER_OPEN)
        third = service(strategy).run(bounds=BOUNDS, trigger=TRIGGER_EXPORT)

        assert first.acquired is True
        assert second.skipped_reason == SKIP_ALREADY_TRIED
        assert third.skipped_reason == SKIP_ALREADY_TRIED
        assert len(strategy.calls) == 1

    def test_a_different_area_is_still_attempted(self):
        strategy = FakeStrategy()
        service(strategy).run(bounds=BOUNDS)
        elsewhere = (-105.0, 39.5, -104.99, 39.51)
        service(strategy).run(bounds=elsewhere)
        assert len(strategy.calls) == 2

    def test_a_failed_attempt_is_not_retried_on_every_trigger(self):
        """A source that is down must not be re-probed by each export."""
        strategy = FakeStrategy(boom=RuntimeError("socket died"))
        first = service(strategy).run(bounds=BOUNDS)
        second = service(strategy).run(bounds=BOUNDS)
        assert "socket died" in first.skipped_reason
        assert second.skipped_reason == SKIP_ALREADY_TRIED
        assert len(strategy.calls) == 1


class TestErrorTolerance:
    def test_a_strategy_that_raises_is_reported_not_propagated(self):
        strategy = FakeStrategy(boom=RuntimeError("socket died"))
        outcome = service(strategy).run(bounds=BOUNDS)
        assert outcome.acquired is False
        assert "socket died" in outcome.skipped_reason

    def test_a_broken_settings_service_is_survivable(self):
        broken = MagicMock()
        broken.get_bool_setting.side_effect = RuntimeError("registry gone")
        broken.get_setting.side_effect = RuntimeError("registry gone")
        svc = TerrainAcquisitionService(settings_service=broken,
                                        logger=MagicMock(),
                                        strategy=FakeStrategy())
        # Defaults apply and nothing escapes.
        assert svc.terrain_enabled() is True
        assert svc.max_mb() == DEFAULT_MAX_MB

    def test_cancel_check_reaches_the_strategy(self):
        strategy = MagicMock()
        strategy.provider_id = 'fake_provider'
        strategy.label = 'Fake DEM'
        strategy.estimate_mb.return_value = 1.0
        strategy.already_covered.return_value = False
        strategy.out_dir.return_value = None
        strategy.acquire.return_value = AcquisitionOutcome(cancelled=True)

        service(strategy).run(bounds=BOUNDS, cancel_check=lambda: True)
        assert strategy.acquire.call_args.kwargs['cancel_check'] is not None


class TestTerrariumStrategy:
    """The online default: prefetch the working area, same tiles, sooner."""

    def _strategy(self, cache):
        return TerrariumStrategy(settings_service=settings(),
                                 logger=MagicMock(), cache_service=cache,
                                 zoom=12)

    def test_coverage_is_measured_in_missing_tiles(self):
        cache = MagicMock()
        cache.count_missing_tiles.return_value = 0
        assert self._strategy(cache).already_covered(BOUNDS) is True
        cache.count_missing_tiles.return_value = 3
        assert self._strategy(cache).already_covered(BOUNDS) is False

    def test_a_cache_probe_failure_is_not_coverage(self):
        cache = MagicMock()
        cache.count_missing_tiles.side_effect = OSError("cache dir gone")
        assert self._strategy(cache).already_covered(BOUNDS) is False

    def test_the_estimate_is_a_handful_of_tiles(self):
        """A flight area at zoom 12 is a few ~10 km tiles - not megabytes."""
        cache = MagicMock()
        assert self._strategy(cache).estimate_mb(BOUNDS) < 1.0

    def test_acquire_prefetches_the_bbox(self):
        cache = MagicMock()
        cache.prefetch_bounds.return_value = 4
        strategy = self._strategy(cache)
        plan = SimpleNamespace(bounds=BOUNDS, detail='x', out_dir=None)
        outcome = strategy.acquire(plan)

        assert outcome.tiles_written == 4
        assert cache.prefetch_bounds.call_args.args[0] == BOUNDS
        assert cache.prefetch_bounds.call_args.kwargs['zoom'] == 12

    def test_a_prefetch_failure_is_reported_not_raised(self):
        cache = MagicMock()
        cache.prefetch_bounds.side_effect = RuntimeError("http dead")
        plan = SimpleNamespace(bounds=BOUNDS, detail='x', out_dir=None)
        outcome = self._strategy(cache).acquire(plan)
        assert outcome.tiles_written == 0
        assert "http dead" in outcome.skipped_reason


class TestUsgs3depStrategy:
    def _strategy(self, fetch=None, settings_service=None):
        return Usgs3depStrategy(
            settings_service=(settings_service if settings_service is not None
                              else settings()),
            logger=MagicMock(), fetch_service=fetch or MagicMock())

    def test_one_square_km_at_one_metre_is_about_four_mb(self):
        mb = self._strategy().estimate_mb(
            (-97.0, 30.0, -97.0 + 1000 / 96500.0, 30.0 + 1000 / 111320.0))
        assert 3.0 < mb < 5.0

    @pytest.mark.parametrize("bounds,inside", [
        ((-97.75, 30.65, -97.74, 30.66), True),      # Texas
        ((-149.9, 61.2, -149.8, 61.3), True),        # Alaska
        ((2.3, 48.8, 2.4, 48.9), False),             # Paris
    ])
    def test_coverage_envelope(self, bounds, inside):
        assert self._strategy().in_coverage(bounds) is inside

    def test_outside_the_us_counts_as_covered(self):
        """Nothing to fetch there ever; do not retry it on every trigger."""
        assert self._strategy().already_covered((2.3, 48.8, 2.4, 48.9)) is True

    def test_a_successful_fetch_registers_the_paths(self, tmp_path):
        fetch = MagicMock()
        fetch.fetch_3dep_dem.return_value = FetchResult(
            product='usgs_3dep_dem', out_dir=str(tmp_path),
            manifest_path=str(tmp_path / 'dem_manifest.csv'), tiles_written=2)
        store = settings()
        strategy = self._strategy(fetch, store)
        plan = SimpleNamespace(bounds=BOUNDS, detail='USGS 3DEP',
                               out_dir=str(tmp_path))
        outcome = strategy.acquire(plan)

        assert outcome.tiles_written == 2
        assert outcome.registered is True
        assert store.writes['Terrain3DEPManifestPath'].endswith('dem_manifest.csv')

    def test_the_provider_selection_is_never_overridden(self):
        """Choosing the source is the operator's decision, not ours."""
        fetch = MagicMock()
        fetch.fetch_3dep_dem.return_value = FetchResult(
            product='usgs_3dep_dem', out_dir='/tmp',
            manifest_path='/tmp/dem_manifest.csv', tiles_written=1)
        store = settings(**{SETTING_PROVIDER: PROVIDER_TERRARIUM})
        plan = SimpleNamespace(bounds=BOUNDS, detail='USGS 3DEP', out_dir='/tmp')
        self._strategy(fetch, store).acquire(plan)
        assert SETTING_PROVIDER not in store.writes

    def test_a_fetch_that_writes_nothing_is_not_registered(self):
        fetch = MagicMock()
        fetch.fetch_3dep_dem.return_value = FetchResult(
            product='usgs_3dep_dem', out_dir='/tmp', manifest_path=None,
            tiles_failed=2,
            errors=[('dem_0_0.tif', 'service returned a non-TIFF body')])
        store = settings()
        plan = SimpleNamespace(bounds=BOUNDS, detail='USGS 3DEP', out_dir='/tmp')
        outcome = self._strategy(fetch, store).acquire(plan)

        assert outcome.registered is False
        assert 'non-TIFF' in outcome.skipped_reason
        assert store.writes == {}


class TestStrategySelection:
    """Sources are registry entries, not branches in calling code."""

    def test_the_default_provider_selects_terrarium(self):
        svc = TerrainAcquisitionService(settings_service=settings(),
                                        logger=MagicMock())
        assert isinstance(svc.strategy(), TerrariumStrategy)

    def test_choosing_3dep_selects_3dep(self):
        svc = TerrainAcquisitionService(
            settings_service=settings(**{SETTING_PROVIDER: PROVIDER_USGS_3DEP_LOCAL}),
            logger=MagicMock())
        assert isinstance(svc.strategy(), Usgs3depStrategy)

    def test_every_registered_strategy_implements_the_contract(self):
        """A new source cannot be half-registered.

        The package re-exports the service class under its module's own
        name, so the registry has to be reached through sys.modules.
        """
        import sys
        module = sys.modules['core.services.terrain.TerrainAcquisitionService']
        for provider_id, factory in module._STRATEGIES.items():
            assert factory.provider_id == provider_id
            assert factory.label
            for name in ('estimate_mb', 'already_covered', 'acquire', 'out_dir'):
                assert callable(getattr(factory, name, None)), (provider_id, name)
