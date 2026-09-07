"""Tests for ``video.csv``, the video/telemetry data dictionary.

It is the video counterpart to ``xmp.csv``: where each telemetry value
lives in a video's SRT, and what the aircraft means by it. Separate from
``drones.csv`` because the identity key differs — videos are matched on the
*container* tag, not the EXIF model.

Two deployment realities are covered explicitly, because both silently
disable the lookup rather than failing:

* an install whose ``video.csv`` is absent or predates a column
* a video remuxed through ffmpeg, which loses its device tag entirely
"""

import os

import pandas as pd
import pytest
from unittest.mock import patch

from core.services.telemetry.DjiSrtParser import parse_dji_srt
from core.services.telemetry.VideoProfileService import (
    DATUM_EXPLICIT,
    DATUM_MSL,
    DATUM_RELATIVE,
    VideoProfile,
    datum_for_video,
    load_profiles,
    normalize_datum,
    profile_for_video,
    profiles_for_device_tag,
    suffix_from_filename,
)

HELPER = "helpers.VideoFileHelper"


def _table(rows):
    return pd.DataFrame(rows)


TABLE = _table([
    {"Manufacturer": "DJI", "Model": "Matrice 4E",
     "Video Device Tag": "DJI DJI Matrice 4E, M4E, M4ED", "Camera": "Wide",
     "SRT Focal Len": 24.0, "Telemetry Location": "Embedded",
     "Telemetry Format": "dji-srt-modern", "Value Scales": "",
     "Latitude Key": "latitude", "Longitude Key": "longitude",
     "Altitude MSL Key": "abs_alt", "Altitude AGL Key": "rel_alt",
     "Altitude Datum": "Both", "Gimbal Pitch Key": "gb_pitch",
     "Gimbal Yaw Key": "gb_yaw", "Gimbal Roll Key": "gb_roll",
     "Nadir Convention": -90.0, "Zoom Ratio Key": "dzoom_ratio"},
    {"Manufacturer": "DJI", "Model": "Matrice 4E",
     "Video Device Tag": "DJI DJI Matrice 4E, M4E, M4ED", "Camera": "Zoom",
     "SRT Focal Len": 168.0, "Telemetry Location": "Embedded",
     "Telemetry Format": "dji-srt-modern", "Value Scales": "",
     "Latitude Key": "latitude", "Longitude Key": "longitude",
     "Altitude MSL Key": "abs_alt", "Altitude AGL Key": "rel_alt",
     "Altitude Datum": "Both", "Gimbal Pitch Key": "gb_pitch",
     "Gimbal Yaw Key": "gb_yaw", "Gimbal Roll Key": "gb_roll",
     "Nadir Convention": -90.0, "Zoom Ratio Key": "dzoom_ratio"},
    {"Manufacturer": "DJI", "Model": "Air 2S", "Video Device Tag": "",
     "Camera": "", "SRT Focal Len": 224.0, "Telemetry Location": "Sidecar",
     "Telemetry Format": "dji-srt-legacy", "Value Scales": "focal_len:10, fnum:100, dzoom_ratio:10000",
     "Latitude Key": "latitude", "Longitude Key": "longitude",
     "Altitude MSL Key": "", "Altitude AGL Key": "altitude",
     "Altitude Datum": "Relative", "Gimbal Pitch Key": "",
     "Gimbal Yaw Key": "", "Gimbal Roll Key": "",
     "Nadir Convention": "", "Zoom Ratio Key": "dzoom_ratio"},
])


class TestNormalizeDatum:
    @pytest.mark.parametrize("value,expected", [
        ("MSL", DATUM_MSL), ("asl", DATUM_MSL), ("Absolute", DATUM_MSL),
        ("Relative", DATUM_RELATIVE), ("AGL", DATUM_RELATIVE),
        ("Takeoff", DATUM_RELATIVE),
        ("Both", DATUM_EXPLICIT), ("Explicit", DATUM_EXPLICIT),
    ])
    def test_spellings(self, value, expected):
        assert normalize_datum(value) == expected

    @pytest.mark.parametrize("value", [None, "", "  ", "nan", "-", "banana"])
    def test_unreadable_is_none(self, value):
        """Must leave the decision to inference rather than pick a datum."""
        assert normalize_datum(value) is None


