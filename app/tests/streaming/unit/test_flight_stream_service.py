"""Unit tests for the ADIAT Flight streaming source.

Covers :class:`FlightFeedStreamService` (producer-side throttle and
timestamp re-stamping) and :class:`FlightStreamManager` (the
``StreamManager``-shaped facade), including the requirement that
detection data published by ADIAT Flight is ignored — ADIAT Desktop runs
its own algorithm over the video.

aiortc is never exercised here: the manager takes a ``service_factory``
injection point and the throttle tests drive ``_emit_frame_ready``
directly, so these tests run in environments without WebRTC deps.
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.FlightStreamService import (  # noqa: E402
    FlightFeedStreamService,
    FlightStreamManager,
)
from core.services.streaming.RTMPStreamService import (  # noqa: E402
    MAX_REASONABLE_FPS_LIMIT,
    StreamType,
)
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


class FakeReceiveService(QObject):
    """Stands in for :class:`FlightFeedStreamService` in manager tests.

    Mirrors the signal surface the manager subscribes to plus the two
    lifecycle calls it makes, so the manager can be exercised without a
    QThread or aiortc.
    """

    frameReady = Signal(np.ndarray, float, int)
    connectionStatusChanged = Signal(bool, str)
    streamStatsChanged = Signal(dict)
    errorOccurred = Signal(str)
    dataChannelOpened = Signal(str)
    dataChannelMessage = Signal(str, bytes)
    finished = Signal()

    def __init__(self, signaling=None, pairing_code=None, fps_limit=None):
        super().__init__()
        self.signaling = signaling
        self.pairing_code = pairing_code
        self.fps_limit = fps_limit
        self.connect_calls = 0
        self.disconnect_calls = 0
        self.terminal_disconnect_calls = 0
        self.dropped_frames = 0

    def request_connect(self):
        self.connect_calls += 1

    def request_disconnect(self):
        # Terminal on the Worker — the manager must NOT use this.
        self.terminal_disconnect_calls += 1

    def cleanup(self, wait=False):
        self.disconnect_calls += 1

    def isRunning(self):
        return False

    def wait(self, ms):
        return True

    def set_fps_limit(self, fps_limit):
        self.fps_limit = fps_limit
        return fps_limit


@pytest.fixture
def manager():
    """A manager wired to a fake receive service (no network, no thread)."""
    created = {}

    def factory(signaling, code, fps_limit):
        service = FakeReceiveService(signaling, code, fps_limit)
        created["service"] = service
        return service

    mgr = FlightStreamManager(
        signaling=InMemorySignalingChannel(),
        service_factory=factory,
    )
    mgr._created = created
    yield mgr
    mgr.disconnect_stream(emit_status=False)


def _frame(width: int = 64, height: int = 32) -> np.ndarray:
    return np.zeros((height, width, 3), dtype=np.uint8)


# ----------------------------------------------------------------------
# FlightFeedStreamService — throttle + timestamps
# ----------------------------------------------------------------------


def test_feed_service_restamps_timestamp_with_perf_counter(qapp):
    """StreamStatistics computes latency as ``perf_counter() - timestamp``.

    The base service forwards the track's RTP presentation time, which
    would make latency meaningless; the streaming source must re-stamp.
    """
    svc = FlightFeedStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append((f, ts, n)))

    before = time.perf_counter()
    # 12.5 is a plausible RTP presentation time; it must NOT be forwarded.
    svc._emit_frame_ready(_frame(), 12.5, 1)
    after = time.perf_counter()

    assert len(received) == 1
    _, timestamp, frame_number = received[0]
    assert frame_number == 1
    assert timestamp != 12.5
    assert before <= timestamp <= after


def test_feed_service_without_limit_emits_every_frame(qapp):
    svc = FlightFeedStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
        fps_limit=None,
    )
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    for i in range(5):
        svc._emit_frame_ready(_frame(), float(i), i + 1)

    assert received == [1, 2, 3, 4, 5]
    assert svc.dropped_frames == 0


def test_feed_service_throttles_to_fps_limit(qapp):
    """Back-to-back frames beyond the cap are dropped at the producer."""
    svc = FlightFeedStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
        fps_limit=1,  # 1 fps -> a 1s interval no test loop can cross
    )
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    for i in range(10):
        svc._emit_frame_ready(_frame(), float(i), i + 1)

    # First frame passes (no previous emit); the rest fall inside the interval.
    assert received == [1]
    assert svc.dropped_frames == 9


def test_feed_service_fps_limit_normalization(qapp):
    svc = FlightFeedStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    assert svc.set_fps_limit(None) is None
    assert svc.set_fps_limit(0) is None
    assert svc.set_fps_limit(-5) is None
    assert svc.set_fps_limit("bogus") is None
    assert svc.set_fps_limit(15) == 15
    assert svc.set_fps_limit(9999) == MAX_REASONABLE_FPS_LIMIT


def test_feed_service_reset_clears_throttle_state(qapp):
    svc = FlightFeedStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
        fps_limit=1,
    )
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    svc._emit_frame_ready(_frame(), 0.0, 1)
    svc._emit_frame_ready(_frame(), 0.0, 2)  # dropped
    assert svc.dropped_frames == 1

    svc.reset()
    assert svc.dropped_frames == 0
    svc._emit_frame_ready(_frame(), 0.0, 3)  # passes again after reset
    assert received == [1, 3]


# ----------------------------------------------------------------------
# FlightStreamManager — connection lifecycle
# ----------------------------------------------------------------------


def test_connect_normalizes_pairing_code_and_starts_service(manager):
    statuses = []
    manager.connectionChanged.connect(lambda ok, msg: statuses.append((ok, msg)))

    assert manager.connect_to_stream("k7q-m3p", StreamType.WEBRTC) is True

    service = manager._created["service"]
    assert service.pairing_code == "K7QM3P"
    assert service.connect_calls == 1
    assert statuses and statuses[0][0] is False  # interim "pairing" status


def test_disconnect_retires_a_receive_thread_that_will_not_stop(manager, monkeypatch):
    """Dropping a still-running QThread makes Qt abort the process."""
    import core.services.streaming.FlightStreamService as fss

    retired = []
    monkeypatch.setattr(fss, "retire_running_thread", lambda thread: retired.append(thread))
    assert manager.connect_to_stream("k7q-m3p", StreamType.WEBRTC) is True
    service = manager._created["service"]
    service.isRunning = lambda: True
    service.wait = lambda ms: False

    manager.disconnect_stream(emit_status=False)

    assert retired == [service]


def test_connect_rejects_malformed_pairing_code(manager):
    statuses = []
    manager.connectionChanged.connect(lambda ok, msg: statuses.append((ok, msg)))

    assert manager.connect_to_stream("nope", StreamType.WEBRTC) is False
    assert "service" not in manager._created
    assert statuses
    connected, message = statuses[-1]
    assert connected is False
    assert message.startswith("Error:")


def test_connect_rejects_code_with_confusable_characters(manager):
    """``I``/``L``/``O``/``0``/``1`` are outside the pairing alphabet."""
    assert manager.connect_to_stream("ABCIL0", StreamType.WEBRTC) is False
    assert "service" not in manager._created


def test_connect_passes_fps_limit_to_service(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC, fps_limit=10)
    assert manager._created["service"].fps_limit == 10


def test_connect_replaces_existing_session(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    first = manager._created["service"]

    manager.connect_to_stream("XYZ789", StreamType.WEBRTC)
    second = manager._created["service"]

    assert second is not first
    assert first.disconnect_calls == 1
    assert second.pairing_code == "XYZ789"


def test_disconnect_tears_down_and_reports(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    statuses = []
    manager.connectionChanged.connect(lambda ok, msg: statuses.append((ok, msg)))
    manager.disconnect_stream()

    assert service.disconnect_calls == 1
    assert statuses[-1] == (False, "Disconnected")
    assert manager.is_connected() is False
    assert manager.get_stream_info() == {}


def test_disconnect_keeps_the_pairing_code_reusable(manager):
    """Disconnect must not end the publish session on the Worker.

    ``request_disconnect`` calls ``delete_session``, which kills the code
    and forces the operator to mint a new one on the tablet. Disconnect is
    routinely used to change settings and reconnect, so the slot has to be
    left in ``awaiting_viewer`` (plan §20) — the same choice the Flight
    Viewer's tile-close path makes.
    """
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    manager.disconnect_stream()

    assert service.disconnect_calls == 1            # cleanup()
    assert service.terminal_disconnect_calls == 0   # request_disconnect()


def test_disconnect_stops_forwarding_frames(manager):
    """A frame emitted by a torn-down service must not reach the viewer."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    frames = []
    manager.frameReceived.connect(lambda f, ts, n: frames.append(n))
    manager.disconnect_stream()

    service.frameReady.emit(_frame(), 1.0, 7)
    assert frames == []


