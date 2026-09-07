"""Unit tests for :class:`WebRTCStreamService` (plan §12).

The plan calls for stubbed-``RTCPeerConnection`` lifecycle tests and
synthetic-frame conversion tests. Since aiortc is an optional dependency
(``ImportError`` is surfaced at ``request_connect`` time), the tests
here verify:

* The module imports cleanly without aiortc.
* The fingerprint extractor parses common SDP shapes.
* :meth:`request_disconnect` is a no-op when the loop has not started.
* When aiortc is absent, the service emits a clean ``errorOccurred`` on
  ``run()`` and exits without raising.

End-to-end tests against a real aiortc publisher live behind the manual
smoke path in plan §14.
"""

from __future__ import annotations

import asyncio
import os
import sys
import warnings

import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402
from core.services.streaming.WebRTCStreamService import WebRTCStreamService  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_extract_remote_fingerprint_returns_hex_only_uppercase() -> None:
    """Match ADIAT_Mobile/SdpFingerprintExtractor — hex+colons, uppercased,
    NO ``sha-256 `` algorithm prefix. SAS derivation feeds this exact
    shape into the canonical hash; the desktop and mobile must agree."""
    sdp = (
        "v=0\r\n"
        "a=group:BUNDLE 0\r\n"
        "a=fingerprint:sha-256 ab:cd:ef:01:23:45\r\n"
    )
    assert WebRTCStreamService._extract_remote_fingerprint(sdp) == "AB:CD:EF:01:23:45"


def test_extract_remote_fingerprint_returns_none_when_absent() -> None:
    assert WebRTCStreamService._extract_remote_fingerprint("v=0") is None
    assert WebRTCStreamService._extract_remote_fingerprint("") is None


def test_extract_remote_fingerprint_case_insensitive_prefix() -> None:
    """RFC 4566: SDP attribute names are case-insensitive. The hex
    output is always uppercased to match mobile's emit shape."""
    sdp = "A=Fingerprint:SHA-256 ab:cd:ef\r\n"
    assert WebRTCStreamService._extract_remote_fingerprint(sdp) == "AB:CD:EF"


def test_request_disconnect_before_run_is_safe(qapp) -> None:
    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    # No loop has been created; request_disconnect should set the stop flag
    # without raising.
    svc.request_disconnect()
    svc.cleanup()


def test_reset_clears_transient_state(qapp) -> None:
    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    svc._frame_n = 42
    svc._was_disconnected = True
    svc._remote_fp_initial = "sha-256 DEADBEEF"
    svc.reset()
    assert svc._frame_n == 0
    assert svc._sas_words is None
    assert svc._was_disconnected is False
    assert svc._remote_fp_initial is None
    assert svc._snapshot_channel is None
    svc.cleanup()


def test_send_snapshot_request_no_op_when_channel_missing(qapp) -> None:
    """``_send_snapshot_request`` must tolerate a missing or closed channel."""
    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    # No channel allocated yet — must not raise.
    assert svc._snapshot_channel is None
    svc._send_snapshot_request()

    class _ClosedChannel:
        readyState = "closed"

        def send(self, _data):  # pragma: no cover - should not be called
            raise AssertionError("send should not run when channel is not open")

    svc._snapshot_channel = _ClosedChannel()
    svc._send_snapshot_request()
    svc.cleanup()


def test_send_snapshot_request_sends_json_when_channel_open(qapp) -> None:
    """When the channel is open, the desktop emits the request_snapshot envelope."""
    import json

    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    sent = []

    class _OpenChannel:
        readyState = "open"

        def send(self, data):
            sent.append(data)

    svc._snapshot_channel = _OpenChannel()
    svc._send_snapshot_request()
    assert sent
    envelope = json.loads(sent[0])
    assert envelope == {"type": "request_snapshot"}
    svc.cleanup()


def test_default_ice_restart_grace_is_60_seconds(qapp) -> None:
    """The grace window before treating ``failed`` as terminal is operator-visible."""
    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    assert svc._ice_restart_grace == 60.0
    svc.cleanup()


