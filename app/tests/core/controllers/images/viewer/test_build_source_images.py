"""Tests for Viewer._build_source_images' path-identity contract.

The viewer keeps two lists of the same flight: ``images`` (the AOI subset read
from the result XML) and ``source_images`` (every capture in the original
folder). Several features -- the GPS map, coverage extents, the WALDO heading
pre-pass, and AOI-in-neighbouring-images -- decide whether an entry in one list
is the same capture as an entry in the other. They did that by comparing raw
path strings, and the two lists spell the same file differently, so the answer
was always "no".

These tests pin the contract rather than the spelling: one entry per real file,
``has_aoi`` set from actual identity, and the AOI entries carrying the camera
metadata the projection code reads off them.
"""

import os

from core.controllers.images.viewer.Viewer import Viewer


class _FakeViewer:
    """The three attributes _build_source_images touches, and nothing else.

    _build_source_images is a pure function of (images, settings, logger), so it
    is exercised unbound rather than by constructing a real Viewer -- which
    would need a Qt window, a result file and a full controller graph.
    """

    def __init__(self, images, input_dir):
        self.images = images
        self.settings = {'input_dir': input_dir}
        self.logger = _NullLogger()

    def build(self):
        return Viewer._build_source_images(self)


class _NullLogger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass


def _flight(tmp_path, capture_names):
    """Create an input folder of captures and the result folder beside it."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    for name in capture_names:
        (input_dir / name).write_bytes(b"\xff\xd8\xff")
    results_dir = tmp_path / "output" / "ADIAT_Results"
    results_dir.mkdir(parents=True)
    return str(input_dir), str(results_dir)


def _as_xml_service_would_resolve(results_dir, name):
    """The un-normalized spelling get_images used to hand the viewer.

    Kept literal so this test still fails if the join-without-normalize is
    reintroduced anywhere, not only in XmlService.
    """
    return os.path.join(results_dir, "..", "..", "input", name)


def test_relative_spelling_still_matches_the_scanned_capture(tmp_path):
    """The defect, end to end: two spellings of one file must be one entry."""
    input_dir, results_dir = _flight(tmp_path, ["DJI_0065.JPG", "DJI_0066.JPG"])
    images = [{'path': _as_xml_service_would_resolve(results_dir, "DJI_0065.JPG")}]

    source_images = _FakeViewer(images, input_dir).build()

    assert len(source_images) == 2, "one entry per real file, no duplicates"
    flagged = [e for e in source_images if e['has_aoi']]
    assert [e['name'] for e in flagged] == ["DJI_0065.JPG"]


def test_capture_without_detections_is_kept_and_flagged_false(tmp_path):
    input_dir, results_dir = _flight(tmp_path, ["DJI_0065.JPG", "DJI_0066.JPG"])
    images = [{'path': _as_xml_service_would_resolve(results_dir, "DJI_0065.JPG")}]

    source_images = _FakeViewer(images, input_dir).build()

    unflagged = [e for e in source_images if not e['has_aoi']]
    assert [e['name'] for e in unflagged] == ["DJI_0066.JPG"]


def test_aoi_entries_carry_the_camera_metadata_the_projection_reads(tmp_path):
    """AOINeighborService reads these keys off whichever list it is given.

    Entries used to be built as {'path','name','has_aoi'} literals, so the
    inverse projection saw bearing=None and fov_alignment=None and silently
    used a different camera model than the forward projection that produced
    the AOI's GPS in the first place.
    """
    input_dir, results_dir = _flight(tmp_path, ["DJI_0065.JPG"])
    images = [{
        'path': _as_xml_service_would_resolve(results_dir, "DJI_0065.JPG"),
        'bearing': 271.5,
        'mask_path': 'DJI_0065.tif',
        'width': 5472,
        'height': 3648,
        'fov_alignment': {'corners': [(1, 1), (1, 2), (2, 2), (2, 1)]},
    }]

    entry = _FakeViewer(images, input_dir).build()[0]

    assert entry['bearing'] == 271.5
    assert entry['mask_path'] == 'DJI_0065.tif'
    assert entry['width'] == 5472
    assert entry['fov_alignment']['corners']


def test_aoi_entry_tracks_later_edits_to_the_viewer_dict(tmp_path):
    """The Align Image tool writes onto the viewer's dict after this runs.

    A copy taken here would go stale the moment the user aligns an image, and
    the neighbour search would keep ray-casting from the metadata the alignment
    exists to override.
    """
    input_dir, results_dir = _flight(tmp_path, ["DJI_0065.JPG"])
    viewer_image = {'path': _as_xml_service_would_resolve(results_dir, "DJI_0065.JPG")}
    images = [viewer_image]

    entry = _FakeViewer(images, input_dir).build()[0]
    viewer_image['fov_alignment'] = {'corners': [(1, 1), (1, 2), (2, 2), (2, 1)]}

    assert entry['fov_alignment'] == viewer_image['fov_alignment']


def test_aoi_image_missing_from_the_source_folder_is_appended_once(tmp_path):
    """A relocated capture still has to appear, but exactly once."""
    input_dir, results_dir = _flight(tmp_path, ["DJI_0065.JPG"])
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    moved = elsewhere / "DJI_0099.JPG"
    moved.write_bytes(b"\xff\xd8\xff")
    images = [
        {'path': _as_xml_service_would_resolve(results_dir, "DJI_0065.JPG")},
        {'path': str(moved)},
    ]

    source_images = _FakeViewer(images, input_dir).build()

    assert len(source_images) == 2
    assert sorted(e['name'] for e in source_images) == ["DJI_0065.JPG", "DJI_0099.JPG"]
    assert all(e['has_aoi'] for e in source_images)


def test_unreachable_source_folder_falls_back_to_the_aoi_subset(tmp_path):
    _, results_dir = _flight(tmp_path, [])
    images = [{'path': _as_xml_service_would_resolve(results_dir, "DJI_0065.JPG")}]

    source_images = _FakeViewer(images, str(tmp_path / "gone")).build()

    assert len(source_images) == 1
    assert source_images[0]['has_aoi'] is True
    assert source_images[0]['name'] == "DJI_0065.JPG"


def test_non_image_files_in_the_source_folder_are_ignored(tmp_path):
    input_dir, results_dir = _flight(tmp_path, ["DJI_0065.JPG"])
    (tmp_path / "input" / "notes.txt").write_text("x")
    images = [{'path': _as_xml_service_would_resolve(results_dir, "DJI_0065.JPG")}]

    source_images = _FakeViewer(images, input_dir).build()

    assert [e['name'] for e in source_images] == ["DJI_0065.JPG"]
