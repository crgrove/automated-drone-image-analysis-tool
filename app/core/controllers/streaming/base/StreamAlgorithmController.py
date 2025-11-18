"""
StreamAlgorithmController - Base class for streaming detection algorithm controllers.

Defines the interface that all streaming detection algorithms must implement.
Similar to AlgorithmController for image analysis algorithms.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QMetaObject
import numpy as np
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod, ABCMeta


# Create a metaclass that combines QWidget's metaclass with ABCMeta
class QABCMeta(type(QWidget), ABCMeta):
    pass


class StreamAlgorithmController(QWidget, ABC, metaclass=QABCMeta):
    """
    Base class for streaming detection algorithm controllers.

    All streaming detection algorithms should inherit from this class and implement
    the required methods. This provides a consistent interface for the StreamViewerWindow
    to interact with different algorithms.

    Similar to how image analysis algorithms integrate into MainWindow, streaming
    algorithms integrate into StreamViewerWindow through this interface.
    """

    # Signals for communication with StreamViewerWindow
    detectionsReady = Signal(list)  # List of detections from current frame
    frameProcessed = Signal(np.ndarray)  # Processed frame with overlays
    configChanged = Signal(dict)  # Configuration changed by user
    statusUpdate = Signal(str)  # Status message for display
    requestRecording = Signal(bool)  # Request to start/stop recording

    def __init__(self, algorithm_config: Dict[str, Any], theme: str, parent=None):
        """
        Initialize the algorithm controller.

        Args:
            algorithm_config: Algorithm configuration dictionary (from registry)
            theme: UI theme ('light' or 'dark')
            parent: Parent widget
        """
        super().__init__(parent)

        self.algorithm_config = algorithm_config
        self.theme = theme
        self.is_running = False
        # By default algorithms rely on the viewer's DetectionRenderer. Algorithms
        # that emit fully annotated frames should set this to True so the viewer
        # can bypass additional rendering.
        self.provides_custom_rendering = False

        # Setup UI (implemented by subclass)
        self.setup_ui()

    @abstractmethod
    def setup_ui(self):
        """
        Setup the algorithm-specific UI.

        This should create all UI elements specific to this algorithm.
        Must be implemented by subclass.
        """
        pass

    @abstractmethod
    def process_frame(self, frame: np.ndarray, timestamp: float) -> List[Dict]:
        """
        Process a frame and return detections.

        This is the core algorithm processing method. It receives a frame from
        the stream and returns a list of detections.

        Args:
            frame: Input frame (BGR format from OpenCV)
            timestamp: Frame timestamp

        Returns:
            List of detection dictionaries with keys:
                - bbox: (x, y, w, h) bounding box
                - confidence: float (0-1)
                - class_name: str
                - id: int (optional, for tracking)
                - any other algorithm-specific data

        Must be implemented by subclass.
        """
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Get current algorithm configuration.

        Returns a dictionary containing all algorithm parameters and settings.
        Used for saving/loading configurations.

        Returns:
            Dictionary of configuration parameters

        Must be implemented by subclass.
        """
        pass

    @abstractmethod
    def set_config(self, config: Dict[str, Any]):
        """
        Apply algorithm configuration.

        Updates the algorithm with new configuration parameters.
        Used for loading saved configurations.

        Args:
            config: Dictionary of configuration parameters

        Must be implemented by subclass.
        """
        pass

    def on_stream_connected(self, resolution: tuple):
        """
        Called when stream connects.

        Override this to handle stream connection events (e.g., initialize
        algorithm-specific resources based on stream resolution).

        Args:
            resolution: (width, height) of stream
        """
        self.is_running = True

    def on_stream_disconnected(self):
        """
        Called when stream disconnects.

        Override this to handle cleanup when stream stops.
        """
        self.is_running = False

    def on_recording_started(self, recording_path: str):
        """
        Called when recording starts.

        Override this to handle recording start events.

        Args:
            recording_path: Path where recording is being saved
        """
        pass

    def on_recording_stopped(self, recording_path: str):
        """
        Called when recording stops.

        Override this to handle recording stop events.

        Args:
            recording_path: Path where recording was saved
        """
        pass

    def get_stats(self) -> Dict[str, str]:
        """
        Get algorithm-specific statistics for display.

        Override this to provide algorithm-specific stats (e.g., detection count,
        processing time, algorithm-specific metrics).

        Returns:
            Dictionary of stat name -> formatted value
        """
        return {}

    def reset(self):
        """
        Reset algorithm state.

        Override this to reset any accumulated state (e.g., background models,
        tracking history, etc.).
        """
        pass

    def cleanup(self):
        """
        Clean up algorithm resources.

        Override this to release any algorithm-specific resources
        (e.g., models, buffers, etc.).
        """
        pass

    # Helper methods for subclasses

    def _emit_status(self, message: str):
        """Emit a status message."""
        self.statusUpdate.emit(message)

    def _emit_config_changed(self):
        """Emit signal that configuration has changed."""
        self.configChanged.emit(self.get_config())

    def _request_recording_start(self):
        """Request recording to start."""
        self.requestRecording.emit(True)

    def _request_recording_stop(self):
        """Request recording to stop."""
        self.requestRecording.emit(False)
