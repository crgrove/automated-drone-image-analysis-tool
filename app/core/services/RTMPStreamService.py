"""
RTMPStreamService.py - Real-time RTMP stream processing service for ADIAT

Handles RTMP/HLS video stream input with optimized performance for real-time
color detection applications. Designed for <250ms latency processing.
"""

# Set environment variable to avoid numpy compatibility issues - MUST be first
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
# Also set these for better compatibility
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')

import cv2
import numpy as np
import threading
import time
from queue import Queue, Empty
from typing import Optional, Tuple, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from core.services.LoggerService import LoggerService


class StreamType(Enum):
    RTMP = "rtmp"
    HLS = "hls"
    FILE = "file"
    HDMI_CAPTURE = "hdmi_capture"


@dataclass
class StreamConfig:
    """Configuration for stream connection."""
    url: str
    stream_type: StreamType = StreamType.RTMP
    reconnect_attempts: int = 5
    buffer_size: int = 1  # Minimize buffering for real-time
    fps_limit: int = 30
    resolution_limit: Tuple[int, int] = (1920, 1080)


@dataclass
class FrameData:
    """Container for frame and metadata."""
    frame: np.ndarray
    timestamp: float
    frame_number: int
    fps: float


class RTMPStreamService(QThread):
    """
    Real-time RTMP stream processing service optimized for low-latency applications.

    Features:
    - Sub-250ms latency processing pipeline
    - Automatic reconnection with exponential backoff
    - Frame rate adaptation and quality scaling
    - Thread-safe frame delivery
    - GPU acceleration when available
    """

    # Signals for Qt integration
    frameReady = pyqtSignal(np.ndarray, float, int)  # frame, timestamp, frame_number
    connectionStatusChanged = pyqtSignal(bool, str)  # connected, status_message
    streamStatsChanged = pyqtSignal(dict)  # fps, resolution, bitrate, etc.
    errorOccurred = pyqtSignal(str)  # error_message
    videoPositionChanged = pyqtSignal(float, float)  # current_time, total_time

    def __init__(self, config: StreamConfig):
        super().__init__()
        self.config = config
        self.logger = LoggerService()

        # Stream state
        self._cap = None
        self._connected = False
        self._should_stop = False
        self._frame_number = 0
        self._last_frame_time = 0

        # Performance tracking
        self._fps_counter = 0
        self._fps_start_time = time.time()
        self._current_fps = 0

        # Video file playback control
        self._is_file = (config.stream_type == StreamType.FILE)
        self._is_playing = True
        self._total_frames = 0
        self._current_frame_pos = 0
        self._video_fps = 30
        self._total_duration = 0
        self._playback_lock = threading.Lock()

        # Seek request mechanism for thread safety
        self._seek_requested = False
        self._seek_target_frame = 0

        # Frame processing
        self._frame_queue = Queue(maxsize=3)  # Small buffer for real-time
        self._processing_thread = None

        # Reconnection logic
        self._current_reconnect_delay = 1.0
        self._max_reconnect_delay = 30.0

    def run(self):
        """Main thread loop for stream processing."""
        self.logger.info(f"Starting RTMP stream service: {self.config.url}")

        reconnect_attempts = 0

        while not self._should_stop and reconnect_attempts < self.config.reconnect_attempts:
            try:
                if self._connect_to_stream():
                    self._connected = True
                    self.connectionStatusChanged.emit(True, "Connected")
                    reconnect_attempts = 0  # Reset on successful connection
                    self._current_reconnect_delay = 1.0

                    # Start processing loop
                    self._process_stream()

                else:
                    reconnect_attempts += 1
                    if reconnect_attempts < self.config.reconnect_attempts:
                        self.connectionStatusChanged.emit(False, f"Reconnecting... (attempt {reconnect_attempts})")
                        time.sleep(self._current_reconnect_delay)
                        self._current_reconnect_delay = min(self._current_reconnect_delay * 2, self._max_reconnect_delay)

            except Exception as e:
                self.logger.error(f"Stream processing error: {e}")
                self.errorOccurred.emit(str(e))
                break

        if reconnect_attempts >= self.config.reconnect_attempts:
            self.errorOccurred.emit("Maximum reconnection attempts exceeded")

        self._cleanup()
        self.connectionStatusChanged.emit(False, "Disconnected")

    def _connect_to_stream(self) -> bool:
        """Establish connection to the video stream."""
        try:
            self.logger.info(f"Connecting to stream: {self.config.url}")

            # Configure OpenCV for different stream types
            if self.config.stream_type == StreamType.HDMI_CAPTURE:
                # Handle HDMI capture device
                try:
                    device_index = int(self.config.url)
                    self.logger.info(f"Connecting to HDMI capture device {device_index}")
                    # Try DirectShow backend instead of MSMF for better performance
                    self._cap = cv2.VideoCapture(device_index, cv2.CAP_DSHOW)
                    print(f"HDMI: Using DirectShow backend for device {device_index}")
                except ValueError:
                    self.logger.error(f"Invalid device index: {self.config.url}")
                    return False
            elif self.config.stream_type == StreamType.RTMP:
                # Handle RTMP streams with FFMPEG backend for better compatibility
                self.logger.info(f"Connecting to RTMP stream: {self.config.url}")
                self._cap = cv2.VideoCapture(self.config.url, cv2.CAP_FFMPEG)
                # Set buffer size for low latency
                self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
            else:
                # Handle HLS streams and files
                self._cap = cv2.VideoCapture(self.config.url)

            if not self._cap.isOpened():
                self.logger.error("Failed to open stream")
                return False

            # Optimize for real-time processing
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, self.config.buffer_size)
            self._cap.set(cv2.CAP_PROP_FPS, self.config.fps_limit)

            # Additional settings for HDMI capture devices
            if self.config.stream_type == StreamType.HDMI_CAPTURE:
                # Optimize HDMI capture for best performance (720p @ ~25fps)
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
                self._cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
                self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self._cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                self.logger.info("HDMI capture optimized for 720p @ 25fps performance")

            # Test frame read
            ret, frame = self._cap.read()
            if not ret or frame is None:
                self.logger.error("Failed to read initial frame")
                return False

            # Log stream properties
            fps = self._cap.get(cv2.CAP_PROP_FPS)
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Get file-specific properties if this is a video file
            if self._is_file:
                self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self._video_fps = fps if fps > 0 else 30
                self._total_duration = self._total_frames / self._video_fps if self._video_fps > 0 else 0
                self.logger.info(f"Video file connected: {width}x{height} @ {fps}fps, "f"{self._total_frames} frames, {self._total_duration:.1f}s duration")
            else:
                self.logger.info(f"Stream connected: {width}x{height} @ {fps}fps")

            # Emit initial stats
            stats = {
                'fps': fps,
                'resolution': (width, height),
                'connected_time': time.time()
            }

            # Add file-specific stats
            if self._is_file:
                stats.update({
                    'is_file': True,
                    'total_frames': self._total_frames,
                    'total_duration': self._total_duration,
                    'current_position': 0
                })
                # Emit initial position
                self.videoPositionChanged.emit(0, self._total_duration)

            self.streamStatsChanged.emit(stats)

            return True

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            if self._cap:
                self._cap.release()
                self._cap = None
            return False

    def _process_stream(self):
        """Main stream processing loop optimized for low latency."""
        frame_interval = 1.0 / self.config.fps_limit
        last_process_time = 0
        consecutive_errors = 0
        max_consecutive_errors = 5

        while not self._should_stop and self._connected and self._cap and self._cap.isOpened():
            try:
                current_time = time.time()

                # Handle pause state and seek requests for video files
                if self._is_file:
                    with self._playback_lock:
                        # Handle seek requests first (thread-safe)
                        if self._seek_requested and self._cap:
                            try:
                                self._cap.set(cv2.CAP_PROP_POS_FRAMES, self._seek_target_frame)
                                self._current_frame_pos = self._seek_target_frame
                                self._seek_requested = False
                                self.logger.info(f"Seek completed to frame {self._seek_target_frame}")
                            except Exception as e:
                                self.logger.error(f"Seek execution error: {e}")
                                self._seek_requested = False

                        # Handle pause state
                        if not self._is_playing:
                            time.sleep(0.1)  # Sleep while paused
                            continue

                # Frame rate limiting (skip for HDMI capture to test maximum throughput)
                if self.config.stream_type != StreamType.HDMI_CAPTURE:
                    # For files, respect the video's original FPS
                    target_interval = frame_interval
                    if self._is_file and self._video_fps > 0:
                        target_interval = 1.0 / self._video_fps

                    if current_time - last_process_time < target_interval:
                        time.sleep(0.001)  # Small sleep to prevent excessive CPU usage
                        continue

                # Read frame with timeout handling
                ret, frame = self._cap.read()

                if not ret or frame is None:
                    consecutive_errors += 1
                    if consecutive_errors >= max_consecutive_errors:
                        self.logger.error(f"Failed to read {consecutive_errors} consecutive frames, stopping")
                        break
                    else:
                        self.logger.warning(f"Failed to read frame ({consecutive_errors}/{max_consecutive_errors})")
                        time.sleep(0.1)  # Small delay before retry
                        continue

                # Reset error counter on successful frame read
                consecutive_errors = 0

                # Validate frame
                if frame.size == 0:
                    self.logger.warning("Received empty frame")
                    continue

                # Performance optimization: resize if needed
                try:
                    height, width = frame.shape[:2]
                    if width > self.config.resolution_limit[0] or height > self.config.resolution_limit[1]:
                        scale_factor = min(
                            self.config.resolution_limit[0] / width,
                            self.config.resolution_limit[1] / height
                        )
                        new_width = int(width * scale_factor)
                        new_height = int(height * scale_factor)
                        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                except Exception as e:
                    self.logger.error(f"Error resizing frame: {e}")
                    continue

                # Update performance metrics
                self._update_fps_counter()

                # Update video position for files
                if self._is_file:
                    self._current_frame_pos = int(self._cap.get(cv2.CAP_PROP_POS_FRAMES))
                    current_time_in_video = self._current_frame_pos / self._video_fps if self._video_fps > 0 else 0
                    self.videoPositionChanged.emit(current_time_in_video, self._total_duration)

                # Make a copy of the frame to prevent memory issues
                try:
                    frame_copy = frame.copy()
                    # Emit frame for processing
                    self.frameReady.emit(frame_copy, current_time, self._frame_number)
                    self._frame_number += 1
                    last_process_time = current_time
                except Exception as e:
                    self.logger.error(f"Error emitting frame: {e}")
                    continue

            except Exception as e:
                self.logger.error(f"Frame processing error: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    self.logger.error("Too many consecutive errors, stopping stream")
                    break
                time.sleep(0.1)  # Small delay before retry

    def _update_fps_counter(self):
        """Update FPS tracking."""
        self._fps_counter += 1
        current_time = time.time()

        if current_time - self._fps_start_time >= 1.0:
            self._current_fps = self._fps_counter / (current_time - self._fps_start_time)
            self._fps_counter = 0
            self._fps_start_time = current_time

            # Emit updated stats
            if self._cap:
                width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                self.streamStatsChanged.emit({
                    'fps': self._current_fps,
                    'resolution': (width, height),
                    'frame_number': self._frame_number,
                    'timestamp': current_time
                })

    def stop(self):
        """Stop the stream processing."""
        self.logger.info("Stopping RTMP stream service")
        self._should_stop = True
        self._connected = False  # Immediately mark as disconnected to break loops

    def play_pause(self):
        """Toggle play/pause state for video files."""
        if not self._is_file:
            return False

        with self._playback_lock:
            self._is_playing = not self._is_playing
            self.logger.info(f"Video {'playing' if self._is_playing else 'paused'}")
            return self._is_playing

    def seek_to_time(self, time_seconds: float):
        """Seek to specific time in video file."""
        if not self._is_file or not self._cap:
            return False

        try:
            with self._playback_lock:
                # Calculate frame position
                target_frame = int(time_seconds * self._video_fps)
                target_frame = max(0, min(target_frame, self._total_frames - 1))

                # Set seek request flag - the capture thread will handle it safely
                self._seek_requested = True
                self._seek_target_frame = target_frame

                # Update position immediately for UI feedback
                actual_time = target_frame / self._video_fps if self._video_fps > 0 else 0
                self.videoPositionChanged.emit(actual_time, self._total_duration)

                self.logger.info(f"Seek requested to {actual_time:.1f}s (frame {target_frame})")
                return True

        except Exception as e:
            self.logger.error(f"Seek error: {e}")
            return False

    def seek_relative(self, seconds_delta: float):
        """Seek relative to current position."""
        if not self._is_file:
            return False

        current_time = self._current_frame_pos / self._video_fps if self._video_fps > 0 else 0
        new_time = current_time + seconds_delta
        return self.seek_to_time(new_time)

    def seek_to_beginning(self):
        """Seek to beginning of video."""
        return self.seek_to_time(0)

    def seek_to_end(self):
        """Seek to end of video."""
        if not self._is_file:
            return False
        return self.seek_to_time(self._total_duration - 1)

    def is_file_playback(self) -> bool:
        """Check if this is file playback (not live stream)."""
        return self._is_file

    def is_playing(self) -> bool:
        """Check if video is currently playing."""
        return self._is_playing

    def get_playback_info(self) -> dict:
        """Get current playback information for files."""
        if not self._is_file:
            return {}

        current_time = self._current_frame_pos / self._video_fps if self._video_fps > 0 else 0
        return {
            'is_file': True,
            'is_playing': self._is_playing,
            'current_time': current_time,
            'total_duration': self._total_duration,
            'current_frame': self._current_frame_pos,
            'total_frames': self._total_frames,
            'fps': self._video_fps
        }

    def _cleanup(self):
        """Clean up resources."""
        try:
            # Clear any pending seek requests
            self._seek_requested = False

            if self._cap:
                self._cap.release()
                self._cap = None
        except Exception as e:
            self.logger.error(f"Error releasing video capture: {e}")
        finally:
            self._connected = False

    def is_connected(self) -> bool:
        """Check if stream is currently connected."""
        return self._connected and self._cap and self._cap.isOpened()

    def get_stream_info(self) -> Dict[str, Any]:
        """Get current stream information."""
        if not self._cap:
            return {}

        return {
            'url': self.config.url,
            'type': self.config.stream_type.value,
            'fps': self._current_fps,
            'resolution': (
                int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ),
            'frame_count': self._frame_number,
            'connected': self._connected
        }


class StreamManager(QObject):
    """
    High-level manager for RTMP stream operations.
    Provides simplified interface for ADIAT integration.
    """

    frameReceived = pyqtSignal(np.ndarray, float)  # frame, timestamp
    connectionChanged = pyqtSignal(bool, str)  # connected, message
    statsUpdated = pyqtSignal(dict)  # stream statistics
    videoPositionChanged = pyqtSignal(float, float)  # current_time, total_time

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()
        self._service = None
        self._current_config = None

    def connect_to_stream(self, url: str, stream_type: StreamType = StreamType.RTMP) -> bool:
        """
        Connect to a video stream.

        Args:
            url: Stream URL (RTMP, HLS, or file path)
            stream_type: Type of stream

        Returns:
            bool: True if connection initiated successfully
        """
        try:
            # Stop existing service
            self.disconnect_stream()

            # Create new configuration
            # Gradually increase FPS for HDMI capture testing
            fps_limit = 35 if stream_type == StreamType.HDMI_CAPTURE else 30

            self._current_config = StreamConfig(
                url=url,
                stream_type=stream_type,
                reconnect_attempts=5,
                buffer_size=1,  # Minimal buffering
                fps_limit=fps_limit,
                resolution_limit=(1920, 1080)
            )

            # Create and start service
            self._service = RTMPStreamService(self._current_config)

            # Connect signals
            self._service.frameReady.connect(self._on_frame_ready)
            self._service.connectionStatusChanged.connect(self.connectionChanged)
            self._service.streamStatsChanged.connect(self.statsUpdated)
            self._service.videoPositionChanged.connect(self.videoPositionChanged)
            self._service.errorOccurred.connect(self._on_error)

            # Start service
            self._service.start()

            self.logger.info(f"Stream connection initiated: {url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to stream: {e}")
            return False

    def disconnect_stream(self):
        """Disconnect from current stream."""
        if self._service:
            # Stop the service first
            self._service.stop()

            # Immediately quit the thread's event loop
            self._service.quit()

            # Give the thread time to finish
            if not self._service.wait(3000):  # Wait up to 3 seconds
                self.logger.warning("Stream service didn't stop gracefully, terminating...")
                self._service.terminate()
                if not self._service.wait(1000):
                    self.logger.error("Stream service still running after terminate")

            # Now disconnect signals after the thread has stopped
            try:
                # Disconnect signals after stopping to ensure we get final status updates
                try:
                    self._service.frameReady.disconnect()
                except TypeError:
                    pass  # Already disconnected
                try:
                    self._service.connectionStatusChanged.disconnect()
                except TypeError:
                    pass
                try:
                    self._service.streamStatsChanged.disconnect()
                except TypeError:
                    pass
                try:
                    self._service.videoPositionChanged.disconnect()
                except TypeError:
                    pass
                try:
                    self._service.errorOccurred.disconnect()
                except TypeError:
                    pass
            except Exception as e:
                self.logger.debug(f"Error disconnecting signals: {e}")

            # Delete the service to ensure proper cleanup
            self._service.deleteLater()
            self._service = None

        # Always emit disconnection status to ensure UI updates
        self.connectionChanged.emit(False, "Disconnected")

    def is_connected(self) -> bool:
        """Check if currently connected to a stream."""
        return self._service and self._service.is_connected()

    def get_stream_info(self) -> Dict[str, Any]:
        """Get current stream information."""
        if self._service:
            return self._service.get_stream_info()
        return {}

    def _on_frame_ready(self, frame: np.ndarray, timestamp: float, frame_number: int):
        """Handle incoming frame from service."""
        self.frameReceived.emit(frame, timestamp)

    def _on_error(self, error_message: str):
        """Handle service errors."""
        self.logger.error(f"Stream error: {error_message}")
        self.connectionChanged.emit(False, f"Error: {error_message}")

    # Video playback control methods
    def play_pause(self):
        """Toggle play/pause for video files."""
        if self._service:
            return self._service.play_pause()
        return False

    def seek_to_time(self, time_seconds: float):
        """Seek to specific time in video."""
        if self._service:
            return self._service.seek_to_time(time_seconds)
        return False

    def seek_relative(self, seconds_delta: float):
        """Seek relative to current position."""
        if self._service:
            return self._service.seek_relative(seconds_delta)
        return False

    def seek_to_beginning(self):
        """Seek to beginning of video."""
        if self._service:
            return self._service.seek_to_beginning()
        return False

    def seek_to_end(self):
        """Seek to end of video."""
        if self._service:
            return self._service.seek_to_end()
        return False

    def is_file_playback(self) -> bool:
        """Check if current stream is a file."""
        if self._service:
            return self._service.is_file_playback()
        return False

    def is_playing(self) -> bool:
        """Check if video is playing."""
        if self._service:
            return self._service.is_playing()
        return True

    def get_playback_info(self) -> dict:
        """Get playback information."""
        if self._service:
            return self._service.get_playback_info()
        return {}
