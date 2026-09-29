"""Tests for map layer registry: topo base + roads/MVUM/trails overlays."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

from core.views.images.viewer.widgets.MapTileLoader import (
    MapTileLoader,
    BASE_SOURCES,
    OVERLAY_SOURCES,
    WEB_MERCATOR_HALF_WORLD_M,
)
from core.views.images.viewer.widgets.GPSMapView import GPSMapView, OVERLAY_LAYER_Z


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def _loader(tmp_path, source, offline=False):
    loader = MapTileLoader(offline_only=offline)
    loader.cache_dir = tmp_path  # isolate from the shared disk cache
    loader.set_tile_source(source)
    return loader


# ---------------------------------------------------------------------------
# Registry and URL construction
# ---------------------------------------------------------------------------

def test_registry_covers_expected_sources():
    assert set(BASE_SOURCES) == {'map', 'satellite', 'topo'}
    assert set(OVERLAY_SOURCES) == {'roads', 'mvum', 'trails', 'usfs_trails'}
    assert set(OVERLAY_LAYER_Z) == set(OVERLAY_SOURCES)


@pytest.mark.parametrize("source,fragment", [
    ('map', "tile.openstreetmap.org/12/700/1583.png"),
    ('satellite', "World_Imagery/MapServer/tile/12/1583/700"),
    ('topo', "tile.opentopomap.org/12/700/1583.png"),
    ('roads', "Reference/World_Transportation/MapServer/tile/12/1583/700"),
    ('trails', "tile.waymarkedtrails.org/hiking/12/700/1583.png"),
])
def test_tile_url_templates(tmp_path, source, fragment):
    loader = _loader(tmp_path, source)
    assert fragment in loader.tile_url(700, 1583, 12)


@pytest.mark.parametrize("source,service", [
    ('mvum', "EDW/EDW_MVUM_01/MapServer/export"),
    ('usfs_trails', "EDW/EDW_TrailNFSPublish_01/MapServer/export"),
])
def test_export_sources_render_via_bbox(tmp_path, source, service):
    loader = _loader(tmp_path, source)
    url = loader.tile_url(0, 0, 1)
    assert service in url
    assert "bboxSR=3857" in url
    assert "transparent=true" in url
    assert "format=png32" in url
    assert f"size={loader.tile_size},{loader.tile_size}" in url
    # Tile (0, 0) at zoom 1 is the world's north-west quadrant
    assert f"bbox={-WEB_MERCATOR_HALF_WORLD_M},0.0,0.0,{WEB_MERCATOR_HALF_WORLD_M}" in url


def test_tile_bounds_3857_quadrants(tmp_path):
    loader = _loader(tmp_path, 'mvum')
    half = WEB_MERCATOR_HALF_WORLD_M
    assert loader.tile_bounds_3857(0, 0, 1) == (-half, 0.0, 0.0, half)
    assert loader.tile_bounds_3857(1, 1, 1) == (0.0, -half, half, 0.0)


def test_is_overlay_classification():
    assert MapTileLoader.is_overlay('mvum')
    assert MapTileLoader.is_overlay('trails')
    assert not MapTileLoader.is_overlay('map')
    assert not MapTileLoader.is_overlay('topo')


@pytest.mark.parametrize("source,expected", [
    ('map', 19), ('satellite', 20), ('topo', 17), ('trails', 18), ('mvum', 22),
])
def test_max_zoom_per_source(tmp_path, source, expected):
    assert _loader(tmp_path, source).max_zoom() == expected


# ---------------------------------------------------------------------------
# Overlay failure semantics: transparent, never gray, no ancestor fallback
# ---------------------------------------------------------------------------

def test_offline_uncached_overlay_emits_transparent_placeholder(app, tmp_path):
    """An offline overlay miss is a transparent PLACEHOLDER, not imagery: it
    arrives on its own channel so consumers never cache the failure as a
    legitimate empty tile (the bug that left overlays blank after
    connectivity returned)."""
    loader = _loader(tmp_path, 'trails', offline=True)
    tiles, placeholders, errors = [], [], []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append(pm))
    loader.tile_placeholder.connect(lambda x, y, z, pm: placeholders.append(pm))
    loader.tile_error.connect(errors.append)

    loader.load_tile(5, 6, 10)

    assert tiles == [], "a failed fetch must never masquerade as a loaded tile"
    assert len(placeholders) == 1
    assert errors == [], "a missing overlay tile is not an error condition"
    image = placeholders[0].toImage()
    assert image.pixelColor(128, 128).alpha() == 0


def test_cached_transparent_overlay_tile_served_verbatim(app, tmp_path):
    # A fully transparent tile is uniform - the base-layer placeholder
    # heuristic would replace it with an ancestor crop; overlays must not.
    transparent = QPixmap(256, 256)
    transparent.fill(Qt.transparent)
    transparent.save(str(tmp_path / "trails_10_5_6.png"))
    loader = _loader(tmp_path, 'trails', offline=True)
    tiles = []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append(pm))

    loader.load_tile(5, 6, 10)

    assert len(tiles) == 1
    assert tiles[0].toImage().pixelColor(10, 10).alpha() == 0


def test_offline_uncached_base_still_reports_and_grays(app, tmp_path):
    loader = _loader(tmp_path, 'topo', offline=True)
    tiles, errors = [], []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append(pm))
    loader.tile_error.connect(errors.append)

    loader.load_tile(5, 6, 10)

    assert len(tiles) == 1
    assert len(errors) == 1
    assert tiles[0].toImage().pixelColor(128, 128).alpha() == 255


# ---------------------------------------------------------------------------
# GPSMapView overlay layer management
# ---------------------------------------------------------------------------

def _tile(alpha=0):
    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.transparent if alpha == 0 else Qt.red)
    return pixmap


def test_set_overlays_creates_named_offline_aware_loaders(app):
    view = GPSMapView(offline_only=True)
    view.set_overlays(['mvum', 'trails', 'bogus'])

    assert view.active_overlays == ['mvum', 'trails']
    assert view.overlay_loaders['mvum'].tile_source == 'mvum'
    assert view.overlay_loaders['trails'].tile_source == 'trails'
    assert view.overlay_loaders['mvum'].offline_only is True


def test_overlay_tiles_sit_between_base_and_pod(app):
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['trails'])

    view._on_overlay_tile_loaded('trails', 100, 200, 12, _tile())

    item = view.overlay_tile_items['trails'][(100, 200, 12)]
    assert item.scene() is view.scene
    assert item.zValue() == OVERLAY_LAYER_Z['trails']
    assert -100 < item.zValue() < -50


def test_overlay_tile_for_other_zoom_is_cached_not_placed(app):
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['mvum'])

    view._on_overlay_tile_loaded('mvum', 1, 2, 9, _tile())

    assert (1, 2, 9) not in view.overlay_tile_items.get('mvum', {})
    assert (1, 2, 9, 'mvum') in view.all_tile_items


def test_tile_for_inactive_overlay_is_dropped(app):
    view = GPSMapView()
    view.current_zoom = 12
    view._on_overlay_tile_loaded('trails', 1, 2, 12, _tile())
    assert view.overlay_tile_items.get('trails', {}) == {}


def test_disabling_overlay_removes_its_tiles(app):
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['trails', 'mvum'])
    view._on_overlay_tile_loaded('trails', 1, 2, 12, _tile())
    view._on_overlay_tile_loaded('mvum', 1, 2, 12, _tile())

    view.set_overlays(['mvum'])

    assert view.overlay_tile_items['trails'] == {}
    assert (1, 2, 12) in view.overlay_tile_items['mvum']
    assert view.active_overlays == ['mvum']


def test_zoom_level_change_drops_overlay_tiles(app):
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['roads'])
    view._on_overlay_tile_loaded('roads', 1, 2, 12, _tile())

    view._change_tile_zoom_level(13)

    assert view.overlay_tile_items['roads'] == {}


def test_set_offline_mode_fans_out_to_overlay_loaders(app):
    view = GPSMapView(offline_only=False)
    view.set_overlays(['trails'])
    view.set_offline_mode(True)
    assert view.tile_loader.offline_only is True
    assert view.overlay_loaders['trails'].offline_only is True


# ---------------------------------------------------------------------------
# PR #149 review regression (B6): overlay fetch failures must be retryable,
# never cached as imagery.
# ---------------------------------------------------------------------------

def test_b6_failed_overlay_tile_is_not_cached_as_imagery(app):
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['trails'])

    view._on_overlay_tile_placeholder('trails', 1, 2, 12)

    assert (1, 2, 12, 'trails') not in view.all_tile_items
    assert (1, 2, 12) not in view.overlay_tile_items.get('trails', {})
    assert (1, 2, 12) in view.overlay_failed_tiles['trails']


def test_b6_layer_toggle_clears_failures_and_refetches(app):
    """Offline miss -> online -> layer toggle must cause a real fetch: the
    toggle forgets the failure, and the next visible sweep asks the loader."""
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['trails'])
    view._on_overlay_tile_placeholder('trails', 1, 2, 12)

    view.set_overlays([])                 # toggle off
    view.set_overlays(['trails'])         # toggle back on
    assert view.overlay_failed_tiles['trails'] == set()

    requests = []
    view.overlay_loaders['trails'].load_tile = (
        lambda x, y, z: requests.append((x, y, z)))
    view.overlay_tile_items['trails'] = {}
    # Sweep the exact tile through the overlay loop.
    view.overlay_failed_tiles.setdefault('trails', set())
    for name in view.active_overlays:
        loader = view.overlay_loaders.get(name)
        items = view.overlay_tile_items.setdefault(name, {})
        failed = view.overlay_failed_tiles.setdefault(name, set())
        key = (1, 2, 12)
        if key not in items and key not in failed and \
                (1, 2, 12, name) not in view.all_tile_items:
            loader.load_tile(1, 2, 12)
    assert (1, 2, 12) in requests


def test_b6_success_after_failure_replaces_the_blank(app):
    """HTTP failure followed by success: the later real tile renders and the
    failure record is cleared."""
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['trails'])
    view._on_overlay_tile_placeholder('trails', 1, 2, 12)
    assert (1, 2, 12) in view.overlay_failed_tiles['trails']

    view._on_overlay_tile_loaded('trails', 1, 2, 12, _tile())

    assert (1, 2, 12) not in view.overlay_failed_tiles['trails']
    assert (1, 2, 12) in view.overlay_tile_items['trails']
    assert (1, 2, 12, 'trails') in view.all_tile_items


def test_b6_genuinely_empty_successful_tile_stays_cached(app):
    """A transparent tile delivered as a SUCCESS (the server really has no
    trail there) is legitimate imagery and remains cached."""
    view = GPSMapView()
    view.current_zoom = 12
    view.set_overlays(['trails'])
    transparent = QPixmap(256, 256)
    transparent.fill(Qt.transparent)

    view._on_overlay_tile_loaded('trails', 1, 2, 12, transparent)

    assert (1, 2, 12, 'trails') in view.all_tile_items
    assert view.overlay_failed_tiles.get('trails', set()) == set()


# ---------------------------------------------------------------------------
# Source captured at request time (review finding 4, PR #43 follow-up): a
# reply that arrives after the user switched layers must neither be cached
# under the NEW source's name nor displayed in the new layer.
# ---------------------------------------------------------------------------

def _fake_reply_factory(error=None, png_data=None):
    """A finished-signal reply the loader can consume like a QNetworkReply."""
    from PySide6.QtCore import QObject, Signal
    from PySide6.QtNetwork import QNetworkReply

    class Reply(QObject):
        finished = Signal()

        def error(self):
            return error if error is not None else QNetworkReply.NetworkError.NoError

        def errorString(self):
            return "refused"

        def attribute(self, _attr):
            return None

        def readAll(self):
            return png_data

    return Reply()


def _png_bytes(color=Qt.red):
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.WriteOnly)
    tile = QPixmap(32, 32)
    tile.fill(color)
    assert tile.save(buffer, 'PNG')
    buffer.close()
    return data


def test_switching_source_mid_download_never_poisons_the_other_cache(app, tmp_path, monkeypatch):
    """A street-map response arriving after a switch to satellite is cached as
    a MAP tile, not a satellite tile, and is not displayed."""
    from types import SimpleNamespace

    loader = _loader(tmp_path, 'map', offline=False)
    reply = _fake_reply_factory(png_data=_png_bytes())
    loader.network_manager = SimpleNamespace(get=lambda request: reply)
    monkeypatch.setattr(loader, '_looks_unavailable', lambda pixmap: False)
    tiles, placeholders = [], []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append((x, y, z)))
    loader.tile_placeholder.connect(lambda x, y, z, pm: placeholders.append((x, y, z)))

    loader.download_tile(1, 2, 3)  # requested while the source is 'map'
    loader.set_tile_source('satellite')
    reply.finished.emit()  # the original street-map response arrives late

    assert not (tmp_path / 'satellite_3_1_2.png').exists(), \
        'street map saved into the satellite cache'
    assert (tmp_path / 'map_3_1_2.png').exists()
    assert not loader.active_downloads
    assert tiles == [], 'a deselected source must not be displayed'
    assert placeholders == []


def test_download_completing_for_current_source_still_emits(app, tmp_path, monkeypatch):
    from types import SimpleNamespace

    loader = _loader(tmp_path, 'map', offline=False)
    reply = _fake_reply_factory(png_data=_png_bytes())
    loader.network_manager = SimpleNamespace(get=lambda request: reply)
    monkeypatch.setattr(loader, '_looks_unavailable', lambda pixmap: False)
    tiles = []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append((x, y, z)))

    loader.download_tile(1, 2, 3)
    reply.finished.emit()

    assert tiles == [(1, 2, 3)]
    assert (tmp_path / 'map_3_1_2.png').exists()
    assert not loader.active_downloads


def test_switching_away_and_back_before_completion_still_displays(app, tmp_path, monkeypatch):
    from types import SimpleNamespace

    loader = _loader(tmp_path, 'map', offline=False)
    reply = _fake_reply_factory(png_data=_png_bytes())
    loader.network_manager = SimpleNamespace(get=lambda request: reply)
    monkeypatch.setattr(loader, '_looks_unavailable', lambda pixmap: False)
    tiles = []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append((x, y, z)))

    loader.download_tile(1, 2, 3)
    loader.set_tile_source('satellite')
    loader.set_tile_source('map')  # back before the reply lands
    reply.finished.emit()

    assert tiles == [(1, 2, 3)]


def test_stale_source_error_never_grays_the_new_layer(app, tmp_path):
    """A late FAILURE for the old source must not paint a gray tile (or a
    fallback crop) into the layer the user is looking at now, and the failure
    is remembered under the ORIGINAL source's key."""
    from types import SimpleNamespace
    from PySide6.QtNetwork import QNetworkReply

    loader = _loader(tmp_path, 'map', offline=False)
    reply = _fake_reply_factory(error=QNetworkReply.NetworkError.ConnectionRefusedError)
    loader.network_manager = SimpleNamespace(get=lambda request: reply)
    tiles, placeholders = [], []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append((x, y, z)))
    loader.tile_placeholder.connect(lambda x, y, z, pm: placeholders.append((x, y, z)))

    loader.download_tile(1, 2, 3)
    loader.set_tile_source('satellite')
    reply.finished.emit()

    assert tiles == []
    assert placeholders == []
    assert (1, 2, 3, 'map') in loader._fallback_failed
    assert (1, 2, 3, 'satellite') not in loader._fallback_failed
    assert not loader.active_downloads


def test_b6_online_error_emits_placeholder_channel(app, tmp_path):
    """The download-error path emits on tile_placeholder, not tile_loaded, so
    consumers cannot mistake the failure for a served tile."""
    from unittest.mock import MagicMock
    from PySide6.QtNetwork import QNetworkReply

    loader = _loader(tmp_path, 'trails', offline=False)
    tiles, placeholders = [], []
    loader.tile_loaded.connect(lambda x, y, z, pm: tiles.append((x, y, z)))
    loader.tile_placeholder.connect(lambda x, y, z, pm: placeholders.append((x, y, z)))

    reply = MagicMock()
    reply.error.return_value = QNetworkReply.NetworkError.ConnectionRefusedError
    reply.errorString.return_value = "refused"
    reply.attribute.return_value = None
    loader.on_tile_downloaded(reply, 5, 6, 10)

    assert placeholders == [(5, 6, 10)]
    assert tiles == []
