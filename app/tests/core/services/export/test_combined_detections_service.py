"""Unit tests for CombinedDetectionsService (combined KML / CalTopo detections)."""

import xml.etree.ElementTree as ET
import zipfile
from unittest.mock import MagicMock, patch

import pytest

from core.services.export.CombinedDetectionsService import (
    CombinedDetectionsService,
    detection_image_name,
)

_MODULE = "core.services.export.CombinedDetectionsService"
_KML_NS = {'kml': 'http://www.opengis.net/kml/2.2'}


def _write_run(tmp_path, name, images):
    """Create <name>/ADIAT_Results/ADIAT_Data.xml plus the image files.

    Args:
        images: list of (filename, aoi_flags) - one AOI per flag string.
    """
    run_dir = tmp_path / name
    results_dir = run_dir / "ADIAT_Results"
    results_dir.mkdir(parents=True)

    image_blocks = []
    for filename, aoi_flags in images:
        (run_dir / filename).write_text("jpg")
        aois = "".join(
            f'<areas_of_interest center="(10, 10)" radius="5" area="20.0" '
            f'flagged="{flag}" number="{i + 1}"/>'
            for i, flag in enumerate(aoi_flags)
        )
        image_blocks.append(
            f'<image path="../{filename}" hidden="False" width="100" height="100">{aois}</image>')

    xml = (
        '<data>'
        '<settings input_dir="in" output_dir="out" identifier_color="(255, 0, 255)" '
        'aoi_radius="15" algorithm="HSVColorRange" thermal="False" num_processes="1" '
        'min_area="10" max_area="" hist_ref_path="" kmeans_clusters="">'
        '<options><option name="sensitivity" value="5"/></options>'
        '</settings>'
        f'<images>{"".join(image_blocks)}</images>'
        '</data>'
    )
    xml_path = results_dir / "ADIAT_Data.xml"
    xml_path.write_text(xml)
    return str(xml_path)


def _run(name, images, duplicate_sightings=None):
    """A stand-in RunReportContext."""
    run = MagicMock()
    run.run_name = name
    run.images = images
    run.total_aoi_count = sum(len(img['areas_of_interest']) for img in images)
    run.duplicate_sightings = duplicate_sightings or {}
    run.settings = {}
    return run


def _image(name, aois):
    return {'path': f'/missions/{name}', 'name': name, 'areas_of_interest': aois}


def _service():
    return CombinedDetectionsService(logger=MagicMock())


def _placemarks(kml_path):
    """{folder name: [(placemark name, description, (lon, lat))]} from a KML file."""
    root = ET.parse(kml_path).getroot()
    folders = {}
    for folder in root.iter('{http://www.opengis.net/kml/2.2}Folder'):
        entries = []
        for placemark in folder.findall('kml:Placemark', _KML_NS):
            coords = placemark.find('.//kml:coordinates', _KML_NS).text.strip().split(',')
            entries.append((
                placemark.find('kml:name', _KML_NS).text,
                placemark.find('kml:description', _KML_NS).text,
                (float(coords[0]), float(coords[1])),
            ))
        folders[folder.find('kml:name', _KML_NS).text] = entries
    return folders


class _PositioningStub:
    """Patch the image services so every AOI lands at a known position."""

    def __init__(self, positions=None, camera_gps=None, read_error=None):
        """
        Args:
            positions: Values calculate_gps_with_custom_altitude returns in turn.
            camera_gps: The image GPS LocationInfo.get_gps returns.
            read_error: Exception ImageService raises, to simulate unreadable files.
        """
        self.positions = list(positions or [])
        self.camera_gps = camera_gps if camera_gps is not None else {'latitude': 30.0, 'longitude': -97.0}
        self.read_error = read_error

    def __enter__(self):
        self._patches = [
            patch(f"{_MODULE}.ImageService"),
            patch(f"{_MODULE}.AOIService"),
            patch(f"{_MODULE}.LocationInfo.get_gps", return_value=self.camera_gps),
        ]
        image_service_cls, aoi_service_cls, _ = [p.start() for p in self._patches]
        if self.read_error is not None:
            image_service_cls.side_effect = self.read_error
        aoi_service = aoi_service_cls.return_value
        aoi_service.calculate_gps_with_custom_altitude.side_effect = self.positions
        aoi_service.get_cached_or_representative_color.return_value = {
            'rgb': (255, 0, 0), 'hex': '#ff0000', 'hue_degrees': 0}
        self.image_service_cls = image_service_cls
        self.aoi_service = aoi_service
        return self

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()


