"""
shared_widgets.py - Shared widgets for streaming viewers

Contains reusable widgets and components used across multiple streaming viewers:
- DetectionTracker: Tracks detections across frames
- DetectionThumbnailWidget: Displays clickable detection thumbnails
- StreamControlWidget: Stream connection and recording controls

The zoomable live video widget lives in
core.views.streaming.components.StreamingVideoDisplay.
"""

import numpy as np
import cv2
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout,
                               QGroupBox, QLineEdit, QPushButton, QComboBox, QFileDialog,
                               QMessageBox, QSizePolicy)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtWidgets import QApplication
from core.services.streaming.RTMPStreamService import StreamType
from core.services.streaming.contracts import FocusTarget
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin
from helpers.WidgetHelper import hand_off_focus


class HDMIDeviceScanWorker(QObject):
    """Worker that scans for HDMI capture devices in a background thread."""

    finished = Signal(object, object)  # found_devices, device_backends (use object for dict compatibility)

    def run(self):
        """Scan for devices - runs in background thread.

        Uses multiple retries and delays to handle devices that may be slow to release
        from previous connections.
        """
        # time is imported at module level

        backends = []
        if hasattr(cv2, 'CAP_MSMF'):
            backends.append((cv2.CAP_MSMF, "MSMF"))
        if hasattr(cv2, 'CAP_DSHOW'):
            backends.append((cv2.CAP_DSHOW, "DirectShow"))
        backends.append((cv2.CAP_ANY, "Auto"))

        found_devices = {}
        device_backends = {}
        max_devices = 5  # Reduced for faster scanning
        max_retries = 2  # Retry each device up to 2 times if it fails

        for backend_id, backend_name in backends:
            consecutive_failures = 0
            for index in range(max_devices):
                if index in found_devices:
                    consecutive_failures = 0
                    continue

                if consecutive_failures >= 2:
                    break

                # Try multiple times for each device (handles slow device release)
                for retry in range(max_retries):
                    cap = None
                    try:
                        cap = cv2.VideoCapture(index, backend_id)
                        if cap is not None and cap.isOpened():
                            # Verify device is actually working by reading a test frame
                            ret, test_frame = cap.read()
                            if ret and test_frame is not None and test_frame.size > 0:
                                # Use generic device name - platform-agnostic approach
                                label = f"Device {index} ({backend_name})"
                                found_devices[index] = (label, backend_id, backend_name)
                                consecutive_failures = 0
                                break  # Success, move to next device
                            else:
                                # Device opened but couldn't read frame - might be busy
                                if retry < max_retries - 1:
                                    time.sleep(0.3)  # Wait before retry
                        else:
                            consecutive_failures += 1
                            if retry < max_retries - 1:
                                time.sleep(0.2)  # Wait before retry
                    except Exception:
                        if retry < max_retries - 1:
                            time.sleep(0.2)  # Wait before retry
                    finally:
                        if cap is not None:
                            try:
                                cap.release()
                            except Exception:
                                pass
                            # Small delay after release to ensure device is freed
                            time.sleep(0.1)

                # If we exhausted retries and didn't find device, increment failure count
                if index not in found_devices:
                    consecutive_failures += 1

        # Build device_backends mapping
        combo_idx = 0
        for dev_index in sorted(found_devices.keys()):
            _, backend_id, _ = found_devices[dev_index]
            device_backends[combo_idx] = backend_id
            combo_idx += 1

        self.finished.emit(found_devices, device_backends)


@dataclass
class Track:
    """Represents a tracked detection with static thumbnail for gallery display.

    The thumbnail is captured once when the track is first created, preventing
    the 'moving thumbnail' issue where thumbnails drift as the object moves.
    """
    track_id: int
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    centroid: Tuple[int, int]

    # Static thumbnail - captured ONCE with .copy() to prevent memory leak
    thumbnail: np.ndarray

    # Metadata for click-to-seek functionality
    first_frame_index: int
    first_timestamp: float  # seconds

    # Frame resolution when detection was captured (for coordinate scaling)
    frame_resolution: Tuple[int, int] = (0, 0)  # (width, height)

    # Tracking state
    frames_seen: int = 1
    is_confirmed: bool = False
    saved_to_gallery: bool = False
    detection_type: str = "detection"
    confidence: float = 0.0

    # Additional metadata for gallery sorting
    detection_color: Optional[Tuple[int, int, int]] = None  # BGR color
    pixel_area: float = 0.0  # Pixel area of detection
    rarity: float = 0.0  # Rarity score (from confidence)


