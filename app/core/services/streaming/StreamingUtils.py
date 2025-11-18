"""
Shared utilities for streaming video processing.

This module provides common infrastructure for all streaming detection algorithms:
- FrameQueue: Low-latency single-slot frame queue with automatic frame dropping
- ThreadedCaptureWorker: Background thread for continuous frame capture
- PerformanceMetrics: Performance tracking and statistics
- TimingOverlayRenderer: Renders performance overlays on frames
"""

import time
import threading
import numpy as np
import cv2
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field
from threading import Thread, Lock
from core.services.LoggerService import LoggerService


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

@dataclass
class StageTimings:
    """Timing measurements for each pipeline stage."""
    capture_ms: float = 0.0
    preprocessing_ms: float = 0.0
    detection_ms: float = 0.0
    motion_detection_ms: float = 0.0
    color_detection_ms: float = 0.0
    fusion_ms: float = 0.0
    render_ms: float = 0.0
    total_ms: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'capture_ms': self.capture_ms,
            'preprocessing_ms': self.preprocessing_ms,
            'detection_ms': self.detection_ms,
            'motion_detection_ms': self.motion_detection_ms,
            'color_detection_ms': self.color_detection_ms,
            'fusion_ms': self.fusion_ms,
            'render_ms': self.render_ms,
            'total_ms': self.total_ms
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for streaming detection."""
    fps: float = 0.0
    frame_count: int = 0
    detection_count: int = 0
    dropped_frames: int = 0
    average_timings: Optional[StageTimings] = None
    processing_time_ms: float = 0.0
    recent_timings: List[StageTimings] = field(default_factory=list)
    max_recent_samples: int = 30

    def update(self, timings: StageTimings, detection_count: int):
        """Update metrics with new timing data."""
        self.frame_count += 1
        self.detection_count = detection_count
        self.recent_timings.append(timings)

        # Keep only recent samples
        if len(self.recent_timings) > self.max_recent_samples:
            self.recent_timings.pop(0)

        # Calculate averages
        if self.recent_timings:
            avg = StageTimings()
            avg.capture_ms = np.mean([t.capture_ms for t in self.recent_timings])
            avg.preprocessing_ms = np.mean([t.preprocessing_ms for t in self.recent_timings])
            avg.motion_detection_ms = np.mean([t.motion_detection_ms for t in self.recent_timings])
            avg.color_detection_ms = np.mean([t.color_detection_ms for t in self.recent_timings])
            avg.detection_ms = np.mean([t.detection_ms for t in self.recent_timings])
            avg.fusion_ms = np.mean([t.fusion_ms for t in self.recent_timings])
            avg.render_ms = np.mean([t.render_ms for t in self.recent_timings])
            avg.total_ms = np.mean([t.total_ms for t in self.recent_timings])
            self.average_timings = avg

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for signal emission."""
        result = {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'detection_count': self.detection_count,
            'dropped_frames': self.dropped_frames,
            'processing_time_ms': self.processing_time_ms
        }
        if self.average_timings:
            result['timings'] = self.average_timings.to_dict()
            result['average_timings'] = self.average_timings.to_dict()
        return result


# ============================================================================
# FRAME QUEUE
# ============================================================================

class FrameQueue:
    """
    Thread-safe single-slot frame queue with automatic frame dropping.

    Only stores the most recent frame to ensure low latency. Old frames
    are automatically dropped when new frames arrive.

    This is used for real-time video processing where we always want to
    process the most recent frame, not queue up old frames.
    """

    def __init__(self):
        self.frame: Optional[np.ndarray] = None
        self.timestamp: float = 0.0
        self.lock = Lock()
        self.dropped_count: int = 0

    def put(self, frame: np.ndarray, timestamp: float) -> bool:
        """
        Add frame to queue, dropping old frame if present.

        Args:
            frame: The video frame (will be copied)
            timestamp: Frame timestamp

        Returns:
            True if a frame was dropped, False otherwise
        """
        dropped = False
        with self.lock:
            if self.frame is not None:
                # Drop old frame
                dropped = True
                self.dropped_count += 1
            self.frame = frame.copy()
            self.timestamp = timestamp
        return dropped

    def get(self) -> Tuple[Optional[np.ndarray], float]:
        """
        Get and remove frame from queue.

        Returns:
            Tuple of (frame, timestamp) or (None, 0.0) if empty
        """
        with self.lock:
            frame = self.frame
            timestamp = self.timestamp
            self.frame = None
            self.timestamp = 0.0
        return frame, timestamp

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        with self.lock:
            return self.frame is None

    def get_dropped_count(self) -> int:
        """Get number of dropped frames."""
        with self.lock:
            return self.dropped_count

    def reset_dropped_count(self) -> int:
        """Reset and return dropped frame count."""
        with self.lock:
            count = self.dropped_count
            self.dropped_count = 0
            return count


# ============================================================================
# THREADED CAPTURE WORKER
# ============================================================================

