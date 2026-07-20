"""Unit tests for StreamManager FPS-limit behavior."""

from unittest.mock import Mock, patch

import cv2
import numpy as np
import pytest

from core.services.streaming.RTMPStreamService import (
    RTMPStreamService,
    StreamConfig,
    StreamManager,
    StreamType,
)


def _build_seekable_service():
    """A file-playback service with a stubbed capture, ready to seek."""
    service = RTMPStreamService(StreamConfig(url="video.mp4", stream_type=StreamType.FILE))
    service._cap = Mock()
    service._total_frames = 100
    service._video_fps = 30
    service._seek_admission_open = True
    return service


class _ScriptedCapture:
    """Minimal capture backend that exits once its scripted frames are read."""

    def __init__(self, frames, positions, set_results=None):
        self.frames = list(frames)
        self.positions = list(positions)
        self.set_results = list(set_results) if set_results is not None else None
        self.read_count = 0
        self.set_calls = []

    def isOpened(self):
        return self.read_count < len(self.frames)

    def read(self):
        frame = self.frames[self.read_count]
        self.read_count += 1
        if frame is None:
            return False, None
        return True, frame

    def get(self, property_id):
        if property_id == cv2.CAP_PROP_POS_FRAMES:
            position_index = max(0, self.read_count - 1)
            return self.positions[position_index]
        return 0

    def set(self, property_id, value):
        self.set_calls.append((property_id, value))
        if self.set_results is not None:
            return self.set_results.pop(0)
        return True

    def grab(self):
        return False


class _CopyFailingFrame(np.ndarray):
    """Valid-looking ndarray whose defensive copy fails."""

    def copy(self, order="C"):
        raise RuntimeError("copy failed")


def _prepare_process_loop(service, capture, target_frame=42):
    """Arm a paused file seek and return its request id."""
    service._cap = capture
    service._connected = True
    service._is_playing = False
    service._total_frames = 100
    assert service.seek_to_frame(target_frame) == target_frame
    return service.last_seek_id


class TestSeekToFrame:
    """Authoritative frame-index seeking used by gallery navigation."""

    def test_returns_resolved_frame_for_valid_index(self, qapp):
        service = _build_seekable_service()
        assert service.seek_to_frame(42) == 42
        assert service._seek_target_frame == 42
        assert service._seek_requested is True

    def test_frame_zero_is_successful(self, qapp):
        service = _build_seekable_service()
        # Frame 0 must be a success (not None), unlike a bare boolean API.
        assert service.seek_to_frame(0) == 0

    def test_clamps_below_zero_and_above_last_frame(self, qapp):
        service = _build_seekable_service()  # total_frames == 100
        assert service.seek_to_frame(-5) == 0
        assert service.seek_to_frame(9999) == 99  # total_frames - 1

    def test_returns_none_without_capture(self, qapp):
        service = RTMPStreamService(StreamConfig(url="video.mp4", stream_type=StreamType.FILE))
        service._cap = None
        assert service.seek_to_frame(5) is None

    def test_unknown_total_frames_does_not_clamp_to_zero(self, qapp):
        service = _build_seekable_service()
        service._total_frames = 0  # backend reports an unknown count as zero
        # Without the guard, min(42, -1) would collapse every seek to 0.
        assert service.seek_to_frame(42) == 42

    def test_seek_to_time_delegates_and_reports_bool(self, qapp):
        service = _build_seekable_service()
        assert service.seek_to_time(1.0) is True  # int(1.0 * 30) -> frame 30
        assert service._seek_target_frame == 30

    def test_manager_seek_to_frame_passes_through_resolved_value(self, qapp):
        manager = StreamManager()
        manager._service = Mock()
        manager._service.seek_to_frame = Mock(return_value=17)
        assert manager.seek_to_frame(17) == 17
        manager._service.seek_to_frame.assert_called_once_with(17)

    def test_manager_seek_to_frame_returns_none_without_service(self, qapp):
        manager = StreamManager()
        manager._service = None
        assert manager.seek_to_frame(3) is None

    def test_new_seek_fails_queued_predecessor(self, qapp):
        """Replacing an unapplied seek gives the old request one terminal result."""
        service = _build_seekable_service()
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        assert service.seek_to_frame(10) == 10
        first_id = service.last_seek_id
        assert service.seek_to_frame(20) == 20
        second_id = service.last_seek_id

        assert second_id > first_id
        assert completions == [(first_id, -1, False)]
        assert service._seek_target_id == second_id
        assert service._seek_target_frame == 20

    def test_new_seek_fails_active_predecessor_then_completes(self, qapp):
        """Replacing an active seek cannot silently drop or later re-complete it."""
        service = _build_seekable_service()
        service._cap.set = Mock(return_value=True)
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        assert service.seek_to_frame(10) == 10
        first_id = service.last_seek_id
        assert service._apply_seek_request() is True

        assert service.seek_to_frame(20) == 20
        second_id = service.last_seek_id
        assert completions == [(first_id, -1, False)]
        assert service._apply_seek_request() is True
        service._complete_pending_seek_frame(21)

        assert completions == [
            (first_id, -1, False),
            (second_id, 21, True),
        ]


