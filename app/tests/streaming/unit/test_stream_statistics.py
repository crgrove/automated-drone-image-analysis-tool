"""Unit tests for StreamStatistics."""

import pytest
import sys
import time
from types import SimpleNamespace
from core.controllers.streaming.components.StreamStatistics import StreamStatistics, PerformanceStats


class TestStreamStatistics:
    """Test suite for StreamStatistics."""

    def test_initialization(self):
        """Test statistics initialization."""
        stats = StreamStatistics()

        assert stats.window_size == 30
        assert stats.start_time > 0
        assert stats.frame_count == 0
        assert stats.dropped_frame_count == 0
        assert stats.get_stats().total_frames == 0

    def test_initialization_with_window_size(self):
        """Test statistics initialization with custom window size."""
        stats = StreamStatistics(window_size=60)

        assert stats.window_size == 60

    def test_record_frame(self):
        """Test recording a frame."""
        stats = StreamStatistics()

        stats.on_frame_received()
        stats.on_frame_processed(16.67, 0)  # ~60 FPS processing time

        assert stats.frame_count == 1
        assert len(stats.processing_times) == 1
        assert stats.processing_times[0] == 16.67
        assert stats.get_stats().total_frames == 1

    def test_record_dropped_frame(self):
        """Test recording a dropped frame."""
        stats = StreamStatistics()

        stats.on_frame_dropped()

        assert stats.dropped_frame_count == 1
        assert stats.get_stats().dropped_frames == 1
        assert stats.frame_count == 0  # Dropped frames don't count

    def test_get_stats(self):
        """Test getting statistics."""
        stats = StreamStatistics()

        # Record some frames with proper timing
        for i in range(10):
            stats.on_frame_received()
            time.sleep(0.001)  # Small delay to create frame intervals
            stats.on_frame_processed(16.67, 0)  # ~60 FPS

        performance = stats.get_stats()

        assert isinstance(performance, PerformanceStats)
        assert performance.total_frames == 10
        assert performance.fps > 0
        assert performance.avg_processing_time_ms > 0

    def test_get_stats_with_dropped_frames(self):
        """Test getting statistics with dropped frames."""
        stats = StreamStatistics()

        # Record some frames and drops
        for i in range(10):
            stats.on_frame_received()
            stats.on_frame_processed(16.67, 0)
        for i in range(5):
            stats.on_frame_dropped()

        performance = stats.get_stats()

        assert performance.total_frames == 10
        assert performance.dropped_frames == 5

    def test_reset(self):
        """Test resetting statistics."""
        stats = StreamStatistics()

        # Record some data
        for i in range(10):
            stats.on_frame_received()
            stats.on_frame_processed(16.67, 0)
        stats.on_frame_dropped()

        # Reset
        stats.reset()

        assert stats.frame_count == 0
        assert stats.dropped_frame_count == 0
        assert len(stats.processing_times) == 0
        assert stats.get_stats().total_frames == 0
        assert stats.get_stats().dropped_frames == 0

    def test_fps_calculation(self, monkeypatch):
        """Test FPS calculation."""
        # FPS comes from wall-clock frame intervals, so drive the module's clock
        # rather than sleeping: a macOS CI runner overslept 33 ms sleeps ~4x and
        # the sleep-based version of this test measured 8 FPS.
        now = [1000.0]
        monkeypatch.setattr(sys.modules[StreamStatistics.__module__], 'time', SimpleNamespace(time=lambda: now[0]))
        stats = StreamStatistics()

        # Record frames at exactly 30 FPS (33.33ms per frame)
        # Note: FPS is calculated from frame intervals, not processing times
        frame_interval = 1.0 / 30.0
        for i in range(30):
            now[0] += frame_interval
            stats.on_frame_received()
            stats.on_frame_processed(33.33, 0)

        performance = stats.get_stats()

        assert performance.fps == pytest.approx(30.0)

    def test_processing_time_average(self):
        """Test processing time average calculation."""
        stats = StreamStatistics()

        # Record frames with varying processing times
        processing_times = [10.0, 20.0, 30.0, 40.0, 50.0]
        for pt in processing_times:
            stats.on_frame_received()
            stats.on_frame_processed(pt, 0)

        performance = stats.get_stats()

        # Average should be approximately 30.0
        assert 25.0 <= performance.avg_processing_time_ms <= 35.0

    def test_uptime_calculation(self):
        """Test uptime calculation."""
        stats = StreamStatistics()

        time.sleep(0.1)  # Wait a bit

        performance = stats.get_stats()

        assert performance.uptime_seconds >= 0.1
