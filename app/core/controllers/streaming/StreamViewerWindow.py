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
                               QFileDialog, QApplication, QDialog)
from PySide6.QtCore import Qt, QTimer, Slot, QSettings, QUrl, QThread, QObject
from PySide6.QtGui import QAction, QDesktopServices
from typing import Optional, Dict, Any, List, Callable
import numpy as np
from types import SimpleNamespace
import time
import os

import qdarktheme
from core.controllers.Perferences import Preferences
from core.controllers.streaming.StreamingGuide import StreamingGuide
# MainWindow imported lazily in _open_image_analysis() to avoid circular dependency
from core.services.SettingsService import SettingsService
from core.views.streaming.StreamViewerWindow_ui import Ui_StreamViewerWindow
from core.services.LoggerService import LoggerService
from core.controllers.streaming.components import StreamCoordinator, DetectionRenderer, StreamStatistics
from core.controllers.streaming.components.FrameProcessingWorker import FrameProcessingWorker
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
        self.settings_service = SettingsService()
        self.app_version = self.settings_service.get_setting('app_version', '2.0.0') or '2.0.0'
        self.theme = theme
        self._maximized_applied = False
        # Store algorithm name - if None, will load default, if empty string, won't load
        self._initial_algorithm_name = algorithm_name if algorithm_name is not None else "ColorAnomalyAndMotionDetection"
        self._pending_auto_record = False
        self._pending_record_dir = None
        self._pending_algorithm_options = None
        self._pending_processing_resolution = None  # Desired resolution from wizard (to be capped to native)

        # Setup UI
        self.ui = Ui_StreamViewerWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Automated Drone Image Analysis Tool v{self.app_version} - Sponsored by TEXSAR")

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

        # Store algorithm configs for session persistence (forgotten on close)
        self._algorithm_configs: Dict[str, Dict[str, Any]] = {}

        # Frame processing worker thread (moves algorithm processing off main thread)
        self._processing_thread: Optional[QThread] = None
        self._processing_worker: Optional[FrameProcessingWorker] = None
        self._is_stopping_worker = False  # Flag to prevent new frames from being queued during cleanup

        # Setup custom widgets
        self.setup_custom_widgets()
        self.setup_menus()

        # Connect core signals
        self.connect_signals()

        # UI update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statistics_display)
        self.update_timer.start(1000)  # Update every second

        # Load algorithm if specified (empty string means don't load)
        if self._initial_algorithm_name and self._initial_algorithm_name.strip():
            self.load_algorithm(self._initial_algorithm_name)

        # self.logger.info("StreamViewerWindow initialized")

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

    def setup_menus(self):
        """Create top-level menus for navigation and help."""
        menu_bar = self.menuBar()
        menu_bar.clear()

        # Primary navigation menu
        primary_menu = menu_bar.addMenu("Menu")
        self.action_streaming_guide = QAction("Streaming Analysis Wizard", self)
        self.action_image_analysis = QAction("Image Analysis", self)
        self.action_preferences = QAction("Preferences", self)
        primary_menu.addAction(self.action_streaming_guide)
        primary_menu.addSeparator()
        primary_menu.addAction(self.action_image_analysis)
        primary_menu.addAction(self.action_preferences)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        self.action_manual = QAction("Manual", self)
        self.action_community = QAction("Community Forum", self)
        help_menu.addAction(self.action_manual)
        help_menu.addAction(self.action_community)

        # Wire actions
        self.action_streaming_guide.triggered.connect(self._open_streaming_guide)
        self.action_image_analysis.triggered.connect(self._open_image_analysis)
        self.action_preferences.triggered.connect(self._open_preferences)
        self.action_manual.triggered.connect(self._open_manual)
        self.action_community.triggered.connect(self._open_community_forum)

    def _setup_recording_widget(self):
        """Setup recording widget in its own section between Algorithm Controls and the bottom of the panel."""
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
        default_recording_dir = os.path.expanduser("~")
        self.recording_dir_edit = QLineEdit(default_recording_dir)
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
        default_recording_dir = os.path.expanduser("~")
        saved_dir = self.settings.value("recording/output_dir", default_recording_dir)
        # Migrate old default "./recordings" or "/recordings" to new default (user's home directory)
        # Normalize paths for comparison
        if saved_dir:
            saved_dir_normalized = os.path.normpath(saved_dir).replace('\\', '/')
            old_defaults = ["./recordings", "/recordings", "recordings"]
            old_defaults_normalized = [os.path.normpath(d).replace('\\', '/') for d in old_defaults]
            if saved_dir_normalized in old_defaults_normalized or saved_dir_normalized.endswith('/recordings'):
                saved_dir = default_recording_dir
                self.settings.setValue("recording/output_dir", saved_dir)
                self.settings.sync()
        else:
            saved_dir = default_recording_dir
            self.settings.setValue("recording/output_dir", saved_dir)
            self.settings.sync()
        self.recording_dir_edit.setText(saved_dir)

        # Connect signals
        self.start_recording_btn.clicked.connect(self._emit_start_recording)
        self.stop_recording_btn.clicked.connect(self.on_stop_recording_requested)
        self.recording_dir_browse.clicked.connect(self._browse_recording_directory)
        self.recording_dir_edit.textChanged.connect(self._on_recording_directory_changed)

    def _emit_start_recording(self):
        """Emit start recording signal with directory."""
        default_recording_dir = os.path.expanduser("~")
        directory = self.recording_dir_edit.text().strip() or default_recording_dir
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
        default_recording_dir = os.path.expanduser("~")
        cleaned = directory.strip() or default_recording_dir
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
        preferred_order = [
            "ColorAnomalyAndMotionDetection",
            "ColorDetection",
        ]
        for key in preferred_order:
            if key in registry:
                label = registry[key].get("label", key)
                algorithm_options.append((label, key))
        for key, cfg in registry.items():
            if key not in [k for _, k in algorithm_options]:
                algorithm_options.append((cfg.get("label", key), key))

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

    def apply_wizard_data(self, wizard_data: dict) -> None:
        """Apply wizard selections to the viewer and optionally auto-connect."""
        if not wizard_data:
            return

        stream_type = wizard_data.get("stream_type")
        if stream_type:
            idx = self.stream_controls.type_combo.findText(stream_type)
            if idx >= 0:
                self.stream_controls.type_combo.setCurrentIndex(idx)

        stream_url = wizard_data.get("stream_url")
        if stream_url:
            self.stream_controls.url_input.setText(stream_url)

        default_recording_dir = os.path.expanduser("~")
        recording_dir = wizard_data.get("recording_dir") or default_recording_dir
        if hasattr(self, "recording_dir_edit"):
            self.recording_dir_edit.setText(recording_dir)
        self.settings.setValue("recording/output_dir", recording_dir)
        self.settings.sync()

        algorithm = wizard_data.get("algorithm")
        algorithm_options = wizard_data.get("algorithm_options") or {}

        # Calculate and set min/max area from object size and GSD (like MainWindow does)
        # GSD is stored in gsd_list as a list of sensor GSD values
        gsd_list = wizard_data.get('gsd_list', [])
        if wizard_data.get('object_size_min') and wizard_data.get('object_size_max') and gsd_list:
            # Use the first GSD value from the list (or average if multiple sensors)
            # Each item in gsd_list is a dict with 'gsd' key in cm/pixel
            gsd_values = [item.get('gsd') for item in gsd_list if item.get('gsd')]
            if gsd_values:
                # Use the first GSD value (or could average them)
                gsd_cm_per_pixel = gsd_values[0]

                object_size_min_ft = wizard_data['object_size_min']
                object_size_max_ft = wizard_data['object_size_max']

                # Convert object size from feet to cm, then to pixels
                # object_size_cm = object_size_ft * 30.48
                # pixels = object_size_cm / gsd_cm_per_pixel
                # area_pixels = pixels^2
                min_pixels = (object_size_min_ft * 30.48) / gsd_cm_per_pixel
                max_pixels = (object_size_max_ft * 30.48) / gsd_cm_per_pixel
                min_area = max(10, int((min_pixels * min_pixels) / 250))
                max_area = max(100, int(max_pixels * max_pixels))

                # Merge calculated min/max area into algorithm options
                # Map to algorithm-specific field names
                algorithm_options['min_area'] = min_area
                algorithm_options['max_area'] = max_area
                # ColorAnomalyAndMotionDetection uses min_detection_area/max_detection_area
                algorithm_options['min_detection_area'] = min_area
                algorithm_options['max_detection_area'] = max_area
                # Also set color-specific areas for ColorAnomalyAndMotionDetection
                algorithm_options['color_min_detection_area'] = min_area
                algorithm_options['color_max_detection_area'] = max_area

        # Convert wizard's processing resolution (percentage) to actual dimensions
        resolution = wizard_data.get("processing_resolution")
        if resolution:
            # Map wizard percentage values to actual dimensions
            # 25 = 480p, 50 = 720p, 75 = 1080p, 100 = 4K
            resolution_map = {
                25: (854, 480),      # 480p
                50: (1280, 720),     # 720p
                75: (1920, 1080),    # 1080p
                100: (3840, 2160)    # 4K
            }

            # Get dimensions from map
            if isinstance(resolution, (int, float)) and resolution in resolution_map:
                processing_width, processing_height = resolution_map[resolution]

                # Store as pending - will be capped to native resolution when first frame arrives
                self._pending_processing_resolution = (processing_width, processing_height)

                # Add to algorithm options (will be updated with capped value when stream connects)
                algorithm_options['processing_width'] = processing_width
                algorithm_options['processing_height'] = processing_height
                algorithm_options['processing_resolution'] = (processing_width, processing_height)

            # Save the setting (keep as percentage for wizard persistence)
            self.settings_service.set_setting("StreamingProcessingResolution", resolution)

        if algorithm:
            # Store algorithm options BEFORE loading algorithm (like MainWindow does)
            self._pending_algorithm_options = algorithm_options

            if hasattr(self, "algorithm_combo"):
                for i in range(self.algorithm_combo.count()):
                    if self.algorithm_combo.itemData(i) == algorithm:
                        self.algorithm_combo.setCurrentIndex(i)
                        break

            # Check if algorithm is already loaded
            if algorithm == self.current_algorithm_name and self.algorithm_widget:
                # Algorithm already loaded - apply options immediately
                QApplication.processEvents()
                self._apply_algorithm_options(algorithm_options)
                self._pending_algorithm_options = None
            else:
                # Load algorithm (will apply pending options in load_algorithm)
                self.on_algorithm_selected(algorithm)

        self._pending_auto_record = bool(wizard_data.get("auto_record"))
        self._pending_record_dir = recording_dir

        if wizard_data.get("auto_connect") and stream_url:
            combo_text = self.stream_controls.type_combo.currentText()
            stream_type_map = {
                "File": StreamType.FILE,
                "HDMI Capture": StreamType.HDMI_CAPTURE,
                "RTMP Stream": StreamType.RTMP,
            }
            selected_type = stream_type_map.get(combo_text, StreamType.FILE)
            self.on_connect_requested(stream_url, selected_type)

    def _apply_algorithm_options(self, options: dict):
        """Apply algorithm options from wizard to the current algorithm widget.

        Args:
            options: Dictionary of algorithm options from wizard
        """
        if not self.algorithm_widget or not options:
            return

        try:
            # Try set_config first (used by algorithm controllers)
            if hasattr(self.algorithm_widget, 'set_config'):
                self.algorithm_widget.set_config(options)
                # self.logger.info(f"Applied algorithm options via set_config: {list(options.keys())}")
            # Fallback to load_options (used by wizard controllers)
            elif hasattr(self.algorithm_widget, 'load_options'):
                self.algorithm_widget.load_options(options)
                # self.logger.info(f"Applied algorithm options via load_options: {list(options.keys())}")
            else:
                self.logger.warning(f"Algorithm widget {type(self.algorithm_widget)} has no set_config or load_options method")
        except Exception as e:
            self.logger.error(f"Error applying algorithm options: {e}")

    def _open_streaming_guide(self):
        """Open the Streaming Analysis Guide wizard."""
        try:
            wizard = StreamingGuide(self)
            wizard_data_from_wizard = None

            def _on_wizard_completed(wizard_data):
                nonlocal wizard_data_from_wizard
                wizard_data_from_wizard = wizard_data

            wizard.wizardCompleted.connect(_on_wizard_completed)
            wizard_result = wizard.exec()

            # If wizard was completed (not cancelled), apply the wizard data
            if wizard_result == QDialog.Accepted and wizard_data_from_wizard:
                self.apply_wizard_data(wizard_data_from_wizard)
        except Exception as e:
            self.logger.error(f"Error opening Streaming Analysis Guide: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Streaming Analysis Guide:\n{str(e)}")

    def _open_image_analysis(self):
        """Open the Image Analysis main window and close this streaming viewer."""
        try:
            # Lazy import to avoid circular dependency with MainWindow
            from core.controllers.images.MainWindow import MainWindow
            main_window = MainWindow(qdarktheme)
            app = QApplication.instance()
            if app:
                app._main_window = main_window
            main_window.show()
            self.close()
        except Exception as e:
            self.logger.error(f"Error opening Image Analysis: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Image Analysis:\n{str(e)}")

    def _open_preferences(self):
        """Open the Preferences dialog."""
        try:
            pref = Preferences(self)
            pref.exec()
        except Exception as e:
            self.logger.error(f"Error opening Preferences: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Preferences:\n{str(e)}")

    def _open_manual(self):
        """Open the user manual in the default browser."""
        try:
            url = QUrl("https://www.texsar.org/automated-drone-image-analysis-tool/")
            QDesktopServices.openUrl(url)
            # self.logger.info("Help documentation opened")
        except Exception as e:
            self.logger.error(f"Error opening Help URL: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Help documentation:\n{str(e)}")

    def _open_community_forum(self):
        """Open the community forum link in the default browser."""
        try:
            url = QUrl("https://discord.com/invite/aY9tY7JSPu")
            QDesktopServices.openUrl(url)
            # self.logger.info("Community forum opened")
        except Exception as e:
            self.logger.error(f"Error opening Community Forum URL: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Community Forum:\n{str(e)}")

    def load_algorithm(self, algorithm_name: str):
        """
        Load a streaming detection algorithm.

        Args:
            algorithm_name: Name of algorithm to load
        """
        try:
            # self.logger.info(f"Loading algorithm: {algorithm_name}")

            # Save current algorithm config before removing it
            if self.algorithm_widget and self.current_algorithm_name:
                try:
                    if hasattr(self.algorithm_widget, 'get_config'):
                        saved_config = self.algorithm_widget.get_config()
                        self._algorithm_configs[self.current_algorithm_name] = saved_config
                        # self.logger.info(f"Saved config for algorithm: {self.current_algorithm_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to save config for {self.current_algorithm_name}: {e}")

            # Stop and cleanup processing worker thread
            self._cleanup_processing_worker()

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

            # Ensure the algorithm widget's layout is activated before adding to parent
            # This ensures its size hint is calculated immediately
            if hasattr(self.algorithm_widget, 'layout') and self.algorithm_widget.layout():
                self.algorithm_widget.layout().activate()

            # Add to layout
            self.ui.algorithmControlLayout.addWidget(self.algorithm_widget)

            # Activate the parent layout to force immediate size calculation
            self.ui.algorithmControlLayout.activate()

            # Get the scroll area from the splitter (it's the second widget)
            # The issue: QScrollArea with setWidgetResizable(True) only shows scroll bars
            # when the widget's minimumSizeHint() exceeds the viewport. This calculation
            # is deferred until layout activation. We force it now.
            if self.ui.splitter.count() > 1:
                scroll_area = self.ui.splitter.widget(1)
                if scroll_area and hasattr(scroll_area, 'widget'):
                    right_panel = scroll_area.widget()
                    if right_panel and hasattr(right_panel, 'layout') and right_panel.layout():
                        # Activate the right panel's layout to calculate size hints
                        right_panel.layout().activate()
                        # Force scroll area to recalculate and check for scroll bars
                        scroll_area.updateGeometry()

            # Connect algorithm signals
            self.algorithm_widget.detectionsReady.connect(self.on_detections_ready)
            self.algorithm_widget.frameProcessed.connect(self.on_algorithm_frame_processed)
            self.algorithm_widget.statusUpdate.connect(self.on_status_update)
            self.algorithm_widget.requestRecording.connect(self.on_recording_request)

            # Setup frame processing worker thread (moves heavy computation off main thread)
            self._setup_processing_worker()

            # self.logger.info(f"Algorithm loaded: {algorithm_name}")
            self.ui.statusbar.showMessage(f"Loaded: {algorithm_name}")

            # Restore saved config for this algorithm if available (session persistence)
            # Only restore if we don't have pending wizard options (wizard takes priority)
            if hasattr(self, '_pending_algorithm_options') and self._pending_algorithm_options:
                # Wizard options take priority - apply them
                self._apply_algorithm_options(self._pending_algorithm_options)
                self._pending_algorithm_options = None
            elif algorithm_name in self._algorithm_configs:
                # Restore previously saved config for this algorithm
                saved_config = self._algorithm_configs[algorithm_name]
                # self.logger.info(f"Restoring saved config for algorithm: {algorithm_name}")
                self._apply_algorithm_options(saved_config)

        except Exception as e:
            error_msg = f"Error loading algorithm: {str(e)}"
            self.logger.error(error_msg)
            QMessageBox.critical(self, "Algorithm Load Error", error_msg)

    def _get_algorithm_service(self) -> Optional[QObject]:
        """
        Get the algorithm service object that can be moved to a worker thread.

        Returns:
            The service QObject, or None if not available
        """
        if not self.algorithm_widget:
            return None

        # Different algorithms expose their services differently
        # ColorDetectionController has color_detector
        if hasattr(self.algorithm_widget, 'color_detector'):
            return self.algorithm_widget.color_detector

        # ColorAnomalyAndMotionDetectionController has integrated_detector
        if hasattr(self.algorithm_widget, 'integrated_detector'):
            return self.algorithm_widget.integrated_detector

        # MotionDetectionController has motion_detector
        if hasattr(self.algorithm_widget, 'motion_detector'):
            return self.algorithm_widget.motion_detector

        return None

    def _create_processing_function(self, service: QObject) -> Callable:
        """
        Create a processing function that uses the service to process frames.

        This function will be called in the worker thread, so it should only
        use the service object (which is moved to the worker thread).

        Args:
            service: The algorithm service QObject

        Returns:
            A function that processes a frame and returns detections
        """
        # ColorDetectionService
        if hasattr(service, 'detect_colors'):
            def process_color(frame: np.ndarray, timestamp: float) -> List[Dict]:
                detections = service.detect_colors(frame, timestamp)

                # Create annotated frame directly on the worker thread so the emitted
                # frame already contains algorithm-rendered overlays.
                try:
                    annotated_frame = service.create_annotated_frame(frame, detections)
                    if annotated_frame is not None and annotated_frame is not frame:
                        # Copy annotated frame back into the original buffer that will be emitted
                        np.copyto(frame, annotated_frame)
                except Exception:
                    # Fall back silently if annotation fails – raw frame will be shown
                    pass

                # Convert to standard format
                detection_dicts = []
                for detection in detections:
                    color_id = detection.color_id if detection.color_id is not None else 0
                    detection_dicts.append({
                        'bbox': detection.bbox,
                        'area': detection.area,
                        'confidence': detection.confidence,
                        'class_name': f"Color_{color_id}",
                        'color_id': color_id,
                        'mean_color': detection.mean_color
                    })
                return detection_dicts
            return process_color

        # ColorAnomalyAndMotionDetectionOrchestrator
        if hasattr(service, 'process_frame'):
            # Check if it returns (annotated_frame, detections, timings)
            def process_integrated(frame: np.ndarray, timestamp: float) -> List[Dict]:
                annotated_frame, detections, timings = service.process_frame(frame, timestamp)

                # Ensure the annotated frame is what gets displayed when the algorithm
                # provides its own rendering (copy onto the outgoing buffer).
                try:
                    if annotated_frame is not None and annotated_frame is not frame:
                        np.copyto(frame, annotated_frame)
                except Exception:
                    pass

                # Convert to standard format
                detection_dicts = []
                for detection in detections:
                    detection_dicts.append({
                        'bbox': detection.bbox,
                        'centroid': detection.centroid,
                        'area': detection.area,
                        'confidence': detection.confidence,
                        'class_name': detection.detection_type,
                        'detection_type': detection.detection_type,
                        'timestamp': detection.timestamp,
                        'metadata': detection.metadata
                    })
                return detection_dicts
            return process_integrated

        # MotionDetectionService
        if hasattr(service, 'detect_motion'):
            def process_motion(frame: np.ndarray, timestamp: float) -> List[Dict]:
                detections = service.detect_motion(frame, timestamp)
                # Convert to standard format
                detection_dicts = []
                for detection in detections:
                    detection_dicts.append({
                        'bbox': detection.bbox,
                        'area': detection.area,
                        'confidence': detection.confidence,
                        'class_name': detection.detection_type,
                        'detection_type': detection.detection_type,
                        'timestamp': detection.timestamp,
                        'metadata': detection.metadata
                    })
                return detection_dicts
            return process_motion

        # Fallback: use controller's process_frame (but this won't work from worker thread)
        # So we return None to indicate we can't use worker thread
        return None

    def _setup_processing_worker(self):
        """Set up the frame processing worker thread."""
        # Clean up any existing worker
        self._cleanup_processing_worker()

        if not self.algorithm_widget:
            return

        # Get the algorithm service
        service = self._get_algorithm_service()
        if not service:
            self.logger.warning("Algorithm service not found, processing will run on main thread")
            return

        # Create processing function
        processing_function = self._create_processing_function(service)
        if not processing_function:
            self.logger.warning("Could not create processing function, processing will run on main thread")
            return

        try:
            # Create pause check function for worker (checks if stream is paused)
            def pause_check():
                """Check if stream is paused (called from worker thread)."""
                if (self.stream_coordinator.stream_manager and
                        hasattr(self.stream_coordinator.stream_manager, 'is_playing')):
                    return not self.stream_coordinator.stream_manager.is_playing()
                return False

            # Create worker thread
            self._processing_thread = QThread()
            self._processing_worker = FrameProcessingWorker(processing_function, pause_check)

            # Move service and worker to thread
            service.moveToThread(self._processing_thread)
            self._processing_worker.moveToThread(self._processing_thread)

            # Connect worker signals
            self._processing_worker.frameProcessed.connect(self._on_worker_frame_processed, Qt.QueuedConnection)
            self._processing_worker.errorOccurred.connect(self._on_worker_error, Qt.QueuedConnection)

            # Connect thread finished signal
            self._processing_thread.finished.connect(self._processing_thread.deleteLater)

            # Start thread
            self._processing_thread.start()

            # Reset stopping flag when starting new worker
            self._is_stopping_worker = False

            # self.logger.info("Frame processing worker thread started")

        except Exception as e:
            self.logger.error(f"Failed to setup processing worker: {e}")
            self._cleanup_processing_worker()

    def _cleanup_processing_worker(self):
        """Clean up the frame processing worker thread."""
        # Set flag early to prevent new frames from being queued
        self._is_stopping_worker = True

        # Disconnect processFrameRequested signal immediately to prevent new frames from queuing
        # This effectively clears the queue for new signals (existing queued signals will still process)
        if self._processing_worker:
            try:
                # Disconnect processFrameRequested to prevent new frames from being queued
                self._processing_worker.processFrameRequested.disconnect()
            except (RuntimeError, TypeError):
                # Signal may already be disconnected, ignore
                pass

        # Stop the worker first (thread-safe via signal)
        if self._processing_worker:
            try:
                self._processing_worker.stop()
            except RuntimeError:
                # Worker may already be deleted, ignore
                pass

        # Stop and cleanup thread
        if self._processing_thread:
            if self._processing_thread.isRunning():
                self._processing_thread.quit()
                if not self._processing_thread.wait(2000):  # Wait up to 2 seconds
                    self.logger.warning("Processing thread didn't stop gracefully, terminating")
                    self._processing_thread.terminate()
                    self._processing_thread.wait(1000)
            # Thread will delete itself via deleteLater() connected to finished signal
            self._processing_thread = None

        # Disconnect remaining signals after thread is stopped to prevent queued signals from accessing deleted objects
        if self._processing_worker:
            try:
                self._processing_worker.frameProcessed.disconnect()
                self._processing_worker.errorOccurred.disconnect()
                self._processing_worker.stopRequested.disconnect()
            except (RuntimeError, TypeError):
                # Signals may already be disconnected, ignore
                pass

        # Move service back to main thread after thread is stopped
        service = self._get_algorithm_service()
        if service:
            try:
                service.moveToThread(None)  # Move back to main thread
            except RuntimeError:
                # Service may already be deleted or moved, ignore
                pass

        # Clear worker reference (worker will be deleted when thread is deleted)
        self._processing_worker = None
        self._is_stopping_worker = False  # Reset flag after cleanup

    @Slot(np.ndarray, list, float)
    def _on_worker_frame_processed(self, frame: np.ndarray, detections: List[Dict], processing_time_ms: float):
        """Handle frame processed by worker thread."""
        # This runs on main thread (via QueuedConnection)
        self.stream_statistics.on_frame_processed(processing_time_ms, len(detections))
        self._latest_detections_for_rendering = detections

        rendered_frame = None
        if not self.algorithm_renders_frame:
            # Render detections using the shared renderer (on main thread)
            rendered_frame = self.detection_renderer.render(frame, detections)
            # Update display with rendered frame
            self.video_display.update_frame(rendered_frame)
        else:
            # Algorithm already rendered onto the frame (e.g., ColorDetection)
            self.video_display.update_frame(frame)

        # Update thumbnails
        if detections:
            # Convert detection dicts to objects with required attributes for tracker
            detection_objects = []
            for det_dict in detections:
                obj = SimpleNamespace()
                obj.bbox = det_dict.get('bbox', (0, 0, 0, 0))

                if 'centroid' in det_dict:
                    obj.centroid = det_dict['centroid']
                else:
                    x, y, w, h = obj.bbox
                    obj.centroid = (x + w // 2, y + h // 2)

                obj.area = det_dict.get('area', 0.0)
                obj.confidence = det_dict.get('confidence', 0.0)
                obj.metadata = det_dict.get('metadata', {})
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

        # Record frame if recording
        if self.stream_coordinator.is_recording:
            if not self.algorithm_renders_frame:
                if rendered_frame is None:
                    rendered_frame = frame
                self.stream_coordinator.record_frame(rendered_frame, detections)
            else:
                self.stream_coordinator.record_frame(frame, detections)

        # Emit detections via controller (for compatibility with existing signal connections)
        if self.algorithm_widget:
            # Emit signal directly (we're already on main thread)
            self.algorithm_widget.detectionsReady.emit(detections)

    @Slot(str)
    def _on_worker_error(self, error_msg: str):
        """Handle error from worker thread."""
        self.logger.error(f"Worker thread error: {error_msg}")

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
        # If algorithm is already loaded, still apply pending options if any
        if algorithm_name == self.current_algorithm_name:
            if hasattr(self, '_pending_algorithm_options') and self._pending_algorithm_options:
                QApplication.processEvents()
                self._apply_algorithm_options(self._pending_algorithm_options)
                self._pending_algorithm_options = None
            return

        # self.logger.info(f"Switching algorithm to: {algorithm_name}")
        self.load_algorithm(algorithm_name)
        if not self.algorithm_widget:
            return
        self.stream_statistics.reset()
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
                # Get stream resolution from stream_info if available, otherwise use placeholder
                resolution = self.stream_coordinator.stream_info.get('resolution') or (1920, 1080)
                self.algorithm_widget.on_stream_connected(resolution)

            if self._pending_auto_record:
                default_recording_dir = os.path.expanduser("~")
                record_dir = self._pending_record_dir or self.recording_dir_edit.text().strip() or default_recording_dir
                self.on_start_recording_requested(record_dir)
                self._pending_auto_record = False
        else:
            self.ui.infoPanel.append(f"✗ Disconnected: {message}")

            # Hide playback controls
            self.playback_controls.hide_for_stream()

            # Notify algorithm
            if self.algorithm_widget:
                self.algorithm_widget.on_stream_disconnected()

            # Reset statistics
            self.stream_statistics.reset()

            # Clear pending resolution (will be reapplied on next connection if wizard runs again)
            self._pending_processing_resolution = None

    @Slot(np.ndarray, float)
    def on_frame_received(self, frame: np.ndarray, timestamp: float):
        """Handle frame received from stream."""
        # Record frame receipt in statistics
        self.stream_statistics.on_frame_received(timestamp)

        # Apply resolution capping on first frame (to prevent upscaling)
        if self._pending_processing_resolution is not None:
            # Get native video resolution from frame
            native_height, native_width = frame.shape[:2]
            desired_width, desired_height = self._pending_processing_resolution

            # Cap to native resolution (never upscale)
            capped_width = min(desired_width, native_width)
            capped_height = min(desired_height, native_height)

            # Only update if capping actually changed the resolution
            if capped_width < desired_width or capped_height < desired_height:
                # self.logger.info(
                #     f"Capping processing resolution from {desired_width}x{desired_height} "
                #     f"to {capped_width}x{capped_height} (native: {native_width}x{native_height})"
                # )
                pass

                # Update algorithm with capped resolution
                if self.algorithm_widget:
                    capped_config = {
                        'processing_width': capped_width,
                        'processing_height': capped_height,
                        'processing_resolution': (capped_width, capped_height)
                    }
                    self._apply_algorithm_options(capped_config)

            # Clear pending resolution (only apply once)
            self._pending_processing_resolution = None

        # Check if stream is paused (for file playback) - skip processing if paused
        is_paused = False
        if (self.stream_coordinator.stream_manager and
                hasattr(self.stream_coordinator.stream_manager, 'is_playing')):
            is_paused = not self.stream_coordinator.stream_manager.is_playing()

        # Process frame with algorithm if loaded and not paused
        if self.algorithm_widget and not is_paused:
            # Use worker thread if available, otherwise fall back to main thread
            use_worker = False
            # Check if worker is available, running, and not in the process of stopping
            if (self._processing_worker and self._processing_thread and
                    self._processing_thread.isRunning() and not self._is_stopping_worker):
                # Process frame in worker thread (non-blocking)
                # Emit signal to request processing in worker thread
                try:
                    self._processing_worker.processFrameRequested.emit(frame, timestamp)
                    use_worker = True
                except RuntimeError:
                    # Worker may have been deleted, fall back to main thread processing
                    use_worker = False

            if not use_worker:
                # Fallback to main thread processing (for compatibility)
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
        default_recording_dir = os.path.expanduser("~")
        output_dir = directory or default_recording_dir
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
        default_recording_dir = os.path.expanduser("~")
        output_dir = directory or default_recording_dir
        self.settings.setValue("recording/output_dir", output_dir)
        self.settings.sync()

    @Slot(bool)
    def on_recording_toggled(self, start: bool):
        """Handle recording toggle from algorithms."""
        if start:
            default_recording_dir = os.path.expanduser("~")
            directory = self.recording_dir_edit.text().strip() or default_recording_dir
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
        # Update performance section in stream controls
        stats_obj = self.stream_statistics.get_stats()
        perf_payload = {
            "fps": stats_obj.fps,
            "avg_fps": stats_obj.processing_fps,
            "current_processing_time_ms": stats_obj.avg_processing_time_ms,
            "avg_processing_time_ms": stats_obj.avg_processing_time_ms,
            "latency_ms": stats_obj.latency_ms,
            "total_frames": stats_obj.total_frames,
            "detection_count": stats_obj.detection_count,
            "dropped_frames": stats_obj.dropped_frames,
        }
        self.stream_controls.update_performance(perf_payload)

    def update_theme(self, theme: str):
        """
        Apply the requested theme to the streaming viewer.

        Args:
            theme: Theme name ('Light' or 'Dark')
        """
        normalized = (theme or "dark").lower()
        self.theme = normalized
        try:
            if normalized == "light":
                qdarktheme.setup_theme("light")
            else:
                qdarktheme.setup_theme("dark")
        except Exception as e:
            self.logger.error(f"Error applying theme: {e}")

    def showEvent(self, event):
        """Ensure the viewer launches maximized on first show."""
        super().showEvent(event)
        if not self._maximized_applied:
            self._maximized_applied = True
            self.showMaximized()

    def closeEvent(self, event):
        """Handle window close event."""
        # self.logger.info("Closing StreamViewerWindow")

        # Save current algorithm config before closing (though we'll clear it anyway)
        if self.algorithm_widget and self.current_algorithm_name:
            try:
                if hasattr(self.algorithm_widget, 'get_config'):
                    saved_config = self.algorithm_widget.get_config()
                    self._algorithm_configs[self.current_algorithm_name] = saved_config
            except Exception as e:
                self.logger.warning(f"Failed to save config on close: {e}")

        # Clear algorithm configs (forget settings on close)
        self._algorithm_configs.clear()

        # Cleanup
        self.update_timer.stop()

        # Cleanup processing worker thread
        self._cleanup_processing_worker()

        if self.algorithm_widget:
            self.algorithm_widget.cleanup()

        self.stream_coordinator.cleanup()

        event.accept()
