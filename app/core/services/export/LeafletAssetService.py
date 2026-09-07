"""Leaflet assets and map colours, shared by the widget and the exporter.

Extracted from :mod:`core.views.components.FlightMapView` because
:mod:`core.services.export.FlightMapHtmlService` needed the same palette and
the same ``<head>`` fragment, and was importing them *from the view* - a
service depending on a Qt widget module, which CLAUDE.md 2.1 rules out and
which meant generating an offline map page pulled the widget's Qt imports in
behind it.

Nothing here touches Qt. The widget re-exports these names so its own
callers are unaffected, the same way :mod:`core.views.flight.MapDock`
re-exports the widget's.
"""

from __future__ import annotations

import base64
import re
import sys
from functools import lru_cache
from pathlib import Path


# Per-detector palette — must mirror ``OverlayCompositor.colorForDetector``
# on the mobile side (plan §19.4.4 / ADIAT_Mobile OverlayCompositor.kt
# line ~218) so the operator sees the same orange-for-person pin colour
# the publisher drew on the live video.
DETECTOR_PALETTE = {
    "person": "#FB5E1C",       # AdiatColors.Accent orange
    "color-range": "#58B7FF",  # soft blue
    "motion": "#FFD54F",       # amber
    "dji-native": "#4CAF50",   # green
}
DEFAULT_PIN_COLOR = "#9C27B0"  # fallback purple for unknown detector ids

# Aircraft marker + trail. Cyan reads clearly against both OSM road tiles
# and satellite imagery, and is outside the detector palette so an
# aircraft is never mistaken for a detection.
AIRCRAFT_COLOR = "#00E5FF"
DEFAULT_FEED_ID = "default"

# Cap on JS buffered before the page reports loaded.
_MAX_PENDING_JS = 500

# Vendored Leaflet (see resources/vendor/leaflet/README.md). Keep in step
# with the files on disk.
LEAFLET_VERSION = "1.9.4"
_LEAFLET_CDN_BASE = f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist"


def _vendor_dir() -> Path:
    """Locate ``resources/vendor/leaflet`` in both source and frozen builds."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", ".")) / "resources" / "vendor" / "leaflet"
    # .../app/core/services/export/LeafletAssetService.py -> repo root
    # (export -> services -> core -> app -> root) - the same depth the
    # view sat at, asserted in test_leaflet_asset_service.py.
    root = Path(__file__).resolve().parents[4]
    return root / "resources" / "vendor" / "leaflet"


def _inline_css_images(css: str, directory: Path) -> str:
    """Rewrite ``url(images/x.png)`` in Leaflet's CSS to ``data:`` URIs.

    Leaflet's stylesheet points at its icons relatively. Served from a CDN
    those resolved next to the stylesheet; inlined into our page they
    resolve against the page's base URL instead and 404 — which silently
    blanked the basemap-selector button. Embedding the images keeps the
    stylesheet self-contained. They are tiny (~3 KB in total).
    """
    def replace(match):
        name = match.group(1)
        try:
            raw = (directory / "images" / name).read_bytes()
        except OSError:
            return match.group(0)   # leave the original URL alone
        encoded = base64.b64encode(raw).decode("ascii")
        return f"url(data:image/png;base64,{encoded})"

    return re.sub(r"url\(images/([A-Za-z0-9._-]+)\)", replace, css)


@lru_cache(maxsize=1)
def load_leaflet_assets() -> tuple:
    """Return ``(css, js)`` for Leaflet, inlined from the vendored copies.

    Returns ``(None, None)`` when the vendored files are missing, in which
    case the page falls back to the CDN.

    Inlining rather than linking to a local file avoids every ``file://``
    vs ``qrc://`` vs base-URL question in QtWebEngine, and — the reason
    this exists — removes a network round-trip from the critical path of
    opening a map. Pulling Leaflet from a CDN meant a single transient
    failure (a DNS blip, or the request racing QtWebEngine's network
    service at app start) replaced the entire widget with an error
    message for the rest of the session, with no retry.
    """
    directory = _vendor_dir()
    try:
        css = (directory / "leaflet.css").read_text(encoding="utf-8")
        js = (directory / "leaflet.js").read_text(encoding="utf-8")
    except OSError:
        return (None, None)
    if not css.strip() or not js.strip():
        return (None, None)
    return (_inline_css_images(css, directory), js)


def build_leaflet_head() -> str:
    """Build the ``<head>`` fragment that supplies Leaflet.

    Prefers the vendored copy; falls back to the CDN so a checkout or
    build that is missing ``resources/vendor/leaflet`` still works.
    """
    css, js = load_leaflet_assets()
    if css and js:
        # ``</script>`` inside the library would close the tag early; Leaflet
        # does not contain one, but escape defensively since this is
        # concatenated into markup.
        safe_js = js.replace("</script>", "<\\/script>")
        return f"<style>\n{css}\n</style>\n<script>\n{safe_js}\n</script>"
    return (
        f'<link rel="stylesheet" href="{_LEAFLET_CDN_BASE}/leaflet.css" />\n'
        f'<script src="{_LEAFLET_CDN_BASE}/leaflet.js" crossorigin="anonymous">'
        f'</script>'
    )
