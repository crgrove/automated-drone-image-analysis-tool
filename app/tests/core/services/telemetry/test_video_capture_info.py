"""Tests for deriving capture settings from a video.

The wizard's drone and altitude answers both feed GSD, and GSD feeds the
detection-area filter — area scales with GSD², so a 2x altitude error is
a ~4x area error. Detection therefore has to be right or absent, never
confidently wrong.
"""

import pandas as pd
import pytest
from unittest.mock import patch

from core.services.telemetry.VideoCaptureInfoService import (
    VideoCaptureInfo,
    detect_capture_info,
    match_drone_model,
    read_device_text,
)

SERVICE = "core.services.telemetry.VideoCaptureInfoService"


@pytest.fixture
def drones():
    """A slice of drones.pkl covering both model-naming styles."""
    return pd.DataFrame([
        {"Manufacturer": "DJI", "Model": "Matrice 4E", "Model (Exif)": "M4E, M4ED"},
        {"Manufacturer": "DJI", "Model": "Matrice 4T", "Model (Exif)": "M4T, M4TD"},
        {"Manufacturer": "DJI", "Model": "Mavic 3", "Model (Exif)": "M3"},
        {"Manufacturer": "Skydio", "Model": "X10", "Model (Exif)": "X10"},
    ])


class TestModelMatching:
    def test_human_readable_tag_with_repeated_make(self, drones):
        """DJI writes the make twice: ``DJI DJI Matrice 4E``."""
        assert match_drone_model("DJI DJI Matrice 4E", drones) == ("DJI", "Matrice 4E")

    def test_exif_style_code_tag(self, drones):
        """Other clips carry the short code instead: ``DJI M4TD``."""
        assert match_drone_model("DJI M4TD", drones) == ("DJI", "Matrice 4T")

    def test_a_hyphenated_code_can_match(self, drones):
        """Regression: normalization splits ``L1D-20c`` into two tokens, and
        codes were tested against a set of single words, so any code with
        punctuation could never match."""
        table = pd.DataFrame([{
            "Manufacturer": "DJI", "Model": "Mavic 2 Pro",
            "Model (Exif)": "L1D-20c",
        }])
        assert match_drone_model("DJI L1D-20c", table) == ("DJI", "Mavic 2 Pro")

    def test_code_matches_whole_words_only(self, drones):
        """``M4T`` must not match inside ``M4TD`` and pick the wrong row."""
        assert match_drone_model("DJI M4TD", drones) == ("DJI", "Matrice 4T")
        assert match_drone_model("DJI M4T", drones) == ("DJI", "Matrice 4T")
        assert match_drone_model("DJI M4ED", drones) == ("DJI", "Matrice 4E")

    def test_sibling_models_are_not_confused(self, drones):
        """4E and 4T carry different sensors; a mix-up changes every GSD."""
        assert match_drone_model("DJI DJI Matrice 4T", drones) == ("DJI", "Matrice 4T")
        assert match_drone_model("DJI DJI Matrice 4E", drones) == ("DJI", "Matrice 4E")

    def test_make_must_be_present(self, drones):
        """A bare model name from another vendor must not match a DJI row."""
        assert match_drone_model("Acme Matrice 4E", drones) is None

    def test_other_manufacturers(self, drones):
        assert match_drone_model("Skydio X10", drones) == ("Skydio", "X10")

    def test_unknown_device(self, drones):
        assert match_drone_model("GoPro HERO12", drones) is None

    def test_case_and_punctuation_insensitive(self, drones):
        assert match_drone_model("dji  matrice-4e", drones) == ("DJI", "Matrice 4E")

    def test_longest_name_wins(self):
        """A model that prefixes another must not shadow it."""
        df = pd.DataFrame([
            {"Manufacturer": "DJI", "Model": "Matrice 4", "Model (Exif)": ""},
            {"Manufacturer": "DJI", "Model": "Matrice 4E", "Model (Exif)": ""},
        ])
        assert match_drone_model("DJI Matrice 4E", df) == ("DJI", "Matrice 4E")

    @pytest.mark.parametrize("text", ["", None])
    def test_empty_input(self, drones, text):
        assert match_drone_model(text, drones) is None

    def test_empty_table(self):
        assert match_drone_model("DJI M4TD", pd.DataFrame()) is None


