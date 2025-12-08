"""
FrameProcessingWorker - Background thread worker for algorithm frame processing.

Moves heavy algorithm processing off the main thread to prevent UI blocking.
The worker processes frames using algorithm services directly, which are QObjects
that can safely be moved to worker threads.
"""

from PySide6.QtCore import QObject, Signal, Slot, Qt
from typing import Optional, List, Dict, Any, Callable
import numpy as np
import time


class FrameProcessingWorker(QObject):
    """
    Worker object for processing frames in a background thread.

    This worker runs in a separate QThread and handles all heavy computation
    (algorithm processing, detection) to keep the UI responsive.

    The worker processes frames by calling a processing function that uses the
    algorithm's service objects (which are QObjects that can be moved to threads).
    """

    # Signals emitted from worker thread
    frameProcessed = Signal(np.ndarray, list, float)  # frame, detections, processing_time_ms
    errorOccurred = Signal(str)  # error_message

    # Signal to request frame processing (emitted from main thread, received in worker thread)
    processFrameRequested = Signal(np.ndarray, float)  # frame, timestamp

    # Signal to request stop (emitted from main thread, received in worker thread)
    stopRequested = Signal()

    def __init__(self, processing_function: Callable, pause_check: Optional[Callable[[], bool]] = None):
        """
        Initialize the frame processing worker.

        Args:
            processing_function: Function that processes a frame and returns detections
                Signature: (frame: np.ndarray, timestamp: float) -> List[Dict]
                This function should use algorithm service objects that are moved to
                the worker thread.
            pause_check: Optional function to check if processing should be paused.
                Returns True if paused, False if playing. Called from worker thread.
        """
        super().__init__()
        self.processing_function = processing_function
        self._should_stop = False
        self._pause_check = pause_check

        # Connect the request signal to the processing slot
        self.processFrameRequested.connect(self._process_frame_internal, Qt.QueuedConnection)
        # Connect stop signal to slot
        self.stopRequested.connect(self._handle_stop_request, Qt.QueuedConnection)

    @Slot(np.ndarray, float)
    def _process_frame_internal(self, frame: np.ndarray, timestamp: float):
        """
        Internal slot that processes a frame in the background thread.

        This is called via the processFrameRequested signal, ensuring it runs
        in the worker thread's context.

        Args:
            frame: Input frame (BGR format) - will be copied for thread safety
            timestamp: Frame timestamp
        """
        if self._should_stop or not self.processing_function:
            return

        # Check if paused (skip processing if paused)
        if self._pause_check and self._pause_check():
            return

        try:
            start_time = time.time()

            # Copy frame for thread safety (numpy arrays are not thread-safe by default)
            frame_copy = frame.copy()

            # Process frame with algorithm (calls service methods in worker thread)
            detections = self.processing_function(frame_copy, timestamp)

            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000

            # Emit results back to main thread
            # Note: Rendering happens on main thread since Qt operations must be on main thread
            self.frameProcessed.emit(frame_copy, detections, processing_time_ms)

        except Exception as e:
            error_msg = f"Error processing frame: {str(e)}"
            self.errorOccurred.emit(error_msg)

    @Slot()
    def _handle_stop_request(self):
        """Handle stop request from main thread (runs in worker thread)."""
        self._should_stop = True

    def stop(self):
        """Stop processing frames (thread-safe, can be called from any thread)."""
        # Set flag immediately (this is atomic in Python, so thread-safe)
        # This ensures current/next processing check will see the stop flag
        self._should_stop = True
        # Also emit signal to handle any queued work cleanly
        try:
            self.stopRequested.emit()
        except RuntimeError:
            # Object may already be deleted, flag already set above
            pass