def test_constructor_accepts_custom_ice_restart_grace(qapp) -> None:
    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
        ice_restart_grace=5.0,
    )
    assert svc._ice_restart_grace == 5.0
    svc.cleanup()


def test_consume_signaling_accepts_legacy_offer_sdp_field(qapp) -> None:
    """Plan §18 (W4): the WS broadcast may use ``sdp`` (new) or
    ``offer_sdp`` (legacy). The re-offer handler must accept either —
    real-world Worker builds have been seen omitting the new field."""
    import asyncio

    class _StubSignaling:
        """Yields one ``offer`` message then a ``closed`` message."""

        def __init__(self, message):
            self._message = message

        def subscribe(self, code, role):
            messages = [self._message, {"type": "closed", "reason": "end-of-test"}]

            async def _gen():
                for msg in messages:
                    yield msg

            return _gen()

    captured_sdps = []

    async def fake_handle_reoffer(self, _pc, sdp):
        captured_sdps.append(sdp)

    svc = WebRTCStreamService(
        signaling=_StubSignaling(
            {"type": "offer", "offer_sdp": "v=0\r\nlegacy-payload"}
        ),
        pairing_code="LGCYWS",
    )
    svc._connected = True  # bypass the "ignore re-offers before initial pair" guard

    import core.services.streaming.WebRTCStreamService as svc_module
    original = svc_module.WebRTCStreamService._handle_reoffer
    svc_module.WebRTCStreamService._handle_reoffer = fake_handle_reoffer
    try:
        asyncio.run(svc._consume_signaling(pc=object()))
    finally:
        svc_module.WebRTCStreamService._handle_reoffer = original
        svc.cleanup()

    assert captured_sdps == ["v=0\r\nlegacy-payload"]


def test_handle_reoffer_aborts_on_fingerprint_change(qapp) -> None:
    """Fingerprint change mid-session must close defensively (plan §9 trust model)."""
    import asyncio

    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(),
        pairing_code="ABC234",
    )
    errors = []
    svc.errorOccurred.connect(lambda msg: errors.append(msg))

    svc._remote_fp_initial = "sha-256 AA:BB:CC:DD"
    new_offer = (
        "v=0\r\n"
        "a=fingerprint:sha-256 99:88:77:66\r\n"  # different fingerprint
    )

    class _PC:  # pragma: no cover - sentinel; setRemoteDescription must not be called
        async def setRemoteDescription(self, _desc):
            raise AssertionError("setRemoteDescription should not run on fp mismatch")

        async def createAnswer(self):
            raise AssertionError("createAnswer should not run on fp mismatch")

        async def setLocalDescription(self, _desc):
            raise AssertionError("setLocalDescription should not run on fp mismatch")

    asyncio.run(svc._handle_reoffer(_PC(), new_offer))
    assert errors, "fingerprint change should emit errorOccurred"
    assert "fingerprint" in errors[0].lower()
    svc.cleanup()


def test_missing_aiortc_emits_error_and_exits_cleanly(qapp, monkeypatch) -> None:
    """If aiortc is unavailable, run() must emit errorOccurred and return."""

    # Force the lazy import to fail no matter what is actually installed.
    from core.services.streaming import WebRTCStreamService as svc_module

    def _broken_require():
        raise ImportError("aiortc is not installed in the test environment")

    monkeypatch.setattr(svc_module, "_require_aiortc", _broken_require)

    svc = WebRTCStreamService(
        signaling=InMemorySignalingChannel(), pairing_code="ABC234"
    )
    errors = []
    svc.errorOccurred.connect(lambda msg: errors.append(msg))
    # Drive run() directly on this thread (no QThread.start), since the
    # method body is what we are testing.
    svc.run()
    assert errors, "errorOccurred should fire when aiortc cannot be imported"
    assert "aiortc" in errors[0].lower()


class MediaStreamErrorLike(Exception):
    """Stand-in for aiortc's ``MediaStreamError``, which carries no message.

    Declared here rather than imported so these tests hold whether or not
    aiortc is installed in the environment.
    """