class TestDeviceTagReading:
    def test_prefers_encoder_tag(self):
        with patch(f"{SERVICE}.get_video_device_tags",
                   return_value={"encoder": "DJI M4TD", "make": "DJI"}):
            assert read_device_text("v.mp4") == "DJI M4TD"

    def test_falls_back_to_model_tag(self):
        with patch(f"{SERVICE}.get_video_device_tags",
                   return_value={"model": "FC7303"}):
            assert read_device_text("v.mp4") == "FC7303"

    def test_no_tags(self):
        with patch(f"{SERVICE}.get_video_device_tags", return_value={}):
            assert read_device_text("v.mp4") is None

    def test_blank_tag_is_skipped(self):
        with patch(f"{SERVICE}.get_video_device_tags",
                   return_value={"encoder": "   ", "make": "DJI"}):
            assert read_device_text("v.mp4") == "DJI"


class TestDetectCaptureInfo:
    def _telemetry(self, altitudes):
        from core.services.telemetry.DjiSrtParser import DjiSrtSample
        from core.services.telemetry.TelemetrySourceResolver import TelemetryResolution
        from core.services.telemetry.TelemetryTrack import TelemetryTrack

        track = TelemetryTrack.from_dji_samples([
            DjiSrtSample(start_seconds=float(i), end_seconds=float(i) + 0.03,
                         latitude=30.0, longitude=-97.0,
                         altitude_msl_m=200.0, altitude_ato_m=alt)
            for i, alt in enumerate(altitudes)
        ])
        return TelemetryResolution(track=track, source="embedded", detail="")

    def test_detects_both_fields(self, drones):
        with patch(f"{SERVICE}.get_video_device_tags",
                   return_value={"encoder": "DJI M4TD"}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=self._telemetry([88.0, 89.0, 90.0])):
            info = detect_capture_info("v.mp4", drones_df=drones)

        assert info.make == "DJI"
        assert info.model == "Matrice 4T"
        assert info.altitude_ato_m == pytest.approx(89.0)
        assert info.altitude_samples == 3
        assert info.has_device and info.has_altitude

    def test_ato_is_reported_as_takeoff_relative(self, drones):
        """The wizard field means height above the ground being flown over,
        and ATO only approximates it. The reference travels with the number
        so the operator is not told it is something it is not."""
        from helpers.FormatHelper import FormatHelper

        device = patch(f"{SERVICE}.get_video_device_tags", return_value={})
        telemetry = patch(f"{SERVICE}.load_telemetry_for_video",
                          return_value=self._telemetry([88.0, 89.0, 90.0]))
        with device, telemetry:
            info = detect_capture_info("v.mp4", drones_df=drones)

        assert info.altitude_m == pytest.approx(89.0)
        assert info.altitude_reference == FormatHelper.ALTITUDE_REFERENCE_TAKEOFF
        assert info.altitude_agl_terrain_m is None

    def test_a_log_with_its_own_agl_wins_and_says_so(self, drones):
        """A flight log that resolved a terrain AGL answers the wizard's
        question exactly, so it is preferred over the ATO column and reported
        as terrain-referenced."""
        from core.services.telemetry.FlightLogCsvParser import FlightLogSample
        from core.services.telemetry.TelemetrySourceResolver import TelemetryResolution
        from core.services.telemetry.TelemetryTrack import TelemetryTrack
        from helpers.FormatHelper import FormatHelper

        track = TelemetryTrack.from_samples([
            FlightLogSample(start_seconds=float(i), end_seconds=float(i),
                            latitude=30.0, longitude=-97.0,
                            altitude_ato_m=120.0,
                            altitude_agl_terrain_m=agl)
            for i, agl in enumerate([94.0, 95.0, 96.0])
        ])
        device = patch(f"{SERVICE}.get_video_device_tags", return_value={})
        telemetry = patch(f"{SERVICE}.load_telemetry_for_video",
                          return_value=TelemetryResolution(
                              track=track, source="sidecar", detail=""))
        with device, telemetry:
            info = detect_capture_info("v.mp4", drones_df=drones)

        assert info.altitude_agl_terrain_m == pytest.approx(95.0)
        assert info.altitude_m == pytest.approx(95.0)
        assert info.altitude_reference == FormatHelper.ALTITUDE_REFERENCE_TERRAIN
        # The ATO column is not silently folded into the same median.
        assert info.altitude_ato_m is None

    def test_uses_the_median_altitude(self, drones):
        """Takeoff/landing legs must not drag the representative altitude."""
        with patch(f"{SERVICE}.get_video_device_tags", return_value={}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=self._telemetry([0.0, 1.0, 90.0, 91.0, 92.0])):
            info = detect_capture_info("v.mp4", drones_df=drones)
        assert info.altitude_ato_m == pytest.approx(91.0)
        # Ground fixes are excluded outright, not merely outvoted.
        assert info.altitude_samples == 3

    def test_ground_dominated_clip_reports_the_flying_altitude(self, drones):
        """Real regression: an 80 s clip in the test data has 58% of its
        fixes on the ground and 42% at 77 m. The plain median was -4.4 m,
        which clamps to 0 ft and makes GSD uncomputable — worse than not
        detecting anything."""
        ground = [-4.4] * 58
        flying = [76.9] * 42
        with patch(f"{SERVICE}.get_video_device_tags", return_value={}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=self._telemetry(ground + flying)):
            info = detect_capture_info("v.mp4", drones_df=drones)

        assert info.altitude_ato_m == pytest.approx(76.9)
        assert info.altitude_samples == 42

    def test_a_clip_that_never_left_the_ground_detects_nothing(self, drones):
        """Declining to guess beats pre-selecting an altitude of zero."""
        with patch(f"{SERVICE}.get_video_device_tags", return_value={}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=self._telemetry([-5.6, -4.9, -4.2])):
            info = detect_capture_info("v.mp4", drones_df=drones)
        assert not info.has_altitude

    def test_device_without_telemetry(self, drones):
        from core.services.telemetry.TelemetrySourceResolver import TelemetryResolution

        with patch(f"{SERVICE}.get_video_device_tags",
                   return_value={"encoder": "DJI M4TD"}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=TelemetryResolution(track=None, source="none")):
            info = detect_capture_info("v.mp4", drones_df=drones)

        assert info.has_device
        assert not info.has_altitude

    def test_telemetry_without_a_known_device(self, drones):
        with patch(f"{SERVICE}.get_video_device_tags",
                   return_value={"encoder": "Unknown Cam"}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=self._telemetry([50.0])):
            info = detect_capture_info("v.mp4", drones_df=drones)

        assert not info.has_device
        assert info.has_altitude

    def test_nothing_detectable(self, drones):
        from core.services.telemetry.TelemetrySourceResolver import TelemetryResolution

        with patch(f"{SERVICE}.get_video_device_tags", return_value={}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=TelemetryResolution(track=None, source="none")):
            info = detect_capture_info("v.mp4", drones_df=drones)

        assert info == VideoCaptureInfo()

    def test_failures_are_survivable(self, drones):
        """Detection is advisory — it must never break the wizard."""
        with patch(f"{SERVICE}.get_video_device_tags", side_effect=OSError("boom")), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      side_effect=OSError("also boom")):
            info = detect_capture_info("v.mp4", drones_df=drones)
        assert info == VideoCaptureInfo()

    def test_msl_only_telemetry_yields_no_altitude(self, drones):
        """Deliberate: GSD is computed from height above ground, and AGL is
        not derivable from MSL without terrain data. A Skydio CSV carries
        only MSL, so the operator keeps setting altitude by hand — guessing
        here would square a wrong altitude into the area filter."""
        from core.services.telemetry.DjiSrtParser import DjiSrtSample
        from core.services.telemetry.TelemetrySourceResolver import TelemetryResolution
        from core.services.telemetry.TelemetryTrack import TelemetryTrack

        msl_only = TelemetryResolution(
            track=TelemetryTrack.from_dji_samples([
                DjiSrtSample(start_seconds=0.0, end_seconds=0.03,
                             latitude=30.0, longitude=-97.0,
                             altitude_msl_m=207.0, altitude_ato_m=None),
            ]),
            source="explicit-file", detail="",
        )
        with patch(f"{SERVICE}.get_video_device_tags", return_value={}), \
                patch(f"{SERVICE}.load_telemetry_for_video", return_value=msl_only):
            info = detect_capture_info("v.mp4", drones_df=drones,
                                       metadata_path="C:/logs/msl.csv")

        assert not info.has_altitude
        assert info.altitude_samples == 0

    def test_a_selected_metadata_file_is_used(self, drones):
        """A video whose own telemetry is missing still yields an altitude
        when the operator's file carries AGL — otherwise the wizard falls
        back to a hand-typed guess, and altitude error squares into
        detection-area error."""
        with patch(f"{SERVICE}.get_video_device_tags", return_value={}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=self._telemetry([75.0])) as loader:
            info = detect_capture_info(
                "v.mp4", drones_df=drones, metadata_path="C:/logs/flight.csv")

        assert loader.call_args[0][1] == "C:/logs/flight.csv"
        assert info.altitude_ato_m == pytest.approx(75.0)

    def test_no_metadata_file_still_probes_the_video(self, drones):
        with patch(f"{SERVICE}.get_video_device_tags", return_value={}), \
                patch(f"{SERVICE}.load_telemetry_for_video",
                      return_value=self._telemetry([60.0])) as loader:
            detect_capture_info("v.mp4", drones_df=drones)
        assert loader.call_args[0][1] is None
