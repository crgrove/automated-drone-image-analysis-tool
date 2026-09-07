"""Reusable Leaflet map widget for aircraft position, path, and detections.

Extracted from :class:`~core.views.flight.MapDock.MapDock` so the same map
serves three callers:

* the **Flight Viewer**, where ``MapDock`` now wraps this widget in a
  ``QDockWidget`` (its public API is unchanged);
* the **streaming window**, which embeds the widget directly beneath the
  video;
* anything later that needs a map without dock chrome.

Beyond the detection pins the dock always had, this adds the two things a
live feed needs — a **moving aircraft marker** and a **flight path
polyline** — both keyed by ``feed_id`` so a multi-tile Flight Viewer
session renders one aircraft and one trail per drone.

Two modes, as before:

* **Interactive (Leaflet via QtWebEngine).** Full map with swappable
  Road / Satellite / Hybrid basemaps.
* **Fallback (no QtWebEngine).** A plain list of detections that can be
  deep-linked to a system map app. Aircraft/track updates are no-ops in
  this mode — there is nothing sensible to render them on.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from PySide6.QtCore import QObject, QUrl, Qt, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from helpers.TranslationMixin import TranslationMixin

# Leaflet assets and the shared colour vocabulary live in a Qt-free service
# so the offline-map exporter can use them without importing a widget; see
# core.services.export.LeafletAssetService. Re-exported here because this
# module's callers have always imported them from it.
from core.services.export.LeafletAssetService import (
    AIRCRAFT_COLOR,
    DEFAULT_FEED_ID,
    DEFAULT_PIN_COLOR,
    DETECTOR_PALETTE,
    LEAFLET_VERSION,
    build_leaflet_head,
    load_leaflet_assets,
)

# Cap on JS buffered before the page reports loaded.
_MAX_PENDING_JS = 500


LEAFLET_HTML = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
__ADIAT_LEAFLET_HEAD__
<style>
html, body, #map { height: 100%; margin: 0; padding: 0; background: #1e1e1e; }
.leaflet-container { background: #1e1e1e; }
.adiat-pin {
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid #fff;
    box-shadow: 0 0 4px rgba(0,0,0,0.6);
}
.adiat-aircraft {
    width: 0; height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 20px solid #00E5FF;
    filter: drop-shadow(0 0 3px rgba(0,0,0,0.8));
}
#leaflet-fallback {
    color: #d6d6d6;
    font-family: -apple-system, "Segoe UI", sans-serif;
    padding: 16px;
    line-height: 1.4;
}
</style>
</head>
<body>
<div id="map"></div>
<script>
// Defer ALL map init until the page (and the external Leaflet bundle)
// have finished loading. ``setHtml`` in QtWebEngine starts parsing
// before the CDN script's network round-trip completes, so inlining
// ``L.map(...)`` straight under the leaflet.js tag could fire while
// ``L`` was still ``undefined``. Listening for ``load`` plus an explicit
// guard makes init resilient to slow CDNs without blocking the UI.
var __adiatPendingMarkers = [];
var __adiatPendingView = null;
var __adiatPendingCalls = [];
// If Leaflet never loads (offline / blocked CDN) these stubs stay in place
// for the whole session, so the queue must not grow without bound — a
// 4 Hz feed would otherwise accumulate tens of thousands of dead entries.
var __ADIAT_MAX_PENDING = 500;

// Queue stubs that survive until the real handlers replace them — early
// callers (e.g. a frame arriving before page load) just buffer.
window.addMarker = function(lat, lon, label, key, color) {
    if (__adiatPendingMarkers.length < __ADIAT_MAX_PENDING) {
        __adiatPendingMarkers.push([lat, lon, label, key, color]);
    }
};
window.setView = function(lat, lon, zoom) {
    __adiatPendingView = [lat, lon, zoom];
};
window.fitAll = function() { /* no-op until init */ };
window.clearMarkers = function() { __adiatPendingMarkers = []; };
function __adiatQueue(name, args) {
    // Drop the oldest so a long offline session keeps the most recent
    // position rather than a stale prefix.
    if (__adiatPendingCalls.length >= __ADIAT_MAX_PENDING) {
        __adiatPendingCalls.shift();
    }
    __adiatPendingCalls.push([name, args]);
}
window.setAircraft = function() { __adiatQueue('setAircraft', arguments); };
window.appendTrack = function() { __adiatQueue('appendTrack', arguments); };
window.setTrack = function() { __adiatQueue('setTrack', arguments); };
window.clearTrack = function() { __adiatQueue('clearTrack', arguments); };
window.clearAircraft = function() { __adiatQueue('clearAircraft', arguments); };
window.setFollow = function() { __adiatQueue('setFollow', arguments); };

function __adiatInitLeaflet() {
    if (typeof L === 'undefined') {
        // Leaflet failed to load from the CDN — surface a static fallback
        // instead of leaving the widget blank. Common causes: no internet,
        // captive portal, CDN blocked.
        var el = document.getElementById('map');
        if (el) {
            el.innerHTML = '<div id="leaflet-fallback">' +
                'Map unavailable: the Leaflet library did not load.<br>' +
                'Positions are still tracked in the telemetry readout.</div>';
        }
        return;
    }
    var map = L.map('map', { worldCopyJump: true }).setView([30.0, -97.0], 4);

    // Three swappable basemaps exposed via Leaflet's layer control. Esri's
    // World_Imagery and Reference/Boundaries layers require no API key;
    // OSM is the road default.
    var roadLayer = L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        { maxZoom: 19, attribution: '© OpenStreetMap' });
    var satelliteLayer = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/' +
        'MapServer/tile/{z}/{y}/{x}',
        { maxZoom: 19, attribution: 'Tiles © Esri' });
    var labelsOverlay = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/' +
        'World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        { maxZoom: 19, attribution: 'Labels © Esri' });
    var hybridLayer = L.layerGroup([satelliteLayer, labelsOverlay]);

    roadLayer.addTo(map);
    L.control.layers(
        { 'Road': roadLayer, 'Satellite': satelliteLayer, 'Hybrid': hybridLayer },
        {},
        { position: 'topright', collapsed: true }
    ).addTo(map);

    var markers = {};
    var bounds = null;
    var aircraft = {};     // feed_id -> L.marker
    var tracks = {};       // feed_id -> L.polyline
    var follow = true;     // keep the newest aircraft fix in view
    var hasAutoCentered = false;

    function pinIcon(color) {
        return L.divIcon({
            className: '',
            html: '<div class="adiat-pin" style="background:' + color + '"></div>',
            iconSize: [18, 18],
            iconAnchor: [9, 9],
        });
    }
    function aircraftIcon(heading, color) {
        // The CSS triangle points north; rotate it to the reported bearing.
        var rot = (typeof heading === 'number') ? heading : 0;
        return L.divIcon({
            className: '',
            html: '<div class="adiat-aircraft" style="border-bottom-color:' +
                  (color || '#00E5FF') + ';transform: rotate(' + rot + 'deg)"></div>',
            iconSize: [16, 20],
            iconAnchor: [8, 10],
        });
    }

    window.addMarker = function(lat, lon, label, key, color) {
        if (key && markers[key]) { map.removeLayer(markers[key]); }
        var m = L.marker([lat, lon], { icon: pinIcon(color || '#9C27B0') })
            .addTo(map);
        if (label) { m.bindPopup(label); }
        if (key && window.qt_pinClicked) {
            m.on('click', function() { window.qt_pinClicked(key); });
        }
        if (key) { markers[key] = m; }
        if (bounds === null) { bounds = L.latLngBounds([lat, lon], [lat, lon]); }
        else { bounds.extend([lat, lon]); }
    };
    window.fitAll = function() {
        if (bounds !== null) {
            // ``maxZoom: 18`` keeps multi-detection sessions from zooming to
            // an extreme overhead view when all pins land within meters.
            map.fitBounds(bounds, { padding: [30, 30], maxZoom: 18 });
        }
    };
    window.setView = function(lat, lon, zoom) {
        map.setView([lat, lon], zoom !== undefined ? zoom : 18);
    };
    window.clearMarkers = function() {
        for (var k in markers) { map.removeLayer(markers[k]); }
        markers = {};
        bounds = null;
    };

    window.setFollow = function(enabled) { follow = !!enabled; };

    window.setAircraft = function(key, lat, lon, heading, color, label) {
        key = key || 'default';
        var icon = aircraftIcon(heading, color);
        if (aircraft[key]) {
            aircraft[key].setLatLng([lat, lon]);
            aircraft[key].setIcon(icon);
        } else {
            aircraft[key] = L.marker([lat, lon], {
                icon: icon, zIndexOffset: 1000
            }).addTo(map);
        }
        if (label) { aircraft[key].bindTooltip(label, { direction: 'top' }); }
        // First fix centres the map; afterwards only pan when following and
        // the aircraft has left the visible area, so the operator can pan
        // away to inspect something without being yanked back every tick.
        if (!hasAutoCentered) {
            hasAutoCentered = true;
            map.setView([lat, lon], 17);
        } else if (follow && !map.getBounds().pad(-0.2).contains([lat, lon])) {
            map.panTo([lat, lon]);
        }
    };

    window.appendTrack = function(key, lat, lon, color) {
        key = key || 'default';
        if (!tracks[key]) {
            tracks[key] = L.polyline([], {
                color: color || '#00E5FF', weight: 3, opacity: 0.75
            }).addTo(map);
        }
        tracks[key].addLatLng([lat, lon]);
    };

    window.setTrack = function(key, pointsJson, color) {
        key = key || 'default';
        var pts = [];
        try { pts = JSON.parse(pointsJson) || []; } catch (e) { pts = []; }
        if (!tracks[key]) {
            tracks[key] = L.polyline([], {
                color: color || '#00E5FF', weight: 3, opacity: 0.75
            }).addTo(map);
        }
        tracks[key].setLatLngs(pts);
    };

    window.clearTrack = function(key) {
        if (key) {
            if (tracks[key]) { map.removeLayer(tracks[key]); delete tracks[key]; }
            return;
        }
        for (var k in tracks) { map.removeLayer(tracks[k]); }
        tracks = {};
    };

    window.clearAircraft = function(key) {
        if (key) {
            if (aircraft[key]) { map.removeLayer(aircraft[key]); delete aircraft[key]; }
            return;
        }
        for (var k in aircraft) { map.removeLayer(aircraft[k]); }
        aircraft = {};
        hasAutoCentered = false;
    };

    // Flush anything that arrived before init.
    for (var i = 0; i < __adiatPendingMarkers.length; i++) {
        var a = __adiatPendingMarkers[i];
        window.addMarker(a[0], a[1], a[2], a[3], a[4]);
    }
    __adiatPendingMarkers = [];
    for (var j = 0; j < __adiatPendingCalls.length; j++) {
        var call = __adiatPendingCalls[j];
        try { window[call[0]].apply(null, call[1]); } catch (e) { }
    }
    __adiatPendingCalls = [];
    if (__adiatPendingView !== null) {
        window.setView(__adiatPendingView[0], __adiatPendingView[1],
                       __adiatPendingView[2]);
        __adiatPendingView = null;
    } else {
        window.fitAll();
    }
}

if (document.readyState === 'complete') {
    __adiatInitLeaflet();
} else {
    window.addEventListener('load', __adiatInitLeaflet);
}
</script>
</body>
</html>
"""


