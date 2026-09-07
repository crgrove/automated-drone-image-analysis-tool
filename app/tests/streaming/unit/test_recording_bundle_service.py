"""Unit tests for RecordingBundleService (deriving a bundle's artifacts)."""

import csv
import json
import os
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from core.services.streaming.RecordingBundleService import (
    DETECTIONS_CSV,
    find_bundle_for_video,
    load_replay_detections,
    write_replay_srt,
    FLIGHT_MAP_HTML,
    FLIGHT_PATH_KML,
    RESULTS_XML,
    TELEMETRY_CSV,
    build_aoi,
    finalize_bundle,
)
from core.services.streaming.RecordingSessionService import (
    DetectionRecord,
    RecordingSessionConfig,
    RecordingSessionWriter,
    read_manifest,
)


def _thumbnail(width=40, height=30):
    return np.full((height, width, 3), 200, dtype=np.uint8)


def _record(seq=0, lat=30.1, lon=-97.2, **overrides):
    payload = dict(
        track_id=seq,
        bbox=(100, 120, 20, 24),
        centroid=(110, 132),
        confidence=0.75,
        detection_type="person",
        pixel_area=380.0,
        frame_resolution=(1280, 720),
        first_frame_index=150 + seq,
        video_time_seconds=5.0 + seq,
        recorded_frame_index=148 + seq,
        latitude=lat,
        longitude=lon,
        detection_color=(10, 20, 30),
        thumbnail=_thumbnail(),
        thumbnail_origin=(90, 108),
    )
    payload.update(overrides)
    return DetectionRecord(**payload)


def _build_bundle(tmp_path, *, detections=(), fixes=(), with_video=False, **config_overrides):
    """Run a real capture session, then return its finalized bundle path."""
    config = RecordingSessionConfig(
        root_dir=str(tmp_path),
        algorithm="ColorAnomalyAndMotionDetection",
        algorithm_options={"threshold": 12},
        source_url="C:/flights/dji.mp4",
        source_type="File",
        resolution=(1280, 720),
    )
    for key, value in config_overrides.items():
        setattr(config, key, value)

    writer = RecordingSessionWriter()
    bundle = writer.start_session(config)
    assert bundle is not None
    if with_video:
        # A placeholder MP4 so the manifest lists a video file - the
        # replay SRT is named after it and written beside it.
        with open(os.path.join(bundle, "rec_0001.mp4"), "wb") as fp:
            fp.write(b"\x00")
    for record in detections:
        writer.append_detection(record)
    for fix in fixes:
        writer.append_telemetry(fix)
    writer.note_frame(2)
    writer.finalize()
    return bundle


def _fix(lat, lon, seconds=0.0):
    return {
        "aircraft_latitude": lat,
        "aircraft_longitude": lon,
        "aircraft_altitude_agl_m": 40.0,
        "aircraft_altitude_msl_m": 320.0,
        "aircraft_yaw_deg": 91.5,
        "video_time_seconds": seconds,
        "captured_at_ms": int(seconds * 1000),
        "agl_source": "reported",
    }


