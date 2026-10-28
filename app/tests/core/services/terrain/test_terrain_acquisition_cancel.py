"""Cancelling an automatic terrain acquisition.

A window that closes cancels its download and waits for the worker thread,
so planning must stop between images, and a cancelled run must not count
as an attempt: the next trigger for the same area still fetches it.
No network: the elevation source is faked (CLAUDE.md §3.3).
"""

from unittest.mock import MagicMock, patch

import pytest

from core.services.coverage import aoi
from core.services.terrain.TerrainAcquisitionService import (
    SETTING_ENABLED,
    SETTING_OFFLINE_ONLY,
    SETTING_USE_TERRAIN,
    SKIP_CANCELLED,
    AcquisitionOutcome,
    TerrainAcquisitionService,
    reset_attempt_history,
)

BOUNDS = (-97.7505, 30.6495, -97.7395, 30.6595)
IMAGES = [{'path': p} for p in ('a.jpg', 'b.jpg', 'c.jpg')]


@pytest.fixture(autouse=True)
def clean_state():
    """Attempt history and the connectivity probe are process-wide."""
    reset_attempt_history()
    TerrainAcquisitionService.reset_connectivity()
    yield
    reset_attempt_history()
    TerrainAcquisitionService.reset_connectivity()


class FakeSettings:
    values = {SETTING_USE_TERRAIN: True, SETTING_OFFLINE_ONLY: False, SETTING_ENABLED: True}

    def get_setting(self, name, default=None):
        return self.values.get(name, default)

    def get_bool_setting(self, name, default=False):
        return bool(self.values.get(name, default))


class FakeStrategy:
    """A stand-in elevation source that stops at its first tile once cancelled, like the real ones."""

    provider_id = 'fake_provider'
    label = 'Fake DEM'

    def __init__(self):
        self.calls = []

    def estimate_mb(self, bounds):
        return 1.0

    def already_covered(self, bounds):
        return False

    def out_dir(self):
        return None

    def acquire(self, plan, progress_callback=None, cancel_check=None):
        self.calls.append(plan)
        if cancel_check and cancel_check():
            return AcquisitionOutcome(plan=plan, cancelled=True)
        return AcquisitionOutcome(plan=plan, tiles_written=3, registered=True)


def service(strategy):
    svc = TerrainAcquisitionService(settings_service=FakeSettings(), logger=MagicMock(), strategy=strategy)
    TerrainAcquisitionService._online_checked = True
    TerrainAcquisitionService._online = True
    return svc


@pytest.fixture
def gps_reads():
    """Every image has GPS; the paths read are recorded. Footprints are not needed."""
    calls = []

    def gps(path):
        calls.append(path)
        return 30.65, -97.745

    with patch.object(aoi, 'image_gps', side_effect=gps), patch.object(aoi, '_frame_geometry', return_value=None):
        yield calls


def test_planning_stops_reading_images_once_cancelled(gps_reads):
    plan, reason = service(FakeStrategy()).plan(images=IMAGES, cancel_check=lambda: len(gps_reads) >= 1)

    assert plan is None
    assert reason == SKIP_CANCELLED
    assert gps_reads == ['a.jpg']


def test_a_run_cancelled_while_planning_is_silent_and_downloads_nothing(gps_reads):
    strategy = FakeStrategy()
    outcome = service(strategy).run(images=IMAGES, cancel_check=lambda: len(gps_reads) >= 1)

    assert outcome.cancelled
    assert not outcome.acquired
    assert strategy.calls == []


def test_a_run_cancelled_while_planning_leaves_the_area_untried(gps_reads):
    strategy = FakeStrategy()
    service(strategy).run(images=IMAGES, cancel_check=lambda: len(gps_reads) >= 1)

    assert service(strategy).run(images=IMAGES).acquired


def test_a_cancelled_download_leaves_the_area_untried():
    strategy = FakeStrategy()
    first = service(strategy).run(bounds=BOUNDS, cancel_check=lambda: True)
    second = service(strategy).run(bounds=BOUNDS)

    assert first.cancelled
    assert second.acquired
    assert len(strategy.calls) == 2


def test_explicit_bounds_are_planned_even_when_cancelled():
    """Nothing in planning reads images then; the download itself honours the cancel."""
    plan, reason = service(FakeStrategy()).plan(bounds=BOUNDS, cancel_check=lambda: True)

    assert reason is None
    assert plan.bounds == BOUNDS