class TestLoadProfiles:
    def test_reads_every_row(self):
        assert len(load_profiles(TABLE)) == 3

    def test_parses_a_row(self):
        wide = load_profiles(TABLE)[0]
        assert wide.model == "Matrice 4E"
        assert wide.camera == "Wide"
        assert wide.device_tags == ["DJI DJI Matrice 4E", "M4E", "M4ED"]
        assert wide.altitude_datum == DATUM_EXPLICIT
        assert wide.gimbal_pitch_key == "gb_pitch"
        assert wide.nadir_convention == -90.0
        assert wide.value_scales == {}

    def test_blank_cells_become_none(self):
        air = load_profiles(TABLE)[2]
        assert air.gimbal_pitch_key is None
        assert air.nadir_convention is None
        assert air.altitude_msl_key is None

    def test_a_missing_table_is_survivable(self):
        assert load_profiles(pd.DataFrame()) == []


class TestGimbalAvailability:
    def test_modern_aircraft_reports_a_gimbal(self):
        assert load_profiles(TABLE)[0].has_gimbal is True

    def test_legacy_sidecar_has_none(self):
        """Legacy SRTs carry no gimbal fields at all, so tilt is unknowable
        and a nadir assumption is a guess, not a measurement."""
        assert load_profiles(TABLE)[2].has_gimbal is False


class TestOffNadir:
    """The reported pitch is not an off-nadir angle; the convention decides."""

    def test_dji_convention(self):
        wide = load_profiles(TABLE)[0]
        # -90 is straight down, so -43.5 is 46.5 off nadir, not 43.5. That
        # 3 deg confusion is ~5 m of ground error at 88 m AGL.
        assert wide.off_nadir_degrees(-43.5) == pytest.approx(46.5)
        assert wide.off_nadir_degrees(-90.0) == pytest.approx(0.0)
        assert wide.off_nadir_degrees(0.0) == pytest.approx(90.0)

    def test_an_upward_tilted_gimbal(self):
        """Regression: a difference of *magnitudes* folded upward tilt back
        down, so a gimbal 30 deg above the horizon read as 60 deg off nadir
        instead of 120."""
        wide = load_profiles(TABLE)[0]
        assert wide.off_nadir_degrees(30.0) == pytest.approx(120.0)
        assert wide.off_nadir_degrees(15.0) == pytest.approx(105.0)

    def test_without_a_convention_it_declines(self):
        assert load_profiles(TABLE)[2].off_nadir_degrees(-43.5) is None

    def test_unparseable_pitch(self):
        assert load_profiles(TABLE)[0].off_nadir_degrees("n/a") is None


class TestValueScales:
    """The divisor is per-key. One factor for the whole stream is wrong by
    10x on two of the three fields."""

    def test_legacy_divisors_differ_per_key(self):
        air = load_profiles(TABLE)[2]
        assert air.descale("focal_len", 224) == pytest.approx(22.4)
        assert air.descale("fnum", 280) == pytest.approx(2.8)
        assert air.descale("dzoom_ratio", 10000) == pytest.approx(1.0)

    def test_modern_needs_no_scaling(self):
        wide = load_profiles(TABLE)[0]
        assert wide.descale("focal_len", 24.00) == pytest.approx(24.0)
        assert wide.descale("fnum", 2.8) == pytest.approx(2.8)
        assert wide.descale("dzoom_ratio", 1.00) == pytest.approx(1.0)

    def test_an_unlisted_key_passes_through(self):
        assert load_profiles(TABLE)[2].descale("iso", 120) == pytest.approx(120.0)

    def test_unparseable(self):
        assert load_profiles(TABLE)[0].descale("focal_len", "n/a") is None


class TestDeviceTagMatching:
    def test_matches_the_human_name(self):
        found = profiles_for_device_tag("DJI DJI Matrice 4E", TABLE)
        assert len(found) == 2  # both camera rows
        assert all(p.model == "Matrice 4E" for p in found)

    def test_matches_the_short_code(self):
        """The 4T reports 'DJI M4TD' rather than a human name."""
        assert profiles_for_device_tag("DJI M4ED", TABLE)

    def test_a_code_does_not_match_inside_a_longer_one(self):
        assert profiles_for_device_tag("DJI M4EDX", TABLE) == []

    def test_a_remuxed_tag_matches_nothing(self):
        assert profiles_for_device_tag("Lavf56.15.102", TABLE) == []

    def test_blank_tags_are_skipped(self):
        """Air 2S has no recorded tag; it must not match everything."""
        assert profiles_for_device_tag("anything at all", TABLE) == []

    def test_empty_input(self):
        assert profiles_for_device_tag("", TABLE) == []


