"""Tests for helpers.BuildInfo - the build stamp that identifies field builds."""

import sys

import pytest

from helpers import BuildInfo


def _clear_cache():
    BuildInfo._cached_stamp = None


def test_title_version_appends_stamp_when_flag_on(monkeypatch):
    """Diagnostic builds: the title identifies its own commit."""
    monkeypatch.setattr(BuildInfo.FeatureFlags, 'BUILD_STAMP_IN_TITLE', True)
    monkeypatch.setattr(BuildInfo, 'get_build_stamp', lambda: 'abc1234')
    assert BuildInfo.title_version('2.1.4') == '2.1.4 (abc1234)'


def test_title_version_plain_when_unknown(monkeypatch):
    monkeypatch.setattr(BuildInfo.FeatureFlags, 'BUILD_STAMP_IN_TITLE', True)
    monkeypatch.setattr(BuildInfo, 'get_build_stamp', lambda: '')
    assert BuildInfo.title_version('2.1.4') == '2.1.4'


def test_title_version_plain_when_flag_off(monkeypatch):
    """Production releases: no commit hash in the title even when the stamp
    is perfectly well known. get_build_stamp must not even be consulted."""
    monkeypatch.setattr(BuildInfo.FeatureFlags, 'BUILD_STAMP_IN_TITLE', False)
    monkeypatch.setattr(BuildInfo, 'get_build_stamp',
                        lambda: pytest.fail("stamp must not be read when flag is off"))
    assert BuildInfo.title_version('2.1.4') == '2.1.4'


def test_build_stamp_in_title_off_by_default():
    """Guards the shipping default, so re-enabling is a deliberate edit."""
    assert BuildInfo.FeatureFlags.BUILD_STAMP_IN_TITLE is False


def test_baked_stamp_wins_in_frozen_build(tmp_path, monkeypatch):
    (tmp_path / BuildInfo.BUILD_INFO_FILENAME).write_text('f00dcafe+dirty\n')
    monkeypatch.setattr(sys, '_MEIPASS', str(tmp_path), raising=False)
    _clear_cache()
    try:
        assert BuildInfo.get_build_stamp() == 'f00dcafe+dirty'
    finally:
        _clear_cache()


def test_dev_checkout_reads_live_git(monkeypatch):
    """In this repo (a git checkout, no _MEIPASS) the stamp is a short hash,
    optionally '+dirty'. Guards the fallback the developers rely on."""
    monkeypatch.delattr(sys, '_MEIPASS', raising=False)
    _clear_cache()
    try:
        stamp = BuildInfo.get_build_stamp()
        assert stamp, "expected a live git stamp in a dev checkout"
        head = stamp.removesuffix('+dirty')
        assert 6 <= len(head) <= 16 and all(c in '0123456789abcdef' for c in head)
    finally:
        _clear_cache()


def test_unknown_everywhere_is_empty(tmp_path, monkeypatch):
    monkeypatch.delattr(sys, '_MEIPASS', raising=False)
    monkeypatch.setattr(BuildInfo, '_read_git_stamp', lambda: '')
    # Flag pinned ON so the plain title below proves the UNKNOWN-stamp path,
    # not merely that the flag happens to be off in this release.
    monkeypatch.setattr(BuildInfo.FeatureFlags, 'BUILD_STAMP_IN_TITLE', True)
    _clear_cache()
    try:
        assert BuildInfo.get_build_stamp() == ''
        assert BuildInfo.title_version('2.1.4') == '2.1.4'
    finally:
        _clear_cache()
