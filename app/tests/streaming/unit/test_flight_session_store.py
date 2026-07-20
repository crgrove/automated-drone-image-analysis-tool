"""Unit tests for :class:`FlightSessionStore` (plan §20)."""

from __future__ import annotations

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.FlightSessionStore import FlightSessionStore  # noqa: E402


@pytest.fixture
def store(tmp_path):
    return FlightSessionStore(db_path=tmp_path / "sessions.sqlite")


def _detection(**overrides) -> dict:
    base = {
        "session_id": "S-1",
        "seq": 1,
        "track_key": "person|S-1|42",
        "feed_id": "K3F9PM",
        "captured_at_ms": 1737310912345,
        "class_name": "person",
        "detector_id": "person",
        "confidence": 0.87,
        "bbox_norm": [0.4, 0.5, 0.1, 0.2],
        "location": {"lat": 30.1, "lon": -97.5},
        "aircraft_name": "TEXSAR-01",
        "aircraft_serial": "1ZNDH6V0011234",
        "feed_display_name": "TEXSAR-01 (K3F9PM)",
        "frame_ts_ns": 1737310912000000000,
    }
    base.update(overrides)
    return base


def test_record_session_then_lookup(store) -> None:
    store.record_session(
        session_id="S-1",
        code="K3F9PM",
        worker_url="https://signal.adiat.app",
        aircraft_name="TEXSAR-01",
        aircraft_serial="1ZNDH6V0011234",
        nickname="Aerial Pegasus",
    )
    rec = store.get_session("S-1")
    assert rec is not None
    assert rec.session_id == "S-1"
    assert rec.code == "K3F9PM"
    assert rec.aircraft_name == "TEXSAR-01"
    assert rec.nickname == "Aerial Pegasus"
    assert rec.last_seq == 0


def test_record_session_is_idempotent_and_updates_metadata(store) -> None:
    store.record_session(
        session_id="S-2", code="ABC222", worker_url="https://w",
        aircraft_name=None, aircraft_serial=None,
    )
    store.record_session(
        session_id="S-2", code="ABC222", worker_url="https://w",
        aircraft_name="TEXSAR-02", aircraft_serial="SN-2",
    )
    rec = store.get_session("S-2")
    assert rec is not None
    assert rec.aircraft_name == "TEXSAR-02"
    assert rec.aircraft_serial == "SN-2"


def test_append_detection_dedupes_by_session_id_and_seq(store) -> None:
    store.record_session(session_id="S-1", code="K3F9PM", worker_url="https://w")
    assert store.append_detection(_detection(seq=1)) is True
    # Re-append same (session_id, seq) is silently dropped.
    assert store.append_detection(_detection(seq=1, class_name="DIFFERENT")) is False
    # New seq is accepted.
    assert store.append_detection(_detection(seq=2)) is True
    rows = store.load_session_detections("S-1")
    assert len(rows) == 2
    assert [r["seq"] for r in rows] == [1, 2]
    # The duplicate insert did NOT overwrite class_name on the original row.
    assert rows[0]["class_name"] == "person"


def test_append_detection_rejects_missing_session_id_or_seq(store) -> None:
    assert store.append_detection({"track_key": "x", "captured_at_ms": 1}) is False
    assert store.append_detection({"session_id": "S-1", "captured_at_ms": 1}) is False
    assert store.append_detection({"session_id": "S-1", "seq": 1}) is False  # no captured_at_ms


def test_load_session_detections_restores_envelope_shape(store) -> None:
    store.record_session(session_id="S-1", code="K3F9PM", worker_url="https://w")
    blob = b"\xff\xd8\xff\xe0jpeg"
    store.append_detection(_detection(seq=10))
    store.update_thumb("S-1", "person|S-1|42", blob)
    rows = store.load_session_detections("S-1")
    assert len(rows) == 1
    row = rows[0]
    assert row["seq"] == 10
    assert row["bbox_norm"] == [0.4, 0.5, 0.1, 0.2]
    assert row["location"] == {"lat": 30.1, "lon": -97.5}
    assert row["aircraft_name"] == "TEXSAR-01"
    assert row["feed_display_name"] == "TEXSAR-01 (K3F9PM)"
    assert row["thumb_bytes"] == blob


def test_max_seq_for_session(store) -> None:
    store.record_session(session_id="S-1", code="K3F9PM", worker_url="https://w")
    assert store.max_seq_for_session("S-1") == 0
    store.append_detection(_detection(seq=3))
    store.append_detection(_detection(seq=1, track_key="t1"))
    store.append_detection(_detection(seq=7, track_key="t2"))
    assert store.max_seq_for_session("S-1") == 7


def test_update_thumb_patches_every_matching_row(store) -> None:
    store.record_session(session_id="S-1", code="K3F9PM", worker_url="https://w")
    store.append_detection(_detection(seq=1, track_key="t1"))
    store.append_detection(_detection(seq=2, track_key="t1"))   # same track, new seq
    store.append_detection(_detection(seq=3, track_key="t2"))
    store.update_thumb("S-1", "t1", b"new-jpeg")
    rows = store.load_session_detections("S-1")
    by_seq = {r["seq"]: r for r in rows}
    assert by_seq[1]["thumb_bytes"] == b"new-jpeg"
    assert by_seq[2]["thumb_bytes"] == b"new-jpeg"
    assert "thumb_bytes" not in by_seq[3] or by_seq[3].get("thumb_bytes") is None


def test_recent_sessions_orders_by_last_seen_desc(store) -> None:
    store.record_session(session_id="A", code="AAA111", worker_url="https://w")
    # Force older last_seen_epoch_s on A.
    import sqlite3
    with sqlite3.connect(store._db_path) as conn:
        conn.execute(
            "UPDATE sessions SET last_seen_epoch_s = ? WHERE session_id = 'A'",
            (time.time() - 3600,),
        )
        conn.commit()
    store.record_session(session_id="B", code="BBB222", worker_url="https://w")
    rows = store.recent_sessions(limit=10)
    assert [r.session_id for r in rows] == ["B", "A"]


def test_prune_session_removes_session_and_detections(store) -> None:
    store.record_session(session_id="S-1", code="K3F9PM", worker_url="https://w")
    store.append_detection(_detection(seq=1))
    store.prune_session("S-1")
    assert store.get_session("S-1") is None
    assert store.load_session_detections("S-1") == []


def test_prune_older_than_drops_stale_sessions(store) -> None:
    store.record_session(session_id="OLD", code="O", worker_url="https://w")
    store.record_session(session_id="NEW", code="N", worker_url="https://w")
    import sqlite3
    with sqlite3.connect(store._db_path) as conn:
        conn.execute(
            "UPDATE sessions SET last_seen_epoch_s = ? WHERE session_id = 'OLD'",
            (1.0,),
        )
        conn.commit()
    deleted = store.prune_older_than(epoch_s=time.time() - 3600)
    assert deleted == 1
    assert store.get_session("OLD") is None
    assert store.get_session("NEW") is not None
