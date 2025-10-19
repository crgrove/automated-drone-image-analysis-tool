"""
IntegratedDetectionViewer.py - Real-time integrated anomaly detection viewer

Full-featured GUI for the integrated detection system combining motion detection,
color quantization, fusion, and temporal smoothing with comprehensive parameter controls.
"""

# Set environment variable to avoid numpy compatibility issues - MUST be first
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')

import cv2
import numpy as np
import time
from typing import Optional, List, Dict, Any

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit, QSpinBox, QFrame,
                               QGroupBox, QGridLayout, QTextEdit, QSplitter,
                               QCheckBox, QComboBox, QMessageBox, QStatusBar,
                               QSlider, QFileDialog, QTabWidget, QListWidget, QDoubleSpinBox)

from core.services.RTMPStreamService import StreamManager, StreamType
from core.services.RealtimeIntegratedDetectionService import (
    RealtimeIntegratedDetector,
    IntegratedDetectionConfig,
    MotionAlgorithm,
    FusionMode,
    Detection
)
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

        Clustered detections (when detection clustering is enabled) are shown as a SINGLE thumbnail
        that encompasses the entire merged detection area.

        The number of thumbnails displayed dynamically adjusts based on available window width.

        Args:
            frame: The frame to extract thumbnails from (at original or processing resolution)
            detections: List of detections (coordinates may be in processing resolution)
                       Note: Clustered detections appear as ONE merged detection
            zoom: Zoom level (higher = tighter crop around detection)
            processing_resolution: (width, height) of processing resolution if detections were scaled
            original_resolution: (width, height) of frame if different from processing resolution
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
                x = int(x_raw * scale_x)
                y = int(y_raw * scale_y)
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
                    # Convert to QPixmap and display (no overlays for clustered or single detections)
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
        self.setMaximumSize(16777215, 16777215)
        self.setStyleSheet("QLabel { background-color: black; border: 1px solid gray; }")
        self.setAlignment(Qt.AlignCenter)
        self.setText("No Stream Connected")
        self.setScaledContents(False)
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Profiling
        self._last_update_time = time.perf_counter()
        self._update_count = 0
        self._dropped_frames = 0

    def update_frame(self, frame: np.ndarray):
        """Update display with new frame."""
        start_time = time.perf_counter()

        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width

            # Convert BGR to RGB
            bgr_start = time.perf_counter()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bgr_time = (time.perf_counter() - bgr_start) * 1000

            # Create QImage and QPixmap
            qimage_start = time.perf_counter()
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            qimage_time = (time.perf_counter() - qimage_start) * 1000

            # Scale to fit widget while maintaining aspect ratio
            # Use FastTransformation instead of SmoothTransformation (5-10x faster!)
            # SmoothTransformation is beautiful but VERY slow for real-time video
            scale_start = time.perf_counter()
            widget_size = self.size()
            scaled_pixmap = pixmap.scaled(widget_size, Qt.KeepAspectRatio, Qt.FastTransformation)
            scale_time = (time.perf_counter() - scale_start) * 1000

            # Set pixmap (triggers paint event asynchronously)
            setpixmap_start = time.perf_counter()
            self.setPixmap(scaled_pixmap)
            setpixmap_time = (time.perf_counter() - setpixmap_start) * 1000

            total_time = (time.perf_counter() - start_time) * 1000

            # Track actual display FPS
            self._update_count += 1
            if self._update_count % 60 == 0:
                elapsed = time.perf_counter() - self._last_update_time
                actual_display_fps = 60 / elapsed if elapsed > 0 else 0
                self._last_update_time = time.perf_counter()

                print(f"[DISPLAY] Actual display FPS: {actual_display_fps:.1f}, "
                      f"Widget size: {widget_size.width()}x{widget_size.height()}, "
                      f"Frame size: {width}x{height}, "
                      f"Timings: BGR={bgr_time:.1f}ms, QImage={qimage_time:.1f}ms, "
                      f"Scale={scale_time:.1f}ms, SetPixmap={setpixmap_time:.1f}ms, "
                      f"Total={total_time:.1f}ms")

        except Exception as e:
            print(f"Error updating frame: {e}")


