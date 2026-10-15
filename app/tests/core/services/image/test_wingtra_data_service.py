"""Reading a Wingtra photogrammetry CSV.

This logic shipped inside ``WingtraDataController`` with no coverage at all -
a CSV parser, a fuzzy header mapper, a filename matcher and a geoid-corrected
AGL calculation, all reachable only by driving a file dialog.

Two of these tests are about a wrong number rather than a crash, and those
are the ones that matter:

* the geoid correction. The CSV's altitude is ellipsoidal and the DEM is
  orthometric; differencing them directly overstates height above the ground
  by the local geoid separation, and the error is invisible on the bench.
* ``kappa_to_bearing``. The two conventions agree at 0 and 180, so getting
  the sign wrong mirrors every other heading through north and still looks
  plausible.
"""

import os
from types import SimpleNamespace

import cv2
import numpy as np
import piexif
import pytest

from core.services.image.WingtraDataService import (
    METERS_TO_FEET,
    WingtraImageData,
    build_column_map,
    candidate_folders,
    compute_agl,
    find_wingtra_csvs,
    is_wingtra_image,
    kappa_to_bearing,
    match_image_names,
    parse_wingtra_csv,
    read_csv_image_names,
    resolve_altitude_ft,
    summarize_errors,
    wingtra_agl_ft,
)

WINGTRA_HEADER = (
    "# image name,latitude [decimal degrees],longitude [decimal degrees],"
    "altitude [meter],omega [degrees],phi [degrees],kappa [degrees],"
    "accuracy horizontal [meter],accuracy vertical [meter]"
)


def _write(tmp_path, *rows, header=WINGTRA_HEADER, name="flight.csv"):
    path = tmp_path / name
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    return str(path)


def _row(name="IMG_0001.JPG", lat=30.2672, lon=-97.7431, alt=350.0,
         omega=0.5, phi=1.2, kappa=45.0):
    return f"{name},{lat},{lon},{alt},{omega},{phi},{kappa},0.02,0.03"


# ---------------------------------------------------------------------------
# parse_wingtra_csv
# ---------------------------------------------------------------------------

def test_a_wingtra_export_parses(tmp_path):
    data, errors = parse_wingtra_csv(_write(tmp_path, _row()))

    assert errors == []
    entry = data["IMG_0001.JPG"]
    assert entry.latitude == pytest.approx(30.2672)
    assert entry.altitude_asl == pytest.approx(350.0)
    assert entry.kappa == pytest.approx(45.0)
    assert entry.accuracy_h == pytest.approx(0.02)
    assert entry.altitude_agl is None      # not computed yet


def test_alternate_header_spellings_are_accepted(tmp_path):
    """The header text differs between Wingtra versions and hand-edited
    exports; matching it exactly rejected files that were perfectly usable."""
    header = "filename,lat,lon,alt,roll,pitch,yaw"
    data, errors = parse_wingtra_csv(_write(
        tmp_path, "IMG_1.JPG,30.1,-97.1,300,0,1,90", header=header))

    assert errors == []
    assert data["IMG_1.JPG"].kappa == pytest.approx(90.0)
    # Accuracy columns are optional and default rather than fail.
    assert data["IMG_1.JPG"].accuracy_h == 0.0


def test_a_missing_required_column_rejects_the_file(tmp_path):
    header = "filename,lat,lon,alt"          # no orientation triple
    data, errors = parse_wingtra_csv(_write(tmp_path, "a.jpg,1,2,3", header=header))

    assert data == {}
    assert any("Missing required columns" in e for e in errors)
    assert any("omega" in e for e in errors)