class TestAoiProjection:
    """The exported AOI has to land on the saved thumbnail crop."""

    def test_center_is_relative_to_the_crop_origin(self):
        aoi = build_aoi({
            "seq": 0,
            "bbox": [100, 120, 20, 24],
            "thumbnail_origin": [90, 108],
            "thumbnail_size": [40, 30],
            "pixel_area": 380.0,
        })

        # bbox center is (110, 132) in the frame; the crop starts at (90, 108).
        assert aoi["center"] == (20, 24)
        assert aoi["radius"] == 10
        assert aoi["area"] == 380
        assert aoi["number"] == 1

    def test_center_is_clamped_into_the_thumbnail(self):
        """A crop clamped at a frame edge can push the center off-image."""
        aoi = build_aoi({
            "seq": 3,
            "bbox": [0, 0, 400, 400],
            "thumbnail_origin": [0, 0],
            "thumbnail_size": [40, 30],
        })

        assert aoi["center"] == (39, 29)

    def test_missing_geometry_falls_back_without_raising(self):
        aoi = build_aoi({"seq": 0})

        assert aoi["center"] == (0, 0)
        assert aoi["radius"] == 20
        assert aoi["area"] == 100

    def test_comment_carries_type_time_and_position(self):
        aoi = build_aoi({
            "seq": 0,
            "bbox": [10, 10, 8, 8],
            "detection_type": "person",
            "video_time_seconds": 125.0,
            "latitude": 30.5,
            "longitude": -97.5,
        })

        assert "person" in aoi["user_comment"]
        assert "2:05" in aoi["user_comment"]
        assert "30.500000, -97.500000" in aoi["user_comment"]

    def test_unknown_crop_geometry_centers_on_the_thumbnail(self):
        """ADIAT Flight thumbs are cropped on the mobile publisher.

        Their crop origin is unknown, so projecting the frame-space bbox
        into them lands the marker nowhere meaningful - the crop is
        centered on the detection by construction, so its own center is
        the right placement.
        """
        aoi = build_aoi({
            "seq": 0,
            "bbox": [320, 360, 128, 144],       # frame pixels, valid
            "thumbnail_origin": None,            # crop geometry unknown
            "thumbnail_size": [160, 120],
            "pixel_area": 500.0,
        })

        assert aoi["center"] == (80, 60)
        assert aoi["area"] == 500

    def test_confidence_becomes_a_score(self):
        aoi = build_aoi({"seq": 0, "bbox": [10, 10, 8, 8], "confidence": 0.62})

        assert aoi["confidence"] == 0.62
        assert aoi["score_type"] == "confidence"
        assert aoi["score_method"] == "StreamingRecording"


class TestDetectionArtifacts:
    """detections.csv and ADIAT_Data.xml."""

    def test_csv_has_one_row_per_detection(self, tmp_path):
        bundle = _build_bundle(tmp_path, detections=[_record(0), _record(1)])
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["detections_csv"] == DETECTIONS_CSV
        with open(os.path.join(bundle, DETECTIONS_CSV), encoding="utf-8", newline="") as fp:
            rows = list(csv.DictReader(fp))
        assert len(rows) == 2
        assert rows[0]["detection_type"] == "person"
        assert rows[0]["bbox_x"] == "100"
        assert rows[0]["bbox_w"] == "20"
        assert float(rows[0]["latitude"]) == pytest.approx(30.1)
        assert rows[1]["recorded_frame_index"] == "149"

    def test_results_xml_is_readable_by_xmlservice(self, tmp_path):
        """The whole point of the XML is that the Images window can load it."""
        from core.services.XmlService import XmlService

        bundle = _build_bundle(tmp_path, detections=[_record(0), _record(1)])
        finalize_bundle(bundle, exports=True)

        xml_path = os.path.join(bundle, RESULTS_XML)
        assert os.path.isfile(xml_path)

        service = XmlService(xml_path)
        settings, image_count = service.get_settings()
        assert settings["algorithm"] == "ColorAnomalyAndMotionDetection"
        assert image_count == 2

        images = service.get_images()
        assert len(images) == 2
        for image in images:
            assert len(image["areas_of_interest"]) == 1
            assert os.path.isfile(image["path"])

    def test_results_xml_survives_the_bundle_being_moved(self, tmp_path):
        """A bundle copied to a team drive still has to open."""
        import shutil

        from core.services.XmlService import XmlService

        bundle = _build_bundle(tmp_path, detections=[_record(0)])
        finalize_bundle(bundle, exports=True)

        moved = str(tmp_path / "copied_bundle")
        shutil.copytree(bundle, moved)
        shutil.rmtree(bundle)

        images = XmlService(os.path.join(moved, RESULTS_XML)).get_images()
        assert len(images) == 1
        assert os.path.isfile(images[0]["path"])
        assert moved in images[0]["path"]

    def test_results_xml_records_provenance_options(self, tmp_path):
        bundle = _build_bundle(tmp_path, detections=[_record(0)])
        finalize_bundle(bundle, exports=True)

        root = ET.parse(os.path.join(bundle, RESULTS_XML)).getroot()
        options = {
            option.get("name"): option.get("value")
            for option in root.findall("./settings/options/option")
        }
        assert options["source"] == "ADIAT Streaming Recording"
        assert options["stream_type"] == "File"
        assert options["algorithm.threshold"] == "12"

    def test_detection_without_a_thumbnail_is_skipped_in_xml_but_kept_in_csv(self, tmp_path):
        bundle = _build_bundle(
            tmp_path, detections=[_record(0), _record(1, thumbnail=None)]
        )
        finalize_bundle(bundle, exports=True)

        root = ET.parse(os.path.join(bundle, RESULTS_XML)).getroot()
        assert len(root.findall("./images/image")) == 1
        with open(os.path.join(bundle, DETECTIONS_CSV), encoding="utf-8", newline="") as fp:
            assert len(list(csv.DictReader(fp))) == 2

    def test_no_detections_writes_no_detection_artifacts(self, tmp_path):
        bundle = _build_bundle(tmp_path, fixes=[_fix(30.0, -97.0)])
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["detections_csv"] is None
        assert result["artifacts"]["results_xml"] is None
        assert not os.path.exists(os.path.join(bundle, RESULTS_XML))