class TestProfileForVideo:
    def _tags(self, encoder):
        return patch(f"{HELPER}.get_video_device_tags", return_value={"encoder": encoder})

    def test_resolves_from_the_container_tag(self):
        with self._tags("DJI DJI Matrice 4E"):
            profile = profile_for_video("v.mp4", video_df=TABLE)
        assert profile.model == "Matrice 4E"

    def test_focal_len_picks_the_camera(self):
        """A multi-camera airframe needs the camera to choose a sensor row."""
        with self._tags("DJI DJI Matrice 4E"):
            wide = profile_for_video("v.mp4", video_df=TABLE, focal_len=24.0)
            zoom = profile_for_video("v.mp4", video_df=TABLE, focal_len=168.0)
        assert wide.camera == "Wide"
        assert zoom.camera == "Zoom"

    def test_without_focal_len_airframe_fields_still_resolve(self):
        with self._tags("DJI DJI Matrice 4E"):
            profile = profile_for_video("v.mp4", video_df=TABLE)
        assert profile.altitude_datum == DATUM_EXPLICIT
        assert profile.has_gimbal

    def test_a_remuxed_video_resolves_to_nothing(self):
        with self._tags("Lavf56.15.102"):
            assert profile_for_video("v.mp4", video_df=TABLE) is None

    def test_no_tags_at_all(self):
        with patch(f"{HELPER}.get_video_device_tags", return_value={}):
            assert profile_for_video("v.mp4", video_df=TABLE) is None

    def test_failures_are_survivable(self):
        with patch(f"{HELPER}.get_video_device_tags", side_effect=OSError("boom")):
            assert profile_for_video("v.mp4", video_df=TABLE) is None


class TestDatumForVideo:
    def test_reads_the_recorded_datum(self):
        with patch(f"{HELPER}.get_video_device_tags",
                   return_value={"encoder": "DJI M4E"}):
            assert datum_for_video("v.mp4", video_df=TABLE) == DATUM_EXPLICIT

    def test_unidentifiable_video_leaves_inference_in_charge(self):
        with patch(f"{HELPER}.get_video_device_tags",
                   return_value={"encoder": "Lavf56.15.102"}):
            assert datum_for_video("v.mp4", video_df=TABLE) is None


LOW = ('1\n00:00:00,000 --> 00:00:00,033\n'
       '<font size="36">SrtCnt : 1, DiffTime : 33ms\n2024-03-22 16:51:55,597,864\n'
       '[latitude: 30.65] [longitude: -97.95] [altitude: 9.800000] </font>\n')
HIGH = ('1\n00:00:00,000 --> 00:00:00,033\n'
        '<font size="36">SrtCnt : 1, DiffTime : 33ms\n2019-08-01 10:00:00,000,000\n'
        '[latitude: 41.35] [longitude: -111.86] [altitude: 1622.800000] </font>\n')


class TestRecordedDatumBeatsInference:
    def test_recorded_msl_overrides_a_low_track(self):
        first = parse_dji_srt(LOW, altitude_datum=DATUM_MSL)[0]
        assert first.altitude_msl_m == pytest.approx(9.8)
        assert first.altitude_ato_m is None

    def test_recorded_relative_overrides_a_high_track(self):
        first = parse_dji_srt(HIGH, altitude_datum=DATUM_RELATIVE)[0]
        assert first.altitude_ato_m == pytest.approx(1622.8)
        assert first.altitude_msl_m is None

    def test_unrecorded_falls_back_to_inference(self):
        assert parse_dji_srt(LOW)[0].altitude_ato_m == pytest.approx(9.8)
        assert parse_dji_srt(HIGH)[0].altitude_msl_m == pytest.approx(1622.8)

    def test_explicit_defers_to_inference(self):
        """'Both' says the aircraft states its datums; it says nothing about
        a legacy key, so it must not force one."""
        assert parse_dji_srt(LOW, altitude_datum=DATUM_EXPLICIT)[0] \
            .altitude_ato_m == pytest.approx(9.8)


