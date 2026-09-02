"""Integration tests: per-feed recording in the Flight Viewer.

Each tile owns a :class:`RecordingService`, so every inbound feed is
independently recordable — video, detections, telemetry and map land in
one bundle per feed, the same reviewable artifact the streaming window
produces. These tests drive FlightTileController the way the tile's
context menu does and read the bundles back off disk.
"""

from __future__ import annotations

import os
import sys
from importlib import import_module

import cv2
import numpy as np
import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QFileDialog

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.controllers.flight import FlightTileController  # noqa: E402
from core.services.streaming.RecordingSessionService import read_manifest  # noqa: E402
from core.services.streaming.signaling import InMemorySignalingChannel  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


class FakeRecordingManager(QObject):
    """Stands in for the video writer; these tests are about the bundle."""

    recordingStateChanged = Signal(bool, str)
    recordingStats = Signal(dict)

    def __init__(self, output_dir):
        super().__init__()
        self.output_dir = output_dir
        self.frames = 0

    def start_recording(self, resolution, filename_prefix="rtmp_recording"):
        self.resolution = tuple(resolution)
        video = os.path.join(self.output_dir, "flight_recording.mp4")
        with open(video, "wb") as fp:
            fp.write(b"\x00")
        self.recordingStateChanged.emit(True, video)
        return True

    def stop_recording(self):
        return None

    def add_frame(self, frame, timestamp=None):
        self.frames += 1
        return True

    def get_recording_info(self):
        return {"total_frames": self.frames}


@pytest.fixture(autouse=True)
def fake_recording_manager(monkeypatch):
    recording_module = import_module("core.services.streaming.RecordingService")
    monkeypatch.setattr(recording_module, "RecordingManager", FakeRecordingManager)


@pytest.fixture
def recording_dir(tmp_path, monkeypatch):
    """Answer the controller's folder dialog with a temp directory."""
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        staticmethod(lambda *a, **k: str(tmp_path)),
    )
    return tmp_path


def _make_controller(code="ABC234"):
    controller = FlightTileController(signaling=InMemorySignalingChannel())
    controller._pairing_code = code
    controller._materialize_tile(code)
    return controller


def _frame(width=1280, height=720):
    return np.zeros((height, width, 3), dtype=np.uint8)


def _detection(seq=0, with_thumb=True):
    thumb = None
    if with_thumb:
        ok, buf = cv2.imencode(".jpg", np.full((30, 40, 3), 200, dtype=np.uint8))
        assert ok
        thumb = buf.tobytes()
    return {
        "track_key": f"person|sess|{seq}",
        "class_name": "person",
        "detector_id": "person",
        "confidence": 0.8 + seq * 0.01,
        "captured_at_ms": 1_787_300_000_000 + seq,
        "bbox_norm": [0.25, 0.5, 0.1, 0.2],
        "location": {"lat": 30.25 + seq * 0.001, "lon": -97.75},
        "thumb_bytes": thumb,
        "seq": seq,
    }


def _telemetry(step=0):
    return {
        "aircraft_latitude": 30.25 + step * 0.001,
        "aircraft_longitude": -97.75 - step * 0.001,
        "aircraft_altitude_agl_m": 60.0,
        "captured_at_ms": 1_787_300_000_000 + step * 500,
        "aircraft_name": "TEXSAR-01",
        "aircraft_serial": "SN123",
    }


