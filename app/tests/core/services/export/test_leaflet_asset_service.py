"""Leaflet assets, and the layering rule that moved them here.

``FlightMapHtmlService`` generates an offline map page and needs the same
palette and the same ``<head>`` fragment the live widget uses. It used to
import them from ``core.views.components.FlightMapView`` — a service reaching
into a Qt widget module, which CLAUDE.md 2.1 forbids and which dragged the
widget's Qt imports along behind an export that renders no UI at all.

The vendor-path assertion is the one that earns its keep: the lookup walks a
fixed number of parents from ``__file__``, and moving the module changed how
many. It resolved correctly by coincidence of depth, not by design.
"""

import os
from pathlib import Path

from core.services.export import LeafletAssetService
from core.services.export.LeafletAssetService import (
    AIRCRAFT_COLOR,
    DEFAULT_PIN_COLOR,
    DETECTOR_PALETTE,
    build_leaflet_head,
    load_leaflet_assets,
)


def test_the_vendor_directory_resolves_from_this_modules_location():
    """The parents[] depth must match where the module actually lives."""
    vendor = LeafletAssetService._vendor_dir()

    assert vendor.name == 'leaflet'
    assert vendor.parent.name == 'vendor'
    assert vendor.parent.parent.name == 'resources'
    # And it is the repo's own copy, not a path that happens to be shaped right.
    repo_root = Path(__file__).resolve().parents[5]
    assert vendor == repo_root / 'resources' / 'vendor' / 'leaflet'


def test_the_vendored_assets_load():
    css, js = load_leaflet_assets()

    assert css and js, "resources/vendor/leaflet is missing or empty"
    assert 'leaflet' in css.lower()


def test_the_head_prefers_the_vendored_copy_over_the_cdn():
    """A CDN blip used to replace the whole map with an error for the rest of
    the session, with no retry."""
    head = build_leaflet_head()

    assert 'unpkg.com' not in head
    assert '<style>' in head and '<script>' in head


def test_css_image_urls_are_inlined():
    """Leaflet's stylesheet points at its icons relatively; served from our
    own page those 404'd and silently blanked the basemap selector."""
    css, _js = load_leaflet_assets()

    assert 'url(images/' not in css
    assert 'data:image/png;base64,' in css


def test_the_service_imports_no_qt():
    """The whole point of the move. Read the source rather than the loaded
    module: something else in the test session has Qt imported already."""
    source_path = LeafletAssetService.__file__
    with open(source_path, encoding='utf-8') as handle:
        lines = [line for line in handle if line.startswith(('import ', 'from '))]

    assert not [line for line in lines if 'PySide6' in line]
    assert not [line for line in lines if 'core.views' in line]


def test_the_widget_still_exports_the_names_its_callers_import():
    """Re-exported for compatibility; the widget's callers never had to know
    these moved."""
    from core.views.components import FlightMapView

    assert FlightMapView.DETECTOR_PALETTE is DETECTOR_PALETTE
    assert FlightMapView.DEFAULT_PIN_COLOR == DEFAULT_PIN_COLOR
    assert FlightMapView.AIRCRAFT_COLOR == AIRCRAFT_COLOR
    assert FlightMapView.build_leaflet_head is build_leaflet_head


def test_the_exporter_no_longer_imports_the_view():
    """Import lines only - the module's prose legitimately mentions the
    widget it produces a shareable alternative to."""
    from core.services.export import FlightMapHtmlService

    with open(FlightMapHtmlService.__file__, encoding='utf-8') as handle:
        imports = [line for line in handle
                   if line.startswith(('import ', 'from '))]

    assert not [line for line in imports if 'core.views' in line]
    assert [line for line in imports if 'LeafletAssetService' in line]


def test_the_palette_matches_the_publisher_side_vocabulary():
    """These ids come off the wire; a rename here silently changes pin
    colours rather than failing."""
    assert set(DETECTOR_PALETTE) == {
        'person', 'color-range', 'motion', 'dji-native'}
    # The aircraft is deliberately outside the palette so it can never be
    # mistaken for a detection.
    assert AIRCRAFT_COLOR not in DETECTOR_PALETTE.values()
    assert DEFAULT_PIN_COLOR not in DETECTOR_PALETTE.values()


def test_asset_loading_is_cached():
    """Reading and base64-inlining ~160 KB on every map open was worth
    avoiding."""
    assert load_leaflet_assets() is load_leaflet_assets()
    assert os.path.exists(LeafletAssetService.__file__)
