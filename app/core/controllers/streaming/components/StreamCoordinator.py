"""
StreamCoordinator - Manages stream connection, recording, and frame flow.

This component handles all the plumbing for streaming detection:
- Stream connection/disconnection
- Recording start/stop
- Frame queue management
- Coordinate frame flow from stream to algorithm to display
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional, Callable
import numpy as np

from core.services.LoggerService import LoggerService
from core.services.streaming.RTMPStreamService import StreamManager, StreamType
from core.services.streaming.VideoRecordingService import RecordingManager, RecordingConfig


class StreamCoordinator(QObject):
    """
    Coordinates streaming, recording, and frame processing.

    This class manages the lifecycle of a streaming session including:
    - Connecting/disconnecting from streams
    - Starting/stopping recording
    - Routing frames from stream to algorithm
    - Coordinating frame processing flow
    """

    # Signals
    connectionChanged = Signal(bool, str)  # (connected, message)
    frameReceived = Signal(np.ndarray, float)  # (frame, timestamp)
    recordingStateChanged = Signal(bool, str)  # (recording, path)
    streamInfoUpdated = Signal(dict)  # Stream info (fps, resolution, etc.)
    errorOccurred = Signal(str)  # Error message

    def __init__(self, logger: Optional[LoggerService] = None):
        super().__init__()

        self.logger = logger or LoggerService()

        # Stream management
        self.stream_manager: Optional[StreamManager] = None
        self.is_connected = False
        self.current_stream_url = ""
        self.current_stream_type: Optional[StreamType] = None

        # Recording management
        self.recording_manager: Optional[RecordingManager] = None
        self.is_recording = False
        self.current_recording_path = ""

        # Stream info
        self.stream_info = {
            'fps': 0.0,
            'resolution': (0, 0),
            'latency': 0.0,
            'dropped_frames': 0
        }

    def connect_stream(self, url: str, stream_type: StreamType) -> bool:
        """
        Connect to a stream.

        Args:
            url: Stream URL or file path
            stream_type: Type of stream (RTMP, HLS, File, HDMI) - can be StreamType enum or string

        Returns:
            True if connection initiated successfully
        """
        try:
            # Disconnect existing stream if any
            if self.stream_manager:
                self.disconnect_stream()

            # Handle both enum and string types for stream_type
            if isinstance(stream_type, str):
                # Convert string to enum
                stream_type_map = {
                    "file": StreamType.FILE,
                    "hdmi capture": StreamType.HDMI_CAPTURE,
                    "rtmp stream": StreamType.RTMP,
                    "rtmp": StreamType.RTMP,
                    "hls": StreamType.HLS
                }
                stream_type = stream_type_map.get(stream_type.lower(), StreamType.FILE)

            # self.logger.info(f"Connecting to {stream_type.value} stream: {url}")

            # Create new stream manager
            self.stream_manager = StreamManager()

            # Connect signals
            self.stream_manager.frameReceived.connect(self._on_frame_ready)
            self.stream_manager.connectionChanged.connect(self._on_connection_status_changed)
            # StreamManager provides stats and video position updates
            if hasattr(self.stream_manager, "statsUpdated"):
                self.stream_manager.statsUpdated.connect(self._on_stream_stats_updated)
            if hasattr(self.stream_manager, "videoPositionChanged"):
                self.stream_manager.videoPositionChanged.connect(self._on_video_position_changed)

            # Connect to stream
            if self.stream_manager.connect_to_stream(url, stream_type):
                self.current_stream_url = url
                self.current_stream_type = stream_type
                # self.logger.info("Stream connection initiated")
                return True
            else:
                self.logger.error("Failed to start stream")
                self.errorOccurred.emit("Failed to start stream")
                return False

        except Exception as e:
            error_msg = f"Error connecting to stream: {str(e)}"
            self.logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
            return False

    def disconnect_stream(self):
        """Disconnect from current stream."""
        if self.stream_manager:
            # self.logger.info("Disconnecting stream")

            # Stop recording if active
            if self.is_recording:
                self.stop_recording()

            # Disconnect signals
            try:
                self.stream_manager.frameReceived.disconnect(self._on_frame_ready)
                self.stream_manager.connectionChanged.disconnect(self._on_connection_status_changed)
                if hasattr(self.stream_manager, "statsUpdated"):
                    try:
                        self.stream_manager.statsUpdated.disconnect(self._on_stream_stats_updated)
                    except TypeError:
                        pass
                if hasattr(self.stream_manager, "videoPositionChanged"):
                    try:
                        self.stream_manager.videoPositionChanged.disconnect(self._on_video_position_changed)
                    except TypeError:
                        pass
            except Exception:
                pass

            # Disconnect stream
            self.stream_manager.disconnect_stream()
            self.stream_manager = None

            self.is_connected = False
            self.current_stream_url = ""
            self.current_stream_type = None

            self.connectionChanged.emit(False, "Disconnected")

    def start_recording(self, output_directory: str, metadata: Optional[dict] = None) -> bool:
        """
        Start recording the stream.

        Args:
            output_directory: Directory to save recording
            metadata: Optional metadata to include in recording

        Returns:
            True if recording started successfully
        """
        if not self.is_connected:
            self.errorOccurred.emit("Cannot record: not connected to stream")
            return False

        if self.is_recording:
            self.errorOccurred.emit("Recording already in progress")
            return False

        try:
            # self.logger.info(f"Starting recording to: {output_directory}")

            # Determine recording resolution from stream info
            resolution = self.stream_info.get('resolution', (0, 0))
            if not resolution or resolution == (0, 0):
                resolution = (1280, 720)

            # Create recording manager (expects output directory path)
            self.recording_manager = RecordingManager(output_directory)
            # Connect signals BEFORE starting so we catch the initial recording started signal
            self.recording_manager.recordingStateChanged.connect(self._on_recording_manager_state_changed)

            # Start recording
            success = self.recording_manager.start_recording(resolution)
            if success:
                self.is_recording = True
                # self.logger.info(f"Recording started in: {output_directory}")
                return True
            else:
                self.is_recording = False
                self.errorOccurred.emit("Failed to start recording")
                return False

        except Exception as e:
            error_msg = f"Error starting recording: {str(e)}"
            self.logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
            return False

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording.

        Returns:
            Path to recorded file if successful, None otherwise
        """
        if not self.is_recording or not self.recording_manager:
            return None

        try:
            # self.logger.info("Stopping recording")

            # Save the path before stopping
            recording_path = self.current_recording_path

            # Stop recording - the state change will be handled by the signal
            self.recording_manager.stop_recording()

            # Keep recording_manager reference for test compatibility
            # It will be cleaned up on disconnect or next start_recording

            return recording_path

        except Exception as e:
            error_msg = f"Error stopping recording: {str(e)}"
            self.logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
            return None

    def record_frame(self, frame: np.ndarray, detections: Optional[list] = None):
        """
        Record a frame (if recording is active).

        Args:
            frame: Frame to record
            detections: Optional detection data to include
        """
        if self.is_recording and self.recording_manager:
            self.recording_manager.add_frame(frame)

    def _on_frame_ready(self, frame: np.ndarray, timestamp: float):
        """Handle frame received from stream."""
        # Update stream info
        self._update_stream_info()

        # Record frame if recording
        if self.is_recording:
            self.record_frame(frame)

        # Emit frame for processing
        self.frameReceived.emit(frame, timestamp)

    def _on_connection_status_changed(self, connected: bool, message: str):
        """Handle connection status change."""
        self.is_connected = connected
        self.connectionChanged.emit(connected, message)

    def _on_stream_error(self, error: str):
        """Handle stream error."""
        self.logger.error(f"Stream error: {error}")
        self.errorOccurred.emit(error)

    def _on_stream_stats_updated(self, stats: dict):
        """Handle stats updates from StreamManager/RTMP service."""
        # Merge stats into stream_info dictionary
        self.stream_info.update(stats)
        self.streamInfoUpdated.emit(self.stream_info)

    def _on_video_position_changed(self, current_time: float, total_time: float):
        """Handle video position updates for file playback."""
        self.stream_info["current_time"] = current_time
        self.stream_info["total_time"] = total_time
        self.streamInfoUpdated.emit(self.stream_info)

    def _on_recording_manager_state_changed(self, recording: bool, path_or_message: str):
        """Handle recording state changes from RecordingManager."""
        if recording:
            # Recording started - path_or_message is the actual file path
            self.current_recording_path = path_or_message
            # self.logger.info(f"Recording started: {path_or_message}")
        else:
            # Recording stopped - path_or_message is completion/error message
            self.is_recording = False
            # self.logger.info(f"Recording stopped: {path_or_message}")

        # Forward to UI
        self.recordingStateChanged.emit(recording, path_or_message)

    def _update_stream_info(self):
        """Update stream statistics (polling fallback)."""
        if self.stream_manager:
            # Get info from stream manager/service
            info = self.stream_manager.get_stream_info()
            if info:
                self.stream_info.update(info)
                self.streamInfoUpdated.emit(self.stream_info)

    def get_stream_info(self) -> dict:
        """Get current stream information."""
        return self.stream_info.copy()

    def is_stream_connected(self) -> bool:
        """Check if stream is connected."""
        return self.is_connected

    def is_stream_recording(self) -> bool:
        """Check if recording is active."""
        return self.is_recording

    def cleanup(self):
        """Clean up resources."""
        # self.logger.info("StreamCoordinator cleanup")

        # Stop recording
        if self.is_recording:
            self.stop_recording()

        # Disconnect stream
        if self.is_connected:
            self.disconnect_stream()