class TestStartStop:
    def test_start_requires_a_video_frame(self, recording_dir):
        """The writer is sized from source resolution, known only from a frame."""
        controller = _make_controller()
        try:
            controller._on_recording_start_requested(controller._tile)

            assert controller._recording.is_recording is False
            assert "video" in controller._tile.ui.statusBadgeLabel.text().lower()
        finally:
            controller.tear_down()

    def test_start_records_at_source_resolution(self, recording_dir):
        """The old tile recorder sized the video to the on-screen pixmap;

        a 4K feed came out at whatever the tile measured. The recording is
        now sized from the actual frame.
        """
        controller = _make_controller()
        try:
            controller._tile._latest_frame_bgr = _frame(3840, 2160)
            controller._on_recording_start_requested(controller._tile)

            assert controller._recording.is_recording is True
            assert controller._recording.recording_manager.resolution == (3840, 2160)
            assert controller._tile.is_recording is True
            assert "REC" in controller._tile.ui.statusBadgeLabel.text()
        finally:
            controller.tear_down()

    def test_cancelled_dialog_starts_nothing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: "")
        )
        controller = _make_controller()
        try:
            controller._tile._latest_frame_bgr = _frame()
            controller._on_recording_start_requested(controller._tile)

            assert controller._recording.is_recording is False
        finally:
            controller.tear_down()

    def test_chosen_folder_is_remembered(self, recording_dir):
        controller = _make_controller()
        try:
            controller._tile._latest_frame_bgr = _frame()
            controller._on_recording_start_requested(controller._tile)

            settings = controller._recording_settings()
            assert settings.value(controller._RECORDING_DIR_KEY) == str(recording_dir)
        finally:
            controller.tear_down()

    def test_stop_produces_a_reviewable_bundle(self, recording_dir):
        """Video, detections, telemetry, map — one folder per feed."""
        controller = _make_controller("K3F9PM")
        finished = []
        controller.recordingFinished.connect(lambda code, result: finished.append((code, result)))
        try:
            tile = controller._tile
            tile._latest_frame_bgr = _frame()
            # Telemetry before start so the aircraft identity reaches the manifest.
            controller._publish_telemetry(_telemetry(0))
            controller._on_recording_start_requested(tile)
            bundle = controller._recording.recording_bundle_dir
            assert bundle is not None

            for i in range(5):
                controller._on_frame_for_recording(_frame(), 0.0, i)
            controller._on_detection_promoted(_detection(0))
            controller._on_detection_promoted(_detection(1, with_thumb=False))
            for step in range(1, 4):
                controller._publish_telemetry(_telemetry(step))

            controller._on_recording_stop_requested(tile)

            assert len(finished) == 1
            code, result = finished[0]
            assert code == "K3F9PM"
            assert result["counts"]["detections_stored"] == 2
            assert result["counts"]["telemetry_fixes"] == 3
            # The default footprint is the replay set; the fake video
            # writer dropped an MP4, so the sidecar SRT rides beside it.
            for name in ("detections.jsonl", "telemetry.jsonl",
                         "manifest.json", "flight_recording.SRT"):
                assert os.path.isfile(os.path.join(bundle, name)), name
            for name in ("detections.csv", "ADIAT_Data.xml",
                         "flight_map.html", "flight_path.kml"):
                assert not os.path.exists(os.path.join(bundle, name)), name
            # Both detections have images: the mobile thumb verbatim, and
            # the thumbless one cropped from the live frame.
            assert os.path.isfile(os.path.join(bundle, "detections", "detection_0000.jpg"))
            assert os.path.isfile(os.path.join(bundle, "detections", "detection_0001.jpg"))

            manifest = read_manifest(bundle)
            assert manifest["algorithm"] == "ADIAT Flight"
            assert manifest["source"]["type"] == "webrtc"
            assert manifest["feed"]["pairing_code"] == "K3F9PM"
            assert manifest["feed"]["aircraft_name"] == "TEXSAR-01"
            assert manifest["feed"]["aircraft_serial"] == "SN123"

            assert tile.is_recording is False
            assert tile.ui.statusBadgeLabel.toolTip() == bundle
        finally:
            controller.tear_down()

    def test_detections_before_recording_are_not_stored(self, recording_dir):
        """A recording covers its own window, not the whole session."""
        controller = _make_controller()
        finished = []
        controller.recordingFinished.connect(lambda code, r: finished.append(r))
        try:
            tile = controller._tile
            tile._latest_frame_bgr = _frame()
            controller._on_detection_promoted(_detection(0))

            controller._on_recording_start_requested(tile)
            controller._on_detection_promoted(_detection(1))
            controller._on_recording_stop_requested(tile)

            assert finished[0]["counts"]["detections_stored"] == 1
        finally:
            controller.tear_down()

    def test_tear_down_finalizes_an_active_recording(self, recording_dir):
        """Closing the tile must not cost the operator the recording."""
        controller = _make_controller()
        finished = []
        controller.recordingFinished.connect(lambda code, result: finished.append(result))

        tile = controller._tile
        tile._latest_frame_bgr = _frame()
        controller._on_recording_start_requested(tile)
        controller._on_detection_promoted(_detection(0))
        bundle = controller._recording.recording_bundle_dir

        controller.tear_down()

        assert len(finished) == 1
        assert finished[0]["counts"]["detections_stored"] == 1
        assert os.path.isfile(os.path.join(bundle, "detections.jsonl"))


