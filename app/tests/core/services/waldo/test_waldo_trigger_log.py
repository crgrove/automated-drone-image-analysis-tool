"""Unit tests for WaldoTriggerLogService and its WaldoMetadataService hookup."""

from datetime import datetime, timedelta

import pytest

from core.services.waldo.WaldoMetadataService import (
    WaldoMetadataService,
    WaldoImageRecord,
    WaldoProcessResult,
)
from core.services.waldo.WaldoTriggerLog import (
    TriggerPoint,
    WaldoTriggerLogService,
)


# --------------------------------------------------------------------------
# KML synthesis helpers
# --------------------------------------------------------------------------

KML_HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    '<Document> <name>Test_Triggers</name>\n'
)


def _placemark(name, lat, lon, alt=2400.0):
    # Real files carry a trailing space inside <name> — reproduce it.
    return (
        f'<Placemark> <name>{name} </name> <styleUrl>#whiteDot</styleUrl> '
        f'<Point> <coordinates>{lon:.6f},{lat:.6f},{alt:.2f}</coordinates> '
        f'</Point> </Placemark>\n'
    )


def _write_kml(path, placemarks, close=True):
    text = KML_HEADER + "".join(placemarks)
    if close:
        text += "</Document>\n</kml>\n"
    path.write_text(text, encoding="utf-8")
    return str(path)


# Lane geometry: 0.002 deg latitude ~= 222 m spacing (inside the 600 m
# neighbour guard); 0.02 deg ~= 2.2 km (outside it).
def _lane(lane_idx, frames, lat0, lon, ascending=True):
    marks = []
    for j, frame in enumerate(frames):
        lat = lat0 + (j if ascending else -j) * 0.002
        marks.append((f"000_{lane_idx:02d}_{frame:03d}", lat, lon))
    return marks


# --------------------------------------------------------------------------
# parse_triggers_kml
# --------------------------------------------------------------------------

def test_parse_reads_names_and_coords_in_document_order(tmp_path):
    marks = [_placemark("000_12_000", 41.0, -122.0),
             _placemark("000_12_001", 41.002, -122.0)]
    path = _write_kml(tmp_path / "t.kml", marks)
    points = WaldoTriggerLogService.parse_triggers_kml(path)
    assert [p.name for p in points] == ["000_12_000", "000_12_001"]
    assert points[0].lat == pytest.approx(41.0)
    assert points[0].lon == pytest.approx(-122.0)
    assert points[0].alt == pytest.approx(2400.0)


def test_parse_tolerates_truncated_file(tmp_path):
    # Field Position/Trigger KMLs can end mid-stream with no closing tags.
    marks = [_placemark("000_12_000", 41.0, -122.0)]
    text = KML_HEADER + "".join(marks) + \
        '<Placemark> <name>000_12_001 </name> <Point> <coordinates>-122.000000,41.002'
    path = tmp_path / "trunc.kml"
    path.write_text(text, encoding="utf-8")
    points = WaldoTriggerLogService.parse_triggers_kml(str(path))
    assert len(points) == 2
    assert points[1].lat == pytest.approx(41.002)
    assert points[1].alt is None


def test_parse_skips_linestring_placemarks(tmp_path):
    # Position KMLs hold a LineString track — must not parse as triggers.
    text = KML_HEADER + (
        '<Placemark id="X"> <name>Track</name> <LineString> <coordinates>\n'
        '-122.0,41.0,3000\n-122.0,41.1,3000\n</coordinates> </LineString> </Placemark>\n'
    )
    path = tmp_path / "pos.kml"
    path.write_text(text, encoding="utf-8")
    assert WaldoTriggerLogService.parse_triggers_kml(str(path)) == []


def test_parse_skips_malformed_coordinates(tmp_path):
    marks = [
        _placemark("000_12_000", 41.0, -122.0),
        '<Placemark> <name>bad </name> <Point> <coordinates>not,numbers</coordinates> </Point> </Placemark>\n',
        _placemark("000_12_001", 41.002, -122.0),
    ]
    path = _write_kml(tmp_path / "t.kml", marks)
    points = WaldoTriggerLogService.parse_triggers_kml(path)
    assert [p.name for p in points] == ["000_12_000", "000_12_001"]


def test_parse_unreadable_path_returns_empty(tmp_path):
    assert WaldoTriggerLogService.parse_triggers_kml(str(tmp_path / "nope.kml")) == []


# --------------------------------------------------------------------------
# image_trigger_name
# --------------------------------------------------------------------------

@pytest.mark.parametrize("image,expected", [
    ("0_000_12_035.jpg", "000_12_035"),
    ("1_000_00_002.JPG", "000_00_002"),
    (r"E:\somewhere\1_000_04_019.jpg", "000_04_019"),
    ("DJI_0001.JPG", None),
    ("2_000_00_000.jpg", None),
])
def test_image_trigger_name(image, expected):
    assert WaldoTriggerLogService.image_trigger_name(image) == expected


# --------------------------------------------------------------------------
# headings_by_name
# --------------------------------------------------------------------------

