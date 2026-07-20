"""Unit tests for the §20 wire-level pieces: GET /state + meta-channel
``resume_complete`` / ``session_changed`` control messages + (session_id,
seq) dedup on the detection feed.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

httpx = pytest.importorskip("httpx")

from core.services.streaming.DetectionFeedService import DetectionFeedService  # noqa: E402
from core.services.streaming.signaling import HttpSignalingChannel, SessionState  # noqa: E402


# ---------------------------------------------------------------------
# HttpSignalingChannel.get_session_state
# ---------------------------------------------------------------------


def _make_channel(handler):
    transport = httpx.MockTransport(handler)
    channel = HttpSignalingChannel(base_url="https://example.test")
    channel._create_client = lambda: httpx.AsyncClient(transport=transport, timeout=5.0)
    return channel


def _run(coro):
    return asyncio.run(coro)


def test_get_session_state_parses_awaiting_viewer() -> None:
    def handler(request):
        assert request.url.path == "/v1/sessions/CODE12/state"
        return httpx.Response(
            200,
            json={
                "state": "awaiting_viewer",
                "session_id": "S-uuid-1",
                "has_offer": True,
            },
        )
    channel = _make_channel(handler)
    state = _run(channel.get_session_state("CODE12"))
    assert state == SessionState(
        state="awaiting_viewer", session_id="S-uuid-1", has_offer=True
    )


def test_get_session_state_treats_404_as_ended() -> None:
    def handler(_):
        return httpx.Response(404, text="not found")
    channel = _make_channel(handler)
    state = _run(channel.get_session_state("MISSNG"))
    assert state.state == "ended"
    assert state.session_id is None
    assert state.has_offer is False


def test_get_session_state_falls_back_on_malformed_json() -> None:
    def handler(_):
        return httpx.Response(200, text="not-json")
    channel = _make_channel(handler)
    state = _run(channel.get_session_state("BADRSP"))
    assert state.state == "ended"


def test_get_session_state_falls_back_on_unknown_state_string() -> None:
    def handler(_):
        return httpx.Response(200, json={"state": "weird", "session_id": "X"})
    channel = _make_channel(handler)
    state = _run(channel.get_session_state("WEIRD1"))
    # Unknown states are normalized to "ended" so the desktop falls
    # back to a clean pairing prompt instead of crashing.
    assert state.state == "ended"


# ---------------------------------------------------------------------
# DetectionFeedService control messages + dedup
# ---------------------------------------------------------------------


def _meta_envelope(session_id: str, seq: int, track_key: str = "t-1") -> bytes:
    return json.dumps({
        "event": "promote",
        "session_id": session_id,
        "seq": seq,
        "track_key": track_key,
        "detector_id": "person",
        "class_name": "person",
        "confidence": 0.9,
        "bbox_norm": [0.1, 0.1, 0.1, 0.1],
        "captured_at_ms": 1_700_000_000_000,
    }).encode("utf-8")


def test_meta_dedupes_by_session_id_seq(qtbot) -> None:
    svc = DetectionFeedService()
    received = []
    svc.detectionPromoted.connect(lambda env: received.append(env))
    svc.handle_message("detections.meta", _meta_envelope("S-1", 1))
    svc.handle_message("detections.meta", _meta_envelope("S-1", 1))  # dup
    svc.handle_message("detections.meta", _meta_envelope("S-1", 2))
    svc.handle_message("detections.meta", _meta_envelope("S-2", 1))  # new session
    seq_pairs = [(e["session_id"], e["seq"]) for e in received]
    assert seq_pairs == [("S-1", 1), ("S-1", 2), ("S-2", 1)]


def test_meta_resume_complete_routes_to_resumeComplete_signal(qtbot) -> None:
    svc = DetectionFeedService()
    received = []
    svc.resumeComplete.connect(lambda sid, seq: received.append((sid, seq)))
    payload = json.dumps({
        "kind": "resume_complete",
        "session_id": "S-42",
        "last_seq": 17,
    }).encode("utf-8")
    svc.handle_message("detections.meta", payload)
    assert received == [("S-42", 17)]


def test_meta_session_changed_routes_to_sessionChanged_signal(qtbot) -> None:
    svc = DetectionFeedService()
    received = []
    svc.sessionChanged.connect(lambda new_sid: received.append(new_sid))
    payload = json.dumps({
        "kind": "session_changed",
        "new_session_id": "S-99",
    }).encode("utf-8")
    svc.handle_message("detections.meta", payload)
    assert received == ["S-99"]


def test_meta_control_messages_dont_emit_detectionPromoted(qtbot) -> None:
    svc = DetectionFeedService()
    promoted = []
    svc.detectionPromoted.connect(lambda env: promoted.append(env))
    for payload in (
        b'{"kind":"resume_complete","session_id":"S","last_seq":1}',
        b'{"kind":"session_changed","new_session_id":"S2"}',
    ):
        svc.handle_message("detections.meta", payload)
    assert promoted == []
