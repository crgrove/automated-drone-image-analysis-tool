"""Signaling subpackage for WebRTC pairing.

Provides the abstract :class:`SignalingChannel` interface plus concrete
implementations used by the Flight Viewer to exchange SDP / ICE /
fingerprint data with paired ADIAT Mobile publishers via the
``adiat-flight-signaling`` Cloudflare Worker.
"""

from .SignalingChannel import (
    CodeAlreadyAnswered,
    CodeNotFound,
    SessionState,
    SignalingChannel,
    ViewerCapReached,
)
from .HttpSignalingChannel import DEFAULT_WORKER_URL, HttpSignalingChannel
from .InMemorySignalingChannel import InMemorySignalingChannel
from . import pairing

__all__ = [
    "CodeAlreadyAnswered",
    "CodeNotFound",
    "DEFAULT_WORKER_URL",
    "HttpSignalingChannel",
    "InMemorySignalingChannel",
    "SessionState",
    "SignalingChannel",
    "ViewerCapReached",
    "pairing",
]
