"""
StreamStatistics - Track and calculate streaming performance statistics.

Provides FPS calculation, latency tracking, and other performance metrics.
"""

import time
from collections import deque
from typing import Optional, Dict
from dataclasses import dataclass, field


@dataclass
class PerformanceStats:
    """Performance statistics data."""
    fps: float = 0.0
    processing_fps: float = 0.0
    avg_processing_time_ms: float = 0.0
    latency_ms: float = 0.0
    dropped_frames: int = 0
    total_frames: int = 0
    detection_count: int = 0
    uptime_seconds: float = 0.0


class StreamStatistics:
    """
    Tracks and calculates streaming performance statistics.

    Monitors:
    - Frame rate (FPS)
    - Processing time per frame
    - Latency
    - Frame drops
    - Detection counts
    """

    def __init__(self, window_size: int = 30):
        """
        Initialize statistics tracker.

        Args:
            window_size: Number of samples to use for rolling averages
        """
        self.window_size = window_size

        # Timing tracking
        self.start_time = time.time()
        self.last_frame_time = time.time()
        self.frame_times = deque(maxlen=window_size)
        self.processing_times = deque(maxlen=window_size)

        # Counters
        self.frame_count = 0
        self.dropped_frame_count = 0
        self.detection_count = 0

        # Current stats
        self._stats = PerformanceStats()

    def on_frame_received(self, timestamp: Optional[float] = None):
        """
        Record frame receipt.

        Args:
            timestamp: Optional timestamp of frame (for latency calculation)
        """
        current_time = time.time()

        # Calculate frame interval
        frame_interval = current_time - self.last_frame_time
        self.frame_times.append(frame_interval)
        self.last_frame_time = current_time

        # Calculate latency if timestamp provided
        if timestamp:
            latency = (current_time - timestamp) * 1000  # Convert to ms
            self._stats.latency_ms = latency

        self.frame_count += 1

        # Update FPS
        self._calculate_fps()

    def on_frame_processed(self, processing_time_ms: float, detection_count: int = 0):
        """
        Record frame processing completion.

        Args:
            processing_time_ms: Time taken to process frame (milliseconds)
            detection_count: Number of detections in this frame
        """
        self.processing_times.append(processing_time_ms)
        self.detection_count += detection_count

        # Update processing stats
        self._calculate_processing_stats()

    def on_frame_dropped(self):
        """Record a dropped frame."""
        self.dropped_frame_count += 1
        self._stats.dropped_frames = self.dropped_frame_count

    def get_stats(self) -> PerformanceStats:
        """
        Get current statistics.

        Returns:
            PerformanceStats object with current metrics
        """
        # Update uptime
        self._stats.uptime_seconds = time.time() - self.start_time
        self._stats.total_frames = self.frame_count
        self._stats.detection_count = self.detection_count

        return self._stats

    def get_stats_dict(self) -> Dict[str, str]:
        """
        Get formatted statistics as dictionary for display.

        Returns:
            Dictionary of stat name -> formatted value
        """
        stats = self.get_stats()

        return {
            'FPS': f"{stats.fps:.1f}",
            'Processing': f"{stats.processing_fps:.1f} fps",
            'Avg Time': f"{stats.avg_processing_time_ms:.1f} ms",
            'Latency': f"{stats.latency_ms:.1f} ms",
            'Dropped': str(stats.dropped_frames),
            'Total Frames': str(stats.total_frames),
            'Detections': str(stats.detection_count),
            'Uptime': self._format_uptime(stats.uptime_seconds)
        }

    def reset(self):
        """Reset all statistics."""
        self.start_time = time.time()
        self.last_frame_time = time.time()
        self.frame_times.clear()
        self.processing_times.clear()
        self.frame_count = 0
        self.dropped_frame_count = 0
        self.detection_count = 0
        self._stats = PerformanceStats()

    def _calculate_fps(self):
        """Calculate current FPS from frame intervals."""
        if len(self.frame_times) > 1:
            avg_interval = sum(self.frame_times) / len(self.frame_times)
            if avg_interval > 0:
                self._stats.fps = 1.0 / avg_interval
            else:
                self._stats.fps = 0.0
        else:
            self._stats.fps = 0.0

    def _calculate_processing_stats(self):
        """Calculate processing statistics."""
        if len(self.processing_times) > 0:
            # Average processing time
            self._stats.avg_processing_time_ms = sum(self.processing_times) / len(self.processing_times)

            # Processing FPS (theoretical max based on processing time)
            if self._stats.avg_processing_time_ms > 0:
                self._stats.processing_fps = 1000.0 / self._stats.avg_processing_time_ms
            else:
                self._stats.processing_fps = 0.0
        else:
            self._stats.avg_processing_time_ms = 0.0
            self._stats.processing_fps = 0.0

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
