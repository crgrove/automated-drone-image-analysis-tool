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

import os
import sys

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
