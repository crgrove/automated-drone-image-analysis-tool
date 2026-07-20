"""In-process :class:`SignalingChannel` implementation for tests + local dev.

Used by the unit/integration suites and by anyone running both peers on
the same machine without needing the Cloudflare Worker. The class is
intentionally small: a dict of offers/answers plus a per-(code, role)
asyncio.Queue that backs the WebSocket-equivalent ``subscribe`` channel.

Both publisher and viewer sides must share the *same* channel object
(typically constructed once per pytest test). Pre-populate offers via
:meth:`put_offer` and observe answers via :meth:`get_answer`.
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from typing import AsyncIterator, Dict, Optional, Tuple

from .SignalingChannel import (
    CodeAlreadyAnswered,
    CodeNotFound,
    SignalingChannel,
    ViewerCapReached,
)


class InMemorySignalingChannel(SignalingChannel):
    """Asyncio-friendly in-process signaling backend for tests + local dev."""

    def __init__(self, *, ttl_seconds: float = 30.0):
        self._ttl = float(ttl_seconds)
        self._offers: Dict[str, Tuple[str, float]] = {}
        self._answers: Dict[str, Tuple[str, float]] = {}
        self._answered_codes: set[str] = set()
        self._cap_responses: Dict[str, Tuple[int, int]] = {}
        # One async queue per (code, role) — the subscribing side gets
        # candidates the *other* side has posted.
        self._mailboxes: Dict[Tuple[str, str], "asyncio.Queue[Optional[dict]]"] = defaultdict(asyncio.Queue)

    # ------------------------------------------------------------------
    # SignalingChannel surface
    # ------------------------------------------------------------------

    async def get_offer(self, code: str) -> str:
        if code in self._cap_responses:
            current, limit = self._cap_responses[code]
            raise ViewerCapReached(current=current, limit=limit)
        if code in self._answered_codes:
            raise CodeAlreadyAnswered(f"code {code!r} already answered")
        record = self._offers.get(code)
        if record is None or record[1] < time.monotonic():
            raise CodeNotFound(f"no offer for code {code!r}")
        return record[0]

    async def post_answer(self, code: str, sdp: str) -> None:
        self._answers[code] = (sdp, time.monotonic() + self._ttl)
        self._answered_codes.add(code)
        # Notify any mobile-side subscriber that an answer has landed.
        await self._mailboxes[(code, "mobile")].put({"type": "answer", "sdp": sdp})

    async def post_ice(self, code: str, role: str, candidate: dict) -> None:
        peer_role = "mobile" if role == "desktop" else "desktop"
        # Wire shape matches the Worker WS broadcast (plan §8): `{type:"ice",
        # candidate:{…}}`. The desktop consumer accepts both ``"ice"`` and
        # ``"candidate"`` for backward compat, but production code paths use
        # ``"ice"``.
        await self._mailboxes[(code, peer_role)].put(
            {"type": "ice", "candidate": dict(candidate)}
        )

    async def subscribe(self, code: str, role: str) -> AsyncIterator[dict]:  # type: ignore[override]
        queue = self._mailboxes[(code, role)]
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=self._ttl)
            except asyncio.TimeoutError:
                return
            if msg is None:
                return
            yield msg

    async def delete_session(self, code: str) -> None:
        self._offers.pop(code, None)
        self._answers.pop(code, None)
        self._answered_codes.discard(code)
        self._cap_responses.pop(code, None)
        # Drain subscribers via the sentinel.
        for role in ("mobile", "desktop"):
            queue = self._mailboxes.pop((code, role), None)
            if queue is not None:
                await queue.put(None)

    async def close(self) -> None:
        self._offers.clear()
        self._answers.clear()
        self._answered_codes.clear()
        self._cap_responses.clear()
        for queue in list(self._mailboxes.values()):
            await queue.put(None)
        self._mailboxes.clear()

    # ------------------------------------------------------------------
    # test helpers
    # ------------------------------------------------------------------

    def put_offer(self, code: str, sdp: str, *, ttl_seconds: Optional[float] = None) -> None:
        """Pre-populate an offer the way the Worker would after a mobile POST."""
        ttl = self._ttl if ttl_seconds is None else float(ttl_seconds)
        self._offers[code] = (sdp, time.monotonic() + ttl)

    def expire_offer(self, code: str) -> None:
        """Force-expire an offer so :meth:`get_offer` raises :class:`CodeNotFound`."""
        if code in self._offers:
            sdp, _ = self._offers[code]
            self._offers[code] = (sdp, time.monotonic() - 1.0)

    def get_answer(self, code: str) -> Optional[str]:
        """Inspect the most recent answer the desktop posted (test-side)."""
        record = self._answers.get(code)
        return record[0] if record else None

    def set_viewer_cap_response(self, code: str, current: int, limit: int) -> None:
        """Simulate the publisher-side ``cap_reached`` response on the offer."""
        self._cap_responses[code] = (int(current), int(limit))

    def mark_answered(self, code: str) -> None:
        """Simulate the ``already answered`` race per plan §9 *Trust model*."""
        self._answered_codes.add(code)