class IntegratedDetectionControlWidget(QWidget):
    """Control widget for integrated detection parameters organized in tabs."""

    configChanged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the control interface with tabbed organization."""
        layout = QVBoxLayout(self)

        # Create tab widget for organized controls
        self.tabs = QTabWidget()

        # Tab 1: Input & Processing
        self.tab_input = self._create_input_tab()
        self.tabs.addTab(self.tab_input, "Input & Processing")

        # Tab 2: Motion Detection
        self.tab_motion = self._create_motion_tab()
        self.tabs.addTab(self.tab_motion, "Motion Detection")

        # Tab 3: Color Anomaly
        self.tab_color = self._create_color_tab()
        self.tabs.addTab(self.tab_color, "Color Anomaly")

        # Tab 4: Fusion & Temporal
        self.tab_fusion = self._create_fusion_tab()
        self.tabs.addTab(self.tab_fusion, "Fusion & Temporal")

        # Tab 5: False Positive Reduction
        self.tab_fpr = self._create_fpr_tab()
        self.tabs.addTab(self.tab_fpr, "False Pos. Reduction")

        # Tab 6: Rendering
        self.tab_render = self._create_rendering_tab()
        self.tabs.addTab(self.tab_render, "Rendering")

        layout.addWidget(self.tabs)

    def _create_input_tab(self) -> QWidget:
        """Create Input & Processing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Processing Resolution
        res_group = QGroupBox("Processing Resolution")
        res_layout = QVBoxLayout(res_group)

        # Dropdown for preset resolutions
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.resolution_preset = QComboBox()

        # Common 16:9 resolutions (matching Real-Time Color Detection)
        self.resolution_presets = {
            "Original": None,  # Use video's native resolution
            "426x240": (426, 240),
            "640x360": (640, 360),
            "960x540": (960, 540),
            "1280x720": (1280, 720),
            "1600x900": (1600, 900),
            "1920x1080": (1920, 1080),
            "2560x1440": (2560, 1440),
            "3200x1800": (3200, 1800),
            "3840x2160": (3840, 2160),
            "5120x2880": (5120, 2880),
            "7680x4320": (7680, 4320),
            "Custom": "custom"  # Special marker for custom resolution
        }

        for preset in self.resolution_presets.keys():
            self.resolution_preset.addItem(preset)

        self.resolution_preset.setCurrentText("1280x720")
        self.resolution_preset.setToolTip("Select a preset resolution for processing. Lower resolutions are faster but less detailed.\n"
                                         "'Original' uses the video's native resolution (no downsampling).\n"
                                         "720p (1280x720) provides excellent balance between speed and detection accuracy.\n"
                                         "Select 'Custom' to manually set width and height.")
        preset_layout.addWidget(self.resolution_preset)
        res_layout.addLayout(preset_layout)

        # Custom resolution inputs (hidden by default)
        custom_layout = QGridLayout()
        custom_layout.addWidget(QLabel("Width:"), 0, 0)
        self.processing_width = QSpinBox()
        self.processing_width.setRange(320, 3840)
        self.processing_width.setValue(1280)
        self.processing_width.setEnabled(False)
        self.processing_width.setToolTip("Custom processing width in pixels (320-3840).\nOnly enabled when 'Custom' preset is selected.\nLower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_width, 0, 1)

        custom_layout.addWidget(QLabel("Height:"), 1, 0)
        self.processing_height = QSpinBox()
        self.processing_height.setRange(240, 2160)
        self.processing_height.setValue(720)
        self.processing_height.setEnabled(False)
        self.processing_height.setToolTip("Custom processing height in pixels (240-2160).\nOnly enabled when 'Custom' preset is selected.\nLower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_height, 1, 1)

        res_layout.addLayout(custom_layout)
        layout.addWidget(res_group)

        # Performance Options
        perf_group = QGroupBox("Performance Options")
        perf_layout = QVBoxLayout(perf_group)

        self.threaded_capture = QCheckBox("Use Threaded Capture")
        self.threaded_capture.setChecked(True)  # Default ON
        self.threaded_capture.setToolTip("Enables background video decoding in a separate thread.\n"
                                        "Allows processing to happen in parallel with video capture.\n"
                                        "Improves performance especially for high-resolution videos (2K/4K).\n"
                                        "Highly recommended for all video sources. No downsides.")
        perf_layout.addWidget(self.threaded_capture)

        self.render_at_processing_res = QCheckBox("Render at Processing Resolution (faster for high-res)")
        self.render_at_processing_res.setChecked(True)  # Default ON
        self.render_at_processing_res.setToolTip("Renders detection overlays at processing resolution instead of original video resolution.\n"
                                                 "Significantly faster for high-resolution videos (1080p+) with minimal visual impact.\n"
                                                 "Example: Processing at 720p but video is 4K - renders at 720p then upscales.\n"
                                                 "Recommended: ON for high-res videos, OFF for native 720p or lower.")
        perf_layout.addWidget(self.render_at_processing_res)

        self.enable_morphology = QCheckBox("Enable Morphological Filtering")
        self.enable_morphology.setChecked(True)  # Default ON (current behavior)
        self.enable_morphology.setToolTip("Applies morphological operations (opening/closing) to reduce noise in detection masks.\n"
                                          "Removes small noise artifacts and fills small holes in detections.\n"
                                          "Provides ~5-10% speed boost when disabled, but increases false positives.\n"
                                          "Recommended: ON for most use cases (default), OFF only for very clean video.")
        perf_layout.addWidget(self.enable_morphology)

        layout.addWidget(perf_group)
        layout.addStretch()

        return widget

    def _create_motion_tab(self) -> QWidget:
        """Create Motion Detection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Motion
        self.enable_motion = QCheckBox("Enable Motion Detection")
        self.enable_motion.setChecked(False)
        self.enable_motion.setToolTip("Detect moving objects by analyzing frame-to-frame differences.\n"
                                     "Works best for stationary cameras or slow-moving cameras.\n"
                                     "Automatically pauses when excessive camera movement is detected.\n"
                                     "Can be combined with Color Detection for more robust detection.")
        layout.addWidget(self.enable_motion)

        # Algorithm Selection
        algo_group = QGroupBox("Algorithm")
        algo_layout = QGridLayout(algo_group)

        algo_layout.addWidget(QLabel("Type:"), 0, 0)
        self.motion_algorithm = QComboBox()
        self.motion_algorithm.addItems(["FRAME_DIFF", "MOG2", "KNN"])
        self.motion_algorithm.setCurrentText("MOG2")
        self.motion_algorithm.setToolTip("Motion detection algorithm:\n\n"
                                        "• FRAME_DIFF: Simple frame differencing. Fast, sensitive to all motion.\n"
                                        "  Good for: Quick tests, high-contrast scenes.\n\n"
                                        "• MOG2: Gaussian mixture model (recommended). Adapts to lighting changes.\n"
                                        "  Good for: General use, varying lighting, shadows optional.\n\n"
                                        "• KNN: K-nearest neighbors. More robust to noise than MOG2.\n"
                                        "  Good for: Noisy videos, complex backgrounds.")
        algo_layout.addWidget(self.motion_algorithm, 0, 1)

        layout.addWidget(algo_group)

        # Detection Parameters
        param_group = QGroupBox("Detection Parameters")
        param_layout = QGridLayout(param_group)

        row = 0
        param_layout.addWidget(QLabel("Motion Threshold:"), row, 0)
        self.motion_threshold = QSpinBox()
        self.motion_threshold.setRange(1, 255)
        self.motion_threshold.setValue(10)
        self.motion_threshold.setToolTip("Minimum pixel intensity change to consider as motion (1-255).\n"
                                        "Lower values = more sensitive, detects subtle motion, more false positives.\n"
                                        "Higher values = less sensitive, only strong motion, fewer false positives.\n"
                                        "Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.")
        param_layout.addWidget(self.motion_threshold, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Min Area (px):"), row, 0)
        self.min_detection_area = QSpinBox()
        self.min_detection_area.setRange(1, 100000)
        self.min_detection_area.setValue(5)
        self.min_detection_area.setToolTip("Minimum detection area in pixels (1-100000).\n"
                                          "Filters out very small detections (noise, insects, raindrops).\n"
                                          "Lower values = detect smaller objects, more noise.\n"
                                          "Higher values = only large objects, less noise.\n"
                                          "Recommended: 5-10 for person detection, 50-100 for vehicle detection.")
        param_layout.addWidget(self.min_detection_area, row, 1)

        row += 1
        param_layout.addWidget(QLabel("Max Area (px):"), row, 0)
        self.max_detection_area = QSpinBox()
        self.max_detection_area.setRange(10, 1000000)
        self.max_detection_area.setValue(1000)
        self.max_detection_area.setToolTip("Maximum detection area in pixels (10-1000000).\n"
                                          "Filters out very large detections (shadows, clouds, global lighting changes).\n"
                                          "Lower values = only small/medium objects.\n"
                                          "Higher values = allow large objects.\n"
                                          "Recommended: 1000 for people, 10000 for vehicles, higher for large objects.")
        param_layout.addWidget(self.max_detection_area, row, 1)

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
        self.persistence_frames.setValue(3)
        self.persistence_frames.setToolTip("Size of temporal window for persistence filtering (2-30 frames).\n"
                                          "Motion must appear in N out of M consecutive frames to be confirmed.\n"
                                          "Larger values = longer memory, more stable, slower response.\n"
                                          "Smaller values = shorter memory, faster response, more flicker.\n"
                                          "Recommended: 3 for 30fps video (100ms window), 5 for 60fps.")
        persist_layout.addWidget(self.persistence_frames, 0, 1)

        persist_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.persistence_threshold = QSpinBox()
        self.persistence_threshold.setRange(1, 30)
        self.persistence_threshold.setValue(2)
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
        self.bg_history.setValue(50)
        self.bg_history.setToolTip("Number of frames to learn background model (10-500).\n"
                                   "Only applies to MOG2 and KNN algorithms.\n"
                                   "Longer history = adapts slower to lighting changes, more stable.\n"
                                   "Shorter history = adapts faster, less stable.\n"
                                   "Recommended: 50 (~1.7 sec at 30fps) for general use.")
        bg_layout.addWidget(self.bg_history, 0, 1)

        bg_layout.addWidget(QLabel("Variance Threshold:"), 1, 0)
        self.bg_var_threshold = QDoubleSpinBox()
        self.bg_var_threshold.setRange(1.0, 100.0)
        self.bg_var_threshold.setValue(10.0)
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
        self.camera_movement_threshold.setValue(15)
        self.camera_movement_threshold.setToolTip("Percentage of frame with motion to consider as camera movement (1-100%).\n"
                                                  "If more than this % of pixels show motion, pause detection.\n"
                                                  "Lower values = detect camera movement sooner (more pauses).\n"
                                                  "Higher values = tolerate more motion before pausing (fewer pauses).\n"
                                                  "Recommended: 15% for drone/handheld, 30% for shaky tripod.")
        cam_thresh_layout.addWidget(self.camera_movement_threshold)
        self.camera_movement_label = QLabel("15%")
        cam_thresh_layout.addWidget(self.camera_movement_label)
        cam_layout.addLayout(cam_thresh_layout)

        layout.addWidget(cam_group)
        layout.addStretch()

        return widget

    def _create_color_tab(self) -> QWidget:
        """Create Color Anomaly tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable Color
        self.enable_color_quantization = QCheckBox("Enable Color Quantization Detection")
        self.enable_color_quantization.setChecked(True)
        self.enable_color_quantization.setToolTip("Detect rare/unusual colors in the scene using color quantization.\n"
                                                  "Finds colors that appear infrequently (statistical anomalies).\n"
                                                  "Works well for: bright colored clothing, vehicles, equipment in natural scenes.\n"
                                                  "Can be combined with Motion Detection for more robust detection.")
        layout.addWidget(self.enable_color_quantization)

        # Quantization Parameters
        quant_group = QGroupBox("Quantization Parameters")
        quant_layout = QGridLayout(quant_group)

        quant_layout.addWidget(QLabel("Quantization Bits:"), 0, 0)
        bits_layout = QHBoxLayout()
        self.color_quantization_bits = QSlider(Qt.Horizontal)
        self.color_quantization_bits.setRange(3, 8)
        self.color_quantization_bits.setValue(4)
        self.color_quantization_bits.setToolTip("Number of bits for color quantization (3-8 bits).\n"
                                                "Controls color histogram resolution.\n"
                                                "Lower bits (3-4) = fewer bins, faster, more grouping, less precise.\n"
                                                "Higher bits (6-8) = more bins, slower, less grouping, more precise.\n"
                                                "Recommended: 4 bits (512 colors) for general use, 5 bits for detailed scenes.")
        bits_layout.addWidget(self.color_quantization_bits)
        self.color_bits_label = QLabel("4 bits")
        bits_layout.addWidget(self.color_bits_label)
        quant_layout.addLayout(bits_layout, 0, 1)

        quant_layout.addWidget(QLabel("Rarity Percentile:"), 1, 0)
        percentile_layout = QHBoxLayout()
        self.color_rarity_percentile = QSlider(Qt.Horizontal)
        self.color_rarity_percentile.setRange(0, 100)
        self.color_rarity_percentile.setValue(30)  # Default 30%
        self.color_rarity_percentile.setToolTip("Rarity threshold as percentile of color histogram (0-100%).\n"
                                               "Detects colors that appear in fewer pixels than this percentile.\n"
                                               "Lower values (10-20%) = only very rare colors (fewer detections).\n"
                                               "Higher values (40-60%) = include more common colors (more detections).\n"
                                               "Recommended: 30% for general use, 15-20% for high-specificity (bright objects only).")
        percentile_layout.addWidget(self.color_rarity_percentile)
        self.color_percentile_label = QLabel("30%")
        percentile_layout.addWidget(self.color_percentile_label)
        quant_layout.addLayout(percentile_layout, 1, 1)

        quant_layout.addWidget(QLabel("Min Area (px):"), 2, 0)
        self.color_min_detection_area = QSpinBox()
        self.color_min_detection_area.setRange(1, 10000)
        self.color_min_detection_area.setValue(15)
        self.color_min_detection_area.setToolTip("Minimum detection area for color anomalies in pixels (1-10000).\n"
                                                 "Filters out very small color patches (noise, specks).\n"
                                                 "Lower values = detect smaller colored objects, more noise.\n"
                                                 "Higher values = only larger colored regions, less noise.\n"
                                                 "Recommended: 15 for person detection, 50 for vehicles.")
        quant_layout.addWidget(self.color_min_detection_area, 2, 1)

        quant_layout.addWidget(QLabel("Max Area (px):"), 3, 0)
        self.color_max_detection_area = QSpinBox()
        self.color_max_detection_area.setRange(100, 1000000)
        self.color_max_detection_area.setValue(50000)
        self.color_max_detection_area.setToolTip("Maximum detection area for color anomalies in pixels (100-1000000).\n"
                                                 "Filters out very large color patches (false positives, large objects).\n"
                                                 "Lower values = only detect smaller colored objects.\n"
                                                 "Higher values = allow larger colored regions.\n"
                                                 "Recommended: 50000 for general use, 10000 for small objects only.")
        quant_layout.addWidget(self.color_max_detection_area, 3, 1)

        layout.addWidget(quant_group)

        # Hue Expansion
        hue_group = QGroupBox("Hue Expansion")
        hue_layout = QVBoxLayout(hue_group)

        self.enable_hue_expansion = QCheckBox("Enable Hue Expansion")
        self.enable_hue_expansion.setChecked(False)
        self.enable_hue_expansion.setToolTip("Expands detected rare colors to include similar hues.\n"
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
                                           "Expands rare hue detection by ±N hue values.\n"
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

    def _create_fusion_tab(self) -> QWidget:
        """Create Fusion & Temporal tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Fusion
        fusion_group = QGroupBox("Detection Fusion")
        fusion_layout = QVBoxLayout(fusion_group)

        self.enable_fusion = QCheckBox("Enable Fusion (when both motion and color enabled)")
        self.enable_fusion.setChecked(False)
        self.enable_fusion.setToolTip("Combines motion and color detections when both are enabled.\n"
                                      "Only active when both Motion and Color detection are ON.\n"
                                      "Different modes control how detections are merged.\n"
                                      "Recommended: ON for robust multi-modal detection.")
        fusion_layout.addWidget(self.enable_fusion)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Fusion Mode:"))
        self.fusion_mode = QComboBox()
        self.fusion_mode.addItems(["UNION", "INTERSECTION", "COLOR_PRIORITY", "MOTION_PRIORITY"])
        self.fusion_mode.setCurrentText("UNION")
        self.fusion_mode.setToolTip("How to combine motion and color detections:\n\n"
                                    "• UNION: Show all detections from both (most detections).\n"
                                    "  Use for: Maximum coverage, don't miss anything.\n\n"
                                    "• INTERSECTION: Only show detections found by both (fewest false positives).\n"
                                    "  Use for: High confidence, reduce false positives.\n\n"
                                    "• COLOR_PRIORITY: Show color detections + motion detections that match color.\n"
                                    "  Use for: Trust color more (e.g., bright colored objects).\n\n"
                                    "• MOTION_PRIORITY: Show motion detections + color detections that match motion.\n"
                                    "  Use for: Trust motion more (e.g., moving camouflaged objects).")
        mode_layout.addWidget(self.fusion_mode)
        mode_layout.addStretch()
        fusion_layout.addLayout(mode_layout)

        layout.addWidget(fusion_group)

        # Temporal Voting
        temporal_group = QGroupBox("Temporal Voting")
        temporal_layout = QVBoxLayout(temporal_group)

        self.enable_temporal_voting = QCheckBox("Enable Temporal Voting (reduce flicker)")
        self.enable_temporal_voting.setChecked(True)
        self.enable_temporal_voting.setToolTip("Smooths detections across frames using temporal consistency.\n"
                                               "Detections must appear in N out of M consecutive frames to be confirmed.\n"
                                               "Significantly reduces flickering false positives.\n"
                                               "Recommended: ON for all use cases (default).")
        temporal_layout.addWidget(self.enable_temporal_voting)

        window_layout = QGridLayout()
        window_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.temporal_window_frames = QSpinBox()
        self.temporal_window_frames.setRange(2, 30)
        self.temporal_window_frames.setValue(5)  # Default 5
        self.temporal_window_frames.setToolTip("Size of temporal voting window (2-30 frames).\n"
                                               "Detections must appear in N out of M consecutive frames.\n"
                                               "Larger values = longer memory, more stable, slower response to new objects.\n"
                                               "Smaller values = shorter memory, faster response, less stable.\n"
                                               "Recommended: 5 for 30fps (~167ms window), 7 for 60fps.")
        window_layout.addWidget(self.temporal_window_frames, 0, 1)

        window_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.temporal_threshold_frames = QSpinBox()
        self.temporal_threshold_frames.setRange(1, 30)
        self.temporal_threshold_frames.setValue(3)  # Default 3
        self.temporal_threshold_frames.setToolTip("Number of frames within window where detection must appear (N of M).\n"
                                                  "Higher values = more stringent, filters transient false positives.\n"
                                                  "Lower values = more lenient, faster response to new objects.\n"
                                                  "Must be ≤ Window Frames.\n"
                                                  "Recommended: 3 out of 5 (detection in 60% of frames).")
        window_layout.addWidget(self.temporal_threshold_frames, 1, 1)

        temporal_layout.addLayout(window_layout)
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

        # Detection Clustering
        cluster_group = QGroupBox("Detection Clustering")
        cluster_layout = QVBoxLayout(cluster_group)

        self.enable_detection_clustering = QCheckBox("Enable Detection Clustering")
        self.enable_detection_clustering.setChecked(False)  # Default OFF
        self.enable_detection_clustering.setToolTip("Combines nearby detections into single merged detection.\n"
                                                    "Groups detections whose centroids are within specified distance.\n"
                                                    "Merged detection encompasses all combined contours.\n"
                                                    "Useful for: Combining scattered patches of same object.\n"
                                                    "Recommended: OFF by default, ON if objects appear fragmented.")
        cluster_layout.addWidget(self.enable_detection_clustering)

        cluster_dist_layout = QGridLayout()
        cluster_dist_layout.addWidget(QLabel("Clustering Distance (px):"), 0, 0)
        self.clustering_distance = QSpinBox()
        self.clustering_distance.setRange(0, 500)
        self.clustering_distance.setValue(50)  # Default 50px
        self.clustering_distance.setToolTip("Maximum centroid distance to merge detections (0-500 pixels).\n"
                                           "Detections closer than this distance are combined into one.\n"
                                           "Lower values = only merge very close detections.\n"
                                           "Higher values = merge distant detections (may over-merge).\n"
                                           "Recommended: 50px for people, 100px for vehicles at 720p.")
        cluster_dist_layout.addWidget(self.clustering_distance, 0, 1)

        cluster_layout.addLayout(cluster_dist_layout)
        layout.addWidget(cluster_group)

        # Color Exclusion
        exclusion_group = QGroupBox("Color Exclusion")
        exclusion_layout = QVBoxLayout(exclusion_group)

        self.enable_color_exclusion = QCheckBox("Enable Color Exclusion")
        self.enable_color_exclusion.setChecked(False)
        self.enable_color_exclusion.setToolTip("Excludes specific colors from detection (background learning).\n"
                                               "Useful for ignoring known background colors (grass, sky, buildings).\n"
                                               "Select colors below to exclude from color anomaly detection.\n"
                                               "Recommended: Use to filter out dominant environmental colors.")
        exclusion_layout.addWidget(self.enable_color_exclusion)

        # Color hue toggles (separated by 20 degrees on 360° wheel)
        exclusion_layout.addWidget(QLabel("Exclude Colors (20° steps, 0-360°):"))

        # Create grid of color checkboxes
        colors_grid = QGridLayout()
        self.hue_color_toggles = []

        # Hue colors every 20 degrees on full 360° wheel (18 colors)
        # Format: (name, hue_degrees_360, hex_color_for_display)
        hue_colors = [
            ("Red", 0, "#FF0000"),
            ("Red-Orange", 20, "#FF3300"),
            ("Orange", 40, "#FF6600"),
            ("Yellow-Orange", 60, "#FF9900"),
            ("Yellow", 80, "#FFCC00"),
            ("Yellow-Green", 100, "#CCFF00"),
            ("Green", 120, "#00FF00"),
            ("Green-Cyan", 140, "#00FF66"),
            ("Cyan", 160, "#00FFCC"),
            ("Cyan-Blue", 180, "#00CCFF"),
            ("Blue", 200, "#0099FF"),
            ("Blue-Violet", 220, "#0066FF"),
            ("Violet", 240, "#0033FF"),
            ("Purple", 260, "#6600FF"),
            ("Magenta", 280, "#9900FF"),
            ("Pink-Magenta", 300, "#CC00FF"),
            ("Pink", 320, "#FF00CC"),
            ("Hot Pink", 340, "#FF0066"),
        ]

        for i, (name, hue_360, color_hex) in enumerate(hue_colors):
            checkbox = QCheckBox(name)
            checkbox.setStyleSheet(f"QCheckBox {{ color: {color_hex}; font-weight: bold; }}")
            checkbox.setChecked(False)
            checkbox.setProperty("hue_value_360", hue_360)  # Store hue in 360° scale
            self.hue_color_toggles.append(checkbox)

            row = i // 3
            col = i % 3
            colors_grid.addWidget(checkbox, row, col)

        exclusion_layout.addLayout(colors_grid)

        layout.addWidget(exclusion_group)
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
        self.render_shape = QComboBox()
        self.render_shape.addItems(["Box", "Circle", "Dot", "Off"])
        self.render_shape.setCurrentText("Circle")
        self.render_shape.setToolTip("Shape to draw around detections:\n\n"
                                     "• Box: Rectangle around detection bounding box.\n"
                                     "  Use for: Precise boundaries, technical visualization.\n\n"
                                     "• Circle: Circle encompassing detection (150% of contour radius).\n"
                                     "  Use for: General use, cleaner look (default).\n\n"
                                     "• Dot: Small dot at detection centroid.\n"
                                     "  Use for: Minimal overlay, fast rendering.\n\n"
                                     "• Off: No shape overlay (only thumbnails/text if enabled).\n"
                                     "  Use for: Clean video with minimal overlays.")
        shape_layout.addWidget(self.render_shape, 0, 1)

        layout.addWidget(shape_group)

        # Text & Contours
        vis_group = QGroupBox("Visual Options")
        vis_layout = QVBoxLayout(vis_group)

        self.render_text = QCheckBox("Show Text Labels (slower)")
        self.render_text.setToolTip("Displays text labels near detections showing detection information.\n"
                                    "Adds ~5-15ms processing overhead depending on detection count.\n"
                                    "Labels show: detection type, confidence, area.\n"
                                    "Recommended: OFF for speed, ON for debugging/analysis.")
        vis_layout.addWidget(self.render_text)

        self.render_contours = QCheckBox("Show Contours (slowest)")
        self.render_contours.setToolTip("Draws exact detection contours (pixel-precise boundaries).\n"
                                       "Adds ~10-20ms processing overhead (very expensive).\n"
                                       "Shows exact shape detected by algorithm.\n"
                                       "Recommended: OFF for speed, ON only for detailed analysis.")
        vis_layout.addWidget(self.render_contours)

        self.use_detection_color = QCheckBox("Use Detection Color (hue @ 100% sat/val for color anomalies)")
        self.use_detection_color.setChecked(True)  # Default ON
        self.use_detection_color.setToolTip("Color the detection overlay based on detected color.\n"
                                            "For color anomalies: Uses the detected hue at 100% saturation/value.\n"
                                            "For motion detections: Uses default color (green/blue).\n"
                                            "Helps visually identify what color was detected.\n"
                                            "Recommended: ON for color detection, OFF for motion-only.")
        vis_layout.addWidget(self.use_detection_color)

        layout.addWidget(vis_group)

        # Detection Limits
        limit_group = QGroupBox("Performance Limits")
        limit_layout = QGridLayout(limit_group)

        limit_layout.addWidget(QLabel("Max Detections:"), 0, 0)
        self.max_detections_to_render = QSpinBox()
        self.max_detections_to_render.setRange(0, 1000)
        self.max_detections_to_render.setValue(100)
        self.max_detections_to_render.setSpecialValueText("Unlimited")
        self.max_detections_to_render.setToolTip("Maximum number of detections to render on screen (0-1000).\n"
                                                 "Prevents rendering slowdown when hundreds of detections occur.\n"
                                                 "Shows highest confidence detections first.\n"
                                                 "0 = Unlimited (may cause lag with many detections).\n"
                                                 "Recommended: 100 for general use, 50 for complex rendering (text+contours).")
        limit_layout.addWidget(self.max_detections_to_render, 0, 1)

        layout.addWidget(limit_group)

        # Overlay Options
        overlay_group = QGroupBox("Overlay Options")
        overlay_layout = QVBoxLayout(overlay_group)

        self.show_timing_overlay = QCheckBox("Show Timing Overlay (FPS, metrics)")
        self.show_timing_overlay.setChecked(False)  # Default OFF
        self.show_timing_overlay.setToolTip("Displays detailed timing information on video overlay.\n"
                                           "Shows: FPS, processing time, detection counts, pipeline breakdown.\n"
                                           "Useful for performance tuning and debugging.\n"
                                           "Recommended: OFF for clean view, ON when optimizing performance.")
        overlay_layout.addWidget(self.show_timing_overlay)

        self.show_detection_thumbnails = QCheckBox("Show Detection Thumbnails (auto-fit window width)")
        self.show_detection_thumbnails.setChecked(False)  # Default OFF
        self.show_detection_thumbnails.setToolTip("Shows zoomed thumbnails of detected objects below video.\n"
                                                  "Number of thumbnails adjusts automatically to window width (1-20).\n"
                                                  "Thumbnails persist for 2 seconds minimum (reduces flicker).\n"
                                                  "Useful for: Close-up view of detections, tracking specific objects.\n"
                                                  "Recommended: ON for analysis, OFF for clean display.")
        overlay_layout.addWidget(self.show_detection_thumbnails)

        layout.addWidget(overlay_group)
        layout.addStretch()

        return widget

    def connect_signals(self):
        """Connect all control signals."""
        # Processing
        self.resolution_preset.currentTextChanged.connect(self.on_resolution_preset_changed)
        self.processing_width.valueChanged.connect(self.emit_config)
        self.processing_height.valueChanged.connect(self.emit_config)
        self.threaded_capture.toggled.connect(self.emit_config)
        self.render_at_processing_res.toggled.connect(self.emit_config)

        # Motion
        self.enable_motion.toggled.connect(self.emit_config)
        self.motion_algorithm.currentTextChanged.connect(self.emit_config)
        self.motion_threshold.valueChanged.connect(self.emit_config)
        self.min_detection_area.valueChanged.connect(self.emit_config)
        self.max_detection_area.valueChanged.connect(self.emit_config)
        self.blur_kernel_size.valueChanged.connect(self.emit_config)
        self.morphology_kernel_size.valueChanged.connect(self.emit_config)
        self.persistence_frames.valueChanged.connect(self.emit_config)
        self.persistence_threshold.valueChanged.connect(self.emit_config)
        self.bg_history.valueChanged.connect(self.emit_config)
        self.bg_var_threshold.valueChanged.connect(self.emit_config)
        self.bg_detect_shadows.toggled.connect(self.emit_config)
        self.pause_on_camera_movement.toggled.connect(self.emit_config)
        self.camera_movement_threshold.valueChanged.connect(self.update_camera_movement_label)

        # Color
        self.enable_color_quantization.toggled.connect(self.emit_config)
        self.color_quantization_bits.valueChanged.connect(self.update_color_bits_label)
        self.color_rarity_percentile.valueChanged.connect(self.update_color_percentile_label)
        self.color_min_detection_area.valueChanged.connect(self.emit_config)
        self.enable_hue_expansion.toggled.connect(self.emit_config)
        self.hue_expansion_range.valueChanged.connect(self.update_hue_range_label)

        # Fusion
        self.enable_fusion.toggled.connect(self.emit_config)
        self.fusion_mode.currentTextChanged.connect(self.emit_config)
        self.enable_temporal_voting.toggled.connect(self.emit_config)
        self.temporal_window_frames.valueChanged.connect(self.emit_config)
        self.temporal_threshold_frames.valueChanged.connect(self.emit_config)

        # FPR
        self.enable_aspect_ratio_filter.toggled.connect(self.emit_config)
        self.min_aspect_ratio.valueChanged.connect(self.emit_config)
        self.max_aspect_ratio.valueChanged.connect(self.emit_config)
        self.enable_detection_clustering.toggled.connect(self.emit_config)
        self.clustering_distance.valueChanged.connect(self.emit_config)
        self.enable_color_exclusion.toggled.connect(self.emit_config)

        # Hue color toggles
        for toggle in self.hue_color_toggles:
            toggle.toggled.connect(self.emit_config)

        # Rendering
        self.render_shape.currentTextChanged.connect(self.emit_config)
        self.render_text.toggled.connect(self.emit_config)
        self.render_contours.toggled.connect(self.emit_config)
        self.use_detection_color.toggled.connect(self.emit_config)
        self.max_detections_to_render.valueChanged.connect(self.emit_config)
        self.show_timing_overlay.toggled.connect(self.emit_config)
        self.show_detection_thumbnails.toggled.connect(self.emit_config)

    def update_camera_movement_label(self):
        """Update camera movement threshold label."""
        value = self.camera_movement_threshold.value()
        self.camera_movement_label.setText(f"{value}%")
        self.emit_config()

    def update_color_bits_label(self):
        """Update color bits label."""
        value = self.color_quantization_bits.value()
        self.color_bits_label.setText(f"{value} bits")
        self.emit_config()

    def update_color_percentile_label(self):
        """Update color percentile label."""
        value = self.color_rarity_percentile.value()
        self.color_percentile_label.setText(f"{value}%")
        self.emit_config()

    def update_hue_range_label(self):
        """Update hue expansion range label."""
        value = self.hue_expansion_range.value()
        self.hue_range_label.setText(f"±{value} (~{value*2}°)")
        self.emit_config()

    def on_resolution_preset_changed(self, preset_name: str):
        """Handle resolution preset change."""
        if preset_name == "Custom":
            # Enable manual inputs
            self.processing_width.setEnabled(True)
            self.processing_height.setEnabled(True)
        else:
            # Disable manual inputs and set preset values
            self.processing_width.setEnabled(False)
            self.processing_height.setEnabled(False)

            resolution = self.resolution_presets.get(preset_name)
            # Handle "Original" (None) and other presets
            if resolution and resolution != "custom":
                self.processing_width.setValue(resolution[0])
                self.processing_height.setValue(resolution[1])
            elif preset_name == "Original":
                # "Original" means no downsampling - values don't matter, will be ignored
                pass

        self.emit_config()

    def emit_config(self):
        """Emit current configuration."""
        config = self.get_config()
        self.configChanged.emit(config)

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        # Map string algorithm names to enum
        algo_map = {
            "FRAME_DIFF": MotionAlgorithm.FRAME_DIFF,
            "MOG2": MotionAlgorithm.MOG2,
            "KNN": MotionAlgorithm.KNN
        }

        # Map string fusion modes to enum
        fusion_map = {
            "UNION": FusionMode.UNION,
            "INTERSECTION": FusionMode.INTERSECTION,
            "COLOR_PRIORITY": FusionMode.COLOR_PRIORITY,
            "MOTION_PRIORITY": FusionMode.MOTION_PRIORITY
        }

        # Map shape names to indices
        shape_map = {"Box": 0, "Circle": 1, "Dot": 2, "Off": 3}

        # Build excluded hue ranges from toggles
        excluded_hue_ranges = []
        tolerance = 10.0  # ±10 degrees for each color (20 degree separation on 360° wheel)

        for toggle in self.hue_color_toggles:
            if toggle.isChecked():
                hue_360 = toggle.property("hue_value_360")

                # Convert from 360° scale to OpenCV's 0-179 scale
                # OpenCV uses hue/2 to fit in 8-bit (0-179 instead of 0-359)
                hue_cv = hue_360 / 2.0

                # Apply tolerance in OpenCV scale (convert tolerance too)
                tolerance_cv = tolerance / 2.0  # ±10° becomes ±5 in OpenCV scale
                hue_min = max(0, hue_cv - tolerance_cv)
                hue_max = min(179, hue_cv + tolerance_cv)
                excluded_hue_ranges.append((hue_min, hue_max))

        # Handle "Original" resolution preset (no downsampling)
        current_preset = self.resolution_preset.currentText()
        if current_preset == "Original":
            # Use very large values so no downsampling occurs
            processing_width = 99999
            processing_height = 99999
        else:
            processing_width = self.processing_width.value()
            processing_height = self.processing_height.value()

        config = {
            'processing_width': processing_width,
            'processing_height': processing_height,
            'use_threaded_capture': self.threaded_capture.isChecked(),
            'render_at_processing_res': self.render_at_processing_res.isChecked(),

            'enable_motion': self.enable_motion.isChecked(),
            'motion_algorithm': algo_map[self.motion_algorithm.currentText()],
            'motion_threshold': self.motion_threshold.value(),
            'min_detection_area': self.min_detection_area.value(),
            'max_detection_area': self.max_detection_area.value(),
            'blur_kernel_size': self.blur_kernel_size.value(),
            'morphology_kernel_size': self.morphology_kernel_size.value(),
            'enable_morphology': self.enable_morphology.isChecked(),
            'persistence_frames': self.persistence_frames.value(),
            'persistence_threshold': self.persistence_threshold.value(),
            'bg_history': self.bg_history.value(),
            'bg_var_threshold': self.bg_var_threshold.value(),
            'bg_detect_shadows': self.bg_detect_shadows.isChecked(),
            'pause_on_camera_movement': self.pause_on_camera_movement.isChecked(),
            'camera_movement_threshold': self.camera_movement_threshold.value() / 100.0,

            'enable_color_quantization': self.enable_color_quantization.isChecked(),
            'color_quantization_bits': self.color_quantization_bits.value(),
            'color_rarity_percentile': float(self.color_rarity_percentile.value()),
            'color_min_detection_area': self.color_min_detection_area.value(),
            'color_max_detection_area': self.color_max_detection_area.value(),
            'enable_hue_expansion': self.enable_hue_expansion.isChecked(),
            'hue_expansion_range': self.hue_expansion_range.value(),

            'enable_fusion': self.enable_fusion.isChecked(),
            'fusion_mode': fusion_map[self.fusion_mode.currentText()],
            'enable_temporal_voting': self.enable_temporal_voting.isChecked(),
            'temporal_window_frames': self.temporal_window_frames.value(),
            'temporal_threshold_frames': self.temporal_threshold_frames.value(),

            'enable_aspect_ratio_filter': self.enable_aspect_ratio_filter.isChecked(),
            'min_aspect_ratio': self.min_aspect_ratio.value(),
            'max_aspect_ratio': self.max_aspect_ratio.value(),
            'enable_detection_clustering': self.enable_detection_clustering.isChecked(),
            'clustering_distance': self.clustering_distance.value(),
            'enable_color_exclusion': self.enable_color_exclusion.isChecked(),
            'excluded_hue_ranges': excluded_hue_ranges,

            'render_shape': shape_map[self.render_shape.currentText()],
            'render_text': self.render_text.isChecked(),
            'render_contours': self.render_contours.isChecked(),
            'use_detection_color_for_rendering': self.use_detection_color.isChecked(),
            'max_detections_to_render': self.max_detections_to_render.value(),
            'show_timing_overlay': self.show_timing_overlay.isChecked(),
            'show_detection_thumbnails': self.show_detection_thumbnails.isChecked(),
        }

        return config


class StreamControlWidget(QWidget):
    """Stream connection and control widget."""

    connectRequested = Signal(str, str)
    disconnectRequested = Signal()
    startRecordingRequested = Signal()
    stopRecordingRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup stream control interface."""
        layout = QVBoxLayout(self)

        # Connection group
        connection_group = QGroupBox("Stream Connection")
        connection_layout = QGridLayout(connection_group)

        # Stream URL with browse button for files
        connection_layout.addWidget(QLabel("Stream URL:"), 0, 0)

        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Click to browse for video file...")
        self.url_input.setToolTip("Enter stream URL or file path, or click to browse for video file.\n"
                                  "Supported formats:\n"
                                  "• Video Files: .mp4, .avi, .mov, .mkv, .flv, .wmv, .m4v, .3gp, .webm\n"
                                  "• RTMP Streams: rtmp://server:port/app/stream\n"
                                  "• HDMI Capture: Device index (0, 1, 2, etc.)")
        url_layout.addWidget(self.url_input, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setToolTip("Browse for video file.\nOpens file dialog to select a video file from your computer.")
        url_layout.addWidget(self.browse_button)

        connection_layout.addLayout(url_layout, 0, 1)

        # Stream type
        connection_layout.addWidget(QLabel("Stream Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["File", "HDMI Capture", "RTMP Stream"])
        self.type_combo.setToolTip("Select the type of video source:\n\n"
                                   "• File: Pre-recorded video file from disk.\n"
                                   "  Supports playback controls (play/pause/seek).\n\n"
                                   "• HDMI Capture: Live video from HDMI capture card.\n"
                                   "  Enter device index (usually 0 for first device).\n\n"
                                   "• RTMP Stream: Network video stream (live or file-based).\n"
                                   "  Enter full RTMP URL.")
        connection_layout.addWidget(self.type_combo, 1, 1)

        # Connection buttons
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.connect_button.setToolTip("Connect to the specified stream/file.\n"
                                       "Starts video playback and detection processing.")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setToolTip("Disconnect from current stream.\nStops video playback and detection processing.")

        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        # Status display
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")

        # Performance display
        performance_group = QGroupBox("Performance")
        performance_layout = QGridLayout(performance_group)

        self.fps_label = QLabel("FPS: --")
        self.latency_label = QLabel("Processing: -- ms")
        self.detections_label = QLabel("Detections: --")

        performance_layout.addWidget(self.fps_label, 0, 0)
        performance_layout.addWidget(self.latency_label, 0, 1)
        performance_layout.addWidget(self.detections_label, 1, 0)

        # Recording group
        recording_group = QGroupBox("Recording")
        recording_layout = QVBoxLayout(recording_group)

        # Recording buttons
        recording_button_layout = QHBoxLayout()
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

        recording_button_layout.addWidget(self.start_recording_btn)
        recording_button_layout.addWidget(self.stop_recording_btn)

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

        recording_layout.addLayout(recording_button_layout)
        recording_layout.addWidget(self.recording_status)
        recording_layout.addWidget(self.recording_info)

        # Add to main layout
        layout.addWidget(connection_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(performance_group)
        layout.addWidget(recording_group)
        layout.addStretch()

    def connect_signals(self):
        """Connect UI signals."""
        self.connect_button.clicked.connect(self.request_connect)
        self.disconnect_button.clicked.connect(self.disconnectRequested.emit)
        self.type_combo.currentTextChanged.connect(self.on_stream_type_changed)
        self.browse_button.clicked.connect(self.browse_for_file)
        self.url_input.mousePressEvent = self.on_url_input_clicked
        self.start_recording_btn.clicked.connect(self.startRecordingRequested.emit)
        self.stop_recording_btn.clicked.connect(self.stopRecordingRequested.emit)

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
        processing_time = stats.get('total_ms', 0)
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
        if self.type_combo.currentText() == "File":
            self.browse_for_file()
        else:
            QLineEdit.mousePressEvent(self.url_input, event)


class PlaybackControlBar(QWidget):
    """Video playback control bar with play/pause and timeline scrubbing."""

    playPauseClicked = Signal()
    seekRequested = Signal(float)  # time in seconds

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(60)
        self.setup_ui()

        # State
        self._is_playing = True
        self._duration = 0.0
        self._updating_from_signal = False  # Prevent feedback loop

    def setup_ui(self):
        """Setup playback control UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Timeline layout
        timeline_layout = QHBoxLayout()

        # Current time label
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setMinimumWidth(50)
        timeline_layout.addWidget(self.current_time_label)

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1000)  # 0-1000 for smooth scrubbing
        self.timeline_slider.setValue(0)
        self.timeline_slider.sliderPressed.connect(self.on_slider_pressed)
        self.timeline_slider.sliderReleased.connect(self.on_slider_released)
        self.timeline_slider.valueChanged.connect(self.on_slider_moved)
        timeline_layout.addWidget(self.timeline_slider, 1)

        # Total time label
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setMinimumWidth(50)
        timeline_layout.addWidget(self.total_time_label)

        layout.addLayout(timeline_layout)

        # Control buttons layout
        buttons_layout = QHBoxLayout()

        # Play/Pause button
        self.play_pause_button = QPushButton("⏸ Pause")
        self.play_pause_button.setMinimumWidth(100)
        self.play_pause_button.setStyleSheet("QPushButton { font-size: 14px; padding: 5px; }")
        self.play_pause_button.clicked.connect(self.on_play_pause_clicked)
        buttons_layout.addWidget(self.play_pause_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Initially hide (only show for video files)
        self.setVisible(False)

    def on_play_pause_clicked(self):
        """Handle play/pause button click."""
        self.playPauseClicked.emit()

    def on_slider_pressed(self):
        """Handle slider press (user starting to drag)."""
        # Don't update slider position from signals while user is dragging
        self._updating_from_signal = True

    def on_slider_released(self):
        """Handle slider release (user finished dragging)."""
        self._updating_from_signal = False
        # Emit seek request
        if self._duration > 0:
            position_fraction = self.timeline_slider.value() / 1000.0
            seek_time = position_fraction * self._duration
            self.seekRequested.emit(seek_time)

    def on_slider_moved(self, value):
        """Handle slider position change (update time label during drag)."""
        if self._duration > 0:
            position_fraction = value / 1000.0
            current_time = position_fraction * self._duration
            self.current_time_label.setText(self.format_time(current_time))

    def update_position(self, current_time: float, total_duration: float):
        """Update playback position from stream."""
        self._duration = total_duration

        # Update total time label
        self.total_time_label.setText(self.format_time(total_duration))

        # Update slider position (only if user isn't dragging)
        if not self._updating_from_signal:
            if total_duration > 0:
                position_fraction = current_time / total_duration
                slider_value = int(position_fraction * 1000)
                self.timeline_slider.setValue(slider_value)
                self.current_time_label.setText(self.format_time(current_time))

    def update_play_state(self, is_playing: bool):
        """Update play/pause button state."""
        self._is_playing = is_playing
        if is_playing:
            self.play_pause_button.setText("⏸ Pause")
        else:
            self.play_pause_button.setText("▶ Play")

    def format_time(self, seconds: float) -> str:
        """Format time in seconds to MM:SS format."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def show_for_file(self):
        """Show the playback controls (for video files)."""
        self.setVisible(True)

    def hide_for_stream(self):
        """Hide the playback controls (for live streams)."""
        self.setVisible(False)


class IntegratedDetectionViewer(QMainWindow):
    """Main integrated detection viewer window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Core services
        self.stream_manager = StreamManager()
        self.integrated_detector = RealtimeIntegratedDetector()
        self.recording_manager = RecordingManager("./recordings")

        # UI components
        self.video_display = None
        self.thumbnail_widget = None
        self.integrated_controls = None
        self.stream_controls = None
        self.playback_controls = None

        # State
        self.is_detecting = False
        self.is_recording = False
        self.current_detections = []
        self.current_frame = None
        self.stream_resolution = (640, 480)

        # Excluded hue ranges (for color exclusion)
        self.excluded_hue_ranges = []

        # End-to-end profiling
        self._profiling_enabled = True
        self._profiling_frame_count = 0
        self._profiling_data = {
            'qt_signal_ms': [],
            'detection_processing_ms': [],
            'qt_display_ms': [],
            'total_pipeline_ms': []
        }
        self._last_frame_timestamp = time.time()

        # Frame dropping to prevent queue backup
        self._is_processing = False
        self._dropped_frames = 0

        self.setup_ui()
        self.connect_signals()

        # Apply default configuration
        self.update_detection_config(self.integrated_controls.get_config())

        self.logger.info("Integrated Detection Viewer initialized")

    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("ADIAT - Real-Time Anomaly Detection")
        self.setMinimumSize(1400, 900)

        # Set tooltip stylesheet for better readability
        self.setStyleSheet("""
            QToolTip {
                background-color: #E1F5FE;
                color: #01579B;
                border: 1px solid #0288D1;
                padding: 5px;
                border-radius: 3px;
                font-size: 10pt;
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
        video_layout.addWidget(self.video_display, 1)

        # Playback control bar (for video files)
        self.playback_controls = PlaybackControlBar()
        video_layout.addWidget(self.playback_controls, 0)

        # Detection thumbnails (always visible to prevent video jumping)
        self.thumbnail_widget = DetectionThumbnailWidget()
        video_layout.addWidget(self.thumbnail_widget, 0)

        # Detection info panel
        info_panel = QTextEdit()
        info_panel.setMaximumHeight(120)
        info_panel.setReadOnly(True)
        info_panel.setPlaceholderText("Detection information will appear here...")
        video_layout.addWidget(info_panel, 0)
        self.info_panel = info_panel

        # Control panel
        control_widget = QWidget()
        control_widget.setMaximumWidth(450)
        control_layout = QVBoxLayout(control_widget)

        # Stream controls
        self.stream_controls = StreamControlWidget()
        control_layout.addWidget(self.stream_controls)

        # Integrated detection controls
        self.integrated_controls = IntegratedDetectionControlWidget()
        control_layout.addWidget(self.integrated_controls)

        # Add to splitter
        splitter.addWidget(video_widget)
        splitter.addWidget(control_widget)
        splitter.setSizes([900, 500])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Connect to stream to begin detection")

    def connect_signals(self):
        """Connect all signals and slots."""
        # Stream manager signals
        self.stream_manager.frameReceived.connect(self.process_frame)
        self.stream_manager.connectionChanged.connect(self.on_connection_changed)
        self.stream_manager.videoPositionChanged.connect(self.on_video_position_changed)

        # Integrated detector signals
        self.integrated_detector.frameProcessed.connect(self.on_frame_processed)
        self.integrated_detector.performanceUpdate.connect(self.on_performance_update)

        # UI control signals
        self.stream_controls.connectRequested.connect(self.connect_to_stream)
        self.stream_controls.disconnectRequested.connect(self.disconnect_from_stream)
        self.stream_controls.startRecordingRequested.connect(self.start_recording)
        self.stream_controls.stopRecordingRequested.connect(self.stop_recording)
        self.integrated_controls.configChanged.connect(self.update_detection_config)

        # Playback control signals
        self.playback_controls.playPauseClicked.connect(self.on_play_pause_clicked)
        self.playback_controls.seekRequested.connect(self.on_seek_requested)

        # Recording manager signals
        self.recording_manager.recordingStateChanged.connect(self.on_recording_state_changed)
        self.recording_manager.recordingStats.connect(self.on_recording_stats)

    def connect_to_stream(self, url: str, stream_type_str: str):
        """Connect to stream."""
        try:
            # Convert string to enum
            stream_type = StreamType.RTMP
            if stream_type_str.lower() == 'file':
                stream_type = StreamType.FILE
            elif stream_type_str.lower() == 'hdmi capture':
                stream_type = StreamType.HDMI_CAPTURE

            success = self.stream_manager.connect_to_stream(url, stream_type)
            if success:
                self.is_detecting = True
                self.status_bar.showMessage(f"Connecting to {url}...")
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
        self.status_bar.showMessage("Disconnected")

    def update_detection_config(self, config_dict: Dict[str, Any]):
        """Update integrated detection configuration."""
        try:
            # Create IntegratedDetectionConfig from dictionary
            config = IntegratedDetectionConfig(
                processing_width=config_dict['processing_width'],
                processing_height=config_dict['processing_height'],
                use_threaded_capture=config_dict['use_threaded_capture'],
                render_at_processing_res=config_dict['render_at_processing_res'],

                enable_motion=config_dict['enable_motion'],
                motion_algorithm=config_dict['motion_algorithm'],
                motion_threshold=config_dict['motion_threshold'],
                min_detection_area=config_dict['min_detection_area'],
                max_detection_area=config_dict['max_detection_area'],
                blur_kernel_size=config_dict['blur_kernel_size'],
                morphology_kernel_size=config_dict['morphology_kernel_size'],
                enable_morphology=config_dict['enable_morphology'],
                persistence_frames=config_dict['persistence_frames'],
                persistence_threshold=config_dict['persistence_threshold'],
                bg_history=config_dict['bg_history'],
                bg_var_threshold=config_dict['bg_var_threshold'],
                bg_detect_shadows=config_dict['bg_detect_shadows'],
                pause_on_camera_movement=config_dict['pause_on_camera_movement'],
                camera_movement_threshold=config_dict['camera_movement_threshold'],

                enable_color_quantization=config_dict['enable_color_quantization'],
                color_quantization_bits=config_dict['color_quantization_bits'],
                color_rarity_percentile=config_dict['color_rarity_percentile'],
                color_min_detection_area=config_dict['color_min_detection_area'],
                color_max_detection_area=config_dict['color_max_detection_area'],
                enable_hue_expansion=config_dict['enable_hue_expansion'],
                hue_expansion_range=config_dict['hue_expansion_range'],

                enable_fusion=config_dict['enable_fusion'],
                fusion_mode=config_dict['fusion_mode'],
                enable_temporal_voting=config_dict['enable_temporal_voting'],
                temporal_window_frames=config_dict['temporal_window_frames'],
                temporal_threshold_frames=config_dict['temporal_threshold_frames'],

                enable_aspect_ratio_filter=config_dict['enable_aspect_ratio_filter'],
                min_aspect_ratio=config_dict['min_aspect_ratio'],
                max_aspect_ratio=config_dict['max_aspect_ratio'],
                enable_detection_clustering=config_dict['enable_detection_clustering'],
                clustering_distance=config_dict['clustering_distance'],
                enable_color_exclusion=config_dict['enable_color_exclusion'],
                excluded_hue_ranges=config_dict['excluded_hue_ranges'],

                render_shape=config_dict['render_shape'],
                render_text=config_dict['render_text'],
                render_contours=config_dict['render_contours'],
                use_detection_color_for_rendering=config_dict['use_detection_color_for_rendering'],
                max_detections_to_render=config_dict['max_detections_to_render'],
                show_timing_overlay=config_dict['show_timing_overlay'],
            )

            self.integrated_detector.update_config(config)

        except Exception as e:
            self.logger.error(f"Error updating config: {e}")

    def process_frame(self, frame: np.ndarray, timestamp: float):
        """Process incoming frame from stream."""
        if not self.is_detecting:
            return

        # Drop frame if still processing previous frame (prevents queue backup)
        if self._is_processing:
            self._dropped_frames += 1
            if self._dropped_frames % 30 == 0:
                self.logger.warning(f"Dropped {self._dropped_frames} frames due to processing backlog")
            return

        self._is_processing = True

        # Start end-to-end timing
        pipeline_start = time.perf_counter()
        qt_signal_time = (pipeline_start - timestamp) * 1000  # Time from capture to Qt signal delivery

        try:
            if frame is None or frame.size == 0:
                self._is_processing = False
                return

            # Store current frame
            self.current_frame = frame.copy()

            # Update stream resolution
            try:
                height, width = frame.shape[:2]
                self.stream_resolution = (width, height)
            except Exception as e:
                self.logger.error(f"Resolution update failed: {e}")

            # Process through integrated detector
            detection_start = time.perf_counter()
            annotated_frame, detections, timings = self.integrated_detector.process_frame(frame, timestamp)
            detection_time = (time.perf_counter() - detection_start) * 1000

            # Update display
            display_start = time.perf_counter()
            self.video_display.update_frame(annotated_frame)
            display_time = (time.perf_counter() - display_start) * 1000

            # Store detections
            self.current_detections = detections

            # Update thumbnails if enabled (widget always visible to prevent jumping)
            config = self.integrated_controls.get_config()
            if config.get('show_detection_thumbnails', False) and len(detections) > 0:
                # Pass resolution information to correctly scale detection coordinates
                processing_res = (config['processing_width'], config['processing_height'])
                original_res = (frame.shape[1], frame.shape[0])  # (width, height) from frame
                self.thumbnail_widget.update_thumbnails(
                    frame, detections, zoom=3.0,
                    processing_resolution=processing_res,
                    original_resolution=original_res
                )
            else:
                self.thumbnail_widget.clear_thumbnails()

            # End-to-end profiling
            total_pipeline_time = (time.perf_counter() - pipeline_start) * 1000

            if self._profiling_enabled:
                self._profiling_frame_count += 1
                self._profiling_data['qt_signal_ms'].append(qt_signal_time)
                self._profiling_data['detection_processing_ms'].append(detection_time)
                self._profiling_data['qt_display_ms'].append(display_time)
                self._profiling_data['total_pipeline_ms'].append(total_pipeline_time)

                # Log detailed profiling every 60 frames (every ~2 seconds at 30fps)
                if self._profiling_frame_count % 60 == 0:
                    avg_qt_signal = sum(self._profiling_data['qt_signal_ms'][-60:]) / 60
                    avg_detection = sum(self._profiling_data['detection_processing_ms'][-60:]) / 60
                    avg_display = sum(self._profiling_data['qt_display_ms'][-60:]) / 60
                    avg_total = sum(self._profiling_data['total_pipeline_ms'][-60:]) / 60

                    dropped_info = f", Dropped={self._dropped_frames}" if self._dropped_frames > 0 else ""
                    self.logger.info(f"[PROFILING] End-to-end averages (last 60 frames): "
                                   f"Qt Signal={avg_qt_signal:.1f}ms, "
                                   f"Detection={avg_detection:.1f}ms, "
                                   f"Display={avg_display:.1f}ms, "
                                   f"Total Pipeline={avg_total:.1f}ms, "
                                   f"Theoretical FPS={1000/avg_total:.1f}"
                                   f"{dropped_info}")

                    # Keep only last 300 samples to avoid memory bloat
                    for key in self._profiling_data:
                        if len(self._profiling_data[key]) > 300:
                            self._profiling_data[key] = self._profiling_data[key][-300:]

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
        finally:
            self._is_processing = False

    def on_frame_processed(self, annotated_frame: np.ndarray, detections: List[Detection], metrics):
        """Handle frame processing completion."""
        # Add frame to recording if active
        if self.is_recording:
            try:
                self.recording_manager.add_frame(annotated_frame, time.time())
            except Exception as e:
                self.logger.error(f"Recording failed: {e}")

        # Update info panel
        if detections:
            info_text = f"Detection Results ({len(detections)} found):\n"
            for i, detection in enumerate(detections[:5]):
                x, y, w, h = detection.bbox
                info_text += f"  #{i+1}: Type({detection.detection_type}) Pos({x},{y}) " \
                            f"Size({w}x{h}) Area({int(detection.area)}px) Conf({detection.confidence:.2f})\n"
        else:
            info_text = "No detections found."

        self.info_panel.setPlainText(info_text)

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
            f"integrated_detection_{int(time.time())}"
        )

        if success:
            self.is_recording = True
            self.stream_controls.start_recording_btn.setEnabled(False)
            self.stream_controls.stop_recording_btn.setEnabled(True)
            self.logger.info("Recording started")
        else:
            QMessageBox.critical(self, "Recording Error", "Failed to start recording.")

    def stop_recording(self):
        """Stop video recording."""
        self.recording_manager.stop_recording()
        self.is_recording = False
        self.stream_controls.start_recording_btn.setEnabled(True)
        self.stream_controls.stop_recording_btn.setEnabled(False)
        self.logger.info("Recording stopped")

    def on_recording_state_changed(self, is_recording: bool, path_or_message: str):
        """Handle recording state changes."""
        if is_recording:
            self.stream_controls.recording_status.setText("Status: Recording")
            self.stream_controls.recording_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        else:
            self.stream_controls.recording_status.setText(f"Status: {path_or_message}")
            self.stream_controls.recording_status.setStyleSheet("QLabel { color: gray; }")

    def on_recording_stats(self, stats: Dict[str, Any]):
        """Handle recording statistics updates."""
        duration = stats.get('duration', 0)
        fps = stats.get('recording_fps', 0)
        frames = stats.get('frames_recorded', 0)
        self.stream_controls.recording_info.setText(f"Duration: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames}")

    def on_connection_changed(self, connected: bool, message: str):
        """Handle connection status changes."""
        self.stream_controls.update_connection_status(connected, message)
        if connected:
            self.status_bar.showMessage(f"Connected - {message}")
            # Show playback controls only for video files
            if self.stream_manager.is_file_playback():
                self.playback_controls.show_for_file()
                self.playback_controls.update_play_state(True)  # Start playing
            else:
                self.playback_controls.hide_for_stream()
        else:
            self.status_bar.showMessage(f"Disconnected - {message}")
            self.playback_controls.hide_for_stream()

    def on_video_position_changed(self, current_time: float, total_duration: float):
        """Handle video position updates."""
        self.playback_controls.update_position(current_time, total_duration)

    def on_play_pause_clicked(self):
        """Handle play/pause button click."""
        new_state = self.stream_manager.play_pause()
        self.playback_controls.update_play_state(new_state)
        self.logger.info(f"Video {'playing' if new_state else 'paused'}")

    def on_seek_requested(self, time_seconds: float):
        """Handle seek request from playback controls."""
        self.stream_manager.seek_to_time(time_seconds)
        self.logger.info(f"Seeking to {time_seconds:.1f}s")

    def closeEvent(self, event):
        """Handle window close event."""
        self.disconnect_from_stream()
        if self.is_recording:
            self.recording_manager.stop_recording()
        event.accept()
