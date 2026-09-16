"""ICE server configuration for the Flight Viewer's WebRTC peer connections.

This module exists because the ICE configuration used to be *implicit*.
``RTCPeerConnection()`` was constructed with no ``configuration``
argument, and aiortc fills that in from
``RTCIceGatherer.getDefaultIceServers()`` — which returns Google's public
STUN server, ``stun:stun.l.google.com:19302``. So every pairing attempt
sent a STUN binding request to Google, from a search-and-rescue tool, on
the strength of a library default that nothing in ADIAT named or chose.

STUN itself is not optional here. The Flight Viewer's whole premise
(plan §1) is an off-site observer pairing with a field tablet *over the
public internet, with no shared LAN and no media relay*; without
server-reflexive candidates that case simply does not connect. TURN is a
declared non-goal, so STUN is the only NAT traversal ADIAT has.

What changes is that the choice is now ADIAT's, stated in one place and
overridable by the operator:

.. code-block:: toml

    [webrtc]
    ice_servers = ["stun:stun.example.org:3478"]

The default is Cloudflare's public STUN server. ADIAT already depends
on Cloudflare for signaling — ``signal.adiat.app`` is the
``adiat-flight-signaling`` Worker — so it learns nothing from a binding
request that it does not already see in the pairing itself. Google was a
second third party, added by nobody, learning something the first did
not. Both endpoints answer correctly; only one is already inside the
trust boundary.

An empty list is meaningful and is honoured exactly as written::

    [webrtc]
    ice_servers = []

That yields host candidates only — no third-party contact at all — which
is the right setting for a co-located LAN deployment or an organisation
that will not have its traffic touch a public STUN server. It is not the
default because it would break the over-the-internet pairing the feature
is for.

``None`` is never handed to aiortc: that is the value that re-triggers
the library default, so routing an operator's empty list through it
would put back the very Google endpoint this module removed.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from core.services.LoggerService import LoggerService

# ADIAT's declared default. Deliberately *not* behaviour-preserving:
# the Google endpoint aiortc used to supply was never a decision anyone
# made, so there was no prior choice to honour. Cloudflare already sees
# every pairing (it hosts the signaling Worker), which makes this the
# one STUN provider that adds no party to the flow.
DEFAULT_ICE_SERVER_URLS: tuple = ("stun:stun.cloudflare.com:3478",)

# URI schemes aiortc's ``parse_stun_turn_uri`` understands. Anything else
# raises deep inside ICE gathering, long after the operator edited the
# file, so it is rejected here where the message can name the key.
_VALID_SCHEMES = ("stun:", "stuns:", "turn:", "turns:")


def ice_server_urls(config_section: Optional[dict] = None) -> List[str]:
    """Resolve the ICE server URLs for this install.

    Args:
        config_section: Parsed ``[webrtc]`` table. Defaults to reading
            ``config.toml`` via :func:`helpers.AppConfig.get_section`.

    Returns:
        The configured URLs, or :data:`DEFAULT_ICE_SERVER_URLS` when the
        operator has expressed no preference. An explicitly configured
        empty list is returned as ``[]`` and is *not* replaced by the
        default — "no STUN" is a choice, not a missing value.
    """
    if config_section is None:
        try:
            from helpers.AppConfig import get_section

            config_section = get_section("webrtc")
        except Exception:  # pragma: no cover - defensive
            config_section = {}

    if not isinstance(config_section, dict) or "ice_servers" not in config_section:
        return list(DEFAULT_ICE_SERVER_URLS)

    configured = config_section.get("ice_servers")
    if not isinstance(configured, (list, tuple)):
        LoggerService().warning(
            "ice_config: [webrtc] ice_servers must be a list of URLs; "
            f"got {type(configured).__name__}. Using the default STUN server."
        )
        return list(DEFAULT_ICE_SERVER_URLS)

    return _validated(configured)


def _validated(configured: Sequence) -> List[str]:
    """Keep the well-formed entries, logging the ones dropped and why."""
    logger = LoggerService()
    urls: List[str] = []
    for entry in configured:
        if not isinstance(entry, str) or not entry.strip():
            logger.warning(
                f"ice_config: ignoring non-string [webrtc] ice_servers entry {entry!r}"
            )
            continue
        url = entry.strip()
        if not url.lower().startswith(_VALID_SCHEMES):
            logger.warning(
                f"ice_config: ignoring ICE server {url!r} - expected one of "
                f"{', '.join(s.rstrip(':') for s in _VALID_SCHEMES)}"
            )
            continue
        urls.append(url)
    return urls


def build_ice_servers(config_section: Optional[dict] = None) -> list:
    """Build the ``RTCIceServer`` list for an :class:`RTCPeerConnection`.

    Imports aiortc lazily so this module stays importable in environments
    without the WebRTC extras, matching
    :func:`core.services.streaming.WebRTCStreamService._require_aiortc`.

    Returns:
        A list of ``RTCIceServer``. Possibly empty — hand it to
        ``RTCConfiguration(iceServers=...)`` as-is; do not substitute
        ``None`` for an empty list.
    """
    from aiortc import RTCIceServer  # type: ignore

    return [RTCIceServer(urls=url) for url in ice_server_urls(config_section)]
