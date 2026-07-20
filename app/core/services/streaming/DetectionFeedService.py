"""DataChannel detection demux for the Flight Viewer.

Subscribes to a :class:`~core.services.streaming.WebRTCStreamService.\
WebRTCStreamService`'s ``dataChannelMessage(label, payload)`` signal and
turns the two channels described in plan §6 — ``detections.meta`` (JSON
envelopes) and ``detections.thumb`` (binary JPEG bytes) — into a stream
of fully-formed ``detectionPromoted`` / ``detectionUpdated`` events.

The matcher pairs meta envelopes with their thumbnail by ``sha256``. A
meta envelope whose thumb has not yet arrived is buffered with a short
timeout; conversely a thumb without a known meta is held until the meta
arrives or the timeout expires. Promotions without a ``thumb`` field
surface immediately with ``thumb_bytes=None`` (per plan §6 — placeholder
gallery rows).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal

from core.services.LoggerService import LoggerService

THUMB_TIMEOUT_SECONDS = 10.0

META_LABEL = "detections.meta"
THUMB_LABEL = "detections.thumb"
SNAPSHOT_LABEL = "detections.snapshot"


@dataclass
class _PendingMeta:
    """A meta envelope that is waiting for its companion thumb."""

    envelope: dict
    expected_sha256: Optional[str]
    expected_bytes: Optional[int]
    arrived_at: float = field(default_factory=time.monotonic)


@dataclass
class _PendingThumb:
    """A thumb payload that arrived before its meta envelope."""

    payload: bytes
    sha256: str
    arrived_at: float = field(default_factory=time.monotonic)


class DetectionFeedService(QObject):
    """Pair JSON envelopes with JPEG bytes and surface as parsed events.

    The class is a pure ``QObject`` (no QThread). It lives on the same
    QThread as the ``WebRTCStreamService`` that feeds it, so callers
    should connect the stream service's ``dataChannelMessage`` signal to
    :meth:`handle_message` directly.
    """

    detectionPromoted = Signal(dict)  # envelope merged with optional thumb_bytes
    detectionUpdated = Signal(dict)
    detectionSnapshot = Signal(list)  # bulk snapshot from M3 channel
    feedError = Signal(str)
    # Mobile → desktop control messages on the ``detections.meta``
    # channel after a resume handshake (plan §20):
    #   ``resumeComplete`` carries (session_id, last_seq) once backfill
    #     has finished — the desktop can drop any "Reconnecting…" UI.
    #   ``sessionChanged`` carries (new_session_id) when mobile has
    #     started a fresh publish session since the desktop's stored
    #     ``session_id`` — desktop discards local history (or archives
    #     it) and adopts the new session_id.
    resumeComplete = Signal(str, int)        # session_id, last_seq
    sessionChanged = Signal(str)             # new session_id

    def __init__(self, parent: Optional[QObject] = None, *, thumb_timeout: float = THUMB_TIMEOUT_SECONDS):
        super().__init__(parent)
        self.logger = LoggerService()
        self._pending_meta: Dict[str, _PendingMeta] = {}
        self._pending_thumb: Dict[str, _PendingThumb] = {}
        self._thumb_timeout = float(thumb_timeout)
        # Labels we've already logged as "unknown" once — keeps the debug
        # log readable when the publisher opens a per-session channel we
        # don't yet consume (e.g. ``telemetry``, sent at ~3 Hz).
        self._unknown_labels_seen: set = set()
        # ``(session_id, seq)`` of envelopes we've already emitted. The
        # resume backfill from mobile (plan §20) may overlap with what
        # the desktop already received pre-close; dedup keeps the
        # gallery row count honest. Bounded to the last few thousand
        # entries; older entries naturally rotate out as sessions end.
        self._seen_seq: set = set()

    # ------------------------------------------------------------------
    # entry point: WebRTCStreamService.dataChannelMessage -> here
    # ------------------------------------------------------------------

    def handle_message(self, label: str, payload: bytes) -> None:
        """Route a single DataChannel message to its handler."""
        if label == META_LABEL:
            self._handle_meta(payload)
        elif label == THUMB_LABEL:
            self._handle_thumb(payload)
        elif label == SNAPSHOT_LABEL:
            self._handle_snapshot(payload)
        else:
            # Unknown channel — not an error. Publishers may open per-session
            # auxiliary channels (e.g. ``telemetry``) at high frequency; log
            # once per label and stay quiet thereafter to keep the debug log
            # readable.
            if label not in self._unknown_labels_seen:
                self._unknown_labels_seen.add(label)
                self.logger.debug(
                    f"DetectionFeedService: ignoring messages on unknown channel "
                    f"{label!r} (subsequent messages silently dropped)"
                )

    # ------------------------------------------------------------------
    # meta
    # ------------------------------------------------------------------

    def _handle_meta(self, payload: bytes) -> None:
        try:
            envelope = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.feedError.emit(f"malformed detections.meta envelope: {exc}")
            return

        if not isinstance(envelope, dict):
            self.feedError.emit("detections.meta envelope must be a JSON object")
            return

        # Resume control messages on the ``detections.meta`` channel
        # (plan §20). A ``kind`` field distinguishes these from regular
        # MetaEnvelopes (which use ``event = promote|update``).
        kind = envelope.get("kind")
        if kind == "resume_complete":
            session_id = envelope.get("session_id")
            last_seq = envelope.get("last_seq")
            if isinstance(session_id, str) and isinstance(last_seq, (int, float)):
                self.resumeComplete.emit(session_id, int(last_seq))
            return
        if kind == "session_changed":
            new_session_id = envelope.get("new_session_id")
            if isinstance(new_session_id, str) and new_session_id:
                self.sessionChanged.emit(new_session_id)
            return

        # Dedup regular MetaEnvelopes by (session_id, seq). Backfill on
        # resume can replay events the desktop received pre-close — the
        # session_id+seq pair is the stable identity.
        session_id = envelope.get("session_id")
        seq = envelope.get("seq")
        if (
            isinstance(session_id, str)
            and session_id
            and isinstance(seq, (int, float))
        ):
            key = (session_id, int(seq))
            if key in self._seen_seq:
                return
            self._seen_seq.add(key)

        thumb = envelope.get("thumb")
        if not thumb:
            # No thumb attached — surface immediately with bytes=None.
            self._emit(envelope, thumb_bytes=None)
            return

        expected_sha = thumb.get("sha256") if isinstance(thumb, dict) else None
        expected_bytes = thumb.get("bytes") if isinstance(thumb, dict) else None
        if not expected_sha:
            # Thumb dict present but no sha — surface meta now; the thumb
            # path can never pair, so it would be a wasted buffer.
            self._emit(envelope, thumb_bytes=None)
            return

        # Pair if the thumb arrived first.
        pending = self._pending_thumb.pop(expected_sha, None)
        if pending is not None:
            self._emit(envelope, thumb_bytes=pending.payload)
            return

        self._gc_pending(now=time.monotonic())
        self._pending_meta[expected_sha] = _PendingMeta(
            envelope=envelope,
            expected_sha256=expected_sha,
            expected_bytes=expected_bytes,
        )

    # ------------------------------------------------------------------
    # thumb
    # ------------------------------------------------------------------

    def _handle_thumb(self, payload: bytes) -> None:
        if not payload:
            return
        sha = hashlib.sha256(payload).hexdigest()
        pending = self._pending_meta.pop(sha, None)
        if pending is not None:
            if pending.expected_bytes and pending.expected_bytes != len(payload):
                self.feedError.emit(
                    f"thumb byte count mismatch for sha {sha[:8]}: "
                    f"expected {pending.expected_bytes}, got {len(payload)}"
                )
                return
            self._emit(pending.envelope, thumb_bytes=payload)
            return

        # Thumb arrived before meta — buffer.
        self._gc_pending(now=time.monotonic())
        self._pending_thumb[sha] = _PendingThumb(payload=payload, sha256=sha)

    # ------------------------------------------------------------------
    # snapshot
    # ------------------------------------------------------------------

    def _handle_snapshot(self, payload: bytes) -> None:
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.feedError.emit(f"malformed detections.snapshot: {exc}")
            return
        if not isinstance(decoded, list):
            self.feedError.emit("detections.snapshot must be a JSON array")
            return
        self.detectionSnapshot.emit(decoded)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _emit(self, envelope: dict, thumb_bytes: Optional[bytes]) -> None:
        merged = dict(envelope)
        merged["thumb_bytes"] = thumb_bytes
        event = (envelope.get("event") or "promote").lower()
        if event == "update":
            self.detectionUpdated.emit(merged)
        else:
            self.detectionPromoted.emit(merged)

    def _gc_pending(self, *, now: float) -> None:
        cutoff = now - self._thumb_timeout
        stale_meta = [k for k, v in self._pending_meta.items() if v.arrived_at < cutoff]
        for k in stale_meta:
            envelope = self._pending_meta.pop(k).envelope
            # Surface the meta even without its thumb so the gallery still
            # gets a row; plan §6 allows placeholder rows.
            self._emit(envelope, thumb_bytes=None)
        stale_thumb = [k for k, v in self._pending_thumb.items() if v.arrived_at < cutoff]
        for k in stale_thumb:
            self._pending_thumb.pop(k, None)