class TestFilenameSuffix:
    """A Matrice 30T records one video per camera, so the name identifies it.

    This is the only camera signal that survives remuxing: every M30T sample
    available has had its telemetry stripped and its device tag replaced with
    ``Lavf...``, so ``focal_len`` is not readable at all.
    """

    @pytest.mark.parametrize("name,expected", [
        ("DJI_20250706140555_0019_W.MP4", "W"),
        ("DJI_20250706134702_0002_T.MP4", "T"),
        ("DJI_20260725143826_0001_V.MP4", "V"),
        (os.path.join("D:", "Drone_Images", "x_Z.mp4"), "Z"),
        ("DJI_0462.MP4", None),
        ("", None),
        (None, None),
    ])
    def test_parsing(self, name, expected):
        assert suffix_from_filename(name) == expected

    def test_suffix_picks_the_camera_over_focal_len(self):
        """Preferred because it needs no telemetry and, unlike focal_len,
        cannot be changed by zooming."""
        table = _table([
            {"Manufacturer": "DJI", "Model": "Matrice 30T",
             "Video Device Tag": "DJI M30T", "Camera": "Wide",
             "Filename Suffix": "W"},
            {"Manufacturer": "DJI", "Model": "Matrice 30T",
             "Video Device Tag": "DJI M30T", "Camera": "Thermal",
             "Filename Suffix": "T"},
        ])
        with patch(f"{HELPER}.get_video_device_tags",
                   return_value={"encoder": "DJI M30T"}):
            wide = profile_for_video("DJI_0019_W.MP4", video_df=table)
            thermal = profile_for_video("DJI_0019_T.MP4", video_df=table)
        assert wide.camera == "Wide"
        assert thermal.camera == "Thermal"

    def test_an_unrecorded_camera_claims_no_camera(self):
        """Regression: falling through to another camera's row handed back the
        wrong sensor geometry — a Mavic 3T ``_W`` video resolved as Thermal,
        which would feed GSD the 7.68x6.14 thermal sensor instead of the
        6.4x4.8 wide one. Airframe facts are shared and stay; the camera does
        not."""
        table = _table([
            {"Manufacturer": "DJI", "Model": "Mavic 3T", "Video Device Tag": "DJI M3T",
             "Camera": "Thermal", "Filename Suffix": "T", "SRT Focal Len": 40.0,
             "Altitude Datum": "Both", "Gimbal Pitch Key": "gb_pitch",
             "Nadir Convention": -90.0},
        ])
        with patch(f"{HELPER}.get_video_device_tags",
                   return_value={"encoder": "DJI M3T"}):
            wide = profile_for_video("DJI_x_W.MP4", video_df=table)

        assert wide is not None
        assert wide.camera == ""
        assert wide.srt_focal_len is None
        assert wide.filename_suffix == ""
        # Still usable for everything that is an airframe property.
        assert wide.altitude_datum == DATUM_EXPLICIT
        assert wide.has_gimbal is True

    def test_an_airframe_with_no_suffixes_is_unaffected(self):
        """A Matrice 4E writes a single ``_V`` file, so a stray suffix must not
        blank its camera."""
        with patch(f"{HELPER}.get_video_device_tags",
                   return_value={"encoder": "DJI DJI Matrice 4E"}):
            profile = profile_for_video("DJI_x_V.MP4", video_df=TABLE, focal_len=24.0)
        assert profile.camera == "Wide"

    def test_a_suffix_alone_cannot_identify_the_model(self):
        """Many DJI aircraft write ``_W``, so with no device tag there is no
        model to look up and the dictionary must not guess one."""
        with patch(f"{HELPER}.get_video_device_tags",
                   return_value={"encoder": "Lavf56.15.102"}):
            assert profile_for_video("DJI_0019_W.MP4", video_df=TABLE) is None


