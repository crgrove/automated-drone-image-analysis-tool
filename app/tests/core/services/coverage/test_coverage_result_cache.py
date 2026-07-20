"""Tests for the in-session CoverageResultCache lifecycle."""

from core.services.coverage.CoverageResultCache import CoverageResultCache


def test_cache_lifecycle():
    cache = CoverageResultCache()
    assert cache.has_result() is False
    assert cache.get_result() is None

    sentinel = object()
    cache.set_result(sentinel)
    assert cache.has_result() is True
    assert cache.get_result() is sentinel

    cache.invalidate()
    assert cache.has_result() is False
    assert cache.get_result() is None


# ---------------------------------------------------------------------------
# Config fingerprinting + staleness
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock

from core.services.coverage.CoverageResultCache import config_fingerprint


def _settings(values):
    s = MagicMock()
    s.get_setting.side_effect = lambda k, default='': values.get(k, default)
    return s


def test_fingerprint_covers_terrain_and_canopy_keys():
    fp = config_fingerprint(_settings({
        'TerrainProviderId': 'usgs_3dep_local',
        'Terrain3DEPManifestPath': 'C:/dem/m.csv',
        'CanopyKind': 'meta',
    }))
    assert 'usgs_3dep_local' in fp
    assert 'C:/dem/m.csv' in fp
    assert 'meta' in fp


def test_fingerprint_changes_when_a_source_changes():
    base = {'TerrainProviderId': 'terrarium', 'CanopyKind': 'none'}
    fp1 = config_fingerprint(_settings(base))
    fp2 = config_fingerprint(_settings({**base, 'CanopyKind': 'meta'}))
    assert fp1 != fp2


def test_fingerprint_none_settings_is_empty():
    assert config_fingerprint(None) == ''


def test_fingerprint_survives_get_setting_errors():
    s = MagicMock()
    s.get_setting.side_effect = RuntimeError("registry broken")
    assert isinstance(config_fingerprint(s), str)


def test_empty_cache_is_never_stale():
    cache = CoverageResultCache()
    assert cache.is_stale("anything") is False


def test_matching_fingerprint_is_fresh():
    cache = CoverageResultCache()
    cache.set_result(object(), "fp-a")
    assert cache.is_stale("fp-a") is False
    assert cache.has_result() is True


def test_mismatched_fingerprint_is_stale():
    cache = CoverageResultCache()
    cache.set_result(object(), "fp-a")
    assert cache.is_stale("fp-b") is True


def test_unfingerprinted_result_is_trusted():
    """Back-compat: results cached without a fingerprint never go stale."""
    cache = CoverageResultCache()
    cache.set_result(object())
    assert cache.is_stale("fp-b") is False


def test_empty_current_fingerprint_is_trusted():
    cache = CoverageResultCache()
    cache.set_result(object(), "fp-a")
    assert cache.is_stale("") is False


def test_invalidate_clears_result_and_fingerprint():
    cache = CoverageResultCache()
    cache.set_result(object(), "fp-a")
    cache.invalidate()
    assert cache.has_result() is False
    assert cache.is_stale("fp-b") is False