class DetectionTracker(QObject):
    """Tracks detections across frames to maintain stable thumbnail assignments with ghost memory and minimum display duration."""

    # Signal emitted when a track is confirmed (seen for confirmation_threshold frames)
    track_confirmed = Signal(object)  # Emits Track object

    def __init__(self, max_slots=7, distance_threshold=100.0, ghost_frames=60, ghost_distance_multiplier=3.0, min_display_frames=60, parent=None):
        """
        Initialize detection tracker.

        Args:
            max_slots: Maximum number of thumbnail slots
            distance_threshold: Maximum centroid distance to consider same detection (pixels)
            ghost_frames: Number of frames to remember lost detections before freeing slot (default 60 = ~2s at 30fps)
            ghost_distance_multiplier: Multiplier for ghost matching threshold (handles camera pans)
                                      Default 3.0 means ghosts can match up to 300px away (for 100px threshold)
            min_display_frames: Minimum frames to display a thumbnail before it can be replaced (default 60 = ~2s at 30fps)
            parent: Parent QObject
        """
        super().__init__(parent)

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

        # Track storage for gallery: {track_id: Track}
        self.tracks: Dict[int, Track] = {}

        # Configurable confirmation threshold (frames before appearing in gallery)
        self.confirmation_threshold: int = 5

        # Maximum tracks to store (memory management)
        self.max_tracks: int = 200

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
        """Clear all tracking state including ghost memory, display info, and tracks."""
        self.slot_assignments.clear()
        self.slot_display_info.clear()
        self.previous_detections.clear()
        self.id_to_slot.clear()
        self.ghost_detections.clear()
        self.tracks.clear()
        self.next_id = 0
        self.frame_count = 0

    def set_confirmation_threshold(self, frames: int):
        """Set number of frames required before a track appears in gallery.

        Args:
            frames: Number of frames (minimum 1)
        """
        self.confirmation_threshold = max(1, frames)

    def update_track(self, track_id: int, detection, frame: np.ndarray,
                     frame_index: int, timestamp: float):
        """Create or update a Track object, capturing static thumbnail on first appearance.

        Args:
            track_id: The detection's track ID
            detection: Detection object with bbox, centroid, etc.
            frame: The current video frame
            frame_index: Current frame index
            timestamp: Current timestamp in seconds
        """
        if track_id not in self.tracks:
            # New track - capture static thumbnail with context (like thumbnail bar)
            x, y, w, h = detection.bbox
            frame_h, frame_w = frame.shape[:2]

            # Add context padding similar to DetectionThumbnailWidget's zoom calculation
            # zoom=3.0 gives context_multiplier = 4.5/3.0 = 1.5
            context_multiplier = 1.5
            zoom_w = int(w * context_multiplier)
            zoom_h = int(h * context_multiplier)

            # Minimum size to match gallery display (120x120)
            zoom_w = max(120, zoom_w)
            zoom_h = max(120, zoom_h)

            # Center on detection
            cx = x + w // 2
            cy = y + h // 2
            x1 = max(0, cx - zoom_w // 2)
            y1 = max(0, cy - zoom_h // 2)
            x2 = min(frame_w, cx + zoom_w // 2)
            y2 = min(frame_h, cy + zoom_h // 2)

            # CRITICAL: Use .copy() to prevent memory leak from holding entire frame
            thumbnail = frame[y1:y2, x1:x2].copy()

            # Create new Track with metadata for gallery sorting
            det_confidence = getattr(detection, 'confidence', 0.0)

            # Get detection color - check multiple sources
            det_color = None
            # First try mean_color (from ColorDetection)
            if hasattr(detection, 'mean_color') and detection.mean_color is not None:
                mc = detection.mean_color
                if isinstance(mc, (list, tuple)) and len(mc) >= 3:
                    det_color = (int(mc[0]), int(mc[1]), int(mc[2]))
            # Then try metadata.display_color (from ColorAnomalyAndMotionDetection)
            if det_color is None:
                metadata = getattr(detection, 'metadata', None) or {}
                if 'display_color' in metadata:
                    dc = metadata['display_color']
                    if isinstance(dc, (list, tuple)) and len(dc) >= 3:
                        det_color = (int(dc[0]), int(dc[1]), int(dc[2]))
                elif 'color' in metadata:
                    dc = metadata['color']
                    if isinstance(dc, (list, tuple)) and len(dc) >= 3:
                        det_color = (int(dc[0]), int(dc[1]), int(dc[2]))

            self.tracks[track_id] = Track(
                track_id=track_id,
                bbox=detection.bbox,
                centroid=detection.centroid,
                thumbnail=thumbnail,
                first_frame_index=frame_index,
                first_timestamp=timestamp,
                frame_resolution=(frame_w, frame_h),  # Store resolution for coordinate scaling
                detection_type=getattr(detection, 'detection_type', 'detection'),
                confidence=det_confidence,
                detection_color=det_color,
                pixel_area=getattr(detection, 'area', 0.0),
                rarity=det_confidence,  # Use confidence as rarity proxy
            )
        else:
            # Existing track - just increment frames seen
            # Keep bbox/centroid STATIC from first detection (like thumbnail)
            # so they match first_frame_index when seeking
            track = self.tracks[track_id]
            track.frames_seen += 1

            # Check confirmation threshold
            if not track.is_confirmed and track.frames_seen >= self.confirmation_threshold:
                track.is_confirmed = True
                self.track_confirmed.emit(track)

        # Prune old tracks if over limit
        self._prune_tracks()

    def _prune_tracks(self):
        """Remove oldest tracks when exceeding memory limit."""
        if len(self.tracks) > self.max_tracks:
            # Sort by track_id (older tracks have lower IDs)
            sorted_ids = sorted(self.tracks.keys())
            # Remove oldest tracks, keeping confirmed ones longer
            to_remove = len(self.tracks) - self.max_tracks
            removed = 0
            for old_id in sorted_ids:
                if removed >= to_remove:
                    break
                track = self.tracks[old_id]
                # Skip confirmed tracks that haven't been saved to gallery yet
                if track.is_confirmed and not track.saved_to_gallery:
                    continue
                del self.tracks[old_id]
                removed += 1


class ClickableThumbnailLabel(QLabel):
    """Thumbnail slot label that reports left-clicks by slot index."""

    clicked = Signal(int)  # slot index

    def __init__(self, slot_index: int, parent=None):
        super().__init__(parent)
        self.slot_index = slot_index
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.slot_index)
        super().mousePressEvent(event)


class DetectionThumbnailWidget(QWidget):
    """Widget to display thumbnails of top detections with dynamic sizing."""

    # Emits a FocusTarget (source-frame coords) when a populated slot is clicked.
    thumbnail_focus_requested = Signal(object)

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

        # Latest focus payload per populated slot (slot_index -> FocusTarget).
        # A resize alone preserves hidden slots for paused hide/reshow. The next
        # frame update invalidates hidden slots because their pixmaps are no
        # longer current.
        self._focus_targets = {}

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
                label = ClickableThumbnailLabel(i)
                label.setFixedSize(self.thumbnail_size, self.thumbnail_size)
                label.setStyleSheet("QLabel { background-color: black; border: 2px solid #555; }")
                label.setAlignment(Qt.AlignCenter)
                label.setScaledContents(False)
                label.clicked.connect(self._on_thumbnail_clicked)
                # Insert before the last item (which is the stretch)
                self.layout.insertWidget(self.layout.count() - 1, label)
                self.thumbnail_labels.append(label)
        elif max_thumbnails < current_count:
            # Hide excess thumbnail labels. The focus payload is kept: the label
            # keeps its last pixmap while hidden, so widening the window later
            # re-shows the same pixmap and it must stay clickable (while paused
            # no frame would repopulate the payload).
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

    @staticmethod
    def _compute_live_thumbnail_crop(
            frame_shape: Tuple[int, int, int],
            centroid: Tuple[int, int],
            bbox: Tuple[int, int, int, int],
            zoom: float = 3.0) -> Tuple[int, int, int, int]:
        """Compute a square crop for the live thumbnail strip."""
        frame_h, frame_w = frame_shape[:2]
        cx, cy = int(centroid[0]), int(centroid[1])
        _x, _y, w_raw, h_raw = bbox
        w = max(1, int(w_raw))
        h = max(1, int(h_raw))

        # Keep the same context model as before, but normalize to a square crop
        # so thumbnails use the slot area more consistently.
        base_context_multiplier = 4.5
        context_multiplier = base_context_multiplier / zoom
        crop_side = int(max(w, h) * context_multiplier)
        crop_side = max(60, crop_side)

        x1 = max(0, cx - crop_side // 2)
        y1 = max(0, cy - crop_side // 2)
        x2 = min(frame_w, x1 + crop_side)
        y2 = min(frame_h, y1 + crop_side)

        # Re-anchor when clamping at the frame edges so the crop stays square when possible.
        if x2 - x1 < crop_side:
            x1 = max(0, x2 - crop_side)
        if y2 - y1 < crop_side:
            y1 = max(0, y2 - crop_side)

        return x1, y1, x2, y2

    def update_thumbnails(self, frame: np.ndarray, detections: List, zoom: float = 3.0,
                          processing_resolution: tuple = None, original_resolution: tuple = None,
                          frame_index: int = 0, timestamp: float = 0.0):
        """Update thumbnails with tracked detections in stable slots.

        Args:
            frame: The frame to extract thumbnails from (at source/original resolution)
            detections: List of detections (coordinates already in source-frame
                space - services scale them back from processing resolution)
            zoom: Zoom level (higher = tighter crop around detection)
            processing_resolution: accepted for signature compatibility; NOT
                used to rescale coordinates (they are already source-space)
            original_resolution: accepted for signature compatibility; NOT used
                to rescale coordinates
            frame_index: Current frame index for track storage
            timestamp: Current timestamp in seconds for track storage
        """
        # Use tracker to get stable slot assignments
        slot_assignments = self.tracker.update(detections)

        # Update track objects only for detections currently shown in thumbnail slots.
        # This keeps gallery growth aligned with visible detections and bounds per-frame work.
        visible_detections = list(slot_assignments.values())
        seen_track_ids = set()
        for detection in visible_detections:
            track_id = detection.metadata.get('track_id')
            if track_id is not None:
                if track_id in seen_track_ids:
                    continue
                seen_track_ids.add(track_id)
                self.tracker.update_track(track_id, detection, frame, frame_index, timestamp)

        # Detection coordinates are already in source-frame space (services
        # scale them back from processing resolution), so no processing->source
        # rescale is applied here. See FocusTarget / StreamDetection.
        frame_h, frame_w = frame.shape[:2]

        # A resize alone intentionally preserves hidden slots so paused users
        # can hide and re-show the same clickable thumbnail. Once a newer frame
        # arrives, however, hidden labels are not rendered from that frame and
        # must be invalidated so stale pixmaps/targets cannot reappear later.
        for slot_idx, label in enumerate(self.thumbnail_labels):
            if not label.isVisible():
                label.clear()
                self._focus_targets.pop(slot_idx, None)

        # Update each visible thumbnail label based on slot assignment (stable positions)
        for slot_idx, label in enumerate(self.thumbnail_labels):
            if not label.isVisible():
                continue

            if slot_idx in slot_assignments:
                detection = slot_assignments[slot_idx]

                # Coordinates are source-frame pixels; use them directly.
                cx_raw, cy_raw = detection.centroid
                x_raw, y_raw, w_raw, h_raw = detection.bbox
                cx = int(cx_raw)
                cy = int(cy_raw)

                x1, y1, x2, y2 = self._compute_live_thumbnail_crop(
                    frame.shape,
                    (cx, cy),
                    (x_raw, y_raw, w_raw, h_raw),
                    zoom=zoom,
                )

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
                    # Capture the click-to-focus payload for this slot in
                    # source-frame coordinates.
                    self._focus_targets[slot_idx] = FocusTarget(
                        center_xy=(cx, cy),
                        reference_size=(frame_w, frame_h),
                    )
                else:
                    label.clear()
                    self._focus_targets.pop(slot_idx, None)
            else:
                # No detection assigned to this slot
                label.clear()
                self._focus_targets.pop(slot_idx, None)

    def _on_thumbnail_clicked(self, slot_index: int):
        """Emit a focus request for a populated slot; ignore empty slots."""
        target = self._focus_targets.get(slot_index)
        if target is not None:
            self.thumbnail_focus_requested.emit(target)

    def clear_focus_targets(self):
        """Drop all stored click-to-focus payloads."""
        self._focus_targets.clear()

    def clear_thumbnails(self):
        """Clear all thumbnails (including hidden ones), focus payloads, and tracking.

        Hidden labels are cleared too, otherwise a hidden thumbnail from a
        previous source could reappear (with a stale pixmap) when the window is
        widened after a new source connects.
        """
        for label in self.thumbnail_labels:
            label.clear()
        self._focus_targets.clear()
        self.tracker.clear()


class StreamControlWidget(TranslationMixin, QWidget):
    """Shared stream connection and control widget with optional recording controls."""

    connectRequested = Signal(str, object, object)  # url, stream_type, hdmi_backend
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
        connection_group = QGroupBox(self.tr("Stream Connection"))
        connection_group.setToolTip(
            self.tr("Configure and connect to video source (file, HDMI capture, or RTMP stream)")
        )
        connection_layout = QGridLayout(connection_group)

        # Stream type (moved to row 0)
        connection_layout.addWidget(QLabel(self.tr("Stream Type:")), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItem(self.tr("File"), "File")
        self.type_combo.addItem(self.tr("HDMI Capture"), "HDMI Capture")
        self.type_combo.addItem(self.tr("RTMP Stream"), "RTMP Stream")
        self.type_combo.setToolTip(
            self.tr(
                "Select the type of video source:\n"
                "• File: Pre-recorded video file with timeline controls\n"
                "• HDMI Capture: Live capture from HDMI capture device\n"
                "• RTMP Stream: Real-time streaming from RTMP/HTTP source"
            )
        )
        connection_layout.addWidget(self.type_combo, 0, 1)

        # Stream URL/Path (moved to row 1)
        connection_layout.addWidget(QLabel(self.tr("Stream URL/Path:")), 1, 0)

        # Container for URL input - can be QLineEdit or QComboBox
        url_layout = QHBoxLayout()

        # QLineEdit for File and RTMP
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.tr("Click to browse for video file..."))
        self.url_input.setText("")  # Default empty for file selection
        self.url_input.setToolTip(
            self.tr(
                "Enter or browse for the video source:\n"
                "• File: Click to browse for video file (MP4, AVI, MOV, etc.)\n"
                "• RTMP Stream: Enter RTMP URL (rtmp://server:port/app/stream)"
            )
        )
        url_layout.addWidget(self.url_input, 1)

        # QComboBox for HDMI Capture (hidden by default)
        self.hdmi_device_combo = QComboBox()
        self.hdmi_device_combo.setToolTip(self.tr("Select HDMI capture device"))
        self.hdmi_device_combo.setVisible(False)
        self.hdmi_device_combo.addItem(self.tr("Scanning for devices..."), None)
        self.hdmi_device_combo.setEnabled(False)
        url_layout.addWidget(self.hdmi_device_combo, 1)

        self.browse_button = QPushButton(self.tr("Browse..."))
        self.browse_button.setVisible(True)  # Visible by default since File is default
        self.browse_button.setToolTip(
            self.tr(
                "Open file browser to select a video file for analysis.\n"
                "Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM"
            )
        )
        url_layout.addWidget(self.browse_button)

        # Scan button for HDMI devices (hidden by default)
        self.scan_button = QPushButton(self.tr("Scan..."))
        self.scan_button.setVisible(False)
        self.scan_button.setToolTip(self.tr("Scan for available HDMI capture devices"))
        url_layout.addWidget(self.scan_button)

        connection_layout.addLayout(url_layout, 1, 1)

        # Connection buttons
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton(self.tr("Connect"))
        self.connect_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.connect_button.setToolTip(
            self.tr("Connect to the specified video source and begin processing.")
        )
        self.disconnect_button = QPushButton(self.tr("Disconnect"))
        self.disconnect_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setToolTip(
            self.tr("Disconnect from the current video source and stop processing.")
        )

        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        # Status display
        self.status_label = QLabel(self.tr("Status: Disconnected"))
        self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        self.status_label.setToolTip(self.tr("Current connection status"))

        # Performance display
        performance_group = QGroupBox(self.tr("Performance"))
        performance_group.setToolTip(self.tr("Real-time performance metrics"))
        performance_layout = QGridLayout(performance_group)

        # Resolution labels
        self.video_resolution_label = QLabel(self.tr("Video: --"))
        self.video_resolution_label.setToolTip(self.tr("Original video resolution"))
        self.processing_resolution_label = QLabel(self.tr("Processing: --"))
        self.processing_resolution_label.setToolTip(
            self.tr("Resolution used for detection processing")
        )

        # FPS labels
        self.video_fps_label = QLabel(self.tr("Source FPS: --"))
        self.video_fps_label.setToolTip(self.tr("Source frame rate and the applied processing cadence"))
        self.processing_fps_label = QLabel(self.tr("Proc FPS: --"))
        self.processing_fps_label.setToolTip(
            self.tr("Actual frames per second being processed")
        )

        # Timing labels
        self.processing_label = QLabel(self.tr("Time: -- ms"))
        self.processing_label.setToolTip(
            self.tr("Time in milliseconds to process each frame")
        )
        self.latency_label = QLabel(self.tr("Latency: -- ms"))
        self.latency_label.setToolTip(
            self.tr("End-to-end latency from frame capture to display")
        )

        # Stats labels
        self.total_frames_label = QLabel(self.tr("Frames: --"))
        self.total_frames_label.setToolTip(self.tr("Total number of frames processed"))
        self.detections_label = QLabel(self.tr("Detections: --"))
        self.detections_label.setToolTip(self.tr("Number of detections in current frame"))

        # Layout: 4 rows x 2 columns
        performance_layout.addWidget(self.video_resolution_label, 0, 0)
        performance_layout.addWidget(self.processing_resolution_label, 0, 1)
        performance_layout.addWidget(self.video_fps_label, 1, 0)
        performance_layout.addWidget(self.processing_fps_label, 1, 1)
        performance_layout.addWidget(self.processing_label, 2, 0)
        performance_layout.addWidget(self.latency_label, 2, 1)
        performance_layout.addWidget(self.total_frames_label, 3, 0)
        performance_layout.addWidget(self.detections_label, 3, 1)

        # Recording group (optional)
        if self.include_recording:
            recording_group = QGroupBox(self.tr("Recording"))
            recording_layout = QVBoxLayout(recording_group)

            # Recording buttons
            recording_button_layout = QHBoxLayout()
            self.start_recording_btn = QPushButton(self.tr("Start Recording"))
            self.start_recording_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-weight: bold; }")
            self.start_recording_btn.setToolTip(
                self.tr("Start recording the video stream with detection overlays.")
            )
            self.stop_recording_btn = QPushButton(self.tr("Stop Recording"))
            self.stop_recording_btn.setEnabled(False)
            self.stop_recording_btn.setToolTip(
                self.tr("Stop the current recording and save to file.")
            )

            recording_button_layout.addWidget(self.start_recording_btn)
            recording_button_layout.addWidget(self.stop_recording_btn)

            # Recording status
            self.recording_status = QLabel(self.tr("Status: Not Recording"))
            self.recording_status.setStyleSheet("QLabel { color: gray; }")
            self.recording_status.setToolTip(
                self.tr("Current recording status and output file path")
            )

            # Recording info
            self.recording_info = QLabel(self.tr("Duration: --"))
            self.recording_info.setToolTip(
                self.tr("Recording statistics: Duration, FPS, Frames")
            )

            recording_layout.addLayout(recording_button_layout)
            recording_layout.addWidget(self.recording_status)
            recording_layout.addWidget(self.recording_info)

            # Recording directory selector
            dir_layout = QHBoxLayout()
            dir_label = QLabel(self.tr("Save to:"))
            self.recording_dir_edit = QLineEdit("./recordings")
            self.recording_dir_edit.setToolTip(
                self.tr("Directory where video recordings will be saved.")
            )
            self.recording_dir_browse = QPushButton(self.tr("Browse..."))
            self.recording_dir_browse.setToolTip(
                self.tr("Choose a folder to store recordings.")
            )

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
        self.scan_button.clicked.connect(self._scan_hdmi_devices)
        self.hdmi_device_combo.currentIndexChanged.connect(self._on_hdmi_device_selected)
        self.url_input.mousePressEvent = self.on_url_input_clicked
        if self.include_recording:
            self.start_recording_btn.clicked.connect(self._emit_start_recording)
            self.stop_recording_btn.clicked.connect(self.stopRecordingRequested.emit)
            self.recording_dir_browse.clicked.connect(self._browse_recording_directory)
            self.recording_dir_edit.textChanged.connect(self._on_recording_directory_changed)

    def on_stream_type_changed(self, stream_type: str):
        """Handle stream type selection changes."""
        stream_type_value = self.type_combo.currentData() or stream_type
        if stream_type_value == "HDMI Capture":
            # Show HDMI device combo, hide URL input
            self.url_input.setVisible(False)
            self.hdmi_device_combo.setVisible(True)
            self.browse_button.setVisible(False)
            self.scan_button.setVisible(True)
            # Don't auto-scan here - let user click Scan or wizard will set up devices
        elif stream_type_value == "File":
            # Show URL input, hide HDMI combo
            self.url_input.setVisible(True)
            self.hdmi_device_combo.setVisible(False)
            self.url_input.setPlaceholderText(self.tr("Click to browse for video file..."))
            self.url_input.setText("")
            self.browse_button.setVisible(True)
            self.scan_button.setVisible(False)
        elif stream_type_value == "RTMP Stream":
            # Show URL input, hide HDMI combo
            self.url_input.setVisible(True)
            self.hdmi_device_combo.setVisible(False)
            self.url_input.setPlaceholderText(self.tr("rtmp://server:port/app/stream"))
            self.url_input.setText("")
            self.browse_button.setVisible(False)
            self.scan_button.setVisible(False)

    def request_connect(self):
        """Request stream connection."""
        combo_text = self.type_combo.currentData() or self.type_combo.currentText()
        hdmi_backend = None

        # Get URL from appropriate widget
        if combo_text == "HDMI Capture":
            # Get device index from HDMI combo box
            device_index = self.hdmi_device_combo.currentData()
            if device_index is None:
                QMessageBox.warning(
                    self,
                    self.tr("Invalid Device"),
                    self.tr("Please select a valid HDMI capture device.")
                )
                return
            url = str(device_index)
            if hasattr(self, '_device_backends'):
                hdmi_backend = self._device_backends.get(self.hdmi_device_combo.currentIndex())
        else:
            # Get URL from text input
            url = self.url_input.text().strip()
            if not url:
                QMessageBox.warning(
                    self,
                    self.tr("Invalid URL"),
                    self.tr("Please enter a valid stream URL.")
                )
                return

        # Map combo box text to StreamType enum
        stream_type_map = {
            "File": StreamType.FILE,
            "HDMI Capture": StreamType.HDMI_CAPTURE,
            "RTMP Stream": StreamType.RTMP
        }
        stream_type = stream_type_map.get(combo_text, StreamType.FILE)
        self.connectRequested.emit(url, stream_type, hdmi_backend)

    def update_connection_status(self, connected: bool, message: str):
        """Update connection status display."""
        if connected:
            self.status_label.setText(
                self.tr("Status: {message}").format(message=message)
            )
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            # Enable the successor first, then hand focus to it: disabling the
            # widget that has focus makes Qt walk the focus chain into whatever
            # control was created next, which is nowhere near this panel.
            self.disconnect_button.setEnabled(True)
            hand_off_focus(
                self.disconnect_button,
                self.connect_button, self.type_combo, self.hdmi_device_combo,
                self.scan_button, self.url_input, self.browse_button
            )
            self.connect_button.setEnabled(False)
            # Disable device selection while connected
            self.type_combo.setEnabled(False)
            self.hdmi_device_combo.setEnabled(False)
            self.scan_button.setEnabled(False)
            self.url_input.setEnabled(False)
            self.browse_button.setEnabled(False)
        else:
            self.status_label.setText(
                self.tr("Status: {message}").format(message=message)
            )
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            self.connect_button.setEnabled(True)
            hand_off_focus(self.connect_button, self.disconnect_button)
            self.disconnect_button.setEnabled(False)
            # Re-enable device selection after disconnect
            self.type_combo.setEnabled(True)
            self.url_input.setEnabled(True)
            self.browse_button.setEnabled(True)
            # For HDMI, re-enable device combo and scan button
            if self.type_combo.currentData() == "HDMI Capture":
                self.hdmi_device_combo.setEnabled(True)
                self.scan_button.setEnabled(True)

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
            self.stop_recording_btn.setEnabled(True)
            hand_off_focus(self.stop_recording_btn, self.start_recording_btn)
            self.start_recording_btn.setEnabled(False)
            self.start_recording_btn.setStyleSheet(start_disabled_style)
            self.stop_recording_btn.setStyleSheet(stop_active_style)
            self.recording_status.setText(self.tr("Status: Recording"))
            self.recording_status.setStyleSheet("QLabel { color: #ff4444; font-weight: bold; }")
            if path_or_message:
                self.recording_info.setText(
                    self.tr("Output: {value}").format(value=path_or_message)
                )
        else:
            # Recording stopped
            self.start_recording_btn.setEnabled(True)
            self.start_recording_btn.setStyleSheet(start_active_style)
            hand_off_focus(self.start_recording_btn, self.stop_recording_btn)
            self.stop_recording_btn.setEnabled(False)
            self.stop_recording_btn.setStyleSheet(stop_inactive_style)
            self.recording_status.setText(self.tr("Status: Not Recording"))
            self.recording_status.setStyleSheet("QLabel { color: gray; }")
            if path_or_message:
                self.recording_info.setText(
                    self.tr("Duration: {value}").format(value=path_or_message)
                )
            else:
                self.recording_info.setText(self.tr("Duration: --"))

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
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Recording Directory"),
            current_dir or "."
        )
        if selected_dir:
            self.recording_dir_edit.setText(selected_dir)
            self.recordingDirectoryChanged.emit(selected_dir)

    def _scan_hdmi_devices(self):
        """Scan for available HDMI capture devices using OpenCV with multiple backends."""
        # Show scanning state
        self.hdmi_device_combo.clear()
        self.hdmi_device_combo.addItem(self.tr("Scanning..."), None)
        self.hdmi_device_combo.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.scan_button.setText(self.tr("Scanning..."))
        QApplication.processEvents()  # Update UI immediately

        self._device_backends = {}

        # Create worker and thread
        self._scan_thread = QThread()
        self._scan_worker = HDMIDeviceScanWorker()
        self._scan_worker.moveToThread(self._scan_thread)

        # Connect signals
        self._scan_thread.started.connect(self._scan_worker.run)
        self._scan_worker.finished.connect(self._on_hdmi_scan_finished)
        self._scan_worker.finished.connect(self._scan_thread.quit)
        self._scan_worker.finished.connect(self._scan_worker.deleteLater)
        self._scan_thread.finished.connect(self._scan_thread.deleteLater)

        # Start scanning
        self._scan_thread.start()

    def _on_hdmi_scan_finished(self, found_devices: dict, device_backends: dict) -> None:
        """Handle HDMI scan completion - update UI with results."""
        # Restore button state
        self.scan_button.setEnabled(True)
        self.scan_button.setText(self.tr("Scan"))

        self._device_backends = device_backends
        self.hdmi_device_combo.clear()

        if not found_devices:
            self.hdmi_device_combo.addItem(self.tr("No capture devices found"), None)
            self.hdmi_device_combo.setEnabled(False)
        else:
            # Add found devices to combo box, sorted by index
            for dev_index in sorted(found_devices.keys()):
                label, backend_id, backend_name = found_devices[dev_index]
                # Translate the label
                translated_label = self.tr("Device {index} ({backend})").format(
                    index=dev_index, backend=backend_name)
                self.hdmi_device_combo.addItem(translated_label, dev_index)

            self.hdmi_device_combo.setEnabled(True)
            if self.hdmi_device_combo.count() > 0:
                self.hdmi_device_combo.setCurrentIndex(0)

    def _on_hdmi_device_selected(self, index: int):
        """Handle HDMI device selection from combo box."""
        # Device index is stored in itemData, which is automatically used in request_connect
        pass

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
        # Resolution info
        video_resolution = stats.get('video_resolution')
        processing_resolution = stats.get('processing_resolution')

        if video_resolution:
            self.video_resolution_label.setText(
                self.tr("Video: {width}x{height}").format(
                    width=video_resolution[0],
                    height=video_resolution[1]
                )
            )
        if processing_resolution:
            self.processing_resolution_label.setText(
                self.tr("Processing: {width}x{height}").format(
                    width=processing_resolution[0],
                    height=processing_resolution[1]
                )
            )

        # FPS info
        video_fps = stats.get('video_fps', 0)
        applied_source_fps = stats.get('applied_source_fps', 0)
        # Use processing_fps (actual processed frames/sec, accounts for frame rate limiting)
        # Fall back to avg_fps or fps for backwards compatibility
        processing_fps = stats.get('processing_fps', stats.get('avg_fps', stats.get('fps', 0)))

        if video_fps > 0:
            if applied_source_fps and abs(float(applied_source_fps) - float(video_fps)) > 0.05:
                self.video_fps_label.setText(
                    self.tr("Source FPS: {source:.1f} (Applied {applied:.1f})").format(
                        source=video_fps,
                        applied=applied_source_fps,
                    )
                )
            else:
                self.video_fps_label.setText(
                    self.tr("Source FPS: {fps:.1f}").format(fps=video_fps)
                )
        self.processing_fps_label.setText(
            self.tr("Proc FPS: {fps:.1f}").format(fps=processing_fps)
        )

        # Timing info
        processing_time = stats.get('current_processing_time_ms', stats.get('avg_processing_time_ms', stats.get('total_ms', 0)))
        latency = stats.get('latency_ms', 0)

        self.processing_label.setText(
            self.tr("Time: {time:.1f} ms").format(time=processing_time)
        )
        self.latency_label.setText(
            self.tr("Latency: {latency:.1f} ms").format(latency=latency)
        )

        # Stats
        total_frames = stats.get('total_frames', 0)
        detection_count = stats.get('detection_count', stats.get('detections', 0))

        self.total_frames_label.setText(
            self.tr("Frames: {count}").format(count=total_frames)
        )
        self.detections_label.setText(
            self.tr("Detections: {count}").format(count=detection_count)
        )

    def browse_for_file(self):
        """Open file dialog to select video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Video File"),
            "",
            self.tr(
                "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;All Files (*)"
            )
        )
        if file_path:
            self.url_input.setText(file_path)

    def on_url_input_clicked(self, event):
        """Handle clicks on URL input field."""
        # If file type is selected, open file browser on click
        if self.type_combo.currentData() == "File":
            self.browse_for_file()
        else:
            # Call the original mousePressEvent for normal behavior
            QLineEdit.mousePressEvent(self.url_input, event)
