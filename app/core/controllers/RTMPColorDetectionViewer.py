"""
RTMPColorDetectionViewer.py - Real-time RTMP stream viewer with HSV color detection

Integrates with ADIAT's existing HSV interface and provides real-time video
stream processing with color detection capabilities.
"""

# Set environment variable to avoid numpy compatibility issues - MUST be first
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')

import cv2
import numpy as np
import time
import math
from typing import Optional, List, Dict, Any

from PySide6.QtCore import Qt, QTimer, Signal, QRect
from PySide6.QtGui import QImage, QPixmap, QFont, QColor, QKeySequence, QPainter, QBrush, QPen
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit, QSpinBox, QFrame,
                               QGroupBox, QGridLayout, QTextEdit, QSplitter,
                               QColorDialog, QCheckBox, QComboBox, QProgressBar,
                               QMessageBox, QStatusBar, QSlider, QFileDialog, QDialog, QTabWidget,
                               QListWidget, QListWidgetItem, QDoubleSpinBox)

from core.services.RTMPStreamService import StreamManager, StreamType
from core.services.RealtimeColorDetectionService import RealtimeColorDetector, HSVConfig, Detection, MotionAlgorithm, FusionMode
from core.services.VideoRecordingService import RecordingManager
from core.services.LoggerService import LoggerService


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

    def update(self, current_detections: List[Detection]) -> Dict[int, Detection]:
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

    def _match_detections(self, current_detections: List[Detection]) -> List[Detection]:
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
            best_is_ghost = False

            # First, try to match to previous detections (prioritize active detections)
            for i, prev_det in enumerate(self.previous_detections):
                if i in used_prev_indices:
                    continue

                prev_cx, prev_cy = prev_det.centroid
                distance = np.sqrt((curr_cx - prev_cx)**2 + (curr_cy - prev_cy)**2)

                if distance < best_distance:
                    best_distance = distance
                    best_match_idx = i
                    best_is_ghost = False

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
                        best_is_ghost = True

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

    def update_thumbnails(self, frame: np.ndarray, detections: List[Detection], zoom: float = 3.0,
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

        # NOTE: Detections are already scaled to original resolution by the service
        # So we can use their coordinates directly on the frame without any scaling

        # Update each thumbnail label based on slot assignment (only visible ones)
        for slot_idx, label in enumerate(self.thumbnail_labels):
            if not label.isVisible():
                continue

            if slot_idx in slot_assignments:
                detection = slot_assignments[slot_idx]

                # Extract zoomed region around detection centroid
                # Coordinates are already in frame resolution
                cx, cy = detection.centroid
                x, y, w, h = detection.bbox

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
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"Error updating frame: {e}")