class TestFlightFeedBundles:
    """A flight-shaped record travels the whole derive pipeline."""

    def _flight_record(self, seq=0):
        import cv2
        ok, buf = cv2.imencode(".jpg", np.full((30, 40, 3), 210, dtype=np.uint8))
        assert ok
        from core.services.streaming.RecordingSessionService import (
            detection_record_from_flight_envelope,
        )
        return detection_record_from_flight_envelope(
            {
                "track_key": f"person|sess|{seq}",
                "class_name": "person",
                "confidence": 0.9,
                "captured_at_ms": 1_787_300_000_000 + seq,
                "bbox_norm": [0.25, 0.5, 0.1, 0.2],
                "location": {"lat": 30.25 + seq * 0.001, "lon": -97.75},
                "thumb_bytes": buf.tobytes(),
            },
            recorded_frame_index=30 + seq,
            frame_bgr=np.zeros((720, 1280, 3), dtype=np.uint8),
        )

    def test_flight_detections_reach_csv_xml_and_map(self, tmp_path):
        bundle = _build_bundle(
            tmp_path,
            detections=[self._flight_record(0), self._flight_record(1)],
            fixes=[_fix(30.25, -97.75, 0.0), _fix(30.26, -97.76, 1.0)],
        )
        result = finalize_bundle(bundle, exports=True)

        with open(os.path.join(bundle, DETECTIONS_CSV), encoding="utf-8", newline="") as fp:
            rows = list(csv.DictReader(fp))
        assert rows[0]["track_key"] == "person|sess|0"
        assert rows[0]["captured_at_ms"] == "1787300000000"
        assert float(rows[0]["latitude"]) == pytest.approx(30.25)

        # The XML re-opens with the mobile thumbs as its images.
        from core.services.XmlService import XmlService
        images = XmlService(os.path.join(bundle, RESULTS_XML)).get_images()
        assert len(images) == 2
        assert os.path.isfile(images[0]["path"])

        # The map pins at the publisher's geotag.
        page = open(os.path.join(bundle, FLIGHT_MAP_HTML), encoding="utf-8").read()
        assert "30.251" in page
        assert result["counts"]["detections_geotagged"] == 2


