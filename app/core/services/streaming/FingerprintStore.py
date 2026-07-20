"""SQLite-backed TOFU store for paired ADIAT_Mobile publishers (plan §19.4.3).

Each successful Flight Viewer pairing produces a DTLS fingerprint. The
SAS gate already defends against a same-session MitM (plan §9). TOFU
adds *trust-on-first-use* across sessions:

1. On the first SAS-confirm with a given publisher, the operator labels
   the device ("Operator A's M4E") and we persist
   ``(label, sha256_fingerprint)``.
2. On any subsequent connect that the operator identifies as the *same*
   device, we compare the incoming fingerprint to the stored one:

   - Match → silently update ``last_seen_epoch_s``.
   - Mismatch → surface a prominent warning, let the operator accept
     (overwriting with a note) or reject.

Schema (plan §19.4.3):

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS peer_fingerprints (
        device_label TEXT PRIMARY KEY,
        sha256 TEXT NOT NULL,
        first_seen_epoch_s REAL NOT NULL,
        last_seen_epoch_s REAL NOT NULL,
        notes TEXT
    );

The database lives next to the existing ADIAT app data so it ships with
the rest of the user's persistent state.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import List, Optional

from core.services.LoggerService import LoggerService


@dataclass(frozen=True)
class PeerRecord:
    """One trusted publisher (DTLS identity) plus the operator's label for it."""

    device_label: str
    sha256: str
    first_seen_epoch_s: float
    last_seen_epoch_s: float
    notes: Optional[str] = None


def _default_db_path() -> Path:
    """Resolve the canonical on-disk location for the fingerprint DB.

    Mirrors :class:`LoggerService`'s app-data convention: Windows/macOS
    use ``~/AppData/Roaming/ADIAT/``; Linux uses XDG.
    """
    import platform

    if platform.system() == "Windows" or sys.platform == "darwin":
        base = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ADIAT"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        base = Path(xdg) / "ADIAT"
    return base / "flight_viewer_peers.sqlite"


class FingerprintStore:
    """Thread-safe SQLite wrapper for the peer fingerprint table.

    Connections are short-lived (open per call). The lock serializes
    writes from the Qt main thread + any background threads that might
    end up calling :meth:`record_pairing` from a service callback.
    """

    def __init__(self, *, db_path: Optional[Path] = None):
        self.logger = LoggerService()
        self._db_path = Path(db_path) if db_path else _default_db_path()
        self._lock = Lock()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    # ------------------------------------------------------------------
    # schema
    # ------------------------------------------------------------------

    def _ensure_schema(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS peer_fingerprints (
                    device_label TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    first_seen_epoch_s REAL NOT NULL,
                    last_seen_epoch_s REAL NOT NULL,
                    notes TEXT
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=5.0, isolation_level=None)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def list_devices(self) -> List[PeerRecord]:
        """Return all stored devices, most-recently-seen first."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT device_label, sha256, first_seen_epoch_s, "
                "last_seen_epoch_s, notes FROM peer_fingerprints "
                "ORDER BY last_seen_epoch_s DESC"
            ).fetchall()
        return [PeerRecord(*row) for row in rows]

    def get(self, device_label: str) -> Optional[PeerRecord]:
        """Look up a single device by operator-assigned label."""
        if not device_label:
            return None
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT device_label, sha256, first_seen_epoch_s, "
                "last_seen_epoch_s, notes FROM peer_fingerprints "
                "WHERE device_label = ?",
                (device_label,),
            ).fetchone()
        return PeerRecord(*row) if row else None

    def find_by_fingerprint(self, sha256: str) -> Optional[PeerRecord]:
        """Reverse lookup — used to detect already-paired devices.

        Useful for the "recent devices" dropdown: when the publisher
        re-pairs without the operator selecting a label up front, we can
        suggest the previously-used label instead of treating it as new.
        """
        normalized = _normalize_fp(sha256)
        if not normalized:
            return None
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT device_label, sha256, first_seen_epoch_s, "
                "last_seen_epoch_s, notes FROM peer_fingerprints "
                "ORDER BY last_seen_epoch_s DESC"
            ).fetchall()
        for row in rows:
            if _normalize_fp(row[1]) == normalized:
                return PeerRecord(*row)
        return None

    def record_pairing(
        self,
        device_label: str,
        sha256: str,
        *,
        notes: Optional[str] = None,
    ) -> PeerRecord:
        """Insert or update a fingerprint record.

        Idempotent: re-recording the same ``(label, sha256)`` pair only
        bumps ``last_seen_epoch_s``. A new sha256 for an existing label
        is treated as a deliberate operator override (e.g. tablet
        replaced) — the previous fingerprint is overwritten and a note
        captures the swap.
        """
        if not device_label or not sha256:
            raise ValueError("device_label and sha256 are both required")
        now = time.time()
        with self._lock, self._connect() as conn:
            existing = conn.execute(
                "SELECT sha256, first_seen_epoch_s FROM peer_fingerprints "
                "WHERE device_label = ?",
                (device_label,),
            ).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO peer_fingerprints "
                    "(device_label, sha256, first_seen_epoch_s, last_seen_epoch_s, notes) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (device_label, sha256, now, now, notes),
                )
                first_seen = now
            else:
                first_seen = existing[1]
                conn.execute(
                    "UPDATE peer_fingerprints SET sha256 = ?, "
                    "last_seen_epoch_s = ?, notes = COALESCE(?, notes) "
                    "WHERE device_label = ?",
                    (sha256, now, notes, device_label),
                )
        return PeerRecord(
            device_label=device_label,
            sha256=sha256,
            first_seen_epoch_s=first_seen,
            last_seen_epoch_s=now,
            notes=notes,
        )

    def forget(self, device_label: str) -> None:
        """Drop a previously-trusted device. Operator-initiated."""
        with self._lock, self._connect() as conn:
            conn.execute(
                "DELETE FROM peer_fingerprints WHERE device_label = ?",
                (device_label,),
            )

    def matches(self, device_label: str, sha256: str) -> bool:
        """``True`` if the stored fingerprint for ``device_label`` equals ``sha256``."""
        record = self.get(device_label)
        if record is None:
            return False
        return _normalize_fp(record.sha256) == _normalize_fp(sha256)


def _normalize_fp(fp: str) -> str:
    """Canonicalize a fingerprint string for equality comparison."""
    return (fp or "").replace(":", "").replace(" ", "").strip().lower()
