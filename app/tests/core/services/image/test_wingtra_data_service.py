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

from types import SimpleNamespace

import pytest

from core.services.image.WingtraDataService import (
    METERS_TO_FEET,
    WingtraImageData,
    build_column_map,
    compute_agl,
    kappa_to_bearing,
    match_image_names,
    parse_wingtra_csv,
    summarize_errors,
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
