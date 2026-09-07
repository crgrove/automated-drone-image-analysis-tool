"""Tests for the reusable map view's aircraft marker and flight path.

The Leaflet page runs in QtWebEngine, so these tests assert on the
JavaScript the widget *emits* rather than on rendered pixels — the same
approach the existing MapDock tests take. JS is captured by stubbing
``_run_js``.
"""

import json
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from core.views.components.FlightMapView import (
    AIRCRAFT_COLOR,
    DEFAULT_FEED_ID,
    FlightMapView,
)


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def view(qtbot):
    widget = FlightMapView()
    qtbot.addWidget(widget)
    calls = []
    widget._run_js = calls.append          # capture instead of execute
    widget.js_calls = calls
    return widget


def envelope(lat=30.5, lon=-97.7, yaw=90.0):
    return {
        "aircraft_latitude": lat,
        "aircraft_longitude": lon,
        "aircraft_yaw_deg": yaw,
    }


class TestConstruction:
    def test_constructs_in_either_mode(self, qtbot):
        widget = FlightMapView()
        qtbot.addWidget(widget)
        assert isinstance(widget.is_interactive, bool)
        assert widget.detection_count == 0
        assert widget.track_length() == 0


class TestAircraftMarker:
    def test_emits_set_aircraft(self, view):
        assert view.update_aircraft(envelope()) is True
        js = " ".join(view.js_calls)
        assert "window.setAircraft(" in js
        assert "30.5" in js and "-97.7" in js

    def test_passes_heading_through(self, view):
        view.update_aircraft(envelope(yaw=137.0))
        assert "137.0" in " ".join(view.js_calls)

    def test_missing_heading_defaults_to_zero(self, view):
        view.update_aircraft({"aircraft_latitude": 1.0, "aircraft_longitude": 2.0})
        aircraft_js = [c for c in view.js_calls if "setAircraft" in c][0]
        assert "0.0" in aircraft_js

    def test_uses_the_aircraft_colour(self, view):
        view.update_aircraft(envelope())
        assert AIRCRAFT_COLOR in " ".join(view.js_calls)

    def test_rejects_envelope_without_position(self, view):
        assert view.update_aircraft({"aircraft_yaw_deg": 90.0}) is False
        assert view.js_calls == []

    def test_rejects_non_dict(self, view):
        assert view.update_aircraft(None) is False
        assert view.update_aircraft("nope") is False

    def test_label_is_json_encoded(self, view):
        view.update_aircraft(envelope(), label='Drone "A"')
        assert json.dumps('Drone "A"') in " ".join(view.js_calls)

    def test_feed_id_keys_the_marker(self, view):
        view.update_aircraft(envelope(), feed_id="ABC234")
        assert '"ABC234"' in " ".join(view.js_calls)


class TestFlightPath:
    def test_appends_by_default(self, view):
        view.update_aircraft(envelope())
        assert any("appendTrack" in c for c in view.js_calls)
        assert view.track_length() == 1

    def test_append_can_be_suppressed(self, view):
        """File playback replaces the trail instead of appending."""
        view.update_aircraft(envelope(), extend_track=False)
        assert not any("appendTrack" in c for c in view.js_calls)
        assert view.track_length() == 0

    def test_track_length_accumulates(self, view):
        for i in range(3):
            view.update_aircraft(envelope(lat=30.0 + i))
        assert view.track_length() == 3

    def test_set_track_replaces(self, view):
        view.set_track([(30.0, -97.0), (30.1, -97.1)])
        assert view.track_length() == 2
        js = [c for c in view.js_calls if "setTrack" in c][0]
        assert "30.0" in js and "-97.1" in js

    def test_set_track_shorter_shrinks(self, view):
        """Seeking backwards must shorten the plotted trail."""
        view.set_track([(30.0, -97.0)] * 5)
        assert view.track_length() == 5
        view.set_track([(30.0, -97.0)] * 2)
        assert view.track_length() == 2

    def test_set_track_filters_bad_points(self, view):
        view.set_track([(30.0, -97.0), (None, -97.1), ("x", 1), (30.2, -97.2)])
        assert view.track_length() == 2

    def test_set_track_empty(self, view):
        view.set_track([])
        assert view.track_length() == 0

    def test_clear_track_for_one_feed(self, view):
        view.update_aircraft(envelope(), feed_id="A")
        view.update_aircraft(envelope(), feed_id="B")
        view.clear_track("A")
        assert view.track_length("A") == 0
        assert view.track_length("B") == 1

    def test_clear_all_tracks(self, view):
        view.update_aircraft(envelope(), feed_id="A")
        view.update_aircraft(envelope(), feed_id="B")
        view.clear_track(None)
        assert view.track_length("A") == 0
        assert view.track_length("B") == 0


class TestMultiFeed:
    def test_two_feeds_track_independently(self, view):
        view.update_aircraft(envelope(lat=30.0), feed_id="ABC234")
        view.update_aircraft(envelope(lat=31.0), feed_id="XYZ789")
        view.update_aircraft(envelope(lat=30.1), feed_id="ABC234")

        assert view.track_length("ABC234") == 2
        assert view.track_length("XYZ789") == 1

    def test_default_feed_id(self, view):
        view.update_aircraft(envelope())
        assert view.track_length(DEFAULT_FEED_ID) == 1


class TestDetections:
    def test_add_detection_counts(self, view):
        view.add_detection({
            "track_key": "t1",
            "location": {"lat": 30.0, "lon": -97.0},
            "class_name": "person",
        })
        assert view.detection_count == 1

    def test_dedupes_by_track_key(self, view):
        for _ in range(3):
            view.add_detection({
                "track_key": "t1",
                "location": {"lat": 30.0, "lon": -97.0},
            })
        assert view.detection_count == 1

    def test_skips_missing_location(self, view):
        view.add_detection({"track_key": "t1"})
        assert view.detection_count == 0

    def test_ignores_non_dict(self, view):
        view.add_detection(None)
        view.add_detection("nope")
        assert view.detection_count == 0


