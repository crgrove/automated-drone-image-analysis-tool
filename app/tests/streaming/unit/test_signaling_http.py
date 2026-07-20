"""Unit tests for :class:`HttpSignalingChannel`.

These tests stub the ``httpx.AsyncClient`` so the channel can be exercised
without a live Cloudflare Worker. The goal is to verify the response
mapping — JSON envelopes, status codes — not to test ``httpx`` itself.

A live integration test against the deployed Worker is part of the manual
smoke checklist (plan §14) rather than this unit suite.
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Dict

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

httpx = pytest.importorskip("httpx")

from core.services.streaming.signaling import (  # noqa: E402
    CodeAlreadyAnswered,
    CodeNotFound,
    DEFAULT_WORKER_URL,
    HttpSignalingChannel,
    ViewerCapReached,
)


def _make_channel(handler):
    """Construct a channel whose underlying httpx client uses a MockTransport.

    The channel lazily creates one ``httpx.AsyncClient`` per asyncio loop via
    ``_create_client``; we override that factory so every loop the test spins
    up gets a fresh mocked client without touching the network.
    """
    transport = httpx.MockTransport(handler)
    channel = HttpSignalingChannel(base_url="https://example.test")
    channel._create_client = lambda: httpx.AsyncClient(
        transport=transport, timeout=5.0
    )
    return channel


def run(coro):
    return asyncio.run(coro)


def test_default_worker_url_is_used_when_not_overridden() -> None:
    channel = HttpSignalingChannel()
    assert channel.base_url == DEFAULT_WORKER_URL
    assert channel.base_url == "https://signal.adiat.app"
    asyncio.run(channel.close())


def test_get_offer_parses_json_envelope() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/sessions/ABC234/offer"
        return httpx.Response(
            200,
            json={"type": "offer", "sdp": "v=0\r\n..."},
        )

    channel = _make_channel(handler)
    sdp = run(channel.get_offer("ABC234"))
    assert sdp.startswith("v=0")
    run(channel.close())


def test_get_offer_accepts_plain_sdp_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="v=0\r\nplain-sdp", headers={"content-type": "application/sdp"})

    channel = _make_channel(handler)
    sdp = run(channel.get_offer("ABC234"))
    assert "plain-sdp" in sdp
    run(channel.close())


def test_get_offer_maps_404_to_code_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="not found")

    channel = _make_channel(handler)
    with pytest.raises(CodeNotFound):
        run(channel.get_offer("MSSNG2"))
    run(channel.close())


def test_get_offer_maps_409_to_code_already_answered() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(409, text="already answered")

    channel = _make_channel(handler)
    with pytest.raises(CodeAlreadyAnswered):
        run(channel.get_offer("DUPCAT"))
    run(channel.close())


def test_get_offer_maps_cap_reached_envelope() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"type": "cap_reached", "current": 3, "limit": 3},
        )

    channel = _make_channel(handler)
    with pytest.raises(ViewerCapReached) as exc_info:
        run(channel.get_offer("CAPCAP"))
    assert exc_info.value.current == 3
    assert exc_info.value.limit == 3
    run(channel.close())


def test_get_offer_accepts_legacy_offer_sdp_field() -> None:
    """Plan §18 (W4): Worker envelope ships both ``sdp`` and ``offer_sdp``;
    real builds in the field have been seen to only populate the legacy
    ``offer_sdp`` key. Desktop must tolerate that."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"type": "offer", "offer_sdp": "v=0\r\nlegacy-only-payload"},
        )

    channel = _make_channel(handler)
    sdp = run(channel.get_offer("LGCYFP"))
    assert sdp.startswith("v=0")
    assert "legacy-only" in sdp
    run(channel.close())


def test_get_offer_prefers_sdp_over_legacy_field() -> None:
    """When both fields are populated (the documented envelope shape),
    the new ``sdp`` field wins so we stay aligned with the WS broadcast."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "type": "offer",
                "sdp": "v=0\r\nnew-payload",
                "offer_sdp": "v=0\r\nlegacy-payload",
            },
        )

    channel = _make_channel(handler)
    sdp = run(channel.get_offer("BTHFLD"))
    assert "new-payload" in sdp
    assert "legacy-payload" not in sdp
    run(channel.close())


def test_get_offer_translates_unreachable_to_code_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    channel = _make_channel(handler)
    with pytest.raises(CodeNotFound):
        run(channel.get_offer("ABC234"))
    run(channel.close())


def test_post_answer_uses_v1_path_and_json_body() -> None:
    captured: Dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = request.read()
        return httpx.Response(200)

    channel = _make_channel(handler)
    run(channel.post_answer("ABC234", "v=0...answer"))
    assert captured["path"] == "/v1/sessions/ABC234/answer"
    assert b"v=0...answer" in captured["body"]
    run(channel.close())


def test_post_ice_targets_role_endpoint() -> None:
    captured: Dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        return httpx.Response(200)

    channel = _make_channel(handler)
    run(channel.post_ice("ABC234", "desktop", {"candidate": "candidate:1 ..."}))
    assert captured["path"] == "/v1/sessions/ABC234/ice/desktop"
    run(channel.close())


def test_post_ice_swallows_404_when_session_gone() -> None:
    """An ICE trickle after teardown should be a no-op, not an exception."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(410)

    channel = _make_channel(handler)
    # Should not raise.
    run(channel.post_ice("DELT22", "desktop", {"candidate": "x"}))
    run(channel.close())


