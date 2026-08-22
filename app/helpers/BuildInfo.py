"""BuildInfo - identifies exactly which commit a running ADIAT was built from.

Field debugging has repeatedly stalled on one question: what code is this
machine actually running? The version string alone cannot answer it - every
build cut from the same release line says "2.1.4" whether or not it contains
a given fix. The build stamp closes that gap:

- Packaged builds: app.spec bakes ``build_info.txt`` (short commit hash,
  plus ``+dirty`` when the build tree had uncommitted changes) into the
  bundle at build time.
- Dev checkouts: the stamp is read live from git.

The stamp is appended to the window titles, so any field screenshot
self-identifies, and logged at startup so any field log does too.
"""

import os
import subprocess
import sys

from helpers import FeatureFlags

BUILD_INFO_FILENAME = 'build_info.txt'

# Resolved once per process; the commit a running build was cut from cannot
# change mid-run.
_cached_stamp = None


def get_build_stamp():
    """Return the short commit hash this build was cut from, or ''.

    Packaged builds read the file baked in by app.spec; dev runs ask git.
    Unknown (no file, no git) is '' - callers show plain versions then.
    """
    global _cached_stamp
    if _cached_stamp is None:
        _cached_stamp = _read_baked_stamp() or _read_git_stamp()
    return _cached_stamp


def title_version(app_version):
    """Version string for window titles: '2.1.4 (58ef930)' or '2.1.4'.

    Gated by FeatureFlags.BUILD_STAMP_IN_TITLE, which is off for production
    releases (end users should not see a commit hash) and flipped on when
    cutting a build for field diagnosis. The startup log carries the stamp
    either way, so a plain title never costs us the commit identity.

    The stamp rides the title rather than the persisted app_version setting,
    which must stay parseable by the version-comparison helpers.
    """
    if not FeatureFlags.BUILD_STAMP_IN_TITLE:
        return app_version
    stamp = get_build_stamp()
    return f"{app_version} ({stamp})" if stamp else app_version


def _read_baked_stamp():
    """The stamp app.spec wrote into the bundle, or ''."""
    base = getattr(sys, '_MEIPASS', None)
    if not base:
        return ''
    try:
        with open(os.path.join(base, BUILD_INFO_FILENAME), encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return ''


def _read_git_stamp():
    """Live git hash for dev checkouts, or ''."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        rev = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        if rev.returncode != 0:
            return ''
        stamp = rev.stdout.strip()
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        if status.returncode == 0 and status.stdout.strip():
            stamp += '+dirty'
        return stamp
    except (OSError, subprocess.SubprocessError):
        return ''