class TestFlightArtifacts:
    """telemetry.csv, flight_map.html and flight_path.kml."""

    def test_telemetry_csv_written(self, tmp_path):
        bundle = _build_bundle(
            tmp_path, fixes=[_fix(30.0, -97.0, 0.0), _fix(30.01, -97.01, 1.0)]
        )
        finalize_bundle(bundle, exports=True)

        with open(os.path.join(bundle, TELEMETRY_CSV), encoding="utf-8", newline="") as fp:
            rows = list(csv.DictReader(fp))
        assert len(rows) == 2
        assert float(rows[1]["aircraft_latitude"]) == pytest.approx(30.01)
        assert rows[0]["agl_source"] == "reported"

    def test_telemetry_csv_carries_every_altitude_reference(self, tmp_path):
        """All three references reach the CSV, and stay in their own column.

        The writer uses ``extrasaction="ignore"``, so a key the column
        list forgets is dropped without a word - which is how
        ``terrain_elevation_m`` went missing before. A detection carries no
        altitude of its own; it reaches these values by joining
        ``detections.csv`` to this file on ``video_time_seconds``, so a
        missing column costs the join too.
        """
        fix = _fix(30.0, -97.0, 0.0)
        fix["aircraft_altitude_agl_terrain_m"] = 31.5
        fix["terrain_elevation_m"] = 288.5
        fix["agl_source"] = "terrain"
        bundle = _build_bundle(tmp_path, fixes=[fix])
        finalize_bundle(bundle, exports=True)

        with open(os.path.join(bundle, TELEMETRY_CSV), encoding="utf-8", newline="") as fp:
            row = next(csv.DictReader(fp))

        assert float(row["aircraft_altitude_msl_m"]) == pytest.approx(320.0)
        # ATO and AGL are different numbers in different columns.
        assert float(row["aircraft_altitude_agl_m"]) == pytest.approx(40.0)
        assert float(row["aircraft_altitude_agl_terrain_m"]) == pytest.approx(31.5)
        assert float(row["terrain_elevation_m"]) == pytest.approx(288.5)
        assert row["agl_source"] == "terrain"

    def test_a_flight_session_leaves_the_terrain_columns_blank(self, tmp_path):
        """ADIAT Flight supplies AGL, so desktop takes no DEM sample.

        Documented rather than fixed: skipping the lookups is the point of
        trusting Flight's measured AGL, and the operator gets the AGL
        itself either way.
        """
        fix = _fix(30.0, -97.0, 0.0)
        fix["aircraft_altitude_agl_terrain_m"] = 31.5
        fix["agl_source"] = "flight"
        bundle = _build_bundle(tmp_path, fixes=[fix])
        finalize_bundle(bundle, exports=True)

        with open(os.path.join(bundle, TELEMETRY_CSV), encoding="utf-8", newline="") as fp:
            row = next(csv.DictReader(fp))

        assert float(row["aircraft_altitude_agl_terrain_m"]) == pytest.approx(31.5)
        assert row["terrain_elevation_m"] == ""

    def test_flight_map_contains_path_and_pins(self, tmp_path):
        bundle = _build_bundle(
            tmp_path,
            detections=[_record(0, lat=30.005, lon=-97.005)],
            fixes=[_fix(30.0, -97.0, 0.0), _fix(30.01, -97.01, 1.0)],
        )
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["flight_map_html"] == FLIGHT_MAP_HTML
        page = open(os.path.join(bundle, FLIGHT_MAP_HTML), encoding="utf-8").read()
        assert "30.005" in page
        assert "-97.01" in page
        assert "ColorAnomalyAndMotionDetection" in page

    def test_flight_kml_has_a_path_and_a_placemark(self, tmp_path):
        bundle = _build_bundle(
            tmp_path,
            detections=[_record(0)],
            fixes=[_fix(30.0, -97.0, 0.0), _fix(30.01, -97.01, 1.0)],
        )
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["flight_path_kml"] == FLIGHT_PATH_KML
        kml = open(os.path.join(bundle, FLIGHT_PATH_KML), encoding="utf-8").read()
        assert "LineString" in kml
        assert "Flight Path" in kml
        assert "person #1" in kml

    def test_no_telemetry_skips_map_and_kml(self, tmp_path):
        """A source with no location data produces no flight artifacts."""
        bundle = _build_bundle(
            tmp_path, detections=[_record(0, lat=None, lon=None)]
        )
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["flight_map_html"] is None
        assert result["artifacts"]["flight_path_kml"] is None
        assert result["artifacts"]["telemetry_csv"] is None
        # ...but the detections were still stored.
        assert result["artifacts"]["detections_csv"] == DETECTIONS_CSV

    def test_geotagged_detections_alone_still_produce_a_map(self, tmp_path):
        """A live feed can geotag detections before any path accumulates."""
        bundle = _build_bundle(tmp_path, detections=[_record(0)])
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["flight_map_html"] == FLIGHT_MAP_HTML

    def test_declining_the_map_suppresses_it_entirely(self, tmp_path):
        """Detections are geotagged regardless, so the choice must be honoured.

        Without this the map and KML were still written from the geotagged
        detections even with "Save flight map" unchecked.
        """
        bundle = _build_bundle(
            tmp_path, detections=[_record(0)], save_flight_map=False
        )
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["flight_map_html"] is None
        assert result["artifacts"]["flight_path_kml"] is None
        assert not os.path.exists(os.path.join(bundle, FLIGHT_MAP_HTML))
        assert not os.path.exists(os.path.join(bundle, FLIGHT_PATH_KML))
        # The detections themselves are unaffected.
        assert result["artifacts"]["detections_csv"] == DETECTIONS_CSV

    def test_a_manifestless_bundle_still_gets_its_map(self, tmp_path):
        """Crash recovery must not read a missing option as a refusal."""
        bundle = _build_bundle(tmp_path, detections=[_record(0)])
        os.remove(os.path.join(bundle, "manifest.json"))

        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["flight_map_html"] == FLIGHT_MAP_HTML