@pytest.fixture
def fake_open_replay(monkeypatch):
    """Capture handoffs to the dedicated Replay window."""
    opened = []
    replay_module = import_module("core.controllers.streaming.ReplayWindow")
    monkeypatch.setattr(replay_module, "open_replay", lambda video: opened.append(video))
    return opened


class TestReplayHandoff:
    """One click on the tile opens the recording in the replay surface."""

    def _record_once(self, controller):
        controller._tile._latest_frame_bgr = _frame()
        controller._on_recording_start_requested(controller._tile)
        bundle = controller._recording.recording_bundle_dir
        controller._on_recording_stop_requested(controller._tile)
        return bundle

    def test_a_finished_recording_offers_replay(self, recording_dir):
        controller = _make_controller()
        try:
            assert controller._tile._replay_available is False

            bundle = self._record_once(controller)

            assert controller._tile._replay_available is True
            assert controller._last_replay_video == os.path.join(
                bundle, "flight_recording.mp4"
            )
        finally:
            controller.tear_down()

    def test_replay_opens_the_dedicated_replay_window(
            self, recording_dir, fake_open_replay):
        """Replay is its own experience - the handoff goes to ReplayWindow,
        never to the analysis page."""
        controller = _make_controller()
        try:
            bundle = self._record_once(controller)

            controller._tile.replayRequested.emit(controller._tile)

            assert fake_open_replay == [
                os.path.join(bundle, "flight_recording.mp4")
            ]
        finally:
            controller.tear_down()

    def test_each_click_repoints_the_replay_window(
            self, recording_dir, fake_open_replay):
        controller = _make_controller()
        try:
            self._record_once(controller)

            controller._tile.replayRequested.emit(controller._tile)
            controller._tile.replayRequested.emit(controller._tile)

            # open_replay itself reuses one window per app; the tile just
            # asks twice.
            assert len(fake_open_replay) == 2
        finally:
            controller.tear_down()

    def test_replay_before_any_recording_is_a_soft_no(
            self, recording_dir, fake_open_replay):
        controller = _make_controller()
        try:
            controller._tile.replayRequested.emit(controller._tile)

            assert fake_open_replay == []
            badge = controller._tile.ui.statusBadgeLabel.text()
            assert "No finished recording" in badge
        finally:
            controller.tear_down()

    def test_replay_survives_the_bundle_being_deleted(
            self, recording_dir, fake_open_replay):
        """A vanished folder degrades to the badge, not a crash."""
        import shutil

        controller = _make_controller()
        try:
            bundle = self._record_once(controller)
            shutil.rmtree(bundle)

            controller._tile.replayRequested.emit(controller._tile)

            assert fake_open_replay == []
        finally:
            controller.tear_down()


