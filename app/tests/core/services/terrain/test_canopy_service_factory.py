"""Tests for CanopyServiceFactory.create_from_settings and the create_canopy_service alias."""

from unittest.mock import MagicMock, patch

from core.services.terrain.CanopyServiceFactory import (
    CanopyServiceFactory,
    create_canopy_service,
    CANOPY_KIND_NONE,
)


def _settings(values):
    s = MagicMock()
    s.get_setting.side_effect = lambda k, d=None: values.get(k, d)
    return s


def test_none_settings_returns_none():
    assert CanopyServiceFactory.create_from_settings(None) is None


def test_kind_none_returns_none():
    s = _settings({'CanopyKind': CANOPY_KIND_NONE})
    assert CanopyServiceFactory.create_from_settings(s) is None


def test_landfire_missing_paths_returns_none():
    s = _settings({'CanopyKind': 'landfire'})
    assert CanopyServiceFactory.create_from_settings(s) is None


def test_missing_paths_logs_info_not_warning():
    """No canopy source configured is the expected steady state (re-checked on
    every viewer/map open), so it is logged at INFO, not WARNING."""
    s = _settings({'CanopyKind': 'meta'})   # kind set, paths empty
    with patch('core.services.terrain.CanopyServiceFactory.LoggerService') as MockLog:
        logger = MockLog.return_value
        assert CanopyServiceFactory.create_from_settings(s) is None
    logger.info.assert_called_once()
    logger.warning.assert_not_called()


def test_meta_with_paths_builds_service(tmp_path):
    manifest = tmp_path / "m.csv"
    manifest.write_text("filename,product,minX,minY,maxX,maxY\n")
    s = _settings({'CanopyKind': 'meta',
                   'CanopyManifestPath': str(manifest),
                   'CanopyTilesDir': str(tmp_path)})
    svc = CanopyServiceFactory.create_from_settings(s)
    assert svc is not None
    assert svc.kind == 'meta'


def test_alias_matches_classmethod():
    s = _settings({'CanopyKind': CANOPY_KIND_NONE})
    assert create_canopy_service(s) is None


def test_available_kinds_shape():
    kinds = CanopyServiceFactory.available_kinds()
    ids = [k['id'] for k in kinds]
    assert ids == ['none', 'landfire', 'meta']
    assert all('label' in k and 'requires_paths' in k for k in kinds)


def test_construction_raises_returns_none(tmp_path):
    """When CanopyService construction raises, the factory's try/except must
    swallow the error and disable canopy (return None) rather than propagate."""
    manifest = tmp_path / "m.csv"
    manifest.write_text("filename,product,minX,minY,maxX,maxY\n")
    s = _settings({'CanopyKind': 'meta',
                   'CanopyManifestPath': str(manifest),
                   'CanopyTilesDir': str(tmp_path)})

    # The factory imports CanopyService inside create_from_settings via
    # `from core.services.terrain.CanopyService import CanopyService`, so the
    # name is resolved from that module at call time. Patch it there to raise.
    with patch('core.services.terrain.CanopyService.CanopyService',
               side_effect=RuntimeError("boom")):
        assert CanopyServiceFactory.create_from_settings(s) is None


def test_registered_but_missing_on_disk_returns_none_with_warning(tmp_path):
    """Dangling registration (results folder moved/deleted) must disable canopy
    cleanly with a WARNING - not construct a service that ERROR-logs 'manifest
    not found' on every viewer/map open."""
    s = _settings({'CanopyKind': 'meta',
                   'CanopyManifestPath': str(tmp_path / "gone" / "chm_manifest.csv"),
                   'CanopyTilesDir': str(tmp_path / "gone")})
    with patch('core.services.terrain.CanopyServiceFactory.LoggerService') as MockLog:
        logger = MockLog.return_value
        assert CanopyServiceFactory.create_from_settings(s) is None
    logger.warning.assert_called_once()
    assert "missing on disk" in logger.warning.call_args.args[0]


def test_manifest_present_but_tiles_dir_missing_returns_none(tmp_path):
    manifest = tmp_path / "m.csv"
    manifest.write_text("filename,product,minX,minY,maxX,maxY\n")
    s = _settings({'CanopyKind': 'meta',
                   'CanopyManifestPath': str(manifest),
                   'CanopyTilesDir': str(tmp_path / "nonexistent_tiles")})
    assert CanopyServiceFactory.create_from_settings(s) is None