class TestCleanShutdown:
    """Field report: closing the app during a live feed printed three
    "Task was destroyed but it is pending!" warnings, then a "Video track
    error:" with no message at all.

    Both are the ordinary close path complaining about itself: the loop
    was closed with work still in flight, and the track ending because
    the peer went away was reported as a fault.
    """

    def _service(self):
        return WebRTCStreamService(
            signaling=InMemorySignalingChannel(), pairing_code="ABC234"
        )

    # -- draining the loop before closing it ---------------------------

    def test_drain_leaves_nothing_pending(self, qapp) -> None:
        """What asyncio complains about at collection time is a task that
        was never finished; after the drain there are none."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        try:
            async def forever():
                await asyncio.sleep(3600)

            async def seed():
                loop.create_task(forever())      # e.g. websockets keepalive
                loop.create_task(forever())      # e.g. an orphaned _tear_down
                await asyncio.sleep(0)

            loop.run_until_complete(seed())
            assert [t for t in asyncio.all_tasks(loop) if not t.done()]

            svc._drain_loop(loop)

            assert not [t for t in asyncio.all_tasks(loop) if not t.done()]
        finally:
            loop.close()
            svc.cleanup()

    def test_drain_lets_cancellation_finish_its_cleanup(self, qapp) -> None:
        """Cancelling is not enough - a task's ``finally`` is where the
        transport actually gets released, and that only runs if the
        cancellation is awaited."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        released = []
        try:
            async def holds_a_transport():
                try:
                    await asyncio.sleep(3600)
                finally:
                    await asyncio.sleep(0)       # yields, as a real close does
                    released.append("closed")

            async def seed():
                loop.create_task(holds_a_transport())
                await asyncio.sleep(0)

            loop.run_until_complete(seed())

            svc._drain_loop(loop)

            assert released == ["closed"]
        finally:
            loop.close()
            svc.cleanup()

    def test_drain_of_an_idle_loop_is_a_no_op(self, qapp) -> None:
        svc = self._service()
        loop = asyncio.new_event_loop()
        try:
            svc._drain_loop(loop)
            assert loop.is_closed() is False
        finally:
            loop.close()
            svc.cleanup()

    def test_drain_of_a_closed_loop_is_silent(self, qapp) -> None:
        """A shutdown path that can throw turns a clean close into a crash
        report - and one that warns is still noise on the console the
        operator is watching."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        loop.close()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            svc._drain_loop(loop)  # must not raise

        assert [str(w.message) for w in caught] == []
        svc.cleanup()

    # -- one teardown, awaited -----------------------------------------

    def test_stop_starts_exactly_one_teardown(self, qapp) -> None:
        """``request_disconnect`` then ``cleanup`` - the ordinary
        close-the-tile-then-close-the-window sequence - must not stack
        teardowns."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        started = []

        async def fake_tear_down():
            started.append(1)
            await asyncio.sleep(3600)

        svc._tear_down = fake_tear_down
        try:
            async def stop_twice():
                svc._begin_tear_down()
                svc._begin_tear_down()
                await asyncio.sleep(0)

            loop.run_until_complete(stop_twice())

            assert started == [1]
        finally:
            svc._drain_loop(loop)
            loop.close()
            svc.cleanup()

    def test_finish_awaits_the_teardown_already_under_way(self, qapp) -> None:
        """The orphan in the field report was a half-run teardown: the loop
        stopped mid-flight, and the finally block then started a *second*
        one that skipped the cancel the first had already claimed."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        calls = []

        async def fake_tear_down():
            calls.append("start")
            await asyncio.sleep(0)
            calls.append("done")

        svc._tear_down = fake_tear_down
        try:
            async def stop_then_finish():
                svc._begin_tear_down()
                await asyncio.sleep(0)          # teardown starts, then suspends
                await svc._finish_tear_down()

            loop.run_until_complete(stop_then_finish())

            assert calls == ["start", "done"], "one teardown, run to completion"
            assert svc._teardown_task is None
        finally:
            loop.close()
            svc.cleanup()

    def test_finish_tears_down_when_nothing_started_one(self, qapp) -> None:
        """A terminal negotiation error ends the loop without a stop
        request; the finally block is then the only teardown there is."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        calls = []

        async def fake_tear_down():
            calls.append("start")

        svc._tear_down = fake_tear_down
        try:
            loop.run_until_complete(svc._finish_tear_down())

            assert calls == ["start"]
        finally:
            loop.close()
            svc.cleanup()

    def test_schedule_stop_without_a_running_loop_still_sets_stop(self, qapp) -> None:
        svc = self._service()
        svc._schedule_stop()

        assert svc._stop.is_set() is True
        assert svc._teardown_task is None
        svc.cleanup()

    # -- closing across a loop that has already gone -------------------
    #
    # run()'s finally closes the loop before it clears self._loop, and a
    # UI-thread close can land in between. No check on the caller's side
    # can exclude that: only the owning thread knows the loop is closing.
    # The old is_running() test turned the race into an unhandled
    # RuntimeError on the Qt main thread, inside a slot, for a tile the
    # operator had just closed.

    def test_a_close_arriving_after_the_loop_closed_does_not_raise(self, qapp) -> None:
        svc = self._service()
        loop = asyncio.new_event_loop()
        loop.close()
        svc._loop = loop            # what run() leaves behind for a beat

        svc._schedule_stop()        # must not raise "Event loop is closed"

        # The stop still registers: it is a threading.Event set by the
        # caller, not something queued onto the loop that just died.
        assert svc._stop.is_set() is True
        assert svc._teardown_task is None
        svc.cleanup()

    def test_confirm_sas_after_the_loop_closed_does_not_raise(self, qapp) -> None:
        """No production caller today, but it carried the same defect - and
        an unused copy of a pattern is where the pattern comes back from."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        loop.close()
        svc._loop = loop

        svc.confirm_sas(True)       # must not raise

        assert svc._sas_accepted is True
        svc.cleanup()

    def test_a_close_on_a_live_loop_still_queues_teardown(self, qapp) -> None:
        """The tolerance must not have cost the ordinary path its post."""
        svc = self._service()
        loop = asyncio.new_event_loop()
        posted = []
        loop.call_soon_threadsafe = lambda cb, *a: posted.append(cb)
        svc._loop = loop
        try:
            svc._schedule_stop()
        finally:
            loop.close()

        assert posted == [svc._begin_tear_down]
        assert svc._stop.is_set() is True
        svc.cleanup()

    # -- the empty "Video track error:" --------------------------------

    def test_a_track_ending_during_shutdown_is_not_an_error(self, qapp) -> None:
        """MediaStreamError carries no message, so the operator was shown
        "Video track error:" and nothing else - for the close they had just
        asked for."""
        svc = self._service()
        errors = []
        svc.errorOccurred.connect(errors.append)

        class EndedTrack:
            async def recv(self):
                svc._stop.set()                  # the close lands first
                raise MediaStreamErrorLike()

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(svc._consume_video(EndedTrack()))
        finally:
            loop.close()

        assert errors == []
        svc.cleanup()

    def test_a_track_failing_mid_flight_still_reports(self, qapp) -> None:
        """The publisher dropping out unannounced is a real event - and it
        now names the failure instead of trailing off after the colon."""
        svc = self._service()
        errors = []
        svc.errorOccurred.connect(errors.append)

        class BrokenTrack:
            async def recv(self):
                raise MediaStreamErrorLike()     # no message, as aiortc's has none

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(svc._consume_video(BrokenTrack()))
        finally:
            loop.close()

        assert errors == ["Video track error: MediaStreamErrorLike"]
        svc.cleanup()

    def test_a_message_bearing_failure_is_passed_through(self, qapp) -> None:
        svc = self._service()
        errors = []
        svc.errorOccurred.connect(errors.append)

        class BrokenTrack:
            async def recv(self):
                raise RuntimeError("decoder gave up")

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(svc._consume_video(BrokenTrack()))
        finally:
            loop.close()

        assert errors == ["Video track error: decoder gave up"]
        svc.cleanup()