def test_no_header_is_reported(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    data, errors = parse_wingtra_csv(str(path))

    assert data == {}
    assert errors == ["CSV file has no header row"]


def test_one_bad_row_does_not_cost_the_flight(tmp_path):
    """A truncated final line is normal in a card pull."""
    data, errors = parse_wingtra_csv(_write(
        tmp_path,
        _row("IMG_0001.JPG"),
        "IMG_0002.JPG,not-a-number,-97.7,350,0,1,45,0.02,0.03",
        _row("IMG_0003.JPG")))

    assert set(data) == {"IMG_0001.JPG", "IMG_0003.JPG"}
    assert len(errors) == 1
    assert "Row 3" in errors[0]


def test_a_blank_image_name_is_skipped_silently(tmp_path):
    """Trailing blank rows are not errors worth showing the operator."""
    data, errors = parse_wingtra_csv(_write(
        tmp_path, _row(), ",30.1,-97.1,300,0,1,45,0.02,0.03"))

    assert set(data) == {"IMG_0001.JPG"}
    assert errors == []


def test_a_missing_file_is_reported_not_raised(tmp_path):
    data, errors = parse_wingtra_csv(str(tmp_path / "nope.csv"))

    assert data == {}
    assert any("File not found" in e for e in errors)


def test_a_byte_order_mark_does_not_break_the_first_header(tmp_path):
    """Excel writes one; it used to land inside the first column name."""
    path = tmp_path / "bom.csv"
    path.write_text("﻿" + WINGTRA_HEADER + "\n" + _row() + "\n",
                    encoding="utf-8")

    data, errors = parse_wingtra_csv(str(path))

    assert errors == []
    assert "IMG_0001.JPG" in data


# ---------------------------------------------------------------------------
# build_column_map
# ---------------------------------------------------------------------------

def test_header_matching_ignores_case_and_padding():
    mapping = build_column_map(["  # Image Name ", "LATITUDE", "Lon", "ALT",
                                "Omega", "Phi", "Kappa"])

    assert mapping["image"] == "  # Image Name "
    assert mapping["latitude"] == "LATITUDE"
    assert mapping["longitude"] == "Lon"


def test_the_first_matching_alias_wins():
    """Alias order is the tie-break when an export carries two spellings."""
    mapping = build_column_map(["image", "image name", "lat", "lon", "alt",
                                "omega", "phi", "kappa"])

    assert mapping["image"] == "image name"   # earlier in the alias list


# ---------------------------------------------------------------------------
# match_image_names
# ---------------------------------------------------------------------------

def _parsed(*names):
    return {name: WingtraImageData(name, 30.0, -97.0, 300.0, 0, 0, 0, 0, 0)
            for name in names}


def test_exact_names_match():
    matched, unmatched_csv, unmatched_images = match_image_names(
        _parsed("A.JPG", "B.JPG"), ["A.JPG", "B.JPG", "C.JPG"])

    assert set(matched) == {"A.JPG", "B.JPG"}
    assert unmatched_csv == []
    assert unmatched_images == ["C.JPG"]


def test_case_differences_still_match_and_key_on_the_result_name():
    """The CSV and the image folder come from different tools. The result
    name is the key, because that is what every consumer looks up by."""
    matched, unmatched_csv, _unmatched_images = match_image_names(
        _parsed("img_0001.jpg"), ["IMG_0001.JPG"])

    assert set(matched) == {"IMG_0001.JPG"}
    assert unmatched_csv == []


def test_an_exact_match_is_not_lost_to_a_case_folded_one():
    matched, _csv, _images = match_image_names(
        _parsed("A.JPG"), ["a.jpg", "A.JPG"])

    assert "A.JPG" in matched


def test_nothing_matching_reports_both_sides():
    """This is what the operator sees when the CSV is from another flight."""
    matched, unmatched_csv, unmatched_images = match_image_names(
        _parsed("X.JPG"), ["A.JPG", "B.JPG"])

    assert matched == {}
    assert unmatched_csv == ["X.JPG"]
    assert sorted(unmatched_images) == ["A.JPG", "B.JPG"]


# ---------------------------------------------------------------------------
# compute_agl
# ---------------------------------------------------------------------------

class _Terrain:
    """Terrain service stub returning one fixed answer."""

    def __init__(self, elevation_m=100.0, geoid_undulation_m=None,
                 source='terrain'):
        self._result = SimpleNamespace(
            elevation_m=elevation_m,
            geoid_undulation_m=geoid_undulation_m,
            source=source,
        )
        self.queries = []

    def get_elevation(self, lat, lon):
        self.queries.append((lat, lon))
        return self._result


def test_agl_is_the_difference_from_the_terrain():
    data = _parsed("A.JPG")
    data["A.JPG"].altitude_asl = 350.0

    computed = compute_agl(data, terrain_service=_Terrain(elevation_m=100.0))

    assert computed == 1
    assert data["A.JPG"].altitude_agl == pytest.approx(250.0)


def test_the_geoid_undulation_comes_off_first():
    """The number-wrong case. The CSV altitude is ellipsoidal and the DEM is
    orthometric; skipping this overstates height above the ground by the
    local geoid separation - and reads perfectly plausibly."""
    data = _parsed("A.JPG")
    data["A.JPG"].altitude_asl = 350.0

    compute_agl(data, terrain_service=_Terrain(elevation_m=100.0,
                                               geoid_undulation_m=-26.0))

    # 350 - (-26) - 100 = 276, not 250.
    assert data["A.JPG"].altitude_agl == pytest.approx(276.0)


def test_an_aircraft_is_never_below_ground():
    """A small negative is DEM resolution error, not a subterranean flight."""
    data = _parsed("A.JPG")
    data["A.JPG"].altitude_asl = 95.0

    compute_agl(data, terrain_service=_Terrain(elevation_m=100.0))

    assert data["A.JPG"].altitude_agl == pytest.approx(1.0)


def test_no_dem_coverage_leaves_the_altitude_unset():
    """Reporting zero AGL for an image the DEM cannot answer for would feed
    a zero into GSD; absent is the honest answer."""
    data = _parsed("A.JPG")

    computed = compute_agl(data, terrain_service=_Terrain(source='fallback'))

    assert computed == 0
    assert data["A.JPG"].altitude_agl is None


def test_no_terrain_service_at_all_is_not_an_error(monkeypatch):
    """No DEM cache and no network: the load still succeeds, without AGL.

    ``terrain_service=None`` means "use the shared one", so the shared
    getter is what has to report unavailability - patching it here also
    keeps the test off the network (CLAUDE.md 3.3).
    """
    import core.services.image.WingtraDataService as module
    monkeypatch.setattr(module, 'get_terrain_service', lambda logger=None: None)
    data = _parsed("A.JPG")

    assert compute_agl(data) == 0
    assert data["A.JPG"].altitude_agl is None


def test_every_image_is_queried_once():
    data = _parsed("A.JPG", "B.JPG", "C.JPG")
    terrain = _Terrain()

    assert compute_agl(data, terrain_service=terrain) == 3
    assert len(terrain.queries) == 3


# ---------------------------------------------------------------------------
# kappa_to_bearing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('kappa, bearing', [
    (0.0, 0.0),
    (90.0, 270.0),      # the sign case: CCW photogrammetric -> CW geographic
    (180.0, 180.0),     # agrees either way, which is why the error hides
    (270.0, 90.0),
    (-45.0, 45.0),
    (405.0, 315.0),     # wraps
])
def test_kappa_becomes_a_geographic_bearing(kappa, bearing):
    assert kappa_to_bearing(kappa) == pytest.approx(bearing)