# ---------------------------------------------------------------------------
# Loading and flattening
# ---------------------------------------------------------------------------

def test_load_runs_matches_report_scope_and_drops_empty_runs(tmp_path):
    flagged = _write_run(tmp_path, "Flight1", [("a.jpg", ["True", "False"])])
    unflagged = _write_run(tmp_path, "Flight2", [("b.jpg", ["False"])])

    runs = _service().load_runs([flagged, unflagged])

    assert [run.run_name for run in runs] == ["Flight1"]
    assert [aoi['flagged'] for aoi in runs[0].images[0]['areas_of_interest']] == [True]


def test_load_runs_include_flag_keeps_unflagged_images(tmp_path):
    unflagged = _write_run(tmp_path, "Flight2", [("b.jpg", ["False", "False"])])

    service = CombinedDetectionsService(include_images_without_flagged_aois=True, logger=MagicMock())
    runs = service.load_runs([unflagged])

    assert service.count_detections(runs) == 2


def test_load_runs_resolves_images_through_the_scan_session(tmp_path):
    xml_path = _write_run(tmp_path, "Flight1", [("a.jpg", ["True"])])
    (tmp_path / "Flight1" / "a.jpg").unlink()
    relocated = tmp_path / "elsewhere.jpg"
    relocated.write_text("jpg")
    session = MagicMock()
    session.resolve_file.return_value = str(relocated)

    service = CombinedDetectionsService(recovery_session=session, logger=MagicMock())
    runs = service.load_runs([xml_path])

    assert runs[0].images[0]['path'] == str(relocated)


def test_flatten_runs_names_images_as_the_report_does():
    run1 = _run("Flight1", [_image('a.jpg', [{}, {}])])
    run2 = _run("Flight2", [_image('a.jpg', [{}]), _image('b.jpg', [{}])])

    images, flagged_aois, spans = CombinedDetectionsService.flatten_runs([run1, run2])

    assert [img['name'] for img in images] == ['[1] a.jpg', '[2] a.jpg', '[2] b.jpg']
    assert flagged_aois == {0: [0, 1], 1: [0], 2: [0]}
    assert [(run.run_name, start, stop) for run, start, stop in spans] == [
        ("Flight1", 0, 1), ("Flight2", 1, 3)]
    # The runs' own dicts are untouched, so the PDF can name them itself
    assert run2.images[0]['name'] == 'a.jpg'


def test_detection_image_name():
    assert detection_image_name(3, {'name': 'DJI_0001.JPG'}) == "[3] DJI_0001.JPG"


# ---------------------------------------------------------------------------
# KML
# ---------------------------------------------------------------------------

def test_generate_kml_writes_a_folder_per_run(tmp_path):
    run1 = _run("Flight1", [_image('a.jpg', [{'center': (1, 2), 'area': 30}])])
    run2 = _run("Flight2", [_image('b.jpg', [{'center': (3, 4), 'area': 40}, {'center': (5, 6)}])])
    output = tmp_path / "detections.kml"

    with _PositioningStub(positions=[(30.1, -97.1), (30.2, -97.2), (30.3, -97.3)]):
        summary = _service().generate_kml(str(output), [run1, run2])

    assert summary == {'exported': 3, 'unplaced': 0}
    folders = _placemarks(output)
    assert list(folders) == ["1. Flight1", "2. Flight2"]
    assert [name for name, _, _ in folders["2. Flight2"]] == [
        "[2] b.jpg - AOI 1", "[2] b.jpg - AOI 2"]
    assert folders["1. Flight1"][0][2] == (-97.1, 30.1)
    assert "Estimated AOI GPS" in folders["1. Flight1"][0][1]
    assert "Run: Flight1" in folders["1. Flight1"][0][1]
    assert ET.parse(output).getroot().find('kml:Document/kml:name', _KML_NS).text == "detections"


def test_generate_kml_uses_terrain_preference_and_no_altitude_override(tmp_path):
    run = _run("Flight1", [_image('a.jpg', [{'center': (1, 2)}])])
    service = CombinedDetectionsService(use_terrain_elevation=False, logger=MagicMock())

    with _PositioningStub(positions=[(30.1, -97.1)]) as stub:
        service.generate_kml(str(tmp_path / "out.kml"), [run])

    args = stub.aoi_service.calculate_gps_with_custom_altitude.call_args.args
    assert args[2] is None  # no Wingtra AGL, no operator override
    assert args[3] is False


