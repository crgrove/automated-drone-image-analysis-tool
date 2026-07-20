"""Map dock for the Flight Viewer (plan §15 M3).

Renders detection locations on an interactive map alongside the
Mission Gallery. Clicking a row in the gallery centers the map on
the corresponding pin (plan §15 — "Map widget for detection locations
(single dock; clicking a row centers the map)").

The dock has two modes:

* **Interactive (Leaflet via QtWebEngine).** If ``PySide6.QtWebEngineWidgets``
  imports successfully, the dock embeds a tiny HTML page with Leaflet and
  OpenStreetMap tiles. Markers are pushed by calling
  :meth:`add_detection`; the map auto-fits to the latest set, and
  :meth:`focus_detection` re-centers without changing the marker set.
* **Fallback (no QtWebEngine).** Replaced with a plain ``QListWidget`` of
  ``class · lat,lon · "Open in browser"`` rows that the operator can use
  to deep-link out to a system map app. Functional but visually minimal —
  exists so the dock degrades gracefully on environments where
  ``QtWebEngine`` isn't installed.
"""

from __future__ import annotations

import json
from typing import Dict, Optional

from PySide6.QtCore import Qt, QUrl, Signal, Slot, QObject
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from helpers.TranslationMixin import TranslationMixin


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


# HTML template loaded into the embedded view. Pulls Leaflet from a CDN
# (operator must have internet for tiles anyway) and exposes three JS
# functions on ``window``: ``addMarker(lat, lon, label, key, color)``,
# ``setView(lat, lon, zoom)``, ``clearMarkers()``. Pin click events fire
# ``window.qt_pinClicked(key)`` (a Python-injected callback) so the desktop
# can highlight the matching Mission Gallery row (plan §19.4.4).
LEAFLET_HTML = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        crossorigin="anonymous"></script>
<style>
html, body, #map { height: 100%; margin: 0; padding: 0; background: #1e1e1e; }
.leaflet-container { background: #1e1e1e; }
.adiat-pin {
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid #fff;
    box-shadow: 0 0 4px rgba(0,0,0,0.6);
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
// before the CDN script's network round-trip completes, so the previous
// pattern of inlining ``L.map(...)`` straight under the leaflet.js
// tag could fire while ``L`` was still ``undefined`` ("L is not defined"
// crash in the console). Listening for ``load`` plus an explicit guard
// makes the init resilient to slow CDNs without blocking the UI.
var __adiatPendingMarkers = [];
var __adiatPendingView = null;

// Queue stubs that survive until the real handlers replace them — early
// callers (e.g. ``add_detection`` racing the page load) just buffer.
window.addMarker = function(lat, lon, label, key, color) {
    __adiatPendingMarkers.push([lat, lon, label, key, color]);
};
window.setView = function(lat, lon, zoom) {
    __adiatPendingView = [lat, lon, zoom];
};
window.fitAll = function() { /* no-op until init */ };
window.clearMarkers = function() { __adiatPendingMarkers = []; };

function __adiatInitLeaflet() {
    if (typeof L === 'undefined') {
        // Leaflet failed to load from the CDN — surface a static
        // fallback message instead of leaving the dock blank. Common
        // causes: no internet, captive portal, CDN blocked.
        var el = document.getElementById('map');
        if (el) {
            el.innerHTML = '<div id="leaflet-fallback">' +
                'Map unavailable: could not load Leaflet from unpkg.com.<br>' +
                'Check internet connectivity; pins are still tracked in ' +
                'the Mission Gallery list.</div>';
        }
        return;
    }
    var map = L.map('map', { worldCopyJump: true }).setView([30.0, -97.0], 4);

    // Three swappable basemaps — Road / Satellite / Hybrid — exposed
    // via Leaflet's built-in layer-control widget at the top-right of
    // the map. Esri's World_Imagery and Reference/Boundaries layers
    // require no API key; OSM is the road default.
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
    function pinIcon(color) {
        return L.divIcon({
            className: '',
            html: '<div class="adiat-pin" style="background:' + color + '"></div>',
            iconSize: [18, 18],
            iconAnchor: [9, 9],
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
            // ``maxZoom: 18`` keeps multi-detection sessions from
            // zooming to an extreme overhead view when all pins
            // happen to land within meters of each other.
            map.fitBounds(bounds, { padding: [30, 30], maxZoom: 18 });
        }
    };
    window.setView = function(lat, lon, zoom) {
        // Default zoom 18 — tight enough that the operator immediately
        // sees roof / road context around a SAR target instead of a
        // wide regional view they have to manually zoom into.
        map.setView([lat, lon], zoom !== undefined ? zoom : 18);
    };
    window.clearMarkers = function() {
        for (var k in markers) { map.removeLayer(markers[k]); }
        markers = {};
        bounds = null;
    };
    // Flush anything that arrived before init.
    for (var i = 0; i < __adiatPendingMarkers.length; i++) {
        var a = __adiatPendingMarkers[i];
        window.addMarker(a[0], a[1], a[2], a[3], a[4]);
    }
    __adiatPendingMarkers = [];
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
    here to bridge Leaflet's pin-click event back to the desktop's
    ``pinClicked`` Qt signal (plan §19.4.4).
    """
    try:
        from PySide6.QtWebChannel import QWebChannel  # type: ignore
    except ImportError:
        return None
    return QWebChannel


class _MapBridge(QObject):
    """Tiny QObject exposed to the embedded Leaflet page as ``window.adiatBridge``.

    Receives ``pin_clicked`` calls from Leaflet's marker ``click`` handler
    and re-emits them as a Qt signal on the owning :class:`MapDock`.
    """

    def __init__(self, dock: "MapDock"):
        super().__init__(dock)
        self._dock = dock

    @Slot(str)
    def pin_clicked(self, key: str) -> None:
        self._dock.pinClicked.emit(key)


class MapDock(TranslationMixin, QDockWidget):
    """Single dock widget showing detection pins on a map."""

    rowActivated = Signal(dict)
    pinClicked = Signal(str)  # track_key of the clicked pin (plan §19.4.4)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Map"))
        # ``objectName`` is required for QMainWindow.saveState() / restoreState()
        # to round-trip this dock — without it Qt logs
        # ``QMainWindow::saveState(): 'objectName' not set for QDockWidget``
        # and silently drops the dock's state from the saved layout.
        self.setObjectName("mapDock")
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
            | QDockWidget.DockWidgetClosable
        )

        # ``track_key`` → detection dict; we use this to dedup pins from
        # snapshot replays so the map stays consistent with the gallery.
        self._detections: Dict[str, dict] = {}

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

        # Try to set up the JS→Python bridge via QWebChannel so Leaflet
        # pin clicks reach the desktop. ``QtWebChannel`` ships with
        # ``QtWebEngine`` in PySide6, but we still tolerate it being
        # absent — the pin colours/popups still work without the bridge.
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

        html = LEAFLET_HTML.replace("</body>", bridge_setup_js + "</body>")
        self._view.setHtml(html, baseUrl=QUrl("https://signal.adiat.app/map/"))
        self.setWidget(self._view)
        # If a detection arrives before the page has loaded, queue it; the
        # ``loadFinished`` signal flushes the queue.
        self._pending_js: list[str] = []
        self._loaded = False
        self._view.loadFinished.connect(self._on_loaded)

    def _on_loaded(self, ok: bool) -> None:
        self._loaded = bool(ok)
        if not self._loaded:
            return
        for js in self._pending_js:
            self._run_js(js)
        self._pending_js = []
        # Once the initial backlog is in, fit the view to whatever we have.
        self._run_js("window.fitAll && window.fitAll();")

    def _run_js(self, js: str) -> None:
        if self._WebEngineView is None:
            return
        if not getattr(self, "_loaded", False):
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
        contents = QWidget(self)
        layout = QVBoxLayout(contents)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        notice = QLabel(
            self.tr(
                "QtWebEngine not available — install PySide6-Addons for "
                "the interactive map. Showing list view instead."
            )
        )
        notice.setWordWrap(True)
        notice.setStyleSheet("QLabel { color: palette(mid); font-size: 10px; }")
        layout.addWidget(notice)

        self._fallback_list = QListWidget(contents)
        self._fallback_list.itemActivated.connect(self._on_fallback_activated)
        layout.addWidget(self._fallback_list, stretch=1)

        self.setWidget(contents)

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
    # public API
    # ------------------------------------------------------------------

    def add_detection(self, detection: dict) -> None:
        """Plot (or update) a detection's pin on the map."""
        if not isinstance(detection, dict):
            return
        loc = detection.get("location") or {}
        lat = loc.get("lat")
        lon = loc.get("lon")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            return

        key = str(detection.get("track_key") or f"{lat:.6f},{lon:.6f}")
        self._detections[key] = dict(detection)

        if self._WebEngineView is not None:
            label = detection.get("class_name") or detection.get("detector_id") or ""
            confidence = detection.get("confidence")
            if isinstance(confidence, (int, float)):
                label = f"{label} {float(confidence) * 100:.0f}%"
            # Match the publisher's detector palette (plan §19.4.4).
            detector_id = (
                detection.get("detector_id")
                or detection.get("class_name")
                or ""
            )
            color = DETECTOR_PALETTE.get(str(detector_id), DEFAULT_PIN_COLOR)
            js = (
                f"window.addMarker({float(lat)}, {float(lon)}, "
                f"{json.dumps(str(label))}, {json.dumps(key)}, "
                f"{json.dumps(color)});"
            )
            self._run_js(js)
            return

        # Fallback: list-only row
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
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            return
        if self._WebEngineView is not None:
            # Zoom 19 on focus — one tighter than the auto-fit / setView
            # default so a row-click really hones in on the target.
            self._run_js(f"window.setView({float(lat)}, {float(lon)}, 19);")
            return
        # Fallback: select the matching row
        for i in range(self._fallback_list.count()):
            item = self._fallback_list.item(i)
            if item.data(Qt.UserRole) is detection:
                self._fallback_list.setCurrentItem(item)
                self._fallback_list.scrollToItem(item)
                return

    def clear(self) -> None:
        self._detections.clear()
        if self._WebEngineView is not None:
            self._run_js("window.clearMarkers && window.clearMarkers();")
        else:
            self._fallback_list.clear()

    @property
    def detection_count(self) -> int:
        return len(self._detections)

    @property
    def is_interactive(self) -> bool:
        """``True`` when the dock is using the Leaflet view."""
        return self._WebEngineView is not None