def test_a_bearing_is_always_in_range():
    for kappa in (-720.0, -1.0, 359.9, 1080.0):
        assert 0.0 <= kappa_to_bearing(kappa) < 360.0


# ---------------------------------------------------------------------------
# misc
# ---------------------------------------------------------------------------

def test_error_summaries_are_capped():
    """A malformed export produces one error per row; the operator needs the
    shape of it, not two thousand lines."""
    text = summarize_errors([f"Row {i}: bad" for i in range(25)], limit=10)

    assert text.count("\n") == 10
    assert "and 15 more errors" in text


def test_short_error_lists_are_not_annotated():
    assert summarize_errors(["one", "two"]) == "one\ntwo"


def test_the_feet_conversion_is_the_shared_constant():
    assert METERS_TO_FEET == pytest.approx(3.28084)


# ---------------------------------------------------------------------------
# finding a geotags CSV for the operator
# ---------------------------------------------------------------------------

def _images(folder, *names):
    """Result-image paths in *folder*; the files need not exist for the search."""
    return [str(folder / name) for name in names]


def test_only_the_image_column_of_a_wingtra_csv_is_read(tmp_path):
    path = _write(tmp_path, _row("A.JPG"), _row("B.JPG"))

    assert read_csv_image_names(path) == ["A.JPG", "B.JPG"]


def test_a_csv_missing_a_wingtra_column_is_not_a_geotags_file(tmp_path):
    """A bearing-track CSV has a position but no orientation triple."""
    path = _write(tmp_path, "2026-10-12T10:00:00Z,43.7,-110.7,2190",
                  header="timestamp,latitude,longitude,altitude")

    assert read_csv_image_names(path) is None


def test_an_unreadable_csv_is_not_a_geotags_file(tmp_path):
    path = tmp_path / "binary.csv"
    path.write_bytes(b"\xff\xfe\x00\x81garbage")

    assert read_csv_image_names(str(path)) is None


def test_the_search_covers_each_image_folder_and_its_parent(tmp_path):
    flight_a = tmp_path / "mission" / "flight_a"
    flight_b = tmp_path / "mission" / "flight_b"
    paths = _images(flight_a, "1.JPG", "2.JPG") + _images(flight_b, "3.JPG")

    folders = candidate_folders(paths)

    assert folders == [str(flight_a), str(tmp_path / "mission"), str(flight_b)]