def test_delete_session_is_best_effort() -> None:
    """``delete_session`` should not raise even when the Worker returns 404."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    channel = _make_channel(handler)
    run(channel.delete_session("ABC234"))
    run(channel.close())


def test_http_to_ws_conversion() -> None:
    assert HttpSignalingChannel._http_to_ws("https://x.example.com") == "wss://x.example.com"
    assert HttpSignalingChannel._http_to_ws("http://x.example.com") == "ws://x.example.com"
    assert HttpSignalingChannel._http_to_ws("ws://already.ws") == "ws://already.ws"


# ----------------------------------------------------------------------
# WebSocket subscribe — reconnect-with-backoff
# ----------------------------------------------------------------------
# These tests stub ``websockets.connect`` so we never touch the network.
# Each "connect attempt" returns an async context manager whose iterator
# yields a deterministic sequence of frames or raises a predetermined
# exception, modeling either a successful connection or a transport drop.


pytest.importorskip("websockets")


class _FakeWs:
    """Async-iterable stub modeling one WebSocket connection cycle.

    Pass either a list of JSON-encodable frames to yield, or an Exception
    instance to raise after yielding any preceding frames.
    """

    def __init__(self, *, frames=(), raise_after=None):
        self._frames = list(frames)
        self._raise_after = raise_after

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._frames:
            frame = self._frames.pop(0)
            # Preserve dict→JSON convenience for the test author
            if isinstance(frame, dict):
                import json
                return json.dumps(frame)
            return frame
        if self._raise_after is not None:
            raise self._raise_after
        raise StopAsyncIteration


def _patch_websockets(monkeypatch, factories):
    """Replace ``websockets.connect`` with a factory queue.

    Each call to ``connect(url)`` pops the next factory in the queue. The
    factory is invoked (no args) and must return an async context manager.
    Once the queue is exhausted, subsequent calls raise so the channel's
    backoff loop is forced to exit when the test wants it to.
    """
    import websockets  # type: ignore

    queue = list(factories)

    def _connect(_url, **_kwargs):
        if not queue:
            raise RuntimeError("test factory queue exhausted")
        return queue.pop(0)()

    monkeypatch.setattr(websockets, "connect", _connect)


def test_subscribe_yields_frames_from_single_session(monkeypatch) -> None:
    _patch_websockets(
        monkeypatch,
        [
            lambda: _FakeWs(
                frames=[
                    {"type": "ice", "candidate": {"candidate": "c1"}},
                    {"type": "ice", "candidate": {"candidate": "c2"}},
                    {"type": "closed", "reason": "session ended"},
                ]
            ),
        ],
    )
    channel = HttpSignalingChannel(base_url="https://example.test")
    seen = []

    async def consume():
        async for msg in channel.subscribe("ABC234", "desktop"):
            seen.append(msg)

    run(consume())
    run(channel.close())
    # All three frames should arrive; the ``closed`` message terminates
    # the generator without an outer reconnect attempt.
    assert [m["type"] for m in seen] == ["ice", "ice", "closed"]


def test_subscribe_reconnects_after_transport_drop(monkeypatch) -> None:
    # First connection drops mid-stream; second connection delivers a
    # ``closed`` so the generator can terminate cleanly.
    _patch_websockets(
        monkeypatch,
        [
            lambda: _FakeWs(
                frames=[{"type": "ice", "candidate": {"candidate": "c1"}}],
                raise_after=ConnectionResetError("simulated drop"),
            ),
            lambda: _FakeWs(
                frames=[
                    {"type": "ice", "candidate": {"candidate": "c2"}},
                    {"type": "closed", "reason": "ok"},
                ]
            ),
        ],
    )
    channel = HttpSignalingChannel(base_url="https://example.test")
    # Shrink the backoff so the test completes quickly.
    channel.SUBSCRIBE_INITIAL_BACKOFF = 0.0
    channel.SUBSCRIBE_MAX_BACKOFF = 0.0

    seen = []

    async def consume():
        async for msg in channel.subscribe("ABC234", "desktop"):
            seen.append(msg)

    run(consume())
    run(channel.close())
    # Frames from both connection cycles should arrive in order.
    candidates = [m["candidate"]["candidate"] for m in seen if m["type"] == "ice"]
    assert candidates == ["c1", "c2"]
    assert seen[-1]["type"] == "closed"


def test_subscribe_exits_when_channel_closed(monkeypatch) -> None:
    # Connection drops; channel is closed before the reconnect window
    # expires, so the generator must exit rather than spin.
    closed_event = asyncio.Event()

    def _factory():
        closed_event.set()
        return _FakeWs(raise_after=ConnectionResetError("simulated drop"))

    _patch_websockets(monkeypatch, [_factory])
    channel = HttpSignalingChannel(base_url="https://example.test")
    channel.SUBSCRIBE_INITIAL_BACKOFF = 0.05
    channel.SUBSCRIBE_MAX_BACKOFF = 0.05

    async def consume():
        # Schedule a close() that will fire once the first connect attempt
        # has happened, so the backoff loop sees ``self._closed = True``
        # after sleeping and exits.
        async def closer():
            await closed_event.wait()
            await channel.close()

        asyncio.create_task(closer())
        async for _msg in channel.subscribe("ABC234", "desktop"):
            pass  # consume but expect to exit quickly

    run(consume())
