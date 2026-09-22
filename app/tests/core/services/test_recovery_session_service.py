"""Unit tests for RecoverySessionService."""

import os
from unittest.mock import patch

import importlib

from core.services.RecoverySessionService import RecoverySession

recovery_module = importlib.import_module("core.services.RecoverySessionService")


def test_matches_root_normalizes_case_and_separators(tmp_path):
    session = RecoverySession(str(tmp_path))
    assert session.matches_root(str(tmp_path))
    assert session.matches_root(str(tmp_path).upper()) == (os.name == 'nt')
    assert not session.matches_root(str(tmp_path / "other"))
    assert not session.matches_root("")


def test_candidate_folders_scan_root_only_by_default(tmp_path):
    session = RecoverySession(str(tmp_path))
    assert session.candidate_folders() == [str(tmp_path)]


def test_candidate_folders_picks_come_before_scan_root(tmp_path):
    pick1 = tmp_path / "flight1"
    pick2 = tmp_path / "flight2"
    pick1.mkdir()
    pick2.mkdir()
    session = RecoverySession(str(tmp_path))
    session.remember(str(pick1))
    session.remember(str(pick2))
    # Newest pick first, scan root last
    assert session.candidate_folders() == [str(pick2), str(pick1), str(tmp_path)]


def test_candidate_folders_filters_missing_and_roots(tmp_path):
    session = RecoverySession(str(tmp_path / "gone"))
    session.remember(str(tmp_path / "also_gone"))
    assert session.candidate_folders() == []


def test_remember_dedupes_and_ignores_roots(tmp_path):
    pick = tmp_path / "flight"
    pick.mkdir()
    session = RecoverySession(str(tmp_path))
    session.remember(str(pick))
    session.remember(str(pick))
    session.remember(os.path.abspath(os.sep))  # filesystem root: ignored
    session.remember("")
    assert session.candidate_folders() == [str(pick), str(tmp_path)]


def test_candidate_folders_dedupes_pick_equal_to_scan_root(tmp_path):
    session = RecoverySession(str(tmp_path))
    session.remember(str(tmp_path))
    assert session.candidate_folders() == [str(tmp_path)]


def test_find_files_by_extension_sweeps_session_folders(tmp_path):
    deep = tmp_path / "flight" / "logs"
    deep.mkdir(parents=True)
    (deep / "Mission_Triggers.kml").write_text("x")
    (deep / "tracklog.GPX").write_text("x")  # extension match is case-blind
    (tmp_path / "notes.txt").write_text("x")
    session = RecoverySession(str(tmp_path))

    found = session.find_files_by_extension(('.kml', '.gpx'))

    assert sorted(os.path.basename(f) for f in found) == \
        ["Mission_Triggers.kml", "tracklog.GPX"]


def test_find_files_by_extension_picks_before_scan_root_and_dedupes(tmp_path):
    root = tmp_path / "scanned"
    root.mkdir()
    (root / "a.kml").write_text("x")
    pick = tmp_path / "picked"
    pick.mkdir()
    (pick / "b.kml").write_text("x")
    session = RecoverySession(str(root))
    session.remember(str(pick))

    found = session.find_files_by_extension(('.kml',))

    assert [os.path.basename(f) for f in found] == ["b.kml", "a.kml"]
    # A second sweep serves from the cached indexes and stays identical
    assert session.find_files_by_extension(('.kml',)) == found


def test_get_index_builds_once_per_folder(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    session = RecoverySession(str(tmp_path))

    with patch.object(
        recovery_module, 'index_folder_by_filename',
        wraps=recovery_module.index_folder_by_filename
    ) as mock_index:
        first = session.get_index(str(tmp_path))
        second = session.get_index(str(tmp_path))

    assert first is second
    assert mock_index.call_count == 1
    assert 'a.jpg' in first


def test_get_index_logs_truncation(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    (tmp_path / "b.jpg").write_text("x")
    session = RecoverySession(str(tmp_path))

    real_index = recovery_module.index_folder_by_filename
    with patch.object(session.logger, 'warning') as mock_warning:
        index = session.get_index(str(tmp_path))
        # Force a truncated build via the real max_entries knob
        session._indexes.clear()
        with patch.object(
            recovery_module, 'index_folder_by_filename',
            side_effect=lambda folder: real_index(folder, max_entries=1)
        ):
            truncated = session.get_index(str(tmp_path))

    assert not getattr(index, 'truncated', False)
    assert getattr(truncated, 'truncated', False)
    mock_warning.assert_called_once()
