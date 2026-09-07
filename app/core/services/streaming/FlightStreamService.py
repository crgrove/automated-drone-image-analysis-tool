"""ADIAT Flight live feed as a first-class streaming video source.

The Flight Viewer already consumes ADIAT Flight's WebRTC publish session
via :class:`~core.services.streaming.WebRTCStreamService.WebRTCStreamService`
(video track + ``detections.*`` DataChannels). Streaming *analysis* wants
only the video: ADIAT Desktop runs its own detection algorithm over the
frames, so anything the phone/tablet already inferred is redundant and
would double-report into the gallery.

This module therefore provides two pieces:

* :class:`FlightFeedStreamService` — a :class:`WebRTCStreamService`
  subclass that adds the producer-side FPS throttle and the
  ``perf_counter`` re-stamping that ADIAT's streaming pipeline expects
  from a live source.
* :class:`FlightStreamManager` — a façade whose public surface matches
  :class:`~core.services.streaming.RTMPStreamService.StreamManager`, so
  :class:`~core.controllers.streaming.components.StreamCoordinator.\
StreamCoordinator` and everything downstream of it (frame worker,
  renderer, recorder, gallery) treat an ADIAT Flight feed exactly like a
  file, HDMI capture, or RTMP stream.

**Detection data is deliberately ignored, telemetry is not.** ADIAT
Desktop runs its own detector over these frames, so consuming the
publisher's detections would double-report into the gallery and mix two
detector configurations in one session — the manager never constructs a
``DetectionFeedService``. Aircraft *telemetry* is a different matter:
nothing else can supply it, and the HUD and map need it, so the
``telemetry`` channel is consumed via
:class:`~core.services.streaming.TelemetryFeedService.TelemetryFeedService`
and re-emitted on :attr:`FlightStreamManager.telemetryReceived`. Every
other channel is logged once at debug level and dropped. See
:meth:`FlightStreamManager._on_data_channel_opened`.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np
from PySide6.QtCore import QObject, Signal

from core.services.LoggerService import LoggerService
from core.services.streaming.RTMPStreamService import (
    MAX_REASONABLE_FPS_LIMIT,
    StreamType,
)
from core.services.streaming.TelemetryFeedService import (
    TELEMETRY_LABEL,
    TelemetryFeedService,
)
from core.services.streaming.WebRTCStreamService import WebRTCStreamService
from core.services.streaming.signaling import (
    SignalingChannel,
    default_signaling_channel,
    pairing,
)

# How long to give the WebRTC thread to unwind on an explicit disconnect
# before we stop blocking the UI thread. aiortc's SCTP/DTLS teardown is
# normally well under a second; the Flight Viewer uses the same budget.
DISCONNECT_WAIT_MS = 3000

# Prefix on ``connectionChanged`` messages that report a failure rather than
# progress. The pairing UI keys off this to tell "still connecting" from
# "this attempt failed"; it is deliberately not translated so both sides
# agree on the marker.
ERROR_STATUS_PREFIX = "Error: "


class FlightFeedStreamService(WebRTCStreamService):
    """WebRTC receive service tuned for the streaming-analysis pipeline.

    Differences from the Flight Viewer's plain
    :class:`WebRTCStreamService`:

    * **Frames are re-stamped with** ``time.perf_counter()``. The base
      class forwards the track's presentation timestamp, but
      :class:`~core.controllers.streaming.components.StreamStatistics.\
StreamStatistics` computes latency as ``perf_counter() - timestamp`` and
      :class:`~core.controllers.streaming.StreamViewerWindow.\
StreamViewerWindow` keys its original-frame cache by that value. An RTP
      presentation time would render latency meaningless and the cache
      keys unstable.
    * **An optional FPS cap is applied at the producer.** Matches how
      RTMP/HDMI honour the algorithm's ``target_fps`` so a 60 fps feed
      does not queue frames the worker will only discard.
    """

    def __init__(self, *args, fps_limit: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._fps_limit = self._normalize_fps_limit(fps_limit)
        self._last_emit_time = 0.0
        self._dropped_frames = 0

    @staticmethod
    def _normalize_fps_limit(fps_limit: Optional[int]) -> Optional[int]:
        """Clamp to the supported range; ``None`` means follow the source."""
        if fps_limit is None:
            return None
        try:
            value = int(fps_limit)
        except (TypeError, ValueError):
            return None
        if value <= 0:
            return None
        return max(1, min(value, MAX_REASONABLE_FPS_LIMIT))

    def set_fps_limit(self, fps_limit: Optional[int]) -> Optional[int]:
        """Update the cap while connected. Returns the normalized value."""
        self._fps_limit = self._normalize_fps_limit(fps_limit)
        return self._fps_limit

    @property
    def dropped_frames(self) -> int:
        """Frames decoded but skipped to honour the FPS cap."""
        return self._dropped_frames

    def _emit_frame_ready(
        self,
        frame: np.ndarray,
        timestamp: float,
        frame_number: int,
    ) -> None:
        """Throttle to the FPS cap, then emit with a perf_counter stamp.

        The cadence cap composes with — it does not replace — the base
        class's backpressure gate, which is why this delegates upward
        instead of emitting directly. A cap bounds how fast frames arrive;
        only the gate bounds how many can be outstanding, and a consumer
        slower than the cap still grows the queue without one.
        """
        now = time.perf_counter()
        limit = self._fps_limit
        if limit is not None and limit > 0:
            interval = 1.0 / limit
            if self._last_emit_time and (now - self._last_emit_time) < interval:
                self._dropped_frames += 1
                return
        self._last_emit_time = now
        super()._emit_frame_ready(frame, now, frame_number)

    def reset(self) -> None:
        """Lifecycle hook (CLAUDE.md §2.2.1) — also clear throttle state."""
        super().reset()
        self._last_emit_time = 0.0
        self._dropped_frames = 0


class FlightStreamManager(QObject):
    """``StreamManager``-shaped façade over an ADIAT Flight WebRTC feed.

    Exposes the same signals and methods as
    :class:`~core.services.streaming.RTMPStreamService.StreamManager` so
    :class:`StreamCoordinator` can swap one for the other based on the
    selected source type. Seek/pause members exist but are inert: a live
    feed has no timeline, exactly like HDMI and RTMP.

    The ``url`` argument to :meth:`connect_to_stream` is the six-character
    pairing code shown by ADIAT Flight, normalized through
    :func:`core.services.streaming.signaling.pairing.normalize_pairing_code`.
    """

    frameReceived = Signal(np.ndarray, float, int)  # frame, timestamp, frame_number
    connectionChanged = Signal(bool, str)           # connected, message
    statsUpdated = Signal(dict)                     # stream statistics
    videoPositionChanged = Signal(float, float)     # current_time, total_time
    seekCompleted = Signal(int, int, bool)          # request_id, position, success
    telemetryReceived = Signal(dict)                # parsed aircraft telemetry

    def __init__(
        self,
        signaling: Optional[SignalingChannel] = None,
        service_factory=None,
    ):
        """
        Args:
            signaling: Signaling backend. Defaults to the operator-configured
                Worker (shared with the Flight Viewer).
            service_factory: Callable ``(signaling, code, fps_limit)`` returning
                the receive service. Injection point for tests; production
                builds a :class:`FlightFeedStreamService`.
        """
        super().__init__()
        self.logger = LoggerService()
        self._signaling = signaling
        self._service_factory = service_factory or self._build_service
        self._service: Optional[FlightFeedStreamService] = None
        self._pairing_code: Optional[str] = None
        self._connected = False
        self._fps_limit: Optional[int] = None
        self._frame_number = 0
        self._resolution = (0, 0)
        self._observed_fps = 0.0
        self._ignored_channels: set = set()
        # Demuxes the ``telemetry`` DataChannel. Constructed per session so
        # a reconnect cannot surface the previous flight's last envelope.
        self._telemetry_feed: Optional[TelemetryFeedService] = None

    # ------------------------------------------------------------------
    # construction helpers
    # ------------------------------------------------------------------

    def _build_service(
        self,
        signaling: SignalingChannel,
        code: str,
        fps_limit: Optional[int],
    ) -> FlightFeedStreamService:
        return FlightFeedStreamService(
            signaling=signaling,
            pairing_code=code,
            fps_limit=fps_limit,
        )

    # ------------------------------------------------------------------
    # StreamManager-compatible API
    # ------------------------------------------------------------------

    def connect_to_stream(
        self,
        url: str,
        stream_type: StreamType = StreamType.WEBRTC,
        hdmi_backend: Optional[int] = None,
        fps_limit: Optional[int] = None,
    ) -> bool:
        """Pair with ADIAT Flight and start receiving video.

        Args:
            url: The six-character pairing code from ADIAT Flight.
            stream_type: Accepted for signature parity; ignored.
            hdmi_backend: Accepted for signature parity; ignored.
            fps_limit: Optional processing cadence cap.

        Returns:
            True when the receive session was started. A malformed pairing
            code returns False and emits ``connectionChanged(False, ...)``
            so the viewer surfaces the reason instead of silently idling.
        """
        self.disconnect_stream(emit_status=False)

        try:
            code = pairing.normalize_pairing_code(url)
        except ValueError as exc:
            message = str(exc)
            self.logger.error(f"ADIAT Flight: invalid pairing code {url!r}: {message}")
            self.connectionChanged.emit(False, f"{ERROR_STATUS_PREFIX}{message}")
            return False

        if self._signaling is None:
            try:
                self._signaling = default_signaling_channel()
            except Exception as exc:  # noqa: BLE001 - surfaced to the operator
                self.logger.error(f"ADIAT Flight: signaling setup failed: {exc}")
                self.connectionChanged.emit(False, f"{ERROR_STATUS_PREFIX}{exc}")
                return False

        self._pairing_code = code
        self._fps_limit = fps_limit
        self._frame_number = 0
        self._resolution = (0, 0)
        self._observed_fps = 0.0
        self._ignored_channels = set()

        try:
            self._service = self._service_factory(self._signaling, code, fps_limit)
        except Exception as exc:  # noqa: BLE001 - surfaced to the operator
            self.logger.error(f"ADIAT Flight: failed to create receive service: {exc}")
            self.connectionChanged.emit(False, f"{ERROR_STATUS_PREFIX}{exc}")
            self._service = None
            return False

        service = self._service
        service.frameReady.connect(self._on_frame_ready)
        service.connectionStatusChanged.connect(self._on_connection_status_changed)
        service.streamStatsChanged.connect(self._on_service_stats)
        service.errorOccurred.connect(self._on_error)
        service.dataChannelOpened.connect(self._on_data_channel_opened)

        # Telemetry IS consumed — nothing else can tell the desktop where
        # the aircraft is, and the HUD and map both need it. The feed
        # service filters by label, so detection traffic on the same
        # ``dataChannelMessage`` signal is dropped inside it.
        #
        # Detections remain deliberately unwired: no DetectionFeedService is
        # constructed here, because ADIAT Desktop runs its own algorithm
        # over these frames and consuming the publisher's detections would
        # double-report into the gallery.
        telemetry_feed = TelemetryFeedService(parent=self)
        telemetry_feed.telemetryReceived.connect(self._on_telemetry)
        service.dataChannelMessage.connect(telemetry_feed.handle_message)
        self._telemetry_feed = telemetry_feed

        try:
            service.request_connect()
        except Exception as exc:  # noqa: BLE001 - surfaced to the operator
            self.logger.error(f"ADIAT Flight: failed to start receive service: {exc}")
            self.connectionChanged.emit(False, f"{ERROR_STATUS_PREFIX}{exc}")
            self.disconnect_stream(emit_status=False)
            return False

        self.connectionChanged.emit(False, "Pairing with ADIAT Flight...")
        return True

    def disconnect_stream(self, emit_status: bool = True):
        """Tear down the receive session and release the pairing slot.

        Args:
            emit_status: When False, suppresses the terminal
                ``connectionChanged(False, "Disconnected")``. Used when a
                replacement source is about to connect, so the viewer does
                not see a spurious disconnect between the two.
        """
        service = self._service
        self._service = None
        self._connected = False
        telemetry_feed = self._telemetry_feed
        self._telemetry_feed = None

        if service is not None:
            disconnects = [
                (service.frameReady, self._on_frame_ready),
                (service.connectionStatusChanged, self._on_connection_status_changed),
                (service.streamStatsChanged, self._on_service_stats),
                (service.errorOccurred, self._on_error),
                (service.dataChannelOpened, self._on_data_channel_opened),
            ]
            if telemetry_feed is not None:
                disconnects.append(
                    (service.dataChannelMessage, telemetry_feed.handle_message)
                )
            for signal, slot in disconnects:
                try:
                    signal.disconnect(slot)
                except (TypeError, RuntimeError):
                    pass

        if telemetry_feed is not None:
            try:
                telemetry_feed.deleteLater()
            except (AttributeError, RuntimeError):
                pass

            stopped = True
            try:
                # ``cleanup`` — NOT ``request_disconnect``. The latter calls
                # ``delete_session`` on the Worker, which is terminal: the
                # pairing code dies and the operator has to generate a fresh
                # one on the tablet before reconnecting. Disconnect here is
                # routinely used to change algorithm settings and reconnect,
                # so the slot must be left in ``awaiting_viewer`` (plan §20)
                # exactly as the Flight Viewer's tile-close path does.
                service.cleanup()
                if hasattr(service, "isRunning") and service.isRunning():
                    stopped = bool(service.wait(DISCONNECT_WAIT_MS))
                    if not stopped:
                        self.logger.warning(
                            "ADIAT Flight receive service did not stop within "
                            f"{DISCONNECT_WAIT_MS}ms; deferring deletion until "
                            "its thread exits"
                        )
            except Exception as exc:  # noqa: BLE001 - teardown is best effort
                self.logger.warning(f"ADIAT Flight: error during disconnect: {exc}")

            # Deleting a QThread that is still running trips Qt's
            # "destroyed while thread is still running" abort, so defer to
            # ``finished`` when the wait timed out (mirrors StreamManager).
            try:
                if stopped:
                    service.deleteLater()
                else:
                    service.finished.connect(service.deleteLater)
            except (AttributeError, RuntimeError):
                pass

        self._pairing_code = None
        if emit_status:
            self.connectionChanged.emit(False, "Disconnected")

    def set_fps_limit(self, fps_limit: Optional[int]) -> bool:
        """Update the processing cadence cap while connected."""
        if not self._service:
            return False
        try:
            self._fps_limit = self._service.set_fps_limit(fps_limit)
            return True
        except Exception as exc:  # noqa: BLE001 - never fatal
            self.logger.error(f"ADIAT Flight: failed to update FPS limit: {exc}")
            return False

    def is_connected(self) -> bool:
        """True once ICE has paired and frames can flow."""
        return bool(self._service is not None and self._connected)

    def get_stream_info(self) -> Dict[str, Any]:
        """Current source information in ``StreamManager`` shape."""
        if not self._service:
            return {}
        return {
            'url': self._pairing_code or "",
            'type': StreamType.WEBRTC.value,
            'fps': self._observed_fps,
            'source_fps': self._observed_fps,
            'resolution': self._resolution,
            'frame_count': self._frame_number,
            'connected': self._connected,
            'is_playing': True,
        }

    @property
    def last_seek_id(self) -> int:
        """Always 0 — a live feed issues no seeks."""
        return 0

    # -- inert timeline members (live source, no seeking) ---------------

    def play_pause(self) -> bool:
        """No-op: a live feed cannot be paused."""
        return False

    def seek_to_time(self, time_seconds: float) -> bool:
        """No-op: a live feed has no timeline."""
        return False

    def seek_to_frame(self, frame_index: int) -> Optional[int]:
        """No-op: a live feed has no timeline."""
        return None

    def seek_relative(self, seconds_delta: float) -> bool:
        """No-op: a live feed has no timeline."""
        return False

    def seek_to_beginning(self) -> bool:
        """No-op: a live feed has no timeline."""
        return False

    def seek_to_end(self) -> bool:
        """No-op: a live feed has no timeline."""
        return False

    def is_file_playback(self) -> bool:
        """False — ADIAT Flight is always a live source."""
        return False

    def is_playing(self) -> bool:
        """True — a live feed is never in a paused state."""
        return True

    def get_playback_info(self) -> dict:
        """Empty — matches ``StreamManager`` for non-file sources."""
        return {}

    # ------------------------------------------------------------------
    # service signal handlers
    # ------------------------------------------------------------------

    def _on_frame_ready(self, frame: np.ndarray, timestamp: float, frame_number: int):
        """Forward a decoded frame and track resolution for stats."""
        if frame is None or getattr(frame, "size", 0) == 0:
            return
        self._frame_number = frame_number
        try:
            height, width = frame.shape[:2]
            if width > 0 and height > 0:
                self._resolution = (int(width), int(height))
        except (AttributeError, ValueError):
            pass
        self.frameReceived.emit(frame, timestamp, frame_number)

    def _on_connection_status_changed(self, connected: bool, message: str):
        """Translate WebRTC connection status into StreamManager semantics."""
        self._connected = bool(connected)
        self.connectionChanged.emit(bool(connected), message or "")

    def _on_service_stats(self, stats: dict):
        """Reshape :class:`WebRTCStats` into the RTMP stats dictionary.

        Downstream consumers read ``resolution`` as a ``(width, height)``
        tuple and ``fps``/``source_fps`` as floats; the WebRTC service
        reports ``width``/``height`` as separate keys.
        """
        if not isinstance(stats, dict):
            return

        width = stats.get('width') or 0
        height = stats.get('height') or 0
        if width and height:
            self._resolution = (int(width), int(height))

        fps = stats.get('fps')
        if isinstance(fps, (int, float)) and fps > 0:
            self._observed_fps = float(fps)

        dropped = 0
        if self._service is not None:
            dropped = getattr(self._service, 'dropped_frames', 0)

        self.statsUpdated.emit({
            'fps': self._observed_fps,
            'source_fps': self._observed_fps,
            'resolution': self._resolution,
            'frame_number': self._frame_number,
            'timestamp': time.time(),
            'is_playing': True,
            'capture_dropped_frames': dropped,
            'bitrate_kbps': stats.get('bitrate_kbps', 0.0),
            'ice_state': stats.get('ice_state', ''),
        })

    def _on_error(self, error_message: str):
        """Surface receive-service errors as a connection failure."""
        self.logger.error(f"ADIAT Flight stream error: {error_message}")
        self.connectionChanged.emit(False, f"{ERROR_STATUS_PREFIX}{error_message}")

    def _on_telemetry(self, envelope: dict):
        """Forward a parsed aircraft telemetry envelope."""
        if isinstance(envelope, dict):
            self.telemetryReceived.emit(envelope)

    @property
    def last_telemetry(self) -> Optional[dict]:
        """Most recent telemetry envelope, or None if none has arrived."""
        if self._telemetry_feed is None:
            return None
        return self._telemetry_feed.last_envelope

    def _on_data_channel_opened(self, label: str):
        """Log which publisher DataChannels are consumed vs dropped.

        ADIAT Flight opens ``detections.meta`` / ``detections.thumb`` /
        ``telemetry`` alongside the video track. Only ``telemetry`` is
        consumed — the desktop's own algorithm is the authority on
        detections for this session, so the publisher's are discarded
        rather than merged. Logged once per label to keep the debug log
        readable.
        """
        if label in self._ignored_channels:
            return
        self._ignored_channels.add(label)
        if label == TELEMETRY_LABEL:
            self.logger.debug(
                f"ADIAT Flight: consuming publisher DataChannel {label!r}"
            )
            return
        self.logger.debug(
            f"ADIAT Flight: ignoring publisher DataChannel {label!r} "
            "(streaming analysis consumes video and telemetry only)"
        )
