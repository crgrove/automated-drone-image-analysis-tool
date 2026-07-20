"""HTTPS + WebSocket :class:`SignalingChannel` against the Cloudflare Worker.

Talks to the ``adiat-flight-signaling`` Worker (plan §8). The desktop
needs no credentials — the Worker exposes a public URL and enforces
single-use codes + TTLs entirely server-side via a Durable Object per
pairing code.

Wire shape (plan §8):

* ``GET    /v1/sessions/{code}/offer``                  → offer SDP
* ``POST   /v1/sessions/{code}/answer``                 → submit answer
* ``POST   /v1/sessions/{code}/ice/{role}``             → trickle ICE
* ``WS     /v1/sessions/{code}/subscribe?role={role}``  → stream peer events
* ``DELETE /v1/sessions/{code}``                        → tear down session

Responses are JSON-shaped where possible. For the offer endpoint we
expect either:

* ``200`` ``{"type": "offer", "sdp": "..."}``
* ``200`` ``{"type": "cap_reached", "current": N, "limit": M}``
* ``404`` no such code (mapped to :class:`CodeNotFound`)
* ``409`` already answered (mapped to :class:`CodeAlreadyAnswered`)
"""

from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Optional

from core.services.LoggerService import LoggerService

from .SignalingChannel import (
    CodeAlreadyAnswered,
    CodeNotFound,
    SessionState,
    SignalingChannel,
    ViewerCapReached,
)


# Canonical ADIAT-hosted Worker URL (custom domain on Cloudflare; the
# ``workers.dev`` URL of the same deployment is the documented fallback if
# DNS for ``adiat.app`` is misconfigured — see plan §17 *Worker URL
# configuration*). Operators can override via ``config.toml`` under the
# ``[signaling] base_url`` key; see :class:`FlightViewerController` for the
# lookup. The URL is intentionally public — no credentials embedded.
DEFAULT_WORKER_URL = "https://signal.adiat.app"


def _extract_sdp(payload: dict) -> Optional[str]:
    """Read an SDP from a Worker envelope, tolerating the legacy field name.

    Plan §18 (W4) documents that ``GET /offer`` returns both ``sdp`` and
    ``offer_sdp`` for backward compatibility. The same envelope shape is
    also broadcast over the WebSocket for iceRestart re-offers. Real
    Worker builds in the field have been seen to only populate the
    legacy ``offer_sdp`` key, so we always check both.
    """
    if not isinstance(payload, dict):
        return None
    for field in ("sdp", "offer_sdp"):
        value = payload.get(field)
        if isinstance(value, str) and value:
            return value
    return None

# ``httpx`` and ``websockets`` are imported lazily so importing this module
# does not fail when the optional dependencies are absent (the Flight
# Viewer's launch path raises an actionable ImportError if the user picks
# this backend without installing them).


def _require_httpx():
    try:
        import httpx  # type: ignore  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "httpx is required for HttpSignalingChannel. "
            "Run `pip install httpx websockets` to enable Cloudflare Worker signaling."
        ) from exc


def _require_websockets():
    try:
        import websockets  # type: ignore  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "websockets is required for HttpSignalingChannel. "
            "Run `pip install httpx websockets` to enable Cloudflare Worker signaling."
        ) from exc