class HSVColorPickerDialog(QDialog):
    """Custom color picker dialog with HSV threshold visualization."""

    def __init__(self, initial_color=QColor(255, 0, 0), hue_threshold=20, sat_threshold=50, val_threshold=50, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Target Color with HSV Thresholds")
        self.setFixedSize(800, 600)

        # Store parameters
        self.selected_color = initial_color
        self.hue_threshold = hue_threshold
        self.sat_threshold = sat_threshold
        self.val_threshold = val_threshold

        # Create UI
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the custom color picker UI."""
        layout = QVBoxLayout(self)

        # Top section with color picker and preview
        top_layout = QHBoxLayout()

        # Left side - Standard color picker
        picker_frame = QFrame()
        picker_frame.setFrameStyle(QFrame.StyledPanel)
        picker_layout = QVBoxLayout(picker_frame)

        # Create a custom color widget that shows HSV ranges
        self.color_preview = HSVColorPreviewWidget(self.selected_color)
        self.color_preview.setFixedSize(300, 200)
        picker_layout.addWidget(QLabel("HSV Color Visualization"))
        picker_layout.addWidget(self.color_preview)

        # Standard color picker button
        self.picker_button = QPushButton("Pick Color from Standard Dialog")
        picker_layout.addWidget(self.picker_button)

        top_layout.addWidget(picker_frame)

        # Right side - Threshold controls and live preview
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_layout = QVBoxLayout(controls_frame)

        # Selected color display
        controls_layout.addWidget(QLabel("Selected Color:"))
        self.color_sample = QFrame()
        self.color_sample.setFixedSize(100, 50)
        self.color_sample.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.update_color_sample()
        controls_layout.addWidget(self.color_sample)

        # HSV values display
        self.hsv_info = QLabel()
        self.update_hsv_info()
        controls_layout.addWidget(self.hsv_info)

        # Threshold controls
        controls_layout.addWidget(QLabel("HSV Thresholds:"))

        # Hue threshold
        hue_layout = QHBoxLayout()
        hue_layout.addWidget(QLabel("Hue ±"))
        self.hue_spinbox = QSpinBox()
        self.hue_spinbox.setRange(0, 179)
        self.hue_spinbox.setValue(self.hue_threshold)
        hue_layout.addWidget(self.hue_spinbox)
        controls_layout.addLayout(hue_layout)

        # Saturation threshold
        sat_layout = QHBoxLayout()
        sat_layout.addWidget(QLabel("Saturation ±"))
        self.sat_spinbox = QSpinBox()
        self.sat_spinbox.setRange(0, 255)
        self.sat_spinbox.setValue(self.sat_threshold)
        sat_layout.addWidget(self.sat_spinbox)
        controls_layout.addLayout(sat_layout)

        # Value threshold
        val_layout = QHBoxLayout()
        val_layout.addWidget(QLabel("Value ±"))
        self.val_spinbox = QSpinBox()
        self.val_spinbox.setRange(0, 255)
        self.val_spinbox.setValue(self.val_threshold)
        val_layout.addWidget(self.val_spinbox)
        controls_layout.addLayout(val_layout)

        # Range preview
        controls_layout.addWidget(QLabel("Detection Range Preview:"))
        self.range_preview = HSVRangePreviewWidget()
        self.range_preview.setFixedSize(250, 150)
        controls_layout.addWidget(self.range_preview)

        controls_layout.addStretch()
        top_layout.addWidget(controls_frame)

        layout.addLayout(top_layout)

        # Bottom buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Update previews
        self.update_previews()

    def connect_signals(self):
        """Connect UI signals."""
        self.picker_button.clicked.connect(self.open_standard_picker)
        self.hue_spinbox.valueChanged.connect(self.update_thresholds)
        self.sat_spinbox.valueChanged.connect(self.update_thresholds)
        self.val_spinbox.valueChanged.connect(self.update_thresholds)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def open_standard_picker(self):
        """Open standard color picker."""
        color = QColorDialog.getColor(self.selected_color, self, "Select Target Color")
        if color.isValid():
            self.selected_color = color
            self.update_color_sample()
            self.update_hsv_info()
            self.update_previews()

    def update_thresholds(self):
        """Update threshold values from spinboxes."""
        self.hue_threshold = self.hue_spinbox.value()
        self.sat_threshold = self.sat_spinbox.value()
        self.val_threshold = self.val_spinbox.value()
        self.update_previews()

    def update_color_sample(self):
        """Update the color sample display."""
        self.color_sample.setStyleSheet(f"background-color: {self.selected_color.name()}")

    def update_hsv_info(self):
        """Update HSV information display."""
        h, s, v, _ = self.selected_color.getHsv()
        self.hsv_info.setText(f"HSV: H={h}, S={s}, V={v}")

    def update_previews(self):
        """Update all preview widgets."""
        self.color_preview.update_color_and_thresholds(
            self.selected_color, self.hue_threshold, self.sat_threshold, self.val_threshold
        )
        self.range_preview.update_range(
            self.selected_color, self.hue_threshold, self.sat_threshold, self.val_threshold
        )

    def get_result(self):
        """Get the selected color and thresholds."""
        return {
            'color': self.selected_color,
            'hue_threshold': self.hue_threshold,
            'sat_threshold': self.sat_threshold,
            'val_threshold': self.val_threshold
        }


class HSVColorPreviewWidget(QWidget):
    """Widget that shows HSV color wheel with threshold ranges."""

    def __init__(self, color=QColor(255, 0, 0)):
        super().__init__()
        self.color = color
        self.hue_threshold = 20
        self.sat_threshold = 50
        self.val_threshold = 50

    def update_color_and_thresholds(self, color, hue_thresh, sat_thresh, val_thresh):
        """Update color and threshold parameters."""
        self.color = color
        self.hue_threshold = hue_thresh
        self.sat_threshold = sat_thresh
        self.val_threshold = val_thresh
        self.update()

    def paintEvent(self, event):
        """Paint the HSV visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Draw HSV color wheel/rectangle
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 20

        # Get target color HSV
        target_h, target_s, target_v, _ = self.color.getHsv()

        # Draw hue circle
        painter.setPen(QPen(Qt.black, 2))
        for angle in range(0, 360, 2):
            hue_color = QColor.fromHsv(angle, 255, 255)
            painter.setPen(QPen(hue_color, 3))

            # Calculate position on circle
            x = center_x + radius * 0.8 * math.cos(math.radians(angle - 90))
            y = center_y + radius * 0.8 * math.sin(math.radians(angle - 90))
            painter.drawPoint(int(x), int(y))

        # Highlight target hue and range
        painter.setPen(QPen(Qt.white, 4))
        painter.setBrush(QBrush(Qt.transparent))

        # Draw hue range arc
        hue_start = target_h - self.hue_threshold
        hue_end = target_h + self.hue_threshold

        for angle in range(max(0, hue_start), min(360, hue_end + 1), 2):
            x = center_x + radius * 0.8 * math.cos(math.radians(angle - 90))
            y = center_y + radius * 0.8 * math.sin(math.radians(angle - 90))
            painter.drawPoint(int(x), int(y))

        # Draw target color marker

        target_x = center_x + radius * 0.8 * math.cos(math.radians(target_h - 90))
        target_y = center_y + radius * 0.8 * math.sin(math.radians(target_h - 90))
        painter.setPen(QPen(Qt.black, 3))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(int(target_x - 8), int(target_y - 8), 16, 16)

        # Draw saturation and value ranges as rectangles
        sat_rect = QRect(10, height - 60, width - 20, 20)
        val_rect = QRect(10, height - 35, width - 20, 20)

        # Saturation range
        painter.fillRect(sat_rect, QColor(200, 200, 200))
        sat_start = max(0, target_s - self.sat_threshold)
        sat_end = min(255, target_s + self.sat_threshold)
        sat_range_width = (sat_end - sat_start) / 255 * sat_rect.width()
        sat_range_x = sat_start / 255 * sat_rect.width()
        painter.fillRect(int(sat_rect.x() + sat_range_x), sat_rect.y(), int(sat_range_width), sat_rect.height(), QColor(0, 255, 0, 100))

        # Value range
        painter.fillRect(val_rect, QColor(200, 200, 200))
        val_start = max(0, target_v - self.val_threshold)
        val_end = min(255, target_v + self.val_threshold)
        val_range_width = (val_end - val_start) / 255 * val_rect.width()
        val_range_x = val_start / 255 * val_rect.width()
        painter.fillRect(int(val_rect.x() + val_range_x), val_rect.y(), int(val_range_width), val_rect.height(), QColor(0, 255, 0, 100))

        # Labels
        painter.setPen(QPen(Qt.black))
        painter.drawText(10, height - 65, "Saturation Range")
        painter.drawText(10, height - 40, "Value Range")


class HSVRangePreviewWidget(QWidget):
    """Widget that shows color swatches within the HSV range."""

    def __init__(self):
        super().__init__()
        self.color = QColor(255, 0, 0)
        self.hue_threshold = 20
        self.sat_threshold = 50
        self.val_threshold = 50

    def update_range(self, color, hue_thresh, sat_thresh, val_thresh):
        """Update the range parameters."""
        self.color = color
        self.hue_threshold = hue_thresh
        self.sat_threshold = sat_thresh
        self.val_threshold = val_thresh
        self.update()

    def paintEvent(self, event):
        """Paint color swatches showing the detection range."""
        painter = QPainter(self)

        width = self.width()
        height = self.height()

        # Get target HSV
        target_h, target_s, target_v, _ = self.color.getHsv()

        # Calculate ranges
        hue_min = max(0, target_h - self.hue_threshold)
        hue_max = min(359, target_h + self.hue_threshold)
        sat_min = max(0, target_s - self.sat_threshold)
        sat_max = min(255, target_s + self.sat_threshold)
        val_min = max(0, target_v - self.val_threshold)
        val_max = min(255, target_v + self.val_threshold)

        # Draw grid of color samples showing HSV ranges
        cols = 8
        rows = 6
        cell_width = width // cols
        cell_height = height // rows

        for row in range(rows):
            for col in range(cols):
                # Calculate HSV values for this cell
                # Columns represent hue variations
                h = hue_min + (hue_max - hue_min) * col / (cols - 1) if cols > 1 else target_h

                # Rows represent saturation and value combinations
                if row < 3:
                    # Top 3 rows: vary saturation, keep value at target
                    s = sat_min + (sat_max - sat_min) * row / 2 if sat_max > sat_min else target_s
                    v = target_v
                else:
                    # Bottom 3 rows: vary value, keep saturation at target
                    s = target_s
                    v = val_min + (val_max - val_min) * (row - 3) / 2 if val_max > val_min else target_v

                # Ensure values are in valid range
                h = max(0, min(359, int(h)))
                s = max(0, min(255, int(s)))
                v = max(0, min(255, int(v)))

                # Create color and draw cell
                cell_color = QColor.fromHsv(h, s, v)
                painter.fillRect(col * cell_width, row * cell_height, cell_width - 1, cell_height - 1, cell_color)

        # Draw border around target color area
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(0, 0, width - 1, height - 1)

        # Add labels to help users understand the grid
        painter.setPen(QPen(Qt.white, 1))
        painter.drawText(5, 15, "Hue Variations →")

        # Add row labels
        painter.drawText(5, cell_height + 15, "Sat")
        painter.drawText(5, cell_height * 2 + 15, "Range")
        painter.drawText(5, cell_height * 4 + 15, "Val")
        painter.drawText(5, cell_height * 5 + 15, "Range")


class VideoTimelineWidget(QWidget):
    """Video timeline control widget for file playback."""

    playPauseToggled = Signal()
    seekRequested = Signal(float)  # time in seconds
    seekRelative = Signal(float)   # relative seconds
    jumpToBeginning = Signal()
    jumpToEnd = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_time = 0.0
        self.total_time = 0.0
        self.is_playing = True
        self.is_file = False
        self.setup_ui()
        self.connect_signals()
        self.setVisible(False)  # Hidden by default for live streams

    def setup_ui(self):
        """Setup timeline control interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)  # Reduced vertical margins
        layout.setSpacing(3)  # Reduced spacing between elements

        # Main timeline controls
        timeline_layout = QHBoxLayout()
        timeline_layout.setSpacing(5)  # Compact spacing

        # Jump to beginning button
        self.beginning_btn = QPushButton("⟸")
        self.beginning_btn.setFixedSize(28, 28)  # Slightly smaller
        self.beginning_btn.setToolTip("Jump to beginning of video.\n"
                                       "Keyboard shortcut: Home key\n"
                                       "Resets video to first frame")
        timeline_layout.addWidget(self.beginning_btn)

        # Play/Pause button
        self.play_pause_btn = QPushButton("⏸")
        self.play_pause_btn.setFixedSize(35, 28)  # Slightly smaller
        self.play_pause_btn.setToolTip("Play/Pause video playback.\n"
                                        "Keyboard shortcut: Space bar\n"
                                        "Detection continues even when paused")
        timeline_layout.addWidget(self.play_pause_btn)

        # Jump to end button
        self.end_btn = QPushButton("⟹")
        self.end_btn.setFixedSize(28, 28)  # Slightly smaller
        self.end_btn.setToolTip("Jump to end of video.\n"
                                "Keyboard shortcut: End key\n"
                                "Seeks to last frame")
        timeline_layout.addWidget(self.end_btn)

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(1000)  # Use 0-1000 for better precision
        self.timeline_slider.setValue(0)
        self.timeline_slider.setFixedHeight(20)  # Fixed height for compactness
        self.timeline_slider.setToolTip("Video timeline scrubber.\n"
                                        "• Click to jump to specific position\n"
                                        "• Drag to scrub through video\n"
                                        "Only available for file playback sources")
        timeline_layout.addWidget(self.timeline_slider, 1)

        # Time display
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(80)  # Slightly smaller
        self.time_label.setStyleSheet("QLabel { font-family: monospace; font-size: 11px; }")
        self.time_label.setToolTip("Current playback position / Total video duration (MM:SS format)")
        timeline_layout.addWidget(self.time_label)

        layout.addLayout(timeline_layout)

        # Instructions - more compact
        instructions = QLabel("Space=Play/Pause • ←/→=±10s • Home/End=Jump")
        instructions.setStyleSheet("QLabel { font-size: 9px; color: gray; }")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setMaximumHeight(15)  # Limit height
        layout.addWidget(instructions)

    def connect_signals(self):
        """Connect UI signals."""
        self.play_pause_btn.clicked.connect(self.playPauseToggled)
        self.beginning_btn.clicked.connect(self.jumpToBeginning)
        self.end_btn.clicked.connect(self.jumpToEnd)
        self.timeline_slider.sliderPressed.connect(self._on_slider_pressed)
        self.timeline_slider.sliderReleased.connect(self._on_slider_released)

    def _on_slider_pressed(self):
        """Handle slider press - pause updates during dragging."""
        self._dragging = True

    def _on_slider_released(self):
        """Handle slider release - seek to position."""
        self._dragging = False
        if self.total_time > 0:
            # Convert slider position (0-1000) to time
            time_position = (self.timeline_slider.value() / 1000.0) * self.total_time
            self.seekRequested.emit(time_position)

    def update_timeline(self, current_time: float, total_time: float):
        """Update timeline display."""
        self.current_time = current_time
        self.total_time = total_time

        # Update time label
        current_str = self._format_time(current_time)
        total_str = self._format_time(total_time)
        self.time_label.setText(f"{current_str} / {total_str}")

        # Update slider position (only if not dragging)
        if not getattr(self, '_dragging', False) and total_time > 0:
            slider_pos = int((current_time / total_time) * 1000)
            self.timeline_slider.setValue(slider_pos)

    def update_play_state(self, is_playing: bool):
        """Update play/pause button state."""
        self.is_playing = is_playing
        self.play_pause_btn.setText("⏸" if is_playing else "▶")
        self.play_pause_btn.setToolTip("Pause" if is_playing else "Play")

    def set_file_mode(self, is_file: bool):
        """Show/hide timeline for file vs live stream."""
        self.is_file = is_file
        self.setVisible(is_file)

    def _format_time(self, seconds: float) -> str:
        """Format time as MM:SS."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def handle_key_press(self, key):
        """Handle keyboard shortcuts."""
        if not self.is_file:
            return False

        if key == Qt.Key_Space:
            self.playPauseToggled.emit()
            return True
        elif key == Qt.Key_Left:
            self.seekRelative.emit(-10.0)  # Skip back 10 seconds
            return True
        elif key == Qt.Key_Right:
            self.seekRelative.emit(10.0)   # Skip forward 10 seconds
            return True
        elif key == Qt.Key_Home:
            self.jumpToBeginning.emit()
            return True
        elif key == Qt.Key_End:
            self.jumpToEnd.emit()
            return True

        return False


class HSVControlWidget(QWidget):
    """HSV control widget matching ADIAT's existing interface."""

    configChanged = Signal(dict)  # Emitted when configuration changes

    def __init__(self, parent=None):
        super().__init__(parent)

        # Multiple color range support
        self.color_ranges = []  # List of color range dictionaries
        self.current_range_index = 0  # Currently selected/editing range

        # Initialize with one default red range
        self._add_default_range()

        self.setup_ui()
        self.connect_signals()

    def _add_default_range(self):
        """Add default red color range."""
        default_range = {
            'name': 'Red',
            'color': QColor(255, 0, 0),
            'hue_minus': 20,
            'hue_plus': 20,
            'sat_minus': 50,
            'sat_plus': 50,
            'val_minus': 50,
            'val_plus': 50
        }
        self.color_ranges.append(default_range)

    @property
    def selected_color(self):
        """Get currently selected range's color for backward compatibility."""
        if self.color_ranges:
            return self.color_ranges[self.current_range_index]['color']
        return QColor(255, 0, 0)

    @selected_color.setter
    def selected_color(self, color):
        """Set currently selected range's color for backward compatibility."""
        if self.color_ranges:
            self.color_ranges[self.current_range_index]['color'] = color

    def setup_ui(self):
        """Setup the HSV control interface with tabbed organization."""
        layout = QVBoxLayout(self)

        # Create tab widget for organized controls
        self.tabs = QTabWidget()

        # Tab 1: Color Selection
        self.tab_color = self._create_color_tab()
        self.tabs.addTab(self.tab_color, "Color Selection")

        # Tab 2: Detection
        self.tab_detection = self._create_detection_tab()
        self.tabs.addTab(self.tab_detection, "Detection")

        # Tab 3: Processing
        self.tab_processing = self._create_processing_tab()
        self.tabs.addTab(self.tab_processing, "Processing")

        # Tab 4: Motion Detection
        self.tab_motion = self._create_motion_tab()
        self.tabs.addTab(self.tab_motion, "Motion Detection")

        # Tab 5: Fusion & Temporal
        self.tab_fusion = self._create_fusion_tab()
        self.tabs.addTab(self.tab_fusion, "Fusion & Temporal")

        # Tab 6: False Pos. Reduction
        self.tab_fpr = self._create_fpr_tab()
        self.tabs.addTab(self.tab_fpr, "False Pos. Reduction")

        # Tab 7: Rendering
        self.tab_rendering = self._create_rendering_tab()
        self.tabs.addTab(self.tab_rendering, "Rendering")

        layout.addWidget(self.tabs)

    def _create_color_tab(self) -> QWidget:
        """Create Color Selection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # ═══ Color Range List ═══
        range_list_group = QGroupBox("Active Color Ranges (Maximum 3)")
        range_list_group.setToolTip("Manage multiple HSV color ranges for detection.\n"
                                     "Select a range to edit its settings below.")
        range_list_layout = QVBoxLayout(range_list_group)

        # List widget to show all ranges
        self.color_range_list = QListWidget()
        self.color_range_list.setMaximumHeight(120)
        self.color_range_list.setToolTip("Click a color range to select and edit it.\n"
                                          "The selected range's settings appear in the controls below.")
        range_list_layout.addWidget(self.color_range_list)

        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_range_button = QPushButton("+ Add Range")
        self.add_range_button.setToolTip("Add a new color range (maximum 3 ranges)")
        button_layout.addWidget(self.add_range_button)

        self.remove_range_button = QPushButton("− Remove Range")
        self.remove_range_button.setToolTip("Remove the selected color range")
        button_layout.addWidget(self.remove_range_button)
        button_layout.addStretch()

        range_list_layout.addLayout(button_layout)
        layout.addWidget(range_list_group)

        # ═══ Color Range Editor ═══
        editor_label = QLabel("Editing Selected Range:")
        editor_label.setStyleSheet("font-weight: bold; color: #4A9EFF;")
        layout.addWidget(editor_label)

        # Color selection group
        color_group = QGroupBox("Color Selection")
        color_group.setToolTip("Select the target color to detect in the video stream")
        color_layout = QHBoxLayout(color_group)

        # Color picker button
        self.color_button = QPushButton(" Pick Color")
        self.color_button.setMinimumHeight(30)
        self.color_button.setToolTip("Open the advanced HSV color picker to select target color.\n"
                                      "Features visual HSV range preview and live image testing.\n"
                                      "Click to interactively choose colors from video frames.")
        color_layout.addWidget(self.color_button)

        # Color sample display
        self.color_sample = QFrame()
        self.color_sample.setMinimumSize(50, 30)
        self.color_sample.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.color_sample.setStyleSheet("background-color: red")
        self.color_sample.setToolTip("Currently selected target color for detection.\n"
                                      "This swatch shows the exact color being searched for in the video stream.")
        color_layout.addWidget(self.color_sample)

        color_layout.addStretch()
        layout.addWidget(color_group)

        # HSV threshold controls
        threshold_group = QGroupBox("HSV Thresholds")
        threshold_group.setToolTip("Fine-tune color detection by adjusting HSV (Hue, Saturation, Value) ranges.\n"
                                    "Wider ranges detect more color variations but may include false positives.")
        threshold_layout = QGridLayout(threshold_group)

        # Hue threshold
        threshold_layout.addWidget(QLabel("Hue Range:"), 0, 0)
        threshold_layout.addWidget(QLabel("-"), 0, 1)
        self.hue_minus_spinbox = QSpinBox()
        self.hue_minus_spinbox.setRange(0, 179)
        self.hue_minus_spinbox.setValue(20)
        self.hue_minus_spinbox.setToolTip("Lower hue threshold (0-179).\n"
                                          "Hue represents the color on the color wheel:\n"
                                          "• Red: 0-10, 170-179 • Orange: 10-25\n"
                                          "• Yellow: 25-35 • Green: 35-85\n"
                                          "• Cyan: 85-95 • Blue: 95-130\n"
                                          "• Purple: 130-155 • Pink: 155-170\n"
                                          "Lower values = wider color matching")
        threshold_layout.addWidget(self.hue_minus_spinbox, 0, 2)
        threshold_layout.addWidget(QLabel("+"), 0, 3)
        self.hue_plus_spinbox = QSpinBox()
        self.hue_plus_spinbox.setRange(0, 179)
        self.hue_plus_spinbox.setValue(20)
        self.hue_plus_spinbox.setToolTip("Upper hue threshold (0-179).\n"
                                         "Defines how much variation in color hue to accept.\n"
                                         "Higher values = wider color matching range\n"
                                         "Tip: Use asymmetric ranges for better precision")
        threshold_layout.addWidget(self.hue_plus_spinbox, 0, 4)

        # Saturation threshold
        threshold_layout.addWidget(QLabel("Saturation Range:"), 1, 0)
        threshold_layout.addWidget(QLabel("-"), 1, 1)
        self.saturation_minus_spinbox = QSpinBox()
        self.saturation_minus_spinbox.setRange(0, 255)
        self.saturation_minus_spinbox.setValue(50)
        self.saturation_minus_spinbox.setToolTip("Lower saturation threshold (0-255).\n"
                                                  "Saturation is the color intensity/purity:\n"
                                                  "• 0: Gray/white (no color)\n"
                                                  "• 128: Moderate color intensity\n"
                                                  "• 255: Pure, vivid color\n"
                                                  "Lower values include more washed-out colors")
        threshold_layout.addWidget(self.saturation_minus_spinbox, 1, 2)
        threshold_layout.addWidget(QLabel("+"), 1, 3)
        self.saturation_plus_spinbox = QSpinBox()
        self.saturation_plus_spinbox.setRange(0, 255)
        self.saturation_plus_spinbox.setValue(50)
        self.saturation_plus_spinbox.setToolTip("Upper saturation threshold (0-255).\n"
                                                 "Defines range of acceptable color intensity.\n"
                                                 "Higher values include more vivid colors\n"
                                                 "Tip: Decrease for muted/pastel colors")
        threshold_layout.addWidget(self.saturation_plus_spinbox, 1, 4)

        # Value threshold
        threshold_layout.addWidget(QLabel("Value Range:"), 2, 0)
        threshold_layout.addWidget(QLabel("-"), 2, 1)
        self.value_minus_spinbox = QSpinBox()
        self.value_minus_spinbox.setRange(0, 255)
        self.value_minus_spinbox.setValue(50)
        self.value_minus_spinbox.setToolTip("Lower value/brightness threshold (0-255).\n"
                                            "Value represents brightness/lightness:\n"
                                            "• 0: Black (darkest)\n"
                                            "• 128: Medium brightness\n"
                                            "• 255: White (brightest)\n"
                                            "Lower values include darker shades")
        threshold_layout.addWidget(self.value_minus_spinbox, 2, 2)
        threshold_layout.addWidget(QLabel("+"), 2, 3)
        self.value_plus_spinbox = QSpinBox()
        self.value_plus_spinbox.setRange(0, 255)
        self.value_plus_spinbox.setValue(50)
        self.value_plus_spinbox.setToolTip("Upper value/brightness threshold (0-255).\n"
                                           "Defines range of acceptable brightness.\n"
                                           "Higher values include brighter shades\n"
                                           "Tip: Adjust for lighting conditions")
        threshold_layout.addWidget(self.value_plus_spinbox, 2, 4)
        layout.addWidget(threshold_group)
        layout.addStretch()

        return widget

    def _create_detection_tab(self) -> QWidget:
        """Create Detection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Area constraints
        area_group = QGroupBox("Detection Constraints")
        area_group.setToolTip("Filter detections by size to eliminate noise and focus on relevant objects")
        area_layout = QGridLayout(area_group)

        # Minimum area
        area_layout.addWidget(QLabel("Min Area (pixels):"), 0, 0)
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setRange(1, 100000)
        self.min_area_spinbox.setValue(100)
        self.min_area_spinbox.setToolTip("Minimum detection size in pixels (1-100,000).\n"
                                         "Objects smaller than this will be filtered out.\n"
                                         "Use to eliminate noise and small false positives.\n"
                                         "Example: 100 = 10x10 pixel minimum object\n"
                                         "Tip: Increase to focus on larger objects")
        area_layout.addWidget(self.min_area_spinbox, 0, 1)

        # Maximum area
        area_layout.addWidget(QLabel("Max Area (pixels):"), 1, 0)
        self.max_area_spinbox = QSpinBox()
        self.max_area_spinbox.setRange(100, 1000000)
        self.max_area_spinbox.setValue(50000)
        self.max_area_spinbox.setToolTip("Maximum detection size in pixels (100-1,000,000).\n"
                                         "Objects larger than this will be filtered out.\n"
                                         "Use to eliminate large false positives or background.\n"
                                         "Example: 50,000 = approximately 223x223 pixels\n"
                                         "Tip: Decrease to focus on smaller objects")
        area_layout.addWidget(self.max_area_spinbox, 1, 1)
        layout.addWidget(area_group)

        # Confidence threshold
        confidence_group = QGroupBox("Confidence Filtering")
        confidence_group.setToolTip("Filter detections by confidence score")
        confidence_group.setMinimumHeight(120)  # Ensure group box has adequate height
        confidence_layout_main = QVBoxLayout(confidence_group)

        confidence_layout = QGridLayout()
        confidence_layout.addWidget(QLabel("Confidence Threshold:"), 0, 0)
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(0)  # Default: show all detections
        self.confidence_slider.setTickPosition(QSlider.TicksBelow)
        self.confidence_slider.setTickInterval(10)
        self.confidence_slider.setToolTip("Filter detections by confidence score (0-100%).\n"
                                          "• 0%: Show all detections (default)\n"
                                          "• 25%: Filter weak matches\n"
                                          "• 50%: Show medium+ confidence only\n"
                                          "• 75%+: Show high confidence only\n"
                                          "Higher values reduce false positives but may miss valid detections")
        confidence_layout.addWidget(self.confidence_slider, 0, 1)

        self.confidence_label = QLabel("0%")
        self.confidence_label.setStyleSheet("QLabel { font-weight: bold; color: white; }")
        self.confidence_label.setToolTip("Current confidence threshold percentage")
        confidence_layout.addWidget(self.confidence_label, 0, 2)

        # Confidence description
        self.confidence_desc = QLabel("Show all detections")
        self.confidence_desc.setStyleSheet("QLabel { font-size: 10px; color: gray; }")
        self.confidence_desc.setToolTip("Description of current confidence filter behavior")
        confidence_layout.addWidget(self.confidence_desc, 1, 0, 1, 3)

        confidence_layout_main.addLayout(confidence_layout)
        layout.addWidget(confidence_group)

        # Hue Expansion
        hue_group = QGroupBox("Hue Expansion")
        hue_layout = QVBoxLayout(hue_group)

        self.enable_hue_expansion = QCheckBox("Enable Hue Expansion")
        self.enable_hue_expansion.setChecked(False)
        self.enable_hue_expansion.setToolTip("Expands detected colors to include similar hues.\n"
                                              "Groups similar colors together (e.g., red and orange, blue and cyan).\n"
                                              "Helps detect objects even if exact color varies slightly.\n"
                                              "Recommended: OFF for specific colors (e.g., red jacket only),\n"
                                              "ON for color families (e.g., any warm colors).")
        hue_layout.addWidget(self.enable_hue_expansion)

        hue_range_layout = QHBoxLayout()
        hue_range_layout.addWidget(QLabel("Expansion Range:"))
        self.hue_expansion_range = QSlider(Qt.Horizontal)
        self.hue_expansion_range.setRange(0, 30)
        self.hue_expansion_range.setValue(5)
        self.hue_expansion_range.setToolTip("Hue expansion range in OpenCV hue units (0-30, ~0-60 degrees).\n"
                                             "Expands color detection by ±N hue values.\n"
                                             "Larger values = wider color range, detect more variations.\n"
                                             "Smaller values = narrower color range, more specific.\n"
                                             "Recommended: 5 (~10°) for slight variations, 10-15 (~20-30°) for color families.")
        hue_range_layout.addWidget(self.hue_expansion_range)
        self.hue_range_label = QLabel("±5 (~10°)")
        hue_range_layout.addWidget(self.hue_range_label)
        hue_layout.addLayout(hue_range_layout)

        layout.addWidget(hue_group)
        layout.addStretch()

        return widget

    def _create_processing_tab(self) -> QWidget:
        """Create Processing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Processing resolution
        res_group = QGroupBox("Processing Resolution")
        res_group.setToolTip("Configure video processing resolution for performance tuning")
        res_layout = QHBoxLayout(res_group)
        res_layout.addWidget(QLabel("Resolution:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "Original",
            "426x240",
            "640x360",
            "960x540",
            "1280x720",
            "1600x900",
            "1920x1080",
            "2560x1440",
            "3200x1800",
            "3840x2160",
            "5120x2880",
            "7680x4320"
        ])
        self.resolution_combo.setCurrentText("Original")
        self.resolution_combo.setToolTip("Video processing resolution:\n"
                                          "• Original: Process at native resolution (highest quality, slowest)\n"
                                          "• 426x240: 240p - Ultra fast, very low quality\n"
                                          "• 640x360: 360p - Very fast, low quality\n"
                                          "• 960x540: 540p (qHD) - Fast with decent quality\n"
                                          "• 1280x720: 720p HD - Balanced speed and quality\n"
                                          "• 1600x900: 900p HD+ - Good quality, moderate speed\n"
                                          "• 1920x1080: 1080p Full HD - High quality, slower\n"
                                          "• 2560x1440: 1440p QHD - Very high quality, slow\n"
                                          "• 3200x1800: QHD+ - Ultra high quality, very slow\n"
                                          "• 3840x2160: 4K UHD - Maximum quality, extremely slow\n"
                                          "• 5120x2880: 5K - Professional quality\n"
                                          "• 7680x4320: 8K - Cinema quality\n"
                                          "Lower resolutions improve FPS but may miss small objects")
        res_layout.addWidget(self.resolution_combo)
        res_layout.addStretch()
        layout.addWidget(res_group)

        # Performance options
        perf_group = QGroupBox("Performance Options")
        perf_group.setToolTip("Configure performance optimizations")
        perf_layout = QVBoxLayout(perf_group)

        self.threaded_capture_checkbox = QCheckBox("Use Threaded Capture (30-200% FPS boost)")
        self.threaded_capture_checkbox.setChecked(False)
        self.threaded_capture_checkbox.setToolTip("Enables background video decoding in a separate thread.\n"
                                                   "Allows processing to happen in parallel with video capture.\n"
                                                   "Provides 30-200% FPS boost especially for high-resolution videos (2K/4K).\n"
                                                   "Highly recommended for all video sources. No downsides.")
        perf_layout.addWidget(self.threaded_capture_checkbox)

        self.render_at_processing_res_checkbox = QCheckBox("Render at Processing Resolution")
        self.render_at_processing_res_checkbox.setChecked(False)
        self.render_at_processing_res_checkbox.setToolTip("Renders detection overlays at processing resolution instead of original video resolution.\n"
                                                          "Significantly faster for high-resolution videos (1080p+) with minimal visual impact.\n"
                                                          "Example: Processing at 720p but video is 4K - renders at 720p then upscales.\n"
                                                          "Recommended: ON for high-res videos, OFF for native 720p or lower.")
        perf_layout.addWidget(self.render_at_processing_res_checkbox)

        layout.addWidget(perf_group)

        # Processing options
        options_group = QGroupBox("Processing Options")
        options_group.setToolTip("Configure detection processing and acceleration options")
        options_layout = QVBoxLayout(options_group)

        self.morphology_checkbox = QCheckBox("Enable Morphological Filtering")
        self.morphology_checkbox.setChecked(True)
        self.morphology_checkbox.setToolTip("Apply morphological operations to clean up detections.\n"
                                            "Uses opening (erosion + dilation) to:\n"
                                            "• Remove small noise and artifacts\n"
                                            "• Smooth detection boundaries\n"
                                            "• Fill small holes in detected regions\n"
                                            "Recommended: Enabled for cleaner results")
        options_layout.addWidget(self.morphology_checkbox)

        self.gpu_checkbox = QCheckBox("Enable GPU Acceleration")
        self.gpu_checkbox.setChecked(False)
        self.gpu_checkbox.setToolTip("Use GPU for accelerated image processing (requires CUDA).\n"
                                     "Benefits:\n"
                                     "• Significantly faster processing for high-resolution video\n"
                                     "• Better performance with multiple color targets\n"
                                     "Requirements:\n"
                                     "• NVIDIA GPU with CUDA support\n"
                                     "• OpenCV compiled with CUDA support\n"
                                     "Note: May not provide benefit for low-resolution streams")
        options_layout.addWidget(self.gpu_checkbox)

        layout.addWidget(options_group)
        layout.addStretch()

        return widget

    def _create_motion_tab(self) -> QWidget:
        """Create Motion Detection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Motion
        self.motion_enabled_checkbox = QCheckBox("Enable Motion Detection")
        self.motion_enabled_checkbox.setChecked(False)
        self.motion_enabled_checkbox.setToolTip("Detect moving objects by analyzing frame-to-frame differences.\n"
                                                 "Works best for stationary cameras or slow-moving cameras.\n"
                                                 "Automatically pauses when excessive camera movement is detected.\n"
                                                 "Can be combined with Color Detection for more robust detection.")
        layout.addWidget(self.motion_enabled_checkbox)

        # Algorithm Selection
        algo_group = QGroupBox("Algorithm")
        algo_layout = QGridLayout(algo_group)

        algo_layout.addWidget(QLabel("Type:"), 0, 0)
        self.motion_algorithm_combo = QComboBox()
        self.motion_algorithm_combo.addItems(["FRAME_DIFF", "MOG2", "KNN"])
        self.motion_algorithm_combo.setCurrentText("KNN")
        self.motion_algorithm_combo.setToolTip("Motion detection algorithm:\n\n"
                                                "• FRAME_DIFF: Simple frame differencing. Fast, sensitive to all motion.\n"
                                                "  Good for: Quick tests, high-contrast scenes.\n\n"
                                                "• MOG2: Gaussian mixture model (recommended). Adapts to lighting changes.\n"
                                                "  Good for: General use, varying lighting, shadows optional.\n\n"
                                                "• KNN: K-nearest neighbors. More robust to noise than MOG2.\n"
                                                "  Good for: Noisy videos, complex backgrounds.")
        algo_layout.addWidget(self.motion_algorithm_combo, 0, 1)

        layout.addWidget(algo_group)

        # Motion Processing Resolution
        motion_res_group = QGroupBox("Motion Processing Resolution")
        motion_res_group.setToolTip("Separate processing resolution for motion detection.\n"
                                     "Lower resolution = faster motion detection.\n"
                                     "Independent from color detection resolution for optimal performance.")
        motion_res_layout = QHBoxLayout(motion_res_group)
        motion_res_layout.addWidget(QLabel("Resolution:"))
        self.motion_resolution_combo = QComboBox()
        self.motion_resolution_combo.addItems([
            "Same as Color",
            "426x240",
            "640x360",
            "960x540",
            "1280x720",
            "1600x900",
            "1920x1080",
            "2560x1440",
            "3200x1800",
            "3840x2160",
            "5120x2880",
            "7680x4320"
        ])
        self.motion_resolution_combo.setCurrentText("Same as Color")
        self.motion_resolution_combo.setToolTip("Motion detection processing resolution:\n"
                                                 "• Same as Color: Use color detection resolution (default)\n"
                                                 "• 426x240: Ultra fast motion detection (recommended for speed)\n"
                                                 "• 640x360: Very fast, good for most use cases\n"
                                                 "• Higher resolutions: More accurate but slower\n\n"
                                                 "PERFORMANCE TIP: Use low resolution for motion (426x240)\n"
                                                 "and high resolution for color (720p+) for best balance.\n"
                                                 "Example: Motion @ 240p + Color @ 720p = ~2x faster than both @ 720p")
        motion_res_layout.addWidget(self.motion_resolution_combo)
        motion_res_layout.addStretch()
        layout.addWidget(motion_res_group)

        # Detection Parameters
        param_group = QGroupBox("Detection Parameters")
        param_layout = QGridLayout(param_group)

        row = 0
        param_layout.addWidget(QLabel("Motion Threshold:"), row, 0)
        self.motion_threshold_spinbox = QSpinBox()
        self.motion_threshold_spinbox.setRange(1, 255)
        self.motion_threshold_spinbox.setValue(1)
        self.motion_threshold_spinbox.setToolTip("Minimum pixel intensity change to consider as motion (1-255).\n"
                                                  "Lower values = more sensitive, detects subtle motion, more false positives.\n"
                                                  "Higher values = less sensitive, only strong motion, fewer false positives.\n"
                                                  "Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.")
        param_layout.addWidget(self.motion_threshold_spinbox, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Min Area (px):"), row, 0)
        self.motion_min_area_spinbox = QSpinBox()
        self.motion_min_area_spinbox.setRange(1, 100000)
        self.motion_min_area_spinbox.setValue(100)
        self.motion_min_area_spinbox.setToolTip("Minimum detection area in pixels (1-100000).\n"
                                                 "Filters out very small detections (noise, insects, raindrops).\n"
                                                 "Lower values = detect smaller objects, more noise.\n"
                                                 "Higher values = only large objects, less noise.\n"
                                                 "Recommended: 5-10 for person detection, 50-100 for vehicle detection.")
        param_layout.addWidget(self.motion_min_area_spinbox, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Max Area (px):"), row, 0)
        self.motion_max_area_spinbox = QSpinBox()
        self.motion_max_area_spinbox.setRange(10, 1000000)
        self.motion_max_area_spinbox.setValue(1000)
        self.motion_max_area_spinbox.setToolTip("Maximum detection area in pixels (10-1000000).\n"
                                                 "Filters out very large detections (shadows, clouds, global lighting changes).\n"
                                                 "Lower values = only small/medium objects.\n"
                                                 "Higher values = allow large objects.\n"
                                                 "Recommended: 1000 for people, 10000 for vehicles, higher for large objects.")
        param_layout.addWidget(self.motion_max_area_spinbox, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Max Detections:"), row, 0)
        self.max_motion_detections_spinbox = QSpinBox()
        self.max_motion_detections_spinbox.setRange(0, 500)
        self.max_motion_detections_spinbox.setValue(5)
        self.max_motion_detections_spinbox.setToolTip("Maximum number of motion detections to process per frame (0 = unlimited).\n"
                                                       "PERFORMANCE CRITICAL: Limits processing to prevent frame rate drops.\n"
                                                       "When camera pans, entire frame moves creating thousands of detections.\n"
                                                       "This caps processing to keep system responsive.\n"
                                                       "• 0: Unlimited (may cause severe slowdown during camera movement)\n"
                                                       "• 50: Fast, good for real-time tracking of a few objects\n"
                                                       "• 100: Balanced performance (recommended)\n"
                                                       "• 200+: Slower, only use if you need to track many objects\n"
                                                       "Note: Best used WITH 'Pause on Camera Movement' for optimal performance.")
        param_layout.addWidget(self.max_motion_detections_spinbox, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Blur Kernel (odd):"), row, 0)
        self.blur_kernel_size = QSpinBox()
        self.blur_kernel_size.setRange(1, 21)
        self.blur_kernel_size.setSingleStep(2)
        self.blur_kernel_size.setValue(5)
        self.blur_kernel_size.setToolTip("Gaussian blur kernel size (must be odd: 1, 3, 5, 7, etc.).\n"
                                         "Smooths the frame before motion detection to reduce noise.\n"
                                         "Larger values = more smoothing, less noise, less detail.\n"
                                         "Smaller values = less smoothing, more detail, more noise.\n"
                                         "Recommended: 5 for general use, 1 for no blur, 7-9 for noisy videos.")
        param_layout.addWidget(self.blur_kernel_size, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Morphology Kernel:"), row, 0)
        self.morphology_kernel_size = QSpinBox()
        self.morphology_kernel_size.setRange(1, 21)
        self.morphology_kernel_size.setSingleStep(2)
        self.morphology_kernel_size.setValue(3)
        self.morphology_kernel_size.setToolTip("Morphological operation kernel size (odd numbers: 1, 3, 5, etc.).\n"
                                                "Removes small noise and fills holes in detections.\n"
                                                "Larger values = remove more noise, merge nearby detections.\n"
                                                "Smaller values = preserve detail, keep detections separate.\n"
                                                "Recommended: 3 for general use, 1 for precise edges, 5-7 for noisy videos.")
        param_layout.addWidget(self.morphology_kernel_size, row, 1)

        layout.addWidget(param_group)

        # Persistence Filter
        persist_group = QGroupBox("Persistence Filter")
        persist_layout = QGridLayout(persist_group)

        persist_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.persistence_frames = QSpinBox()
        self.persistence_frames.setRange(2, 30)
        self.persistence_frames.setValue(15)
        self.persistence_frames.setToolTip("Size of temporal window for persistence filtering (2-30 frames).\n"
                                            "Motion must appear in N out of M consecutive frames to be confirmed.\n"
                                            "Larger values = longer memory, more stable, slower response.\n"
                                            "Smaller values = shorter memory, faster response, more flicker.\n"
                                            "Recommended: 3 for 30fps video (100ms window), 5 for 60fps.")
        persist_layout.addWidget(self.persistence_frames, 0, 1)

        persist_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.persistence_threshold = QSpinBox()
        self.persistence_threshold.setRange(1, 30)
        self.persistence_threshold.setValue(7)
        self.persistence_threshold.setToolTip("Number of frames within window where motion must appear (N of M).\n"
                                               "Higher values = more stringent, filters flickering false positives.\n"
                                               "Lower values = more lenient, detects brief/intermittent motion.\n"
                                               "Must be ≤ Window Frames.\n"
                                               "Recommended: 2 (motion in 2 of last 3 frames)")
        persist_layout.addWidget(self.persistence_threshold, 1, 1)

        layout.addWidget(persist_group)

        # Background Subtraction
        bg_group = QGroupBox("Background Subtraction (MOG2/KNN)")
        bg_layout = QGridLayout(bg_group)

        bg_layout.addWidget(QLabel("History Frames:"), 0, 0)
        self.bg_history = QSpinBox()
        self.bg_history.setRange(10, 500)
        self.bg_history.setValue(20)
        self.bg_history.setToolTip("Number of frames to learn background model (10-500).\n"
                                    "Only applies to MOG2 and KNN algorithms.\n"
                                    "Longer history = adapts slower to lighting changes, more stable.\n"
                                    "Shorter history = adapts faster, less stable.\n"
                                    "Recommended: 50 (~1.7 sec at 30fps) for general use.")
        bg_layout.addWidget(self.bg_history, 0, 1)

        bg_layout.addWidget(QLabel("Variance Threshold:"), 1, 0)
        self.bg_var_threshold = QDoubleSpinBox()
        self.bg_var_threshold.setRange(1.0, 100.0)
        self.bg_var_threshold.setValue(20.0)
        self.bg_var_threshold.setToolTip("Variance threshold for background/foreground classification (1.0-100.0).\n"
                                          "Only applies to MOG2 and KNN algorithms.\n"
                                          "Lower values = more sensitive, detects subtle changes, more false positives.\n"
                                          "Higher values = less sensitive, only strong foreground objects.\n"
                                          "Recommended: 10.0 for indoor, 15-20 for outdoor with varying lighting.")
        bg_layout.addWidget(self.bg_var_threshold, 1, 1)

        self.bg_detect_shadows = QCheckBox("Detect Shadows (slower)")
        self.bg_detect_shadows.setToolTip("Enables shadow detection in MOG2 background subtractor.\n"
                                           "Helps distinguish shadows from actual objects (reduces false positives).\n"
                                           "Adds ~10-20% processing overhead.\n"
                                           "Recommended: ON for outdoor scenes with strong shadows, OFF for speed.")
        bg_layout.addWidget(self.bg_detect_shadows, 2, 0, 1, 2)

        layout.addWidget(bg_group)

        # Camera Movement
        cam_group = QGroupBox("Camera Movement Detection")
        cam_layout = QVBoxLayout(cam_group)

        self.pause_on_camera_movement = QCheckBox("Pause on Camera Movement")
        self.pause_on_camera_movement.setChecked(True)
        self.pause_on_camera_movement.setToolTip("Automatically pauses motion detection when camera is moving/panning.\n"
                                                  "Prevents false positives caused by camera movement (entire scene appears to move).\n"
                                                  "Detects camera movement by measuring percentage of frame with motion.\n"
                                                  "Recommended: ON for handheld/drone footage, OFF for stationary tripod cameras.")
        cam_layout.addWidget(self.pause_on_camera_movement)

        cam_thresh_layout = QHBoxLayout()
        cam_thresh_layout.addWidget(QLabel("Threshold:"))
        self.camera_movement_threshold = QSlider(Qt.Horizontal)
        self.camera_movement_threshold.setRange(1, 100)
        self.camera_movement_threshold.setValue(1)
        self.camera_movement_threshold.setToolTip("Percentage of frame with motion to consider as camera movement (1-100%).\n"
                                                   "If more than this % of pixels show motion, pause detection.\n"
                                                   "Lower values = detect camera movement sooner (more pauses).\n"
                                                   "Higher values = tolerate more motion before pausing (fewer pauses).\n"
                                                   "Recommended: 15% for drone/handheld, 30% for shaky tripod.")
        cam_thresh_layout.addWidget(self.camera_movement_threshold)
        self.camera_movement_label = QLabel("1%")
        cam_thresh_layout.addWidget(self.camera_movement_label)
        cam_layout.addLayout(cam_thresh_layout)

        layout.addWidget(cam_group)

        # Motion Confidence Threshold
        motion_conf_group = QGroupBox("Motion Confidence Filtering")
        motion_conf_group.setToolTip("Filter motion detections by confidence score (separate from color detection confidence)")
        motion_conf_group.setMinimumHeight(120)
        motion_conf_layout_main = QVBoxLayout(motion_conf_group)

        motion_conf_layout = QGridLayout()
        motion_conf_layout.addWidget(QLabel("Motion Confidence:"), 0, 0)
        self.motion_confidence_slider = QSlider(Qt.Horizontal)
        self.motion_confidence_slider.setRange(0, 100)
        self.motion_confidence_slider.setValue(0)  # Default: show all motion detections
        self.motion_confidence_slider.setTickPosition(QSlider.TicksBelow)
        self.motion_confidence_slider.setTickInterval(10)
        self.motion_confidence_slider.setToolTip("Filter motion detections by confidence score (0-100%).\n"
                                                  "Confidence is based on detection area relative to max area.\n"
                                                  "• 0%: Show all motion detections (default)\n"
                                                  "• 25%: Filter weak motion matches\n"
                                                  "• 50%: Show medium+ confidence only\n"
                                                  "• 75%+: Show high confidence only\n"
                                                  "Higher values reduce false positives but may miss valid motion.\n"
                                                  "This is separate from the Color Detection confidence threshold.")
        motion_conf_layout.addWidget(self.motion_confidence_slider, 0, 1)

        self.motion_confidence_label = QLabel("0%")
        self.motion_confidence_label.setStyleSheet("QLabel { font-weight: bold; color: white; }")
        self.motion_confidence_label.setToolTip("Current motion confidence threshold percentage")
        motion_conf_layout.addWidget(self.motion_confidence_label, 0, 2)

        # Motion confidence description
        self.motion_confidence_desc = QLabel("Show all motion detections")
        self.motion_confidence_desc.setStyleSheet("QLabel { font-size: 10px; color: gray; }")
        self.motion_confidence_desc.setToolTip("Description of current motion confidence filter behavior")
        motion_conf_layout.addWidget(self.motion_confidence_desc, 1, 0, 1, 3)

        motion_conf_layout_main.addLayout(motion_conf_layout)
        layout.addWidget(motion_conf_group)
        layout.addStretch()

        return widget

    def _create_fusion_tab(self) -> QWidget:
        """Create Fusion & Temporal tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Detection Fusion
        fusion_group = QGroupBox("Detection Fusion")
        fusion_group.setToolTip("Combine color and motion detections")
        fusion_layout = QVBoxLayout(fusion_group)

        self.fusion_enabled_checkbox = QCheckBox("Enable Detection Fusion")
        self.fusion_enabled_checkbox.setChecked(False)
        self.fusion_enabled_checkbox.setToolTip("Enable fusion to combine color and motion detections")
        fusion_layout.addWidget(self.fusion_enabled_checkbox)

        fusion_mode_layout = QHBoxLayout()
        fusion_mode_layout.addWidget(QLabel("Mode:"))
        self.fusion_mode_combo = QComboBox()
        self.fusion_mode_combo.addItems(["Union", "Intersection", "Color Priority", "Motion Priority"])
        self.fusion_mode_combo.setCurrentText("Union")
        self.fusion_mode_combo.setToolTip("Fusion mode:\n"
                                           "• Union: All detections, merge overlapping\n"
                                           "• Intersection: Only detections in both\n"
                                           "• Color Priority: Color + non-overlapping motion\n"
                                           "• Motion Priority: Motion + non-overlapping color")
        fusion_mode_layout.addWidget(self.fusion_mode_combo)
        fusion_mode_layout.addStretch()
        fusion_layout.addLayout(fusion_mode_layout)
        layout.addWidget(fusion_group)

        # Temporal Voting
        temporal_group = QGroupBox("Temporal Voting")
        temporal_group.setToolTip("Filter out transient detections by requiring consistency across frames")
        temporal_layout = QVBoxLayout(temporal_group)

        self.temporal_enabled_checkbox = QCheckBox("Enable Temporal Voting")
        self.temporal_enabled_checkbox.setChecked(False)
        self.temporal_enabled_checkbox.setToolTip("Enable temporal voting to filter transient detections")
        temporal_layout.addWidget(self.temporal_enabled_checkbox)

        temporal_params_layout = QGridLayout()
        temporal_params_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.temporal_window_spinbox = QSpinBox()
        self.temporal_window_spinbox.setRange(2, 10)
        self.temporal_window_spinbox.setValue(3)
        self.temporal_window_spinbox.setToolTip("Number of frames to track in history")
        temporal_params_layout.addWidget(self.temporal_window_spinbox, 0, 1)

        temporal_params_layout.addWidget(QLabel("Threshold Frames (N):"), 1, 0)
        self.temporal_threshold_spinbox = QSpinBox()
        self.temporal_threshold_spinbox.setRange(1, 10)
        self.temporal_threshold_spinbox.setValue(2)
        self.temporal_threshold_spinbox.setToolTip("Detections must appear in N frames to be valid")
        temporal_params_layout.addWidget(self.temporal_threshold_spinbox, 1, 1)

        temporal_layout.addLayout(temporal_params_layout)
        layout.addWidget(temporal_group)
        layout.addStretch()

        return widget

    def _create_fpr_tab(self) -> QWidget:
        """Create False Positive Reduction tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Aspect Ratio Filter
        aspect_group = QGroupBox("Aspect Ratio Filter")
        aspect_layout = QVBoxLayout(aspect_group)

        self.enable_aspect_ratio_filter = QCheckBox("Enable Aspect Ratio Filtering")
        self.enable_aspect_ratio_filter.setChecked(False)  # Default OFF
        self.enable_aspect_ratio_filter.setToolTip("Filters detections based on aspect ratio (width/height).\n"
                                                    "Removes very thin/elongated detections (wires, shadows, cracks).\n"
                                                    "Useful for filtering non-object shapes.\n"
                                                    "Recommended: OFF by default, ON if many thin false positives.")
        aspect_layout.addWidget(self.enable_aspect_ratio_filter)

        ratio_layout = QGridLayout()
        ratio_layout.addWidget(QLabel("Min Ratio:"), 0, 0)
        self.min_aspect_ratio = QDoubleSpinBox()
        self.min_aspect_ratio.setRange(0.1, 10.0)
        self.min_aspect_ratio.setValue(0.2)
        self.min_aspect_ratio.setSingleStep(0.1)
        self.min_aspect_ratio.setToolTip("Minimum aspect ratio (width/height) to keep (0.1-10.0).\n"
                                          "Rejects very tall/thin vertical detections.\n"
                                          "Example: 0.2 = reject if height > 5× width.\n"
                                          "Lower values = allow thinner objects.\n"
                                          "Recommended: 0.2 for filtering poles/wires, 0.5 for people.")
        ratio_layout.addWidget(self.min_aspect_ratio, 0, 1)

        ratio_layout.addWidget(QLabel("Max Ratio:"), 1, 0)
        self.max_aspect_ratio = QDoubleSpinBox()
        self.max_aspect_ratio.setRange(0.1, 20.0)
        self.max_aspect_ratio.setValue(5.0)
        self.max_aspect_ratio.setSingleStep(0.1)
        self.max_aspect_ratio.setToolTip("Maximum aspect ratio (width/height) to keep (0.1-20.0).\n"
                                          "Rejects very wide/thin horizontal detections.\n"
                                          "Example: 5.0 = reject if width > 5× height.\n"
                                          "Higher values = allow wider objects.\n"
                                          "Recommended: 5.0 for filtering shadows/lines, 10.0 for vehicles.")
        ratio_layout.addWidget(self.max_aspect_ratio, 1, 1)

        aspect_layout.addLayout(ratio_layout)
        layout.addWidget(aspect_group)

        # Detection Clustering (moved from rendering tab)
        cluster_group = QGroupBox("Detection Clustering")
        cluster_layout = QVBoxLayout(cluster_group)

        self.clustering_enabled_checkbox = QCheckBox("Enable Detection Clustering")
        self.clustering_enabled_checkbox.setChecked(False)  # Default OFF
        self.clustering_enabled_checkbox.setToolTip("Combines nearby detections into single merged detection.\n"
                                                     "Groups detections whose centroids are within specified distance.\n"
                                                     "Merged detection encompasses all combined contours.\n"
                                                     "Useful for: Combining scattered patches of same object.\n"
                                                     "Recommended: OFF by default, ON if objects appear fragmented.")
        cluster_layout.addWidget(self.clustering_enabled_checkbox)

        cluster_dist_layout = QGridLayout()
        cluster_dist_layout.addWidget(QLabel("Clustering Distance (px):"), 0, 0)
        self.clustering_distance_spinbox = QSpinBox()
        self.clustering_distance_spinbox.setRange(0, 500)
        self.clustering_distance_spinbox.setValue(50)  # Default 50px
        self.clustering_distance_spinbox.setToolTip("Maximum centroid distance to merge detections (0-500 pixels).\n"
                                                     "Detections closer than this distance are combined into one.\n"
                                                     "Lower values = only merge very close detections.\n"
                                                     "Higher values = merge distant detections (may over-merge).\n"
                                                     "Recommended: 50px for people, 100px for vehicles at 720p.")
        cluster_dist_layout.addWidget(self.clustering_distance_spinbox, 0, 1)

        cluster_layout.addLayout(cluster_dist_layout)
        layout.addWidget(cluster_group)

        layout.addStretch()

        return widget

    def _create_rendering_tab(self) -> QWidget:
        """Create Rendering tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Shape Options
        shape_group = QGroupBox("Shape Options")
        shape_layout = QGridLayout(shape_group)

        shape_layout.addWidget(QLabel("Shape Mode:"), 0, 0)
        self.render_shape_combo = QComboBox()
        self.render_shape_combo.addItems(["Box", "Circle", "Dot", "Off"])
        self.render_shape_combo.setCurrentText("Circle")
        self.render_shape_combo.setToolTip("Shape to draw around detections:\n\n"
                                            "• Box: Rectangle around detection bounding box.\n"
                                            "  Use for: Precise boundaries, technical visualization.\n\n"
                                            "• Circle: Circle encompassing detection (150% of contour radius).\n"
                                            "  Use for: General use, cleaner look (default).\n\n"
                                            "• Dot: Small dot at detection centroid.\n"
                                            "  Use for: Minimal overlay, fast rendering.\n\n"
                                            "• Off: No shape overlay (only thumbnails/text if enabled).\n"
                                            "  Use for: Clean video with minimal overlays.")
        shape_layout.addWidget(self.render_shape_combo, 0, 1)

        layout.addWidget(shape_group)

        # Text & Contours
        vis_group = QGroupBox("Visual Options")
        vis_layout = QVBoxLayout(vis_group)

        self.render_text_checkbox = QCheckBox("Show Text Labels (slower)")
        self.render_text_checkbox.setToolTip("Displays text labels near detections showing detection information.\n"
                                              "Adds ~5-15ms processing overhead depending on detection count.\n"
                                              "Labels show: detection type, confidence, area.\n"
                                              "Recommended: OFF for speed, ON for debugging/analysis.")
        vis_layout.addWidget(self.render_text_checkbox)

        self.render_contours_checkbox = QCheckBox("Show Contours (slowest)")
        self.render_contours_checkbox.setToolTip("Draws exact detection contours (pixel-precise boundaries).\n"
                                                  "Adds ~10-20ms processing overhead (very expensive).\n"
                                                  "Shows exact shape detected by algorithm.\n"
                                                  "Recommended: OFF for speed, ON only for detailed analysis.")
        vis_layout.addWidget(self.render_contours_checkbox)

        self.use_detection_color = QCheckBox("Use Detection Color (hue @ 100% sat/val for detected colors)")
        self.use_detection_color.setChecked(True)  # Default ON
        self.use_detection_color.setToolTip("Color the detection overlay based on detected color.\n"
                                              "For color detections: Uses the detected hue at 100% saturation/value.\n"
                                              "For motion detections: Uses default color (green/blue).\n"
                                              "Helps visually identify what color was detected.\n"
                                              "Recommended: ON for color detection, OFF for motion-only.")
        vis_layout.addWidget(self.use_detection_color)

        layout.addWidget(vis_group)

        # Detection Limits
        limit_group = QGroupBox("Performance Limits")
        limit_layout = QGridLayout(limit_group)

        limit_layout.addWidget(QLabel("Max Detections:"), 0, 0)
        self.max_detections_spinbox = QSpinBox()
        self.max_detections_spinbox.setRange(0, 1000)
        self.max_detections_spinbox.setValue(100)
        self.max_detections_spinbox.setSpecialValueText("Unlimited")
        self.max_detections_spinbox.setToolTip("Maximum number of detections to render on screen (0-1000).\n"
                                                 "Prevents rendering slowdown when hundreds of detections occur.\n"
                                                 "Shows highest confidence detections first.\n"
                                                 "0 = Unlimited (may cause lag with many detections).\n"
                                                 "Recommended: 100 for general use, 50 for complex rendering (text+contours).")
        limit_layout.addWidget(self.max_detections_spinbox, 0, 1)

        layout.addWidget(limit_group)

        # Overlay Options
        overlay_group = QGroupBox("Overlay Options")
        overlay_layout = QVBoxLayout(overlay_group)

        self.show_timing_overlay_checkbox = QCheckBox("Show Timing Overlay (FPS, metrics)")
        self.show_timing_overlay_checkbox.setChecked(False)  # Default OFF
        self.show_timing_overlay_checkbox.setToolTip("Displays detailed timing information on video overlay.\n"
                                                      "Shows: FPS, processing time, detection counts, pipeline breakdown.\n"
                                                      "Useful for performance tuning and debugging.\n"
                                                      "Recommended: OFF for clean view, ON when optimizing performance.")
        overlay_layout.addWidget(self.show_timing_overlay_checkbox)

        self.show_detections_checkbox = QCheckBox("Show Detections")
        self.show_detections_checkbox.setChecked(True)  # Default ON
        self.show_detections_checkbox.setToolTip("Toggle detection rendering on/off.\n"
                                                  "When OFF, no detection overlays are shown (clean video).\n"
                                                  "Recommended: ON for analysis, OFF for clean recording.")
        overlay_layout.addWidget(self.show_detections_checkbox)

        layout.addWidget(overlay_group)
        layout.addStretch()

        return widget

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.color_button.clicked.connect(self.select_color)
        self.hue_minus_spinbox.valueChanged.connect(self.emit_config)
        self.hue_plus_spinbox.valueChanged.connect(self.emit_config)
        self.saturation_minus_spinbox.valueChanged.connect(self.emit_config)
        self.saturation_plus_spinbox.valueChanged.connect(self.emit_config)
        self.value_minus_spinbox.valueChanged.connect(self.emit_config)
        self.value_plus_spinbox.valueChanged.connect(self.emit_config)
        self.min_area_spinbox.valueChanged.connect(self.emit_config)
        self.max_area_spinbox.valueChanged.connect(self.emit_config)
        self.resolution_combo.currentTextChanged.connect(self.emit_config)
        self.confidence_slider.valueChanged.connect(self.update_confidence_threshold)
        self.morphology_checkbox.toggled.connect(self.emit_config)
        self.gpu_checkbox.toggled.connect(self.emit_config)
        self.threaded_capture_checkbox.toggled.connect(self.emit_config)
        self.render_at_processing_res_checkbox.toggled.connect(self.emit_config)

        # Hue expansion signals
        self.enable_hue_expansion.toggled.connect(self.emit_config)
        self.hue_expansion_range.valueChanged.connect(self.update_hue_expansion_label)

        # Motion detection signals
        self.motion_enabled_checkbox.toggled.connect(self.emit_config)
        self.motion_algorithm_combo.currentTextChanged.connect(self.emit_config)
        self.motion_resolution_combo.currentTextChanged.connect(self.emit_config)
        self.motion_min_area_spinbox.valueChanged.connect(self.emit_config)
        self.motion_max_area_spinbox.valueChanged.connect(self.emit_config)
        self.max_motion_detections_spinbox.valueChanged.connect(self.emit_config)
        self.motion_threshold_spinbox.valueChanged.connect(self.emit_config)
        self.blur_kernel_size.valueChanged.connect(self.emit_config)
        self.morphology_kernel_size.valueChanged.connect(self.emit_config)
        self.persistence_frames.valueChanged.connect(self.emit_config)
        self.persistence_threshold.valueChanged.connect(self.emit_config)
        self.bg_history.valueChanged.connect(self.emit_config)
        self.bg_var_threshold.valueChanged.connect(self.emit_config)
        self.bg_detect_shadows.toggled.connect(self.emit_config)
        self.pause_on_camera_movement.toggled.connect(self.emit_config)
        self.camera_movement_threshold.valueChanged.connect(self.update_camera_movement_label)
        self.motion_confidence_slider.valueChanged.connect(self.update_motion_confidence_threshold)

        # Temporal voting signals
        self.temporal_enabled_checkbox.toggled.connect(self.emit_config)
        self.temporal_window_spinbox.valueChanged.connect(self.emit_config)
        self.temporal_threshold_spinbox.valueChanged.connect(self.emit_config)

        # Clustering signals
        self.clustering_enabled_checkbox.toggled.connect(self.emit_config)
        self.clustering_distance_spinbox.valueChanged.connect(self.emit_config)

        # Fusion signals
        self.fusion_enabled_checkbox.toggled.connect(self.emit_config)
        self.fusion_mode_combo.currentTextChanged.connect(self.emit_config)

        # False Positive Reduction signals
        self.enable_aspect_ratio_filter.toggled.connect(self.emit_config)
        self.min_aspect_ratio.valueChanged.connect(self.emit_config)
        self.max_aspect_ratio.valueChanged.connect(self.emit_config)

        # Rendering signals
        self.render_shape_combo.currentTextChanged.connect(self.emit_config)
        self.render_text_checkbox.toggled.connect(self.emit_config)
        self.render_contours_checkbox.toggled.connect(self.emit_config)
        self.use_detection_color.toggled.connect(self.emit_config)
        self.max_detections_spinbox.valueChanged.connect(self.emit_config)
        self.show_timing_overlay_checkbox.toggled.connect(self.emit_config)
        self.show_detections_checkbox.toggled.connect(self.emit_config)

        # Color range list signals
        self.color_range_list.currentRowChanged.connect(self.on_range_selected)
        self.add_range_button.clicked.connect(self.add_color_range)
        self.remove_range_button.clicked.connect(self.remove_color_range)

        # HSV spinbox signals to update current range
        self.hue_minus_spinbox.valueChanged.connect(self.update_current_range_values)
        self.hue_plus_spinbox.valueChanged.connect(self.update_current_range_values)
        self.saturation_minus_spinbox.valueChanged.connect(self.update_current_range_values)
        self.saturation_plus_spinbox.valueChanged.connect(self.update_current_range_values)
        self.value_minus_spinbox.valueChanged.connect(self.update_current_range_values)
        self.value_plus_spinbox.valueChanged.connect(self.update_current_range_values)

        # Initial list population
        self.refresh_range_list()
        self.color_range_list.setCurrentRow(0)

    # ═══════════════════════════════════════════════════════════════════════
    # COLOR RANGE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════

    def refresh_range_list(self):
        """Refresh the color range list widget with current ranges."""
        self.color_range_list.clear()
        for i, range_data in enumerate(self.color_ranges):
            color = range_data['color']
            name = range_data['name']
            h, s, v, _ = color.getHsvF()

            # Format HSV summary
            hsv_summary = (f"H:{int(h*179)}±{range_data['hue_minus']}/{range_data['hue_plus']}, "
                          f"S:{int(s*255)}±{range_data['sat_minus']}/{range_data['sat_plus']}, "
                          f"V:{int(v*255)}±{range_data['val_minus']}/{range_data['val_plus']}")

            # Create list item with color swatch
            item_text = f"  {name}   ({hsv_summary})"
            item = QListWidgetItem(item_text)

            # Set background color swatch
            item.setBackground(color)
            # Set text color to contrast with background
            brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
            text_color = QColor(0, 0, 0) if brightness > 128 else QColor(255, 255, 255)
            item.setForeground(text_color)

            self.color_range_list.addItem(item)

        # Update button states
        self.add_range_button.setEnabled(len(self.color_ranges) < 3)
        self.remove_range_button.setEnabled(len(self.color_ranges) > 1)

    def on_range_selected(self, index: int):
        """Handle selection of a color range from the list."""
        if index < 0 or index >= len(self.color_ranges):
            return

        self.current_range_index = index
        range_data = self.color_ranges[index]

        # Block signals to avoid triggering config updates while loading
        self.hue_minus_spinbox.blockSignals(True)
        self.hue_plus_spinbox.blockSignals(True)
        self.saturation_minus_spinbox.blockSignals(True)
        self.saturation_plus_spinbox.blockSignals(True)
        self.value_minus_spinbox.blockSignals(True)
        self.value_plus_spinbox.blockSignals(True)

        # Load range values into controls
        self.hue_minus_spinbox.setValue(range_data['hue_minus'])
        self.hue_plus_spinbox.setValue(range_data['hue_plus'])
        self.saturation_minus_spinbox.setValue(range_data['sat_minus'])
        self.saturation_plus_spinbox.setValue(range_data['sat_plus'])
        self.value_minus_spinbox.setValue(range_data['val_minus'])
        self.value_plus_spinbox.setValue(range_data['val_plus'])

        # Update color button and sample
        self.update_color_button()

        # Unblock signals
        self.hue_minus_spinbox.blockSignals(False)
        self.hue_plus_spinbox.blockSignals(False)
        self.saturation_minus_spinbox.blockSignals(False)
        self.saturation_plus_spinbox.blockSignals(False)
        self.value_minus_spinbox.blockSignals(False)
        self.value_plus_spinbox.blockSignals(False)

    def update_current_range_values(self):
        """Update current range's values from spinboxes."""
        if not self.color_ranges:
            return

        range_data = self.color_ranges[self.current_range_index]
        range_data['hue_minus'] = self.hue_minus_spinbox.value()
        range_data['hue_plus'] = self.hue_plus_spinbox.value()
        range_data['sat_minus'] = self.saturation_minus_spinbox.value()
        range_data['sat_plus'] = self.saturation_plus_spinbox.value()
        range_data['val_minus'] = self.value_minus_spinbox.value()
        range_data['val_plus'] = self.value_plus_spinbox.value()

        # Refresh list to show updated values
        current_row = self.color_range_list.currentRow()
        self.refresh_range_list()
        self.color_range_list.setCurrentRow(current_row)

    def add_color_range(self):
        """Add a new color range."""
        if len(self.color_ranges) >= 3:
            return

        # Default colors for new ranges
        default_colors = [
            ('Red', QColor(255, 0, 0)),
            ('Green', QColor(0, 255, 0)),
            ('Blue', QColor(0, 0, 255)),
            ('Yellow', QColor(255, 255, 0)),
            ('Cyan', QColor(0, 255, 255)),
            ('Magenta', QColor(255, 0, 255))
        ]

        # Pick a color that's not already used
        used_names = [r['name'] for r in self.color_ranges]
        for name, color in default_colors:
            if name not in used_names:
                new_range = {
                    'name': name,
                    'color': color,
                    'hue_minus': 20,
                    'hue_plus': 20,
                    'sat_minus': 50,
                    'sat_plus': 50,
                    'val_minus': 50,
                    'val_plus': 50
                }
                self.color_ranges.append(new_range)
                break

        # Refresh list and select new range
        self.refresh_range_list()
        self.color_range_list.setCurrentRow(len(self.color_ranges) - 1)
        self.emit_config()

    def remove_color_range(self):
        """Remove the selected color range."""
        if len(self.color_ranges) <= 1:
            return  # Must keep at least one range

        current_row = self.color_range_list.currentRow()
        if current_row >= 0:
            self.color_ranges.pop(current_row)

            # Select previous range or first if we removed the first
            new_index = max(0, current_row - 1)
            self.current_range_index = new_index

            self.refresh_range_list()
            self.color_range_list.setCurrentRow(new_index)
            self.emit_config()

    def get_color_name_from_hsv(self, color: QColor) -> str:
        """Determine color name from HSV values.

        Args:
            color: QColor object

        Returns:
            String color name (e.g., 'Red', 'Green', 'Blue', etc.)
        """
        h, s, v, _ = color.getHsvF()

        # Convert to 0-360 range for easier interpretation
        hue = int(h * 360)
        sat = int(s * 255)
        val = int(v * 255)

        # Handle grayscale colors (low saturation)
        if sat < 30:
            if val < 50:
                return 'Black'
            elif val > 200:
                return 'White'
            else:
                return 'Gray'

        # Handle low value (dark colors)
        if val < 50:
            return 'Black'

        # Determine color based on hue (0-360)
        # Red wraps around (330-360 and 0-10)
        if hue >= 330 or hue < 10:
            return 'Red'
        elif 10 <= hue < 25:
            return 'Orange'
        elif 25 <= hue < 45:
            return 'Yellow'
        elif 45 <= hue < 80:
            return 'Yellow-Green'
        elif 80 <= hue < 150:
            return 'Green'
        elif 150 <= hue < 170:
            return 'Cyan'
        elif 170 <= hue < 200:
            return 'Light Blue'
        elif 200 <= hue < 260:
            return 'Blue'
        elif 260 <= hue < 290:
            return 'Purple'
        elif 290 <= hue < 320:
            return 'Magenta'
        elif 320 <= hue < 330:
            return 'Pink'
        else:
            return 'Unknown'

    def select_color(self):
        """Open advanced HSV color picker dialog."""
        try:
            from algorithms.HSVColorRange.views.color_range_dialog import ColorRangeDialog

            # Get current range data directly (not from spinboxes which may be stale)
            range_data = self.color_ranges[self.current_range_index]

            # Prepare initial values from stored range_data
            h, s, v, _ = range_data['color'].getHsvF()
            initial_hsv = (h, s, v)

            # Convert stored ranges to 0-1 format for dialog
            h_minus_range = range_data['hue_minus'] / 179  # OpenCV hue range 0-179
            h_plus_range = range_data['hue_plus'] / 179
            s_minus_range = range_data['sat_minus'] / 255  # OpenCV saturation range 0-255
            s_plus_range = range_data['sat_plus'] / 255
            v_minus_range = range_data['val_minus'] / 255  # OpenCV value range 0-255
            v_plus_range = range_data['val_plus'] / 255

            initial_ranges = {
                'h_minus': h_minus_range, 'h_plus': h_plus_range,
                's_minus': s_minus_range, 's_plus': s_plus_range,
                'v_minus': v_minus_range, 'v_plus': v_plus_range
            }

            # Create dialog with image preview if available
            current_frame = getattr(self, 'current_frame', None)
            dialog = ColorRangeDialog(current_frame, initial_hsv, initial_ranges, self)

            if dialog.exec() == QDialog.Accepted:
                hsv_data = dialog.get_hsv_ranges()

                # Update color from dialog
                h, s, v = hsv_data['h'], hsv_data['s'], hsv_data['v']
                picked_color = QColor.fromHsvF(h, s, v)

                # Save to current range data
                range_data['color'] = picked_color
                range_data['name'] = self.get_color_name_from_hsv(picked_color)  # Auto-update name
                range_data['hue_minus'] = int(hsv_data['h_minus'] * 179)
                range_data['hue_plus'] = int(hsv_data['h_plus'] * 179)
                range_data['sat_minus'] = int(hsv_data['s_minus'] * 255)
                range_data['sat_plus'] = int(hsv_data['s_plus'] * 255)
                range_data['val_minus'] = int(hsv_data['v_minus'] * 255)
                range_data['val_plus'] = int(hsv_data['v_plus'] * 255)

                # Update UI to reflect saved changes
                self.color_sample.setStyleSheet(f"background-color: {picked_color.name()}")

                # Block signals while updating spinboxes to prevent feedback loops
                self.hue_minus_spinbox.blockSignals(True)
                self.hue_plus_spinbox.blockSignals(True)
                self.saturation_minus_spinbox.blockSignals(True)
                self.saturation_plus_spinbox.blockSignals(True)
                self.value_minus_spinbox.blockSignals(True)
                self.value_plus_spinbox.blockSignals(True)

                # Update spinboxes to match saved range_data
                self.hue_minus_spinbox.setValue(range_data['hue_minus'])
                self.hue_plus_spinbox.setValue(range_data['hue_plus'])
                self.saturation_minus_spinbox.setValue(range_data['sat_minus'])
                self.saturation_plus_spinbox.setValue(range_data['sat_plus'])
                self.value_minus_spinbox.setValue(range_data['val_minus'])
                self.value_plus_spinbox.setValue(range_data['val_plus'])

                # Unblock signals
                self.hue_minus_spinbox.blockSignals(False)
                self.hue_plus_spinbox.blockSignals(False)
                self.saturation_minus_spinbox.blockSignals(False)
                self.saturation_plus_spinbox.blockSignals(False)
                self.value_minus_spinbox.blockSignals(False)
                self.value_plus_spinbox.blockSignals(False)

                # Refresh list to show new color
                current_row = self.color_range_list.currentRow()
                self.refresh_range_list()
                self.color_range_list.setCurrentRow(current_row)

                self.emit_config()

        except ImportError:
            # Fallback to old dialog if new one is not available
            # Get values from stored range_data, not spinboxes
            range_data = self.color_ranges[self.current_range_index]
            avg_hue = int((range_data['hue_minus'] + range_data['hue_plus']) / 2)
            avg_sat = int((range_data['sat_minus'] + range_data['sat_plus']) / 2)
            avg_val = int((range_data['val_minus'] + range_data['val_plus']) / 2)

            dialog = HSVColorPickerDialog(
                initial_color=self.selected_color,
                hue_threshold=avg_hue,
                sat_threshold=avg_sat,
                val_threshold=avg_val,
                parent=self
            )

            if dialog.exec() == QDialog.Accepted:
                result = dialog.get_result()

                # Save to current range
                range_data = self.color_ranges[self.current_range_index]
                range_data['color'] = result['color']
                range_data['name'] = self.get_color_name_from_hsv(result['color'])  # Auto-update name
                range_data['hue_minus'] = result['hue_threshold']
                range_data['hue_plus'] = result['hue_threshold']
                range_data['sat_minus'] = result['sat_threshold']
                range_data['sat_plus'] = result['sat_threshold']
                range_data['val_minus'] = result['val_threshold']
                range_data['val_plus'] = result['val_threshold']

                # Update UI
                self.color_sample.setStyleSheet(f"background-color: {result['color'].name()}")

                # Block signals while updating spinboxes to prevent feedback loops
                self.hue_minus_spinbox.blockSignals(True)
                self.hue_plus_spinbox.blockSignals(True)
                self.saturation_minus_spinbox.blockSignals(True)
                self.saturation_plus_spinbox.blockSignals(True)
                self.value_minus_spinbox.blockSignals(True)
                self.value_plus_spinbox.blockSignals(True)

                # Update spinboxes
                self.hue_minus_spinbox.setValue(result['hue_threshold'])
                self.hue_plus_spinbox.setValue(result['hue_threshold'])
                self.saturation_minus_spinbox.setValue(result['sat_threshold'])
                self.saturation_plus_spinbox.setValue(result['sat_threshold'])
                self.value_minus_spinbox.setValue(result['val_threshold'])
                self.value_plus_spinbox.setValue(result['val_threshold'])

                # Unblock signals
                self.hue_minus_spinbox.blockSignals(False)
                self.hue_plus_spinbox.blockSignals(False)
                self.saturation_minus_spinbox.blockSignals(False)
                self.saturation_plus_spinbox.blockSignals(False)
                self.value_minus_spinbox.blockSignals(False)
                self.value_plus_spinbox.blockSignals(False)

                # Refresh list
                current_row = self.color_range_list.currentRow()
                self.refresh_range_list()
                self.color_range_list.setCurrentRow(current_row)

                self.emit_config()

    def update_confidence_threshold(self):
        """Handle confidence threshold slider changes."""
        value = self.confidence_slider.value()
        self.confidence_label.setText(f"{value}%")

        # Update description based on value
        if value == 0:
            self.confidence_desc.setText("Show all detections")
        elif value < 25:
            self.confidence_desc.setText("Show most detections")
        elif value < 50:
            self.confidence_desc.setText("Show medium+ confidence")
        elif value < 75:
            self.confidence_desc.setText("Show high confidence only")
        else:
            self.confidence_desc.setText("Show highest confidence only")

        self.emit_config()

    def update_motion_confidence_threshold(self):
        """Handle motion confidence threshold slider changes."""
        value = self.motion_confidence_slider.value()
        self.motion_confidence_label.setText(f"{value}%")

        # Update description based on value
        if value == 0:
            self.motion_confidence_desc.setText("Show all motion detections")
        elif value < 25:
            self.motion_confidence_desc.setText("Show most motion detections")
        elif value < 50:
            self.motion_confidence_desc.setText("Show medium+ confidence motion")
        elif value < 75:
            self.motion_confidence_desc.setText("Show high confidence motion only")
        else:
            self.motion_confidence_desc.setText("Show highest confidence motion only")

        self.emit_config()

    def update_hue_expansion_label(self):
        """Handle hue expansion range slider changes."""
        value = self.hue_expansion_range.value()
        degrees = value * 2  # OpenCV hue is 0-179, full circle is 360°
        self.hue_range_label.setText(f"±{value} (~{degrees}°)")
        self.emit_config()

    def update_camera_movement_label(self):
        """Handle camera movement threshold slider changes."""
        value = self.camera_movement_threshold.value()
        self.camera_movement_label.setText(f"{value}%")
        self.emit_config()

    def update_color_button(self):
        """Update color button and sample to reflect currently selected range."""
        if not self.color_ranges:
            return

        range_data = self.color_ranges[self.current_range_index]
        color = range_data['color']

        # Update color sample background
        self.color_sample.setStyleSheet(f"background-color: {color.name()}")

    def emit_config(self):
        """Emit current configuration."""
        # Create HSV ranges data for all color ranges
        hsv_ranges_list = []
        for range_data in self.color_ranges:
            color = range_data['color']
            h, s, v, _ = color.getHsvF()
            hsv_ranges_list.append({
                'h': h, 's': s, 'v': v,
                'h_minus': range_data['hue_minus'] / 179,
                'h_plus': range_data['hue_plus'] / 179,
                's_minus': range_data['sat_minus'] / 255,
                's_plus': range_data['sat_plus'] / 255,
                'v_minus': range_data['val_minus'] / 255,
                'v_plus': range_data['val_plus'] / 255,
                'name': range_data['name']
            })

        # For backward compatibility, use first range
        hsv_ranges = hsv_ranges_list[0] if hsv_ranges_list else None

        # Parse processing resolution (for color detection)
        processing_resolution = None
        resolution_text = self.resolution_combo.currentText()
        if resolution_text != "Original":
            # Parse "WIDTHxHEIGHT" format (e.g., "1920x1080")
            try:
                parts = resolution_text.lower().split('x')
                if len(parts) == 2:
                    width = int(parts[0])
                    height = int(parts[1])
                    processing_resolution = (width, height)
            except (ValueError, IndexError):
                self.logger.warning(f"Invalid resolution format: {resolution_text}")

        # Parse motion processing resolution (separate from color)
        motion_processing_resolution = None
        motion_resolution_text = self.motion_resolution_combo.currentText()
        if motion_resolution_text != "Same as Color":
            # Parse "WIDTHxHEIGHT" format
            try:
                parts = motion_resolution_text.lower().split('x')
                if len(parts) == 2:
                    width = int(parts[0])
                    height = int(parts[1])
                    motion_processing_resolution = (width, height)
            except (ValueError, IndexError):
                self.logger.warning(f"Invalid motion resolution format: {motion_resolution_text}")

        # Parse motion algorithm
        motion_algorithm = MotionAlgorithm.FRAME_DIFF
        if self.motion_algorithm_combo.currentText() == "MOG2":
            motion_algorithm = MotionAlgorithm.MOG2
        elif self.motion_algorithm_combo.currentText() == "KNN":
            motion_algorithm = MotionAlgorithm.KNN

        # Parse fusion mode
        fusion_mode = FusionMode.UNION
        if self.fusion_mode_combo.currentText() == "Intersection":
            fusion_mode = FusionMode.INTERSECTION
        elif self.fusion_mode_combo.currentText() == "Color Priority":
            fusion_mode = FusionMode.COLOR_PRIORITY
        elif self.fusion_mode_combo.currentText() == "Motion Priority":
            fusion_mode = FusionMode.MOTION_PRIORITY

        # Parse render shape
        render_shape = 0  # Box (default)
        if self.render_shape_combo.currentText() == "Circle":
            render_shape = 1
        elif self.render_shape_combo.currentText() == "Dot":
            render_shape = 2
        elif self.render_shape_combo.currentText() == "Off":
            render_shape = 3

        config = {
            'target_color_rgb': (self.selected_color.red(), self.selected_color.green(), self.selected_color.blue()),
            'hsv_ranges': hsv_ranges,  # First range for backward compatibility
            'hsv_ranges_list': hsv_ranges_list,  # All ranges for multi-color detection
            # For backward compatibility, provide average values from first range
            'hue_threshold': int((self.color_ranges[0]['hue_minus'] + self.color_ranges[0]['hue_plus']) / 2) if self.color_ranges else 20,
            'saturation_threshold': int((self.color_ranges[0]['sat_minus'] + self.color_ranges[0]['sat_plus']) / 2) if self.color_ranges else 50,
            'value_threshold': int((self.color_ranges[0]['val_minus'] + self.color_ranges[0]['val_plus']) / 2) if self.color_ranges else 50,
            'min_area': self.min_area_spinbox.value(),
            'max_area': self.max_area_spinbox.value(),
            'processing_resolution': processing_resolution,
            'confidence_threshold': self.confidence_slider.value() / 100.0,  # Convert to 0-1 range
            'morphology_enabled': self.morphology_checkbox.isChecked(),
            'gpu_acceleration': self.gpu_checkbox.isChecked(),
            'show_labels': True,  # Legacy parameter, always enabled
            'use_threaded_capture': self.threaded_capture_checkbox.isChecked(),

            # Hue expansion
            'enable_hue_expansion': self.enable_hue_expansion.isChecked(),
            'hue_expansion_range': self.hue_expansion_range.value(),

            # Motion detection
            'enable_motion_detection': self.motion_enabled_checkbox.isChecked(),
            'motion_algorithm': motion_algorithm,
            'min_detection_area': self.motion_min_area_spinbox.value(),
            'max_detection_area': self.motion_max_area_spinbox.value(),
            'motion_threshold': self.motion_threshold_spinbox.value(),
            'blur_kernel_size': self.blur_kernel_size.value(),
            'morphology_kernel_size': self.morphology_kernel_size.value(),
            'persistence_frames': self.persistence_frames.value(),
            'persistence_threshold': self.persistence_threshold.value(),
            'bg_history': self.bg_history.value(),
            'bg_var_threshold': self.bg_var_threshold.value(),
            'bg_detect_shadows': self.bg_detect_shadows.isChecked(),
            'pause_on_camera_movement': self.pause_on_camera_movement.isChecked(),
            'camera_movement_threshold': self.camera_movement_threshold.value() / 100.0,  # Convert to 0-1

            # Temporal voting
            'enable_temporal_voting': self.temporal_enabled_checkbox.isChecked(),
            'temporal_window_frames': self.temporal_window_spinbox.value(),
            'temporal_threshold_frames': self.temporal_threshold_spinbox.value(),

            # Clustering
            'enable_detection_clustering': self.clustering_enabled_checkbox.isChecked(),
            'clustering_distance': float(self.clustering_distance_spinbox.value()),

            # Fusion
            'enable_detection_fusion': self.fusion_enabled_checkbox.isChecked(),
            'fusion_mode': fusion_mode,

            # False Positive Reduction
            'enable_aspect_ratio_filter': self.enable_aspect_ratio_filter.isChecked(),
            'min_aspect_ratio': self.min_aspect_ratio.value(),
            'max_aspect_ratio': self.max_aspect_ratio.value(),

            # Rendering options
            'render_shape': render_shape,
            'render_text': self.render_text_checkbox.isChecked(),
            'render_contours': self.render_contours_checkbox.isChecked(),
            'use_detection_color_for_rendering': self.use_detection_color.isChecked(),
            'render_at_processing_res': self.render_at_processing_res_checkbox.isChecked(),
            'max_detections_to_render': self.max_detections_spinbox.value(),
            'show_timing_overlay': self.show_timing_overlay_checkbox.isChecked(),
            'show_detections': self.show_detections_checkbox.isChecked()
        }
        self.configChanged.emit(config)

    def get_hsv_config(self) -> HSVConfig:
        """Get current configuration as HSVConfig object."""
        # Create HSV ranges data for all color ranges
        hsv_ranges_list = []
        for range_data in self.color_ranges:
            color = range_data['color']
            h, s, v, _ = color.getHsvF()
            hsv_ranges_list.append({
                'h': h, 's': s, 'v': v,
                'h_minus': range_data['hue_minus'] / 179,
                'h_plus': range_data['hue_plus'] / 179,
                's_minus': range_data['sat_minus'] / 255,
                's_plus': range_data['sat_plus'] / 255,
                'v_minus': range_data['val_minus'] / 255,
                'v_plus': range_data['val_plus'] / 255,
                'name': range_data['name']
            })

        # For backward compatibility, use first range
        hsv_ranges = hsv_ranges_list[0] if hsv_ranges_list else None

        # Parse processing resolution (for color detection)
        processing_resolution = None
        resolution_text = self.resolution_combo.currentText()
        if resolution_text != "Original":
            # Parse "WIDTHxHEIGHT" format (e.g., "1920x1080")
            try:
                parts = resolution_text.lower().split('x')
                if len(parts) == 2:
                    width = int(parts[0])
                    height = int(parts[1])
                    processing_resolution = (width, height)
            except (ValueError, IndexError):
                self.logger.warning(f"Invalid resolution format: {resolution_text}")

        # Parse motion processing resolution (separate from color)
        motion_processing_resolution = None
        motion_resolution_text = self.motion_resolution_combo.currentText()
        if motion_resolution_text != "Same as Color":
            # Parse "WIDTHxHEIGHT" format
            try:
                parts = motion_resolution_text.lower().split('x')
                if len(parts) == 2:
                    width = int(parts[0])
                    height = int(parts[1])
                    motion_processing_resolution = (width, height)
            except (ValueError, IndexError):
                self.logger.warning(f"Invalid motion resolution format: {motion_resolution_text}")

        # Parse motion algorithm
        motion_algorithm = MotionAlgorithm.FRAME_DIFF
        if self.motion_algorithm_combo.currentText() == "MOG2":
            motion_algorithm = MotionAlgorithm.MOG2
        elif self.motion_algorithm_combo.currentText() == "KNN":
            motion_algorithm = MotionAlgorithm.KNN

        # Parse fusion mode
        fusion_mode = FusionMode.UNION
        if self.fusion_mode_combo.currentText() == "Intersection":
            fusion_mode = FusionMode.INTERSECTION
        elif self.fusion_mode_combo.currentText() == "Color Priority":
            fusion_mode = FusionMode.COLOR_PRIORITY
        elif self.fusion_mode_combo.currentText() == "Motion Priority":
            fusion_mode = FusionMode.MOTION_PRIORITY

        # Parse render shape
        render_shape = 0  # Box (default)
        if self.render_shape_combo.currentText() == "Circle":
            render_shape = 1
        elif self.render_shape_combo.currentText() == "Dot":
            render_shape = 2
        elif self.render_shape_combo.currentText() == "Off":
            render_shape = 3

        return HSVConfig(
            target_color_rgb=(self.selected_color.red(), self.selected_color.green(), self.selected_color.blue()),
            # For backward compatibility, provide average values from first range
            hue_threshold=int((self.color_ranges[0]['hue_minus'] + self.color_ranges[0]['hue_plus']) / 2) if self.color_ranges else 20,
            saturation_threshold=int((self.color_ranges[0]['sat_minus'] + self.color_ranges[0]['sat_plus']) / 2) if self.color_ranges else 50,
            value_threshold=int((self.color_ranges[0]['val_minus'] + self.color_ranges[0]['val_plus']) / 2) if self.color_ranges else 50,
            min_area=self.min_area_spinbox.value(),
            max_area=self.max_area_spinbox.value(),
            processing_resolution=processing_resolution,
            motion_processing_resolution=motion_processing_resolution,
            confidence_threshold=self.confidence_slider.value() / 100.0,
            morphology_enabled=self.morphology_checkbox.isChecked(),
            gpu_acceleration=self.gpu_checkbox.isChecked(),
            show_labels=True,  # Legacy parameter, always enabled
            hsv_ranges=hsv_ranges,  # First range for backward compatibility
            hsv_ranges_list=hsv_ranges_list,  # All ranges for multi-color detection
            use_threaded_capture=self.threaded_capture_checkbox.isChecked(),

            # Hue expansion
            enable_hue_expansion=self.enable_hue_expansion.isChecked(),
            hue_expansion_range=self.hue_expansion_range.value(),

            # Motion detection
            enable_motion_detection=self.motion_enabled_checkbox.isChecked(),
            motion_algorithm=motion_algorithm,
            min_detection_area=self.motion_min_area_spinbox.value(),
            max_detection_area=self.motion_max_area_spinbox.value(),
            max_motion_detections=self.max_motion_detections_spinbox.value(),
            motion_threshold=self.motion_threshold_spinbox.value(),
            blur_kernel_size=self.blur_kernel_size.value(),
            morphology_kernel_size=self.morphology_kernel_size.value(),
            persistence_frames=self.persistence_frames.value(),
            persistence_threshold=self.persistence_threshold.value(),
            bg_history=self.bg_history.value(),
            bg_var_threshold=self.bg_var_threshold.value(),
            bg_detect_shadows=self.bg_detect_shadows.isChecked(),
            pause_on_camera_movement=self.pause_on_camera_movement.isChecked(),
            camera_movement_threshold=self.camera_movement_threshold.value() / 100.0,  # Convert to 0-1
            motion_confidence_threshold=self.motion_confidence_slider.value() / 100.0,  # Convert to 0-1

            # Temporal voting
            enable_temporal_voting=self.temporal_enabled_checkbox.isChecked(),
            temporal_window_frames=self.temporal_window_spinbox.value(),
            temporal_threshold_frames=self.temporal_threshold_spinbox.value(),

            # Detection clustering
            enable_detection_clustering=self.clustering_enabled_checkbox.isChecked(),
            clustering_distance=float(self.clustering_distance_spinbox.value()),

            # Detection fusion
            enable_detection_fusion=self.fusion_enabled_checkbox.isChecked(),
            fusion_mode=fusion_mode,

            # False Positive Reduction
            enable_aspect_ratio_filter=self.enable_aspect_ratio_filter.isChecked(),
            min_aspect_ratio=self.min_aspect_ratio.value(),
            max_aspect_ratio=self.max_aspect_ratio.value(),

            # Rendering options
            render_shape=render_shape,
            render_text=self.render_text_checkbox.isChecked(),
            render_contours=self.render_contours_checkbox.isChecked(),
            use_detection_color_for_rendering=self.use_detection_color.isChecked(),
            render_at_processing_res=self.render_at_processing_res_checkbox.isChecked(),
            max_detections_to_render=self.max_detections_spinbox.value(),
            show_timing_overlay=self.show_timing_overlay_checkbox.isChecked(),
            show_detections=self.show_detections_checkbox.isChecked()
        )


class StreamControlWidget(QWidget):
    """Stream connection and control widget."""

    connectRequested = Signal(str, str)  # url, stream_type
    disconnectRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.connect_button.setToolTip("Connect to the specified video source and begin processing.\n"
                                        "Color detection will start automatically upon successful connection.")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setToolTip("Disconnect from the current video source and stop processing.\n"
                                           "Any active recording will be stopped automatically.")

        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        # Status display
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        self.status_label.setToolTip("Current connection status:\n"
                                      "• Disconnected: No active video source\n"
                                      "• Connected: Streaming and processing video\n"
                                      "• Error: Connection problem or stream interrupted")

        # Performance display
        performance_group = QGroupBox("Performance")
        performance_group.setToolTip("Real-time performance metrics for video processing and color detection")
        performance_layout = QGridLayout(performance_group)

        self.fps_label = QLabel("FPS: --")
        self.fps_label.setToolTip("Frames per second being processed from the video stream.\n"
                                   "Lower FPS may indicate system load or slow stream.")
        self.latency_label = QLabel("Processing: -- ms")
        self.latency_label.setToolTip("Time in milliseconds to process each frame including color detection.\n"
                                       "Lower values indicate better real-time performance.\n"
                                       "Target: <50ms for smooth real-time detection")
        self.detections_label = QLabel("Detections: --")
        self.detections_label.setToolTip("Number of color matches found in the current frame.\n"
                                          "Adjust HSV thresholds and area constraints to refine detections.")

        performance_layout.addWidget(self.fps_label, 0, 0)
        performance_layout.addWidget(self.latency_label, 0, 1)
        performance_layout.addWidget(self.detections_label, 1, 0)

        # Add to main layout
        layout.addWidget(connection_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(performance_group)
        layout.addStretch()

    def connect_signals(self):
        """Connect UI signals."""
        self.connect_button.clicked.connect(self.request_connect)
        self.disconnect_button.clicked.connect(self.disconnectRequested.emit)
        self.type_combo.currentTextChanged.connect(self.on_stream_type_changed)
        self.browse_button.clicked.connect(self.browse_for_file)
        self.url_input.mousePressEvent = self.on_url_input_clicked

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
            self.url_input.setPlaceholderText("rtmp://server:port/app/stream or http://user:pass@host:port/stream")
            self.url_input.setText("")
            self.browse_button.setVisible(False)

    def request_connect(self):
        """Request stream connection."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid stream URL.")
            return

        stream_type = self.type_combo.currentText().lower()
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

    def update_performance(self, stats: Dict[str, Any]):
        """Update performance display."""
        fps = stats.get('fps', 0)
        processing_time = stats.get('current_processing_time_ms', 0)
        detection_count = stats.get('detection_count', 0)

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


class RTMPColorDetectionViewer(QMainWindow):
    """Main RTMP color detection viewer window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Core services
        self.stream_manager = StreamManager()
        self.color_detector = RealtimeColorDetector()
        self.recording_manager = RecordingManager("./recordings")

        # UI components
        self.video_display = None
        self.hsv_controls = None
        self.stream_controls = None
        self.recording_controls = None

        # State
        self.is_detecting = False
        self.is_recording = False
        self.current_detections = []
        self.current_frame = None
        self.stream_resolution = (640, 480)

        self.setup_ui()
        self.connect_signals()

        self.logger.info("RTMP Color Detection Viewer initialized")

    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("ADIAT - Real-Time Color Detection")
        self.setMinimumSize(1200, 800)

        # Set custom tooltip styling - light blue background with black text
        self.setStyleSheet("""
            QToolTip {
                background-color: lightblue;
                color: black;
                border: 1px solid #333333;
                padding: 4px;
                font-size: 11px;
            }
        """)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)

        # Video display area
        video_widget = QWidget()
        video_layout = QVBoxLayout(video_widget)

        self.video_display = VideoDisplayWidget()
        self.video_display.setToolTip("Live video stream with color detection visualization.\n"
                                       "Detected objects are highlighted with:\n"
                                       "• Green bounding boxes around matches\n"
                                       "• Detection ID and area labels (if enabled)\n"
                                       "• Confidence scores for each detection\n"
                                       "The display automatically scales to fit the window")
        video_layout.addWidget(self.video_display, 1)  # Give video display stretch factor of 1

        # Timeline controls (for file playback) - fixed size, no stretch
        self.timeline_widget = VideoTimelineWidget()
        self.timeline_widget.setMaximumHeight(80)  # Limit timeline height
        self.timeline_widget.setToolTip("Video playback controls (for file sources only).\n"
                                        "Keyboard shortcuts:\n"
                                        "• Space: Play/Pause\n"
                                        "• Left Arrow: Skip back 10 seconds\n"
                                        "• Right Arrow: Skip forward 10 seconds\n"
                                        "• Home: Jump to beginning\n"
                                        "• End: Jump to end")
        video_layout.addWidget(self.timeline_widget, 0)  # No stretch - stays compact

        # Detection thumbnails - fixed size, no stretch
        self.thumbnail_widget = DetectionThumbnailWidget()
        self.thumbnail_widget.setToolTip("Detection thumbnails showing zoomed views of detected objects.\n"
                                         "• Automatically tracks detections across frames\n"
                                         "• Thumbnails persist for ~2 seconds even if detection disappears\n"
                                         "• Number of thumbnails adjusts based on window width\n"
                                         "• Sorted left-to-right by position in frame")
        video_layout.addWidget(self.thumbnail_widget, 0)  # No stretch - stays fixed size

        # Detection info panel - fixed size, no stretch
        info_panel = QTextEdit()
        info_panel.setMaximumHeight(150)
        info_panel.setMinimumHeight(150)  # Prevent shrinking too much
        info_panel.setReadOnly(True)
        info_panel.setPlaceholderText("Detection information will appear here...")
        info_panel.setToolTip("Detailed detection information panel.\n"
                              "Shows for each detection:\n"
                              "• Detection number and position (x, y coordinates)\n"
                              "• Size dimensions (width × height in pixels)\n"
                              "• Total area in pixels\n"
                              "• Confidence score (0.0-1.0)\n"
                              "Displays up to 5 detections at a time")
        video_layout.addWidget(info_panel, 0)  # No stretch - stays fixed size
        self.info_panel = info_panel

        # Control panel
        control_widget = QWidget()
        control_widget.setMaximumWidth(350)
        control_layout = QVBoxLayout(control_widget)

        # Stream controls
        self.stream_controls = StreamControlWidget()
        control_layout.addWidget(self.stream_controls)

        # HSV controls
        self.hsv_controls = HSVControlWidget()
        control_layout.addWidget(self.hsv_controls)

        # Recording controls
        self.recording_controls = self._create_recording_controls()
        control_layout.addWidget(self.recording_controls)

        # Add to splitter
        splitter.addWidget(video_widget)
        splitter.addWidget(control_widget)
        splitter.setSizes([800, 400])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Connect to stream to begin detection")

    def _create_recording_controls(self) -> QWidget:
        """Create recording control widget."""
        group = QGroupBox("Recording")
        group.setToolTip("Record video stream with detection annotations to file")
        layout = QVBoxLayout(group)

        # Recording buttons
        button_layout = QHBoxLayout()
        self.start_recording_btn = QPushButton("Start Recording")
        self.start_recording_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-weight: bold; }")
        self.start_recording_btn.setToolTip("Start recording the video stream with detection overlays.\n"
                                            "Recordings are saved to the ./recordings directory.\n"
                                            "File format: MP4 with H.264 codec\n"
                                            "Note: Connect to stream before recording")
        self.stop_recording_btn = QPushButton("Stop Recording")
        self.stop_recording_btn.setEnabled(False)
        self.stop_recording_btn.setToolTip("Stop the current recording and save to file.\n"
                                           "The file path will be displayed in the status label.\n"
                                           "Recording includes all detection annotations and labels")

        button_layout.addWidget(self.start_recording_btn)
        button_layout.addWidget(self.stop_recording_btn)

        # Recording status
        self.recording_status = QLabel("Status: Not Recording")
        self.recording_status.setStyleSheet("QLabel { color: gray; }")
        self.recording_status.setToolTip("Current recording status and output file path")

        # Recording info
        self.recording_info = QLabel("Duration: --")
        self.recording_info.setToolTip("Recording statistics:\n"
                                       "• Duration: Total recording time in seconds\n"
                                       "• FPS: Recording frame rate\n"
                                       "• Frames: Total frames written to file")

        layout.addLayout(button_layout)
        layout.addWidget(self.recording_status)
        layout.addWidget(self.recording_info)

        # Connect signals
        self.start_recording_btn.clicked.connect(self.start_recording)
        self.stop_recording_btn.clicked.connect(self.stop_recording)

        return group

    def connect_signals(self):
        """Connect all signals and slots."""
        # Stream manager signals
        self.stream_manager.frameReceived.connect(self.process_frame)
        self.stream_manager.connectionChanged.connect(self.on_connection_changed)
        self.stream_manager.statsUpdated.connect(self.on_stream_stats)
        self.stream_manager.videoPositionChanged.connect(self.on_video_position_changed)

        # Color detector signals
        self.color_detector.detectionsReady.connect(self.on_detections_ready)
        self.color_detector.performanceUpdate.connect(self.on_performance_update)

        # Recording manager signals
        self.recording_manager.recordingStateChanged.connect(self.on_recording_state_changed)
        self.recording_manager.recordingStats.connect(self.on_recording_stats)

        # UI control signals
        self.stream_controls.connectRequested.connect(self.connect_to_stream)
        self.stream_controls.disconnectRequested.connect(self.disconnect_from_stream)
        self.hsv_controls.configChanged.connect(self.update_detection_config)

        # Timeline control signals
        self.timeline_widget.playPauseToggled.connect(self.toggle_play_pause)
        self.timeline_widget.seekRequested.connect(self.seek_to_time)
        self.timeline_widget.seekRelative.connect(self.seek_relative)
        self.timeline_widget.jumpToBeginning.connect(self.jump_to_beginning)
        self.timeline_widget.jumpToEnd.connect(self.jump_to_end)

    def connect_to_stream(self, url: str, stream_type_str: str):
        """Connect to RTMP stream."""
        try:
            # Convert string to enum
            stream_type = StreamType.RTMP
            if stream_type_str.lower() == 'hls':
                stream_type = StreamType.HLS
            elif stream_type_str.lower() == 'file':
                stream_type = StreamType.FILE
            elif stream_type_str.lower() == 'hdmi capture':
                stream_type = StreamType.HDMI_CAPTURE
            elif stream_type_str.lower() == 'rtmp stream':
                stream_type = StreamType.RTMP

            success = self.stream_manager.connect_to_stream(url, stream_type)
            if success:
                self.is_detecting = True
                self.status_bar.showMessage(f"Connecting to {url}...")
                # Update detector with current config
                self.update_detection_config()

                # Update timeline widget based on stream type
                self.timeline_widget.set_file_mode(stream_type == StreamType.FILE)
            else:
                QMessageBox.critical(self, "Connection Failed", "Failed to initiate stream connection.")

        except Exception as e:
            self.logger.error(f"Error connecting to stream: {e}")
            QMessageBox.critical(self, "Connection Error", f"Error connecting to stream:\n{str(e)}")

    def disconnect_from_stream(self):
        """Disconnect from current stream."""
        self.stream_manager.disconnect_stream()
        self.is_detecting = False
        self.video_display.setText("No Stream Connected")
        self.info_panel.clear()
        self.thumbnail_widget.clear_thumbnails()
        self.status_bar.showMessage("Disconnected")

    def update_detection_config(self):
        """Update color detection configuration."""
        config = self.hsv_controls.get_hsv_config()
        self.color_detector.update_config(config)

    def process_frame(self, frame: np.ndarray, timestamp: float):
        """Process incoming frame from stream."""
        if not self.is_detecting:
            return

        try:
            # Validate frame first
            if frame is None or frame.size == 0:
                self.logger.warning("Received invalid frame")
                return

            # Create a working copy to prevent memory issues
            working_frame = frame.copy()

            # Perform color detection with timeout protection
            try:
                detections = self.color_detector.detect_colors(working_frame, timestamp)
            except Exception as e:
                self.logger.error(f"Color detection failed: {e}")
                detections = []

            # Create annotated frame
            try:
                annotated_frame = self.color_detector.create_annotated_frame(working_frame, detections)
            except Exception as e:
                self.logger.error(f"Frame annotation failed: {e}")
                annotated_frame = working_frame  # Use original frame if annotation fails

            # Update display
            try:
                self.video_display.update_frame(annotated_frame)
            except Exception as e:
                self.logger.error(f"Display update failed: {e}")

            # Store current detections and frame
            self.current_detections = detections
            self.current_frame = working_frame

            # Update stream resolution for recording
            try:
                height, width = working_frame.shape[:2]
                self.stream_resolution = (width, height)
            except Exception as e:
                self.logger.error(f"Resolution update failed: {e}")

            # Update detection thumbnails
            try:
                # Get processing resolution from config
                config = self.hsv_controls.get_hsv_config()
                processing_res = config.processing_resolution
                original_res = (self.stream_resolution[0], self.stream_resolution[1])

                # Update thumbnails with zoom=3.0 for tight crop
                self.thumbnail_widget.update_thumbnails(
                    working_frame,
                    detections,
                    zoom=3.0,
                    processing_resolution=processing_res,
                    original_resolution=original_res
                )
            except Exception as e:
                self.logger.error(f"Thumbnail update failed: {e}")

            # Add frame to recording if active
            if self.is_recording:
                try:
                    self.recording_manager.add_frame(working_frame, timestamp)
                except Exception as e:
                    self.logger.error(f"Recording failed: {e}")

            # Emit signal with results
            try:
                self.color_detector.detectionsReady.emit(detections, timestamp, annotated_frame)
            except Exception as e:
                self.logger.error(f"Signal emission failed: {e}")

        except Exception as e:
            self.logger.error(f"Critical error processing frame: {e}")
            import traceback
            self.logger.error(f"Frame processing traceback: {traceback.format_exc()}")

    def on_detections_ready(self, detections: List[Detection], timestamp: float, annotated_frame: np.ndarray):
        """Handle detection results."""
        # Update info panel
        if detections:
            info_text = f"Detection Results ({len(detections)} found):\n"
            for i, detection in enumerate(detections[:5]):  # Show top 5
                x, y, w, h = detection.bbox
                info_text += f"  #{i+1}: Pos({x},{y}) Size({w}x{h}) Area({int(detection.area)}px) Conf({detection.confidence:.2f})\n"
        else:
            info_text = "No detections found."

        self.info_panel.setPlainText(info_text)

    def on_connection_changed(self, connected: bool, message: str):
        """Handle connection status changes."""
        self.stream_controls.update_connection_status(connected, message)
        if connected:
            self.status_bar.showMessage(f"Connected - {message}")
        else:
            self.status_bar.showMessage(f"Disconnected - {message}")

    def on_stream_stats(self, stats: Dict[str, Any]):
        """Handle stream statistics updates."""
        # Update status bar with stream info
        fps = stats.get('fps', 0)
        resolution = stats.get('resolution', (0, 0))
        self.status_bar.showMessage(f"Stream: {resolution[0]}x{resolution[1]} @ {fps:.1f}fps")

    def on_performance_update(self, stats: Dict[str, Any]):
        """Handle performance statistics updates."""
        self.stream_controls.update_performance(stats)

    def start_recording(self):
        """Start video recording."""
        if not self.stream_manager.is_connected():
            QMessageBox.warning(self, "No Stream", "Please connect to a stream before recording.")
            return

        success = self.recording_manager.start_recording(
            self.stream_resolution,
            f"rtmp_detection_{int(time.time())}"
        )

        if success:
            self.is_recording = True
            self.start_recording_btn.setEnabled(False)
            self.stop_recording_btn.setEnabled(True)
            self.logger.info("Recording started")
        else:
            QMessageBox.critical(self, "Recording Error", "Failed to start recording.")

    def stop_recording(self):
        """Stop video recording."""
        self.recording_manager.stop_recording()
        self.is_recording = False
        self.start_recording_btn.setEnabled(True)
        self.stop_recording_btn.setEnabled(False)
        self.logger.info("Recording stopped")

    def on_recording_state_changed(self, is_recording: bool, path_or_message: str):
        """Handle recording state changes."""
        if is_recording:
            self.recording_status.setText("Status: Recording")
            self.recording_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        else:
            self.recording_status.setText(f"Status: {path_or_message}")
            self.recording_status.setStyleSheet("QLabel { color: gray; }")

    def on_recording_stats(self, stats: Dict[str, Any]):
        """Handle recording statistics updates."""
        duration = stats.get('duration', 0)
        fps = stats.get('recording_fps', 0)
        frame_count = stats.get('frame_count', 0)

        info_text = f"Duration: {duration:.1f}s"
        if fps > 0:
            info_text += f" | {fps:.1f} fps | {frame_count} frames"

        self.recording_info.setText(info_text)

    def closeEvent(self, event):
        """Handle window close event."""
        self.disconnect_from_stream()
        if self.is_recording:
            self.stop_recording()
        event.accept()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for video playback."""
        if self.timeline_widget.handle_key_press(event.key()):
            event.accept()
        else:
            super().keyPressEvent(event)

    def on_video_position_changed(self, current_time: float, total_time: float):
        """Handle video position updates from stream manager."""
        self.timeline_widget.update_timeline(current_time, total_time)

    def toggle_play_pause(self):
        """Toggle play/pause state for video files."""
        if self.stream_manager.is_file_playback():
            is_playing = self.stream_manager.play_pause()
            self.timeline_widget.update_play_state(is_playing)

    def seek_to_time(self, time_seconds: float):
        """Seek to specific time in video."""
        if self.stream_manager.is_file_playback():
            self.stream_manager.seek_to_time(time_seconds)

    def seek_relative(self, seconds_delta: float):
        """Seek relative to current position."""
        if self.stream_manager.is_file_playback():
            self.stream_manager.seek_relative(seconds_delta)

    def jump_to_beginning(self):
        """Jump to beginning of video."""
        if self.stream_manager.is_file_playback():
            self.stream_manager.seek_to_beginning()

    def jump_to_end(self):
        """Jump to end of video."""
        if self.stream_manager.is_file_playback():
            self.stream_manager.seek_to_end()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    viewer = RTMPColorDetectionViewer()
    viewer.show()
    sys.exit(app.exec())
