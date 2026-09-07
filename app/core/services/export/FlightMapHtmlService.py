"""Standalone flight map page for a recording bundle.

The streaming window already renders a live map
(:class:`~core.views.components.FlightMapView.FlightMapView`), but that map
is a Qt widget driven by JS calls — it cannot be handed to anyone. This
service writes the same picture as a **single self-contained HTML file**:
the flight path the aircraft flew during the recording, every stored
detection pinned at the aircraft position of its frame, and markers for
where the recorded segment started and ended.

Self-contained matters. Leaflet's CSS/JS are inlined from the vendored
copy via :func:`~core.views.components.FlightMapView.build_leaflet_head`,
and all data is baked into the page as a JSON literal, so the file opens
in any browser on any machine with no ADIAT, no server and no Python.
Only the basemap tiles need the network; with no connection the path and
pins still draw over an empty canvas.

Colors mirror the live map's palette so a pin means the same thing in the
exported page as it did on screen during the flight.
"""

from __future__ import annotations

import html
import json
from typing import Dict, List, Optional, Sequence, Tuple

from core.services.export.LeafletAssetService import (
    AIRCRAFT_COLOR,
    DEFAULT_PIN_COLOR,
    DETECTOR_PALETTE,
    build_leaflet_head,
)

# Where the recorded segment began and ended. Distinct from both the
# detector palette and the cyan track so three things never collide.
START_COLOR = "#4CAF50"
END_COLOR = "#F44336"


def pin_color_for(detection_type: Optional[str]) -> str:
    """Pick a pin color, matching the live map's per-detector palette."""
    if not detection_type:
        return DEFAULT_PIN_COLOR
    return DETECTOR_PALETTE.get(str(detection_type).lower(), DEFAULT_PIN_COLOR)


_PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__TITLE__</title>
__ADIAT_LEAFLET_HEAD__
<style>
html, body { height: 100%; margin: 0; padding: 0; background: #1e1e1e; }
#map { position: absolute; top: 0; left: 0; right: 0; bottom: 0; }
.leaflet-container { background: #1e1e1e; }
.adiat-pin {
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid #fff;
    box-shadow: 0 0 4px rgba(0,0,0,0.6);
}
#adiat-caption {
    position: absolute; top: 10px; left: 10px; z-index: 500;
    max-width: 340px;
    padding: 8px 12px;
    border-radius: 4px;
    background: rgba(30,30,30,0.82);
    color: #e8e8e8;
    font: 12px/1.45 -apple-system, "Segoe UI", sans-serif;
    box-shadow: 0 1px 6px rgba(0,0,0,0.5);
}
#adiat-caption h1 { margin: 0 0 4px; font-size: 13px; font-weight: 600; }
#adiat-caption p { margin: 0; color: #b9b9b9; }
#adiat-empty {
    position: absolute; top: 50%; left: 0; right: 0;
    text-align: center; color: #d6d6d6; z-index: 400;
    font: 14px -apple-system, "Segoe UI", sans-serif;
}
</style>
</head>
<body>
<div id="map"></div>
<div id="adiat-caption"><h1>__CAPTION_TITLE__</h1><p>__CAPTION_DETAIL__</p></div>
<script>
var ADIAT_MAP_DATA = __DATA__;

function adiatInit() {
    if (typeof L === 'undefined') {
        document.getElementById('map').innerHTML =
            '<div id="adiat-empty">Map unavailable: the Leaflet library did not load.</div>';
        return;
    }
    var data = ADIAT_MAP_DATA;
    var map = L.map('map', { worldCopyJump: true }).setView([30.0, -97.0], 4);

    var roadLayer = L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        { maxZoom: 19, attribution: '\\u00a9 OpenStreetMap' });
    var satelliteLayer = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/' +
        'MapServer/tile/{z}/{y}/{x}',
        { maxZoom: 19, attribution: 'Tiles \\u00a9 Esri' });
    var labelsOverlay = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/' +
        'World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        { maxZoom: 19, attribution: 'Labels \\u00a9 Esri' });
    var hybridLayer = L.layerGroup([satelliteLayer, labelsOverlay]);
    roadLayer.addTo(map);
    L.control.layers(
        { 'Road': roadLayer, 'Satellite': satelliteLayer, 'Hybrid': hybridLayer },
        {}, { position: 'topright', collapsed: true }
    ).addTo(map);

    function pinIcon(color) {
        return L.divIcon({
            className: '',
            html: '<div class="adiat-pin" style="background:' + color + '"></div>',
            iconSize: [18, 18],
            iconAnchor: [9, 9]
        });
    }

    var bounds = null;
    function extend(latlng) {
        if (bounds === null) { bounds = L.latLngBounds(latlng, latlng); }
        else { bounds.extend(latlng); }
    }

    if (data.path && data.path.length > 1) {
        L.polyline(data.path, {
            color: data.track_color, weight: 3, opacity: 0.9
        }).addTo(map);
    }
    (data.path || []).forEach(extend);

    if (data.path && data.path.length) {
        var first = data.path[0];
        var last = data.path[data.path.length - 1];
        L.marker(first, { icon: pinIcon(data.start_color) })
            .addTo(map).bindPopup(data.start_label);
        if (data.path.length > 1) {
            L.marker(last, { icon: pinIcon(data.end_color) })
                .addTo(map).bindPopup(data.end_label);
        }
    }

    (data.detections || []).forEach(function(det) {
        var marker = L.marker([det.lat, det.lon], { icon: pinIcon(det.color) }).addTo(map);
        if (det.popup) { marker.bindPopup(det.popup); }
        extend([det.lat, det.lon]);
    });

    if (bounds !== null) {
        map.fitBounds(bounds.pad(0.15));
    } else {
        document.getElementById('map').insertAdjacentHTML(
            'beforeend',
            '<div id="adiat-empty">No location data was recorded for this flight.</div>');
    }
}

