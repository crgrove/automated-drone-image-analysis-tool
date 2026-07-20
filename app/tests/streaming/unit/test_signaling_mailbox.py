"""Unit tests for :class:`InMemorySignalingChannel` (plan §12).

Exercises the new abstract :class:`SignalingChannel` contract (plan §8)
against the in-memory backend. The same test surface should pass against
any :class:`HttpSignalingChannel` driven via a mock HTTP server; the
in-memory channel is the deterministic baseline.
"""

from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.signaling import (  # noqa: E402
    CodeAlreadyAnswered,
    CodeNotFound,
    InMemorySignalingChannel,
    ViewerCapReached,
)


def run(coro):
    return asyncio.run(coro)


def test_get_offer_returns_published_sdp() -> None:
    async def scenario():
        ch = InMemorySignalingChannel()
        ch.put_offer("ABC234", "v=0...offer")
        sdp = await ch.get_offer("ABC234")
        assert sdp == "v=0...offer"

    run(scenario())


def test_get_offer_raises_code_not_found_when_missing() -> None:
    async def scenario():
        ch = InMemorySignalingChannel()
        with pytest.raises(CodeNotFound):
            await ch.get_offer("MSSNG2")

    run(scenario())


def test_get_offer_raises_code_already_answered() -> None:
    async def scenario():
        ch = InMemorySignalingChannel()
        ch.put_offer("DUPCAT", "v=0...offer")
        ch.mark_answered("DUPCAT")
        with pytest.raises(CodeAlreadyAnswered):
            await ch.get_offer("DUPCAT")

    run(scenario())


def test_get_offer_raises_viewer_cap_reached() -> None:
    async def scenario():
        ch = InMemorySignalingChannel()
        ch.set_viewer_cap_response("CAPCAP", current=3, limit=3)
        with pytest.raises(ViewerCapReached) as exc_info:
            await ch.get_offer("CAPCAP")
        assert exc_info.value.current == 3
        assert exc_info.value.limit == 3

    run(scenario())


def test_get_offer_raises_when_expired() -> None:
    async def scenario():
        ch = InMemorySignalingChannel()
        ch.put_offer("XPRDTL", "v=0...offer")
        ch.expire_offer("XPRDTL")
        with pytest.raises(CodeNotFound):
            await ch.get_offer("XPRDTL")

    run(scenario())


def test_post_answer_round_trip() -> None:
    async def scenario():
        ch = InMemorySignalingChannel()
        await ch.post_answer("RTRPP2", "v=0...answer")
        assert ch.get_answer("RTRPP2") == "v=0...answer"

    run(scenario())


def test_delete_session_drops_offer_and_answer() -> None:
    async def scenario():
        ch = InMemorySignalingChannel()
        ch.put_offer("DETETE", "v=0...offer")
        await ch.post_answer("DETETE", "v=0...answer")
        await ch.delete_session("DETETE")
        # New `get_offer` should now return CodeNotFound — record gone.
        with pytest.raises(CodeNotFound):
            await ch.get_offer("DETETE")
        assert ch.get_answer("DETETE") is None

    run(scenario())


def test_subscribe_yields_posted_ice_candidates_in_order() -> None:
    """Plan §8 wire shape: the Worker emits ``{type:"ice", candidate:{…}}``."""

    async def scenario():
        ch = InMemorySignalingChannel()
        candidates = []

        async def collect():
            async for msg in ch.subscribe("JCEERD", "desktop"):
                if msg.get("type") == "ice":
                    candidates.append(msg["candidate"])
                    if len(candidates) >= 3:
                        break

        collector = asyncio.create_task(collect())
        # Mobile posts three candidates → desktop's subscribe sees them.
        await ch.post_ice("JCEERD", "mobile", {"candidate": "c1"})
        await ch.post_ice("JCEERD", "mobile", {"candidate": "c2"})
        await ch.post_ice("JCEERD", "mobile", {"candidate": "c3"})
        await asyncio.wait_for(collector, timeout=1.0)
        assert [c["candidate"] for c in candidates] == ["c1", "c2", "c3"]

    run(scenario())


def test_post_answer_emits_answer_to_mobile_subscriber() -> None:
    """Mobile-side WS subscriber gets an ``{type: answer}`` message when desktop POSTs."""
    async def scenario():
        ch = InMemorySignalingChannel()
        observed = []

        async def collect():
            async for msg in ch.subscribe("ANSWRD", "mobile"):
                observed.append(msg)
                if msg.get("type") == "answer":
                    break

        collector = asyncio.create_task(collect())
        await ch.post_answer("ANSWRD", "v=0...answer")
        await asyncio.wait_for(collector, timeout=1.0)
        assert observed[-1]["type"] == "answer"
        assert observed[-1]["sdp"] == "v=0...answer"

    run(scenario())
