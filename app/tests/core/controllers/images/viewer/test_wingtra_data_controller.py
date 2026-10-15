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

    assert [c[0] for c in calls] == ['parse', 'match', 'match', 'agl']
    assert calls[0][1] == '/tmp/flight.csv'
    # The controller supplies the result image names; the service does not
    # reach into the viewer.
    assert calls[1][1] == ["IMG_0001.JPG", "IMG_0002.JPG"]
    # Then the flight's frames with no AOI - none on this viewer.
    assert calls[2][1] == []
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


# ---------------------------------------------------------------------------
# finding the geotags when the results open
# ---------------------------------------------------------------------------

WINGTRA_HEADER = (
    "# image name,latitude [decimal degrees],longitude [decimal degrees],"
    "altitude [meter],omega [degrees],phi [degrees],kappa [degrees],"
    "accuracy horizontal [meter],accuracy vertical [meter]"
)


def _results(tmp_path, *names):
    """A viewer over result images in tmp_path, with a real ADIAT_Data.xml."""
    from core.services.XmlService import XmlService

    xml_path = tmp_path / "ADIAT_Data.xml"
    if not xml_path.exists():
        xml_path.write_text("<data><images/></data>")
    viewer = _viewer(*names)
    for image in viewer.images:
        image['path'] = str(tmp_path / image['name'])
    viewer.xml_service = XmlService(str(xml_path))
    viewer.xml_path = str(xml_path)
    return viewer


def _write_geotags(folder, *names, file_name="Flight 1 geotags.csv", kappa=90.0):
    rows = [f"{name},43.78,-110.72,2190.0,0.5,1.0,{kappa},5.00,10.00" for name in names]
    path = folder / file_name
    path.write_text("\n".join([WINGTRA_HEADER, *rows]) + "\n", encoding="utf-8")
    return str(path)


def _candidate(path, matched=2, rows=2):
    from core.services.image.WingtraDataService import WingtraCsvCandidate
    return WingtraCsvCandidate(path=path, row_count=rows, matched_count=matched)


class _Recorder:
    """Stands in for the dialogs and the loader, recording what was asked."""

    def __init__(self, monkeypatch, controller, *, answer=None, item=None,
                 candidates=(), wingtra=False):
        from PySide6.QtWidgets import QInputDialog, QMessageBox

        module = importlib.import_module(MODULE)
        self.questions = []
        self.item_prompts = []
        self.loaded = []
        self.browsed = []
        self.searched = []

        def question(parent, title, text, *args):
            self.questions.append(text)
            return answer

        def get_item(parent, title, text, items, *args):
            self.item_prompts.append(items)
            if item is None:
                return '', False
            return items[item], True

        def search(paths, names):
            self.searched.append(list(paths))
            return list(candidates)

        def load(path, confirm):
            self.loaded.append((path, confirm))
            return True

        def browse(start_dir=None):
            self.browsed.append(start_dir)

        monkeypatch.setattr(QMessageBox, 'question', staticmethod(question))
        monkeypatch.setattr(QInputDialog, 'getItem', staticmethod(get_item))
        monkeypatch.setattr(module, 'find_wingtra_csvs', search)
        monkeypatch.setattr(module, 'is_wingtra_image', lambda path: wingtra)
        monkeypatch.setattr(controller, 'load_csv', load)
        monkeypatch.setattr(controller, 'prompt_and_load_csv', browse)


