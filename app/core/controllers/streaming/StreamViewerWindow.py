"""
StreamViewerWindow - Main container for streaming detection algorithms.

This window acts as the container for streaming detection algorithms,
similar to how MainWindow is the container for image analysis algorithms.

It provides:
- Stream management (connection, disconnection)
- Recording management
- Algorithm loading and lifecycle management
- Frame routing from stream to algorithm to display
- UI coordination
"""

from PySide6.QtWidgets import (QMainWindow, QMessageBox, QLabel, QComboBox, QHBoxLayout,
                               QVBoxLayout, QPushButton, QLineEdit, QGroupBox, QWidget,
                               QFileDialog)
from PySide6.QtCore import Qt, QTimer, Slot, QSettings
from typing import Optional, Dict, Any, List
import numpy as np
from types import SimpleNamespace
import time

from core.views.streaming.StreamViewerWindow_ui import Ui_StreamViewerWindow
from core.services.LoggerService import LoggerService
from core.controllers.streaming.components import StreamCoordinator, DetectionRenderer, StreamStatistics
from core.controllers.streaming.shared_widgets import VideoDisplayWidget, DetectionThumbnailWidget, StreamControlWidget
from core.views.streaming.components import PlaybackControlBar
from core.controllers.streaming.base import StreamAlgorithmController
from core.services.streaming.RTMPStreamService import StreamType


