"""Abstract :class:`SignalingChannel` for the Flight Viewer.

The plan §8 defines a thin HTTPS + WebSocket interface against the
``adiat-flight-signaling`` Cloudflare Worker. Concrete backends
(:class:`HttpSignalingChannel` for production, :class:`InMemorySignalingChannel`
for tests) implement the five coroutine surface points below.

The desktop never publishes an offer — mobile creates the session via
``POST /v1/sessions``. The desktop only reads ``offer``, writes
``answer``, exchanges ICE candidates, and (optionally) deletes the
session early.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Optional


@dataclass(frozen=True)
class SessionState:
    """Worker's view of a pairing code (plan §20 ``GET /v1/sessions/:code/state``).

    Returned by :meth:`SignalingChannel.get_session_state`. Lets the
    desktop decide whether to auto-resume a persisted session
    (``state == "awaiting_viewer"`` and matching ``session_id``),
    show a "code already in use" prompt (``state == "active"``), or
    fall back to a fresh-pair flow (``state == "ended"`` / missing).
    """

    state: str          # "active" | "awaiting_viewer" | "ended"
    session_id: Optional[str]
    has_offer: bool


class CodeNotFound(LookupError):
    """Raised when no session exists for the requested code, or it expired."""


class CodeAlreadyAnswered(RuntimeError):
    """Raised when the session already has an answer posted.

    Distinct from :class:`CodeNotFound` per plan §9 *Trust model*: a code
    that has already been answered should prompt the operator to suspect
    interception and generate a fresh code.
    """


class ViewerCapReached(RuntimeError):
    """Raised when the publisher signals it already has the maximum viewers.

    Carries the current viewer count in :attr:`current` and the cap in
    :attr:`limit` so the dialog can render a precise message.
    """

    def __init__(self, current: int, limit: int):
        super().__init__(
            f"Publisher reports {current}/{limit} viewers already connected"
        )
        self.current = current
        self.limit = limit


class SignalingChannel(ABC):
    """Abstract base for Flight Viewer signaling backends.

    Implementations *must* be safe to use from inside an asyncio event
    loop. None of the methods touch media; payloads are small JSON
    representing SDP or ICE candidates.
    """

    @abstractmethod
    async def get_offer(self, code: str) -> str:
        """Fetch the publisher's SDP offer for ``code``.

        Raises:
            CodeNotFound: When no session exists for ``code`` or it has
                expired/timed out.
            CodeAlreadyAnswered: When an answer was posted before this
                read — possible MitM race per plan §9.
            ViewerCapReached: When the publisher signals it has reached
                its concurrent-viewer cap.
        """

    @abstractmethod
    async def post_answer(self, code: str, sdp: str) -> None:
        """Submit the viewer's SDP answer for ``code``."""

    @abstractmethod
    async def post_ice(self, code: str, role: str, candidate: dict) -> None:
        """Submit a trickled ICE candidate.

        Args:
            code: Pairing code.
            role: ``"desktop"`` for this side; ``"mobile"`` is the peer.
            candidate: ICE candidate dict (``candidate``/``sdpMid``/``sdpMLineIndex``).
        """

    @abstractmethod
    def subscribe(self, code: str, role: str) -> AsyncIterator[dict]:
        """Yield JSON messages as the peer publishes them.

        Each message is a dict shaped ``{"type": "...", ...}`` matching
        the Worker's WebSocket envelope (plan §8). Known types include
        ``candidate``, ``answer``, ``closed``, ``error``.
        """

    async def get_session_state(self, code: str) -> SessionState:
        """Return the Worker's session-state view of ``code`` (plan §20).

        Default implementation returns ``SessionState("ended", None, False)``
        so older signaling backends that don't expose the state endpoint
        cleanly downgrade to "treat as expired" — the desktop falls
        through to the empty pairing dialog rather than crashing.
        """
        return SessionState(state="ended", session_id=None, has_offer=False)

    @abstractmethod
    async def delete_session(self, code: str) -> None:
        """Operator-initiated teardown of the session.

        Best-effort; deletions that fail because the session already
        evicted from the Worker's Durable Object are not an error.
        """

    @abstractmethod
    async def close(self) -> None:
        """Release any backing resources (HTTP pool, websockets)."""