def test_a_geotags_csv_beside_the_images_is_found(tmp_path):
    csv_path = _write(tmp_path, _row("A.JPG"), _row("B.JPG"), _row("C.JPG"),
                      name="Flight 1 geotags.csv")

    found = find_wingtra_csvs(_images(tmp_path, "A.JPG", "B.JPG"), ["A.JPG", "B.JPG"])

    assert len(found) == 1
    assert found[0].path == csv_path
    assert found[0].row_count == 3
    assert found[0].matched_count == 2


def test_a_geotags_csv_one_folder_up_is_found(tmp_path):
    """Operators move the photos into a subfolder; the CSV stays behind."""
    images = tmp_path / "images"
    images.mkdir()
    csv_path = _write(tmp_path, _row("A.JPG"))

    found = find_wingtra_csvs(_images(images, "A.JPG"), ["A.JPG"])

    assert [c.path for c in found] == [csv_path]


def test_names_match_case_insensitively(tmp_path):
    _write(tmp_path, _row("img_0001.jpg"))

    found = find_wingtra_csvs(_images(tmp_path, "IMG_0001.JPG"), ["IMG_0001.JPG"])

    assert len(found) == 1


def test_csvs_that_are_not_geotags_for_these_results_are_not_offered(tmp_path):
    """An unrelated CSV, and a Wingtra CSV from another flight, are both
    left alone - offering them would put the wrong footprints on the map."""
    _write(tmp_path, "1,2,3", header="a,b,c", name="notes.csv")
    _write(tmp_path, _row("OTHER_FLIGHT.JPG"), name="other.csv")

    assert find_wingtra_csvs(_images(tmp_path, "A.JPG"), ["A.JPG"]) == []


def test_the_csv_naming_the_most_results_comes_first(tmp_path):
    _write(tmp_path, _row("A.JPG"), name="partial.csv")
    best = _write(tmp_path, _row("A.JPG"), _row("B.JPG"), name="full.csv")

    found = find_wingtra_csvs(_images(tmp_path, "A.JPG", "B.JPG"), ["A.JPG", "B.JPG"])

    assert [c.path for c in found][0] == best
    assert [c.matched_count for c in found] == [2, 1]


def test_a_missing_folder_is_skipped(tmp_path):
    assert find_wingtra_csvs(_images(tmp_path / "gone", "A.JPG"), ["A.JPG"]) == []


def _jpeg_with_make(tmp_path, make, model=b'RGB61'):
    path = str(tmp_path / "frame.jpg")
    ok, encoded = cv2.imencode('.jpg', np.zeros((8, 8, 3), dtype=np.uint8))
    assert ok
    with open(path, 'wb') as handle:
        handle.write(encoded.tobytes())
    piexif.insert(piexif.dump({'0th': {piexif.ImageIFD.Make: make,
                                       piexif.ImageIFD.Model: model}}), path)
    return path


def test_a_wingtra_payload_is_recognised_by_its_make(tmp_path):
    """The RGB61 pads its Make with NULs; that must not hide it."""
    assert is_wingtra_image(_jpeg_with_make(tmp_path, b'WINGTRA\x00\x00\x00'))


def test_other_makes_are_not_wingtra(tmp_path):
    assert not is_wingtra_image(_jpeg_with_make(tmp_path, b'DJI', b'M3T'))


def test_an_unreadable_image_is_not_wingtra(tmp_path):
    path = tmp_path / "broken.jpg"
    path.write_bytes(b"not a jpeg")

    assert not is_wingtra_image(str(path))
    assert not is_wingtra_image(os.path.join(str(tmp_path), "missing.jpg"))


# ---------------------------------------------------------------------------
# the altitude every surface sizes a Wingtra image with
# ---------------------------------------------------------------------------

def test_the_operator_override_wins():
    assert resolve_altitude_ft({'wingtra_agl_ft': 318.0}, 250.0) == 250.0


def test_a_wingtra_agl_stands_in_without_an_override():
    assert resolve_altitude_ft({'wingtra_agl_ft': 318.0}, None) == 318.0


@pytest.mark.parametrize('image', [None, {}, {'wingtra_agl_ft': None}, {'wingtra_agl_ft': 0.0}])
def test_without_either_the_image_metadata_decides(image):
    """None, not zero: a zero would feed straight into GSD."""
    assert resolve_altitude_ft(image, None) is None
    assert wingtra_agl_ft(image) is None


def test_a_non_positive_override_is_no_override():
    """The altitude dialog stores -1 when the operator declines it."""
    assert resolve_altitude_ft({'wingtra_agl_ft': 318.0}, -1) == 318.0