class TestFlightPathOrdering:
    """The drawn path is the route flown, not the order it was watched in."""

    def test_scrubbed_playback_is_reordered_by_video_time(self, tmp_path):
        from core.services.streaming.RecordingBundleService import _coords
        from core.services.streaming.RecordingSessionService import (
            TELEMETRY_LOG, read_jsonl,
        )

        # Recorded while the operator jumped back and forth in the file.
        bundle = _build_bundle(tmp_path, fixes=[
            _fix(30.2, -97.2, 20.0),
            _fix(30.0, -97.0, 0.0),
            _fix(30.1, -97.1, 10.0),
        ])
        rows = read_jsonl(os.path.join(bundle, TELEMETRY_LOG))

        assert _coords(rows) == [(30.0, -97.0), (30.1, -97.1), (30.2, -97.2)]

    def test_live_fixes_keep_their_arrival_order(self):
        from core.services.streaming.RecordingBundleService import _coords

        # A live feed carries no video time; order as logged is the truth.
        rows = [
            {"aircraft_latitude": 30.2, "aircraft_longitude": -97.2},
            {"aircraft_latitude": 30.0, "aircraft_longitude": -97.0},
        ]

        assert _coords(rows) == [(30.2, -97.2), (30.0, -97.0)]

    def test_repeated_positions_collapse(self):
        from core.services.streaming.RecordingBundleService import _coords

        rows = [
            {"aircraft_latitude": 30.0, "aircraft_longitude": -97.0},
            {"aircraft_latitude": 30.0, "aircraft_longitude": -97.0},
            {"aircraft_latitude": 30.1, "aircraft_longitude": -97.1},
            {"aircraft_latitude": 30.0, "aircraft_longitude": -97.0},
        ]

        # Only *consecutive* repeats go: revisiting a spot is real movement.
        assert _coords(rows) == [(30.0, -97.0), (30.1, -97.1), (30.0, -97.0)]

    def test_partial_video_times_are_not_reordered(self):
        """A mixed log has no single timeline to sort on."""
        from core.services.streaming.RecordingBundleService import _coords

        rows = [
            {"aircraft_latitude": 30.2, "aircraft_longitude": -97.2, "video_time_seconds": 20.0},
            {"aircraft_latitude": 30.0, "aircraft_longitude": -97.0},
        ]

        assert _coords(rows) == [(30.2, -97.2), (30.0, -97.0)]

    def test_telemetry_csv_keeps_every_raw_row(self, tmp_path):
        """Tidying the path must not tidy the record it came from."""
        bundle = _build_bundle(tmp_path, fixes=[
            _fix(30.0, -97.0, 0.0),
            _fix(30.0, -97.0, 1.0),
            _fix(30.1, -97.1, 2.0),
        ])
        finalize_bundle(bundle, exports=True)

        with open(os.path.join(bundle, TELEMETRY_CSV), encoding="utf-8", newline="") as fp:
            assert len(list(csv.DictReader(fp))) == 3


