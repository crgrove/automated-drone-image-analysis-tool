"""Backpressure on the WebRTC frame path.

``frameReady`` crosses from the decode thread to GUI-thread slots, so
every emission posts a queued event holding a full-resolution BGR
ndarray onto an unbounded queue. The Flight Viewer connects two such
slots per tile. Emitting unconditionally lets that queue grow without
bound the moment the GUI thread falls behind — memory climbs, the UI
locks, and the process dies on an allocation failure with no Python
traceback.

These tests pin the gate that bounds it: at most one frame outstanding,
drop the rest, and never freeze the feed permanently if an
acknowledgement goes missing.

aiortc is never exercised — the tests drive ``_emit_frame_ready``
directly, as the sibling throttle tests do.
"""

from __future__ import annotations

import os
import sys
import threading
import time

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.FlightStreamService import (  # noqa: E402
    FlightFeedStreamService,
)
from core.services.streaming.WebRTCStreamService import (  # noqa: E402
    FRAME_ACK_TIMEOUT_SECONDS,
    WebRTCStreamService,
)
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _service():
    return WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )


def _frame(value=0):
    return np.full((4, 4, 3), value, dtype=np.uint8)


def test_consumer_keeping_up_receives_every_frame():
    """Same-thread delivery is direct, so the gate reopens before returning."""
    svc = _service()
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    for i in range(5):
        svc._emit_frame_ready(_frame(i), float(i), i)

    assert received == [0, 1, 2, 3, 4]
    assert svc.backpressure_drops == 0


def test_frame_dropped_while_previous_is_outstanding():
    """The whole point: one frame in flight, the rest are refused."""
    svc = _service()
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    # Stand in for the GUI thread not yet having drained the queued event.
    svc._frame_in_flight = True
    svc._frame_in_flight_since = time.monotonic()

    for i in range(10):
        svc._emit_frame_ready(_frame(i), float(i), i)

    assert received == []
    assert svc.backpressure_drops == 10


def test_gate_reopens_once_the_consumer_acknowledges():
    svc = _service()
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    svc._frame_in_flight = True
    svc._frame_in_flight_since = time.monotonic()
    svc._emit_frame_ready(_frame(1), 1.0, 1)
    assert received == []

    # The acknowledgement the GUI thread would deliver.
    svc._on_frame_delivered()
    svc._emit_frame_ready(_frame(2), 2.0, 2)
    assert received == [2]


def test_lost_acknowledgement_does_not_freeze_the_feed():
    """A missing ack must degrade the feed, never stop it forever."""
    svc = _service()
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    svc._frame_in_flight = True
    svc._frame_in_flight_since = time.monotonic() - (FRAME_ACK_TIMEOUT_SECONDS + 0.5)

    svc._emit_frame_ready(_frame(7), 7.0, 7)

    assert received == [7]
    assert svc.backpressure_drops == 0


def test_reset_reopens_the_gate():
    """A reconnect must not inherit a stuck in-flight flag."""
    svc = _service()
    svc._frame_in_flight = True
    svc._frame_in_flight_since = time.monotonic()
    svc._backpressure_drops = 12
    svc._backpressure_warned = True

    svc.reset()

    assert svc._frame_in_flight is False
    assert svc.backpressure_drops == 0
    assert svc._backpressure_warned is False

    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))
    svc._emit_frame_ready(_frame(1), 1.0, 1)
    assert received == [1]


def test_backlog_stays_bounded_when_the_consumer_is_slower_than_the_source(qtbot):
    """The failure this fixes, end to end.

    A decode thread pushing faster than the GUI thread can render must
    not accumulate. Without the gate, queue depth grows with the
    producer's output for as long as it runs; with it, depth never
    exceeds the single in-flight frame.
    """
    svc = _service()
    emitted = []
    rendered = []
    depths = []

    def slow_render(_f, _ts, n):
        # Everything emitted but not yet rendered is sitting in the
        # queue behind us — that is the backlog the gate has to bound.
        depths.append(len(emitted) - len(rendered))
        time.sleep(0.01)
        rendered.append(n)

    svc.frameReady.connect(slow_render)

    def _emit(i):
        before = svc.backpressure_drops
        svc._emit_frame_ready(_frame(i % 255), float(i), i)
        if svc.backpressure_drops == before:
            emitted.append(i)

    attempts = []
    done = threading.Event()

    def produce():
        deadline = time.monotonic() + 0.5
        i = 0
        while time.monotonic() < deadline:
            _emit(i)
            attempts.append(i)
            i += 1
            time.sleep(0.001)
        done.set()

    worker = threading.Thread(target=produce, name="test-decode", daemon=True)
    worker.start()
    qtbot.waitUntil(done.is_set, timeout=5000)
    worker.join(timeout=2)
    # Drain: the last emitted frame may still be queued. The gate closing
    # again is precisely the signal that every render event has run.
    qtbot.waitUntil(lambda: not svc._frame_in_flight, timeout=5000)

    # The producer really did outrun the consumer, or the test proves nothing.
    assert len(attempts) > len(rendered)
    # Every frame the consumer never saw was refused at the source rather
    # than queued behind it.
    assert svc.backpressure_drops == len(attempts) - len(rendered)
    assert rendered == emitted
    # Depth is O(1), not O(frames produced).
    assert max(depths) <= 1


def test_fps_cap_composes_with_the_gate():
    """The subclass throttle delegates upward instead of bypassing it."""
    svc = FlightFeedStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
        fps_limit=None,
    )
    received = []
    svc.frameReady.connect(lambda f, ts, n: received.append(n))

    svc._frame_in_flight = True
    svc._frame_in_flight_since = time.monotonic()

    for i in range(4):
        svc._emit_frame_ready(_frame(i), float(i), i)

    assert received == []
    assert svc.backpressure_drops == 4
    # Cadence limiting is a separate concern with a separate counter.
    assert svc.dropped_frames == 0
