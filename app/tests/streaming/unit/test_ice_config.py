"""ICE server configuration — and the library default it exists to displace.

``RTCPeerConnection()`` with no ``configuration`` is not "no ICE servers".
aiortc fills the gap from ``RTCIceGatherer.getDefaultIceServers()``, which
returns Google's public STUN server, so the Flight Viewer was sending a
STUN binding request to Google on every pairing attempt without anything
in ADIAT naming that choice.

The tests that matter here pin the shape of the decision: an operator's
explicitly empty list must survive as an empty list (a "falsy means
unset" reflex would quietly restore a public STUN server they had just
removed), ``WebRTCStreamService`` must always pass a configuration
object, and the declared default must stay off Google — a revert there
is invisible at runtime, because pairing works either way.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.services.streaming import ice_config  # noqa: E402
from core.services.streaming.ice_config import (  # noqa: E402
    DEFAULT_ICE_SERVER_URLS,
    ice_server_urls,
)


def test_no_config_yields_the_declared_default():
    """Absent operator config, ADIAT's own default applies — not aiortc's."""
    assert ice_server_urls({}) == list(DEFAULT_ICE_SERVER_URLS)


def test_an_explicit_empty_list_is_honoured_as_empty():
    """The whole point of the module.

    ``[]`` means "host candidates only, no third-party contact". Treating
    it as falsy-therefore-unset would hand the operator back the STUN
    server they just removed, which is the exact bug this replaces.
    """
    assert ice_server_urls({"ice_servers": []}) == []


def test_a_configured_server_replaces_the_default():
    urls = ice_server_urls({"ice_servers": ["stun:stun.example.org:3478"]})

    assert urls == ["stun:stun.example.org:3478"]
    assert urls != list(DEFAULT_ICE_SERVER_URLS)


def test_turn_and_stuns_uris_are_accepted():
    """aiortc parses all four schemes; the validator must not narrow that."""
    configured = [
        "stun:a.example:3478",
        "stuns:b.example:5349",
        "turn:c.example:3478",
        "turns:d.example:5349",
    ]

    assert ice_server_urls({"ice_servers": configured}) == configured


def test_entries_with_an_unusable_scheme_are_dropped_not_passed_through():
    """A bad URI raises deep inside ICE gathering, far from the edit that
    caused it. Dropping it here keeps the rest of the config working."""
    urls = ice_server_urls(
        {"ice_servers": ["https://not-a-stun-server.example", "stun:ok.example:3478"]}
    )

    assert urls == ["stun:ok.example:3478"]


def test_blank_and_non_string_entries_are_dropped():
    urls = ice_server_urls({"ice_servers": ["", "   ", 42, None, "stun:ok.example:3478"]})

    assert urls == ["stun:ok.example:3478"]


def test_a_non_list_value_falls_back_to_the_default():
    """Operator-supplied TOML is never allowed to break pairing outright."""
    assert ice_server_urls({"ice_servers": "stun:one.example"}) == list(
        DEFAULT_ICE_SERVER_URLS
    )


def test_urls_are_stripped_of_surrounding_whitespace():
    assert ice_server_urls({"ice_servers": ["  stun:ok.example:3478  "]}) == [
        "stun:ok.example:3478"
    ]


def test_the_default_is_read_from_the_webrtc_config_section(monkeypatch):
    """The key lives at ``[webrtc] ice_servers``; nothing else is consulted."""
    seen = {}

    def fake_get_section(name):
        seen["name"] = name
        return {"ice_servers": ["stun:from-config.example:3478"]}

    import helpers.AppConfig as AppConfig

    monkeypatch.setattr(AppConfig, "get_section", fake_get_section)

    assert ice_server_urls() == ["stun:from-config.example:3478"]
    assert seen["name"] == "webrtc"


def test_build_ice_servers_wraps_each_url(monkeypatch):
    """Returns RTCIceServer objects, and an empty list stays a list — never
    ``None``, which is the value aiortc reads as "use my defaults"."""
    pytest.importorskip("aiortc")
    from core.services.streaming.ice_config import build_ice_servers

    servers = build_ice_servers({"ice_servers": ["stun:ok.example:3478"]})
    assert len(servers) == 1
    assert servers[0].urls == "stun:ok.example:3478"

    empty = build_ice_servers({"ice_servers": []})
    assert empty == []
    assert empty is not None


def test_webrtc_service_never_constructs_a_bare_peer_connection():
    """The regression guard.

    A future edit that drops the ``configuration`` argument restores the
    silent Google STUN call with no visible symptom — pairing keeps
    working, so no other test would notice. Parsed rather than grepped so
    the assertion reads the code, not the comments around it.
    """
    import ast
    import inspect

    from core.services.streaming import WebRTCStreamService as module

    tree = ast.parse(inspect.getsource(module))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "RTCPeerConnection"
    ]

    assert calls, "expected WebRTCStreamService to construct an RTCPeerConnection"
    for call in calls:
        keywords = {kw.arg for kw in call.keywords}
        assert "configuration" in keywords, (
            "A bare RTCPeerConnection() makes aiortc substitute its default "
            "ICE servers (Google's public STUN). Pass configuration= instead."
        )


def test_the_declared_default_is_a_stun_uri():
    """STUN is required: the Flight Viewer pairs over the public internet
    with no TURN relay (plan §1), so an empty default would break it."""
    assert DEFAULT_ICE_SERVER_URLS
    assert all(url.startswith("stun:") for url in DEFAULT_ICE_SERVER_URLS)


def test_the_declared_default_is_not_a_google_endpoint():
    """The reason for the switch, pinned.

    aiortc's default was Google's public STUN server, reached purely by
    omission. ADIAT routes every pairing through Cloudflare already (the
    ``adiat-flight-signaling`` Worker sees the code, both peers'
    addresses and the full SDP), so Cloudflare learns nothing from a
    binding request while Google would. Nothing at runtime would flag a
    revert — pairing succeeds against either — so it is asserted.
    """
    joined = " ".join(DEFAULT_ICE_SERVER_URLS).lower()

    assert "google" not in joined
    assert "cloudflare" in joined


def test_module_imports_without_aiortc_installed():
    """Matches WebRTCStreamService's lazy-import contract — importing this
    module must not require the optional WebRTC extras."""
    assert ice_config.ice_server_urls is ice_server_urls