class TestSeekThrottleBypass:
    """A completed seek must read its frame even under a low FPS throttle (paused seek)."""

    def test_normal_throttle_holds_within_interval(self, qapp):
        service = _build_seekable_service()
        service._video_fps = 5  # 200 ms interval
        # Only 10 ms since the last processed frame -> normally throttle.
        assert service._should_throttle_file_frame(
            current_time=100.010, last_process_time=100.000,
            fps_limit=5, frame_interval=0.2, seek_just_completed=False,
        ) is True

    def test_completed_seek_bypasses_throttle(self, qapp):
        service = _build_seekable_service()
        service._video_fps = 5  # 200 ms interval
        # Same tiny elapsed time, but a just-completed seek must NOT be throttled,
        # or the sought frame is never read and paused playback waits forever.
        assert service._should_throttle_file_frame(
            current_time=100.010, last_process_time=100.000,
            fps_limit=5, frame_interval=0.2, seek_just_completed=True,
        ) is False

    def test_throttle_expires_after_interval(self, qapp):
        service = _build_seekable_service()
        service._video_fps = 5  # 200 ms interval
        assert service._should_throttle_file_frame(
            current_time=100.300, last_process_time=100.000,
            fps_limit=5, frame_interval=0.2, seek_just_completed=False,
        ) is False


class TestApplySeekRequest:
    """Seek application must check cap.set() and only await a frame on success."""

    def test_successful_set_awaits_frame(self, qapp):
        service = _build_seekable_service()
        service._cap.set = Mock(return_value=True)
        service._seek_requested = True
        service._seek_target_frame = 42

        assert service._apply_seek_request() is True
        assert service._awaiting_seek_frame is True
        assert service._current_frame_pos == 42
        assert service._active_seek_target_frame == 42
        assert service._seek_requested is False

    def test_rejected_set_does_not_await(self, qapp):
        service = _build_seekable_service()
        service._cap.set = Mock(return_value=False)  # backend rejects the seek
        service._seek_requested = True
        service._seek_target_frame = 42

        assert service._apply_seek_request() is False
        # Must not strand paused playback waiting for a frame that never comes.
        assert service._awaiting_seek_frame is False
        assert service._seek_requested is False

    def test_set_exception_does_not_await(self, qapp):
        service = _build_seekable_service()
        service._cap.set = Mock(side_effect=RuntimeError("boom"))
        service._seek_requested = True
        service._seek_target_frame = 42

        assert service._apply_seek_request() is False
        assert service._awaiting_seek_frame is False
        assert service._seek_requested is False

    def test_no_pending_request_is_noop(self, qapp):
        service = _build_seekable_service()
        service._seek_requested = False
        service._awaiting_seek_frame = False

        assert service._apply_seek_request() is False
        assert service._awaiting_seek_frame is False

    def test_awaiting_frame_bypasses_throttle(self, qapp):
        service = _build_seekable_service()
        service._video_fps = 5  # 200 ms interval
        service._awaiting_seek_frame = True
        # A post-seek pending read must not be throttled even within the interval.
        assert service._should_throttle_file_frame(
            current_time=100.010, last_process_time=100.000,
            fps_limit=5, frame_interval=0.2, seek_just_completed=service._awaiting_seek_frame,
        ) is False