class TestRecordingFolderDialog:
    """Field report: the picker opened on "Path does not exist"."""

    def test_the_default_folder_is_created_not_just_named(self, monkeypatch, tmp_path):
        """Handing getExistingDirectory an uncreated path greets the
        operator with a Windows error instead of a folder."""
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        controller = _make_controller()
        try:
            default = controller._default_recording_dir()
            assert not os.path.isdir(default)

            resolved = controller._resolve_start_dir("")

            assert os.path.isdir(resolved)
            assert os.path.normpath(resolved) == os.path.normpath(default)
        finally:
            controller.tear_down()

    def test_an_existing_saved_folder_is_honoured(self, monkeypatch, tmp_path):
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        saved = tmp_path / "flight_recordings"
        saved.mkdir()
        controller = _make_controller()
        try:
            assert os.path.normpath(controller._resolve_start_dir(str(saved))) == \
                os.path.normpath(str(saved))
        finally:
            controller.tear_down()

    def test_a_saved_folder_on_a_missing_drive_falls_back(self, monkeypatch, tmp_path):
        """The operator's card reader is not attached today."""
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))
        controller = _make_controller()
        try:
            # "Z:/..." is a missing drive only on Windows; a path under a regular file is unreachable everywhere.
            blocker = tmp_path / "card_reader"
            blocker.write_text("")
            resolved = controller._resolve_start_dir(str(blocker / "recordings"))

            assert os.path.isdir(resolved)
            assert "card_reader" not in resolved
        finally:
            controller.tear_down()

    def test_it_always_returns_something_openable(self, monkeypatch, tmp_path):
        """Even if every candidate fails, the dialog gets a real folder."""
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        monkeypatch.setenv("HOME", str(tmp_path))

        def refuse(*_args, **_kwargs):
            raise OSError("read-only")

        controller = _make_controller()
        try:
            monkeypatch.setattr(os, "makedirs", refuse)
            resolved = controller._resolve_start_dir("Z:/nope")

            assert os.path.isdir(resolved)
        finally:
            controller.tear_down()


class TestIndependence:
    """Two feeds, two recordings, no cross-talk."""

    def test_each_feed_records_its_own_bundle(self, recording_dir):
        alpha = _make_controller("AAA111")
        bravo = _make_controller("BBB222")
        results = {}
        alpha.recordingFinished.connect(lambda code, r: results.setdefault(code, r))
        bravo.recordingFinished.connect(lambda code, r: results.setdefault(code, r))
        try:
            alpha._tile._latest_frame_bgr = _frame(1280, 720)
            bravo._tile._latest_frame_bgr = _frame(1920, 1080)

            alpha._on_recording_start_requested(alpha._tile)
            bravo._on_recording_start_requested(bravo._tile)
            bundle_a = alpha._recording.recording_bundle_dir
            bundle_b = bravo._recording.recording_bundle_dir
            assert bundle_a != bundle_b

            # Interleaved traffic stays with its own feed.
            alpha._on_detection_promoted(_detection(0))
            bravo._on_detection_promoted(_detection(10))
            bravo._on_detection_promoted(_detection(11))
            alpha._publish_telemetry(_telemetry(0))
            bravo._publish_telemetry(_telemetry(1))
            bravo._publish_telemetry(_telemetry(2))

            # Stopping one feed leaves the other recording.
            alpha._on_recording_stop_requested(alpha._tile)
            assert bravo._recording.is_recording is True
            bravo._on_detection_promoted(_detection(12))
            bravo._on_recording_stop_requested(bravo._tile)

            assert results["AAA111"]["counts"]["detections_stored"] == 1
            assert results["AAA111"]["counts"]["telemetry_fixes"] == 1
            assert results["BBB222"]["counts"]["detections_stored"] == 3
            assert results["BBB222"]["counts"]["telemetry_fixes"] == 2
            assert read_manifest(bundle_a)["video"]["resolution"] == [1280, 720]
            assert read_manifest(bundle_b)["video"]["resolution"] == [1920, 1080]
        finally:
            alpha.tear_down()
            bravo.tear_down()

    def test_only_the_recording_feed_captures(self, recording_dir):
        recording = _make_controller("AAA111")
        idle = _make_controller("BBB222")
        finished = []
        recording.recordingFinished.connect(lambda code, r: finished.append(r))
        try:
            recording._tile._latest_frame_bgr = _frame()
            idle._tile._latest_frame_bgr = _frame()
            recording._on_recording_start_requested(recording._tile)

            # Traffic on the idle feed goes nowhere.
            idle._on_detection_promoted(_detection(5))
            idle._publish_telemetry(_telemetry(5))
            idle._on_frame_for_recording(_frame(), 0.0, 0)
            assert idle._recording.is_recording is False

            recording._on_detection_promoted(_detection(0))
            recording._on_recording_stop_requested(recording._tile)

            assert finished[0]["counts"]["detections_stored"] == 1
        finally:
            recording.tear_down()
            idle.tear_down()
