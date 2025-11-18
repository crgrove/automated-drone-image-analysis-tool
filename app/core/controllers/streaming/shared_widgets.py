"""
shared_widgets.py - Shared widgets for streaming viewers

Contains reusable widgets and components used across multiple streaming viewers:
- DetectionTracker: Tracks detections across frames
- DetectionThumbnailWidget: Displays detection thumbnails
- VideoDisplayWidget: Optimized video display widget
- StreamControlWidget: Stream connection and recording controls
"""

import numpy as np
import cv2
import time
from typing import List, Dict, Optional, Any
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout,
                               QGroupBox, QLineEdit, QPushButton, QComboBox, QFileDialog,
                               QMessageBox)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal
from core.services.streaming.RTMPStreamService import StreamType


class DetectionTracker:
    """Tracks detections across frames to maintain stable thumbnail assignments with ghost memory and minimum display duration."""

    def __init__(self, max_slots=7, distance_threshold=100.0, ghost_frames=60, ghost_distance_multiplier=3.0, min_display_frames=60):
        """
        Initialize detection tracker.

        Args:
            max_slots: Maximum number of thumbnail slots
            distance_threshold: Maximum centroid distance to consider same detection (pixels)
            ghost_frames: Number of frames to remember lost detections before freeing slot (default 60 = ~2s at 30fps)
            ghost_distance_multiplier: Multiplier for ghost matching threshold (handles camera pans)
                                      Default 3.0 means ghosts can match up to 300px away (for 100px threshold)
            min_display_frames: Minimum frames to display a thumbnail before it can be replaced (default 60 = ~2s at 30fps)
        """
        self.max_slots = max_slots
        self.distance_threshold = distance_threshold
        self.ghost_frames = ghost_frames
        self.ghost_distance_multiplier = ghost_distance_multiplier
        self.min_display_frames = min_display_frames

        # Current slot assignments: {slot_index: Detection}
        self.slot_assignments = {}

        # Slot display tracking: {slot_index: {'detection_id': id, 'frames_displayed': count, 'last_detection': Detection}}
        # Tracks how long each slot has been displaying its current detection
        self.slot_display_info = {}

        # Tracking history for matching
        self.previous_detections = []

        # Next detection ID
        self.next_id = 0

        # Detection ID to slot mapping
        self.id_to_slot = {}

        # Ghost memory: tracks recently lost detections
        # Format: {detection_id: {'centroid': (x, y), 'slot': slot_idx, 'frames_lost': count}}
        self.ghost_detections = {}

        # Frame counter
        self.frame_count = 0

    def update(self, current_detections: List) -> Dict[int, any]:
        """
        Update tracking with new detections and return slot assignments.

        Uses ghost memory and minimum display duration to maintain stable thumbnails.
        Thumbnails are displayed for at least min_display_frames even if detection disappears.

        Args:
            current_detections: List of detections from current frame

        Returns:
            Dictionary mapping slot index (0-6) to Detection objects (including held thumbnails)
        """
        self.frame_count += 1

        # Match current detections to previous detections (and ghosts)
        matched_detections = self._match_detections(current_detections)

        # Update slot assignments - keep thumbnails showing for minimum duration
        new_slot_assignments = {}

        # First, handle existing slot assignments (keep thumbnails for minimum duration)
        for slot_idx in range(self.max_slots):
            if slot_idx in self.slot_display_info:
                info = self.slot_display_info[slot_idx]
                info['frames_displayed'] += 1

                # Check if this slot's detection is still active
                detection_still_active = False
                for detection in matched_detections:
                    if detection.metadata.get('track_id') == info['detection_id']:
                        # Detection still active - update with fresh detection
                        new_slot_assignments[slot_idx] = detection
                        info['last_detection'] = detection
                        detection_still_active = True
                        # Remove from ghosts if it was ghosted (it's back!)
                        if info['detection_id'] in self.ghost_detections:
                            del self.ghost_detections[info['detection_id']]
                        break

                if not detection_still_active:
                    # Detection disappeared - check if we should keep displaying it
                    if info['frames_displayed'] < self.min_display_frames:
                        # Keep displaying the last known thumbnail (hold for minimum duration)
                        new_slot_assignments[slot_idx] = info['last_detection']
                    # else: slot expires and becomes available

        # Handle detections that already have slot assignments but aren't in slot_display_info yet
        # (This can happen when a ghost revives)
        for detection in matched_detections:
            det_id = detection.metadata.get('track_id')
            if det_id in self.id_to_slot:
                slot = self.id_to_slot[det_id]
                if slot not in self.slot_display_info and slot not in new_slot_assignments:
                    # Revived ghost or new assignment - initialize display info
                    new_slot_assignments[slot] = detection
                    self.slot_display_info[slot] = {
                        'detection_id': det_id,
                        'frames_displayed': 0,
                        'last_detection': detection
                    }
                    # Remove from ghosts if it was ghosted
                    if det_id in self.ghost_detections:
                        del self.ghost_detections[det_id]

        # Handle lost detections - move to ghost memory
        active_ids = {d.metadata.get('track_id') for d in matched_detections}

        # Track which detection IDs have slots (either active or being held)
        displayed_ids = set()
        for slot_idx, info in self.slot_display_info.items():
            displayed_ids.add(info['detection_id'])

        lost_ids = displayed_ids - active_ids

        for lost_id in lost_ids:
            if lost_id not in self.ghost_detections and lost_id in self.id_to_slot:
                # New ghost - store its last known position and slot
                slot = self.id_to_slot[lost_id]
                # Find the last centroid
                last_centroid = None
                if slot in self.slot_display_info:
                    last_det = self.slot_display_info[slot]['last_detection']
                    last_centroid = last_det.centroid

                if last_centroid:
                    self.ghost_detections[lost_id] = {
                        'centroid': last_centroid,
                        'slot': slot,
                        'frames_lost': 0
                    }

        # Age ghosts and remove expired ones
        expired_ghosts = []
        for ghost_id, ghost_info in self.ghost_detections.items():
            ghost_info['frames_lost'] += 1
            if ghost_info['frames_lost'] > self.ghost_frames:
                expired_ghosts.append(ghost_id)

        # Clean up expired ghosts and their slot mappings
        for ghost_id in expired_ghosts:
            del self.ghost_detections[ghost_id]
            if ghost_id in self.id_to_slot:
                del self.id_to_slot[ghost_id]

        # Clean up expired slot display info (slots that are no longer showing anything)
        slots_to_remove = []
        for slot_idx, info in self.slot_display_info.items():
            if slot_idx not in new_slot_assignments:
                slots_to_remove.append(slot_idx)

        for slot_idx in slots_to_remove:
            del self.slot_display_info[slot_idx]
            # Also remove from id_to_slot mapping
            det_id = None
            for id, slot in list(self.id_to_slot.items()):
                if slot == slot_idx:
                    det_id = id
                    break
            if det_id:
                del self.id_to_slot[det_id]

        # Assign new detections to truly empty slots (not held slots)
        # Sort new detections by position (left-to-right, top-to-bottom) for stable ordering
        new_detections = [d for d in matched_detections if d.metadata.get('track_id') not in self.id_to_slot]
        new_detections.sort(key=lambda d: (d.centroid[1] // 100, d.centroid[0]))  # Group by row, then column

        for detection in new_detections:
            # Find first truly available slot (not occupied or held)
            for slot_idx in range(self.max_slots):
                if slot_idx not in new_slot_assignments:
                    det_id = detection.metadata.get('track_id')
                    self.id_to_slot[det_id] = slot_idx
                    new_slot_assignments[slot_idx] = detection
                    # Initialize slot display info
                    self.slot_display_info[slot_idx] = {
                        'detection_id': det_id,
                        'frames_displayed': 0,
                        'last_detection': detection
                    }
                    break

        # Store for next frame
        self.previous_detections = matched_detections
        self.slot_assignments = new_slot_assignments

        return new_slot_assignments

    def _match_detections(self, current_detections: List) -> List:
        """
        Match current detections to previous detections and ghosts using centroid distance.
        Assigns track IDs to detections, reviving ghosts when possible.

        Args:
            current_detections: List of detections from current frame

        Returns:
            List of detections with track_id added to metadata
        """
        if not self.previous_detections and not self.ghost_detections:
            # First frame - assign new IDs to all detections
            for detection in current_detections:
                detection.metadata['track_id'] = self.next_id
                self.next_id += 1
            return current_detections

        # Build cost matrix based on centroid distance
        matched_detections = []
        used_prev_indices = set()
        used_ghost_ids = set()

        for curr_det in current_detections:
            curr_cx, curr_cy = curr_det.centroid
            best_match_idx = None
            best_ghost_id = None
            best_distance = self.distance_threshold

            # First, try to match to previous detections (prioritize active detections)
            for i, prev_det in enumerate(self.previous_detections):
                if i in used_prev_indices:
                    continue

                prev_cx, prev_cy = prev_det.centroid
                distance = np.sqrt((curr_cx - prev_cx)**2 + (curr_cy - prev_cy)**2)

                if distance < best_distance:
                    best_distance = distance
                    best_match_idx = i

            # If no match to active detections, try matching to ghosts
            if best_match_idx is None:
                for ghost_id, ghost_info in self.ghost_detections.items():
                    if ghost_id in used_ghost_ids:
                        continue

                    ghost_cx, ghost_cy = ghost_info['centroid']
                    distance = np.sqrt((curr_cx - ghost_cx)**2 + (curr_cy - ghost_cy)**2)

                    # Use larger threshold for ghosts to handle camera pans
                    # Ghosts can match from much farther away since camera might have moved
                    ghost_threshold = self.distance_threshold * self.ghost_distance_multiplier
                    if distance < ghost_threshold and distance < best_distance:
                        best_distance = distance
                        best_ghost_id = ghost_id

            if best_match_idx is not None:
                # Matched to previous detection - keep same ID
                prev_det = self.previous_detections[best_match_idx]
                curr_det.metadata['track_id'] = prev_det.metadata['track_id']
                used_prev_indices.add(best_match_idx)
            elif best_ghost_id is not None:
                # Matched to ghost - revive the ghost!
                curr_det.metadata['track_id'] = best_ghost_id
                used_ghost_ids.add(best_ghost_id)
                # The ghost will be removed from ghost_detections in update()
            else:
                # New detection - assign new ID
                curr_det.metadata['track_id'] = self.next_id
                self.next_id += 1

            matched_detections.append(curr_det)

        return matched_detections

    def clear(self):
        """Clear all tracking state including ghost memory and display info."""
        self.slot_assignments.clear()
        self.slot_display_info.clear()
        self.previous_detections.clear()
        self.id_to_slot.clear()
        self.ghost_detections.clear()
        self.next_id = 0
        self.frame_count = 0


class DetectionThumbnailWidget(QWidget):
    """Widget to display thumbnails of top detections with dynamic sizing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(150)
        self.setStyleSheet("QWidget { background-color: #2b2b2b; }")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        # Thumbnail configuration
        self.thumbnail_size = 120  # Fixed size for each thumbnail
        self.thumbnail_spacing = 10  # Spacing between thumbnails
        self.thumbnail_labels = []

        # Detection tracker - will be updated with dynamic max_slots
        # ghost_frames=60 means remember lost detections for ~2 seconds at 30fps
        # min_display_frames=60 means hold thumbnails for ~2 seconds minimum (reduces flicker!)
        # ghost_distance_multiplier=3.0 means ghosts can match up to 300px away (handles camera pans)
        self.tracker = DetectionTracker(
            max_slots=20,
            distance_threshold=100.0,
            ghost_frames=60,
            ghost_distance_multiplier=3.0,
            min_display_frames=60
        )

        # Add stretch to push thumbnails to the left
        self.layout.addStretch()

    def resizeEvent(self, event):
        """Handle widget resize to adjust number of visible thumbnails."""
        super().resizeEvent(event)
        self._adjust_thumbnail_count()

    def _adjust_thumbnail_count(self):
        """Calculate and adjust the number of thumbnails based on available width."""
        available_width = self.width() - self.layout.contentsMargins().left() - self.layout.contentsMargins().right()

        # Calculate how many thumbnails can fit
        # Formula: (width - margins) / (thumbnail_size + spacing)
        max_thumbnails = max(1, int(available_width / (self.thumbnail_size + self.thumbnail_spacing)))

        # Limit to reasonable maximum
        max_thumbnails = min(max_thumbnails, 20)

        current_count = len(self.thumbnail_labels)

        if max_thumbnails > current_count:
            # Add more thumbnail labels (insert before the stretch item at the end)
            for i in range(current_count, max_thumbnails):
                label = QLabel()
                label.setFixedSize(self.thumbnail_size, self.thumbnail_size)
                label.setStyleSheet("QLabel { background-color: black; border: 2px solid #555; }")
                label.setAlignment(Qt.AlignCenter)
                label.setScaledContents(False)
                # Insert before the last item (which is the stretch)
                self.layout.insertWidget(self.layout.count() - 1, label)
                self.thumbnail_labels.append(label)
        elif max_thumbnails < current_count:
            # Hide excess thumbnail labels
            for i in range(max_thumbnails, current_count):
                self.thumbnail_labels[i].setVisible(False)
            # Show the ones that should be visible
            for i in range(max_thumbnails):
                self.thumbnail_labels[i].setVisible(True)
        else:
            # Same count, just ensure correct visibility
            for i in range(current_count):
                self.thumbnail_labels[i].setVisible(i < max_thumbnails)

        # Update tracker max slots
        self.tracker.max_slots = max_thumbnails

    def update_thumbnails(self, frame: np.ndarray, detections: List, zoom: float = 3.0,
                          processing_resolution: tuple = None, original_resolution: tuple = None):
        """Update thumbnails with tracked detections in stable slots.

        Args:
            frame: The frame to extract thumbnails from (should be at original resolution)
            detections: List of detections (coordinates are already at original resolution - service scales them back)
            zoom: Zoom level (higher = tighter crop around detection)
            processing_resolution: (width, height) of processing resolution (unused, kept for compatibility)
            original_resolution: (width, height) of frame (unused, kept for compatibility)
        """
        # Use tracker to get stable slot assignments
        slot_assignments = self.tracker.update(detections)

        # Calculate scale factor if we need to convert coordinates
        scale_x = 1.0
        scale_y = 1.0
        if processing_resolution and original_resolution:
            scale_x = original_resolution[0] / processing_resolution[0]
            scale_y = original_resolution[1] / processing_resolution[1]

        # Update each thumbnail label based on slot assignment (only visible ones)
        for slot_idx, label in enumerate(self.thumbnail_labels):
            if not label.isVisible():
                continue

            if slot_idx in slot_assignments:
                detection = slot_assignments[slot_idx]

                # Extract zoomed region around detection centroid
                # Scale coordinates if detection is in processing resolution but frame is original
                cx_raw, cy_raw = detection.centroid
                x_raw, y_raw, w_raw, h_raw = detection.bbox

                # Apply scale factor to convert from processing res to frame res
                cx = int(cx_raw * scale_x)
                cy = int(cy_raw * scale_y)
                w = int(w_raw * scale_x)
                h = int(h_raw * scale_y)

                # Calculate zoom window - zoom controls magnification level
                # Higher zoom = tighter crop = detection appears larger in thumbnail
                # zoom=1.0: show wide context (4.5x detection size)
                # zoom=3.0: show tight crop (1.5x detection size) - detection fills most of thumbnail
                # zoom=5.0: show very tight crop (0.9x detection size, just the detection)
                BASE_CONTEXT_MULTIPLIER = 4.5  # Context multiplier at zoom=1.0
                context_multiplier = BASE_CONTEXT_MULTIPLIER / zoom

                zoom_w = int(w * context_multiplier)
                zoom_h = int(h * context_multiplier)

                # Minimum size for very small detections (ensure at least 60px)
                zoom_w = max(60, zoom_w)
                zoom_h = max(60, zoom_h)

                # Calculate extraction bounds centered on detection centroid
                x1 = max(0, cx - zoom_w // 2)
                y1 = max(0, cy - zoom_h // 2)
                x2 = min(frame.shape[1], cx + zoom_w // 2)
                y2 = min(frame.shape[0], cy + zoom_h // 2)

                # Extract region
                thumbnail = frame[y1:y2, x1:x2].copy()

                if thumbnail.size > 0:
                    # Convert to QPixmap and display
                    h, w, ch = thumbnail.shape
                    bytes_per_line = ch * w
                    rgb_thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)
                    q_image = QImage(rgb_thumbnail.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)
                    scaled_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
                    label.setPixmap(scaled_pixmap)
                else:
                    label.clear()
            else:
                # No detection assigned to this slot
                label.clear()

    def clear_thumbnails(self):
        """Clear all thumbnails and reset tracking."""
        for label in self.thumbnail_labels:
            if label.isVisible():
                label.clear()
        self.tracker.clear()


class VideoDisplayWidget(QLabel):
    """Optimized video display widget for real-time streaming."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 480)
        # Remove any maximum size constraints to allow full expansion
        self.setMaximumSize(16777215, 16777215)  # Qt's maximum widget size
        self.setStyleSheet("QLabel { background-color: black; border: 1px solid gray; }")
        self.setAlignment(Qt.AlignCenter)
        self.setText("No Stream Connected")
        self.setScaledContents(False)
        # Set size policy to expanding so it grows to fill available space
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_frame(self, frame: np.ndarray):
        """Update display with new frame."""
        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create QImage and QPixmap
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)

            # Scale to fit widget while maintaining aspect ratio
            # Use FastTransformation for better real-time performance
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
            self.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"Error updating frame: {e}")