class TestReplaySrt:
    """The sidecar SRT that makes a recorded MP4 replay its telemetry."""

    def _fixes(self):
        return [_fix(30.25 + i * 0.001, -97.75 - i * 0.001, float(i)) for i in range(4)]

    @staticmethod
    def _spread_stamps(bundle, seconds_apart=1.0):
        """Restamp the fix log so cues sit N seconds apart.

        The writer stamps ``recorded_at_epoch_s`` at append time, and a
        test appends all its fixes within microseconds - which would
        collapse every cue to t=0.
        """
        import json

        from core.services.streaming.RecordingSessionService import (
            TELEMETRY_LOG,
            read_jsonl,
        )

        started = read_manifest(bundle)["started_at_epoch_s"]
        rows = read_jsonl(os.path.join(bundle, TELEMETRY_LOG))
        for index, row in enumerate(rows):
            row["recorded_at_epoch_s"] = started + index * seconds_apart
        with open(os.path.join(bundle, TELEMETRY_LOG), "w", encoding="utf-8") as fp:
            fp.write("\n".join(json.dumps(r) for r in rows) + "\n")

    def test_srt_round_trips_through_the_real_parser(self, tmp_path):
        from core.services.telemetry.TelemetrySourceResolver import (
            find_sidecar_srt,
            read_srt_track,
        )

        bundle = _build_bundle(tmp_path, fixes=self._fixes(), with_video=True)
        self._spread_stamps(bundle)
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["replay_srt"] == "rec_0001.SRT"
        # The ordinary sidecar discovery finds it next to the video...
        sidecar = find_sidecar_srt(os.path.join(bundle, "rec_0001.mp4"))
        assert sidecar is not None
        # ...and the ordinary DJI parser reads it back.
        track = read_srt_track(sidecar, source="sidecar")
        assert track is not None and len(track) == 4
        point = track.point_at(1.2)
        assert point.latitude == pytest.approx(30.251, abs=1e-6)
        assert point.altitude_ato_m == pytest.approx(40.0)   # ATO from the fix
        assert point.altitude_msl_m == pytest.approx(320.0)
        assert point.yaw_deg == pytest.approx(91.5)

    def test_cue_times_are_relative_to_recording_start(self, tmp_path):
        """A live feed has no source timeline; the recording's own start is t=0."""
        import json

        bundle = _build_bundle(tmp_path, fixes=self._fixes(), with_video=True)
        # Rewrite the stamps so fixes land 2.5s and 7s after start.
        manifest = read_manifest(bundle)
        started = manifest["started_at_epoch_s"]
        rows = []
        from core.services.streaming.RecordingSessionService import TELEMETRY_LOG, read_jsonl
        for offset, row in zip((2.5, 7.0), read_jsonl(os.path.join(bundle, TELEMETRY_LOG))[:2]):
            row["recorded_at_epoch_s"] = started + offset
            rows.append(row)
        with open(os.path.join(bundle, TELEMETRY_LOG), "w", encoding="utf-8") as fp:
            fp.write("\n".join(json.dumps(r) for r in rows) + "\n")

        finalize_bundle(bundle, exports=True)

        srt = open(os.path.join(bundle, "rec_0001.SRT"), encoding="utf-8").read()
        assert "00:00:02,500 -->" in srt
        assert "00:00:07,000 -->" in srt

    def test_cues_prefer_the_recorded_videos_clock(self, tmp_path):
        """An outage splices out of the video; the SRT must compress with it.

        Wall stamps here show a 45-second gap between fixes, but the
        writer's clock shows them one recorded second apart - because
        nothing was written during the outage. Cue times must follow the
        writer, or the HUD would lag the picture by 45s after the gap.
        """
        import json

        from core.services.streaming.RecordingSessionService import (
            TELEMETRY_LOG,
            read_jsonl,
        )

        bundle = _build_bundle(tmp_path, fixes=self._fixes()[:2], with_video=True)
        started = read_manifest(bundle)["started_at_epoch_s"]
        rows = read_jsonl(os.path.join(bundle, TELEMETRY_LOG))
        # Fix 0 at wall t=1s; fix 1 at wall t=46s (a 45s outage between).
        for row, wall, recorded in zip(rows, (1.0, 46.0), (1.0, 2.0)):
            row["recorded_at_epoch_s"] = started + wall
            row["recorded_video_seconds"] = recorded
            row["recorded_frame_index"] = int(recorded * 30)
        with open(os.path.join(bundle, TELEMETRY_LOG), "w", encoding="utf-8") as fp:
            fp.write("\n".join(json.dumps(r) for r in rows) + "\n")

        finalize_bundle(bundle, exports=True)

        srt = open(os.path.join(bundle, "rec_0001.SRT"), encoding="utf-8").read()
        assert "00:00:01,000 -->" in srt
        assert "00:00:02,000 -->" in srt      # one recorded second later...
        assert "00:00:46,000" not in srt      # ...not 45 wall seconds later

    def test_fixes_without_the_stamp_fall_back_to_wall_clock(self, tmp_path):
        """Bundles recorded before the stamp existed still get an SRT."""
        bundle = _build_bundle(tmp_path, fixes=self._fixes(), with_video=True)
        self._spread_stamps(bundle)

        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["replay_srt"] == "rec_0001.SRT"

    def test_no_telemetry_writes_no_srt(self, tmp_path):
        bundle = _build_bundle(tmp_path, detections=[_record(0)], with_video=True)
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["replay_srt"] is None
        assert not os.path.isfile(os.path.join(bundle, "rec_0001.SRT"))

    def test_no_video_file_writes_no_srt(self, tmp_path):
        """Nothing to replay against - a failed video start, say."""
        bundle = _build_bundle(tmp_path, fixes=self._fixes(), with_video=False)
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["replay_srt"] is None

    def test_multi_segment_recording_covers_the_first_segment(self, tmp_path):
        bundle = _build_bundle(tmp_path, fixes=self._fixes(), with_video=True)
        with open(os.path.join(bundle, "rec_0002.mp4"), "wb") as fp:
            fp.write(b"\x00")

        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["replay_srt"] == "rec_0001.SRT"
        assert not os.path.isfile(os.path.join(bundle, "rec_0002.SRT"))

    def test_partial_altitudes_still_produce_cues(self, tmp_path):
        fixes = [{
            "aircraft_latitude": 30.0,
            "aircraft_longitude": -97.0,
            # No altitudes at all - position alone is still a trail.
        }]
        bundle = _build_bundle(tmp_path, fixes=fixes, with_video=True)
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["replay_srt"] == "rec_0001.SRT"
        srt = open(os.path.join(bundle, "rec_0001.SRT"), encoding="utf-8").read()
        assert "[latitude: 30.000000]" in srt
        assert "rel_alt" not in srt