class TestProcessPendingSeekFrame:
    """The real capture loop must finish or fail every accepted seek."""

    def test_matching_post_read_position_completes_seek(self, qapp):
        service = _build_seekable_service()
        capture = _ScriptedCapture(
            [np.zeros((8, 8, 3), dtype=np.uint8)],
            positions=[43],
        )
        request_id = _prepare_process_loop(service, capture)
        frames = []
        completions = []
        service.frameReady.connect(
            lambda _frame, _timestamp, position: frames.append(position)
        )
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        service._process_stream()

        assert frames == [43]
        assert completions == [(request_id, 43, True)]
        assert service._awaiting_seek_frame is False

    def test_accepted_seek_with_wrong_backend_position_fails(self, qapp):
        service = _build_seekable_service()
        capture = _ScriptedCapture(
            [np.zeros((8, 8, 3), dtype=np.uint8)],
            positions=[90],
        )
        request_id = _prepare_process_loop(service, capture)
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        service._process_stream()

        assert completions == [(request_id, 90, False)]
        assert service._awaiting_seek_frame is False

    def test_transient_malformed_frame_retries_then_completes(self, qapp):
        service = _build_seekable_service()
        capture = _ScriptedCapture(
            [
                np.zeros((8,), dtype=np.uint8),
                np.zeros((8, 8, 3), dtype=np.uint8),
            ],
            # Both reads are of target 42 after the retry re-seeks it, so the
            # backend's post-read position is 43 each time.
            positions=[43, 43],
        )
        request_id = _prepare_process_loop(service, capture)
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        with patch("core.services.streaming.RTMPStreamService.time.sleep") as sleep:
            service._process_stream()

        assert capture.read_count == 2
        assert capture.set_calls == [
            (cv2.CAP_PROP_POS_FRAMES, 42),
            (cv2.CAP_PROP_POS_FRAMES, 42),
        ]
        sleep.assert_called_once_with(0.1)
        assert completions == [(request_id, 43, True)]
        assert service._awaiting_seek_frame is False

    def test_retry_rejection_fails_seek_immediately(self, qapp):
        """A backend that cannot re-seek after a bad frame terminates the request."""
        service = _build_seekable_service()
        capture = _ScriptedCapture(
            [np.zeros((8,), dtype=np.uint8)],
            positions=[43],
            set_results=[True, False],
        )
        request_id = _prepare_process_loop(service, capture)
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        with patch("core.services.streaming.RTMPStreamService.time.sleep") as sleep:
            service._process_stream()

        sleep.assert_not_called()
        assert completions == [(request_id, -1, False)]
        assert service._awaiting_seek_frame is False

    def test_capture_closure_cancels_seek_before_retry_limit(self, qapp):
        """Early loop exit still emits exactly one terminal failure."""
        service = _build_seekable_service()
        capture = _ScriptedCapture(
            [
                np.zeros((8,), dtype=np.uint8),
                np.zeros((8,), dtype=np.uint8),
            ],
            positions=[43, 43],
        )
        request_id = _prepare_process_loop(service, capture)
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        with patch("core.services.streaming.RTMPStreamService.time.sleep") as sleep:
            service._process_stream()

        assert capture.read_count == 2
        assert sleep.call_count == 2
        assert completions == [(request_id, -1, False)]
        assert service._awaiting_seek_frame is False
        assert service._seek_frame_failures == 0

    @pytest.mark.parametrize(
        "failure_mode",
        ["read", "shape", "resize", "copy", "emit"],
    )
    def test_repeated_processing_failure_is_bounded(
        self,
        qapp,
        monkeypatch,
        failure_mode,
    ):
        service = _build_seekable_service()
        valid_frame = np.zeros((8, 8, 3), dtype=np.uint8)

        if failure_mode == "read":
            failing_frame = None
        elif failure_mode == "shape":
            failing_frame = np.zeros((8,), dtype=np.uint8)
        elif failure_mode == "resize":
            failing_frame = valid_frame
            service.config.resolution_limit = (4, 4)
            monkeypatch.setattr(
                cv2,
                "resize",
                Mock(side_effect=RuntimeError("resize failed")),
            )
        elif failure_mode == "copy":
            failing_frame = valid_frame.view(_CopyFailingFrame)
        else:
            failing_frame = valid_frame
            monkeypatch.setattr(
                service,
                "_emit_frame_ready",
                Mock(side_effect=RuntimeError("emit failed")),
            )

        capture = _ScriptedCapture(
            [failing_frame] * 5,
            positions=[43] * 5,
        )
        request_id = _prepare_process_loop(service, capture)
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )

        with patch("core.services.streaming.RTMPStreamService.time.sleep") as sleep:
            service._process_stream()

        assert capture.read_count == 5
        assert capture.set_calls == [
            (cv2.CAP_PROP_POS_FRAMES, 42),
        ] * 5
        assert sleep.call_count == 4
        assert completions == [(request_id, -1, False)]
        assert service._awaiting_seek_frame is False


