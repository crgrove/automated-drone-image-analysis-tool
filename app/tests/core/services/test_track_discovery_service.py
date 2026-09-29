"""Unit tests for TrackDiscoveryService."""

from unittest.mock import patch

import importlib

from core.services.TrackDiscoveryService import (
    TrackDiscoveryService,
    TRACK_MIN_POINTS,
)

track_module = importlib.import_module("core.services.TrackDiscoveryService")

# The flight under test: a north-running line near 41.0, -122.0.
FLIGHT_LAT, FLIGHT_LON = 41.0, -122.0


def _write_track_csv(path, lat0, lon0, n=30):
    """A tracklog CSV in the shape BearingCalculationService accepts."""
    lines = ["timestamp,lat,lon"]
    for i in range(n):
        lines.append(f"2026-06-01T10:{i % 60:02d}:00Z,{lat0 + i * 0.001:.6f},{lon0:.6f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def _fake_images(tmp_path, count=6):
    """Dummy image files (existence-checked by the sampler) with GPS by index."""
    paths = []
    for i in range(count):
        p = tmp_path / f"0_000_00_{i:03d}.jpg"
        p.write_text("x")
        paths.append(str(p))
    return paths


def _gps_along_flight(count=6):
    """Image GPS positions lying on the flight line."""
    return {
        i: {'latitude': FLIGHT_LAT + i * 0.004, 'longitude': FLIGHT_LON}
        for i in range(count)
    }


def _patched_gps(paths, positions):
    """Patch LocationInfo.get_gps to answer from *positions* by path index."""
    by_path = {p: positions.get(i) for i, p in enumerate(paths)}

    def fake_get_gps(exif_data=None, full_path=None):
        return by_path.get(full_path)

    return patch.object(track_module.LocationInfo, 'get_gps',
                        staticmethod(fake_get_gps))


def test_matching_track_is_discovered(tmp_path):
    images = _fake_images(tmp_path)
    good = _write_track_csv(tmp_path / "foreflight_tracklog.csv",
                            FLIGHT_LAT, FLIGHT_LON)
    with _patched_gps(images, _gps_along_flight()):
        found = TrackDiscoveryService().discover_track(images, [good])
    assert found == good


def test_wrong_flight_track_is_rejected(tmp_path):
    images = _fake_images(tmp_path)
    # ~55 km north of the imagery - another day's mission.
    wrong = _write_track_csv(tmp_path / "other_flight.csv",
                             FLIGHT_LAT + 0.5, FLIGHT_LON)
    with _patched_gps(images, _gps_along_flight()):
        found = TrackDiscoveryService().discover_track(images, [wrong])
    assert found is None


def test_best_of_multiple_candidates_wins(tmp_path):
    images = _fake_images(tmp_path)
    wrong = _write_track_csv(tmp_path / "other_flight.csv",
                             FLIGHT_LAT + 0.5, FLIGHT_LON)
    good = _write_track_csv(tmp_path / "tracklog.csv", FLIGHT_LAT, FLIGHT_LON)
    with _patched_gps(images, _gps_along_flight()):
        found = TrackDiscoveryService().discover_track(images, [wrong, good])
    assert found == good


def test_unparseable_candidate_is_skipped_silently(tmp_path):
    images = _fake_images(tmp_path)
    junk = tmp_path / "detections.csv"
    junk.write_text("image,x,y\na.jpg,1,2\n", encoding="utf-8")
    good = _write_track_csv(tmp_path / "tracklog.csv", FLIGHT_LAT, FLIGHT_LON)
    with _patched_gps(images, _gps_along_flight()):
        found = TrackDiscoveryService().discover_track(
            images, [str(junk), good])
    assert found == good


def test_short_track_is_not_a_tracklog(tmp_path):
    images = _fake_images(tmp_path)
    stub = _write_track_csv(tmp_path / "stub.csv", FLIGHT_LAT, FLIGHT_LON,
                            n=TRACK_MIN_POINTS - 1)
    with _patched_gps(images, _gps_along_flight()):
        assert TrackDiscoveryService().discover_track(images, [stub]) is None


def test_too_few_image_positions_offers_nothing(tmp_path):
    """Under 3 GPS samples there is no evidence base - never guess."""
    images = _fake_images(tmp_path)
    good = _write_track_csv(tmp_path / "tracklog.csv", FLIGHT_LAT, FLIGHT_LON)
    two_only = {i: pos for i, pos in _gps_along_flight().items() if i < 2}
    with _patched_gps(images, two_only):
        assert TrackDiscoveryService().discover_track(images, [good]) is None


def test_missing_image_files_are_ignored(tmp_path):
    good = _write_track_csv(tmp_path / "tracklog.csv", FLIGHT_LAT, FLIGHT_LON)
    ghosts = [str(tmp_path / f"gone_{i}.jpg") for i in range(6)]
    with _patched_gps(ghosts, _gps_along_flight()):
        assert TrackDiscoveryService().discover_track(ghosts, [good]) is None
