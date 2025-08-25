"""
RTMPAnomalyDetectionViewer.py - Real-time RTMP stream viewer with statistical anomaly detection

Integrates with ADIAT's real-time streaming infrastructure and provides
statistical anomaly detection capabilities optimized for real-time performance.
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

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QSpinBox, QFrame,
                             QGroupBox, QGridLayout, QTextEdit, QSplitter,
                             QCheckBox, QComboBox, QProgressBar,
                             QMessageBox, QStatusBar, QSlider, QFileDialog)

from core.services.RTMPStreamService import StreamManager, StreamType
from core.services.RealtimeAnomalyDetectionService import RealtimeAnomalyDetector, AnomalyConfig, AnomalyDetection
from core.services.VideoRecordingService import RecordingManager
from core.services.LoggerService import LoggerService


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
        from PyQt5.QtWidgets import QSizePolicy
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


class VideoTimelineWidget(QWidget):
    """Video timeline control widget for file playback."""

    playPauseToggled = pyqtSignal()
    seekRequested = pyqtSignal(float)  # time in seconds
    seekRelative = pyqtSignal(float)   # relative seconds
    jumpToBeginning = pyqtSignal()
    jumpToEnd = pyqtSignal()

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
        self.beginning_btn.setToolTip("Jump to beginning")
        timeline_layout.addWidget(self.beginning_btn)

        # Play/Pause button
        self.play_pause_btn = QPushButton("⏸")
        self.play_pause_btn.setFixedSize(35, 28)  # Slightly smaller
        self.play_pause_btn.setToolTip("Play/Pause (Space)")
        timeline_layout.addWidget(self.play_pause_btn)

        # Jump to end button
        self.end_btn = QPushButton("⟹")
        self.end_btn.setFixedSize(28, 28)  # Slightly smaller
        self.end_btn.setToolTip("Jump to end")
        timeline_layout.addWidget(self.end_btn)

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(1000)  # Use 0-1000 for better precision
        self.timeline_slider.setValue(0)
        self.timeline_slider.setFixedHeight(20)  # Fixed height for compactness
        self.timeline_slider.setToolTip("Timeline - Click to seek")
        timeline_layout.addWidget(self.timeline_slider, 1)

        # Time display
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(80)  # Slightly smaller
        self.time_label.setStyleSheet("QLabel { font-family: monospace; font-size: 11px; }")
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


class AnomalyControlWidget(QWidget):
    """Anomaly detection control widget."""

    configChanged = pyqtSignal(dict)  # Emitted when configuration changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the anomaly control interface."""
        layout = QVBoxLayout(self)

        # Sensitivity control group
        sensitivity_group = QGroupBox("Detection Sensitivity")
        sensitivity_layout = QGridLayout(sensitivity_group)

        # Sensitivity slider (1-10)
        sensitivity_layout.addWidget(QLabel("Sensitivity Level:"), 0, 0)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        self.sensitivity_slider.setTickPosition(QSlider.TicksBelow)
        self.sensitivity_slider.setTickInterval(1)
        sensitivity_layout.addWidget(self.sensitivity_slider, 0, 1)

        self.sensitivity_label = QLabel("5")
        self.sensitivity_label.setStyleSheet("QLabel { font-weight: bold; color: blue; }")
        sensitivity_layout.addWidget(self.sensitivity_label, 0, 2)

        # Sensitivity description
        self.sensitivity_desc = QLabel("Medium - Balanced detection")
        self.sensitivity_desc.setStyleSheet("QLabel { font-size: 10px; color: gray; }")
        sensitivity_layout.addWidget(self.sensitivity_desc, 1, 0, 1, 3)

        # Area constraints
        area_group = QGroupBox("Detection Constraints")
        area_layout = QGridLayout(area_group)

        # Minimum area
        area_layout.addWidget(QLabel("Min Area (pixels):"), 0, 0)
        self.min_area_spinbox = QSpinBox()
        self.min_area_spinbox.setRange(1, 100000)
        self.min_area_spinbox.setValue(100)
        area_layout.addWidget(self.min_area_spinbox, 0, 1)

        # Maximum area
        area_layout.addWidget(QLabel("Max Area (pixels):"), 1, 0)
        self.max_area_spinbox = QSpinBox()
        self.max_area_spinbox.setRange(100, 1000000)
        self.max_area_spinbox.setValue(50000)
        area_layout.addWidget(self.max_area_spinbox, 1, 1)

        # Window size for local statistics
        area_layout.addWidget(QLabel("Analysis Mode:"), 2, 0)
        self.window_size_spinbox = QSpinBox()
        self.window_size_spinbox.setRange(1, 5)  # Limit for real-time performance
        self.window_size_spinbox.setValue(1)  # Default to fastest global mode
        self.window_size_spinbox.setSingleStep(2)  # Ensure odd numbers
        self.window_size_spinbox.setToolTip("RX Anomaly Analysis Mode:\n" +
                                            "1 = Global RX (fastest, recommended)\n" +
                                            "   Detects colors that don't fit overall image\n" +
                                            "   Perfect for pink shirt in green scenery\n" +
                                            "3 = Local RX (slower, more detailed)\n" +
                                            "5 = Very detailed (may be too slow)")
        area_layout.addWidget(self.window_size_spinbox, 2, 1)

        # Algorithm options
        algorithm_group = QGroupBox("Algorithm Options")
        algorithm_layout = QGridLayout(algorithm_group)

        # Distance metric
        algorithm_layout.addWidget(QLabel("Distance Metric:"), 0, 0)
        self.distance_combo = QComboBox()
        self.distance_combo.addItems(["euclidean", "manhattan", "mahalanobis_approx"])
        algorithm_layout.addWidget(self.distance_combo, 0, 1)

        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout(options_group)

        # Confidence threshold slider
        confidence_layout = QGridLayout()
        confidence_layout.addWidget(QLabel("Confidence Threshold:"), 0, 0)
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(0)  # Default: show all detections
        self.confidence_slider.setTickPosition(QSlider.TicksBelow)
        self.confidence_slider.setTickInterval(10)
        confidence_layout.addWidget(self.confidence_slider, 0, 1)

        self.confidence_label = QLabel("0%")
        self.confidence_label.setStyleSheet("QLabel { font-weight: bold; color: white; }")
        confidence_layout.addWidget(self.confidence_label, 0, 2)

        # Confidence description
        self.confidence_desc = QLabel("Show all detections")
        self.confidence_desc.setStyleSheet("QLabel { font-size: 10px; color: gray; }")
        confidence_layout.addWidget(self.confidence_desc, 1, 0, 1, 3)

        options_layout.addLayout(confidence_layout)

        self.morphology_checkbox = QCheckBox("Enable Morphological Filtering")
        self.morphology_checkbox.setChecked(True)
        options_layout.addWidget(self.morphology_checkbox)

        self.gpu_checkbox = QCheckBox("Enable GPU Acceleration")
        self.gpu_checkbox.setChecked(False)
        options_layout.addWidget(self.gpu_checkbox)

        self.heatmap_checkbox = QCheckBox("Show Anomaly Heatmap")
        self.heatmap_checkbox.setChecked(False)
        options_layout.addWidget(self.heatmap_checkbox)

        # Add all groups to main layout
        layout.addWidget(sensitivity_group)
        layout.addWidget(area_group)
        layout.addWidget(algorithm_group)
        layout.addWidget(options_group)
        layout.addStretch()

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity)
        self.min_area_spinbox.valueChanged.connect(self.emit_config)
        self.max_area_spinbox.valueChanged.connect(self.emit_config)
        self.window_size_spinbox.valueChanged.connect(self.ensure_odd_window_size)
        self.distance_combo.currentTextChanged.connect(self.emit_config)
        self.confidence_slider.valueChanged.connect(self.update_confidence_threshold)
        self.morphology_checkbox.toggled.connect(self.emit_config)
        self.gpu_checkbox.toggled.connect(self.emit_config)
        self.heatmap_checkbox.toggled.connect(self.emit_config)

    def update_sensitivity(self):
        """Handle sensitivity slider changes."""
        value = self.sensitivity_slider.value()
        self.sensitivity_label.setText(str(value))

        # Update description based on value
        descriptions = {
            1: "Very Low - Few detections", 2: "Low - Conservative",
            3: "Low-Medium", 4: "Medium-Low", 5: "Medium - Balanced detection",
            6: "Medium-High", 7: "High-Medium", 8: "High - Sensitive",
            9: "Very High - Many detections", 10: "Maximum - All variations"
        }
        self.sensitivity_desc.setText(descriptions.get(value, "Medium"))
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

    def ensure_odd_window_size(self):
        """Ensure window size is always odd."""
        value = self.window_size_spinbox.value()
        if value % 2 == 0:
            self.window_size_spinbox.setValue(value + 1)
        else:
            self.emit_config()

    def emit_config(self):
        """Emit current configuration."""
        config = {
            'sensitivity': self.sensitivity_slider.value(),
            'min_area': self.min_area_spinbox.value(),
            'max_area': self.max_area_spinbox.value(),
            'window_size': self.window_size_spinbox.value(),
            'distance_metric': self.distance_combo.currentText(),
            'confidence_threshold': self.confidence_slider.value() / 100.0,  # Convert to 0-1 range
            'morphology_enabled': self.morphology_checkbox.isChecked(),
            'gpu_acceleration': self.gpu_checkbox.isChecked(),
            'show_heatmap': self.heatmap_checkbox.isChecked()
        }
        self.configChanged.emit(config)

    def get_anomaly_config(self) -> AnomalyConfig:
        """Get current configuration as AnomalyConfig object."""
        return AnomalyConfig(
            sensitivity=self.sensitivity_slider.value(),
            min_area=self.min_area_spinbox.value(),
            max_area=self.max_area_spinbox.value(),
            window_size=self.window_size_spinbox.value(),
            distance_metric=self.distance_combo.currentText(),
            confidence_threshold=self.confidence_slider.value() / 100.0,
            morphology_enabled=self.morphology_checkbox.isChecked(),
            gpu_acceleration=self.gpu_checkbox.isChecked(),
            show_heatmap=self.heatmap_checkbox.isChecked()
        )