class TestReplayLoading:
    """Locating a bundle from its video and loading the stored detections."""

    def test_video_inside_a_bundle_is_recognized(self, tmp_path):
        bundle = _build_bundle(tmp_path, detections=[_record(0)], with_video=True)
        finalize_bundle(bundle, exports=True)

        assert find_bundle_for_video(os.path.join(bundle, "rec_0001.mp4")) == bundle

    def test_ordinary_videos_are_not_bundles(self, tmp_path):
        loose = tmp_path / "DJI_0042.MP4"
        loose.write_bytes(b"\x00")

        assert find_bundle_for_video(str(loose)) is None
        assert find_bundle_for_video("") is None

    def test_detections_load_with_resolved_thumbnails(self, tmp_path):
        bundle = _build_bundle(
            tmp_path, detections=[_record(0), _record(1, thumbnail=None)], with_video=True
        )
        finalize_bundle(bundle, exports=True)

        rows = load_replay_detections(bundle)

        assert len(rows) == 2
        assert os.path.isfile(rows[0]["thumbnail_path"])
        assert rows[0]["recorded_frame_index"] == 148
        assert rows[0]["latitude"] == pytest.approx(30.1)
        # The thumbless row loads too - just with no image to show.
        assert "thumbnail_path" not in rows[1]