class ThreadedCaptureWorker:
    """
    Background thread worker for capturing frames from video source.

    Runs in a separate thread to avoid blocking the processing pipeline.
    Always captures the latest frame, dropping old ones in the queue.

    Features:
    - Continuous frame capture in background thread
    - Automatic frame dropping for low latency
    - Optional FPS limiting for video files
    - Thread-safe operation
    - Performance statistics

    Expected improvement: 30-200% FPS increase, lower jitter.
    """

    def __init__(self, video_source, frame_queue: FrameQueue, logger: LoggerService,
                 target_fps: Optional[float] = None):
        """
        Initialize threaded capture worker.

        Args:
            video_source: Video source object with read() method (cv2.VideoCapture compatible)
            frame_queue: FrameQueue to put captured frames into
            logger: Logger instance for logging
            target_fps: Optional target FPS for rate limiting (useful for video files)
        """
        self.video_source = video_source
        self.frame_queue = frame_queue
        self.logger = logger
        self.target_fps = target_fps
        self.frame_delay = (1.0 / target_fps) if target_fps and target_fps > 0 else 0.0

        self._running = False
        self._thread: Optional[Thread] = None
        self._lock = Lock()
        self._frames_captured = 0
        self._capture_errors = 0

    def start(self):
        """Start the capture thread."""
        with self._lock:
            if self._running:
                self.logger.warning("Threaded capture already running")
                return

            self._running = True
            self._thread = Thread(target=self._capture_loop, daemon=True, name="CaptureThread")
            self._thread.start()
            self.logger.info("Threaded capture started")

    def stop(self):
        """Stop the capture thread."""
        with self._lock:
            if not self._running:
                return

            self._running = False

        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            self.logger.info(f"Threaded capture stopped (captured {self._frames_captured} frames, {self._capture_errors} errors)")

    def is_running(self) -> bool:
        """Check if capture thread is running."""
        with self._lock:
            return self._running

    def get_stats(self) -> Dict[str, int]:
        """Get capture statistics."""
        return {
            'frames_captured': self._frames_captured,
            'capture_errors': self._capture_errors
        }

    def _capture_loop(self):
        """Main capture loop that runs in background thread."""
        self.logger.info(f"Capture loop starting (FPS limit: {self.target_fps if self.target_fps else 'None'})...")

        last_capture_time = time.time()

        while True:
            # Check if we should stop
            with self._lock:
                if not self._running:
                    break

            try:
                # FPS limiting: wait if needed before next capture
                if self.frame_delay > 0:
                    current_time = time.time()
                    elapsed = current_time - last_capture_time

                    if elapsed < self.frame_delay:
                        sleep_time = self.frame_delay - elapsed
                        time.sleep(sleep_time)

                    last_capture_time = time.time()

                # Capture frame
                ret, frame = self.video_source.read()

                if not ret or frame is None:
                    self._capture_errors += 1
                    # Don't spam errors, just count them
                    if self._capture_errors <= 3:
                        self.logger.warning(f"Failed to capture frame (error #{self._capture_errors})")
                    # Small delay before retry
                    time.sleep(0.001)
                    continue

                # Put frame in queue (will drop old frame if present)
                timestamp = time.time()
                self.frame_queue.put(frame, timestamp)
                self._frames_captured += 1

                # For live sources (no FPS limit), capture as fast as possible
                # The single-slot queue handles backpressure automatically

            except Exception as e:
                self._capture_errors += 1
                self.logger.error(f"Capture loop error: {e}")
                time.sleep(0.01)  # Brief pause on exception

        self.logger.info("Capture loop exiting")


# ============================================================================
# TIMING OVERLAY RENDERER
# ============================================================================

class TimingOverlayRenderer:
    """Renders FPS and timing information on frames."""

    @staticmethod
    def render(frame: np.ndarray, metrics: PerformanceMetrics,
               latest_timings: Optional[StageTimings] = None) -> np.ndarray:
        """
        Render performance overlay on frame.

        Args:
            frame: Input frame to annotate
            metrics: Current performance metrics
            latest_timings: Latest timing measurements (optional)

        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        h, w = frame.shape[:2]

        # Prepare text lines
        lines = []

        # FPS and frame info
        lines.append(f"FPS: {metrics.fps:.1f} | Frames: {metrics.frame_count}")

        if metrics.dropped_frames > 0:
            lines.append(f"Dropped: {metrics.dropped_frames} frames")

        # Latest timings (real-time)
        if latest_timings:
            lines.append(f"Latest: motion={latest_timings.motion_detection_ms:.1f}ms "
                         f"color={latest_timings.color_detection_ms:.1f}ms "
                         f"render={latest_timings.render_ms:.1f}ms")

        # Average timings
        if metrics.average_timings:
            avg = metrics.average_timings
            lines.append(f"Average: motion={avg.motion_detection_ms:.1f}ms "
                         f"color={avg.color_detection_ms:.1f}ms "
                         f"render={avg.render_ms:.1f}ms")
            lines.append(f"Total: {avg.total_ms:.1f}ms/frame "
                         f"(target: 33ms for 30fps)")

        # Detections
        lines.append(f"Detections: {metrics.detection_count}")

        # Render text with background for readability
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        line_height = 20
        padding = 5

        y_offset = 20
        for line in lines:
            # Get text size for background
            (text_width, text_height), _ = cv2.getTextSize(line, font, font_scale, font_thickness)

            # Draw background rectangle
            cv2.rectangle(annotated,
                          (5, y_offset - text_height - padding),
                          (5 + text_width + padding * 2, y_offset + padding),
                          (0, 0, 0), -1)

            # Draw text
            cv2.putText(annotated, line, (10, y_offset),
                        font, font_scale, (0, 255, 0), font_thickness, cv2.LINE_AA)

            y_offset += line_height

        return annotated
