"""Integration tests: location data in the streaming window.

Covers the two user-visible outcomes end to end — a HUD that tracks the
video and a map showing live position plus flight path — for both source
types, plus the ADIAT Flight telemetry path.
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
from core.services.streaming.FlightStreamService import FlightStreamManager
from core.services.streaming.RTMPStreamService import StreamType
from core.services.telemetry.DjiSrtParser import DjiSrtSample
from core.services.telemetry.TelemetrySourceResolver import (
    SOURCE_EMBEDDED,
    SOURCE_EXPLICIT_FILE,
    TelemetryResolution,
)
from core.services.telemetry.TelemetryTrack import TelemetryTrack

COORD = "core.controllers.streaming.components.StreamTelemetryCoordinator"


def _track(count=6):
    samples = [
        DjiSrtSample(
            start_seconds=float(i),
            end_seconds=float(i) + 0.03,
            latitude=30.0 + i * 0.001,
            longitude=-97.0 - i * 0.001,
            altitude_msl_m=200.0 + i,
            altitude_ato_m=15.0 + i,
            yaw_deg=45.0,
        )
        for i in range(count)
    ]
    return TelemetryTrack.from_dji_samples(samples)


PANEL_KEYS = ("panel/stream_controls_collapsed", "panel/map_collapsed")


@pytest.fixture
def viewer(qapp):
    window = StreamViewerWindow(algorithm_name='', theme='dark')
    # The window restores panel collapse state from real QSettings. Start
    # from a known state so these tests neither depend on nor leave behind
    # the developer's own preferences.
    for key in PANEL_KEYS:
        window.settings.remove(key)
    window.ui.streamControlGroup.setCollapsed(False)
    window.ui.mapGroup.setCollapsed(False)

    # Capture map JS instead of driving QtWebEngine.
    window._map_js = []
    window.map_view._run_js = window._map_js.append
    # Keep DEM enrichment out of the picture; it has its own suite.
    window.telemetry_coordinator._enrichment = MagicMock()
    window.telemetry_coordinator._enrichment.enrich.side_effect = lambda e: e
    yield window
    for key in PANEL_KEYS:
        window.settings.remove(key)
    window.close()
    QApplication.processEvents()


class StubFlightService(QObject):
    """Minimal stand-in for the WebRTC receive service."""

    frameReady = Signal(np.ndarray, float, int)
    connectionStatusChanged = Signal(bool, str)
    streamStatsChanged = Signal(dict)
    errorOccurred = Signal(str)
    dataChannelOpened = Signal(str)
    dataChannelMessage = Signal(str, bytes)
    finished = Signal()

    def __init__(self, signaling=None, pairing_code=None, fps_limit=None):
        super().__init__()
        self.pairing_code = pairing_code
        self.dropped_frames = 0

    def request_connect(self):
        pass

    def request_disconnect(self):
        pass

    def isRunning(self):
        return False

    def wait(self, ms):
        return True

    def set_fps_limit(self, fps_limit):
        return fps_limit


@pytest.fixture
def flight_services():
    created = []

    def factory(self, signaling, code, fps_limit):
        svc = StubFlightService(signaling, code, fps_limit)
        created.append(svc)
        return svc

    with patch.object(FlightStreamManager, "_build_service", factory), \
            patch("core.services.streaming.FlightStreamService."
                  "default_signaling_channel", return_value=MagicMock()):
        yield created


class TestLayout:
    def test_map_sits_in_the_right_column(self, viewer):
        """Not under the video: that pane is wide and short, which turns a
        map into an unusable letterbox strip."""
        assert viewer.ui.mapGroup.isAncestorOf(viewer.map_view)

    def test_map_sits_between_stream_and_algorithm_controls(self, viewer):
        column = viewer.ui.streamControlGroup.parentWidget().layout()
        order = [
            column.indexOf(viewer.ui.streamControlGroup),
            column.indexOf(viewer.ui.mapGroup),
            column.indexOf(viewer.ui.algorithmControlGroup),
        ]
        assert order == sorted(order)
        assert -1 not in order

    def test_stream_controls_and_map_are_collapsible(self, viewer):
        for section in (viewer.ui.streamControlGroup, viewer.ui.mapGroup):
            assert not section.isCollapsed()
            section.setCollapsed(True)
            assert section.isCollapsed()
            assert not section.content_widget.isVisibleTo(section)
            section.setCollapsed(False)
            assert not section.isCollapsed()

    def test_collapsed_state_is_persisted(self, viewer):
        """Folding a section is remembered across sessions.

        The fixture clears these keys before and after, so this cannot
        leak into another test or into the developer's settings.
        """
        viewer.ui.mapGroup.setCollapsed(True)
        assert viewer.settings.value("panel/map_collapsed") in (True, "true")

        viewer.ui.mapGroup.setCollapsed(False)
        assert viewer.settings.value("panel/map_collapsed") in (False, "false")

    def test_hud_starts_hidden(self, viewer):
        """No telemetry yet — nothing to overlay."""
        assert viewer.telemetry_hud.isHidden()

    def test_hud_is_a_child_of_the_video_pane(self, viewer):
        assert viewer.telemetry_hud.parent() is viewer.video_display


class TestFileSourceTelemetry:
    def _connect_file(self, viewer, track):
        manager = MagicMock()
        manager.connect_to_stream = MagicMock(return_value=True)
        resolution = TelemetryResolution(
            track=track, source=SOURCE_EMBEDDED, detail=f"{len(track)} fixes"
        )
        with patch("core.controllers.streaming.components."
                   "StreamCoordinator.StreamManager", return_value=manager), \
                patch(f"{COORD}.load_telemetry_for_video", return_value=resolution):
            viewer.on_connect_requested("v.mp4", StreamType.FILE)
        return manager

    def test_telemetry_loads_on_connect(self, viewer):
        self._connect_file(viewer, _track())
        assert viewer.telemetry_coordinator.is_available

    def test_source_is_reported_in_the_info_panel(self, viewer):
        self._connect_file(viewer, _track())
        assert "embedded" in viewer.ui.infoPanel.toPlainText().lower()

    def test_playback_drives_the_hud(self, viewer):
        self._connect_file(viewer, _track())
        viewer.on_stream_info_updated({"current_time": 3.0, "total_time": 6.0})
        QApplication.processEvents()

        assert not viewer.telemetry_hud.isHidden()
        env = viewer.telemetry_hud.last_envelope
        assert env["aircraft_latitude"] == pytest.approx(30.003)

    def test_playback_moves_the_aircraft_marker(self, viewer):
        self._connect_file(viewer, _track())
        viewer.on_stream_info_updated({"current_time": 2.0, "total_time": 6.0})
        assert any("setAircraft" in js for js in viewer._map_js)

    def test_playback_draws_the_flight_path(self, viewer):
        self._connect_file(viewer, _track())
        viewer.on_stream_info_updated({"current_time": 4.0, "total_time": 6.0})
        assert any("setTrack" in js for js in viewer._map_js)
        assert viewer.map_view.track_length() == 5

    def test_seeking_backwards_shrinks_the_path(self, viewer):
        self._connect_file(viewer, _track())
        viewer.on_stream_info_updated({"current_time": 5.0, "total_time": 6.0})
        long_path = viewer.map_view.track_length()
        viewer.on_stream_info_updated({"current_time": 1.0, "total_time": 6.0})
        assert viewer.map_view.track_length() < long_path

    def test_file_source_replaces_rather_than_appends(self, viewer):
        """Appending would leave a trail ahead of the playhead after a seek."""
        self._connect_file(viewer, _track())
        viewer.on_stream_info_updated({"current_time": 2.0, "total_time": 6.0})
        assert not any("appendTrack" in js for js in viewer._map_js)

    def test_video_without_telemetry_leaves_the_hud_hidden(self, viewer):
        manager = MagicMock()
        manager.connect_to_stream = MagicMock(return_value=True)
        with patch("core.controllers.streaming.components."
                   "StreamCoordinator.StreamManager", return_value=manager), \
                patch(f"{COORD}.load_telemetry_for_video",
                      return_value=TelemetryResolution(track=None, source="none")):
            viewer.on_connect_requested("plain.mp4", StreamType.FILE)
        viewer.on_stream_info_updated({"current_time": 1.0, "total_time": 6.0})

        assert viewer.telemetry_hud.isHidden()
        assert not viewer.telemetry_coordinator.is_available

    def test_disconnect_clears_hud_and_map(self, viewer):
        self._connect_file(viewer, _track())
        viewer.on_stream_info_updated({"current_time": 3.0, "total_time": 6.0})
        assert not viewer.telemetry_hud.isHidden()

        viewer.on_disconnect_requested()
        QApplication.processEvents()

        assert viewer.telemetry_hud.isHidden()
        assert viewer.map_view.track_length() == 0
        assert not viewer.telemetry_coordinator.is_available


class TestSecondaryMetadataFile:
    """An operator-selected SRT/CSV must survive the trip from the controls
    (or the wizard) to the resolver.

    Threading this through the widget rather than ``connectRequested`` is
    the fragile part: the signal is also fired by the wizard's auto-connect
    and by the pairing prompt, so the widget is the single source of truth
    and these tests pin that down.
    """

    def _connect(self, viewer, url="v.mp4", stream_type=StreamType.FILE):
        manager = MagicMock()
        manager.connect_to_stream = MagicMock(return_value=True)
        resolution = TelemetryResolution(
            track=_track(), source=SOURCE_EXPLICIT_FILE,
            path="C:/logs/flight.csv", detail="6 fixes from flight log",
        )
        with patch("core.controllers.streaming.components."
                   "StreamCoordinator.StreamManager", return_value=manager), \
                patch(f"{COORD}.load_telemetry_for_video",
                      return_value=resolution) as loader:
            viewer.on_connect_requested(url, stream_type)
        return loader

    def test_selected_file_reaches_the_resolver(self, viewer):
        viewer.stream_controls.set_metadata_path("C:/logs/flight.csv")
        loader = self._connect(viewer)
        assert loader.call_args[0][1] == "C:/logs/flight.csv"

    def test_no_selection_passes_nothing(self, viewer):
        loader = self._connect(viewer)
        assert not loader.call_args[0][1]

    def test_the_file_is_named_in_the_info_panel(self, viewer):
        viewer.stream_controls.set_metadata_path("C:/logs/flight.csv")
        self._connect(viewer)
        assert "flight.csv" in viewer.ui.infoPanel.toPlainText()

    def test_it_drives_the_hud_like_any_other_source(self, viewer):
        viewer.stream_controls.set_metadata_path("C:/logs/flight.csv")
        self._connect(viewer)
        viewer.on_stream_info_updated({"current_time": 3.0, "total_time": 6.0})
        QApplication.processEvents()

        assert not viewer.telemetry_hud.isHidden()
        assert viewer.telemetry_hud.last_envelope["aircraft_latitude"] == \
            pytest.approx(30.003)

    def test_it_draws_the_flight_path(self, viewer):
        viewer.stream_controls.set_metadata_path("C:/logs/flight.srt")
        self._connect(viewer)
        viewer.on_stream_info_updated({"current_time": 4.0, "total_time": 6.0})
        assert viewer.map_view.track_length() == 5

    def test_wizard_selection_is_carried_into_the_controls(self, viewer):
        viewer.apply_wizard_data({
            "stream_type": "File",
            "stream_url": "C:/videos/flight.mp4",
            "metadata_path": "C:/logs/flight.csv",
        })
        assert viewer.stream_controls.get_metadata_path() == "C:/logs/flight.csv"

    def test_wizard_selection_reaches_the_resolver_on_autoconnect(self, viewer):
        manager = MagicMock()
        manager.connect_to_stream = MagicMock(return_value=True)
        resolution = TelemetryResolution(
            track=_track(), source=SOURCE_EXPLICIT_FILE,
            path="C:/logs/flight.csv", detail="6 fixes",
        )
        with patch("core.controllers.streaming.components."
                   "StreamCoordinator.StreamManager", return_value=manager), \
                patch(f"{COORD}.load_telemetry_for_video",
                      return_value=resolution) as loader:
            viewer.apply_wizard_data({
                "stream_type": "File",
                "stream_url": "C:/videos/flight.mp4",
                "metadata_path": "C:/logs/flight.csv",
                "auto_connect": True,
            })
        assert loader.call_args[0][1] == "C:/logs/flight.csv"

    def test_a_live_source_never_receives_a_path(self, viewer, flight_services):
        """A pairing code has no sidecar; a leftover path would send the
        resolver hunting for a track that cannot exist."""
        viewer.stream_controls.set_metadata_path("C:/logs/flight.csv")
        with patch(f"{COORD}.load_telemetry_for_video") as loader:
            viewer.on_connect_requested("K7QM3P", StreamType.WEBRTC)
        loader.assert_not_called()


class TestAdiatFlightTelemetry:
    def test_live_telemetry_reaches_the_hud(self, viewer, flight_services):
        viewer.on_connect_requested("K7QM3P", StreamType.WEBRTC)
        service = flight_services[0]
        service.connectionStatusChanged.emit(True, "connected")
        service.dataChannelMessage.emit(
            "telemetry",
            b'{"aircraft_latitude": 30.5, "aircraft_longitude": -97.7,'
            b' "aircraft_altitude_msl_m": 210.0, "aircraft_altitude_agl_m": 40.0}',
        )
        QApplication.processEvents()

        assert not viewer.telemetry_hud.isHidden()
        assert viewer.telemetry_hud.last_envelope["aircraft_latitude"] == 30.5

    def test_live_telemetry_moves_the_aircraft(self, viewer, flight_services):
        viewer.on_connect_requested("K7QM3P", StreamType.WEBRTC)
        flight_services[0].dataChannelMessage.emit(
            "telemetry",
            b'{"aircraft_latitude": 30.5, "aircraft_longitude": -97.7}',
        )
        QApplication.processEvents()
        assert any("setAircraft" in js for js in viewer._map_js)

    def test_live_source_appends_to_the_path(self, viewer, flight_services):
        """A live feed has no track to recompute, so each fix extends it."""
        viewer.on_connect_requested("K7QM3P", StreamType.WEBRTC)
        service = flight_services[0]
        for lat in (30.5, 30.6, 30.7):
            service.dataChannelMessage.emit(
                "telemetry",
                f'{{"aircraft_latitude": {lat}, "aircraft_longitude": -97.7}}'.encode(),
            )
        QApplication.processEvents()
        assert viewer.map_view.track_length() == 3

    def test_detections_from_flight_are_still_ignored(self, viewer, flight_services):
        """Telemetry is consumed; publisher detections remain dropped."""
        viewer.on_connect_requested("K7QM3P", StreamType.WEBRTC)
        service = flight_services[0]
        service.connectionStatusChanged.emit(True, "connected")
        service.dataChannelMessage.emit(
            "detections.meta", b'{"event":"promote","track_key":"t1"}'
        )
        service.dataChannelMessage.emit("detections.thumb", b"\xff\xd8\xff")
        QApplication.processEvents()

        assert viewer.gallery_widget.gallery_list.count() == 0
        assert viewer.map_view.detection_count == 0
        assert viewer.telemetry_hud.isHidden()


class TestDetectionPins:
    def test_confirmed_track_is_pinned_at_the_aircraft_position(self, viewer):
        manager = MagicMock()
        manager.connect_to_stream = MagicMock(return_value=True)
        resolution = TelemetryResolution(
            track=_track(), source=SOURCE_EMBEDDED, detail="6 fixes"
        )
        with patch("core.controllers.streaming.components."
                   "StreamCoordinator.StreamManager", return_value=manager), \
                patch(f"{COORD}.load_telemetry_for_video", return_value=resolution):
            viewer.on_connect_requested("v.mp4", StreamType.FILE)
        viewer.on_stream_info_updated({"current_time": 2.0, "total_time": 6.0})

        track = MagicMock()
        track.track_id = 7
        track.first_frame_index = 60      # 2 s at 30 fps
        track.detection_type = "person"
        track.confidence = 0.9
        viewer.stream_coordinator.stream_info["source_fps"] = 30.0

        viewer._on_track_confirmed_for_map(track)
        assert viewer.map_view.detection_count == 1

    def test_no_pin_without_location_data(self, viewer):
        track = MagicMock()
        track.track_id = 1
        viewer._on_track_confirmed_for_map(track)
        assert viewer.map_view.detection_count == 0

    def test_pin_click_selects_the_gallery_track(self, viewer):
        sentinel = MagicMock()
        viewer._gallery_tracks_by_key["track-3"] = sentinel
        with patch.object(viewer, "_on_gallery_track_clicked") as handler:
            viewer._on_map_pin_clicked("track-3")
        handler.assert_called_once_with(sentinel)

    def test_unknown_pin_key_is_ignored(self, viewer):
        with patch.object(viewer, "_on_gallery_track_clicked") as handler:
            viewer._on_map_pin_clicked("nope")
        handler.assert_not_called()