def test_disconnect_can_suppress_status(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    statuses = []
    manager.connectionChanged.connect(lambda ok, msg: statuses.append((ok, msg)))

    manager.disconnect_stream(emit_status=False)
    assert statuses == []


def test_disconnect_without_session_is_safe(manager):
    manager.disconnect_stream()
    manager.disconnect_stream()
    assert manager.is_connected() is False


# ----------------------------------------------------------------------
# FlightStreamManager — frame / stats / status translation
# ----------------------------------------------------------------------


def test_frames_are_forwarded_with_resolution_tracking(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    frames = []
    manager.frameReceived.connect(lambda f, ts, n: frames.append((f.shape, ts, n)))
    service.frameReady.emit(_frame(width=1920, height=1080), 3.5, 42)

    assert frames == [((1080, 1920, 3), 3.5, 42)]
    assert manager.get_stream_info()["resolution"] == (1920, 1080)
    assert manager.get_stream_info()["frame_count"] == 42


def test_empty_frames_are_dropped(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    frames = []
    manager.frameReceived.connect(lambda f, ts, n: frames.append(n))
    service.frameReady.emit(np.zeros((0, 0, 3), dtype=np.uint8), 1.0, 1)

    assert frames == []


def test_stats_are_reshaped_into_stream_manager_form(manager):
    """WebRTCStats reports width/height separately; consumers want a tuple."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    captured = []
    manager.statsUpdated.connect(captured.append)
    service.streamStatsChanged.emit({
        "fps": 24.0,
        "width": 1280,
        "height": 720,
        "bitrate_kbps": 3200.0,
        "ice_state": "connected",
    })

    assert len(captured) == 1
    stats = captured[0]
    assert stats["resolution"] == (1280, 720)
    assert stats["fps"] == 24.0
    assert stats["source_fps"] == 24.0
    assert stats["is_playing"] is True
    assert stats["ice_state"] == "connected"


def test_partial_stats_payload_does_not_crash(manager):
    """A stats dict missing width/height still yields a well-formed payload."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    captured = []
    manager.statsUpdated.connect(captured.append)
    service.streamStatsChanged.emit({})

    assert captured and captured[0]["resolution"] == (0, 0)
    assert captured[0]["fps"] == 0.0


def test_non_dict_stats_are_ignored(manager):
    """Defensive: a malformed payload must not reach downstream consumers."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)

    captured = []
    manager.statsUpdated.connect(captured.append)
    manager._on_service_stats("not a dict")

    assert captured == []


def test_last_known_resolution_survives_a_stats_gap(manager):
    """Recording sizing must not fall back to 0x0 mid-session."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    captured = []
    manager.statsUpdated.connect(captured.append)
    service.streamStatsChanged.emit({"fps": 30.0, "width": 1280, "height": 720})
    service.streamStatsChanged.emit({"fps": 0.0})  # width/height absent

    assert captured[-1]["resolution"] == (1280, 720)
    assert captured[-1]["fps"] == 30.0


def test_connection_status_is_forwarded(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    statuses = []
    manager.connectionChanged.connect(lambda ok, msg: statuses.append((ok, msg)))
    service.connectionStatusChanged.emit(True, "connected")

    assert statuses[-1] == (True, "connected")
    assert manager.is_connected() is True

    service.connectionStatusChanged.emit(False, "closed")
    assert manager.is_connected() is False


def test_service_errors_surface_as_connection_failure(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    statuses = []
    manager.connectionChanged.connect(lambda ok, msg: statuses.append((ok, msg)))
    service.errorOccurred.emit("aiortc is required for the Flight Viewer.")

    assert statuses[-1][0] is False
    assert "aiortc is required" in statuses[-1][1]


def test_get_stream_info_reports_webrtc_type(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    manager._created["service"].connectionStatusChanged.emit(True, "connected")

    info = manager.get_stream_info()
    assert info["type"] == StreamType.WEBRTC.value
    assert info["url"] == "ABC234"
    assert info["connected"] is True
    assert info["is_playing"] is True


def test_set_fps_limit_requires_active_session(manager):
    assert manager.set_fps_limit(15) is False
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    assert manager.set_fps_limit(15) is True
    assert manager._created["service"].fps_limit == 15


# ----------------------------------------------------------------------
# Requirement: detection data from ADIAT Flight is ignored
# ----------------------------------------------------------------------


def test_detection_data_channel_messages_are_not_consumed(manager):
    """ADIAT Desktop runs its own algorithm; publisher detections are dropped.

    Telemetry on the same ``dataChannelMessage`` signal IS consumed (the
    desktop has no other source for aircraft position), so the invariant
    is per-label rather than "nothing is subscribed": detection traffic
    must produce no frames, stats, status changes, or telemetry.
    """
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    frames, stats, statuses, telemetry = [], [], [], []
    manager.frameReceived.connect(lambda f, ts, n: frames.append(n))
    manager.statsUpdated.connect(stats.append)
    manager.connectionChanged.connect(lambda ok, msg: statuses.append(msg))
    manager.telemetryReceived.connect(telemetry.append)

    service.dataChannelMessage.emit(
        "detections.meta",
        b'{"event": "promote", "track_key": "t1"}',
    )
    service.dataChannelMessage.emit("detections.thumb", b"\xff\xd8\xff")
    service.dataChannelMessage.emit("detections.snapshot", b'[{"track_key": "t2"}]')

    assert frames == []
    assert stats == []
    assert statuses == []
    assert telemetry == []


def test_telemetry_channel_is_consumed(manager):
    """Aircraft telemetry reaches the desktop — nothing else can supply it."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    received = []
    manager.telemetryReceived.connect(received.append)
    service.dataChannelMessage.emit(
        "telemetry",
        b'{"aircraft_latitude": 30.5, "aircraft_longitude": -97.7, '
        b'"aircraft_altitude_msl_m": 210.0, "captured_at_ms": 1234}',
    )

    assert len(received) == 1
    assert received[0]["aircraft_latitude"] == 30.5
    assert received[0]["aircraft_longitude"] == -97.7
    assert manager.last_telemetry == received[0]


def test_telemetry_feed_is_rebuilt_per_session(manager):
    """A reconnect must not surface the previous flight's last envelope."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    manager._created["service"].dataChannelMessage.emit(
        "telemetry", b'{"aircraft_latitude": 1.0}'
    )
    assert manager.last_telemetry is not None

    manager.connect_to_stream("XYZ789", StreamType.WEBRTC)
    assert manager.last_telemetry is None


def test_malformed_telemetry_does_not_emit(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    received = []
    manager.telemetryReceived.connect(received.append)
    service.dataChannelMessage.emit("telemetry", b"not json at all")
    service.dataChannelMessage.emit("telemetry", b'"a bare string"')

    assert received == []


def test_opened_detection_channels_are_recorded_as_ignored(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    service = manager._created["service"]

    service.dataChannelOpened.emit("detections.meta")
    service.dataChannelOpened.emit("detections.meta")  # logged once only
    service.dataChannelOpened.emit("telemetry")

    assert manager._ignored_channels == {"detections.meta", "telemetry"}


def test_manager_never_builds_a_detection_feed_service(manager):
    """Guard against a future wiring regression re-introducing detections."""
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)
    for attr in vars(manager).values():
        assert type(attr).__name__ != "DetectionFeedService"


# ----------------------------------------------------------------------
# Inert timeline surface (live source parity with HDMI / RTMP)
# ----------------------------------------------------------------------


def test_timeline_members_are_inert(manager):
    manager.connect_to_stream("ABC234", StreamType.WEBRTC)

    assert manager.is_file_playback() is False
    assert manager.is_playing() is True
    assert manager.play_pause() is False
    assert manager.seek_to_time(5.0) is False
    assert manager.seek_to_frame(10) is None
    assert manager.seek_relative(-2.0) is False
    assert manager.seek_to_beginning() is False
    assert manager.seek_to_end() is False
    assert manager.get_playback_info() == {}
    assert manager.last_seek_id == 0