class TestSeekLifecycle:
    """Seek admission must close before teardown drains pending requests."""

    def test_cleanup_rejects_seek_arriving_during_capture_release(self, qapp):
        service = _build_seekable_service()
        service._connected = True
        attempted_results = []
        completions = []
        service.seekCompleted.connect(
            lambda seek_id, position, success: completions.append(
                (seek_id, position, success)
            )
        )
        service._cap.release.side_effect = lambda: attempted_results.append(
            service.seek_to_frame(5)
        )

        with patch("core.services.streaming.RTMPStreamService.time.sleep"):
            service._cleanup()

        assert attempted_results == [None]
        assert service._seek_requested is False
        assert service._awaiting_seek_frame is False
        assert completions == []


def _build_mock_service():
    service = Mock()
    for signal_name in [
        "frameReady",
        "connectionStatusChanged",
        "streamStatsChanged",
        "videoPositionChanged",
        "errorOccurred",
    ]:
        signal = Mock()
        signal.connect = Mock()
        setattr(service, signal_name, signal)
    service.start = Mock()
    return service


class TestStreamManagerFpsLimit:
    """Test FPS-limit mapping from UI/controller into stream config."""

    def test_connect_with_none_preserves_source_fps_mode(self):
        manager = StreamManager()
        mock_service = _build_mock_service()

        with patch("core.services.streaming.RTMPStreamService.RTMPStreamService", return_value=mock_service) as ctor:
            assert manager.connect_to_stream("video.mp4", StreamType.FILE, fps_limit=None) is True
            stream_config = ctor.call_args.args[0]
            assert stream_config.fps_limit is None

    def test_connect_with_zero_normalizes_to_source_fps_mode(self):
        manager = StreamManager()
        mock_service = _build_mock_service()

        with patch("core.services.streaming.RTMPStreamService.RTMPStreamService", return_value=mock_service) as ctor:
            assert manager.connect_to_stream("video.mp4", StreamType.FILE, fps_limit=0) is True
            stream_config = ctor.call_args.args[0]
            assert stream_config.fps_limit is None

    def test_connect_with_positive_value_uses_explicit_cap(self):
        manager = StreamManager()
        mock_service = _build_mock_service()

        with patch("core.services.streaming.RTMPStreamService.RTMPStreamService", return_value=mock_service) as ctor:
            assert manager.connect_to_stream("video.mp4", StreamType.FILE, fps_limit=15) is True
            stream_config = ctor.call_args.args[0]
            assert stream_config.fps_limit == 15

    def test_connect_with_high_fps_is_clamped(self):
        manager = StreamManager()
        mock_service = _build_mock_service()

        with patch("core.services.streaming.RTMPStreamService.RTMPStreamService", return_value=mock_service) as ctor:
            assert manager.connect_to_stream("video.mp4", StreamType.FILE, fps_limit=240) is True
            stream_config = ctor.call_args.args[0]
            assert stream_config.fps_limit == 60
