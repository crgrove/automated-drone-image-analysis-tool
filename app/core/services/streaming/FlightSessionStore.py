"""SQLite-backed per-session detection store for session continuity (plan §20).

Mobile stamps every MetaEnvelope with ``session_id`` (UUID generated at
``startSession()``) + monotonic ``seq``. The desktop persists every
incoming envelope to this store, keyed by ``(session_id, seq)``, so an
accidental app close doesn't lose the operator's detection record.

On Flight Viewer launch the controller:

1. Reads ``QSettings("ADIAT", "FlightViewer")/LastSession/*`` to find
   the most recent pairing.
2. Calls :meth:`load_session_detections` to replay every persisted
   detection for that session_id into the live Mission Gallery / Map.
3. Reads :meth:`max_seq_for_session` to set the resume cursor sent in
   ``{kind: "resume", session_id, last_seq}`` on the
   ``detections.snapshot_request`` channel.

Schema (plan §20):

.. code-block:: sql

    CREATE TABLE sessions (
        session_id          TEXT PRIMARY KEY,
        code                TEXT NOT NULL,
        worker_url          TEXT NOT NULL,
        created_at_epoch_s  REAL NOT NULL,
        last_seen_epoch_s   REAL NOT NULL,
        ended_at_epoch_s    REAL,
        aircraft_name       TEXT,
        aircraft_serial     TEXT,
        nickname            TEXT,
        last_seq            INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE detections (
        session_id          TEXT NOT NULL,
        seq                 INTEGER NOT NULL,
        track_key           TEXT NOT NULL,
        feed_id             TEXT,
        captured_at_ms      INTEGER NOT NULL,
        class_name          TEXT,
        detector_id         TEXT,
        confidence          REAL,
        bbox_norm_json      TEXT,
        location_json       TEXT,
        aircraft_name       TEXT,
        aircraft_serial     TEXT,
        feed_display_name   TEXT,
        frame_ts_ns         INTEGER,
        thumb_jpeg          BLOB,
        context_frame_jpeg  BLOB,
        received_at_epoch_s REAL NOT NULL,
        PRIMARY KEY (session_id, seq)
    );

The database lives next to the existing ADIAT app data.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import List, Optional

from core.services.LoggerService import LoggerService


def _default_db_path() -> Path:
    """Resolve the canonical on-disk location for the session DB.

    Mirrors :class:`FingerprintStore`'s convention so all Flight
    Viewer state ships together in one directory.
    """
    import platform
    if platform.system() == "Windows" or sys.platform == "darwin":
        base = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "ADIAT"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        base = Path(xdg) / "ADIAT"
    return base / "flight_sessions.sqlite"


@dataclass(frozen=True)
class SessionRecord:
    """One persisted publish-session header."""

    session_id: str
    code: str
    worker_url: str
    created_at_epoch_s: float
    last_seen_epoch_s: float
    ended_at_epoch_s: Optional[float]
    aircraft_name: Optional[str]
    aircraft_serial: Optional[str]
    nickname: Optional[str]
    last_seq: int


class FlightSessionStore:
    """Thread-safe SQLite wrapper for the session + detection tables.

    Connections are short-lived (open per call). The lock serializes
    writes that may race between the Qt main thread (gallery wiring)
    and any signal/slot dispatch that lands on a worker thread.
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
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id          TEXT PRIMARY KEY,
                    code                TEXT NOT NULL,
                    worker_url          TEXT NOT NULL,
                    created_at_epoch_s  REAL NOT NULL,
                    last_seen_epoch_s   REAL NOT NULL,
                    ended_at_epoch_s    REAL,
                    aircraft_name       TEXT,
                    aircraft_serial     TEXT,
                    nickname            TEXT,
                    last_seq            INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS detections (
                    session_id          TEXT NOT NULL,
                    seq                 INTEGER NOT NULL,
                    track_key           TEXT NOT NULL,
                    feed_id             TEXT,
                    captured_at_ms      INTEGER NOT NULL,
                    class_name          TEXT,
                    detector_id         TEXT,
                    confidence          REAL,
                    bbox_norm_json      TEXT,
                    location_json       TEXT,
                    aircraft_name       TEXT,
                    aircraft_serial     TEXT,
                    feed_display_name   TEXT,
                    frame_ts_ns         INTEGER,
                    thumb_jpeg          BLOB,
                    context_frame_jpeg  BLOB,
                    received_at_epoch_s REAL NOT NULL,
                    PRIMARY KEY (session_id, seq)
                );
                CREATE INDEX IF NOT EXISTS idx_detections_track_key
                    ON detections (session_id, track_key);
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=5.0, isolation_level=None)

    # ------------------------------------------------------------------
    # sessions
    # ------------------------------------------------------------------

    def record_session(
        self,
        *,
        session_id: str,
        code: str,
        worker_url: str,
        aircraft_name: Optional[str] = None,
        aircraft_serial: Optional[str] = None,
        nickname: Optional[str] = None,
    ) -> None:
        """Upsert the session header. Idempotent — safe on reconnect."""
        if not session_id or not code:
            return
        now = time.time()
        with self._lock, self._connect() as conn:
            existing = conn.execute(
                "SELECT 1 FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if existing is None:
                conn.execute(
                    """
                    INSERT INTO sessions(
                        session_id, code, worker_url,
                        created_at_epoch_s, last_seen_epoch_s,
                        aircraft_name, aircraft_serial, nickname
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id, code, worker_url,
                        now, now,
                        aircraft_name, aircraft_serial, nickname,
                    ),
                )
            else:
                # Update metadata but keep created_at_epoch_s.
                fields = ["last_seen_epoch_s = ?"]
                params: list = [now]
                if aircraft_name is not None:
                    fields.append("aircraft_name = ?")
                    params.append(aircraft_name)
                if aircraft_serial is not None:
                    fields.append("aircraft_serial = ?")
                    params.append(aircraft_serial)
                if nickname is not None:
                    fields.append("nickname = ?")
                    params.append(nickname)
                if code:
                    fields.append("code = ?")
                    params.append(code)
                if worker_url:
                    fields.append("worker_url = ?")
                    params.append(worker_url)
                params.append(session_id)
                conn.execute(
                    f"UPDATE sessions SET {', '.join(fields)} WHERE session_id = ?",
                    params,
                )

    def mark_session_ended(self, session_id: str) -> None:
        """Stamp ``ended_at_epoch_s`` on the session header."""
        if not session_id:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET ended_at_epoch_s = ? WHERE session_id = ?",
                (time.time(), session_id),
            )

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        if not session_id:
            return None
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """
                SELECT session_id, code, worker_url, created_at_epoch_s,
                       last_seen_epoch_s, ended_at_epoch_s, aircraft_name,
                       aircraft_serial, nickname, last_seq
                FROM sessions WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return SessionRecord(*row)

    def recent_sessions(self, *, limit: int = 20) -> List[SessionRecord]:
        """Return recent sessions, most-recent first."""
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT session_id, code, worker_url, created_at_epoch_s,
                       last_seen_epoch_s, ended_at_epoch_s, aircraft_name,
                       aircraft_serial, nickname, last_seq
                FROM sessions
                ORDER BY last_seen_epoch_s DESC
                LIMIT ?
                """,
                (int(limit),),
            ).fetchall()
        return [SessionRecord(*row) for row in rows]

    # ------------------------------------------------------------------
    # detections
    # ------------------------------------------------------------------

    def append_detection(self, envelope: dict) -> bool:
        """Append a detection envelope. Returns ``True`` if newly stored.

        Idempotent dedup on the primary key ``(session_id, seq)`` —
        a snapshot replay (or resume backfill) that re-delivers the
        same event is silently ignored. Returns ``False`` for skipped
        rows, including ones missing ``session_id`` or ``seq``.
        """
        if not isinstance(envelope, dict):
            return False
        session_id = envelope.get("session_id")
        seq = envelope.get("seq")
        if not isinstance(session_id, str) or not session_id:
            return False
        if not isinstance(seq, (int, float)):
            return False
        seq = int(seq)
        captured_at_ms = envelope.get("captured_at_ms")
        if not isinstance(captured_at_ms, (int, float)):
            return False

        bbox_norm = envelope.get("bbox_norm")
        location = envelope.get("location")
        bbox_json = json.dumps(list(bbox_norm)) if isinstance(bbox_norm, (list, tuple)) else None
        location_json = json.dumps(dict(location)) if isinstance(location, dict) else None
        thumb = envelope.get("thumb_bytes")
        context = envelope.get("context_frame_jpeg")
        thumb_blob = bytes(thumb) if isinstance(thumb, (bytes, bytearray)) else None
        context_blob = bytes(context) if isinstance(context, (bytes, bytearray)) else None
        frame_ts_ns = envelope.get("frame_ts_ns")
        frame_ts_int = int(frame_ts_ns) if isinstance(frame_ts_ns, (int, float)) else None

        with self._lock, self._connect() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO detections(
                        session_id, seq, track_key, feed_id, captured_at_ms,
                        class_name, detector_id, confidence,
                        bbox_norm_json, location_json,
                        aircraft_name, aircraft_serial, feed_display_name,
                        frame_ts_ns, thumb_jpeg, context_frame_jpeg,
                        received_at_epoch_s
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id, seq,
                        str(envelope.get("track_key") or ""),
                        envelope.get("feed_id"),
                        int(captured_at_ms),
                        envelope.get("class_name"),
                        envelope.get("detector_id"),
                        float(envelope.get("confidence"))
                        if isinstance(envelope.get("confidence"), (int, float))
                        else None,
                        bbox_json, location_json,
                        envelope.get("aircraft_name"),
                        envelope.get("aircraft_serial"),
                        envelope.get("feed_display_name"),
                        frame_ts_int,
                        thumb_blob, context_blob,
                        time.time(),
                    ),
                )
            except sqlite3.IntegrityError:
                # Duplicate (session_id, seq) — backfill replay of an
                # already-stored event. Update the row with any newer
                # fields (e.g. thumb arrived later) but report no insert.
                conn.execute(
                    """
                    UPDATE detections SET
                        thumb_jpeg = COALESCE(?, thumb_jpeg),
                        context_frame_jpeg = COALESCE(?, context_frame_jpeg)
                    WHERE session_id = ? AND seq = ?
                    """,
                    (thumb_blob, context_blob, session_id, seq),
                )
                return False
            # Track the highest seq we've seen for this session.
            conn.execute(
                """
                UPDATE sessions
                SET last_seq = MAX(last_seq, ?),
                    last_seen_epoch_s = ?
                WHERE session_id = ?
                """,
                (seq, time.time(), session_id),
            )
        return True

    def update_thumb(self, session_id: str, track_key: str, thumb_jpeg: bytes) -> None:
        """Patch all rows in this session matching ``track_key`` with new thumb bytes."""
        if not session_id or not track_key or not thumb_jpeg:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE detections
                SET thumb_jpeg = ?
                WHERE session_id = ? AND track_key = ?
                """,
                (bytes(thumb_jpeg), session_id, track_key),
            )

    def max_seq_for_session(self, session_id: str) -> int:
        """Return the highest ``seq`` stored for ``session_id`` (``0`` if empty).

        Used as the ``last_seq`` cursor on the resume handshake — mobile
        replays everything newer than this.
        """
        if not session_id:
            return 0
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT MAX(seq) FROM detections WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None or row[0] is None:
            return 0
        return int(row[0])

    def load_session_detections(self, session_id: str) -> List[dict]:
        """Reconstruct stored detection envelopes for replay into the gallery.

        Returned dicts mirror the in-memory envelope shape consumed by
        :class:`MissionGalleryController.add_detection`: ``feed_id``,
        ``track_key``, ``captured_at_ms``, ``class_name``, ``detector_id``,
        ``confidence``, ``bbox_norm`` (list), ``location`` (dict),
        ``aircraft_name``, ``aircraft_serial``, ``feed_display_name``,
        ``frame_ts_ns``, ``session_id``, ``seq``, plus ``thumb_bytes`` /
        ``context_frame_jpeg`` when stored.
        """
        if not session_id:
            return []
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT seq, track_key, feed_id, captured_at_ms, class_name,
                       detector_id, confidence, bbox_norm_json, location_json,
                       aircraft_name, aircraft_serial, feed_display_name,
                       frame_ts_ns, thumb_jpeg, context_frame_jpeg
                FROM detections
                WHERE session_id = ?
                ORDER BY seq
                """,
                (session_id,),
            ).fetchall()
        out: List[dict] = []
        for (seq, track_key, feed_id, captured_at_ms, class_name, detector_id,
             confidence, bbox_norm_json, location_json, aircraft_name,
             aircraft_serial, feed_display_name, frame_ts_ns, thumb_blob,
             context_blob) in rows:
            envelope: dict = {
                "session_id": session_id,
                "seq": int(seq),
                "track_key": track_key,
                "feed_id": feed_id,
                "captured_at_ms": int(captured_at_ms),
                "class_name": class_name,
                "detector_id": detector_id,
                "confidence": confidence,
            }
            if bbox_norm_json:
                try:
                    envelope["bbox_norm"] = json.loads(bbox_norm_json)
                except (TypeError, ValueError):
                    pass
            if location_json:
                try:
                    envelope["location"] = json.loads(location_json)
                except (TypeError, ValueError):
                    pass
            if aircraft_name:
                envelope["aircraft_name"] = aircraft_name
            if aircraft_serial:
                envelope["aircraft_serial"] = aircraft_serial
            if feed_display_name:
                envelope["feed_display_name"] = feed_display_name
            if frame_ts_ns is not None:
                envelope["frame_ts_ns"] = int(frame_ts_ns)
            if thumb_blob:
                envelope["thumb_bytes"] = bytes(thumb_blob)
            if context_blob:
                envelope["context_frame_jpeg"] = bytes(context_blob)
            out.append(envelope)
        return out

    def prune_session(self, session_id: str) -> None:
        """Delete a session and all its detections (operator-initiated discard)."""
        if not session_id:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                "DELETE FROM detections WHERE session_id = ?", (session_id,)
            )
            conn.execute(
                "DELETE FROM sessions WHERE session_id = ?", (session_id,)
            )

    def prune_older_than(self, epoch_s: float) -> int:
        """Delete sessions (and their detections) whose ``last_seen_epoch_s`` is older.

        Returns the number of sessions deleted. Operator-facing cleanup
        for long-running installs (24 h, 7 d, etc.) — caller picks the
        cutoff.
        """
        with self._lock, self._connect() as conn:
            stale = [
                row[0]
                for row in conn.execute(
                    "SELECT session_id FROM sessions WHERE last_seen_epoch_s < ?",
                    (float(epoch_s),),
                ).fetchall()
            ]
            if not stale:
                return 0
            placeholders = ",".join("?" * len(stale))
            conn.execute(
                f"DELETE FROM detections WHERE session_id IN ({placeholders})",
                stale,
            )
            conn.execute(
                f"DELETE FROM sessions WHERE session_id IN ({placeholders})",
                stale,
            )
        return len(stale)


__all__ = [
    "FlightSessionStore",
    "SessionRecord",
]
