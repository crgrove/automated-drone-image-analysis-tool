"""What the Wingtra controller keeps after the parsing moved to a service.

The prompt, the summary dialog, and writing the result into the viewer's
image dicts. The reading, matching and AGL arithmetic are covered against the
service in app/tests/core/services/image/test_wingtra_data_service.py; what
matters here is that the controller delegates rather than reimplementing, and
that the injection into ``parent.images`` is exactly what downstream
consumers read.
"""

import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from core.controllers.images.viewer.WingtraDataController import (
    WingtraDataController,
)
from core.services.image.WingtraDataService import WingtraImageData

MODULE = 'core.controllers.images.viewer.WingtraDataController'


def _data(name="IMG_0001.JPG", kappa=90.0, agl_m=None, phi=1.0, omega=0.5):
    return WingtraImageData(
        image_name=name, latitude=30.0, longitude=-97.0, altitude_asl=350.0,
        omega=omega, phi=phi, kappa=kappa, accuracy_h=0.0, accuracy_v=0.0,
        altitude_agl=agl_m,
    )


class _Settings:
    """Enough of SettingsService for the folder-memory round trip."""

    def __init__(self):
        self.values = {}

    def get_setting(self, key, default=None):
        return self.values.get(key, default)

    def set_setting(self, key, value):
        self.values[key] = value


def _viewer(*names):
    return SimpleNamespace(
        images=[{'name': name} for name in names],
        settings_service=_Settings(),
    )


@pytest.fixture
def controller():
    return WingtraDataController(_viewer("IMG_0001.JPG", "IMG_0002.JPG"))


# ---------------------------------------------------------------------------
# injection into the viewer's image dicts
# ---------------------------------------------------------------------------

def test_the_bearing_reaches_the_image_dict(controller):
    """Every consumer - R-key rotation, the GPS map, KML export, coverage -
    reads image['bearing'], so that is the contract."""
    controller._inject_into_image_dicts({"IMG_0001.JPG": _data(kappa=90.0)})

    assert controller.parent.images[0]['bearing'] == pytest.approx(270.0)
    assert 'bearing' not in controller.parent.images[1]


def test_the_agl_is_injected_in_feet(controller):
    controller._inject_into_image_dicts(
        {"IMG_0001.JPG": _data(agl_m=100.0)})

    assert controller.parent.images[0]['wingtra_agl_ft'] == pytest.approx(328.084)


def test_an_image_without_an_agl_gets_no_agl_key(controller):
    """Absent, not zero: a zero would feed straight into GSD."""
    controller._inject_into_image_dicts({"IMG_0001.JPG": _data(agl_m=None)})

    assert 'wingtra_agl_ft' not in controller.parent.images[0]
    assert 'bearing' in controller.parent.images[0]


def test_gps_map_entries_are_updated_too(controller):
    """The GPS map keeps its own list, keyed by index into images."""
    controller.parent.gps_map_controller = SimpleNamespace(
        gps_data=[{'index': 0}, {'index': 1}])

    controller._inject_into_image_dicts(
        {"IMG_0001.JPG": _data(kappa=90.0, agl_m=100.0)})

    assert controller.parent.gps_map_controller.gps_data[0]['bearing'] == pytest.approx(270.0)
    assert 'wingtra_agl_ft' in controller.parent.gps_map_controller.gps_data[0]
    assert 'bearing' not in controller.parent.gps_map_controller.gps_data[1]


def test_clearing_removes_everything_it_injected(controller):
    controller.parent.gps_map_controller = SimpleNamespace(
        gps_data=[{'index': 0}])
    controller._inject_into_image_dicts(
        {"IMG_0001.JPG": _data(kappa=90.0, agl_m=100.0)})
    controller.is_active = True

    controller.clear_data()

    assert 'bearing' not in controller.parent.images[0]
    assert 'wingtra_agl_ft' not in controller.parent.images[0]
    assert controller.parent.gps_map_controller.gps_data[0]['bearing'] is None
    assert controller.is_active is False
    assert controller.image_data == {}


# ---------------------------------------------------------------------------
# the accessors ImageService calls into
# ---------------------------------------------------------------------------

def test_the_accessors_return_nothing_while_inactive(controller):
    controller.image_data = {"IMG_0001.JPG": _data()}
    controller.is_active = False

    assert controller.get_wingtra_data("IMG_0001.JPG") is None
    assert controller.get_camera_yaw("IMG_0001.JPG") is None
    assert controller.get_altitude_agl_ft("IMG_0001.JPG") is None


def test_yaw_is_the_geographic_bearing(controller):
    controller.image_data = {"IMG_0001.JPG": _data(kappa=90.0)}
    controller.is_active = True

    assert controller.get_camera_yaw("IMG_0001.JPG") == pytest.approx(270.0)