class StreamControlWidget(QWidget):
    """Stream connection and control widget."""

    connectRequested = pyqtSignal(str, str)  # url, stream_type
    disconnectRequested = pyqtSignal()

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
        self.url_input.setText("")  # Default empty for file selection
        url_layout.addWidget(self.url_input, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setVisible(True)  # Visible by default since File is default
        self.browse_button.setToolTip("Browse for video file")
        url_layout.addWidget(self.browse_button)

        connection_layout.addLayout(url_layout, 0, 1)

        # Stream type
        connection_layout.addWidget(QLabel("Stream Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["File", "HDMI Capture", "RTMP Stream"])
        connection_layout.addWidget(self.type_combo, 1, 1)

        # Connection buttons
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.disconnect_button.setEnabled(False)

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
        self.detections_label = QLabel("Anomalies: --")

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
        self.detections_label.setText(f"Anomalies: {detection_count}")

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


class RTMPAnomalyDetectionViewer(QMainWindow):
    """Main RTMP anomaly detection viewer window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Core services
        self.stream_manager = StreamManager()
        self.anomaly_detector = RealtimeAnomalyDetector()
        self.recording_manager = RecordingManager("./recordings")

        # UI components
        self.video_display = None
        self.anomaly_controls = None
        self.stream_controls = None
        self.recording_controls = None

        # State
        self.is_detecting = False
        self.is_recording = False
        self.current_detections = []
        self.current_frame = None
        self.current_anomaly_map = None
        self.stream_resolution = (640, 480)

        self.setup_ui()
        self.connect_signals()

        self.logger.info("RTMP Anomaly Detection Viewer initialized")

    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("ADIAT - Real-Time Anomaly Detection")
        self.setMinimumSize(1200, 800)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)

        # Video display area
        video_widget = QWidget()
        video_layout = QVBoxLayout(video_widget)

        self.video_display = VideoDisplayWidget()
        video_layout.addWidget(self.video_display, 1)  # Give video display stretch factor of 1

        # Timeline controls (for file playback) - fixed size, no stretch
        self.timeline_widget = VideoTimelineWidget()
        self.timeline_widget.setMaximumHeight(80)  # Limit timeline height
        video_layout.addWidget(self.timeline_widget, 0)  # No stretch - stays compact

        # Detection info panel - fixed size, no stretch
        info_panel = QTextEdit()
        info_panel.setMaximumHeight(150)
        info_panel.setMinimumHeight(150)  # Prevent shrinking too much
        info_panel.setReadOnly(True)
        info_panel.setPlaceholderText("Anomaly detection information will appear here...")
        video_layout.addWidget(info_panel, 0)  # No stretch - stays fixed size
        self.info_panel = info_panel

        # Control panel
        control_widget = QWidget()
        control_widget.setMaximumWidth(350)
        control_layout = QVBoxLayout(control_widget)

        # Stream controls
        self.stream_controls = StreamControlWidget()
        control_layout.addWidget(self.stream_controls)

        # Anomaly controls
        self.anomaly_controls = AnomalyControlWidget()
        control_layout.addWidget(self.anomaly_controls)

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
        self.status_bar.showMessage("Ready - Connect to stream to begin anomaly detection")

    def _create_recording_controls(self) -> QWidget:
        """Create recording control widget."""
        group = QGroupBox("Recording")
        layout = QVBoxLayout(group)

        # Recording buttons
        button_layout = QHBoxLayout()
        self.start_recording_btn = QPushButton("Start Recording")
        self.start_recording_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-weight: bold; }")
        self.stop_recording_btn = QPushButton("Stop Recording")
        self.stop_recording_btn.setEnabled(False)

        button_layout.addWidget(self.start_recording_btn)
        button_layout.addWidget(self.stop_recording_btn)

        # Recording status
        self.recording_status = QLabel("Status: Not Recording")
        self.recording_status.setStyleSheet("QLabel { color: gray; }")

        # Recording info
        self.recording_info = QLabel("Duration: --")

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

        # Anomaly detector signals
        self.anomaly_detector.detectionsReady.connect(self.on_detections_ready)
        self.anomaly_detector.performanceUpdate.connect(self.on_performance_update)

        # Recording manager signals
        self.recording_manager.recordingStateChanged.connect(self.on_recording_state_changed)
        self.recording_manager.recordingStats.connect(self.on_recording_stats)

        # UI control signals
        self.stream_controls.connectRequested.connect(self.connect_to_stream)
        self.stream_controls.disconnectRequested.connect(self.disconnect_from_stream)
        self.anomaly_controls.configChanged.connect(self.update_detection_config)

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
        self.status_bar.showMessage("Disconnected")

    def update_detection_config(self):
        """Update anomaly detection configuration."""
        config = self.anomaly_controls.get_anomaly_config()
        self.anomaly_detector.update_config(config)

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

            # Perform anomaly detection
            try:
                detections = self.anomaly_detector.detect_anomalies(working_frame, timestamp)
            except Exception as e:
                self.logger.error(f"Anomaly detection failed: {e}")
                detections = []

            # Create annotated frame (pass anomaly map if available)
            try:
                annotated_frame = self.anomaly_detector.create_annotated_frame(
                    working_frame, detections, self.current_anomaly_map
                )
            except Exception as e:
                self.logger.error(f"Frame annotation failed: {e}")
                annotated_frame = working_frame

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

            # Add frame to recording if active
            if self.is_recording:
                try:
                    self.recording_manager.add_frame(working_frame, timestamp)
                except Exception as e:
                    self.logger.error(f"Recording failed: {e}")

            # Emit signal with results
            try:
                self.anomaly_detector.detectionsReady.emit(detections, timestamp, annotated_frame)
            except Exception as e:
                self.logger.error(f"Signal emission failed: {e}")

        except Exception as e:
            self.logger.error(f"Critical error processing frame: {e}")
            import traceback
            self.logger.error(f"Frame processing traceback: {traceback.format_exc()}")

    def on_detections_ready(self, detections: List[AnomalyDetection], timestamp: float, annotated_frame: np.ndarray):
        """Handle detection results."""
        # Update info panel
        if detections:
            info_text = f"Anomaly Detection Results ({len(detections)} found):\n"
            for i, detection in enumerate(detections[:5]):  # Show top 5
                x, y, w, h = detection.bbox
                info_text += f"  #{i+1}: Pos({x},{y}) Size({w}x{h}) Area({int(detection.area)}px)\n"
                info_text += f"       Anomaly Score: {detection.anomaly_score:.3f} Confidence: {detection.confidence:.2f}\n"
        else:
            info_text = "No anomalies detected."

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
        width, height = resolution

        # Add performance warning for large resolutions
        if width > 1280 or height > 720:
            status_msg = f"Stream: {width}x{height} @ {fps:.1f}fps (Auto-downscaled for performance)"
        else:
            status_msg = f"Stream: {width}x{height} @ {fps:.1f}fps"

        self.status_bar.showMessage(status_msg)

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
            f"rtmp_anomaly_{int(time.time())}"
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
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    viewer = RTMPAnomalyDetectionViewer()
    viewer.show()
    sys.exit(app.exec_())