def _try_import_webengine():
    """Return ``QWebEngineView`` class if available, else ``None``."""
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
    except ImportError:
        return None
    return QWebEngineView


def _try_import_webchannel():
    """Return ``QWebChannel`` class if available, else ``None``.

    ``QtWebChannel`` ships alongside ``QtWebEngine`` in PySide6 — used
    here to bridge Leaflet's pin-click event back to a Qt signal.
    """
    try:
        from PySide6.QtWebChannel import QWebChannel  # type: ignore
    except ImportError:
        return None
    return QWebChannel


class _MapBridge(QObject):
    """Exposed to the embedded page as ``window.adiatBridge``.

    Receives ``pin_clicked`` calls from Leaflet's marker click handler and
    re-emits them as a Qt signal on the owning view.
    """

    def __init__(self, view: "FlightMapView"):
        super().__init__(view)
        self._view = view

    @Slot(str)
    def pin_clicked(self, key: str) -> None:
        self._view.pinClicked.emit(key)


class FlightMapView(TranslationMixin, QWidget):
    """Map widget showing aircraft position, flight path, and detections."""

    rowActivated = Signal(dict)
    pinClicked = Signal(str)  # track_key of the clicked pin

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # ``track_key`` → detection dict; dedups pins from snapshot replays
        # so the map stays consistent with the gallery.
        self._detections: Dict[str, dict] = {}
        # ``feed_id`` → number of fixes appended, so callers can tell an
        # empty trail from one that was never started.
        self._track_lengths: Dict[str, int] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._layout = layout

        self._WebEngineView = _try_import_webengine()
        if self._WebEngineView is not None:
            self._setup_web_view()
        else:
            self._setup_fallback_view()

    # ------------------------------------------------------------------
    # mode A: interactive Leaflet view
    # ------------------------------------------------------------------

    def _setup_web_view(self) -> None:
        view_cls = self._WebEngineView
        assert view_cls is not None  # for type-checkers
        self._view = view_cls(self)

        # Bridge Leaflet pin clicks back to Qt. ``QtWebChannel`` ships with
        # ``QtWebEngine`` in PySide6, but tolerate it being absent — pin
        # colours and popups still work without the bridge.
        channel_cls = _try_import_webchannel()
        bridge_setup_js = ""
        if channel_cls is not None:
            from PySide6.QtWebChannel import QWebChannel  # type: ignore

            self._bridge = _MapBridge(self)
            self._channel = QWebChannel(self._view.page())
            self._channel.registerObject("adiatBridge", self._bridge)
            self._view.page().setWebChannel(self._channel)
            bridge_setup_js = """
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <script>
            new QWebChannel(qt.webChannelTransport, function(channel) {
                var bridge = channel.objects.adiatBridge;
                window.qt_pinClicked = function(key) { bridge.pin_clicked(key); };
            });
            </script>
            """

        html = LEAFLET_HTML.replace("__ADIAT_LEAFLET_HEAD__", build_leaflet_head())
        html = html.replace("</body>", bridge_setup_js + "</body>")
        self._view.setHtml(html, baseUrl=QUrl("https://signal.adiat.app/map/"))
        self._layout.addWidget(self._view)
        # If an update arrives before the page has loaded, queue it; the
        # ``loadFinished`` signal flushes the queue.
        self._pending_js: List[str] = []
        self._loaded = False
        self._view.loadFinished.connect(self._on_loaded)

    def _on_loaded(self, ok: bool) -> None:
        self._loaded = bool(ok)
        if not self._loaded:
            return
        for js in self._pending_js:
            self._run_js(js)
        self._pending_js = []

    def _run_js(self, js: str) -> None:
        if self._WebEngineView is None:
            return
        if not getattr(self, "_loaded", False):
            # Bounded for the same reason as the JS-side queue: a feed can
            # start producing fixes before the page finishes loading.
            if len(self._pending_js) >= _MAX_PENDING_JS:
                del self._pending_js[0]
            self._pending_js.append(js)
            return
        try:
            self._view.page().runJavaScript(js)
        except Exception:  # noqa: BLE001 - never crash the UI on a JS hiccup
            pass

    # ------------------------------------------------------------------
    # mode B: list-only fallback
    # ------------------------------------------------------------------

    def _setup_fallback_view(self) -> None:
        notice = QLabel(
            self.tr(
                "QtWebEngine not available — install PySide6-Addons for "
                "the interactive map. Showing list view instead."
            )
        )
        notice.setWordWrap(True)
        notice.setStyleSheet("QLabel { color: palette(mid); font-size: 10px; }")
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(4)
        self._layout.addWidget(notice)

        self._fallback_list = QListWidget(self)
        self._fallback_list.itemActivated.connect(self._on_fallback_activated)
        self._layout.addWidget(self._fallback_list, stretch=1)

    def _on_fallback_activated(self, item: QListWidgetItem) -> None:
        detection = item.data(Qt.UserRole)
        if isinstance(detection, dict):
            loc = detection.get("location") or {}
            lat = loc.get("lat")
            lon = loc.get("lon")
            if lat is not None and lon is not None:
                QDesktopServices.openUrl(QUrl(f"geo:{lat},{lon}"))
            self.rowActivated.emit(detection)

    # ------------------------------------------------------------------
    # detections
    # ------------------------------------------------------------------

    def add_detection(self, detection: dict) -> None:
        """Plot (or update) a detection's pin on the map."""
        if not isinstance(detection, dict):
            return
        loc = detection.get("location") or {}
        lat = loc.get("lat")
        lon = loc.get("lon")
        if not _is_coord(lat) or not _is_coord(lon):
            return

        key = str(detection.get("track_key") or f"{lat:.6f},{lon:.6f}")
        self._detections[key] = dict(detection)

        if self._WebEngineView is not None:
            label = detection.get("class_name") or detection.get("detector_id") or ""
            confidence = detection.get("confidence")
            if isinstance(confidence, (int, float)):
                label = f"{label} {float(confidence) * 100:.0f}%"
            detector_id = (
                detection.get("detector_id")
                or detection.get("class_name")
                or ""
            )
            color = DETECTOR_PALETTE.get(str(detector_id), DEFAULT_PIN_COLOR)
            self._run_js(
                f"window.addMarker({float(lat)}, {float(lon)}, "
                f"{json.dumps(str(label))}, {json.dumps(key)}, "
                f"{json.dumps(color)});"
            )
            return

        label = detection.get("class_name") or "?"
        item = QListWidgetItem(f"{label}  ·  {lat:.5f}, {lon:.5f}")
        item.setData(Qt.UserRole, detection)
        self._fallback_list.addItem(item)

    def focus_detection(self, detection: dict) -> None:
        """Center the map (or scroll the list) on a single detection."""
        if not isinstance(detection, dict):
            return
        loc = detection.get("location") or {}
        lat = loc.get("lat")
        lon = loc.get("lon")
        if not _is_coord(lat) or not _is_coord(lon):
            return
        if self._WebEngineView is not None:
            # Zoom 19 on focus — one tighter than the auto-fit default so a
            # row click really hones in on the target.
            self._run_js(f"window.setView({float(lat)}, {float(lon)}, 19);")
            return
        for i in range(self._fallback_list.count()):
            item = self._fallback_list.item(i)
            if item.data(Qt.UserRole) is detection:
                self._fallback_list.setCurrentItem(item)
                self._fallback_list.scrollToItem(item)
                return

    def fit_all(self) -> None:
        """Zoom to include every detection pin plotted so far."""
        self._run_js("window.fitAll && window.fitAll();")

    def clear(self) -> None:
        """Remove detection pins. Aircraft and tracks are left alone."""
        self._detections.clear()
        if self._WebEngineView is not None:
            self._run_js("window.clearMarkers && window.clearMarkers();")
        else:
            self._fallback_list.clear()

    # ------------------------------------------------------------------
    # aircraft position + flight path
    # ------------------------------------------------------------------

    def update_aircraft(
        self,
        envelope: dict,
        *,
        feed_id: str = DEFAULT_FEED_ID,
        label: Optional[str] = None,
        extend_track: bool = True,
    ) -> bool:
        """Move the aircraft marker and extend its trail from a telemetry envelope.

        Args:
            envelope: Telemetry in the shared HUD shape (``aircraft_latitude``,
                ``aircraft_longitude``, ``aircraft_yaw_deg``).
            feed_id: Distinguishes aircraft when several feeds share one map.
            label: Optional tooltip (e.g. the drone's name).
            extend_track: Append this fix to the flight path.

        Returns:
            True when the aircraft was actually plotted. False for an
            envelope without a position, and false in the list-only
            fallback mode where there is no map to plot on — callers use
            this to decide whether to reveal the map.
        """
        if not isinstance(envelope, dict):
            return False
        lat = envelope.get("aircraft_latitude")
        lon = envelope.get("aircraft_longitude")
        if not _is_coord(lat) or not _is_coord(lon):
            return False
        if self._WebEngineView is None:
            return False

        heading = envelope.get("aircraft_yaw_deg")
        heading_js = float(heading) if _is_coord(heading) else 0.0

        self._run_js(
            f"window.setAircraft({json.dumps(feed_id)}, {float(lat)}, {float(lon)}, "
            f"{heading_js}, {json.dumps(AIRCRAFT_COLOR)}, "
            f"{json.dumps(label) if label else 'null'});"
        )
        if extend_track:
            self._run_js(
                f"window.appendTrack({json.dumps(feed_id)}, {float(lat)}, "
                f"{float(lon)}, {json.dumps(AIRCRAFT_COLOR)});"
            )
            self._track_lengths[feed_id] = self._track_lengths.get(feed_id, 0) + 1
        return True

    def set_track(
        self,
        points: Sequence[Tuple[float, float]],
        *,
        feed_id: str = DEFAULT_FEED_ID,
    ) -> None:
        """Replace the whole flight path for ``feed_id``.

        Used when scrubbing a video: the trail must shrink when the operator
        seeks backwards, which appending alone cannot express.
        """
        clean = [
            [float(lat), float(lon)]
            for lat, lon in (points or [])
            if _is_coord(lat) and _is_coord(lon)
        ]
        self._track_lengths[feed_id] = len(clean)
        self._run_js(
            f"window.setTrack({json.dumps(feed_id)}, "
            f"{json.dumps(json.dumps(clean))}, {json.dumps(AIRCRAFT_COLOR)});"
        )

    def set_follow(self, enabled: bool) -> None:
        """Whether the map re-centres when the aircraft leaves the view."""
        self._run_js(f"window.setFollow && window.setFollow({str(bool(enabled)).lower()});")

    def clear_track(self, feed_id: Optional[str] = None) -> None:
        """Erase one feed's flight path, or every path when ``feed_id`` is None."""
        if feed_id is None:
            self._track_lengths.clear()
            self._run_js("window.clearTrack && window.clearTrack(null);")
        else:
            self._track_lengths.pop(feed_id, None)
            self._run_js(f"window.clearTrack && window.clearTrack({json.dumps(feed_id)});")

    def clear_aircraft(self, feed_id: Optional[str] = None) -> None:
        """Remove one aircraft marker, or every marker when ``feed_id`` is None."""
        if feed_id is None:
            self._run_js("window.clearAircraft && window.clearAircraft(null);")
        else:
            self._run_js(
                f"window.clearAircraft && window.clearAircraft({json.dumps(feed_id)});"
            )

    def reset(self) -> None:
        """Clear detections, aircraft, and tracks — a fresh session."""
        self.clear()
        self.clear_aircraft(None)
        self.clear_track(None)

    # ------------------------------------------------------------------
    # accessors
    # ------------------------------------------------------------------

    @property
    def detection_count(self) -> int:
        return len(self._detections)

    def track_length(self, feed_id: str = DEFAULT_FEED_ID) -> int:
        """Fixes currently plotted in ``feed_id``'s flight path."""
        return self._track_lengths.get(feed_id, 0)

    @property
    def is_interactive(self) -> bool:
        """``True`` when the widget is using the Leaflet view."""
        return self._WebEngineView is not None


def _is_coord(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
