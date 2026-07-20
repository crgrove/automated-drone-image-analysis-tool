"""Live aircraft telemetry feed for the Flight Viewer (plan §19.3).

Mirrors :class:`~core.services.streaming.DetectionFeedService.\
DetectionFeedService` in shape: consumes the unified
:attr:`WebRTCStreamService.dataChannelMessage` signal, filters by the
``telemetry`` label, and re-emits a parsed envelope on
:attr:`telemetryReceived`. Mobile-side wire format is defined in
``ADIAT_Mobile/core/flightpublish/TelemetryPublisher.kt → TelemetryEnvelope``.

Every field except ``captured_at_ms`` is nullable on the publisher side
— receivers must treat ``null`` and missing keys as "unknown" and not
interpolate.
"""

from __future__ import annotations

import json
from typing import Optional

from PySide6.QtCore import QObject, Signal

from core.services.LoggerService import LoggerService

TELEMETRY_LABEL = "telemetry"


class TelemetryFeedService(QObject):
    """Decodes ``telemetry`` DataChannel messages into typed signals.

    One instance per :class:`FlightTile`. Lives on the same QThread as
    the :class:`WebRTCStreamService` that feeds it.
    """

    telemetryReceived = Signal(dict)
    feedError = Signal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = LoggerService()
        self._last_envelope: Optional[dict] = None

    def handle_message(self, label: str, payload: bytes) -> None:
        """Route a single DataChannel message; no-op if not ours.

        The same ``dataChannelMessage`` signal feeds
        :class:`DetectionFeedService`, so each consumer filters by label
        and ignores the other's traffic.
        """
        if label != TELEMETRY_LABEL:
            return
        try:
            envelope = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.feedError.emit(f"malformed telemetry envelope: {exc}")
            return
        if not isinstance(envelope, dict):
            self.feedError.emit("telemetry envelope must be a JSON object")
            return
        self._last_envelope = envelope
        self.telemetryReceived.emit(envelope)

    @property
    def last_envelope(self) -> Optional[dict]:
        """Most recently parsed envelope, or ``None`` if nothing has arrived."""
        return self._last_envelope
