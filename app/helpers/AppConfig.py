"""TOML-backed application config loader.

The Flight Viewer (plan §17) and any future ADIAT surface that needs an
operator-overridable setting reads from a single ``config.toml`` living
in the user's app-data directory. The file is optional — a missing or
malformed file simply yields an empty config dict, and callers fall back
to their built-in defaults.

Layout (current keys; more may be added later):

.. code-block:: toml

    [signaling]
    base_url = "https://signal.adiat.app"

Location:

* Windows / macOS — ``~/AppData/Roaming/ADIAT/config.toml`` (matches the
  log file path established by :class:`LoggerService`).
* Linux — ``$XDG_CONFIG_HOME/ADIAT/config.toml`` (default
  ``~/.config/ADIAT/config.toml``).
"""

from __future__ import annotations

import os
import platform
import sys
import tomllib
from pathlib import Path
from typing import Any, Dict, Optional


def get_config_path() -> Path:
    """Return the canonical ``config.toml`` location for this platform.

    The directory may not exist; callers should ``Path.exists()`` before
    reading. The path is returned for both reading and (future) writing,
    so the resolver always returns the same answer regardless of file
    state on disk.
    """
    if platform.system() == "Windows" or sys.platform == "darwin":
        base = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ADIAT"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        base = Path(xdg) / "ADIAT"
    return base / "config.toml"


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load ``config.toml`` into a dict.

    Args:
        path: Optional override (used by tests). Defaults to
            :func:`get_config_path`.

    Returns:
        Parsed TOML as a dict, or an empty dict if the file is missing,
        unreadable, or contains malformed TOML. Errors are logged but
        never raised — config is operator-supplied and should never
        crash the app.
    """
    config_path = path or get_config_path()
    if not config_path.exists():
        return {}
    try:
        with config_path.open("rb") as fp:
            return tomllib.load(fp)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        # Defer import so this helper does not pull in the rest of the
        # service stack at import time.
        try:
            from core.services.LoggerService import LoggerService
            LoggerService().warning(
                f"AppConfig: failed to load {config_path}: {exc}"
            )
        except Exception:  # pragma: no cover - defensive
            pass
        return {}


def get_section(section: str, *, path: Optional[Path] = None) -> Dict[str, Any]:
    """Return ``config[section]`` as a dict, or ``{}`` if missing or not a table."""
    config = load_config(path=path)
    value = config.get(section)
    if isinstance(value, dict):
        return value
    return {}