def _points(marks):
    return [TriggerPoint(name=n, lat=lat, lon=lon, alt=None) for n, lat, lon in marks]


def test_headings_serpentine_lanes_get_opposite_directions():
    # Lane 01 flown north (frames ascending), lane 00 flown SOUTH while its
    # frame numbers still ascend geographically north — the serpentine trap.
    lane_a = _lane(1, range(5), 41.0, -122.0, ascending=True)
    lane_b = _lane(0, [4, 3, 2, 1, 0], 41.008, -122.003, ascending=False)
    headings = WaldoTriggerLogService.headings_by_name(_points(lane_a + lane_b))
    for j in range(5):
        assert headings[f"000_01_{j:03d}"] == pytest.approx(0.0, abs=3.0) or \
            headings[f"000_01_{j:03d}"] == pytest.approx(360.0, abs=3.0)
    for j in range(5):
        assert headings[f"000_00_{j:03d}"] == pytest.approx(180.0, abs=3.0)


def test_headings_recaptured_frames_get_recapture_direction():
    # Frames 1-2 of lane 00 were missed on the northbound pass and re-flown
    # SOUTHBOUND at the end of the flight. Their headings must come from the
    # recapture pass, not from where their names sit in the lane.
    lane = _lane(0, [0, 3, 4], 41.0, -122.0, ascending=True)   # 41.000/002/004
    recapture = [("000_00_002", 41.004, -122.0),               # flying south now
                 ("000_00_001", 41.002, -122.0)]
    headings = WaldoTriggerLogService.headings_by_name(_points(lane + recapture))
    assert headings["000_00_000"] == pytest.approx(0.0, abs=3.0)
    assert headings["000_00_002"] == pytest.approx(180.0, abs=3.0)
    assert headings["000_00_001"] == pytest.approx(180.0, abs=3.0)


def test_headings_lane_ends_use_one_sided_bearing():
    # A jump >600 m (0.02 deg) separates two lanes; the triggers flanking the
    # jump must not derive a bearing across it.
    lane_a = _lane(1, range(3), 41.0, -122.0, ascending=True)
    lane_b = _lane(0, range(3), 41.1, -122.003, ascending=True)
    headings = WaldoTriggerLogService.headings_by_name(_points(lane_a + lane_b))
    # Last of lane A and first of lane B still get their own lane's direction.
    assert headings["000_01_002"] == pytest.approx(0.0, abs=3.0)
    assert headings["000_00_000"] == pytest.approx(0.0, abs=3.0)


def test_headings_isolated_trigger_gets_none():
    lane = _lane(1, range(3), 41.0, -122.0, ascending=True)
    isolated = [("000_09_050", 41.5, -122.5)]
    headings = WaldoTriggerLogService.headings_by_name(_points(lane + isolated))
    assert "000_09_050" not in headings
    assert "000_01_001" in headings


def test_headings_stationary_duplicate_neighbour_ignored():
    # A duplicate point (<1 m away) must not produce a degenerate bearing.
    marks = [("000_00_000", 41.0, -122.0),
             ("000_00_001", 41.0, -122.0),
             ("000_00_002", 41.002, -122.0)]
    headings = WaldoTriggerLogService.headings_by_name(_points(marks))
    assert headings["000_00_001"] == pytest.approx(0.0, abs=3.0)


# --------------------------------------------------------------------------
# chronology_fraction
# --------------------------------------------------------------------------

def _rec(name, lat, lon, ts, cam=0, path=None):
    return WaldoImageRecord(path=path or name, name=name, cam_idx=cam,
                            lat=lat, lon=lon, timestamp=ts)


def test_chronology_consistent_timestamps_score_high():
    marks = _lane(0, range(5), 41.0, -122.0, ascending=True)
    t0 = datetime(2026, 7, 23, 6, 30, 0)
    records = [_rec(f"0_{n}.jpg", lat, lon, t0 + timedelta(seconds=4 * j))
               for j, (n, lat, lon) in enumerate(marks)]
    frac = WaldoTriggerLogService.chronology_fraction(_points(marks), records)
    assert frac == pytest.approx(1.0)


def test_chronology_reversed_timestamps_score_low():
    marks = _lane(0, range(5), 41.0, -122.0, ascending=True)
    t0 = datetime(2026, 7, 23, 6, 30, 0)
    records = [_rec(f"0_{n}.jpg", lat, lon, t0 - timedelta(seconds=4 * j))
               for j, (n, lat, lon) in enumerate(marks)]
    frac = WaldoTriggerLogService.chronology_fraction(_points(marks), records)
    assert frac == pytest.approx(0.0)


def test_chronology_too_few_matches_returns_none():
    marks = _lane(0, range(2), 41.0, -122.0, ascending=True)
    t0 = datetime(2026, 7, 23, 6, 30, 0)
    records = [_rec(f"0_{n}.jpg", lat, lon, t0)
               for n, lat, lon in marks]
    assert WaldoTriggerLogService.chronology_fraction(_points(marks), records) is None


# --------------------------------------------------------------------------
# discover
# --------------------------------------------------------------------------