class StreamControlWidget(QWidget):
    """Shared stream connection and control widget with optional recording controls."""

    connectRequested = Signal(str, str)  # url, stream_type
    disconnectRequested = Signal()
    startRecordingRequested = Signal(str)
    stopRecordingRequested = Signal()
    recordingDirectoryChanged = Signal(str)

    def __init__(self, parent=None, include_recording=True):
        """
        Initialize stream control widget.

        Args:
            parent: Parent widget
            include_recording: If True, includes recording controls (default: True)
        """
        super().__init__(parent)
        self.include_recording = include_recording
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup stream control interface."""
        layout = QVBoxLayout(self)

        # Connection group
        connection_group = QGroupBox("Stream Connection")
        connection_group.setToolTip("Configure and connect to video source (file, HDMI capture, or RTMP stream)")
        connection_layout = QGridLayout(connection_group)

        # Stream URL with browse button for files
        connection_layout.addWidget(QLabel("Stream URL:"), 0, 0)

        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Click to browse for video file...")
        self.url_input.setText("")  # Default empty for file selection
        self.url_input.setToolTip("Enter or browse for the video source:\n"
                                  "• File: Click to browse for video file (MP4, AVI, MOV, etc.)\n"
                                  "• HDMI Capture: Enter device index (0, 1, 2, etc.)\n"
                                  "• RTMP Stream: Enter RTMP URL (rtmp://server:port/app/stream)")
        url_layout.addWidget(self.url_input, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setVisible(True)  # Visible by default since File is default
        self.browse_button.setToolTip("Open file browser to select a video file for analysis.\n"
                                      "Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM")
        url_layout.addWidget(self.browse_button)

        connection_layout.addLayout(url_layout, 0, 1)

        # Stream type
        connection_layout.addWidget(QLabel("Stream Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["File", "HDMI Capture", "RTMP Stream"])
        self.type_combo.setToolTip("Select the type of video source:\n"
                                   "• File: Pre-recorded video file with timeline controls\n"
                                   "• HDMI Capture: Live capture from HDMI capture device\n"
                                   "• RTMP Stream: Real-time streaming from RTMP/HTTP source")
        connection_layout.addWidget(self.type_combo, 1, 1)

        # Connection buttons
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.connect_button.setToolTip("Connect to the specified video source and begin processing.")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setToolTip("Disconnect from the current video source and stop processing.")

        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        # Status display
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        self.status_label.setToolTip("Current connection status")

        # Performance display
        performance_group = QGroupBox("Performance")
        performance_group.setToolTip("Real-time performance metrics")
        performance_layout = QGridLayout(performance_group)

        self.fps_label = QLabel("FPS: --")
        self.fps_label.setToolTip("Frames per second being processed")
        self.latency_label = QLabel("Processing: -- ms")
        self.latency_label.setToolTip("Time in milliseconds to process each frame")
        self.detections_label = QLabel("Detections: --")
        self.detections_label.setToolTip("Number of detections in current frame")

        performance_layout.addWidget(self.fps_label, 0, 0)
        performance_layout.addWidget(self.latency_label, 0, 1)
        performance_layout.addWidget(self.detections_label, 1, 0)

        # Recording group (optional)
        if self.include_recording:
            recording_group = QGroupBox("Recording")
            recording_layout = QVBoxLayout(recording_group)

            # Recording buttons
            recording_button_layout = QHBoxLayout()
            self.start_recording_btn = QPushButton("Start Recording")
            self.start_recording_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-weight: bold; }")
            self.start_recording_btn.setToolTip("Start recording the video stream with detection overlays.")
            self.stop_recording_btn = QPushButton("Stop Recording")
            self.stop_recording_btn.setEnabled(False)
            self.stop_recording_btn.setToolTip("Stop the current recording and save to file.")

            recording_button_layout.addWidget(self.start_recording_btn)
            recording_button_layout.addWidget(self.stop_recording_btn)

            # Recording status
            self.recording_status = QLabel("Status: Not Recording")
            self.recording_status.setStyleSheet("QLabel { color: gray; }")
            self.recording_status.setToolTip("Current recording status and output file path")

            # Recording info
            self.recording_info = QLabel("Duration: --")
            self.recording_info.setToolTip("Recording statistics: Duration, FPS, Frames")

            recording_layout.addLayout(recording_button_layout)
            recording_layout.addWidget(self.recording_status)
            recording_layout.addWidget(self.recording_info)

            # Recording directory selector
            dir_layout = QHBoxLayout()
            dir_label = QLabel("Save to:")
            self.recording_dir_edit = QLineEdit("./recordings")
            self.recording_dir_edit.setToolTip("Directory where video recordings will be saved.")
            self.recording_dir_browse = QPushButton("Browse...")
            self.recording_dir_browse.setToolTip("Choose a folder to store recordings.")

            dir_layout.addWidget(dir_label)
            dir_layout.addWidget(self.recording_dir_edit, 1)
            dir_layout.addWidget(self.recording_dir_browse)
            recording_layout.addLayout(dir_layout)

        # Add to main layout
        layout.addWidget(connection_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(performance_group)
        if self.include_recording:
            layout.addWidget(recording_group)
        layout.addStretch()

    def connect_signals(self):
        """Connect UI signals."""
        self.connect_button.clicked.connect(self.request_connect)
        self.disconnect_button.clicked.connect(self.disconnectRequested.emit)
        self.type_combo.currentTextChanged.connect(self.on_stream_type_changed)
        self.browse_button.clicked.connect(self.browse_for_file)
        self.url_input.mousePressEvent = self.on_url_input_clicked
        if self.include_recording:
            self.start_recording_btn.clicked.connect(self._emit_start_recording)
            self.stop_recording_btn.clicked.connect(self.stopRecordingRequested.emit)
            self.recording_dir_browse.clicked.connect(self._browse_recording_directory)
            self.recording_dir_edit.textChanged.connect(self._on_recording_directory_changed)

    def on_stream_type_changed(self, stream_type: str):
        """Handle stream type selection changes."""
        if stream_type == "HDMI Capture":
            self.url_input.setPlaceholderText("Device index (0, 1, 2, etc.)")
            self.url_input.setText("0")
            self.browse_button.setVisible(False)
        elif stream_type == "File":
            self.url_input.setPlaceholderText("Click to browse for video file...")
            self.url_input.setText("")
            self.browse_button.setVisible(True)
        elif stream_type == "RTMP Stream":
            self.url_input.setPlaceholderText("rtmp://server:port/app/stream")
            self.url_input.setText("")
            self.browse_button.setVisible(False)

    def request_connect(self):
        """Request stream connection."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid stream URL.")
            return

        # Map combo box text to StreamType enum
        combo_text = self.type_combo.currentText()
        stream_type_map = {
            "File": StreamType.FILE,
            "HDMI Capture": StreamType.HDMI_CAPTURE,
            "RTMP Stream": StreamType.RTMP
        }
        stream_type = stream_type_map.get(combo_text, StreamType.FILE)
        self.connectRequested.emit(url, stream_type)

    def update_connection_status(self, connected: bool, message: str):
        """Update connection status display."""
        if connected:
            self.status_label.setText(f"Status: {message}")
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        else:
            self.status_label.setText(f"Status: {message}")
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def update_recording_state(self, recording: bool, path_or_message: str = ""):
        """Update recording state and UI."""
        if not self.include_recording:
            return

        start_active_style = (
            "QPushButton { background-color: #ff4444; color: white; font-weight: bold; }"
        )
        start_disabled_style = (
            "QPushButton { background-color: #555555; color: #cccccc; font-weight: bold; }"
        )
        stop_active_style = start_active_style
        stop_inactive_style = (
            "QPushButton { background-color: #444444; color: #aaaaaa; font-weight: bold; }"
        )

        if recording:
            # Recording started
            self.start_recording_btn.setEnabled(False)
            self.start_recording_btn.setStyleSheet(start_disabled_style)
            self.stop_recording_btn.setEnabled(True)
            self.stop_recording_btn.setStyleSheet(stop_active_style)
            self.recording_status.setText("Status: Recording")
            self.recording_status.setStyleSheet("QLabel { color: #ff4444; font-weight: bold; }")
            if path_or_message:
                self.recording_info.setText(f"Output: {path_or_message}")
        else:
            # Recording stopped
            self.start_recording_btn.setEnabled(True)
            self.start_recording_btn.setStyleSheet(start_active_style)
            self.stop_recording_btn.setEnabled(False)
            self.stop_recording_btn.setStyleSheet(stop_inactive_style)
            self.recording_status.setText("Status: Not Recording")
            self.recording_status.setStyleSheet("QLabel { color: gray; }")
            if path_or_message:
                self.recording_info.setText(f"Duration: {path_or_message}")
            else:
                self.recording_info.setText("Duration: --")

    def set_recording_directory(self, directory: str):
        """Set the recording directory path."""
        if not self.include_recording:
            return
        if directory:
            self.recording_dir_edit.setText(directory)

    def get_recording_directory(self) -> str:
        """Get the current recording directory."""
        if not self.include_recording:
            return "./recordings"
        path = self.recording_dir_edit.text().strip()
        return path or "./recordings"

    def _emit_start_recording(self):
        """Emit start recording with current directory."""
        directory = self.get_recording_directory()
        self.startRecordingRequested.emit(directory)

    def _browse_recording_directory(self):
        """Open folder selection dialog for recording directory."""
        current_dir = self.get_recording_directory()
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Recording Directory", current_dir or ".")
        if selected_dir:
            self.recording_dir_edit.setText(selected_dir)
            self.recordingDirectoryChanged.emit(selected_dir)

    def _on_recording_directory_changed(self, directory: str):
        """Handle manual edits to recording directory."""
        cleaned = directory.strip()
        if not cleaned:
            cleaned = "./recordings"
        if cleaned != directory:
            self.recording_dir_edit.setText(cleaned)
        self.recordingDirectoryChanged.emit(cleaned)

    def update_performance(self, stats: Dict[str, Any]):
        """Update performance display."""
        fps = stats.get('fps', stats.get('avg_fps', 0))
        processing_time = stats.get('current_processing_time_ms', stats.get('avg_processing_time_ms', stats.get('total_ms', 0)))
        detection_count = stats.get('detection_count', stats.get('detections', 0))

        self.fps_label.setText(f"FPS: {fps:.1f}")
        self.latency_label.setText(f"Processing: {processing_time:.1f} ms")
        self.detections_label.setText(f"Detections: {detection_count}")

    def browse_for_file(self):
        """Open file dialog to select video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)"
        )
        if file_path:
            self.url_input.setText(file_path)

    def on_url_input_clicked(self, event):
        """Handle clicks on URL input field."""
        # If file type is selected, open file browser on click
        if self.type_combo.currentText() == "File":
            self.browse_for_file()
        else:
            # Call the original mousePressEvent for normal behavior
            QLineEdit.mousePressEvent(self.url_input, event)