if (document.readyState === 'complete') { adiatInit(); }
else { window.addEventListener('load', adiatInit); }
</script>
</body>
</html>
"""


def _popup_html(detection: dict) -> str:
    """Build a detection popup: label, then any detail lines supplied."""
    label = html.escape(str(detection.get("label") or "Detection"))
    lines = [f"<b>{label}</b>"]
    for line in detection.get("details") or []:
        if line:
            lines.append(html.escape(str(line)))
    thumbnail = detection.get("thumbnail")
    if thumbnail:
        # Relative to the page, which sits beside the detections folder in
        # the bundle — so the popup shows the actual crop when the folder
        # travels intact, and degrades to a broken-image icon if it does not.
        src = html.escape(str(thumbnail), quote=True)
        lines.append(f'<img src="{src}" alt="" style="max-width:180px;margin-top:4px" />')
    return "<br>".join(lines)


def build_flight_map_html(
    *,
    path: Sequence[Tuple[float, float]],
    detections: Sequence[dict] = (),
    title: str = "ADIAT Flight Map",
    caption: str = "",
) -> str:
    """Render the standalone map page as a string.

    Args:
        path: Ordered ``(lat, lon)`` fixes flown during the recording.
        detections: Dicts with ``lat``, ``lon`` and optionally ``label``,
            ``details`` (a list of strings), ``detection_type`` (picks the
            pin color) and ``thumbnail`` (a page-relative image path).
        title: Page title, also shown in the caption box.
        caption: One line of context under the title (times, counts).

    Returns:
        A complete HTML document. Safe to write as UTF-8.
    """
    clean_path: List[List[float]] = [
        [float(lat), float(lon)]
        for lat, lon in path or []
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float))
    ]

    pins: List[Dict[str, object]] = []
    for detection in detections or []:
        lat = detection.get("lat")
        lon = detection.get("lon")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            continue
        pins.append({
            "lat": float(lat),
            "lon": float(lon),
            "color": detection.get("color") or pin_color_for(detection.get("detection_type")),
            "popup": _popup_html(detection),
        })

    data = {
        "path": clean_path,
        "detections": pins,
        "track_color": AIRCRAFT_COLOR,
        "start_color": START_COLOR,
        "end_color": END_COLOR,
        "start_label": "Recording started here",
        "end_label": "Recording ended here",
    }

    page = _PAGE_TEMPLATE
    page = page.replace("__ADIAT_LEAFLET_HEAD__", build_leaflet_head())
    page = page.replace("__TITLE__", html.escape(title))
    page = page.replace("__CAPTION_TITLE__", html.escape(title))
    page = page.replace("__CAPTION_DETAIL__", html.escape(caption))
    # `</script>` inside the data would close the tag early; nothing here
    # should contain one, but the popups carry operator-visible strings.
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = page.replace("__DATA__", payload)
    return page


def write_flight_map_html(
    target_path: str,
    *,
    path: Sequence[Tuple[float, float]],
    detections: Sequence[dict] = (),
    title: str = "ADIAT Flight Map",
    caption: str = "",
) -> str:
    """Write :func:`build_flight_map_html` to ``target_path``.

    Returns the path written. Raises ``OSError`` on write failure — the
    caller decides whether a missing map is fatal (it is not).
    """
    page = build_flight_map_html(
        path=path, detections=detections, title=title, caption=caption
    )
    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write(page)
    return target_path


__all__ = [
    "END_COLOR",
    "START_COLOR",
    "build_flight_map_html",
    "pin_color_for",
    "write_flight_map_html",
]