def test_generate_kml_puts_reviewer_input_in_the_description(tmp_path):
    aoi = {'center': (1, 2), 'number': 1, 'user_comment': 'Alice: red jacket',
           'review_note': 'Flagged by 2 of 3 reviewers (Alice, Bob).'}
    sightings = {1: [('IMG_9.jpg', 7)]}
    run = _run("Flight1", [_image('a.jpg', [aoi])], duplicate_sightings=sightings)
    output = tmp_path / "out.kml"

    with _PositioningStub(positions=[(30.1, -97.1)]), \
            patch(f"{_MODULE}.AOIDuplicateService.sightings_line",
                  return_value="Also seen in: IMG_9.jpg (AOI #7)") as sightings_line:
        _service().generate_kml(str(output), [run])

    description = _placemarks(output)["1. Flight1"][0][1]
    assert description.startswith('"Alice: red jacket"')
    assert "Review: Flagged by 2 of 3 reviewers (Alice, Bob)." in description
    assert "Also seen in: IMG_9.jpg (AOI #7)" in description
    # Links are resolved against the AOI's own run, never across runs
    assert sightings_line.call_args.args[1] is sightings


def test_generate_kml_falls_back_to_camera_position(tmp_path):
    run = _run("Flight1", [_image('a.jpg', [{'center': (1, 2)}])])
    output = tmp_path / "out.kml"

    with _PositioningStub(positions=[None], camera_gps={'latitude': 31.0, 'longitude': -98.0}):
        summary = _service().generate_kml(str(output), [run])

    assert summary == {'exported': 1, 'unplaced': 0}
    _, description, coords = _placemarks(output)["1. Flight1"][0]
    assert coords == (-98.0, 31.0)
    assert "Image GPS (AOI position could not be calculated)" in description


def test_generate_kml_counts_aois_it_cannot_place(tmp_path):
    no_gps = _run("Flight1", [_image('a.jpg', [{}, {}])])
    unreadable = _run("Flight2", [_image('b.jpg', [{}])])
    output = tmp_path / "out.kml"

    with _PositioningStub(positions=[None, None], camera_gps={}):
        summary = _service().generate_kml(str(output), [no_gps])
    assert summary == {'exported': 0, 'unplaced': 2}

    with _PositioningStub(read_error=OSError("unreadable")):
        summary = _service().generate_kml(str(output), [unreadable])
    assert summary == {'exported': 0, 'unplaced': 1}


def test_generate_kml_cancel_writes_nothing(tmp_path):
    run = _run("Flight1", [_image('a.jpg', [{}])])
    output = tmp_path / "out.kml"

    with _PositioningStub(positions=[(30.1, -97.1)]):
        summary = _service().generate_kml(str(output), [run], cancel_check=lambda: True)

    assert summary is None
    assert not output.exists()


def test_generate_kml_kmz_path_writes_an_archive(tmp_path):
    run = _run("Flight1", [_image('a.jpg', [{}])])
    output = tmp_path / "out.kmz"

    with _PositioningStub(positions=[(30.1, -97.1)]):
        _service().generate_kml(str(output), [run])

    assert zipfile.is_zipfile(output)


def test_generate_kml_reports_progress(tmp_path):
    run = _run("Flight1", [_image('a.jpg', [{}, {}])])
    progress = []

    with _PositioningStub(positions=[(30.1, -97.1), (30.2, -97.2)]):
        _service().generate_kml(
            str(tmp_path / "out.kml"), [run],
            progress_callback=lambda current, total, message: progress.append((current, total)))

    assert progress[0] == (0, 2)
    assert progress[-1] == (2, 2)


@pytest.mark.parametrize('original_path, expected', [
    (None, '/missions/a.jpg'),
    ('/originals/a.jpg', '/originals/a.jpg'),
])
def test_generate_kml_reads_metadata_from_the_original_image(tmp_path, original_path, expected):
    image = _image('a.jpg', [{}])
    if original_path:
        image['original_path'] = original_path
    run = _run("Flight1", [image])

    with _PositioningStub(positions=[(30.1, -97.1)]) as stub:
        _service().generate_kml(str(tmp_path / "out.kml"), [run])

    assert stub.image_service_cls.call_args.args[0] == expected