class TestReset:
    def test_reset_clears_everything(self, view):
        view.add_detection({"track_key": "t1", "location": {"lat": 1.0, "lon": 2.0}})
        view.update_aircraft(envelope())
        view.reset()

        assert view.detection_count == 0
        assert view.track_length() == 0
        js = " ".join(view.js_calls)
        assert "clearAircraft" in js and "clearTrack" in js

    def test_clear_keeps_the_aircraft(self, view):
        """Clearing detection pins must not drop the aircraft trail."""
        view.update_aircraft(envelope())
        view.clear()
        assert view.track_length() == 1


class TestMapDockDelegation:
    """MapDock's public surface must stay intact after the extraction."""

    def test_dock_forwards_aircraft_updates(self, qtbot):
        from core.views.flight.MapDock import MapDock

        dock = MapDock()
        qtbot.addWidget(dock)
        calls = []
        dock.map_view._run_js = calls.append

        assert dock.update_aircraft(envelope(), feed_id="ABC234") is True
        assert dock.track_length("ABC234") == 1
        assert any("setAircraft" in c for c in calls)

    def test_dock_still_exposes_detection_api(self, qtbot):
        from core.views.flight.MapDock import MapDock

        dock = MapDock()
        qtbot.addWidget(dock)
        dock.add_detection({"track_key": "t1", "location": {"lat": 1.0, "lon": 2.0}})
        assert dock.detection_count == 1
        dock.clear()
        assert dock.detection_count == 0

    def test_dock_re_exports_legacy_symbols(self):
        """Anything importing these from MapDock must keep working."""
        from core.views.flight import MapDock as module

        assert module.LEAFLET_HTML
        assert module.DETECTOR_PALETTE["person"]
        assert module.DEFAULT_PIN_COLOR


class TestVendoredLeaflet:
    """Leaflet ships with the app rather than being fetched at runtime.

    Pulling it from unpkg.com meant a single transient failure — a DNS
    blip, or the request racing QtWebEngine's network service during app
    startup — replaced the whole widget with an error message for the
    rest of the session, with no retry. ADIAT runs in the field on
    marginal connectivity, so the library must not be on the critical
    path of opening a map.
    """

    def test_assets_are_present_in_the_repo(self):
        from core.views.components.FlightMapView import load_leaflet_assets

        css, js = load_leaflet_assets()
        assert css and js, "vendored Leaflet is missing from resources/vendor/leaflet"
        assert "leaflet" in css.lower()
        assert "Leaflet" in js

    def test_page_inlines_the_library_and_hits_no_cdn(self):
        from core.views.components.FlightMapView import build_leaflet_head

        head = build_leaflet_head()
        assert "unpkg.com" not in head
        assert "<script>" in head and "<style>" in head
        # The real library, not a stub.
        assert len(head) > 100_000

    def test_rendered_page_has_no_cdn_reference(self, view):
        from core.views.components.FlightMapView import (
            LEAFLET_HTML, build_leaflet_head,
        )

        page = LEAFLET_HTML.replace("__ADIAT_LEAFLET_HEAD__", build_leaflet_head())
        assert "__ADIAT_LEAFLET_HEAD__" not in page
        assert "unpkg.com/leaflet" not in page

    def test_falls_back_to_the_cdn_when_vendored_files_are_missing(self):
        """A checkout or build without the vendor dir must still work.

        Patched on the service, not on the widget: the loader moved there so
        the offline-map exporter could use it without importing a Qt widget,
        and the widget only re-exports the name.
        """
        from core.services.export import LeafletAssetService as module

        module.load_leaflet_assets.cache_clear()
        try:
            with patch.object(module, "load_leaflet_assets", return_value=(None, None)):
                head = module.build_leaflet_head()
            assert "unpkg.com" in head
            assert "leaflet.js" in head
        finally:
            module.load_leaflet_assets.cache_clear()

    def test_script_close_tags_are_escaped(self):
        """A literal </script> in the payload would close the tag early."""
        from core.services.export import LeafletAssetService as module

        module.load_leaflet_assets.cache_clear()
        try:
            with patch.object(module, "load_leaflet_assets",
                              return_value=("body{}", "var x='</script>';")):
                head = module.build_leaflet_head()
            assert r"'<\/script>'" in head
            # Exactly one real closing tag: the one we emit.
            assert head.count("</script>") == 1
        finally:
            module.load_leaflet_assets.cache_clear()

    def test_css_images_are_inlined_as_data_uris(self):
        """Regression: the basemap selector lost its icon.

        Leaflet's stylesheet points at ``url(images/layers.png)``
        relatively. From a CDN that resolved next to the stylesheet, but
        inlined into our page it resolves against the page base URL and
        404s, leaving the control a blank white box.
        """
        from core.views.components.FlightMapView import load_leaflet_assets

        css, _js = load_leaflet_assets()
        assert "url(images/" not in css, "relative image URL would 404"
        assert css.count("url(data:image/png;base64,") == 3

    def test_missing_image_leaves_its_url_untouched(self):
        """A partial vendor dir must not corrupt the stylesheet."""
        import tempfile
        from pathlib import Path
        from core.services.export.LeafletAssetService import (
            _inline_css_images,
        )

        with tempfile.TemporaryDirectory() as tmp:
            css = ".a{background-image:url(images/nope.png)}"
            assert _inline_css_images(css, Path(tmp)) == css
