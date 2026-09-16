"""Offline Only must actually mean offline, on the paths that used to ignore it.

The preference's own tooltip promises "the app skips any network calls
(map tiles, CalTopo exports) and works with cached data only". Several
surfaces honoured that; the Flight Viewer's two did not. Pairing opened a
WebRTC session against ``signal.adiat.app`` and then the publisher, and
the live map pulled OpenStreetMap and Esri tiles into a QtWebEngine page —
both while the operator had been told nothing would leave the machine.

These tests pin the refusals, and pin *how* they refuse: an operator who
cannot connect needs to be told the setting is why, because a blocked
connection and a wrong pairing code look identical from the outside.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.controllers.flight.FlightTileController import FlightTileController  # noqa: E402
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402
from core.views.components import FlightMapView as FlightMapViewModule  # noqa: E402


class _StubSettings:
    """Stands in for SettingsService without touching the user's store."""

    def __init__(self, offline_only):
        self._offline_only = offline_only
        self.reads = []

    def get_bool_setting(self, name, default_value=False):
        self.reads.append(name)
        if name == "OfflineOnly":
            return self._offline_only
        return default_value


class _StubDialog:
    def __init__(self):
        self.code_errors = []
        self.negotiating = []

    def show_code_error(self, message):
        self.code_errors.append(message)

    def show_negotiating(self, detail=None):
        self.negotiating.append(detail)


@pytest.fixture
def controller(qtbot):
    ctrl = FlightTileController(
        signaling=InMemorySignalingChannel(),
        settings_service=_StubSettings(offline_only=True),
    )
    yield ctrl


def test_pairing_is_refused_while_offline_only_is_enabled(controller):
    """No WebRTCStreamService is constructed, so the WebRTC thread — and
    with it the signaling calls and ICE gathering — never starts."""
    controller._dialog = _StubDialog()

    controller._on_code_submitted("ABC123")

    assert controller._service is None
    assert controller.pairing_code is None


def test_the_refusal_names_the_setting(controller):
    """A silent failure is indistinguishable from a bad pairing code. The
    operator has to be told which knob to turn."""
    dialog = _StubDialog()
    controller._dialog = dialog

    controller._on_code_submitted("ABC123")

    assert len(dialog.code_errors) == 1
    message = dialog.code_errors[0]
    assert "Offline Only" in message
    assert "Preferences" in message
    # It refuses instead of pretending to connect.
    assert dialog.negotiating == []


class _StubService:
    """Records the wiring without starting a QThread or touching a network.

    The real service opens a WebRTC session the moment ``request_connect``
    is called, which is precisely what these tests must not do.
    """

    instances = []

    def __init__(self, signaling=None, pairing_code=None, **kwargs):
        self.pairing_code = pairing_code
        self.connect_requested = False
        type(self).instances.append(self)

    def __getattr__(self, name):
        # Signal connections (errorOccurred.connect, ...) are wiring, not
        # behaviour under test; absorb them.
        return _StubSignal()

    def set_resume_context(self, *args, **kwargs):
        pass

    def request_connect(self):
        self.connect_requested = True

    def cleanup(self):
        pass