class StreamViewerWindow(QMainWindow):
    """
    Main streaming detection window.

    Acts as a container for streaming detection algorithms, handling:
    - Stream connection/disconnection
    - Recording management
    - Algorithm loading and coordination
    - Frame routing and display
    - UI state management

    Similar architecture to MainWindow for image analysis.
    """

    def __init__(self, algorithm_name: Optional[str] = None, theme: str = 'dark'):
        """
        Initialize the streaming viewer window.

        Args:
            algorithm_name: Name of algorithm to load (optional, for direct launch)
            theme: UI theme ('light' or 'dark')
        """
        super().__init__()

        self.logger = LoggerService()
        self.settings = QSettings("ADIAT", "StreamViewer")
        self.theme = theme
        self._maximized_applied = False
        # Store algorithm name - if None, will load default, if empty string, won't load
        self._initial_algorithm_name = algorithm_name if algorithm_name is not None else "ColorAnomalyAndMotionDetection"

        # Setup UI
        self.ui = Ui_StreamViewerWindow()
        self.ui.setupUi(self)

        # Setup tooltip stylesheet
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

        # Core components
        self.stream_coordinator = StreamCoordinator(self.logger)
        self.detection_renderer = DetectionRenderer()
        self.stream_statistics = StreamStatistics()
        self.algorithm_renders_frame = False
        self._latest_detections_for_rendering: List[Dict] = []
        self._last_algorithm_frame: Optional[np.ndarray] = None

        # Current algorithm
        self.algorithm_widget: Optional[StreamAlgorithmController] = None
        self.current_algorithm_name: Optional[str] = None

        # Setup custom widgets
        self.setup_custom_widgets()

        # Connect core signals
        self.connect_signals()

        # UI update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statistics_display)
        self.update_timer.start(1000)  # Update every second

        # Load algorithm if specified (empty string means don't load)
        if self._initial_algorithm_name and self._initial_algorithm_name.strip():
            self.load_algorithm(self._initial_algorithm_name)

        self.logger.info("StreamViewerWindow initialized")

    def setup_custom_widgets(self):
        """Replace placeholder widgets with actual custom widgets."""
        # Video display
        self.video_display = VideoDisplayWidget()
        self.ui.splitter.widget(0).layout().replaceWidget(self.ui.videoLabel, self.video_display)
        self.ui.videoLabel.deleteLater()

        # Playback controls
        self.playback_controls = PlaybackControlBar()
        self.ui.splitter.widget(0).layout().replaceWidget(
            self.ui.playbackControlWidget, self.playback_controls
        )
        self.ui.playbackControlWidget.deleteLater()

        # Thumbnail widget
        self.thumbnail_widget = DetectionThumbnailWidget()
        self.ui.splitter.widget(0).layout().replaceWidget(
            self.ui.thumbnailWidget, self.thumbnail_widget
        )
        self.ui.thumbnailWidget.deleteLater()

        # Stream controls (without recording)
        self.stream_controls = StreamControlWidget(include_recording=False)
        self.ui.streamControlPlaceholder.parent().layout().replaceWidget(
            self.ui.streamControlPlaceholder, self.stream_controls
        )
        self.ui.streamControlPlaceholder.deleteLater()

        # Setup recording widget in its own section
        self._setup_recording_widget()

        # Add algorithm selection to Algorithm Controls section
        self._setup_algorithm_selection()

    def _setup_recording_widget(self):
        """Setup recording widget in its own section between Algorithm Controls and Statistics."""
        # Create recording widget
        recording_widget = QWidget()
        recording_layout = QVBoxLayout(recording_widget)
        recording_layout.setContentsMargins(5, 5, 5, 5)
        recording_layout.setSpacing(5)

        # Recording buttons
        button_layout = QHBoxLayout()
        self.start_recording_btn = QPushButton("Start Recording")
        self.start_recording_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; font-weight: bold; }")
        self.start_recording_btn.setToolTip("Start recording the video stream with detection overlays.")
        self.stop_recording_btn = QPushButton("Stop Recording")
        self.stop_recording_btn.setEnabled(False)
        self.stop_recording_btn.setToolTip("Stop the current recording and save to file.")

        button_layout.addWidget(self.start_recording_btn)
        button_layout.addWidget(self.stop_recording_btn)

        # Recording status
        self.recording_status = QLabel("Status: Not Recording")
        self.recording_status.setStyleSheet("QLabel { color: gray; }")
        self.recording_status.setToolTip("Current recording status and output file path")

        # Recording info
        self.recording_info = QLabel("Duration: --")
        self.recording_info.setToolTip("Recording statistics: Duration, FPS, Frames")

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

        recording_layout.addLayout(button_layout)
        recording_layout.addWidget(self.recording_status)
        recording_layout.addWidget(self.recording_info)
        recording_layout.addLayout(dir_layout)

        # Replace placeholder with recording widget
        self.ui.recordingLayout.replaceWidget(self.ui.recordingPlaceholder, recording_widget)
        self.ui.recordingPlaceholder.deleteLater()

        # Set initial directory from settings
        saved_dir = self.settings.value("recording/output_dir", "./recordings")
        self.recording_dir_edit.setText(saved_dir)

        # Connect signals
        self.start_recording_btn.clicked.connect(self._emit_start_recording)
        self.stop_recording_btn.clicked.connect(self.on_stop_recording_requested)
        self.recording_dir_browse.clicked.connect(self._browse_recording_directory)
        self.recording_dir_edit.textChanged.connect(self._on_recording_directory_changed)

    def _emit_start_recording(self):
        """Emit start recording signal with directory."""
        directory = self.recording_dir_edit.text().strip() or "./recordings"
        self.on_start_recording_requested(directory)

    def _browse_recording_directory(self):
        """Browse for recording directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Recording Directory", self.recording_dir_edit.text()
        )
        if directory:
            self.recording_dir_edit.setText(directory)

    def _on_recording_directory_changed(self, directory: str):
        """Handle recording directory change."""
        cleaned = directory.strip() or "./recordings"
        if cleaned != directory:
            self.recording_dir_edit.setText(cleaned)
        self.settings.setValue("recording/output_dir", cleaned)

    def _setup_algorithm_selection(self):
        """Add algorithm selection dropdown at the top of Algorithm Controls section."""
        # Create algorithm selection layout
        algorithm_layout = QHBoxLayout()
        algorithm_layout.setContentsMargins(0, 0, 0, 10)  # Add bottom margin for spacing

        algorithm_label = QLabel("Algorithm:")
        algorithm_label.setToolTip("Select which streaming detection algorithm to use")

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setToolTip(
            "Choose which streaming detection algorithm to run.\n"
            "• Color Anomaly & Motion Detection: fused anomaly detectors\n"
            "• Color Detection: color-based highlighting"
        )

        # Populate with available algorithms from registry
        registry = self._algorithm_registry()
        algorithm_options = []
        for key in ("ColorAnomalyAndMotionDetection", "ColorDetection"):
            if key in registry:
                label = registry[key].get("label", key)
                algorithm_options.append((label, key))

        # Add to combo box
        for label, key in algorithm_options:
            self.algorithm_combo.addItem(label, key)

        # Set current selection
        if self._initial_algorithm_name:
            for i in range(self.algorithm_combo.count()):
                if self.algorithm_combo.itemData(i) == self._initial_algorithm_name:
                    self.algorithm_combo.setCurrentIndex(i)
                    break

        algorithm_layout.addWidget(algorithm_label)
        algorithm_layout.addWidget(self.algorithm_combo)
        algorithm_layout.addStretch()  # Push to the left

        # Insert at the top of algorithm control layout (before placeholder)
        self.ui.algorithmControlLayout.insertLayout(0, algorithm_layout)

    def connect_signals(self):
        """Connect signals between components."""
        # Stream coordinator signals
        self.stream_coordinator.connectionChanged.connect(self.on_connection_changed)
        self.stream_coordinator.frameReceived.connect(self.on_frame_received)
        self.stream_coordinator.recordingStateChanged.connect(self.on_recording_state_changed)
        self.stream_coordinator.errorOccurred.connect(self.on_error)
        self.stream_coordinator.streamInfoUpdated.connect(self.on_stream_info_updated)

        # Stream controls signals
        self.stream_controls.connectRequested.connect(self.on_connect_requested)
        self.stream_controls.disconnectRequested.connect(self.on_disconnect_requested)

        # Algorithm selection signal (from Algorithm Controls section)
        if hasattr(self, 'algorithm_combo'):
            self.algorithm_combo.currentIndexChanged.connect(self._on_algorithm_combo_changed)

        # Playback controls signals
        self.playback_controls.playPauseToggled.connect(self.on_play_pause_toggled)
        self.playback_controls.seekRequested.connect(self.on_seek_requested)

    def load_algorithm(self, algorithm_name: str):
        """
        Load a streaming detection algorithm.

        Args:
            algorithm_name: Name of algorithm to load
        """
        try:
            self.logger.info(f"Loading algorithm: {algorithm_name}")

            # Remove existing algorithm if any
            if self.algorithm_widget:
                try:
                    self.algorithm_widget.frameProcessed.disconnect(self.on_algorithm_frame_processed)
                except Exception:
                    pass
                self.ui.algorithmControlLayout.removeWidget(self.algorithm_widget)
                self.algorithm_widget.deleteLater()
                self.algorithm_widget = None
                self.algorithm_renders_frame = False
                self.thumbnail_widget.clear_thumbnails()
                self._latest_detections_for_rendering = []
                self._last_algorithm_frame = None

            # Get algorithm configuration
            algorithm_config = self._get_algorithm_config(algorithm_name)
            if not algorithm_config:
                self.logger.error(f"Algorithm not found: {algorithm_name}")
                return

            # Dynamically import and instantiate algorithm controller
            controller_class = self._import_algorithm_controller(algorithm_config)
            if not controller_class:
                self.logger.error(f"Failed to import algorithm controller: {algorithm_name}")
                return

            # Create algorithm widget
            self.algorithm_widget = controller_class(algorithm_config, self.theme)
            self.current_algorithm_name = algorithm_name
            self.algorithm_renders_frame = getattr(self.algorithm_widget, "provides_custom_rendering", False)

            # Sync algorithm combo box selection
            if hasattr(self, 'algorithm_combo'):
                for i in range(self.algorithm_combo.count()):
                    if self.algorithm_combo.itemData(i) == algorithm_name:
                        self.algorithm_combo.blockSignals(True)
                        self.algorithm_combo.setCurrentIndex(i)
                        self.algorithm_combo.blockSignals(False)
                        break

            # Add to layout
            self.ui.algorithmControlLayout.addWidget(self.algorithm_widget)

            # Connect algorithm signals
            self.algorithm_widget.detectionsReady.connect(self.on_detections_ready)
            self.algorithm_widget.frameProcessed.connect(self.on_algorithm_frame_processed)
            self.algorithm_widget.statusUpdate.connect(self.on_status_update)
            self.algorithm_widget.requestRecording.connect(self.on_recording_request)

            self.logger.info(f"Algorithm loaded: {algorithm_name}")
            self.ui.statusbar.showMessage(f"Loaded: {algorithm_name}")

        except Exception as e:
            error_msg = f"Error loading algorithm: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Algorithm Load Error", error_msg)

    def _get_algorithm_config(self, algorithm_name: str) -> Optional[Dict[str, Any]]:
        """
        Get algorithm configuration.

        Args:
            algorithm_name: Name of algorithm

        Returns:
            Algorithm configuration dictionary or None
        """
        algorithms = self._algorithm_registry()
        return algorithms.get(algorithm_name)

    def _algorithm_registry(self) -> Dict[str, Dict[str, Any]]:
        """Return the available streaming algorithms."""
        return {
            'MotionDetection': {
                'label': 'Motion Detection',
                'controller': 'MotionDetectionController',
                'module': 'algorithms.streaming.MotionDetection.controllers.MotionDetectionController'
            },
            'ColorDetection': {
                'label': 'Color Detection',
                'controller': 'ColorDetectionController',
                'module': 'algorithms.streaming.ColorDetection.controllers.ColorDetectionController'
            },
            'ColorAnomalyAndMotionDetection': {
                'label': 'Color Anomaly & Motion Detection',
                'controller': 'ColorAnomalyAndMotionDetectionController',
                'module': 'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.ColorAnomalyAndMotionDetectionController'
            }
        }

    def _import_algorithm_controller(self, algorithm_config: Dict[str, Any]):
        """
        Dynamically import algorithm controller class.

        Args:
            algorithm_config: Algorithm configuration

        Returns:
            Controller class or None
        """
        try:
            module_name = algorithm_config['module']
            class_name = algorithm_config['controller']

            module = __import__(module_name, fromlist=[class_name])
            controller_class = getattr(module, class_name)

            return controller_class

        except Exception as e:
            self.logger.error(f"Failed to import controller: {str(e)}")
            return None

    def _on_algorithm_combo_changed(self, index: int):
        """Handle algorithm selection change from Algorithm Controls dropdown."""
        if hasattr(self, 'algorithm_combo'):
            algorithm_key = self.algorithm_combo.itemData(index)
            if algorithm_key:
                self.on_algorithm_selected(algorithm_key)

    @Slot(str)
    def on_algorithm_selected(self, algorithm_name: str):
        """Handle user selection of a streaming algorithm."""
        if algorithm_name == self.current_algorithm_name:
            return
        self.logger.info(f"Switching algorithm to: {algorithm_name}")
        self.load_algorithm(algorithm_name)
        if not self.algorithm_widget:
            return
        self.stream_statistics.reset()
        self.ui.statsLabel.setText("Switching algorithm...")
        self._latest_detections_for_rendering = []
        self._last_algorithm_frame = None
        self.thumbnail_widget.clear_thumbnails()
        # Notify the new algorithm if we're already connected to a stream
        if self.stream_coordinator.is_connected and self.algorithm_widget:
            resolution = self.stream_coordinator.stream_info.get('resolution') or (1920, 1080)
            try:
                self.algorithm_widget.on_stream_connected(resolution)
            except Exception as e:
                self.logger.error(f"Error notifying algorithm of active stream: {e}")
        config = self._get_algorithm_config(algorithm_name) or {}
        label = config.get("label", algorithm_name)
        self.ui.infoPanel.append(f"Algorithm switched to {label}")

    @Slot(str, object)
    def on_connect_requested(self, url: str, stream_type: StreamType):
        """Handle stream connection request."""
        self.stream_coordinator.connect_stream(url, stream_type)

    @Slot()
    def on_disconnect_requested(self):
        """Handle stream disconnection request."""
        self.stream_coordinator.disconnect_stream()

    @Slot(bool, str)
    def on_connection_changed(self, connected: bool, message: str):
        """Handle connection status change."""
        # Update bottom status bar with connection state
        status_text = f"{'Connected' if connected else 'Disconnected'} - {message}"
        self.ui.statusbar.showMessage(status_text)
        # Update stream controls status section
        if hasattr(self, "stream_controls"):
            self.stream_controls.update_connection_status(connected, message)

        if connected:
            self.ui.infoPanel.append(f"✓ Connected: {message}")

            # Show playback controls for file streams
            if self.stream_coordinator.current_stream_type == StreamType.FILE:
                self.playback_controls.show_for_file()
            else:
                self.playback_controls.hide_for_stream()

            # Notify algorithm
            if self.algorithm_widget:
                # Get stream resolution (placeholder)
                resolution = (1920, 1080)
                self.algorithm_widget.on_stream_connected(resolution)
        else:
            self.ui.infoPanel.append(f"✗ Disconnected: {message}")

            # Hide playback controls
            self.playback_controls.hide_for_stream()

            # Notify algorithm
            if self.algorithm_widget:
                self.algorithm_widget.on_stream_disconnected()

            # Reset statistics
            self.stream_statistics.reset()

    @Slot(np.ndarray, float)
    def on_frame_received(self, frame: np.ndarray, timestamp: float):
        """Handle frame received from stream."""
        # Record frame receipt in statistics
        self.stream_statistics.on_frame_received(timestamp)

        # Process frame with algorithm if loaded
        if self.algorithm_widget:
            start_time = time.time()

            try:
                # Process frame
                detections = self.algorithm_widget.process_frame(frame, timestamp)

                # Record processing completion
                processing_time_ms = (time.time() - start_time) * 1000
                self.stream_statistics.on_frame_processed(processing_time_ms, len(detections))

                self._latest_detections_for_rendering = detections

                rendered_frame = None
                if not self.algorithm_renders_frame:
                    # Render detections using the shared renderer
                    rendered_frame = self.detection_renderer.render(frame, detections)

                    # Update display with rendered frame
                    self.video_display.update_frame(rendered_frame)

                # Update thumbnails
                if detections:
                    # Convert detection dicts to objects with required attributes for tracker
                    detection_objects = []
                    for det_dict in detections:
                        # Create object with required attributes (bbox, centroid, metadata)
                        obj = SimpleNamespace()
                        obj.bbox = det_dict.get('bbox', (0, 0, 0, 0))

                        # Calculate centroid from bbox if not provided
                        if 'centroid' in det_dict:
                            obj.centroid = det_dict['centroid']
                        else:
                            # Calculate from bbox: (x, y, width, height) -> centroid
                            x, y, w, h = obj.bbox
                            obj.centroid = (x + w // 2, y + h // 2)

                        obj.area = det_dict.get('area', 0.0)
                        obj.confidence = det_dict.get('confidence', 0.0)
                        obj.metadata = det_dict.get('metadata', {})
                        # Copy any other attributes
                        for key, value in det_dict.items():
                            if not hasattr(obj, key):
                                setattr(obj, key, value)

                        detection_objects.append(obj)

                    processing_resolution = None
                    original_resolution = None
                    for det in detection_objects:
                        metadata = getattr(det, "metadata", {}) or {}
                        if metadata and processing_resolution is None:
                            processing_resolution = metadata.get('processing_resolution')
                        if metadata and original_resolution is None:
                            original_resolution = metadata.get('original_resolution')
                        if processing_resolution and original_resolution:
                            break

                    self.thumbnail_widget.update_thumbnails(
                        frame,
                        detection_objects,
                        processing_resolution=processing_resolution,
                        original_resolution=original_resolution
                    )

                # Record frame if recording (when rendering is handled here)
                if self.stream_coordinator.is_recording and not self.algorithm_renders_frame:
                    if rendered_frame is None:
                        rendered_frame = frame
                    self.stream_coordinator.record_frame(rendered_frame, detections)

            except Exception as e:
                self.logger.error(f"Error processing frame: {str(e)}")
        else:
            # No algorithm loaded, just display frame
            self.video_display.update_frame(frame)

    @Slot(np.ndarray)
    def on_algorithm_frame_processed(self, annotated_frame: np.ndarray):
        """Handle frames rendered by the algorithm itself."""
        if not self.algorithm_renders_frame:
            return

        self.video_display.update_frame(annotated_frame)

        if self.stream_coordinator.is_recording:
            detections = getattr(self, "_latest_detections_for_rendering", [])
            self.stream_coordinator.record_frame(annotated_frame, detections)

    @Slot(list)
    def on_detections_ready(self, detections: list):
        """Handle detections from algorithm."""
        # Update detection info panel with a concise summary
        self.ui.infoPanel.clear()
        if not detections:
            self.ui.infoPanel.setPlainText("No detections found.")
            return

        self.ui.infoPanel.append(f"Detection Results ({len(detections)} found):")
        # Show a brief summary of up to first 5 detections
        for idx, det in enumerate(detections[:5], start=1):
            bbox = det.get("bbox") if isinstance(det, dict) else getattr(det, "bbox", None)
            cls = det.get("class_name") if isinstance(det, dict) else getattr(det, "class_name", "Detection")
            conf = det.get("confidence") if isinstance(det, dict) else getattr(det, "confidence", None)
            if bbox is not None:
                x, y, w, h = bbox
                summary = f"#{idx}: Type({cls}) Pos({x},{y}) Size({w}x{h})"
            else:
                summary = f"#{idx}: Type({cls})"
            if conf is not None:
                summary += f" Conf({conf:.2f})"
            self.ui.infoPanel.append(summary)

    @Slot(str)
    def on_start_recording_requested(self, directory: str):
        """Start recording with provided directory."""
        output_dir = directory or "./recordings"
        self.settings.setValue("recording/output_dir", output_dir)
        self.settings.sync()
        self.stream_coordinator.start_recording(output_dir)

    @Slot()
    def on_stop_recording_requested(self):
        """Stop the current recording."""
        self.stream_coordinator.stop_recording()

    @Slot(str)
    def on_recording_directory_changed(self, directory: str):
        """Persist recording directory changes."""
        output_dir = directory or "./recordings"
        self.settings.setValue("recording/output_dir", output_dir)
        self.settings.sync()

    @Slot(bool)
    def on_recording_toggled(self, start: bool):
        """Handle recording toggle from algorithms."""
        if start:
            directory = self.recording_dir_edit.text().strip() or "./recordings"
            self.on_start_recording_requested(directory)
        else:
            self.on_stop_recording_requested()

    @Slot(bool, str)
    def on_recording_state_changed(self, recording: bool, path: str):
        """Handle recording state change."""
        # Update recording widget
        self._update_recording_state(recording, path)

        if recording:
            self.ui.statusbar.showMessage(f"Recording started: {path}")

            # Notify algorithm
            if self.algorithm_widget:
                self.algorithm_widget.on_recording_started(path)
        else:
            self.ui.statusbar.showMessage("Recording stopped")

            # Notify algorithm
            if self.algorithm_widget:
                self.algorithm_widget.on_recording_stopped(path)

    def _update_recording_state(self, recording: bool, path: str):
        """Update recording widget UI state."""
        if hasattr(self, 'start_recording_btn') and hasattr(self, 'stop_recording_btn'):
            self.start_recording_btn.setEnabled(not recording)
            self.stop_recording_btn.setEnabled(recording)

            if recording:
                self.recording_status.setText(f"Status: Recording to {path}")
                self.recording_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            else:
                self.recording_status.setText("Status: Not Recording")
                self.recording_status.setStyleSheet("QLabel { color: gray; }")
                self.recording_info.setText("Duration: --")

    @Slot(str)
    def on_status_update(self, message: str):
        """Handle status update from algorithm."""
        self.ui.statusbar.showMessage(message)

    @Slot(str)
    def on_error(self, error: str):
        """Handle error."""
        self.logger.error(error)
        self.ui.infoPanel.append(f"✗ Error: {error}")
        QMessageBox.warning(self, "Error", error)

    @Slot(bool)
    def on_recording_request(self, start: bool):
        """Handle recording request from algorithm."""
        self.on_recording_toggled(start)

    @Slot()
    def on_play_pause_toggled(self):
        """Handle play/pause toggle (for file playback)."""
        # Toggle play/pause on stream manager
        if self.stream_coordinator.stream_manager and hasattr(self.stream_coordinator.stream_manager, 'play_pause'):
            self.stream_coordinator.stream_manager.play_pause()

    @Slot(float)
    def on_seek_requested(self, time_seconds: float):
        """Handle seek request (for file playback)."""
        # Request seek from stream manager
        if self.stream_coordinator.stream_manager and hasattr(self.stream_coordinator.stream_manager, 'seek_to_time'):
            self.stream_coordinator.stream_manager.seek_to_time(time_seconds)

    @Slot(dict)
    def on_stream_info_updated(self, stream_info: dict):
        """Handle stream info updates (for playback position)."""
        # Update playback controls with video position if available
        if self.stream_coordinator.current_stream_type == StreamType.FILE:
            if 'current_time' in stream_info and 'total_time' in stream_info:
                self.playback_controls.update_time(stream_info['current_time'], stream_info['total_time'])
            if 'is_playing' in stream_info:
                is_playing = stream_info['is_playing']
                self.playback_controls.update_play_state(is_playing)

    def update_statistics_display(self):
        """Update statistics display."""
        stats_dict = self.stream_statistics.get_stats_dict()

        # Update detailed stats panel
        stats_text = "\n".join([f"{key}: {value}" for key, value in stats_dict.items()])
        self.ui.statsLabel.setText(stats_text)

        # Update performance section in stream controls
        stats_obj = self.stream_statistics.get_stats()
        perf_payload = {
            "fps": stats_obj.fps,
            "avg_fps": stats_obj.processing_fps,
            "current_processing_time_ms": stats_obj.avg_processing_time_ms,
            "avg_processing_time_ms": stats_obj.avg_processing_time_ms,
            "detection_count": stats_obj.detection_count,
            "dropped_frames": stats_obj.dropped_frames,
        }
        self.stream_controls.update_performance(perf_payload)

    def showEvent(self, event):
        """Ensure the viewer launches maximized on first show."""
        super().showEvent(event)
        if not self._maximized_applied:
            self._maximized_applied = True
            self.showMaximized()

    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Closing StreamViewerWindow")

        # Cleanup
        self.update_timer.stop()

        if self.algorithm_widget:
            self.algorithm_widget.cleanup()

        self.stream_coordinator.cleanup()

        event.accept()
