"""
VideoRecordingService.py - High-performance video recording for RTMP streams

Provides efficient MP4 recording of live streams with minimal impact on
real-time processing performance. Supports hardware encoding when available.
"""

# Set environment variable to avoid numpy._core issues - MUST be first
import os  # noqa: E402
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'
import cv2
import numpy as np
import time
import threading
from queue import Queue, Empty
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from core.services.LoggerService import LoggerService


@dataclass
class RecordingConfig:
    """Configuration for video recording."""
    output_dir: str
    filename_prefix: str = "rtmp_recording"
    fps: int = 30
    quality: int = 23  # H.264 CRF value (lower = better quality)
    codec: str = "mp4v"  # Codec fourcc
    segment_duration: int = 1800  # 30 minutes per segment
    max_segments: int = 100  # Maximum number of segments to keep
    use_hardware_encoding: bool = True


class VideoRecorder(QThread):
    """
    High-performance video recorder for real-time streams.

    Features:
    - Hardware-accelerated encoding when available
    - Automatic file segmentation for long recordings
    - Minimal impact on real-time processing
    - Thread-safe frame queuing
    - Disk space management
    """

    # Signals
    recordingStarted = pyqtSignal(str)  # output_path
    recordingStopped = pyqtSignal(str, float)  # output_path, duration
    segmentCompleted = pyqtSignal(str, str)  # old_path, new_path
    errorOccurred = pyqtSignal(str)  # error_message
    statsUpdated = pyqtSignal(dict)  # recording statistics

    def __init__(self, config: RecordingConfig):
        super().__init__()
        self.config = config
        self.logger = LoggerService()

        # Recording state
        self._is_recording = False
        self._should_stop = False
        self._current_writer = None
        self._current_output_path = None
        self._segment_start_time = None
        self._frame_count = 0
        self._total_frames = 0

        # Frame queue for buffering - reduced for better performance
        self._frame_queue = Queue(maxsize=30)  # ~1 second at 30fps
        self._recording_thread = None

        # Performance tracking
        self._fps_counter = 0
        self._fps_start_time = time.time()
        self._recording_fps = 0

        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)

    def start_recording(self, resolution: Tuple[int, int]) -> bool:
        """
        Start video recording.

        Args:
            resolution: Video resolution (width, height)

        Returns:
            bool: True if recording started successfully
        """
        if self._is_recording:
            self.logger.warning("Recording already in progress")
            return False

        try:
            self._resolution = resolution
            self._should_stop = False
            self._frame_count = 0
            self._segment_start_time = time.time()

            # Generate output filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config.filename_prefix}_{timestamp}.mp4"
            self._current_output_path = os.path.join(self.config.output_dir, filename)

            # Initialize video writer
            if not self._init_video_writer():
                return False

            self._is_recording = True
            self.start()  # Start thread

            self.recordingStarted.emit(self._current_output_path)
            self.logger.info(f"Recording started: {self._current_output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            self.errorOccurred.emit(f"Failed to start recording: {str(e)}")
            return False

    def stop_recording(self):
        """Stop video recording."""
        if not self._is_recording:
            return

        self.logger.info("Stopping video recording")
        self._should_stop = True

        # Wait for thread to finish
        if self.isRunning():
            self.wait(5000)  # Wait up to 5 seconds

    def add_frame(self, frame: np.ndarray, timestamp: float) -> bool:
        """
        Add frame to recording queue.

        Args:
            frame: BGR frame to record
            timestamp: Frame timestamp

        Returns:
            bool: True if frame was queued successfully
        """
        if not self._is_recording:
            return False

        try:
            # Non-blocking queue insertion
            self._frame_queue.put_nowait((frame.copy(), timestamp))
            return True
        except Exception:
            # Queue full - drop frame
            return False

    def run(self):
        """Main recording thread loop."""
        self.logger.info("Recording thread started")

        while not self._should_stop:
            try:
                # Get frame from queue with timeout
                try:
                    frame, timestamp = self._frame_queue.get(timeout=1.0)
                except Empty:
                    continue

                # Write frame
                if self._current_writer and frame is not None:
                    # Ensure frame is correct size
                    if frame.shape[:2][::-1] != self._resolution:
                        frame = cv2.resize(frame, self._resolution)

                    self._current_writer.write(frame)
                    self._frame_count += 1
                    self._total_frames += 1

                    # Update performance stats
                    self._update_stats()

                    # Check for segment rotation
                    if self._should_rotate_segment():
                        self._rotate_segment()

            except Exception as e:
                self.logger.error(f"Recording error: {e}")
                self.errorOccurred.emit(str(e))
                break

        # Cleanup
        self._cleanup_recording()
        self.logger.info("Recording thread stopped")

    def _init_video_writer(self) -> bool:
        """Initialize video writer with optimal settings."""
        try:
            width, height = self._resolution

            # Try hardware encoding first if enabled
            if self.config.use_hardware_encoding:
                self.logger.info("Attempting hardware encoding...")
                for codec_info in self._get_hardware_codecs():
                    try:
                        fourcc = cv2.VideoWriter_fourcc(*codec_info['fourcc'])
                        writer = cv2.VideoWriter(
                            self._current_output_path,
                            fourcc,
                            self.config.fps,
                            (width, height)
                        )

                        if writer.isOpened():
                            self._current_writer = writer
                            self.logger.info(f"✅ Hardware encoding enabled: {codec_info['name']} ({codec_info['fourcc']})")
                            return True
                        else:
                            writer.release()
                            self.logger.debug(f"❌ Hardware codec failed: {codec_info['name']}")
                    except Exception as e:
                        self.logger.debug(f"❌ Hardware codec error {codec_info['name']}: {e}")

                self.logger.warning("🔄 Hardware encoding failed, falling back to software encoding")

            # Fallback to software encoding
            self.logger.info("Using software encoding...")
            fourcc = cv2.VideoWriter_fourcc(*self.config.codec)
            self._current_writer = cv2.VideoWriter(
                self._current_output_path,
                fourcc,
                self.config.fps,
                (width, height)
            )

            if self._current_writer.isOpened():
                self.logger.info(f"Using software codec: {self.config.codec}")
                return True
            else:
                self.logger.error("Failed to initialize video writer")
                return False

        except Exception as e:
            self.logger.error(f"Error initializing video writer: {e}")
            return False

    def _get_hardware_codecs(self) -> list:
        """Get available hardware encoding codecs."""
        # Order by preference - optimized for performance
        codecs = [
            # NVIDIA hardware encoding (best performance)
            {'name': 'H.264 NVENC', 'fourcc': 'h264'},  # lowercase for better compatibility
            {'name': 'H.264 NVENC Alt', 'fourcc': 'H264'},
            {'name': 'H.264 NVENC CUDA', 'fourcc': 'avc1'},

            # Intel Quick Sync Video
            {'name': 'Intel QSV H.264', 'fourcc': 'H264'},
            {'name': 'Intel QSV H.264 Alt', 'fourcc': 'h264'},

            # AMD VCE
            {'name': 'AMD VCE H.264', 'fourcc': 'H264'},
            {'name': 'AMD VCE H.264 Alt', 'fourcc': 'h264'},

            # H.265 (slower but better compression)
            {'name': 'H.265 NVENC', 'fourcc': 'HEVC'},
            {'name': 'H.265 Alt', 'fourcc': 'h265'},
        ]
        return codecs

    def _should_rotate_segment(self) -> bool:
        """Check if segment should be rotated."""
        if not self._segment_start_time:
            return False

        elapsed = time.time() - self._segment_start_time
        return elapsed >= self.config.segment_duration

    def _rotate_segment(self):
        """Rotate to new recording segment."""
        try:
            old_path = self._current_output_path

            # Close current writer
            if self._current_writer:
                self._current_writer.release()
                self._current_writer = None

            # Generate new filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config.filename_prefix}_{timestamp}.mp4"
            self._current_output_path = os.path.join(self.config.output_dir, filename)

            # Initialize new writer
            if self._init_video_writer():
                self._segment_start_time = time.time()
                self._frame_count = 0

                self.segmentCompleted.emit(old_path, self._current_output_path)
                self.logger.info(f"Rotated to new segment: {self._current_output_path}")

                # Cleanup old segments if needed
                self._cleanup_old_segments()
            else:
                self.errorOccurred.emit("Failed to rotate recording segment")

        except Exception as e:
            self.logger.error(f"Error rotating segment: {e}")
            self.errorOccurred.emit(f"Segment rotation error: {str(e)}")

    def _cleanup_old_segments(self):
        """Remove old recording segments to manage disk space."""
        try:
            # Get all recording files
            pattern = f"{self.config.filename_prefix}_*.mp4"
            recording_files = list(Path(self.config.output_dir).glob(pattern))

            # Sort by creation time (oldest first)
            recording_files.sort(key=lambda f: f.stat().st_ctime)

            # Remove excess files
            while len(recording_files) > self.config.max_segments:
                old_file = recording_files.pop(0)
                try:
                    old_file.unlink()
                    self.logger.info(f"Removed old recording: {old_file}")
                except Exception as e:
                    self.logger.error(f"Error removing old recording {old_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error cleaning up old segments: {e}")

    def _update_stats(self):
        """Update recording statistics."""
        self._fps_counter += 1
        current_time = time.time()

        # Update FPS every second
        if current_time - self._fps_start_time >= 1.0:
            self._recording_fps = self._fps_counter / (current_time - self._fps_start_time)
            self._fps_counter = 0
            self._fps_start_time = current_time

            # Calculate recording duration
            duration = current_time - self._segment_start_time if self._segment_start_time else 0

            # Emit stats
            stats = {
                'recording_fps': self._recording_fps,
                'frame_count': self._frame_count,
                'total_frames': self._total_frames,
                'segment_duration': duration,
                'output_path': self._current_output_path,
                'queue_size': self._frame_queue.qsize()
            }

            self.statsUpdated.emit(stats)

    def _cleanup_recording(self):
        """Clean up recording resources."""
        self._is_recording = False

        if self._current_writer:
            self._current_writer.release()
            self._current_writer = None

        # Calculate final duration
        duration = 0
        if self._segment_start_time:
            duration = time.time() - self._segment_start_time

        if self._current_output_path:
            self.recordingStopped.emit(self._current_output_path, duration)

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording

    def get_recording_info(self) -> Dict[str, Any]:
        """Get current recording information."""
        if not self._is_recording:
            return {}

        duration = 0
        if self._segment_start_time:
            duration = time.time() - self._segment_start_time

        return {
            'output_path': self._current_output_path,
            'duration': duration,
            'frame_count': self._frame_count,
            'total_frames': self._total_frames,
            'fps': self._recording_fps,
            'queue_size': self._frame_queue.qsize(),
            'resolution': self._resolution
        }


class RecordingManager(QObject):
    """
    High-level manager for video recording operations.
    Provides simplified interface for ADIAT integration.
    """

    recordingStateChanged = pyqtSignal(bool, str)  # is_recording, path_or_message
    recordingStats = pyqtSignal(dict)  # recording statistics

    def __init__(self, output_dir: str = "./recordings"):
        super().__init__()
        self.logger = LoggerService()
        self._recorder = None
        self._config = RecordingConfig(output_dir=output_dir)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def start_recording(self, resolution: Tuple[int, int], filename_prefix: str = "rtmp_recording") -> bool:
        """
        Start video recording.

        Args:
            resolution: Video resolution (width, height)
            filename_prefix: Prefix for recording files

        Returns:
            bool: True if recording started successfully
        """
        if self._recorder and self._recorder.is_recording():
            self.logger.warning("Recording already in progress")
            return False

        try:
            # Update config
            self._config.filename_prefix = filename_prefix

            # Create new recorder
            self._recorder = VideoRecorder(self._config)

            # Connect signals
            self._recorder.recordingStarted.connect(self._on_recording_started)
            self._recorder.recordingStopped.connect(self._on_recording_stopped)
            self._recorder.segmentCompleted.connect(self._on_segment_completed)
            self._recorder.errorOccurred.connect(self._on_recording_error)
            self._recorder.statsUpdated.connect(self.recordingStats)

            # Start recording
            success = self._recorder.start_recording(resolution)
            if success:
                self.logger.info(f"Recording started with resolution {resolution}")

            return success

        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            self.recordingStateChanged.emit(False, f"Error: {str(e)}")
            return False

    def stop_recording(self):
        """Stop current recording."""
        if self._recorder:
            self._recorder.stop_recording()

    def add_frame(self, frame: np.ndarray, timestamp: float = None) -> bool:
        """
        Add frame to recording.

        Args:
            frame: BGR frame to record
            timestamp: Frame timestamp (uses current time if None)

        Returns:
            bool: True if frame was added successfully
        """
        if not self._recorder or not self._recorder.is_recording():
            return False

        if timestamp is None:
            timestamp = time.time()

        return self._recorder.add_frame(frame, timestamp)

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recorder and self._recorder.is_recording()

    def get_recording_info(self) -> Dict[str, Any]:
        """Get current recording information."""
        if self._recorder:
            return self._recorder.get_recording_info()
        return {}

    def configure(self, **kwargs):
        """
        Configure recording parameters.

        Supported parameters:
        - output_dir: Output directory path
        - fps: Recording frame rate
        - quality: Video quality (H.264 CRF value)
        - segment_duration: Segment duration in seconds
        - use_hardware_encoding: Enable hardware encoding
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                self.logger.info(f"Recording config updated: {key} = {value}")

    def _on_recording_started(self, output_path: str):
        """Handle recording started."""
        self.recordingStateChanged.emit(True, output_path)

    def _on_recording_stopped(self, output_path: str, duration: float):
        """Handle recording stopped."""
        self.recordingStateChanged.emit(False, f"Completed: {duration:.1f}s")
        self.logger.info(f"Recording completed: {output_path} ({duration:.1f}s)")

    def _on_segment_completed(self, old_path: str, new_path: str):
        """Handle segment rotation."""
        self.logger.info(f"Recording segment rotated: {new_path}")

    def _on_recording_error(self, error_message: str):
        """Handle recording error."""
        self.recordingStateChanged.emit(False, f"Error: {error_message}")
        self.logger.error(f"Recording error: {error_message}")