def test_a_single_geotags_file_is_offered_and_loaded_on_yes(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    controller = WingtraDataController(_results(tmp_path, "A.JPG", "B.JPG"))
    csv_path = str(tmp_path / "geotags.csv")
    rec = _Recorder(monkeypatch, controller, answer=QMessageBox.Yes,
                    candidates=[_candidate(csv_path)])

    controller.auto_load_on_open()

    assert len(rec.questions) == 1
    assert rec.questions[0].startswith("Wingtra geotags found - Load?")
    assert csv_path in rec.questions[0]
    assert "2 of 2 images" in rec.questions[0]
    # Already agreed to: no second confirmation dialog.
    assert rec.loaded == [(csv_path, False)]


def test_declining_the_offer_is_remembered(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    from core.services.XmlService import XmlService

    viewer = _results(tmp_path, "A.JPG")
    controller = WingtraDataController(viewer)
    csv_path = str(tmp_path / "geotags.csv")
    rec = _Recorder(monkeypatch, controller, answer=QMessageBox.No,
                    candidates=[_candidate(csv_path)])

    controller.auto_load_on_open()

    assert rec.loaded == []
    # Saved to disk, not just held in memory.
    assert XmlService(viewer.xml_path).get_wingtra_geotags() == {
        'csv_path': csv_path, 'status': 'declined'}


def test_declined_results_are_not_asked_again(tmp_path, monkeypatch):
    viewer = _results(tmp_path, "A.JPG")
    viewer.xml_service.set_wingtra_geotags("x.csv", "declined")
    controller = WingtraDataController(viewer)
    rec = _Recorder(monkeypatch, controller, candidates=[_candidate("x.csv")],
                    wingtra=True)

    controller.auto_load_on_open()

    assert rec.questions == []
    assert rec.searched == []
    assert rec.loaded == []


def test_linked_results_reload_their_csv_without_asking(tmp_path, monkeypatch):
    viewer = _results(tmp_path, "A.JPG")
    csv_path = _write_geotags(tmp_path, "A.JPG")
    viewer.xml_service.set_wingtra_geotags(csv_path, "loaded")
    controller = WingtraDataController(viewer)
    rec = _Recorder(monkeypatch, controller)

    controller.auto_load_on_open()

    assert rec.questions == []
    assert rec.searched == []
    assert rec.loaded == [(csv_path, False)]


def test_a_linked_csv_that_has_moved_falls_back_to_a_search(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    viewer = _results(tmp_path, "A.JPG")
    viewer.xml_service.set_wingtra_geotags(str(tmp_path / "moved.csv"), "loaded")
    controller = WingtraDataController(viewer)
    found = str(tmp_path / "here.csv")
    rec = _Recorder(monkeypatch, controller, answer=QMessageBox.Yes,
                    candidates=[_candidate(found)])

    controller.auto_load_on_open()

    assert rec.searched == [[str(tmp_path / "A.JPG")]]
    assert rec.loaded == [(found, False)]


def test_several_geotags_files_let_the_operator_choose(tmp_path, monkeypatch):
    controller = WingtraDataController(_results(tmp_path, "A.JPG", "B.JPG"))
    first = str(tmp_path / "full.csv")
    second = str(tmp_path / "partial.csv")
    rec = _Recorder(monkeypatch, controller, item=1,
                    candidates=[_candidate(first, 2), _candidate(second, 1)])

    controller.auto_load_on_open()

    assert rec.item_prompts == [["full.csv (2 of 2 images match)",
                                 "partial.csv (1 of 2 images match)"]]
    assert rec.loaded == [(second, False)]


def test_cancelling_the_choice_declines(tmp_path, monkeypatch):
    viewer = _results(tmp_path, "A.JPG")
    controller = WingtraDataController(viewer)
    rec = _Recorder(monkeypatch, controller, item=None,
                    candidates=[_candidate("a.csv"), _candidate("b.csv", 1)])

    controller.auto_load_on_open()

    assert rec.loaded == []
    assert viewer.xml_service.get_wingtra_geotags()['status'] == 'declined'


def test_wingtra_imagery_without_a_csv_offers_to_browse(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    controller = WingtraDataController(_results(tmp_path, "A.JPG"))
    rec = _Recorder(monkeypatch, controller, answer=QMessageBox.Yes, wingtra=True)

    controller.auto_load_on_open()

    assert len(rec.questions) == 1
    assert rec.questions[0].startswith("Load Wingtra GeoTag .csv file?")
    # The file dialog opens where the imagery is.
    assert rec.browsed == [str(tmp_path)]


def test_declining_to_browse_is_remembered(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    viewer = _results(tmp_path, "A.JPG")
    controller = WingtraDataController(viewer)
    rec = _Recorder(monkeypatch, controller, answer=QMessageBox.No, wingtra=True)

    controller.auto_load_on_open()

    assert rec.browsed == []
    assert viewer.xml_service.get_wingtra_geotags()['status'] == 'declined'


def test_other_imagery_without_a_csv_is_left_alone(tmp_path, monkeypatch):
    viewer = _results(tmp_path, "DJI_0001.JPG")
    controller = WingtraDataController(viewer)
    rec = _Recorder(monkeypatch, controller, wingtra=False)

    controller.auto_load_on_open()

    assert rec.questions == []
    assert rec.browsed == []
    assert rec.loaded == []
    assert viewer.xml_service.get_wingtra_geotags() is None


def test_browsing_opens_in_the_given_folder(controller, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    opened_in = []

    def get_open_file_name(parent, title, folder, *args):
        opened_in.append(folder)
        return '', ''

    monkeypatch.setattr(QFileDialog, 'getOpenFileName', staticmethod(get_open_file_name))
    controller.parent.settings_service.set_setting('LastWingtraFolder', str(tmp_path.parent))

    controller.prompt_and_load_csv(str(tmp_path))

    assert opened_in == [str(tmp_path)]


def test_open_accept_and_reopen_end_to_end(qtbot, tmp_path, monkeypatch):
    """Real CSV, real ADIAT_Data.xml: the first open asks and applies the
    bearing; reopening the same results reloads it without asking."""
    from PySide6.QtWidgets import QMessageBox

    module = importlib.import_module(MODULE)
    monkeypatch.setattr(module, 'compute_agl', lambda matched, **kw: 0)
    asked = []

    def question(parent, title, text, *args):
        asked.append(text)
        return QMessageBox.Yes

    monkeypatch.setattr(QMessageBox, 'question', staticmethod(question))
    csv_path = _write_geotags(tmp_path, "A.JPG", "B.JPG", kappa=90.0)

    first = _results(tmp_path, "A.JPG", "B.JPG")
    WingtraDataController(first).auto_load_on_open()

    assert len(asked) == 1
    assert first.images[0]['bearing'] == pytest.approx(270.0)

    # Reopen: a fresh viewer over the same results file.
    reopened = _results(tmp_path, "A.JPG", "B.JPG")
    controller = WingtraDataController(reopened)
    controller.auto_load_on_open()

    assert len(asked) == 1, "a linked CSV reloads without asking again"
    assert controller.csv_path == csv_path
    assert reopened.images[1]['bearing'] == pytest.approx(270.0)


def test_frames_without_aois_get_the_geotags_too(qtbot, tmp_path, monkeypatch):
    """Coverage extent and POD run over every frame of the flight, not just
    the results. A frame with no AOI is a separate dict in source_images; a
    frame with an AOI is the same dict in both lists."""
    module = importlib.import_module(MODULE)

    def flat_100m_agl(data, **kw):
        for row in data.values():
            row.altitude_agl = 100.0
        return len(data)

    monkeypatch.setattr(module, 'compute_agl', flat_100m_agl)
    csv_path = _write_geotags(tmp_path, "A.JPG", "QUIET.JPG", kappa=90.0)

    viewer = _results(tmp_path, "A.JPG")
    quiet = {'path': str(tmp_path / "QUIET.JPG"), 'name': "QUIET.JPG", 'has_aoi': False}
    viewer.source_images = [viewer.images[0], quiet]
    controller = WingtraDataController(viewer)

    assert controller.load_csv(csv_path, confirm=False)

    assert viewer.images[0]['bearing'] == pytest.approx(270.0)
    assert quiet['bearing'] == pytest.approx(270.0)
    assert quiet['wingtra_agl_ft'] == pytest.approx(328.084)
    assert controller.get_wingtra_data("QUIET.JPG") is not None

    controller.clear_data()

    assert 'bearing' not in quiet
    assert 'wingtra_agl_ft' not in quiet
