"""
RTMPMotionDetectionViewer.py - Real-time motion detection viewer for ADIAT

Provides UI controller for real-time motion detection with support for both
static and moving camera scenarios, including drone motion compensation.
"""

import os
import sys
import time
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QSlider, QLabel,
    QComboBox, QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor

from core.views.RTMPMotionDetectionViewer_ui import Ui_RTMPMotionDetectionViewer
from core.services.RTMPStreamService import StreamManager, StreamType
from core.services.RealtimeMotionDetectionService import (
    RealtimeMotionDetector, DetectionMode, MotionAlgorithm,
    MotionDetection, CameraMotion
)
from core.services.VideoRecordingService import VideoRecorder, RecordingConfig
from core.services.LoggerService import LoggerService


class RTMPMotionDetectionViewer(QMainWindow):
    """
    Main viewer window for real-time motion detection with RTMP/video streams.
    
    Features:
    - Dual-mode detection (static/moving camera)
    - Multiple detection algorithms
    - Camera motion compensation for drones
    - Real-time visualization
    - Motion event recording
    - Adjustable detection parameters
    """
    
    def __init__(self, parent=None):
        super(RTMPMotionDetectionViewer, self).__init__(parent)
        self.logger = LoggerService()
        
        # Setup UI
        self.ui = Ui_RTMPMotionDetectionViewer()
        self.ui.setupUi(self)
        
        # Initialize services
        self.stream_manager = StreamManager()
        self.motion_detector = RealtimeMotionDetector()
        self.video_recorder = None
        
        # State tracking
        self._is_connected = False
        self._is_recording = False
        self._is_detecting = True
        self._detection_count = 0
        self._session_start_time = None
        self._last_detection_time = None
        
        # Debounce timer for parameter updates
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._apply_pending_updates)
        self._pending_updates = {}
        
        # Frame skipping for UI responsiveness
        self._frame_skip_counter = 0
        self._max_frame_skip = 3  # Skip up to 3 frames when performance is low
        self._last_process_time = 0
        self._target_process_time = 33  # Target 30 FPS (33ms per frame)
        
        # Recording configuration
        self._recording_config = None
        self._recording_start_time = None
        self._recorded_detections = []
        
        # Initialize UI state BEFORE connecting signals to avoid triggering callbacks
        self._initialize_ui_state()
        
        # Setup UI connections
        self._setup_ui_connections()
        
        # Setup service connections
        self._setup_service_connections()
        
        # Display timer for continuous updates
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self._update_display_stats)
        self.display_timer.start(1000)  # Update every second
        
        self.logger.info("RTMP Motion Detection Viewer initialized")
    
    def _setup_ui_connections(self):
        """Setup UI element signal connections."""
        # Connection controls
        self.ui.connectButton.clicked.connect(self._toggle_connection)
        self.ui.streamTypeCombo.currentTextChanged.connect(self._on_stream_type_changed)
        self.ui.browseButton.clicked.connect(self._browse_file)
        
        # Detection mode controls
        self.ui.modeCombo.currentTextChanged.connect(self._on_mode_changed)
        self.ui.algorithmCombo.currentTextChanged.connect(self._on_algorithm_changed)
        
        # Detection parameters - use sliderReleased and editingFinished to avoid continuous updates
        self.ui.sensitivitySlider.sliderReleased.connect(self._on_sensitivity_changed)
        self.ui.sensitivitySlider.valueChanged.connect(self._on_sensitivity_slider_moving)
        self.ui.minAreaSpinBox.editingFinished.connect(self._on_min_area_changed)
        self.ui.maxAreaSpinBox.editingFinished.connect(self._on_max_area_changed)
        self.ui.thresholdSpinBox.editingFinished.connect(self._on_threshold_changed)
        self.ui.compensationSlider.sliderReleased.connect(self._on_compensation_changed)
        self.ui.compensationSlider.valueChanged.connect(self._on_compensation_slider_moving)
        
        # Visualization options
        self.ui.showVectorsCheckBox.toggled.connect(self._on_show_vectors_changed)
        self.ui.showCameraMotionCheckBox.toggled.connect(self._on_show_camera_changed)
        self.ui.showOverlayCheckBox.toggled.connect(self._on_show_overlay_changed)
        
        # Resolution dropdown
        if hasattr(self.ui, 'resolutionCombo'):
            self.ui.resolutionCombo.currentIndexChanged.connect(self._on_resolution_changed)
        
        # Recording controls
        self.ui.recordButton.clicked.connect(self._toggle_recording)
        self.ui.snapshotButton.clicked.connect(self._take_snapshot)
        
        # Detection toggle
        self.ui.detectButton.clicked.connect(self._toggle_detection)
        
        # Video playback controls (if available from parent UI)
        if hasattr(self.ui, 'playPauseButton'):
            self.ui.playPauseButton.clicked.connect(self._play_pause_video)
        if hasattr(self.ui, 'seekSlider'):
            self.ui.seekSlider.sliderReleased.connect(self._seek_video)
    
    def _setup_service_connections(self):
        """Setup service signal connections."""
        # Stream manager connections
        self.stream_manager.frameReceived.connect(self._process_frame)
        self.stream_manager.connectionChanged.connect(self._on_connection_changed)
        self.stream_manager.statsUpdated.connect(self._on_stream_stats_updated)
        self.stream_manager.videoPositionChanged.connect(self._on_video_position_changed)
        
        # Motion detector connections
        self.motion_detector.detectionsReady.connect(self._on_detections_ready)
        self.motion_detector.performanceUpdate.connect(self._on_performance_update)
        self.motion_detector.modeChanged.connect(self._on_mode_auto_changed)
    
    def _initialize_ui_state(self):
        """Initialize UI elements to default state."""
        # Stream type options
        self.ui.streamTypeCombo.addItems(['RTMP', 'HLS', 'File', 'HDMI Capture'])
        self.ui.streamTypeCombo.setCurrentText('RTMP')
        
        # Detection mode options
        self.ui.modeCombo.addItems(['Auto', 'Static Camera', 'Moving Camera'])
        self.ui.modeCombo.setCurrentText('Auto')
        
        # Algorithm options
        self.ui.algorithmCombo.addItems([
            'Frame Difference',
            'MOG2 Background',
            'KNN Background',
            'Optical Flow',
            'Feature Matching'
        ])
        self.ui.algorithmCombo.setCurrentText('MOG2 Background')
        
        # Set default parameter values
        self.ui.sensitivitySlider.setValue(50)  # 0.5
        self.ui.minAreaSpinBox.setValue(500)
        self.ui.maxAreaSpinBox.setValue(100000)
        self.ui.thresholdSpinBox.setValue(25)
        self.ui.compensationSlider.setValue(80)  # 0.8
        
        # Visualization defaults
        self.ui.showVectorsCheckBox.setChecked(True)
        self.ui.showCameraMotionCheckBox.setChecked(True)
        self.ui.showOverlayCheckBox.setChecked(True)
        
        # Resolution dropdown setup
        if hasattr(self.ui, 'resolutionCombo'):
            self.ui.resolutionCombo.addItem("Auto (1280x720)", None)  # Default behavior
            self.ui.resolutionCombo.addItem("Ultra Fast (320x240)", (320, 240))
            self.ui.resolutionCombo.addItem("Fast (480x360)", (480, 360))
            self.ui.resolutionCombo.addItem("Balanced (640x480)", (640, 480))
            self.ui.resolutionCombo.addItem("Quality (960x720)", (960, 720))
            self.ui.resolutionCombo.addItem("HD (1280x720)", (1280, 720))
            self.ui.resolutionCombo.addItem("Full Resolution", None)
            self.ui.resolutionCombo.setCurrentIndex(3)  # Default to Balanced
            self.ui.resolutionCombo.setToolTip("Lower resolution = faster processing")
        
        # Disable controls initially
        self._set_controls_enabled(False)
        
        # Default stream URL
        self.ui.streamUrlEdit.setText("rtmp://localhost:1935/live/stream")
    
    def _set_controls_enabled(self, enabled: bool):
        """Enable/disable detection controls."""
        self.ui.modeCombo.setEnabled(enabled)
        self.ui.algorithmCombo.setEnabled(enabled)
        self.ui.sensitivitySlider.setEnabled(enabled)
        self.ui.minAreaSpinBox.setEnabled(enabled)
        self.ui.maxAreaSpinBox.setEnabled(enabled)
        self.ui.thresholdSpinBox.setEnabled(enabled)
        self.ui.compensationSlider.setEnabled(enabled)
        self.ui.recordButton.setEnabled(enabled)
        self.ui.snapshotButton.setEnabled(enabled)
        self.ui.detectButton.setEnabled(enabled)
    
    def _toggle_connection(self):
        """Toggle stream connection."""
        if not self._is_connected:
            self._connect_stream()
        else:
            self._disconnect_stream()
    
    def _connect_stream(self):
        """Connect to stream based on selected type."""
        stream_type_text = self.ui.streamTypeCombo.currentText()
        stream_url = self.ui.streamUrlEdit.text().strip()
        
        if not stream_url:
            QMessageBox.warning(self, "Warning", "Please enter a stream URL or file path")
            return
        
        # Map UI text to StreamType enum
        type_map = {
            'RTMP': StreamType.RTMP,
            'HLS': StreamType.HLS,
            'File': StreamType.FILE,
            'HDMI Capture': StreamType.HDMI_CAPTURE
        }
        stream_type = type_map.get(stream_type_text, StreamType.RTMP)
        
        # For HDMI capture, use device index
        if stream_type == StreamType.HDMI_CAPTURE:
            try:
                # Try to parse as device index
                device_index = int(stream_url) if stream_url.isdigit() else 0
                stream_url = str(device_index)
            except:
                stream_url = "0"  # Default to first device
        
        self.logger.info(f"Connecting to {stream_type_text} stream: {stream_url}")
        self.ui.statusLabel.setText("Connecting...")
        
        # Start connection
        if self.stream_manager.connect_to_stream(stream_url, stream_type):
            self._session_start_time = datetime.now()
            self._detection_count = 0
        else:
            QMessageBox.error(self, "Connection Error", "Failed to connect to stream")
            self.ui.statusLabel.setText("Connection failed")
    
    def _disconnect_stream(self):
        """Disconnect from current stream."""
        # Stop recording if active
        if self._is_recording:
            self._stop_recording()
        
        # Disconnect stream
        self.stream_manager.disconnect_stream()
        
        # Reset detector
        self.motion_detector.reset()
        
        # Clear display
        self.ui.videoLabel.clear()
        self.ui.videoLabel.setText("No Stream Connected")
        
        # Reset stats
        self._detection_count = 0
        self._session_start_time = None
        
        self.logger.info("Disconnected from stream")
    
    def _on_connection_changed(self, connected: bool, message: str):
        """Handle stream connection status change."""
        self._is_connected = connected
        
        if connected:
            self.ui.connectButton.setText("Disconnect")
            self.ui.statusLabel.setText(f"Connected: {message}")
            self._set_controls_enabled(True)
        else:
            self.ui.connectButton.setText("Connect")
            self.ui.statusLabel.setText(f"Disconnected: {message}")
            self._set_controls_enabled(False)
            self.ui.videoLabel.clear()
            self.ui.videoLabel.setText("No Stream Connected")
    
    def _process_frame(self, frame: np.ndarray, timestamp: float):
        """Process incoming frame for motion detection."""
        if not self._is_detecting:
            # Just display frame without detection
            self._display_frame(frame)
            return
        
        # Process frame through motion detector
        # The detector will emit detectionsReady signal with results
        self.motion_detector.process_frame(frame)
    
    def _on_detections_ready(self, detections: List[MotionDetection], 
                            camera_motion: Optional[CameraMotion], 
                            annotated_frame: np.ndarray):
        """Handle motion detection results."""
        # Update detection count
        if detections:
            self._detection_count += len(detections)
            self._last_detection_time = datetime.now()
            
            # Record detections if recording
            if self._is_recording and self.video_recorder:
                for detection in detections:
                    self._recorded_detections.append({
                        'timestamp': time.time() - self._recording_start_time,
                        'bbox': detection.bbox,
                        'area': detection.area,
                        'velocity': detection.velocity,
                        'is_compensated': detection.is_compensated
                    })
        
        # Frame skipping logic to maintain UI responsiveness
        import time
        current_time = time.perf_counter()
        
        if self._last_process_time > 0:
            process_time = (current_time - self._last_process_time) * 1000
            if process_time > self._target_process_time * 1.5:  # If taking too long
                self._frame_skip_counter += 1
                if self._frame_skip_counter < self._max_frame_skip:
                    # Skip this frame to maintain UI responsiveness
                    return
        
        self._frame_skip_counter = 0  # Reset skip counter
        self._last_process_time = current_time
        
        # Display annotated frame
        if self.ui.showOverlayCheckBox.isChecked():
            self._display_frame(annotated_frame)
        
        # Update detection info display
        self._update_detection_info(detections, camera_motion)
        
        # Record frame if recording
        if self._is_recording and self.video_recorder:
            self.video_recorder.write_frame(annotated_frame)
    
    def _display_frame(self, frame: np.ndarray):
        """Display frame in the video label."""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get frame dimensions
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # Create QImage
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale to fit label while maintaining aspect ratio
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.ui.videoLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # Display in label
            self.ui.videoLabel.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Error displaying frame: {e}")
    
    def _update_detection_info(self, detections: List[MotionDetection], 
                              camera_motion: Optional[CameraMotion]):
        """Update detection information display."""
        # Update detection count label with area information
        total_area = sum(d.area for d in detections)
        avg_area = total_area / len(detections) if detections else 0
        self.ui.detectionCountLabel.setText(f"Detections: {len(detections)} | Total Area: {int(total_area)} | Avg: {int(avg_area)}")
        
        # Update camera motion info if available
        if camera_motion:
            motion_text = f"Camera Motion: ({camera_motion.global_velocity[0]:.1f}, "
            motion_text += f"{camera_motion.global_velocity[1]:.1f}) "
            motion_text += f"Confidence: {camera_motion.confidence:.2f}"
            self.ui.cameraMotionLabel.setText(motion_text)
        else:
            self.ui.cameraMotionLabel.setText("Camera Motion: None")
        
        # Update detection list if we have a list widget
        if hasattr(self.ui, 'detectionListWidget'):
            self.ui.detectionListWidget.clear()
            for i, detection in enumerate(detections[:10]):  # Show max 10
                info = f"Detection {i+1}: Area={int(detection.area)} px², "
                info += f"Velocity=({detection.velocity[0]:.1f}, {detection.velocity[1]:.1f})"
                if detection.is_compensated:
                    info += " (Compensated)"
                self.ui.detectionListWidget.addItem(info)
    
    def _on_performance_update(self, metrics: dict):
        """Handle performance metrics update."""
        fps = metrics.get('fps', 0)
        processing_time = metrics.get('avg_processing_time_ms', 0)
        mode = metrics.get('mode', 'unknown')
        confidence = metrics.get('mode_confidence', 0)
        gpu_enabled = metrics.get('gpu_enabled', False)
        
        # Update performance labels
        gpu_text = " (GPU)" if gpu_enabled else " (CPU)"
        self.ui.fpsLabel.setText(f"FPS: {fps:.1f}{gpu_text}")
        self.ui.processingTimeLabel.setText(f"Processing: {processing_time:.1f}ms")
        
        # Update mode info if in auto mode
        if self.ui.modeCombo.currentText() == 'Auto':
            self.ui.modeStatusLabel.setText(f"Auto Mode: {mode.title()} ({confidence:.0%})")
    
    def _on_mode_auto_changed(self, new_mode: str):
        """Handle automatic mode change."""
        self.logger.info(f"Motion detector auto-switched to {new_mode} mode")
        if hasattr(self.ui, 'modeStatusLabel'):
            self.ui.modeStatusLabel.setText(f"Auto Mode: {new_mode.title()}")
    
    def _on_stream_stats_updated(self, stats: dict):
        """Handle stream statistics update."""
        resolution = stats.get('resolution', (0, 0))
        stream_fps = stats.get('fps', 0)
        
        # Update stream info labels
        self.ui.resolutionLabel.setText(f"Resolution: {resolution[0]}x{resolution[1]}")
        self.ui.streamFpsLabel.setText(f"Stream FPS: {stream_fps:.1f}")
    
    def _on_video_position_changed(self, current_time: float, total_time: float):
        """Handle video position change for file playback."""
        if hasattr(self.ui, 'seekSlider') and not self.ui.seekSlider.isSliderDown():
            # Update seek slider position
            if total_time > 0:
                position = int((current_time / total_time) * 1000)
                self.ui.seekSlider.setValue(position)
            
            # Update time labels
            if hasattr(self.ui, 'currentTimeLabel'):
                self.ui.currentTimeLabel.setText(self._format_time(current_time))
            if hasattr(self.ui, 'totalTimeLabel'):
                self.ui.totalTimeLabel.setText(self._format_time(total_time))
    
    def _update_display_stats(self):
        """Update display statistics periodically."""
        if self._session_start_time:
            elapsed = (datetime.now() - self._session_start_time).total_seconds()
            self.ui.sessionTimeLabel.setText(f"Session: {self._format_time(elapsed)}")
            self.ui.totalDetectionsLabel.setText(f"Total Detections: {self._detection_count}")
            
            if self._last_detection_time:
                time_since = (datetime.now() - self._last_detection_time).total_seconds()
                self.ui.lastDetectionLabel.setText(f"Last Detection: {time_since:.1f}s ago")
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _schedule_update(self, **kwargs):
        """Schedule a parameter update with debouncing to prevent rapid updates."""
        # Store pending updates
        self._pending_updates.update(kwargs)
        
        # Reset timer to delay update by 100ms
        self._update_timer.stop()
        self._update_timer.start(100)  # 100ms debounce
    
    def _apply_pending_updates(self):
        """Apply all pending parameter updates at once."""
        if self._pending_updates:
            try:
                self.motion_detector.update_config(**self._pending_updates)
                self._pending_updates.clear()
            except Exception as e:
                self.logger.error(f"Error updating motion detector config: {e}")
    
    # Parameter adjustment handlers
    def _on_mode_changed(self, mode_text: str):
        """Handle detection mode change."""
        mode_map = {
            'Auto': DetectionMode.AUTO,
            'Static Camera': DetectionMode.STATIC,
            'Moving Camera': DetectionMode.MOVING
        }
        mode = mode_map.get(mode_text, DetectionMode.AUTO)
        self._schedule_update(mode=mode)
        
        # Enable/disable compensation slider based on mode
        self.ui.compensationSlider.setEnabled(mode != DetectionMode.STATIC)
        self.ui.compensationLabel.setEnabled(mode != DetectionMode.STATIC)
    
    def _on_algorithm_changed(self, algorithm_text: str):
        """Handle algorithm change."""
        algorithm_map = {
            'Frame Difference': MotionAlgorithm.FRAME_DIFF,
            'MOG2 Background': MotionAlgorithm.MOG2,
            'KNN Background': MotionAlgorithm.KNN,
            'Optical Flow': MotionAlgorithm.OPTICAL_FLOW,
            'Feature Matching': MotionAlgorithm.FEATURE_MATCH
        }
        algorithm = algorithm_map.get(algorithm_text, MotionAlgorithm.MOG2)
        self._schedule_update(algorithm=algorithm)
    
    def _on_sensitivity_slider_moving(self, value: int):
        """Update label while slider is moving but don't update detector."""
        self.ui.sensitivityLabel.setText(f"Sensitivity: {value}%")
    
    def _on_sensitivity_changed(self):
        """Handle sensitivity slider release - actually update the detector."""
        value = self.ui.sensitivitySlider.value()
        sensitivity = value / 100.0  # Convert to 0-1 range
        self._schedule_update(sensitivity=sensitivity)
        self.ui.sensitivityLabel.setText(f"Sensitivity: {value}%")
    
    def _on_min_area_changed(self):
        """Handle minimum area change when editing finished."""
        value = self.ui.minAreaSpinBox.value()
        self._schedule_update(min_area=value)
    
    def _on_max_area_changed(self):
        """Handle maximum area change when editing finished."""
        value = self.ui.maxAreaSpinBox.value()
        self._schedule_update(max_area=value)
    
    def _on_threshold_changed(self):
        """Handle motion threshold change when editing finished."""
        value = self.ui.thresholdSpinBox.value()
        self._schedule_update(motion_threshold=value)
    
    def _on_compensation_slider_moving(self, value: int):
        """Update label while slider is moving but don't update detector."""
        self.ui.compensationLabel.setText(f"Compensation: {value}%")
    
    def _on_compensation_changed(self):
        """Handle compensation strength change when slider released."""
        value = self.ui.compensationSlider.value()
        compensation = value / 100.0  # Convert to 0-1 range
        self._schedule_update(compensation_strength=compensation)
        self.ui.compensationLabel.setText(f"Compensation: {value}%")
    
    def _on_show_vectors_changed(self, checked: bool):
        """Handle show vectors checkbox change."""
        self.motion_detector.update_config(show_vectors=checked)
    
    def _on_show_camera_changed(self, checked: bool):
        """Handle show camera motion checkbox change."""
        self.motion_detector.update_config(show_camera_motion=checked)
    
    def _on_show_overlay_changed(self, checked: bool):
        """Handle show overlay checkbox change."""
        # This is handled in _on_detections_ready
        pass
    
    def _on_resolution_changed(self, index: int):
        """Handle resolution dropdown change."""
        if hasattr(self.ui, 'resolutionCombo'):
            resolution = self.ui.resolutionCombo.currentData()
            self._schedule_update(processing_resolution=resolution)
            
            # Log the change
            if resolution:
                self.logger.info(f"Processing resolution changed to: {resolution[0]}x{resolution[1]}")
            else:
                self.logger.info("Processing resolution set to Auto/Full")
    
    def _on_stream_type_changed(self, stream_type: str):
        """Handle stream type selection change."""
        if stream_type == 'File':
            self.ui.browseButton.setEnabled(True)
            self.ui.streamUrlEdit.setPlaceholderText("Select video file...")
        elif stream_type == 'HDMI Capture':
            self.ui.browseButton.setEnabled(False)
            self.ui.streamUrlEdit.setPlaceholderText("Device index (e.g., 0, 1, 2)")
            self.ui.streamUrlEdit.setText("0")
        else:
            self.ui.browseButton.setEnabled(False)
            if stream_type == 'RTMP':
                self.ui.streamUrlEdit.setPlaceholderText("rtmp://server:port/app/stream")
            else:  # HLS
                self.ui.streamUrlEdit.setPlaceholderText("http://server:port/stream.m3u8")
    
    def _browse_file(self):
        """Browse for video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.flv);;All Files (*.*)"
        )
        if file_path:
            self.ui.streamUrlEdit.setText(file_path)
    
    def _toggle_detection(self):
        """Toggle motion detection on/off."""
        self._is_detecting = not self._is_detecting
        
        if self._is_detecting:
            self.ui.detectButton.setText("Stop Detection")
            self.ui.detectButton.setStyleSheet("background-color: #ff6b6b;")
        else:
            self.ui.detectButton.setText("Start Detection")
            self.ui.detectButton.setStyleSheet("background-color: #51cf66;")
            
        self.logger.info(f"Motion detection {'enabled' if self._is_detecting else 'disabled'}")
    
    def _toggle_recording(self):
        """Toggle video recording."""
        if not self._is_recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _start_recording(self):
        """Start recording detected motion."""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motion_detection_{timestamp}.mp4"
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Recording",
                filename,
                "Video Files (*.mp4);;All Files (*.*)"
            )
            
            if not file_path:
                return
            
            # Create recording configuration
            self._recording_config = RecordingConfig(
                output_path=file_path,
                fps=30,
                codec='mp4v',
                include_audio=False
            )
            
            # Initialize recorder
            # Note: We'll need to get frame dimensions from the stream
            frame_size = (1920, 1080)  # Default, will be updated with actual size
            self.video_recorder = VideoRecorder(self._recording_config, frame_size)
            
            if self.video_recorder.start_recording():
                self._is_recording = True
                self._recording_start_time = time.time()
                self._recorded_detections = []
                
                self.ui.recordButton.setText("Stop Recording")
                self.ui.recordButton.setStyleSheet("background-color: #ff6b6b;")
                self.ui.statusLabel.setText(f"Recording to: {os.path.basename(file_path)}")
                
                self.logger.info(f"Started recording to: {file_path}")
            else:
                QMessageBox.error(self, "Recording Error", "Failed to start recording")
                self.video_recorder = None
                
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            QMessageBox.error(self, "Recording Error", f"Failed to start recording: {e}")
    
    def _stop_recording(self):
        """Stop recording."""
        if self.video_recorder:
            self.video_recorder.stop_recording()
            
            # Save detection metadata
            if self._recorded_detections:
                self._save_detection_metadata()
            
            self.video_recorder = None
        
        self._is_recording = False
        self.ui.recordButton.setText("Start Recording")
        self.ui.recordButton.setStyleSheet("")
        self.ui.statusLabel.setText("Recording stopped")
        
        self.logger.info("Stopped recording")
    
    def _save_detection_metadata(self):
        """Save detection metadata to JSON file."""
        try:
            import json
            
            # Create metadata filename based on video filename
            if self._recording_config:
                json_path = self._recording_config.output_path.replace('.mp4', '_metadata.json')
                
                metadata = {
                    'recording_start': self._recording_start_time,
                    'recording_duration': time.time() - self._recording_start_time,
                    'total_detections': len(self._recorded_detections),
                    'detection_mode': self.ui.modeCombo.currentText(),
                    'algorithm': self.ui.algorithmCombo.currentText(),
                    'detections': self._recorded_detections
                }
                
                with open(json_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                self.logger.info(f"Saved detection metadata to: {json_path}")
                
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")
    
    def _take_snapshot(self):
        """Take a snapshot of current frame."""
        try:
            # Get current pixmap from video label
            pixmap = self.ui.videoLabel.pixmap()
            if not pixmap:
                QMessageBox.warning(self, "Warning", "No frame to capture")
                return
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motion_snapshot_{timestamp}.png"
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Snapshot",
                filename,
                "Image Files (*.png *.jpg);;All Files (*.*)"
            )
            
            if file_path:
                pixmap.save(file_path)
                self.ui.statusLabel.setText(f"Snapshot saved: {os.path.basename(file_path)}")
                self.logger.info(f"Snapshot saved to: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error taking snapshot: {e}")
            QMessageBox.error(self, "Snapshot Error", f"Failed to save snapshot: {e}")
    
    def _play_pause_video(self):
        """Play/pause video playback (for file sources)."""
        if self.stream_manager.is_file_playback():
            is_playing = self.stream_manager.play_pause()
            if hasattr(self.ui, 'playPauseButton'):
                self.ui.playPauseButton.setText("Pause" if is_playing else "Play")
    
    def _seek_video(self):
        """Seek video to slider position."""
        if hasattr(self.ui, 'seekSlider') and self.stream_manager.is_file_playback():
            position = self.ui.seekSlider.value() / 1000.0  # Convert to 0-1 range
            playback_info = self.stream_manager.get_playback_info()
            total_duration = playback_info.get('total_duration', 0)
            if total_duration > 0:
                seek_time = position * total_duration
                self.stream_manager.seek_to_time(seek_time)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop recording if active
        if self._is_recording:
            self._stop_recording()
        
        # Disconnect stream
        if self._is_connected:
            self._disconnect_stream()
        
        # Stop timers
        self.display_timer.stop()
        
        event.accept()
        self.logger.info("RTMP Motion Detection Viewer closed")