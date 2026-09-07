"""Tests for the streaming window's unified telemetry source.

The coordinator is the seam that lets one HUD and one map serve both a
DJI video file and a live ADIAT Flight feed, so the tests focus on
source switching, playback sampling, and trail behaviour under seeking.

DEM enrichment is neutralised (its own tests cover it) so these stay
deterministic and network-free.
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from core.controllers.streaming.components import StreamTelemetryCoordinator
from core.services.streaming.RTMPStreamService import StreamType
from core.services.telemetry.DjiSrtParser import DjiSrtSample
from core.services.telemetry.TelemetrySourceResolver import (
    SOURCE_EMBEDDED,
    SOURCE_EXPLICIT_FILE,
    SOURCE_NONE,
    SOURCE_SIDECAR,
    TelemetryResolution,
)
from core.services.telemetry.TelemetryTrack import TelemetryTrack

COORD = "core.controllers.streaming.components.StreamTelemetryCoordinator"


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def coordinator():
    coord = StreamTelemetryCoordinator()
    # Pass envelopes straight through — enrichment has its own suite and
    # would otherwise spin up a DEM worker thread.
    coord._enrichment = MagicMock()
    coord._enrichment.enrich.side_effect = lambda env: env
    yield coord
    coord.cleanup()


def _track(count=5, spacing=1.0):
    samples = [
        DjiSrtSample(
            start_seconds=i * spacing,
            end_seconds=i * spacing + 0.03,
            latitude=30.0 + i * 0.001,
            longitude=-97.0 - i * 0.001,
            altitude_msl_m=200.0 + i,
            altitude_ato_m=15.0 + i,
            yaw_deg=90.0,
        )
        for i in range(count)
    ]
    return TelemetryTrack.from_dji_samples(samples)


def _resolution(track, source=SOURCE_EMBEDDED):
    return TelemetryResolution(
        track=track, source=source, path=None,
        detail=f"{len(track)} fixes embedded in video",
    )


class TestFileSource:
    def test_loads_a_track_and_reports_available(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            assert coordinator.begin_source("v.mp4", StreamType.FILE) is True
        assert coordinator.is_available
        assert len(coordinator.track) == 5

    def test_reports_the_embedded_source(self, coordinator):
        messages = []
        coordinator.telemetryStatus.connect(messages.append)
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            coordinator.begin_source("v.mp4", StreamType.FILE)
        assert any("embedded" in m.lower() for m in messages)

    def test_reports_the_sidecar_source(self, coordinator):
        messages = []
        coordinator.telemetryStatus.connect(messages.append)
        resolution = TelemetryResolution(
            track=_track(), source=SOURCE_SIDECAR, path="v.SRT", detail="5 fixes"
        )
        with patch(f"{COORD}.load_telemetry_for_video", return_value=resolution):
            coordinator.begin_source("v.mp4", StreamType.FILE)
        assert any("SRT" in m for m in messages)

    def test_video_without_telemetry(self, coordinator):
        messages = []
        coordinator.telemetryStatus.connect(messages.append)
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=TelemetryResolution(track=None, source=SOURCE_NONE)):
            assert coordinator.begin_source("v.mp4", StreamType.FILE) is False
        assert not coordinator.is_available
        assert any("No location data" in m for m in messages)

    def test_load_failure_does_not_raise(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video", side_effect=OSError("boom")):
            assert coordinator.begin_source("v.mp4", StreamType.FILE) is False
        assert not coordinator.is_available


class TestSecondaryMetadataFile:
    """An operator-selected SRT/CSV must reach the resolver.

    This is the whole point of the feature: a video whose own telemetry is
    absent or unusable gets its location data from a file the operator
    supplies, exactly as the image-analysis Video Parser has always allowed.
    """

    def test_metadata_path_is_passed_to_the_resolver(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())) as loader:
            coordinator.begin_source("v.mp4", StreamType.FILE, "log.csv")
        loader.assert_called_once()
        assert loader.call_args[0][1] == "log.csv"

    def test_absent_metadata_path_is_none(self, coordinator):
        """Omitting it must still let the sidecar/embedded routes run."""
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())) as loader:
            coordinator.begin_source("v.mp4", StreamType.FILE)
        assert loader.call_args[0][1] is None

    def test_explicit_source_is_named_in_the_status(self, coordinator):
        messages = []
        coordinator.telemetryStatus.connect(messages.append)
        resolution = TelemetryResolution(
            track=_track(), source=SOURCE_EXPLICIT_FILE,
            path="C:/logs/flight.csv", detail="5 fixes from flight log",
        )
        with patch(f"{COORD}.load_telemetry_for_video", return_value=resolution):
            coordinator.begin_source("v.mp4", StreamType.FILE, "C:/logs/flight.csv")
        assert any("flight.csv" in m for m in messages)

    def test_a_rejected_metadata_file_explains_why(self, coordinator):
        """"No location data" hides a fixable problem — a missing column or
        an unaligned timestamp — behind a dead end."""
        messages = []
        coordinator.telemetryStatus.connect(messages.append)
        resolution = TelemetryResolution(
            track=None, source=SOURCE_EXPLICIT_FILE, path="log.csv",
            detail="flight log is missing required columns: Longitude",
        )
        with patch(f"{COORD}.load_telemetry_for_video", return_value=resolution):
            assert coordinator.begin_source(
                "v.mp4", StreamType.FILE, "log.csv") is False
        assert any("Longitude" in m for m in messages)

    def test_live_sources_ignore_a_metadata_path(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video") as loader:
            coordinator.begin_source("K7QM3P", StreamType.WEBRTC, "log.csv")
        loader.assert_not_called()


class TestPlaybackSampling:
    @pytest.fixture
    def loaded(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            coordinator.begin_source("v.mp4", StreamType.FILE)
        return coordinator

    def test_position_emits_an_envelope(self, loaded):
        envelopes = []
        loaded.telemetryUpdated.connect(envelopes.append)
        loaded.on_position_changed(2.0)
        assert len(envelopes) == 1
        assert envelopes[0]["aircraft_latitude"] == pytest.approx(30.002)

    def test_same_fix_is_not_re_emitted(self, loaded):
        """One SRT cue per frame would otherwise spam the HUD."""
        envelopes = []
        loaded.telemetryUpdated.connect(envelopes.append)
        loaded.on_position_changed(2.0)
        loaded.on_position_changed(2.01)
        loaded.on_position_changed(2.02)
        assert len(envelopes) == 1

    def test_advancing_emits_again(self, loaded):
        envelopes = []
        loaded.telemetryUpdated.connect(envelopes.append)
        loaded.on_position_changed(1.0)
        loaded.on_position_changed(3.0)
        assert len(envelopes) == 2

    def test_track_grows_with_playback(self, loaded):
        paths = []
        loaded.trackUpdated.connect(paths.append)
        loaded.on_position_changed(1.0)
        loaded.on_position_changed(3.0)
        assert len(paths[0]) < len(paths[1])

    def test_seeking_backwards_shortens_the_trail(self, loaded):
        paths = []
        loaded.trackUpdated.connect(paths.append)
        loaded.on_position_changed(4.0)
        loaded.on_position_changed(1.0)
        assert len(paths[-1]) < len(paths[0])

    def test_position_beyond_the_track_emits_nothing(self, loaded):
        envelopes = []
        loaded.telemetryUpdated.connect(envelopes.append)
        loaded.on_position_changed(500.0)
        assert envelopes == []

    def test_no_track_is_a_no_op(self, coordinator):
        envelopes = []
        coordinator.telemetryUpdated.connect(envelopes.append)
        coordinator.on_position_changed(1.0)
        assert envelopes == []


class TestLiveSource:
    def test_webrtc_starts_unavailable(self, coordinator):
        assert coordinator.begin_source("K7QM3P", StreamType.WEBRTC) is False
        assert not coordinator.is_available

    def test_first_envelope_makes_it_available(self, coordinator):
        coordinator.begin_source("K7QM3P", StreamType.WEBRTC)
        coordinator.on_live_telemetry({
            "aircraft_latitude": 30.0, "aircraft_longitude": -97.0
        })
        assert coordinator.is_available

    def test_live_envelope_is_forwarded(self, coordinator):
        coordinator.begin_source("K7QM3P", StreamType.WEBRTC)
        envelopes = []
        coordinator.telemetryUpdated.connect(envelopes.append)
        coordinator.on_live_telemetry({
            "aircraft_latitude": 30.0, "aircraft_longitude": -97.0
        })
        assert len(envelopes) == 1
        assert envelopes[0]["aircraft_latitude"] == 30.0

    def test_non_dict_live_payload_ignored(self, coordinator):
        envelopes = []
        coordinator.telemetryUpdated.connect(envelopes.append)
        coordinator.on_live_telemetry("nope")
        assert envelopes == []

    def test_live_source_loads_no_file_track(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video") as loader:
            coordinator.begin_source("K7QM3P", StreamType.WEBRTC)
        loader.assert_not_called()
        assert coordinator.track is None


class TestOtherSources:
    @pytest.mark.parametrize("stream_type", [
        StreamType.HDMI_CAPTURE, StreamType.RTMP,
    ])
    def test_live_non_flight_sources_are_inert(self, coordinator, stream_type):
        with patch(f"{COORD}.load_telemetry_for_video") as loader:
            assert coordinator.begin_source("x", stream_type) is False
        loader.assert_not_called()
        assert not coordinator.is_available


class TestSourceSwitching:
    def test_switching_sources_drops_the_old_track(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            coordinator.begin_source("a.mp4", StreamType.FILE)
        assert coordinator.is_available

        coordinator.begin_source("K7QM3P", StreamType.WEBRTC)
        assert coordinator.track is None
        assert not coordinator.is_available

    def test_availability_signal_fires_on_change(self, coordinator):
        states = []
        coordinator.availabilityChanged.connect(states.append)
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            coordinator.begin_source("a.mp4", StreamType.FILE)
        coordinator.reset()
        assert states == [True, False]

    def test_reset_clears_everything(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            coordinator.begin_source("a.mp4", StreamType.FILE)
        coordinator.on_position_changed(1.0)
        coordinator.reset()
        assert coordinator.track is None
        assert coordinator.last_envelope is None
        assert not coordinator.is_available


class TestGeotagLookups:
    @pytest.fixture
    def loaded(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            coordinator.begin_source("v.mp4", StreamType.FILE)
        return coordinator

    def test_position_at_a_video_time(self, loaded):
        pos = loaded.position_at(2.0)
        assert pos == pytest.approx((30.002, -97.002))

    def test_position_at_beyond_track(self, loaded):
        assert loaded.position_at(500.0) is None

    def test_position_at_without_track(self, coordinator):
        assert coordinator.position_at(1.0) is None

    def test_current_position_from_last_envelope(self, loaded):
        loaded.on_position_changed(3.0)
        assert loaded.current_position() == pytest.approx((30.003, -97.003))

    def test_current_position_works_for_live_feeds(self, coordinator):
        coordinator.begin_source("K7QM3P", StreamType.WEBRTC)
        coordinator.on_live_telemetry({
            "aircraft_latitude": 45.0, "aircraft_longitude": -120.0
        })
        assert coordinator.current_position() == (45.0, -120.0)

    def test_current_position_none_initially(self, coordinator):
        assert coordinator.current_position() is None

    def test_full_path(self, loaded):
        assert len(loaded.full_path()) == 5


class TestEnrichmentIntegration:
    def test_enriched_envelopes_are_re_emitted(self):
        """A late DEM correction must reach the HUD."""
        coord = StreamTelemetryCoordinator()
        try:
            envelopes = []
            coord.telemetryUpdated.connect(envelopes.append)
            coord._on_envelope_enriched({"aircraft_latitude": 1.0,
                                         "agl_source": "terrain"})
            assert envelopes[-1]["agl_source"] == "terrain"
            assert coord.last_envelope["agl_source"] == "terrain"
        finally:
            coord.cleanup()

    def test_envelopes_pass_through_enrichment(self, coordinator):
        with patch(f"{COORD}.load_telemetry_for_video",
                   return_value=_resolution(_track())):
            coordinator.begin_source("v.mp4", StreamType.FILE)
        coordinator.on_position_changed(1.0)
        coordinator._enrichment.enrich.assert_called()
