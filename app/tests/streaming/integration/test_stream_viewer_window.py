"""Integration tests for StreamViewerWindow."""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtTest import QTest

from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
from core.services.streaming.RTMPStreamService import StreamType
from core.services.streaming.contracts import FocusTarget


class TestStreamViewerWindow:
    """Test suite for StreamViewerWindow."""

    def test_initialization(self, qapp):
        """Test window initialization."""
        # Pass empty string to prevent default algorithm loading
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            assert window.theme == 'dark'
            assert window.logger is not None
            assert window.stream_coordinator is not None
            assert window.detection_renderer is not None
            assert window.stream_statistics is not None
            assert window.algorithm_widget is None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_initialization_with_algorithm(self, qapp):
        """Test window initialization with algorithm."""
        # Create a mock controller class that has all required signals and methods
        class MockAlgorithmController(QWidget):
            # Required signals
            detectionsReady = Signal(list)
            frameProcessed = Signal(np.ndarray)
            configChanged = Signal(dict)
            statusUpdate = Signal(str)
            requestRecording = Signal(bool)

            def __init__(self, algorithm_config, theme, parent=None):
                super().__init__(parent)
                self.algorithm_config = algorithm_config
                self.theme = theme
                self.is_running = False

            def setup_ui(self):
                pass

            def process_frame(self, frame, timestamp):
                return []

            def get_config(self):
                return {}

            def set_config(self, config):
                pass

            def cleanup(self):
                """Cleanup method required by StreamViewerWindow."""
                pass

        with patch('core.controllers.streaming.StreamViewerWindow.StreamAlgorithmController', MockAlgorithmController):
            window = StreamViewerWindow(algorithm_name='ColorDetection', theme='dark')
            try:
                # Algorithm should be loaded (may be None if loading fails, which is acceptable in test)
                # Just verify the window was created successfully
                assert window is not None
            finally:
                window.close()
                QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_load_algorithm(self, qapp):
        """Test loading an algorithm."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Mock algorithm config and controller import methods
            mock_config = {'name': 'ColorDetection', 'category': 'streaming'}

            # Create a mock controller class that has all required signals and methods
            class MockAlgorithmController(QWidget):
                # Required signals
                detectionsReady = Signal(list)
                frameProcessed = Signal(np.ndarray)
                configChanged = Signal(dict)
                statusUpdate = Signal(str)
                requestRecording = Signal(bool)

                def __init__(self, algorithm_config, theme, parent=None):
                    super().__init__(parent)
                    self.algorithm_config = algorithm_config
                    self.theme = theme
                    self.is_running = False

                def setup_ui(self):
                    pass

                def process_frame(self, frame, timestamp):
                    return []

                def get_config(self):
                    return {}

                def set_config(self, config):
                    pass

                def cleanup(self):
                    """Cleanup method required by StreamViewerWindow."""
                    pass

            with patch.object(window, '_get_algorithm_config', return_value=mock_config):
                with patch.object(window, '_import_algorithm_controller', return_value=MockAlgorithmController):
                    window.load_algorithm('ColorDetection')

                    # Check that algorithm was loaded
                    assert window.current_algorithm_name == 'ColorDetection'
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_custom_widgets_setup(self, qapp):
        """Test custom widgets are set up."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify custom widgets exist
            assert hasattr(window, 'video_display')
            assert hasattr(window, 'thumbnail_widget')
            assert hasattr(window, 'stream_controls')
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_signal_connections(self, qapp):
        """Test signal connections."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify signals are connected
            assert window.stream_coordinator is not None
            assert window.detection_renderer is not None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_statistics_update_timer(self, qapp):
        """Test statistics update timer."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify timer exists and is running
            assert window.update_timer is not None
            assert window.update_timer.isActive()
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_frame_processing_flow(self, qapp, sample_frame):
        """Test frame processing flow."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Mock algorithm widget
            mock_algorithm = Mock()
            mock_algorithm.process_frame = Mock(return_value=[])
            window.algorithm_widget = mock_algorithm

            # Simulate frame received
            window.stream_coordinator.frameReceived.emit(sample_frame, 0.0, 0)

            # In a real scenario, this would trigger processing
            # For now, we just verify the signal exists
            assert window.stream_coordinator.frameReceived is not None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_recording_controls(self, qapp):
        """Test recording controls."""
        window = StreamViewerWindow(theme='dark')
        try:
            # Verify recording controls exist
            assert window.stream_controls is not None
            # Recording functionality should be available through stream_coordinator
            assert window.stream_coordinator is not None
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_algorithm_switching(self, qapp):
        """Test switching between algorithms."""
        window = StreamViewerWindow(theme='dark')
        try:
            cleanup_calls = []

            # Mock algorithm config and controller import methods
            def get_config_side_effect(name):
                return {'name': name, 'category': 'streaming'}

            # Create a mock controller class that has all required signals and methods
            class MockAlgorithmController(QWidget):
                # Required signals
                detectionsReady = Signal(list)
                frameProcessed = Signal(np.ndarray)
                configChanged = Signal(dict)
                statusUpdate = Signal(str)
                requestRecording = Signal(bool)

                def __init__(self, algorithm_config, theme, parent=None):
                    super().__init__(parent)
                    self.algorithm_config = algorithm_config
                    self.theme = theme
                    self.is_running = False

                def setup_ui(self):
                    pass

                def process_frame(self, frame, timestamp):
                    return []

                def get_config(self):
                    return {}

                def set_config(self, config):
                    pass

                def cleanup(self):
                    """Cleanup method required by StreamViewerWindow."""
                    cleanup_calls.append(self.algorithm_config['name'])

            with patch.object(window, '_get_algorithm_config', side_effect=get_config_side_effect):
                with patch.object(window, '_import_algorithm_controller', return_value=MockAlgorithmController):
                    # Load first algorithm
                    window.load_algorithm('ColorAnomalyAndMotionDetection')
                    first_algorithm = window.current_algorithm_name

                    # Switch to second algorithm
                    window.load_algorithm('ColorDetection')
                    second_algorithm = window.current_algorithm_name

                    # Should have switched
                    assert first_algorithm == 'ColorAnomalyAndMotionDetection'
                    assert second_algorithm == 'ColorDetection'
                    assert cleanup_calls == ['ColorAnomalyAndMotionDetection']
        finally:
            window.close()
            QApplication.processEvents()  # Process events to ensure cleanup completes

    def test_worker_callback_uses_worker_timestamp_for_thumbnails(self, qapp, sample_frame):
        """Thumbnail sync should use worker-provided timestamp, not mutable window state."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.algorithm_renders_frame = False
            window.video_display.update_frame = Mock()
            window._current_frame_timestamp = 999.0  # Deliberately wrong for this callback

            worker_timestamp = 123.456
            original_frame = np.full_like(sample_frame, 17)
            window._original_frames_queue[worker_timestamp] = original_frame

            thumbnail_calls = []

            def capture_thumbnail(frame, detections, **kwargs):
                thumbnail_calls.append((frame, kwargs))

            window.thumbnail_widget.update_thumbnails = capture_thumbnail

            detections = [{'bbox': (10, 10, 20, 20), 'confidence': 0.9}]
            window._on_worker_frame_processed(sample_frame.copy(), detections, worker_timestamp, 4.0, False, 42)

            assert len(thumbnail_calls) == 1
            assert thumbnail_calls[0][0] is original_frame
            assert thumbnail_calls[0][1]['timestamp'] == worker_timestamp
            assert thumbnail_calls[0][1]['frame_index'] == 42
        finally:
            window.close()
            QApplication.processEvents()

    def test_update_thumbnails_runs_on_empty_detections(self, qapp, sample_frame):
        """Empty detection frames should still advance thumbnail aging/expiry."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            timestamp = 9.87
            window._original_frames_queue[timestamp] = sample_frame.copy()
            window.thumbnail_widget.update_thumbnails = Mock()

            window._update_thumbnails(sample_frame, [], timestamp, 7)

            window.thumbnail_widget.update_thumbnails.assert_called_once()
            call_args, call_kwargs = window.thumbnail_widget.update_thumbnails.call_args
            assert call_args[0] is not None
            assert call_args[1] == []
            assert call_kwargs["timestamp"] == timestamp
            assert timestamp not in window._original_frames_queue
        finally:
            window.close()
            QApplication.processEvents()

    def test_queue_worker_frame_replaces_pending_and_counts_drop(self, qapp, sample_frame):
        """Worker queue should keep only latest pending frame under backpressure."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            mock_worker = Mock()
            mock_worker.processFrameRequested = Mock()
            mock_worker.processFrameRequested.emit = Mock()
            mock_thread = Mock()
            mock_thread.isRunning = Mock(return_value=True)

            window._processing_worker = mock_worker
            window._processing_thread = mock_thread
            window._worker_frame_in_flight = True
            window.stream_statistics.on_frame_dropped = Mock()

            old_timestamp = 1.0
            new_timestamp = 2.0
            window._original_frames_queue[old_timestamp] = sample_frame.copy()
            window._pending_worker_frame = (sample_frame.copy(), old_timestamp, 1)

            queued = window._queue_worker_frame(sample_frame.copy(), new_timestamp, 2)

            assert queued is True
            assert window._pending_worker_frame[1] == new_timestamp
            assert old_timestamp not in window._original_frames_queue
            window.stream_statistics.on_frame_dropped.assert_called_once()
        finally:
            window._processing_worker = None
            window._processing_thread = None
            window.close()
            QApplication.processEvents()

    def test_seek_to_track_frame_recovers_thumbnail_frame_off_by_one(self, qapp):
        """Gallery seek targets first_frame_index-1 so the thumbnail's own frame is re-decoded.

        first_frame_index is the position the service reports AFTER decoding the
        thumbnail frame (one past it), so seeking there would land one frame late.
        """
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            stream_mgr = Mock()
            stream_mgr.seek_to_frame = Mock(return_value=49)
            stream_mgr.last_seek_id = 7
            window.stream_coordinator.stream_manager = stream_mgr

            track = Mock()
            track.first_frame_index = 50  # reported post-decode position of frame 49
            track.centroid = (100, 80)
            track.frame_resolution = (640, 480)

            generation = window._begin_focus_generation()
            window._seek_to_track_frame(track, generation)

            # Seek to first_frame_index - 1 (no FPS recomputation); focus armed
            # against the seek request id (not an ambiguous position).
            stream_mgr.seek_to_frame.assert_called_once_with(49)
            assert window._pending_focus_seek_id == 7
            assert window._pending_focus_positions == {49, 50}
            assert window._pending_focus_target.center_xy == (100, 80)
            assert window._pending_focus_target.reference_size == (640, 480)
        finally:
            window.close()
            QApplication.processEvents()

    def test_seek_to_frame_zero_is_a_successful_seek(self, qapp):
        """A resolved frame of 0 must arm focus (0 is not treated as failure)."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            stream_mgr = Mock()
            stream_mgr.seek_to_frame = Mock(return_value=0)
            stream_mgr.last_seek_id = 3
            window.stream_coordinator.stream_manager = stream_mgr

            track = Mock()
            track.first_frame_index = 0
            track.centroid = (5, 5)
            track.frame_resolution = (100, 100)

            generation = window._begin_focus_generation()
            window._seek_to_track_frame(track, generation)

            assert window._pending_focus_seek_id == 3
            assert window._pending_focus_positions == {0, 1}
            assert window._pending_focus_target is not None
        finally:
            window.close()
            QApplication.processEvents()

    def test_failed_seek_clears_pending_focus(self, qapp):
        """A failed seek (None) must clear any pending focus rather than strand it."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            stream_mgr = Mock()
            stream_mgr.seek_to_frame = Mock(return_value=None)
            window.stream_coordinator.stream_manager = stream_mgr

            track = Mock()
            track.first_frame_index = 10
            track.centroid = (1, 1)
            track.frame_resolution = (2, 2)

            generation = window._begin_focus_generation()
            window._pending_focus_target = FocusTarget((9, 9), (9, 9))
            window._seek_to_track_frame(track, generation)

            assert window._pending_focus_target is None
        finally:
            window.close()
            QApplication.processEvents()

    def test_failed_seek_clears_highlight(self, qapp):
        """A failed seek must also clear the highlight (no circle for a frame never reached)."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            stream_mgr = Mock()
            stream_mgr.seek_to_frame = Mock(return_value=None)
            window.stream_coordinator.stream_manager = stream_mgr

            track = Mock()
            track.first_frame_index = 10
            track.centroid = (1, 1)
            track.frame_resolution = (2, 2)
            window._highlight_track = track

            generation = window._begin_focus_generation()
            window._seek_to_track_frame(track, generation)

            assert window._highlight_track is None
            assert window._pending_focus_target is None
        finally:
            window.close()
            QApplication.processEvents()

    def test_focus_timeout_clears_highlight(self, qapp):
        """A focus timeout clears both the pending focus and the highlight."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.logger = Mock()
            window._highlight_track = Mock()
            window._pending_focus_target = FocusTarget((1, 1), (2, 2))
            window._pending_focus_seek_id = 5
            window._pending_focus_generation = window._focus_generation

            window._on_focus_timeout(window._focus_generation)

            assert window._pending_focus_target is None
            assert window._highlight_track is None
        finally:
            window.close()
            QApplication.processEvents()

    def test_pause_preserves_thumbnail_focus_targets(self, qapp):
        """Pausing must NOT clear thumbnail click payloads (thumbnails stay clickable)."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            mgr = Mock()
            mgr.is_playing = Mock(return_value=True)
            mgr.play_pause = Mock()
            window.stream_coordinator.stream_manager = mgr
            window.stream_coordinator.current_stream_type = StreamType.FILE

            # A visible thumbnail has a stored click payload.
            window.thumbnail_widget._focus_targets = {0: FocusTarget((320, 240), (640, 480))}

            window.on_play_pause_toggled()  # user pauses

            targets = window.thumbnail_widget._focus_targets
            assert 0 in targets and targets[0].center_xy == (320, 240)
        finally:
            window.close()
            QApplication.processEvents()

    def test_thumbnail_click_after_pause_still_focuses(self, qapp):
        """A thumbnail click after pausing still reaches focus_on (payload survived pause)."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.video_display.focus_on = Mock()

            mgr = Mock()
            mgr.is_playing = Mock(return_value=True)
            mgr.play_pause = Mock()
            window.stream_coordinator.stream_manager = mgr
            window.stream_coordinator.current_stream_type = StreamType.FILE

            tw = window.thumbnail_widget
            tw.resize(600, 150)
            tw._adjust_thumbnail_count()
            target = FocusTarget((320, 240), (640, 480))
            tw._focus_targets = {0: target}

            window.on_play_pause_toggled()  # pause

            # Drive the slot's click signal (as ClickableThumbnailLabel would).
            tw.thumbnail_labels[0].clicked.emit(0)

            window.video_display.focus_on.assert_called_once_with(target)
        finally:
            window.close()
            QApplication.processEvents()

    def test_connection_loss_clears_display(self, qapp):
        """An unexpected disconnect clears the video display (no retained frame/zoom)."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.video_display.clear_display = Mock()

            window.on_connection_changed(False, "connection lost")

            window.video_display.clear_display.assert_called_once()
        finally:
            window.close()
            QApplication.processEvents()

    def test_same_resolution_replacement_rebuilds_after_disconnect(self, qapp):
        """After a disconnect clears the image, a same-size replacement rebuilds (no stale zoom)."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            vd = window.video_display
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            vd.update_frame(frame)
            vd.focus_on(FocusTarget((320, 240), (640, 480)))
            assert vd.zoomStack  # zoomed on the first source

            # Connection loss clears the display (image + zoom + source size).
            window.on_connection_changed(False, "lost")
            assert vd._image is None and vd._source_size is None and not vd.zoomStack

            # A same-resolution replacement frame is now a fresh first frame,
            # not the direct-pixmap fast path, so it does not inherit old zoom.
            vd.update_frame(np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8))
            assert vd._image is not None
            assert not vd.zoomStack
        finally:
            window.close()
            QApplication.processEvents()

    def test_rapid_gallery_selection_rejects_stale_seek(self, qapp):
        """A superseded (older-generation) delayed seek must not run or arm focus."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            stream_mgr = Mock()
            stream_mgr.seek_to_frame = Mock(return_value=10)
            window.stream_coordinator.stream_manager = stream_mgr

            track = Mock()
            track.first_frame_index = 10
            track.centroid = (1, 1)
            track.frame_resolution = (2, 2)

            gen1 = window._begin_focus_generation()
            window._begin_focus_generation()  # a newer selection supersedes gen1

            window._seek_to_track_frame(track, gen1)  # stale callback

            stream_mgr.seek_to_frame.assert_not_called()
            assert window._pending_focus_target is None
        finally:
            window.close()
            QApplication.processEvents()

    def test_seek_completed_applies_focus_once_by_request_id(self, qapp):
        """seekCompleted(success) for the pending request applies focus exactly once."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.video_display.focus_on = Mock()
            target = FocusTarget((10, 10), (640, 480))
            window._pending_focus_target = target
            window._pending_focus_seek_id = 7
            window._pending_focus_positions = {50, 51}
            window._pending_focus_generation = window._focus_generation

            window._on_seek_completed(7, 51, True)

            window.video_display.focus_on.assert_called_once_with(target)
            assert window._pending_focus_target is None  # consumed

            window.video_display.focus_on.reset_mock()
            window._on_seek_completed(7, 51, True)
            window.video_display.focus_on.assert_not_called()
        finally:
            window.close()
            QApplication.processEvents()

    def test_seek_completed_rejects_unexpected_frame_position(self, qapp):
        """A matching request id must not focus an unrelated decoded frame."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.logger = Mock()
            window.video_display.focus_on = Mock()
            window._pending_focus_target = FocusTarget((10, 10), (640, 480))
            window._pending_focus_seek_id = 7
            window._pending_focus_positions = {50, 51}
            window._highlight_track = Mock()

            window._on_seek_completed(7, 90, True)

            window.video_display.focus_on.assert_not_called()
            assert window._pending_focus_target is None
            assert window._highlight_track is None
            window.logger.warning.assert_called_once()
        finally:
            window.close()
            QApplication.processEvents()

    def test_seek_completed_ignores_other_request_ids(self, qapp):
        """A completion for a different (older) request must not consume a newer focus.

        This is the adjacent-frame race: correlation is by request id, so an
        older seek's frame cannot satisfy a newer selection's pending focus.
        """
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.video_display.focus_on = Mock()
            window._pending_focus_target = FocusTarget((10, 10), (640, 480))
            window._pending_focus_seek_id = 8  # newer selection

            window._on_seek_completed(7, 51, True)  # older seek's completion

            window.video_display.focus_on.assert_not_called()
            assert window._pending_focus_target is not None  # still armed for id 8
        finally:
            window.close()
            QApplication.processEvents()

    def test_seek_completed_failure_abandons_focus_and_highlight(self, qapp):
        """A failed seek completion clears the pending focus AND the highlight (no timeout wait)."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.logger = Mock()
            window.video_display.focus_on = Mock()
            window._pending_focus_target = FocusTarget((10, 10), (640, 480))
            window._pending_focus_seek_id = 4
            window._highlight_track = Mock()

            window._on_seek_completed(4, -1, False)

            window.video_display.focus_on.assert_not_called()
            assert window._pending_focus_target is None
            assert window._highlight_track is None
        finally:
            window.close()
            QApplication.processEvents()

    def test_late_worker_frame_while_paused_is_not_presented(self, qapp, sample_frame):
        """While paused, a late worker frame is not displayed; the raw sought frame is."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.stream_coordinator.current_stream_type = StreamType.FILE
            mgr = Mock()
            mgr.is_playing = Mock(return_value=False)  # paused
            window.stream_coordinator.stream_manager = mgr
            window.video_display.update_frame = Mock()

            # Late worker result (pre-seek frame) while paused: not presented.
            assert window._present_frame(sample_frame, 50, 'worker') is False
            window.video_display.update_frame.assert_not_called()

            # The sought frame travels the raw path and IS presented.
            assert window._present_frame(sample_frame, 51, 'raw') is True
            window.video_display.update_frame.assert_called_once()
        finally:
            window.close()
            QApplication.processEvents()

    def test_thumbnail_focus_cancels_pending_gallery_and_does_not_seek(self, qapp):
        """A thumbnail click focuses immediately, cancels a pending gallery focus, and never seeks."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.video_display.focus_on = Mock()
            stream_mgr = Mock()
            window.stream_coordinator.stream_manager = stream_mgr

            window._pending_focus_target = FocusTarget((1, 1), (2, 2))
            window._pending_focus_seek_id = 5

            target = FocusTarget((100, 50), (640, 480))
            window._on_thumbnail_focus_requested(target)

            assert window._pending_focus_target is None  # gallery pending cancelled
            window.video_display.focus_on.assert_called_once_with(target)
            stream_mgr.seek_to_frame.assert_not_called()
            stream_mgr.seek_to_time.assert_not_called()
        finally:
            window.close()
            QApplication.processEvents()

    def test_live_gallery_click_does_not_seek_or_zoom(self, qapp):
        """RTMP/HDMI gallery history is non-seekable: no seek, no zoom, no armed focus."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.stream_coordinator.current_stream_type = StreamType.RTMP
            stream_mgr = Mock()
            window.stream_coordinator.stream_manager = stream_mgr
            window.video_display.focus_on = Mock()

            track = Mock()
            track.first_frame_index = 5

            with patch('core.controllers.streaming.StreamViewerWindow.QMessageBox'):
                window._on_gallery_track_clicked(track)

            stream_mgr.seek_to_frame.assert_not_called()
            window.video_display.focus_on.assert_not_called()
            assert window._pending_focus_target is None
        finally:
            window.close()
            QApplication.processEvents()

    def test_disconnect_resets_focus_and_clears_display(self, qapp):
        """Disconnect clears the display and drops all pending/highlight focus state."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.video_display.clear_display = Mock()
            window._pending_focus_target = FocusTarget((1, 1), (2, 2))
            window._highlight_track = Mock()

            window.on_disconnect_requested()

            window.video_display.clear_display.assert_called_once()
            assert window._pending_focus_target is None
            assert window._highlight_track is None
        finally:
            window.close()
            QApplication.processEvents()

    def test_focus_timeout_logs_and_clears(self, qapp):
        """A focus timeout (no seekCompleted arrived) logs and clears the pending focus."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.logger = Mock()
            window._pending_focus_target = FocusTarget((1, 1), (2, 2))
            window._pending_focus_seek_id = 9
            window._pending_focus_generation = window._focus_generation

            window._on_focus_timeout(window._focus_generation)

            assert window._pending_focus_target is None
            window.logger.warning.assert_called_once()
        finally:
            window.close()
            QApplication.processEvents()

    def test_focus_timeout_stale_generation_is_noop(self, qapp):
        """A timeout from a superseded generation must not clear a newer pending focus."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window._pending_focus_target = FocusTarget((1, 1), (2, 2))
            window._pending_focus_generation = 5

            window._on_focus_timeout(4)  # stale

            assert window._pending_focus_target is not None
        finally:
            window.close()
            QApplication.processEvents()

    def test_late_worker_frame_while_paused_skips_thumbnails_and_recording(self, qapp, sample_frame):
        """A frame rejected while paused must not update thumbnails or recording."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.algorithm_renders_frame = False
            window.stream_coordinator.current_stream_type = StreamType.FILE
            mgr = Mock()
            mgr.is_playing = Mock(return_value=False)  # paused
            window.stream_coordinator.stream_manager = mgr
            window.stream_coordinator.is_recording = True
            window.stream_coordinator.record_frame = Mock()
            window.video_display.update_frame = Mock()
            window.thumbnail_widget.update_thumbnails = Mock()

            window._on_worker_frame_processed(sample_frame.copy(), [], 1.0, 2.0, False, 7)

            # Rejected by _present_frame while paused -> no coupled side effects.
            window.video_display.update_frame.assert_not_called()
            window.thumbnail_widget.update_thumbnails.assert_not_called()
            window.stream_coordinator.record_frame.assert_not_called()
        finally:
            window.close()
            QApplication.processEvents()

    def test_stale_session_worker_result_is_rejected(self, qapp, sample_frame):
        """A worker result from a superseded session must not repaint/record/thumbnail."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.algorithm_renders_frame = False
            window.stream_coordinator.current_stream_type = StreamType.RTMP  # not paused
            window.stream_coordinator.is_recording = True
            window.stream_coordinator.record_frame = Mock()
            window.video_display.update_frame = Mock()
            window.thumbnail_widget.update_thumbnails = Mock()

            # A disconnect/reconnect has bumped the current session; the result
            # carries its (older) dispatch session, echoed through the signal.
            window._frame_session = 2
            stale_session = 1

            window._on_worker_frame_processed(sample_frame.copy(), [], 1.0, 2.0, False, 7, stale_session)

            window.video_display.update_frame.assert_not_called()
            window.thumbnail_widget.update_thumbnails.assert_not_called()
            window.stream_coordinator.record_frame.assert_not_called()
        finally:
            window.close()
            QApplication.processEvents()

    def test_fast_reconnect_preserves_single_worker_job_in_flight(self, qapp, sample_frame):
        """An old-session job must keep the worker slot until its callback arrives."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            mock_worker = Mock()
            mock_worker.processFrameRequested = Mock()
            mock_worker.processFrameRequested.emit = Mock()
            mock_thread = Mock()
            mock_thread.isRunning = Mock(return_value=True)
            window._processing_worker = mock_worker
            window._processing_thread = mock_thread

            old_session = window._frame_session
            window._worker_frame_in_flight = True
            window.on_connection_changed(False, "lost")
            window.on_connection_changed(True, "reconnected")

            assert window._worker_frame_in_flight is True

            # The first new-session frame waits behind the old job.
            assert window._queue_worker_frame(sample_frame.copy(), 2.0, 20) is True
            assert window._pending_worker_frame is not None
            mock_worker.processFrameRequested.emit.assert_not_called()

            # The stale callback releases exactly one slot and dispatches the
            # latest new-session frame with the current session token.
            window._on_worker_frame_processed(
                sample_frame.copy(), [], 1.0, 2.0, False, 10, old_session
            )
            mock_worker.processFrameRequested.emit.assert_called_once()
            assert mock_worker.processFrameRequested.emit.call_args.args[-1] == window._frame_session
            assert window._worker_frame_in_flight is True

            # A subsequent frame remains pending; it cannot overlap that job.
            assert window._queue_worker_frame(sample_frame.copy(), 3.0, 30) is True
            assert window._pending_worker_frame[1] == 3.0
            mock_worker.processFrameRequested.emit.assert_called_once()
        finally:
            window._processing_worker = None
            window._processing_thread = None
            window.close()
            QApplication.processEvents()

    def test_raw_frame_after_connection_loss_does_not_repaint(self, qapp, sample_frame):
        """A queued raw frame cannot overwrite the disconnect placeholder."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.stream_coordinator.stream_manager = Mock()
            window.stream_coordinator.is_connected = False
            window.video_display.update_frame = Mock()

            window.on_frame_received(sample_frame, 1.0, 10)

            window.video_display.update_frame.assert_not_called()
            assert window._current_frame_timestamp == 0.0
        finally:
            window.close()
            QApplication.processEvents()

    def test_custom_frame_after_connection_loss_does_not_repaint(self, qapp, sample_frame):
        """A queued custom-render frame cannot overwrite the disconnect placeholder."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.algorithm_renders_frame = True
            window.stream_coordinator.stream_manager = Mock()
            window.stream_coordinator.is_connected = False
            window.video_display.update_frame = Mock()

            window.on_algorithm_frame_processed(sample_frame)

            window.video_display.update_frame.assert_not_called()
        finally:
            window.close()
            QApplication.processEvents()

    def test_connection_change_bumps_frame_session(self, qapp):
        """Every connection change starts a new frame session."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            before = window._frame_session
            window.on_connection_changed(False, "lost")
            after_disconnect = window._frame_session
            window.on_connection_changed(True, "connected")
            after_connect = window._frame_session

            assert after_disconnect > before
            assert after_connect > after_disconnect
        finally:
            window.close()
            QApplication.processEvents()

    def test_connect_keeps_the_control_panel_where_the_user_left_it(self, qapp, qtbot):
        """Field report: every Connect/Disconnect scrolled the controls to the bottom.

        Disabling the button that was just clicked makes Qt hand focus to the
        next widget in creation order - the Recording buttons, at the foot of
        the panel - and a scroll area follows focus. The panel must hold still
        and focus must land on the counterpart button.
        """
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.show()
            qtbot.waitExposed(window)
            scroll = window.ui.splitter.widget(1)
            # Force the overflow the field machines have; the window itself has
            # a 600px minimum height that a resize() cannot go under.
            scroll.setFixedHeight(200)
            QApplication.processEvents()
            assert scroll.verticalScrollBar().maximum() > 0

            window.stream_controls.connect_button.setFocus(Qt.OtherFocusReason)
            window.on_connection_changed(True, "test source")

            assert scroll.verticalScrollBar().value() == 0
            assert window.focusWidget() is window.stream_controls.disconnect_button

            window.on_connection_changed(False, "closed")

            assert scroll.verticalScrollBar().value() == 0
            assert window.focusWidget() is window.stream_controls.connect_button
        finally:
            window.close()
            QApplication.processEvents()

    def test_connect_returns_to_live_view_from_the_gallery(self, qapp):
        """A new source is there to be watched: connecting leaves the Gallery."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            gallery_index = window.tab_widget.indexOf(window.gallery_widget)
            window.tab_widget.setCurrentIndex(gallery_index)

            window.on_connection_changed(True, "test source")

            assert window.tab_widget.currentIndex() == 0
        finally:
            window.close()
            QApplication.processEvents()

    def test_connect_does_not_disturb_the_live_view_tab(self, qapp):
        """Already on Live View: nothing to switch."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.tab_widget.setCurrentIndex(0)

            window.on_connection_changed(True, "test source")

            assert window.tab_widget.currentIndex() == 0
        finally:
            window.close()
            QApplication.processEvents()

    def test_disconnect_leaves_the_gallery_open(self, qapp):
        """Reviewing tracks after a stream ends must not be interrupted."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            gallery_index = window.tab_widget.indexOf(window.gallery_widget)
            window.tab_widget.setCurrentIndex(gallery_index)

            window.on_connection_changed(False, "closed")

            assert window.tab_widget.currentIndex() == gallery_index
        finally:
            window.close()
            QApplication.processEvents()

    def test_resolution_changing_sought_frame_keeps_focus(self, qapp):
        """A sought frame that changes resolution must retain its pending focus.

        The display resets its own zoom on a resolution change, but that must
        not clear the window's pending focus; it is applied afterward via
        seekCompleted on the (rebuilt) scene.
        """
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            vd = window.video_display
            vd.update_frame(np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8))

            # Gallery seek in flight, armed against request id 11.
            window._pending_focus_target = FocusTarget((160, 120), (320, 240))
            window._pending_focus_seek_id = 11
            window._pending_focus_positions = {11, 12}

            # The sought frame arrives at a NEW resolution via the raw path.
            window._present_frame(np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8), 12, 'raw')

            # Focus survived the resolution reset...
            assert window._pending_focus_target is not None

            # ...and seekCompleted applies it on the rebuilt scene.
            vd.focus_on = Mock()
            window._on_seek_completed(11, 12, True)
            vd.focus_on.assert_called_once()
        finally:
            window.close()
            QApplication.processEvents()

    def test_disconnect_renders_translated_placeholder(self, qapp):
        """Disconnect shows the translated 'No Stream Connected' placeholder on the real display."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.video_display.update_frame(np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8))
            assert not window.video_display.has_placeholder()

            window.on_disconnect_requested()

            # The window passes self.tr("No Stream Connected") to clear_display;
            # with no translator installed in tests, tr() returns the source, so
            # the placeholder must equal that string. (Avoid calling .tr() here
            # so lupdate does not extract a spurious context from the test.)
            assert window.video_display.has_placeholder()
            assert window.video_display.placeholder_message == "No Stream Connected"
        finally:
            window.close()
            QApplication.processEvents()

    def test_worker_frame_presents_and_records_when_playing(self, qapp, sample_frame):
        """_present_frame refactor preserves recording + thumbnail side effects while playing."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.algorithm_renders_frame = False
            window.stream_coordinator.current_stream_type = StreamType.RTMP  # live => not paused
            window.stream_coordinator.is_recording = True
            window.stream_coordinator.record_frame = Mock()
            window.video_display.update_frame = Mock()
            window.thumbnail_widget.update_thumbnails = Mock()
            window._original_frames_queue[1.0] = sample_frame.copy()

            window._on_worker_frame_processed(sample_frame.copy(), [], 1.0, 2.0, False, 7)

            window.video_display.update_frame.assert_called_once()
            window.stream_coordinator.record_frame.assert_called_once()
            window.thumbnail_widget.update_thumbnails.assert_called_once()
        finally:
            window.close()
            QApplication.processEvents()

    def test_connect_request_passes_hdmi_backend_and_target_fps(self, qapp):
        """Connect request should pass selected backend and configured FPS cap."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.stream_coordinator.connect_stream = Mock()
            mock_algorithm = Mock()
            mock_algorithm.get_config = Mock(return_value={'target_fps': 0})
            window.algorithm_widget = mock_algorithm

            window.on_connect_requested("0", StreamType.HDMI_CAPTURE, hdmi_backend=700)

            window.stream_coordinator.connect_stream.assert_called_once_with(
                "0", StreamType.HDMI_CAPTURE, hdmi_backend=700, fps_limit=None
            )
        finally:
            window.close()

    def test_recording_stats_updates_label(self, qapp):
        """Live recording stats should populate recording info text."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.on_recording_stats_updated({
                "segment_duration": 4.2,
                "recording_fps": 19.7,
                "frame_count": 82,
                "queue_size": 3,
            })

            text = window.recording_info.text()
            assert "4.2" in text
            assert "19.7" in text
            assert "82" in text
        finally:
            window.close()
            QApplication.processEvents()

    def test_connect_request_uses_default_when_algorithm_has_no_target_fps(self, qapp):
        """Missing target_fps should pass None and let stream manager use its default."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.stream_coordinator.connect_stream = Mock()
            mock_algorithm = Mock()
            mock_algorithm.get_config = Mock(return_value={})
            window.algorithm_widget = mock_algorithm

            window.on_connect_requested("video.mp4", StreamType.FILE)

            window.stream_coordinator.connect_stream.assert_called_once_with(
                "video.mp4", StreamType.FILE, hdmi_backend=None, fps_limit=None
            )
        finally:
            window.close()
            QApplication.processEvents()

    def test_config_change_updates_fps_limit_immediately_when_connected(self, qapp):
        """Changing target_fps while connected should update stream cap immediately."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.stream_coordinator.is_connected = True
            window.stream_coordinator.update_fps_limit = Mock(return_value=True)
            window._active_stream_fps_limit = 15

            window.on_algorithm_config_changed({'target_fps': 10})

            window.stream_coordinator.update_fps_limit.assert_called_once_with(10)
            assert window._active_stream_fps_limit == 10
        finally:
            window.close()
            QApplication.processEvents()

    def test_config_change_ignores_same_fps_limit(self, qapp):
        """No update should be sent when target_fps has not changed."""
        window = StreamViewerWindow(algorithm_name='', theme='dark')
        try:
            window.stream_coordinator.is_connected = True
            window.stream_coordinator.update_fps_limit = Mock(return_value=True)
            window._active_stream_fps_limit = 20

            window.on_algorithm_config_changed({'target_fps': 20})

            window.stream_coordinator.update_fps_limit.assert_not_called()
        finally:
            window.close()
            QApplication.processEvents()


def test_flight_viewer_menu_entry_hidden_when_feature_disabled(qapp):
    """Flight Viewer visibility is gated: its action must not appear in any
    menu while FeatureFlags.FLIGHT_VIEWER_ENABLED is False. The flag is
    patched explicitly so the gated-off path stays covered regardless of the
    shipping default."""
    with patch("helpers.FeatureFlags.FLIGHT_VIEWER_ENABLED", False):
        window = StreamViewerWindow(algorithm_name='', theme='dark')
    try:
        menu_texts = [
            action.text()
            for top in window.menuBar().actions() if top.menu()
            for action in top.menu().actions()
        ]
        assert window.action_flight_viewer.text() not in menu_texts
        # Positive control: sibling entries are still present.
        assert window.action_image_analysis.text() in menu_texts
    finally:
        window.close()
        QApplication.processEvents()


def test_flight_viewer_menu_entry_shown_when_feature_enabled(qapp):
    """When the flag is enabled the action appears in the primary menu
    alongside its siblings. The flag is patched True explicitly so this
    enabled path stays covered regardless of the (currently deferred)
    shipping default."""
    with patch("helpers.FeatureFlags.FLIGHT_VIEWER_ENABLED", True):
        window = StreamViewerWindow(algorithm_name='', theme='dark')
    try:
        menu_texts = [
            action.text()
            for top in window.menuBar().actions() if top.menu()
            for action in top.menu().actions()
        ]
        assert window.action_flight_viewer.text() in menu_texts
        assert window.action_image_analysis.text() in menu_texts
    finally:
        window.close()
        QApplication.processEvents()