class TestShippedDictionary:
    """The real video.csv must carry every measured aircraft.

    Each row below is backed by a real file that was inspected, so a
    regression here means the reference data was lost or overwritten.
    """

    # staticmethod, not an instance method: pytest 10 removes class-scoped
    # fixtures defined as instance methods, and this body never touched
    # self. scope="class" stays, so video.csv is still parsed once for the
    # whole class rather than once per test.
    @pytest.fixture(scope="class")
    @staticmethod
    def table():
        path = os.path.join(os.path.dirname(__file__),
                            "..", "..", "..", "..", "video.csv")
        return pd.read_csv(os.path.abspath(path), comment="#")

    def test_it_parses(self, table):
        assert not table.empty
        assert len(load_profiles(table)) == len(table)

    def test_the_m30t_records_a_camera_per_file(self, table):
        """Recorded from real filenames. Its telemetry profile is deliberately
        blank: every available sample is remuxed, so nothing about its SRT is
        verified."""
        rows = {p.filename_suffix: p for p in load_profiles(table)
                if p.model == "Matrice 30T"}
        assert set(rows) == {"W", "Z", "T"}
        assert rows["W"].camera == "Wide"
        assert rows["T"].camera == "Thermal"
        assert rows["W"].altitude_datum is None
        assert rows["W"].telemetry_location is None
        assert rows["W"].has_gimbal is False

    def test_a_sidecar_can_still_be_fully_modern(self, table):
        """The Mavic 3T is why shape, key set, scaling and gimbal each need
        their own column: it writes a *sidecar* in the 5-line <font> shape,
        yet carries the explicit rel_alt/abs_alt pair, the full gimbal triad
        and decimal scaling. 'Sidecar implies legacy' is false."""
        m3t = [p for p in load_profiles(table)
               if p.model == "Mavic 3T" and p.camera == "Thermal"][0]
        assert m3t.writes_sidecar is True
        assert m3t.telemetry_format == "dji-srt-font"
        assert m3t.altitude_datum == DATUM_EXPLICIT
        assert m3t.has_gimbal is True
        # Decimal, despite being a sidecar: focal_len 40.00 means 40 mm.
        assert m3t.descale("focal_len", 40.00) == pytest.approx(40.0)
        # gb_pitch -82.4 is a near-nadir thermal scan, 7.6 deg off.
        assert m3t.off_nadir_degrees(-82.4) == pytest.approx(7.6)

    @pytest.mark.parametrize("model,camera,sidecar,datum,gimbal", [
        # XMP RelativeAltitude +46.1 vs AbsoluteAltitude +358.2, DEM 315.7 m.
        ("Air 2S", "", True, DATUM_RELATIVE, False),
        # Two tracks at 1622-1631 m on a ~1600 m site.
        ("Mavic 2 Pro", "", True, DATUM_MSL, False),
        # Embedded mov_text carrying the explicit pair and full gimbal triad.
        ("Matrice 4E", "Wide", False, DATUM_EXPLICIT, True),
        ("Matrice 4T", "Wide", False, DATUM_EXPLICIT, True),
        # Sidecar, but explicit pair + gimbal all the same.
        ("Mavic 3T", "Thermal", True, DATUM_EXPLICIT, True),
    ])
    def test_measured_aircraft(self, table, model, camera, sidecar, datum, gimbal):
        rows = [p for p in load_profiles(table)
                if p.model == model and p.camera == camera]
        assert rows, f"{model} / {camera or '(single camera)'} missing"
        profile = rows[0]
        assert profile.writes_sidecar is sidecar
        assert profile.altitude_datum == datum
        assert profile.has_gimbal is gimbal

    def test_legacy_divisors_are_recorded(self, table):
        """focal_len 224 = 22.4 mm, fnum 280 = f/2.8, dzoom 10000 = 1.0x —
        three divisors, one stream."""
        air = [p for p in load_profiles(table) if p.model == "Air 2S"][0]
        assert air.descale("focal_len", 224) == pytest.approx(22.4)
        assert air.descale("fnum", 280) == pytest.approx(2.8)
        assert air.descale("dzoom_ratio", 10000) == pytest.approx(1.0)

    def test_the_4t_tag_is_the_short_code(self, table):
        """Its container reports 'DJI M4TD', not a human-readable name."""
        assert profiles_for_device_tag("DJI M4TD", table)

    def test_multi_camera_airframes_have_a_row_per_camera(self, table):
        cams = {p.camera for p in load_profiles(table) if p.model == "Matrice 4T"}
        assert cams == {"Wide", "Zoom", "Thermal"}

    def test_airframe_facts_agree_across_camera_rows(self, table):
        """Repeating them per camera is the drones.csv convention, but the
        repetition must stay consistent."""
        for model in ("Matrice 4E", "Matrice 4T"):
            rows = [p for p in load_profiles(table) if p.model == model]
            assert len({p.altitude_datum for p in rows}) == 1
            assert len({p.telemetry_location for p in rows}) == 1
            assert len({p.nadir_convention for p in rows}) == 1
            assert len({tuple(p.device_tags) for p in rows}) == 1


class TestPickleHelperIntegration:
    def test_the_loader_exposes_the_dictionary(self):
        from helpers.PickleHelper import PickleHelper
        table = PickleHelper.get_video_telemetry_info()
        assert table is not None, "video.csv did not load through PickleHelper"
        assert "Video Device Tag" in table.columns

    def test_the_version_header_is_reported(self):
        from helpers.PickleHelper import PickleHelper
        meta = PickleHelper.get_video_telemetry_file_version()
        assert meta and meta["Version"]


class TestBareProfileDefaults:
    """A profile built from nothing must not claim capabilities."""

    def test_empty_profile(self):
        profile = VideoProfile()
        assert profile.has_gimbal is False
        assert profile.writes_sidecar is None
        assert profile.altitude_datum is None
        assert profile.off_nadir_degrees(-45) is None
        assert profile.descale("focal_len", 224) == pytest.approx(224.0)
