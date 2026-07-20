"""Unit tests for :mod:`helpers.AppConfig`.

Verifies that the TOML loader gracefully handles the three states a real
operator deployment goes through: no file, valid file, malformed file.
The Flight Viewer's signaling URL override flows through this loader, so
the contract here is part of the operator-facing API surface.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from helpers.AppConfig import (  # noqa: E402
    get_config_path,
    get_section,
    load_config,
)


def test_load_config_returns_empty_dict_when_file_missing(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.toml"
    assert load_config(path=missing) == {}


def test_load_config_parses_valid_toml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        '[signaling]\nbase_url = "https://example.test/worker"\n',
        encoding="utf-8",
    )
    config = load_config(path=config_path)
    assert config == {"signaling": {"base_url": "https://example.test/worker"}}


def test_load_config_returns_empty_dict_on_malformed_toml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("this = is not valid toml ===\n", encoding="utf-8")
    # Should not raise; should log a warning and return an empty config so
    # callers fall back to their built-in defaults.
    assert load_config(path=config_path) == {}


def test_get_section_returns_dict_when_present(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        '[signaling]\nbase_url = "https://example.test/worker"\n',
        encoding="utf-8",
    )
    section = get_section("signaling", path=config_path)
    assert section == {"base_url": "https://example.test/worker"}


def test_get_section_returns_empty_when_missing(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("[other]\nkey = 1\n", encoding="utf-8")
    assert get_section("signaling", path=config_path) == {}


def test_get_section_returns_empty_when_value_is_not_a_table(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text('signaling = "not-a-table"\n', encoding="utf-8")
    assert get_section("signaling", path=config_path) == {}


def test_get_config_path_returns_platform_specific_location() -> None:
    path = get_config_path()
    # Doesn't matter which platform we're on — the file is always
    # named ``config.toml`` and sits inside an ``ADIAT`` directory.
    assert path.name == "config.toml"
    assert path.parent.name == "ADIAT"