class HttpSignalingChannel(SignalingChannel):
    """Cloudflare Worker signaling channel.

    Pairs an ``httpx.AsyncClient`` (for the four REST endpoints) with a
    fresh ``websockets`` connection per :meth:`subscribe` call. The class
    is reusable across multiple pairing codes — one channel instance
    typically backs many tiles in the :class:`FlightViewerController`.
    """

    # Reconnect-with-backoff bounds for :meth:`subscribe`. The first
    # reconnect attempt waits ``SUBSCRIBE_INITIAL_BACKOFF`` seconds; each
    # subsequent attempt doubles up to ``SUBSCRIBE_MAX_BACKOFF`` (plan §18
    # → *Desktop residual work* item 1).
    SUBSCRIBE_INITIAL_BACKOFF = 1.0
    SUBSCRIBE_MAX_BACKOFF = 30.0

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        http_timeout: float = 30.0,
    ):
        _require_httpx()

        self.logger = LoggerService()
        self._base_url = (base_url or DEFAULT_WORKER_URL).rstrip("/")
        self._http_timeout = float(http_timeout)
        # One ``httpx.AsyncClient`` per asyncio loop that uses this channel.
        # The viewer reuses a single channel across multiple per-tile
        # QThreads; each tile runs its own loop, and an httpx client binds
        # its connection pool to whichever loop first awaits on it. Sharing
        # one client across loops poisons it the moment the first loop
        # closes ("Event loop is closed" when adding a second feed after
        # the first tile tears down). Keyed by ``id(loop)`` — when a loop
        # ends, its client is left for GC; its pool is already dead.
        self._clients_by_loop: dict = {}
        # Set by :meth:`close` so a long-running :meth:`subscribe` loop
        # exits its reconnect-with-backoff retry rather than spinning
        # forever after the channel is shut down.
        self._closed = False

    def _create_client(self):
        """Factory hook for the per-loop ``httpx.AsyncClient``.

        Production builds return a real client. Unit tests override this on
        the instance to inject an ``httpx.AsyncClient`` backed by
        ``httpx.MockTransport`` without having to also monkey-patch the
        per-loop cache.
        """
        import httpx  # type: ignore

        return httpx.AsyncClient(timeout=self._http_timeout)

    def _client(self):
        """Return the ``httpx.AsyncClient`` bound to the current loop.

        Must be called from inside an ``async def`` method — uses
        :func:`asyncio.get_running_loop` to identify the caller's loop and
        lazily creates a client the first time a given loop touches us.
        """
        loop = asyncio.get_running_loop()
        key = id(loop)
        client = self._clients_by_loop.get(key)
        if client is None:
            client = self._create_client()
            self._clients_by_loop[key] = client
        return client

    # ------------------------------------------------------------------
    # public surface
    # ------------------------------------------------------------------

    async def get_offer(self, code: str) -> str:
        import httpx  # type: ignore

        url = f"{self._base_url}/v1/sessions/{code}/offer"
        try:
            response = await self._client().get(url)
        except httpx.HTTPError as exc:
            raise CodeNotFound(
                f"signaling backend unreachable for code {code!r}: {exc}"
            ) from exc

        if response.status_code == 404:
            raise CodeNotFound(f"no session for code {code!r}")
        if response.status_code == 409:
            raise CodeAlreadyAnswered(
                f"code {code!r} has already been answered"
            )
        if response.status_code >= 400:
            response.raise_for_status()

        # Parse the response envelope. The Worker may return either a raw
        # SDP string (text/plain or application/sdp) or a JSON envelope
        # with ``{"type": "offer", "sdp": ...}`` / ``{"type": "cap_reached", ...}``.
        content_type = (response.headers.get("content-type") or "").lower()
        if "application/json" in content_type:
            try:
                payload = response.json()
            except json.JSONDecodeError as exc:
                raise CodeNotFound(
                    f"signaling returned malformed JSON for code {code!r}: {exc}"
                ) from exc
            return self._extract_offer_from_envelope(code, payload)
        return response.text

    async def post_answer(self, code: str, sdp: str) -> None:
        import httpx  # type: ignore

        # Defensive guard. aiortc occasionally produces a transient empty
        # ``localDescription`` if setLocalDescription is awaited while ICE
        # gathering is still running. The Worker rejects empty SDPs with a
        # 400 + "sdp must be a non-empty string" message that
        # ``raise_for_status`` then drops, so a quick local pre-check
        # surfaces a clearer error.
        if not isinstance(sdp, str) or not sdp.strip():
            raise CodeNotFound(
                f"refusing to POST empty answer SDP for code {code!r} — "
                "aiortc's setLocalDescription may not have produced a body yet"
            )

        url = f"{self._base_url}/v1/sessions/{code}/answer"
        try:
            # Send both ``sdp`` (new, modern) and ``answer_sdp`` (legacy
            # field name) — the Worker accepts either, this keeps us
            # forward- and backward-compatible.
            response = await self._client().post(
                url, json={"sdp": sdp, "answer_sdp": sdp}
            )
        except httpx.HTTPError as exc:
            raise CodeNotFound(
                f"signaling backend unreachable while posting answer for "
                f"code {code!r}: {exc}"
            ) from exc

        if response.status_code == 404:
            raise CodeNotFound(f"no session for code {code!r}")
        if response.status_code == 409:
            raise CodeAlreadyAnswered(
                f"code {code!r} has already been answered"
            )
        if response.status_code >= 400:
            # Surface the Worker's error message + body length in the
            # raised exception so the operator-facing dialog has
            # something more diagnostic than "400 Bad Request".
            worker_msg = self._extract_worker_error(response)
            raise CodeNotFound(
                f"POST /answer for code {code!r} failed with HTTP "
                f"{response.status_code}: {worker_msg} "
                f"(body sent: {len(sdp)} bytes)"
            )

    async def post_ice(self, code: str, role: str, candidate: dict) -> None:
        import httpx  # type: ignore

        url = f"{self._base_url}/v1/sessions/{code}/ice/{role}"
        try:
            response = await self._client().post(url, json={"candidate": candidate})
        except httpx.HTTPError as exc:
            # ICE trickle is opportunistic — log and swallow so a single
            # blip does not tear down the session.
            self.logger.debug(
                f"HttpSignalingChannel.post_ice failed for {code}/{role}: {exc}"
            )
            return

        if response.status_code in (404, 410):
            # Session is gone — peer probably already finished or expired.
            return
        if response.status_code >= 400:
            self.logger.debug(
                f"HttpSignalingChannel.post_ice non-2xx for {code}/{role}: "
                f"{response.status_code}"
            )

    async def subscribe(self, code: str, role: str) -> AsyncIterator[dict]:  # type: ignore[override]
        """Yield WS messages from the Worker, transparently reconnecting on drop.

        The Worker's per-role subscribe handler replays the current cached
        state (offer, answer, ICE candidates) to a freshly-attached watcher,
        so the consumer doesn't need to worry about losing messages across a
        reconnect — they're just re-delivered. We:

        * Loop forever (until :meth:`close` is called or the consumer cancels
          the generator) attempting to re-establish the WebSocket.
        * Use exponential backoff between attempts, capped at
          :attr:`SUBSCRIBE_MAX_BACKOFF`. Backoff is reset to
          :attr:`SUBSCRIBE_INITIAL_BACKOFF` whenever at least one frame is
          received on a connection, so a brief blip doesn't penalize the
          next legitimate disconnect.
        * Terminate on a yielded ``{type:"closed"}`` message — that's the
          publisher / Worker indicating the session is genuinely over,
          which is different from a transport-layer reconnect.
        """
        _require_websockets()
        import websockets  # type: ignore

        ws_url = self._http_to_ws(self._base_url)
        url = f"{ws_url}/v1/sessions/{code}/subscribe?role={role}"
        backoff = self.SUBSCRIBE_INITIAL_BACKOFF

        while not self._closed:
            received_any = False
            session_closed = False
            try:
                async with websockets.connect(
                    url,
                    # Detect dead connections at Cloudflare's edge — without
                    # these, an idle socket can sit silently after a half-NAT
                    # rebinding for several minutes before the OS finally
                    # surfaces a TCP reset. Per plan §19.1.
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                ) as ws:
                    async for raw in ws:
                        if isinstance(raw, bytes):
                            try:
                                raw = raw.decode("utf-8")
                            except UnicodeDecodeError:
                                continue
                        try:
                            message = json.loads(raw)
                        except json.JSONDecodeError as exc:
                            self.logger.debug(
                                f"HttpSignalingChannel.subscribe dropping non-JSON "
                                f"frame for {code}/{role}: {exc}"
                            )
                            continue
                        if not isinstance(message, dict):
                            continue
                        # Reset backoff on the first successful frame of any
                        # connection cycle so the next disconnect starts
                        # back at 1s rather than where the previous attempt
                        # left off.
                        if not received_any:
                            received_any = True
                            backoff = self.SUBSCRIBE_INITIAL_BACKOFF
                        if message.get("type") == "closed":
                            session_closed = True
                        yield message
                        if session_closed:
                            return
            except (GeneratorExit, asyncio.CancelledError):
                # Consumer cancelled or generator was closed — propagate so
                # the calling task can shut down cleanly.
                raise
            except Exception as exc:  # noqa: BLE001
                self.logger.warning(
                    f"HttpSignalingChannel.subscribe disconnected for "
                    f"{code}/{role} (backoff {backoff:.0f}s): {exc}"
                )

            if self._closed:
                return

            # Back off before reconnecting. Cancellation while sleeping must
            # exit cleanly so the consumer can shut us down.
            try:
                await asyncio.sleep(backoff)
            except (GeneratorExit, asyncio.CancelledError):
                raise
            backoff = min(backoff * 2, self.SUBSCRIBE_MAX_BACKOFF)

    async def get_session_state(self, code: str) -> SessionState:
        """Query the Worker's ``GET /v1/sessions/:code/state`` (plan §20).

        Used by :class:`FlightViewerController` to decide whether to
        auto-resume a persisted pairing on launch. Any error path —
        backend unreachable, 404, malformed body — degrades to a
        synthetic ``"ended"`` response so the desktop falls through
        to the empty pairing dialog rather than hanging.
        """
        import httpx  # type: ignore

        ended = SessionState(state="ended", session_id=None, has_offer=False)
        url = f"{self._base_url}/v1/sessions/{code}/state"
        try:
            response = await self._client().get(url)
        except httpx.HTTPError as exc:
            self.logger.debug(
                f"HttpSignalingChannel.get_session_state unreachable for "
                f"{code}: {exc}"
            )
            return ended
        if response.status_code == 404:
            return ended
        if response.status_code >= 400:
            self.logger.debug(
                f"HttpSignalingChannel.get_session_state non-2xx for "
                f"{code}: {response.status_code}"
            )
            return ended
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            self.logger.debug(
                f"HttpSignalingChannel.get_session_state malformed JSON "
                f"for {code}: {exc}"
            )
            return ended
        if not isinstance(payload, dict):
            return ended
        state = payload.get("state")
        if state not in ("active", "awaiting_viewer", "ended"):
            state = "ended"
        session_id = payload.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            session_id = None
        return SessionState(
            state=str(state),
            session_id=session_id,
            has_offer=bool(payload.get("has_offer")),
        )

    async def delete_session(self, code: str) -> None:
        import httpx  # type: ignore

        url = f"{self._base_url}/v1/sessions/{code}"
        try:
            response = await self._client().delete(url)
        except httpx.HTTPError as exc:
            # Best-effort: the Worker will TTL-evict on its own; surface a
            # debug log so this is visible if needed.
            self.logger.debug(
                f"HttpSignalingChannel.delete_session swallowed error for "
                f"{code}: {exc}"
            )
            return
        if response.status_code >= 400 and response.status_code != 404:
            self.logger.debug(
                f"HttpSignalingChannel.delete_session non-2xx for {code}: "
                f"{response.status_code}"
            )

    async def close(self) -> None:
        # Mark closed so any in-flight ``subscribe()`` reconnect-with-backoff
        # loop exits at the next iteration rather than reconnecting against
        # a torn-down client.
        self._closed = True
        # Only the client bound to the *current* loop can be aclosed from
        # here — clients bound to already-closed loops have torn-down pools
        # and would raise on ``aclose``. Pop them and let GC clean up.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            self._clients_by_loop.clear()
            return
        own = self._clients_by_loop.pop(id(loop), None)
        self._clients_by_loop.clear()
        if own is not None:
            try:
                await own.aclose()
            except Exception:  # pragma: no cover - defensive
                pass

    # ------------------------------------------------------------------
    # introspection
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        """Worker URL this channel was constructed against."""
        return self._base_url

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _http_to_ws(url: str) -> str:
        """Convert ``https://...`` → ``wss://...``, ``http://...`` → ``ws://...``."""
        if url.startswith("https://"):
            return "wss://" + url[len("https://"):]
        if url.startswith("http://"):
            return "ws://" + url[len("http://"):]
        return url

    @staticmethod
    def _extract_offer_from_envelope(code: str, payload: dict) -> str:
        """Map the Worker's JSON envelope into either an SDP string or an exception.

        Per plan §18 (W4), ``GET /offer`` returns ``{type:"offer", sdp,
        offer_sdp}`` — both fields populated, ``offer_sdp`` is the legacy
        name preserved for backward compat. We read ``sdp`` first (new
        code) and fall back to ``offer_sdp`` so the desktop keeps working
        against any Worker build that omits the new field.
        """
        if not isinstance(payload, dict):
            raise CodeNotFound(f"signaling returned non-object payload for code {code!r}")

        envelope_type = payload.get("type")
        if envelope_type == "cap_reached":
            current = int(payload.get("current", 0))
            limit = int(payload.get("limit", 0))
            raise ViewerCapReached(current=current, limit=limit)
        if envelope_type in (None, "offer"):
            sdp = _extract_sdp(payload)
            if sdp:
                return sdp
            raise CodeNotFound(f"signaling envelope for {code!r} carried no SDP")
        if envelope_type == "not_found":
            raise CodeNotFound(f"no session for code {code!r}")
        if envelope_type == "already_answered":
            raise CodeAlreadyAnswered(
                f"code {code!r} has already been answered"
            )
        # Unknown envelope type — fail closed; signaling protocol mismatch.
        raise CodeNotFound(
            f"signaling returned unknown envelope type {envelope_type!r} for {code!r}"
        )