def test_pitch_is_converted_to_the_photogrammetry_convention(controller):
    """Wingtra reports 0 at nadir; ADIAT's cameras report -90."""
    controller.image_data = {"IMG_0001.JPG": _data(phi=0.0)}
    controller.is_active = True

    assert controller.get_camera_pitch("IMG_0001.JPG") == pytest.approx(-90.0)


def test_roll_passes_through(controller):
    controller.image_data = {"IMG_0001.JPG": _data(omega=2.5)}
    controller.is_active = True

    assert controller.get_gimbal_roll("IMG_0001.JPG") == pytest.approx(2.5)


def test_an_unknown_image_name_has_no_overrides(controller):
    controller.image_data = {"IMG_0001.JPG": _data()}
    controller.is_active = True

    assert controller.get_camera_yaw("OTHER.JPG") is None


# ---------------------------------------------------------------------------
# delegation
# ---------------------------------------------------------------------------

def test_the_controller_delegates_reading_and_matching(controller, monkeypatch):
    """The controller's job is the prompt and the dialogs; a controller that
    reimplements the parser is what CLAUDE.md 2.1 rules out."""
    from PySide6.QtWidgets import QFileDialog

    module = importlib.import_module(MODULE)
    calls = []

    monkeypatch.setattr(QFileDialog, 'getOpenFileName',
                        staticmethod(lambda *a, **k: ('/tmp/flight.csv', '')))
    monkeypatch.setattr(module, 'parse_wingtra_csv',
                        lambda path: (calls.append(('parse', path))
                                      or ({"IMG_0001.JPG": _data()}, [])))
    monkeypatch.setattr(module, 'match_image_names',
                        lambda parsed, names: (calls.append(('match', list(names)))
                                               or (parsed, [], [])))
    monkeypatch.setattr(module, 'compute_agl',
                        lambda matched, **kw: calls.append(('agl',)) or 1)
    # Accept the summary dialog.
    monkeypatch.setattr(module, 'WingtraDataDialog',
                        lambda *a, **k: MagicMock(exec=lambda: 1))
    monkeypatch.setattr(module.QDialog, 'Accepted', 1, raising=False)

    controller.prompt_and_load_csv()

    assert [c[0] for c in calls] == ['parse', 'match', 'agl']
    assert calls[0][1] == '/tmp/flight.csv'
    # The controller supplies the result image names; the service does not
    # reach into the viewer.
    assert calls[1][1] == ["IMG_0001.JPG", "IMG_0002.JPG"]
    assert controller.is_active is True
    assert controller.parent.images[0]['bearing'] == pytest.approx(270.0)


def test_a_cancelled_prompt_reads_nothing(controller, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    module = importlib.import_module(MODULE)
    calls = []
    monkeypatch.setattr(QFileDialog, 'getOpenFileName',
                        staticmethod(lambda *a, **k: ('', '')))
    monkeypatch.setattr(module, 'parse_wingtra_csv',
                        lambda path: calls.append(path) or ({}, []))

    controller.prompt_and_load_csv()

    assert calls == []
    assert controller.is_active is False


def test_parse_errors_stop_the_load(controller, monkeypatch):
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    module = importlib.import_module(MODULE)
    shown = []
    monkeypatch.setattr(QFileDialog, 'getOpenFileName',
                        staticmethod(lambda *a, **k: ('/tmp/flight.csv', '')))
    monkeypatch.setattr(module, 'parse_wingtra_csv',
                        lambda path: ({}, ['Row 2: bad']))
    monkeypatch.setattr(QMessageBox, 'critical',
                        staticmethod(lambda *a, **k: shown.append(a)))

    controller.prompt_and_load_csv()

    assert shown, "the operator is told the file could not be read"
    assert controller.is_active is False


def test_no_matches_stops_the_load(controller, monkeypatch):
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    module = importlib.import_module(MODULE)
    shown = []
    monkeypatch.setattr(QFileDialog, 'getOpenFileName',
                        staticmethod(lambda *a, **k: ('/tmp/flight.csv', '')))
    monkeypatch.setattr(module, 'parse_wingtra_csv',
                        lambda path: ({"X.JPG": _data("X.JPG")}, []))
    monkeypatch.setattr(module, 'match_image_names',
                        lambda parsed, names: ({}, ["X.JPG"], list(names)))
    monkeypatch.setattr(QMessageBox, 'warning',
                        staticmethod(lambda *a, **k: shown.append(a)))

    controller.prompt_and_load_csv()

    assert shown, "the operator is shown both sides of the mismatch"
    assert controller.is_active is False