def _flight_layout(tmp_path, marks, kml_name="20260723_65561_Triggers.kml"):
    """Field layout: <root>/<kml> with images two levels down in batch dirs."""
    batch_dir = tmp_path / "20260723_65561" / "batch1"
    batch_dir.mkdir(parents=True)
    kml = _write_kml(tmp_path / kml_name, [_placemark(n, lat, lon) for n, lat, lon in marks])
    records = [_rec(f"0_{n}.jpg", lat, lon, None, path=str(batch_dir / f"0_{n}.jpg"))
               for n, lat, lon in marks]
    return kml, records


def test_discover_finds_kml_levels_above_images(tmp_path):
    marks = _lane(0, range(5), 41.0, -122.0, ascending=True)
    kml, records = _flight_layout(tmp_path, marks)
    found = WaldoTriggerLogService().discover(records)
    assert found is not None
    assert found[0] == kml
    assert len(found[1]) == 5


def test_discover_rejects_name_collision_from_other_flight(tmp_path):
    # A sibling flight's log contains the SAME trigger names at different
    # positions (every flight numbers lanes from zero). GPS proximity must
    # pick the right log.
    marks = _lane(0, range(5), 41.0, -122.0, ascending=True)
    decoy_marks = [(n, lat + 1.0, lon + 1.0) for n, lat, lon in marks]
    kml, records = _flight_layout(tmp_path, marks)
    _write_kml(tmp_path / "20260723_99999_Triggers.kml",
               [_placemark(n, lat, lon) for n, lat, lon in decoy_marks])
    found = WaldoTriggerLogService().discover(records)
    assert found is not None
    assert found[0] == kml


def test_discover_returns_none_without_positional_match(tmp_path):
    marks = _lane(0, range(5), 41.0, -122.0, ascending=True)
    _, records = _flight_layout(tmp_path, marks)
    # Re-write the KML with every trigger displaced ~111 km: names all match
    # but no position does, so the log must be rejected.
    far_marks = [(n, lat + 1.0, lon) for n, lat, lon in marks]
    _write_kml(tmp_path / "20260723_65561_Triggers.kml",
               [_placemark(n, lat, lon) for n, lat, lon in far_marks])
    assert WaldoTriggerLogService().discover(records) is None


def test_discover_returns_none_when_no_kml_exists(tmp_path):
    batch_dir = tmp_path / "flight" / "batch1"
    batch_dir.mkdir(parents=True)
    records = [_rec("0_000_00_000.jpg", 41.0, -122.0, None,
                    path=str(batch_dir / "0_000_00_000.jpg"))]
    assert WaldoTriggerLogService().discover(records) is None


# --------------------------------------------------------------------------
# WaldoMetadataService._apply_trigger_log_headings integration
# --------------------------------------------------------------------------

def test_apply_corrects_flipped_headings_and_warns(tmp_path):
    marks = _lane(0, range(5), 41.0, -122.0, ascending=True)  # truth: north
    _, records = _flight_layout(tmp_path, marks)
    t0 = datetime(2026, 7, 23, 6, 30, 0)
    for j, rec in enumerate(records):
        rec.timestamp = t0 + timedelta(seconds=4 * j)
        rec.heading_deg = 180.0  # timestamp derivation got these flipped

    svc = WaldoMetadataService(terrain_service=None)
    result = WaldoProcessResult()
    svc._apply_trigger_log_headings(records, result)

    for rec in records:
        assert rec.heading_deg == pytest.approx(0.0, abs=3.0) or \
            rec.heading_deg == pytest.approx(360.0, abs=3.0)
    assert any("corrected the flight direction of 5" in w for w in result.warnings)
    assert any("Trigger log" in n and "5 of 5" in n for n in result.notes)


def test_apply_rejects_log_contradicting_timestamps(tmp_path):
    marks = _lane(0, range(5), 41.0, -122.0, ascending=True)
    _, records = _flight_layout(tmp_path, marks)
    t0 = datetime(2026, 7, 23, 6, 30, 0)
    for j, rec in enumerate(records):
        rec.timestamp = t0 - timedelta(seconds=4 * j)  # doc order backwards
        rec.heading_deg = 123.0

    svc = WaldoMetadataService(terrain_service=None)
    result = WaldoProcessResult()
    svc._apply_trigger_log_headings(records, result)

    assert all(rec.heading_deg == 123.0 for rec in records)
    assert any("ignored" in w for w in result.warnings)
    assert result.notes == []


def test_apply_no_kml_is_a_quiet_noop(tmp_path):
    batch_dir = tmp_path / "flight" / "batch1"
    batch_dir.mkdir(parents=True)
    records = [_rec("0_000_00_000.jpg", 41.0, -122.0,
                    datetime(2026, 7, 23, 6, 30, 0),
                    path=str(batch_dir / "0_000_00_000.jpg"))]
    records[0].heading_deg = 77.0

    svc = WaldoMetadataService(terrain_service=None)
    result = WaldoProcessResult()
    svc._apply_trigger_log_headings(records, result)

    assert records[0].heading_deg == 77.0
    assert result.warnings == []
    assert result.notes == []