class _StubSignal:
    def connect(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        pass


@pytest.fixture
def stub_service(monkeypatch):
    _StubService.instances = []
    # `import core.controllers.flight.FlightTileController as m` binds the
    # *class*, not the module: the package __init__ re-exports it under the
    # same name, and `import a.b as x` resolves via getattr on the parent.
    module = sys.modules["core.controllers.flight.FlightTileController"]

    monkeypatch.setattr(module, "WebRTCStreamService", _StubService)
    yield _StubService


def test_pairing_proceeds_normally_when_offline_only_is_off(qtbot, stub_service):
    """The gate must not become a general obstacle to pairing."""
    ctrl = FlightTileController(
        signaling=InMemorySignalingChannel(),
        settings_service=_StubSettings(offline_only=False),
    )
    dialog = _StubDialog()
    ctrl._dialog = dialog

    ctrl._on_code_submitted("ABC123")

    assert ctrl.pairing_code == "ABC123"
    assert len(stub_service.instances) == 1
    assert stub_service.instances[0].connect_requested is True
    assert dialog.code_errors == []


def test_the_preference_is_read_at_connect_time_not_cached(qtbot, stub_service):
    """Toggling Offline Only takes effect without relaunching the viewer."""
    settings = _StubSettings(offline_only=True)
    ctrl = FlightTileController(
        signaling=InMemorySignalingChannel(), settings_service=settings
    )
    ctrl._dialog = _StubDialog()

    ctrl._on_code_submitted("ABC123")
    assert stub_service.instances == []

    settings._offline_only = False
    ctrl._on_code_submitted("ABC123")
    assert len(stub_service.instances) == 1


# ----------------------------------------------------------------------
# the live map page
# ----------------------------------------------------------------------

def _build_page(offline_only):
    """Render the map page the way ``_setup_web_view`` does."""
    head = FlightMapViewModule.build_leaflet_head(offline_only=offline_only)
    page = FlightMapViewModule.LEAFLET_HTML.replace("__ADIAT_LEAFLET_HEAD__", head)
    basemap = FlightMapViewModule.BASEMAP_JS
    if offline_only:
        basemap = FlightMapViewModule.OFFLINE_BASEMAP_JS.replace(
            "__ADIAT_OFFLINE_NOTICE__",
            json.dumps("Offline Only mode — basemap tiles not loaded"),
        )
    return page.replace("__ADIAT_BASEMAP_JS__", basemap)


def test_the_offline_map_page_requests_no_tiles():
    """Every tile layer is a live request to OpenStreetMap or Esri. In
    Offline Only the page must reach neither."""
    page = _build_page(offline_only=True)

    assert "__ADIAT_BASEMAP_JS__" not in page, "placeholder left unsubstituted"
    assert "tile.openstreetmap.org" not in page
    assert "server.arcgisonline.com" not in page
    assert "unpkg.com" not in page


def test_the_offline_map_still_renders_positions():
    """Losing the basemap must not lose the geometry — markers, aircraft
    and track draw over an empty canvas, which is the point of keeping
    the map open at all."""
    page = _build_page(offline_only=True)

    assert "L.map('map'" in page
    assert "window.addMarker" in page
    assert "setAircraft" in page
    # And the operator is told why the imagery is missing.
    assert "Offline Only mode" in page


def test_the_online_map_page_still_has_its_basemaps():
    """The gate must not strip tiles from the normal path."""
    page = _build_page(offline_only=False)

    assert "tile.openstreetmap.org" in page
    assert "server.arcgisonline.com" in page
    assert "__ADIAT_BASEMAP_JS__" not in page


def test_the_page_template_carries_the_basemap_placeholder():
    """``_setup_web_view`` substitutes this. If the template loses the
    placeholder the basemap silently disappears in *both* modes."""
    assert "__ADIAT_BASEMAP_JS__" in FlightMapViewModule.LEAFLET_HTML
    # And the template itself names no tile host — the online block is
    # what carries them, which is what makes the offline page verifiable.
    assert "tile.openstreetmap.org" not in FlightMapViewModule.LEAFLET_HTML
    assert "server.arcgisonline.com" not in FlightMapViewModule.LEAFLET_HTML
    assert "tile.openstreetmap.org" in FlightMapViewModule.BASEMAP_JS
    assert "server.arcgisonline.com" in FlightMapViewModule.BASEMAP_JS
    assert "tileLayer" not in FlightMapViewModule.OFFLINE_BASEMAP_JS


def test_the_offline_notice_is_translatable():
    """CLAUDE.md 2.8: new operator-visible text goes through tr(). The
    notice is a placeholder the widget fills with a translated, JSON-escaped
    literal, so an apostrophe in a translation cannot break the page."""
    import inspect

    assert "__ADIAT_OFFLINE_NOTICE__" in FlightMapViewModule.OFFLINE_BASEMAP_JS

    source = inspect.getsource(FlightMapViewModule.FlightMapView._setup_web_view)
    assert "self.tr(" in source
    assert "json.dumps(" in source


def test_flight_map_view_reads_the_preference(monkeypatch):
    """The widget resolves Offline Only from SettingsService."""
    import core.services.SettingsService as settings_module

    monkeypatch.setattr(
        settings_module.SettingsService,
        "get_bool_setting",
        lambda self, name, default_value=False: name == "OfflineOnly",
    )

    assert FlightMapViewModule.FlightMapView._is_offline_only() is True


def test_flight_map_view_defaults_to_online_when_settings_are_unreadable(monkeypatch):
    """A settings failure must not silently blank the operator's basemap."""
    import core.services.SettingsService as settings_module

    def boom(self, name, default_value=False):
        raise RuntimeError("settings unavailable")

    monkeypatch.setattr(settings_module.SettingsService, "get_bool_setting", boom)

    assert FlightMapViewModule.FlightMapView._is_offline_only() is False