class TestDefaultFootprint:
    """A recording's default footprint is the minimal replay set."""

    def test_default_finalize_writes_no_export_files(self, tmp_path):
        bundle = _build_bundle(
            tmp_path,
            detections=[_record(0)],
            fixes=[_fix(30.0, -97.0), _fix(30.1, -97.1)],
            with_video=True,
        )

        result = finalize_bundle(bundle)

        # The replay essentials are present...
        assert result["artifacts"]["replay_srt"] == "rec_0001.SRT"
        assert os.path.isfile(os.path.join(bundle, "detections", "detection_0000.jpg"))
        # ...and none of the export artifacts are.
        for name in (DETECTIONS_CSV, RESULTS_XML, TELEMETRY_CSV,
                     FLIGHT_MAP_HTML, FLIGHT_PATH_KML):
            assert not os.path.exists(os.path.join(bundle, name)), name

    def test_export_bundle_adds_the_shareable_files_later(self, tmp_path):
        """The Replay window's Export button, as a service call."""
        from core.services.streaming.RecordingBundleService import export_bundle

        bundle = _build_bundle(
            tmp_path,
            detections=[_record(0)],
            fixes=[_fix(30.0, -97.0), _fix(30.1, -97.1)],
            with_video=True,
        )
        finalize_bundle(bundle)

        result = export_bundle(bundle)

        for name in (DETECTIONS_CSV, RESULTS_XML, TELEMETRY_CSV,
                     FLIGHT_MAP_HTML, FLIGHT_PATH_KML):
            assert os.path.isfile(os.path.join(bundle, name)), name
        # The manifest carries both waves of artifacts.
        manifest = read_manifest(bundle)
        assert manifest["artifacts"]["replay_srt"] == "rec_0001.SRT"
        assert manifest["artifacts"]["results_xml"] == RESULTS_XML
        assert result["errors"] == []


class TestManifestAndErrors:
    """The manifest describes the finished bundle."""

    def test_manifest_lists_artifacts_and_counts(self, tmp_path):
        bundle = _build_bundle(
            tmp_path,
            detections=[_record(0), _record(1, lat=None, lon=None)],
            fixes=[_fix(30.0, -97.0)],
        )
        finalize_bundle(bundle, exports=True)

        manifest = read_manifest(bundle)
        assert manifest["counts"]["detections_stored"] == 2
        assert manifest["counts"]["detections_geotagged"] == 1
        assert manifest["counts"]["telemetry_fixes"] == 1
        assert manifest["artifacts"]["detections_csv"] == DETECTIONS_CSV
        assert manifest["telemetry"]["available"] is True
        assert manifest["finalized_at"] is not None

    def test_one_failing_artifact_does_not_sink_the_others(self, tmp_path, monkeypatch):
        bundle = _build_bundle(
            tmp_path, detections=[_record(0)], fixes=[_fix(30.0, -97.0), _fix(30.1, -97.1)]
        )

        import core.services.streaming.RecordingBundleService as module

        def boom(*_args, **_kwargs):
            raise RuntimeError("kml exploded")

        monkeypatch.setattr(module, "write_flight_kml", boom)
        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["flight_path_kml"] is None
        assert any("kml exploded" in message for message in result["errors"])
        assert result["artifacts"]["detections_csv"] == DETECTIONS_CSV
        assert result["artifacts"]["flight_map_html"] == FLIGHT_MAP_HTML
        assert "kml exploded" in json.dumps(read_manifest(bundle))

    def test_finalizing_an_empty_bundle_is_harmless(self, tmp_path):
        bundle = _build_bundle(tmp_path)
        result = finalize_bundle(bundle, exports=True)

        assert result["counts"]["detections_stored"] == 0
        assert set(result["artifacts"].values()) == {None}
        assert result["errors"] == []

    def test_finalize_rebuilds_from_logs_alone(self, tmp_path):
        """The crash-repair path: logs on disk, nothing else."""
        bundle = _build_bundle(
            tmp_path, detections=[_record(0)], fixes=[_fix(30.0, -97.0), _fix(30.1, -97.1)]
        )
        for name in (DETECTIONS_CSV, RESULTS_XML, FLIGHT_MAP_HTML, FLIGHT_PATH_KML):
            path = os.path.join(bundle, name)
            if os.path.exists(path):
                os.remove(path)

        result = finalize_bundle(bundle, exports=True)

        assert result["artifacts"]["detections_csv"] == DETECTIONS_CSV
        assert result["artifacts"]["results_xml"] == RESULTS_XML
        assert os.path.isfile(os.path.join(bundle, FLIGHT_MAP_HTML))
