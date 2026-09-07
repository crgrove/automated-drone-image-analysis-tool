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
                               QFileDialog, QApplication, QDialog, QTabWidget, QSpinBox,
                               QSplitter, QCheckBox)
from PySide6.QtCore import Qt, QTimer, Slot, QSettings, QUrl, QThread, QObject, QEvent
from PySide6.QtGui import QAction, QDesktopServices
from typing import Optional, Dict, Any, List, Callable, Tuple
import numpy as np
import cv2
from types import SimpleNamespace
import time
import os
import sys
import pathlib
import platform

import qdarktheme
from core.controllers.Preferences import Preferences
from core.controllers.streaming.StreamingGuide import StreamingGuide
# MainWindow imported lazily in _open_image_analysis() to avoid circular dependency
from core.controllers.UpdateController import UpdateController
from core.services.SettingsService import SettingsService
from helpers import FeatureFlags
from helpers.ThemeHelper import apply_theme
from core.services.ConfigService import ConfigService
from core.views.streaming.StreamViewerWindow_ui import Ui_StreamViewerWindow
from core.services.LoggerService import LoggerService
from helpers import BuildInfo
from helpers.WidgetHelper import retire_widget
from core.controllers.streaming.components import StreamCoordinator, DetectionRenderer, StreamStatistics
from core.controllers.streaming.components import StreamTelemetryCoordinator
from core.controllers.streaming.components.FrameProcessingWorker import FrameProcessingWorker
from core.controllers.streaming.shared_widgets import DetectionThumbnailWidget, StreamControlWidget
from core.views.components.FlightMapView import FlightMapView
from core.views.flight.FlightPairingDialog import FlightPairingDialog
from core.views.flight.TelemetryHud import TelemetryHud
from core.services.streaming.FlightStreamService import ERROR_STATUS_PREFIX
from core.views.streaming.components import PlaybackControlBar, StreamingVideoDisplay
from core.views.streaming.components.TrackGalleryWidget import TrackGalleryWidget
from core.controllers.streaming.base import StreamAlgorithmController
from core.services.streaming.StreamAlgorithmService import StreamAlgorithmService
from core.services.streaming.StreamAnalyzeService import StreamAnalyzeService
from core.services.streaming.RTMPStreamService import (
    SOURCE_TYPE_FILE,
    SOURCE_TYPE_HDMI,
    StreamType,
    is_live_source,
    stream_type_from_source_label,
)
from core.services.streaming.contracts import FocusTarget
from core.services.streaming.RecordingSessionService import DetectionRecord
from helpers.TranslationMixin import TranslationMixin


class StreamViewerWindow(TranslationMixin, QMainWindow):
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
    _lingering_processing_threads: List[QThread] = []
    _MAX_ORIGINAL_FRAME_CACHE = 12
    # Safety net so a backend that never reports the sought frame position
    # cannot strand an armed gallery focus indefinitely.
    _FOCUS_TIMEOUT_MS = 1500

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
        self.update_controller = UpdateController(self, settings_service=self.settings_service)
        self.theme = theme
        self._maximized_applied = False
        # Store algorithm name - if None, will load default, if empty string, won't load
        self._initial_algorithm_name = algorithm_name if algorithm_name is not None else "ColorAnomalyAndMotionDetection"
        self._pending_auto_record = False
        self._pending_record_dir = None
        # Bundle directory of the last finished recording, for the panel's
        # "Open Recording Folder" button.
        self._last_recording_bundle: Optional[str] = None
        # The last finished recording's video, for the one-click Replay
        # button (which opens the dedicated ReplayWindow - this window
        # stays an analysis surface).
        self._last_recording_video: Optional[str] = None
        self._pending_algorithm_options = None
        self._pending_processing_resolution = None  # Desired resolution from wizard (to be capped to native)
        self._active_stream_fps_limit: Optional[int] = None
        # True once the active source has actually connected. Distinguishes a
        # real disconnect from the pre-connection progress reports that
        # WebRTC pairing and RTMP reconnect attempts emit as connected=False.
        self._connection_established = False

        # Setup UI
        self.ui = Ui_StreamViewerWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(
            self.tr(
                "Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR"
            ).format(version=BuildInfo.title_version(self.app_version))
        )

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
        # Normalizes file-derived and live telemetry into one stream so the
        # HUD and map have a single input regardless of source.
        self.telemetry_coordinator = StreamTelemetryCoordinator(logger=self.logger)
        self.detection_renderer = DetectionRenderer()
        self.stream_statistics = StreamStatistics()
        self.algorithm_renders_frame = False
        self._latest_detections_for_rendering: List[Dict] = []
        self._last_algorithm_frame: Optional[np.ndarray] = None
        self._original_frame_for_thumbnails: Optional[np.ndarray] = None  # Store original frame before detection rendering
        self._original_frames_queue: Dict[float, np.ndarray] = {}  # Queue of original frames indexed by timestamp for sync

        # Current algorithm
        self.algorithm_widget: Optional[StreamAlgorithmController] = None
        self.current_algorithm_name: Optional[str] = None

        # Store current frame timestamp for worker thread callback (video timestamp for seeking)
        self._current_frame_timestamp: float = 0.0

        # Store current video frame position (passed through signal chain, not read from stream manager)
        self._current_video_frame_pos: int = 0

        # Store track to highlight when seeking from gallery (cleared on play/next action)
        self._highlight_track = None

        # One-shot gallery zoom focus, applied only once the service reports the
        # sought frame via seekCompleted, correlated by both seek REQUEST ID and
        # the service's authoritative resolved frame window. Generation-tagged
        # so superseded selections and stale delayed callbacks are ignored.
        self._pending_focus_target: Optional[FocusTarget] = None
        self._pending_focus_seek_id: int = 0
        self._pending_focus_positions = set()
        self._focus_generation: int = 0
        self._pending_focus_generation: Optional[int] = None

        # Store algorithm configs for session persistence (forgotten on close)
        self._algorithm_configs: Dict[str, Dict[str, Any]] = {}

        # Map pin key -> gallery Track, so clicking a pin can select the
        # matching gallery entry.
        self._gallery_tracks_by_key: Dict[str, Any] = {}

        # ADIAT Flight pairing prompt, open only while pairing.
        self._pairing_dialog: Optional[FlightPairingDialog] = None
        self._pairing_code: Optional[str] = None

        # Frame processing worker thread (moves algorithm processing off main thread)
        self._processing_thread: Optional[QThread] = None
        self._processing_worker: Optional[FrameProcessingWorker] = None
        self._is_stopping_worker = False  # Flag to prevent new frames from being queued during cleanup
        self._worker_frame_in_flight = False
        self._pending_worker_frame: Optional[Tuple[np.ndarray, float, int]] = None

        # Stream-session generation: bumped on every connection change so a late
        # async worker result from a superseded session (disconnect/replacement
        # source) can be rejected instead of repainting a stale frame. The
        # session travels with each worker job (echoed in frameProcessed).
        self._frame_session: int = 0

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
        # Create tab widget for Live View and Gallery
        self.tab_widget = QTabWidget()

        # === Live View Tab ===
        live_view_widget = QWidget()
        live_layout = QVBoxLayout(live_view_widget)
        live_layout.setContentsMargins(0, 0, 0, 0)
        live_layout.setSpacing(0)

        # Video display (zoomable graphics view; owning window enables key/nav forwarding)
        self.video_display = StreamingVideoDisplay(self)
        self.video_display.playPauseRequested.connect(self.on_play_pause_toggled)
        # NB: the display resets its own zoom on a source-resolution change; the
        # window must NOT clear a pending gallery focus there, or a sought frame
        # that also changes resolution would lose its zoom. Focus is applied via
        # seekCompleted after the (reset) frame is shown.

        # Telemetry HUD, overlaid on the bottom of the video rather than
        # given its own row — the same treatment the Flight Viewer's tiles
        # use, so the two surfaces look identical and the map below keeps
        # the vertical space. Hidden until the first envelope arrives.
        self.telemetry_hud = TelemetryHud(self.video_display)
        self.telemetry_hud.move(0, 0)
        self.telemetry_hud.setVisible(False)
        # The display is a QGraphicsView that repaints on resize; keep the
        # overlay pinned to its bottom edge.
        self.video_display.installEventFilter(self)

        # The video keeps the whole left pane. The map lives in the right
        # column instead — the left pane is wide and short, which turns a
        # map into an unusable letterbox strip.
        live_layout.addWidget(self.video_display)

        # Playback controls
        self.playback_controls = PlaybackControlBar()
        live_layout.addWidget(self.playback_controls)

        # Thumbnail widget
        self.thumbnail_widget = DetectionThumbnailWidget()
        self.thumbnail_widget.thumbnail_focus_requested.connect(self._on_thumbnail_focus_requested)
        live_layout.addWidget(self.thumbnail_widget)

        # Add Live View tab
        self.tab_widget.addTab(live_view_widget, self.tr("Live View"))

        # === Gallery Tab ===
        self.gallery_widget = TrackGalleryWidget()
        self.gallery_widget.track_clicked.connect(self._on_gallery_track_clicked)
        self.tab_widget.addTab(self.gallery_widget, self.tr("Gallery"))

        # Connect track_confirmed signal from tracker to gallery
        self.thumbnail_widget.tracker.track_confirmed.connect(self.gallery_widget.add_track)
        # ...and pin it on the map at the aircraft's position for that frame.
        self.thumbnail_widget.tracker.track_confirmed.connect(self._on_track_confirmed_for_map)
        self.thumbnail_widget.tracker.track_confirmed.connect(
            self._on_track_confirmed_for_recording
        )

        # Replace the placeholder widgets with the tab widget
        # Get the left panel layout and replace videoLabel with tab widget
        left_panel = self.ui.splitter.widget(0)
        left_layout = left_panel.layout()

        # Remove the old placeholder widgets
        left_layout.replaceWidget(self.ui.videoLabel, self.tab_widget)
        self.ui.videoLabel.deleteLater()

        # Remove playback controls placeholder (now in tab)
        left_layout.removeWidget(self.ui.playbackControlWidget)
        self.ui.playbackControlWidget.deleteLater()

        # Remove thumbnail widget placeholder (now in tab)
        left_layout.removeWidget(self.ui.thumbnailWidget)
        self.ui.thumbnailWidget.deleteLater()

        # Stream controls (without recording)
        self.stream_controls = StreamControlWidget(include_recording=False)
        self.ui.streamControlPlaceholder.parent().layout().replaceWidget(
            self.ui.streamControlPlaceholder, self.stream_controls
        )
        self.ui.streamControlPlaceholder.deleteLater()

        # Map, in its own collapsible section between the stream and
        # algorithm controls.
        self.map_view = FlightMapView()
        self.map_view.pinClicked.connect(self._on_map_pin_clicked)
        self.map_view.setMinimumHeight(280)
        self.ui.mapPlaceholder.parent().layout().replaceWidget(
            self.ui.mapPlaceholder, self.map_view
        )
        self.ui.mapPlaceholder.deleteLater()
        self._restore_section_states()
        self.ui.streamControlGroup.collapsedChanged.connect(
            lambda collapsed: self._save_section_state("stream_controls", collapsed)
        )
        self.ui.mapGroup.collapsedChanged.connect(
            lambda collapsed: self._save_section_state("map", collapsed)
        )

        # Setup recording widget in its own section
        self._setup_recording_widget()

        # Add algorithm selection to Algorithm Controls section
        self._setup_algorithm_selection()

    def setup_menus(self):
        """Create top-level menus for navigation and help."""
        menu_bar = self.menuBar()
        menu_bar.clear()

        # Primary navigation menu
        primary_menu = menu_bar.addMenu(self.tr("Menu"))
        self.action_open_recording = QAction(self.tr("Open Recording…"), self)
        self.action_streaming_guide = QAction(self.tr("Streaming Analysis Wizard"), self)
        self.action_image_analysis = QAction(self.tr("Image Analysis"), self)
        self.action_flight_viewer = QAction(self.tr("Flight Viewer"), self)
        self.action_preferences = QAction(self.tr("Preferences"), self)
        primary_menu.addAction(self.action_open_recording)
        primary_menu.addAction(self.action_streaming_guide)
        primary_menu.addSeparator()
        primary_menu.addAction(self.action_image_analysis)
        if FeatureFlags.FLIGHT_VIEWER_ENABLED:
            # Flight Viewer is deferred to a later release
            primary_menu.addAction(self.action_flight_viewer)
        primary_menu.addAction(self.action_preferences)

        # Help menu
        help_menu = menu_bar.addMenu(self.tr("Help"))
        self.action_check_for_updates = QAction(self.tr("Check for Updates"), self)
        self.action_manual = QAction(self.tr("Manual"), self)
        self.action_community = QAction(self.tr("Community Forum"), self)
        self.action_youtube = QAction(self.tr("YouTube Channel"), self)
        help_menu.addAction(self.action_check_for_updates)
        help_menu.addSeparator()
        help_menu.addAction(self.action_manual)
        help_menu.addAction(self.action_community)
        help_menu.addAction(self.action_youtube)

        # Wire actions
        self.action_open_recording.triggered.connect(self._open_recordings_dialog)
        self.action_streaming_guide.triggered.connect(self._open_streaming_guide)
        self.action_image_analysis.triggered.connect(self._open_image_analysis)
        self.action_flight_viewer.triggered.connect(self._open_flight_viewer)
        self.action_preferences.triggered.connect(self._open_preferences)
        self.update_controller.bind_action(self.action_check_for_updates)
        self.action_manual.triggered.connect(self._open_manual)
        self.action_community.triggered.connect(self._open_community_forum)
        self.action_youtube.triggered.connect(self._open_youtube_channel)

    def _setup_recording_widget(self):
        """Setup recording widget in its own section between Algorithm Controls and the bottom of the panel."""
        # Create recording widget
        recording_widget = QWidget()
        recording_layout = QVBoxLayout(recording_widget)
        recording_layout.setContentsMargins(5, 5, 5, 5)
        recording_layout.setSpacing(5)

        # The record toggle lives INLINE with the play button (see
        # PlaybackControlBar) - recording acts on the video, so its
        # trigger sits with the video. The panel keeps everything about
        # where and what to save.

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

        # Recording directory selector
        dir_layout = QHBoxLayout()
        dir_label = QLabel(self.tr("Save to:"))
        default_recording_dir = os.path.expanduser("~")
        self.recording_dir_edit = QLineEdit(default_recording_dir)
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

        # What gets saved beside the video. A recording is a folder, not a
        # bare file: these decide whether the detections the operator was
        # watching, and the flight the aircraft flew, are kept with it.
        self.save_detections_check = QCheckBox(self.tr("Save detections"))
        self.save_detections_check.setToolTip(
            self.tr(
                "Save each confirmed detection with the recording: a thumbnail, its "
                "position, and a results file that opens in the Image Analysis window."
            )
        )
        self.save_map_check = QCheckBox(self.tr("Save flight map"))
        self.save_map_check.setToolTip(
            self.tr(
                "Save the flight path and detection locations as a map and a KML file. "
                "Requires location data from the video or a live ADIAT Flight feed."
            )
        )

        # Shown once a recording has been saved: watch it, or get to the
        # files. Replay opens the dedicated ReplayWindow - watching a
        # recording is its own experience, not an analysis session.
        self.replay_recording_btn = QPushButton(self.tr("Replay"))
        self.replay_recording_btn.setVisible(False)
        self.replay_recording_btn.setToolTip(
            self.tr("Watch this recording: video, detections, telemetry and map.")
        )
        self.open_recording_btn = QPushButton(self.tr("Open Recording Folder"))
        self.open_recording_btn.setVisible(False)
        self.open_recording_btn.setToolTip(
            self.tr("Open the folder holding the last recording and its detections.")
        )

        recording_layout.addWidget(self.recording_status)
        recording_layout.addWidget(self.recording_info)
        recording_layout.addLayout(dir_layout)
        recording_layout.addWidget(self.save_detections_check)
        recording_layout.addWidget(self.save_map_check)
        recording_layout.addWidget(self.replay_recording_btn)
        recording_layout.addWidget(self.open_recording_btn)

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

        # Both default on: an operator who records a search flight almost
        # always wants the record of what was found with it. Restoring is not
        # a user action, so the writes-back stay blocked for it.
        for check, key in (
            (self.save_detections_check, "recording/save_detections"),
            (self.save_map_check, "recording/save_map"),
        ):
            was_blocked = check.blockSignals(True)
            check.setChecked(self._settings_bool(key, True))
            check.blockSignals(was_blocked)
        self._update_map_option_hint()

        # Connect signals
        self.playback_controls.record_btn.clicked.connect(self._on_record_toggle_clicked)
        self.recording_dir_browse.clicked.connect(self._browse_recording_directory)
        self.recording_dir_edit.textChanged.connect(self._on_recording_directory_changed)
        self.save_detections_check.toggled.connect(
            lambda checked: self.settings.setValue("recording/save_detections", checked)
        )
        self.save_map_check.toggled.connect(
            lambda checked: self.settings.setValue("recording/save_map", checked)
        )
        self.open_recording_btn.clicked.connect(self._open_last_recording_folder)
        self.replay_recording_btn.clicked.connect(self._replay_last_recording)

    def _settings_bool(self, key: str, default: bool) -> bool:
        """Read a boolean setting. QSettings returns strings on some platforms."""
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes")
        return bool(value)

    def _update_map_option_hint(self) -> None:
        """Say, in the flight-map option's tooltip, whether location data is here.

        The option stays enabled whatever the source is doing. It is a
        standing preference, not a live capability: a live ADIAT Flight feed
        only counts as "available" once its first telemetry envelope lands,
        so disabling the option - or reading its enabled state at recording
        start - would silently drop the whole flight of a recording that
        began a moment before that envelope arrived.

        Whether a map is actually produced is decided at the end, from the
        fixes that were captured (see
        :func:`~core.services.streaming.RecordingBundleService.\
finalize_bundle`).
        """
        if not hasattr(self, "save_map_check"):
            return
        if self.telemetry_coordinator.is_available:
            self.save_map_check.setToolTip(
                self.tr(
                    "Save the flight path and detection locations as a map and a KML file. "
                    "Location data is available for this source."
                )
            )
        else:
            self.save_map_check.setToolTip(
                self.tr(
                    "Save the flight path and detection locations as a map and a KML file. "
                    "Nothing is saved unless location data arrives while recording."
                )
            )

    def _open_last_recording_folder(self) -> None:
        """Reveal the last saved recording bundle in the file manager."""
        folder = getattr(self, "_last_recording_bundle", None)
        if folder and os.path.isdir(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _replay_last_recording(self) -> None:
        """Watch the recording that just finished, in the Replay window."""
        video = getattr(self, "_last_recording_video", None)
        if video and os.path.isfile(video):
            self._open_replay_window(video)

    def _open_recordings_dialog(self) -> None:
        """Pick any known recording and replay it."""
        from core.services.streaming.RecordingLibrary import RecordingLibrary
        from core.views.streaming.RecordingsDialog import RecordingsDialog

        dialog = RecordingsDialog(RecordingLibrary().recent(), parent=self)
        if dialog.exec() == QDialog.Accepted and dialog.selected_video:
            self._open_replay_window(dialog.selected_video)

    def _open_replay_window(self, video_path: str) -> None:
        """Hand a recording to the dedicated Replay window."""
        try:
            # Lazy import; the replay window composes streaming components.
            from core.controllers.streaming.ReplayWindow import open_replay
            open_replay(video_path)
        except Exception as exc:  # noqa: BLE001 - never take this window down
            self.logger.error(f"Could not open replay: {exc}")
            self.ui.infoPanel.append(
                self.tr("Could not open replay: {error}").format(error=exc)
            )

    def _on_record_toggle_clicked(self):
        """One button, two meanings: start when idle, stop when recording."""
        self.on_recording_toggled(not self.stream_coordinator.is_recording)

    def _browse_recording_directory(self):
        """Browse for recording directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Recording Directory"),
            self.recording_dir_edit.text()
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

        algorithm_label = QLabel(self.tr("Algorithm:"))
        algorithm_label.setToolTip(
            self.tr("Select which streaming detection algorithm to use")
        )

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setToolTip(
            self.tr(
                "Choose which streaming detection algorithm to run.\n"
                "• Color Anomaly & Motion Detection: fused anomaly detectors\n"
                "• Color Detection: color-based highlighting"
            )
        )

        # Populate with available algorithms from shared registry
        registry = self._algorithm_registry()
        algorithm_options = [
            (self.tr(cfg.get("label", key)), key)
            for key, cfg in registry.items()
        ]

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

        # === Gallery Settings ===
        gallery_layout = QHBoxLayout()
        gallery_layout.setContentsMargins(0, 0, 0, 10)

        confirm_label = QLabel(self.tr("Gallery Threshold:"))
        confirm_label.setToolTip(
            self.tr(
                "Number of frames a detection must be seen before appearing in the Gallery tab"
            )
        )

        self.confirmation_spinbox = QSpinBox()
        self.confirmation_spinbox.setRange(1, 30)
        self.confirmation_spinbox.setValue(5)
        self.confirmation_spinbox.setSuffix(self.tr(" frames"))
        self.confirmation_spinbox.setToolTip(
            self.tr(
                "Detections must be seen for this many consecutive frames\n"
                "before appearing in the Gallery. Higher values reduce\n"
                "false positives but delay detection appearance."
            )
        )
        self.confirmation_spinbox.valueChanged.connect(self._on_confirmation_threshold_changed)

        gallery_layout.addWidget(confirm_label)
        gallery_layout.addWidget(self.confirmation_spinbox)
        gallery_layout.addStretch()

        # Insert after algorithm layout
        self.ui.algorithmControlLayout.insertLayout(1, gallery_layout)

    def connect_signals(self):
        """Connect signals between components."""
        # Stream coordinator signals
        self.stream_coordinator.connectionChanged.connect(self.on_connection_changed)
        self.stream_coordinator.frameReceived.connect(self.on_frame_received)
        self.stream_coordinator.recordingStateChanged.connect(self.on_recording_state_changed)
        self.stream_coordinator.recordingStatsUpdated.connect(self.on_recording_stats_updated)
        self.stream_coordinator.recordingBundleReady.connect(self.on_recording_bundle_ready)
        self.stream_coordinator.errorOccurred.connect(self.on_error)
        self.stream_coordinator.streamInfoUpdated.connect(self.on_stream_info_updated)
        self.stream_coordinator.seekCompleted.connect(self._on_seek_completed)
        # Live telemetry (ADIAT Flight) reaches the shared coordinator, which
        # DEM-corrects it and re-emits alongside file-derived telemetry.
        self.stream_coordinator.telemetryReceived.connect(
            self.telemetry_coordinator.on_live_telemetry
        )

        # Telemetry -> HUD + map
        self.telemetry_coordinator.telemetryUpdated.connect(self.on_telemetry_updated)
        self.telemetry_coordinator.trackUpdated.connect(self._on_flight_path_updated)
        self.telemetry_coordinator.telemetryStatus.connect(self._on_telemetry_status)
        # A source with no location data cannot produce a flight map, so the
        # option follows availability rather than being offered and ignored.
        self.telemetry_coordinator.availabilityChanged.connect(
            self._on_telemetry_availability_changed
        )

        # Stream controls signals
        self.stream_controls.connectRequested.connect(self.on_connect_requested)
        self.stream_controls.pairingRequested.connect(self.open_flight_pairing_dialog)
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
            # Match on the combo's stable itemData, not its display text —
            # the visible labels are translated (CLAUDE.md §2.8). findText is
            # kept as a fallback for any combo built without itemData.
            idx = self.stream_controls.type_combo.findData(stream_type)
            if idx < 0:
                idx = self.stream_controls.type_combo.findText(stream_type)
            if idx >= 0:
                self.stream_controls.type_combo.setCurrentIndex(idx)

        stream_url = wizard_data.get("stream_url")
        if stream_url:
            # For HDMI Capture, set the device combo instead of URL input
            if stream_type == SOURCE_TYPE_HDMI:
                # The stream_url is the device index as a string (e.g., "1")
                try:
                    device_index = int(stream_url)
                    hdmi_backend = wizard_data.get("hdmi_backend")

                    # Clear placeholder and add the device from wizard
                    self.stream_controls.hdmi_device_combo.clear()

                    # Use friendly name from wizard if available, otherwise generic
                    device_label = wizard_data.get("device_label", self.tr("Device {index}").format(index=device_index))
                    if hdmi_backend is not None:
                        # Add backend name to label if we have it
                        backend_names = {1400: "MSMF", 700: "DirectShow", 0: "Auto"}
                        backend_name = backend_names.get(hdmi_backend, "")
                        if backend_name and f"({backend_name})" not in device_label:
                            device_label = f"{device_label} ({backend_name})"

                    self.stream_controls.hdmi_device_combo.addItem(device_label, device_index)
                    self.stream_controls.hdmi_device_combo.setCurrentIndex(0)
                    self.stream_controls.hdmi_device_combo.setEnabled(True)

                    # Store the backend
                    if hdmi_backend is not None:
                        if not hasattr(self.stream_controls, '_device_backends'):
                            self.stream_controls._device_backends = {}
                        self.stream_controls._device_backends[0] = hdmi_backend
                except (ValueError, TypeError):
                    pass
            else:
                self.stream_controls.url_input.setText(stream_url)

        # Carry the wizard's metadata-file choice into the controls, which
        # are the single source of truth for it at connect time (including
        # the auto-connect below).
        metadata_path = wizard_data.get("metadata_path")
        if metadata_path and stream_type == SOURCE_TYPE_FILE:
            self.stream_controls.set_metadata_path(metadata_path)

        default_recording_dir = os.path.expanduser("~")
        recording_dir = wizard_data.get("recording_dir") or default_recording_dir
        if hasattr(self, "recording_dir_edit"):
            self.recording_dir_edit.setText(recording_dir)
        self.settings.setValue("recording/output_dir", recording_dir)
        self.settings.sync()

        algorithm = wizard_data.get("algorithm")
        algorithm_options = dict(wizard_data.get("algorithm_options") or {})
        # Thread the source type to the algorithm controller so it can pick a
        # usecase-appropriate model (the AI person detector auto-selects the 1024 model
        # for file sources and keeps the 640 model for live feeds).
        if stream_type:
            algorithm_options["stream_type"] = stream_type

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

        if wizard_data.get("auto_connect"):
            # Resolve from the combo's stable itemData so a translated UI
            # still auto-connects to the source the operator picked.
            source_label = (
                self.stream_controls.type_combo.currentData()
                or self.stream_controls.type_combo.currentText()
            )
            selected_type = stream_type_from_source_label(source_label)
            if selected_type == StreamType.WEBRTC:
                # No code was collected in the wizard (they expire in ~30 s),
                # so auto-connect means "prompt for one now" rather than
                # "connect to a code chosen minutes ago".
                self.open_flight_pairing_dialog()
            elif stream_url:
                # Extract hdmi_backend if specified in wizard data
                hdmi_backend = wizard_data.get("hdmi_backend")
                self.on_connect_requested(
                    stream_url, selected_type, hdmi_backend=hdmi_backend
                )

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

    def _apply_stream_resolution_to_mask_controls(self, resolution: Optional[Tuple[int, int]]):
        """Propagate active stream resolution to algorithm frame mask controls."""
        if not self.algorithm_widget or not resolution:
            return

        width, height = resolution
        if width <= 0 or height <= 0:
            return

        frame_tab = None
        if hasattr(self.algorithm_widget, 'control_widget'):
            frame_tab = getattr(self.algorithm_widget.control_widget, 'frame_tab', None)
        elif hasattr(self.algorithm_widget, 'integrated_controls'):
            frame_tab = getattr(self.algorithm_widget.integrated_controls, 'frame_tab', None)

        if frame_tab and hasattr(frame_tab, 'set_video_resolution'):
            frame_tab.set_video_resolution(width, height)

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
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open Streaming Analysis Guide:\n{error}").format(error=str(e))
            )

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
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open Image Analysis:\n{error}").format(error=str(e))
            )

    def _open_preferences(self):
        """Open the Preferences dialog."""
        try:
            pref = Preferences(self)
            pref.exec()
            self.update_controller.refresh_action_state()
        except Exception as e:
            self.logger.error(f"Error opening Preferences: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open Preferences:\n{error}").format(error=str(e))
            )

    def _open_flight_viewer(self):
        """Open the Flight Viewer alongside this streaming window."""
        try:
            from core.controllers.flight import FlightViewerController

            app = QApplication.instance()
            existing = getattr(app, '_flight_controller', None) if app else None
            if existing is not None and existing.window.isVisible():
                existing.show()
                return

            controller = FlightViewerController()
            if app is not None:
                app._flight_controller = controller
            controller.show()
        except Exception as e:
            self.logger.error(f"Error opening Flight Viewer: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open Flight Viewer:\n{error}").format(error=str(e))
            )

    def _open_manual(self):
        """Open the user manual in the default browser."""
        try:
            url = QUrl("https://www.texsar.org/automated-drone-image-analysis-tool/")
            QDesktopServices.openUrl(url)
            # self.logger.info("Help documentation opened")
        except Exception as e:
            self.logger.error(f"Error opening Help URL: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open Help documentation:\n{error}").format(error=str(e))
            )

    def _open_community_forum(self):
        """Open the community forum link in the default browser."""
        try:
            url = QUrl("https://discord.com/invite/aY9tY7JSPu")
            QDesktopServices.openUrl(url)
            # self.logger.info("Community forum opened")
        except Exception as e:
            self.logger.error(f"Error opening Community Forum URL: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open Community Forum:\n{error}").format(error=str(e))
            )

    def _open_youtube_channel(self):
        """Open the YouTube Channel URL in the default browser."""
        try:
            url = QUrl("https://www.youtube.com/@adiat-u4f")
            QDesktopServices.openUrl(url)
            # self.logger.info("YouTube Channel opened")
        except Exception as e:
            self.logger.error(f"Error opening YouTube Channel URL: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open YouTube Channel:\n{error}").format(error=str(e))
            )

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
                try:
                    self.algorithm_widget.configChanged.disconnect(self.on_algorithm_config_changed)
                except Exception:
                    pass
                try:
                    self.algorithm_widget.cleanup()
                except Exception as e:
                    self.logger.warning(f"Algorithm cleanup failed for {self.current_algorithm_name}: {e}")
                retire_widget(self.algorithm_widget, self.ui.algorithmControlLayout)
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
            self.algorithm_widget.configChanged.connect(self.on_algorithm_config_changed)
            self.algorithm_widget.statusUpdate.connect(self.on_status_update)
            self.algorithm_widget.requestRecording.connect(self.on_recording_request)

            # Setup frame processing worker thread (moves heavy computation off main thread)
            self._setup_processing_worker()

            # self.logger.info(f"Algorithm loaded: {algorithm_name}")
            self.ui.statusbar.showMessage(
                self.tr("Loaded: {algorithm}").format(algorithm=algorithm_name)
            )

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
            error_msg = self.tr("Error loading algorithm: {error}").format(error=str(e))
            self.logger.error(error_msg)
            QMessageBox.critical(
                self,
                self.tr("Algorithm Load Error"),
                error_msg
            )

    def _get_algorithm_service(self) -> Optional[QObject]:
        """
        Get the algorithm service object that can be moved to a worker thread.

        Returns:
            The service QObject, or None if not available
        """
        if not self.algorithm_widget:
            return None

        if hasattr(self.algorithm_widget, "get_stream_service"):
            try:
                service = self.algorithm_widget.get_stream_service()
                if service is not None:
                    return service
            except Exception as exc:
                self.logger.warning(f"Failed to get stream service from controller: {exc}")

        self.logger.warning("Algorithm widget does not provide a stream service")
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
        if not isinstance(service, StreamAlgorithmService):
            self.logger.warning(
                f"Stream service does not implement StreamAlgorithmService: {type(service)}"
            )
            return None

        analyzer = StreamAnalyzeService(service, self.logger)

        def process_normalized(frame: np.ndarray, timestamp: float):
            result = analyzer.process_frame(frame, timestamp)

            try:
                annotated_frame = result.rendered_frame
                if annotated_frame is not None and annotated_frame is not frame:
                    np.copyto(frame, annotated_frame)
            except Exception:
                pass

            return analyzer.to_worker_output(result)

        return process_normalized

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
            self._worker_frame_in_flight = False
            self._pending_worker_frame = None

            # self.logger.info("Frame processing worker thread started")

        except Exception as e:
            self.logger.error(f"Failed to setup processing worker: {e}")
            self._cleanup_processing_worker()

    def _cleanup_processing_worker(self):
        """Clean up the frame processing worker thread."""
        # Guard against re-entrant calls (can happen during shutdown)
        if self._is_stopping_worker:
            return

        # Set flag early to prevent new frames from being queued and re-entry
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
        thread_stopped = True
        if self._processing_thread:
            if self._processing_thread.isRunning():
                self._processing_thread.quit()
                if not self._processing_thread.wait(3000):
                    # Retry once more before giving up; avoid terminate() to keep shutdown graceful.
                    self.logger.warning("Processing thread did not stop within 3s, retrying graceful quit")
                    self._processing_thread.quit()
                    thread_stopped = self._processing_thread.wait(3000)
                    if not thread_stopped:
                        self.logger.error("Processing thread still running after graceful shutdown timeout")
            # Thread will delete itself via deleteLater() connected to finished signal
            if thread_stopped:
                self._processing_thread = None
            else:
                lingering_thread = self._processing_thread

                def _release_lingering_thread():
                    try:
                        StreamViewerWindow._lingering_processing_threads.remove(lingering_thread)
                    except ValueError:
                        pass
                    lingering_thread.deleteLater()

                StreamViewerWindow._lingering_processing_threads.append(lingering_thread)
                lingering_thread.finished.connect(_release_lingering_thread, Qt.QueuedConnection)
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

        # Move service back to main thread after thread is stopped.
        if thread_stopped:
            service = self._get_algorithm_service()
            if service:
                try:
                    # Move service back to main thread (must use actual thread, not None)
                    # Note: moveToThread(None) dissociates object from thread which causes crashes
                    main_thread = QThread.currentThread()  # This runs on main thread
                    service.moveToThread(main_thread)
                except RuntimeError:
                    # Service may already be deleted or moved, ignore
                    pass

        # Clear worker reference (worker will be deleted when thread is deleted)
        self._processing_worker = None
        self._worker_frame_in_flight = False
        if self._pending_worker_frame is not None:
            _, dropped_timestamp, _ = self._pending_worker_frame
            self._discard_original_frame(dropped_timestamp)
        self._pending_worker_frame = None
        self._is_stopping_worker = False  # Reset flag after cleanup

    def _discard_original_frame(self, timestamp: float):
        """Remove a frame from the original-frame queue if present."""
        if timestamp in self._original_frames_queue:
            del self._original_frames_queue[timestamp]

    def _queue_worker_frame(self, frame: np.ndarray, timestamp: float, video_frame_pos: int) -> bool:
        """
        Queue a frame for worker processing with bounded backpressure.

        Uses a single in-flight frame and one pending latest frame to avoid
        unbounded queued work under high input rates.
        """
        if not (self._processing_worker and self._processing_thread and self._processing_thread.isRunning()):
            return False

        if self._worker_frame_in_flight:
            if self._pending_worker_frame is not None:
                _, dropped_timestamp, _ = self._pending_worker_frame
                self._discard_original_frame(dropped_timestamp)
                self.stream_statistics.on_frame_dropped()
            self._pending_worker_frame = (frame, timestamp, video_frame_pos)
            return True

        try:
            self._processing_worker.processFrameRequested.emit(frame, timestamp, video_frame_pos, self._frame_session)
            self._worker_frame_in_flight = True
            return True
        except RuntimeError:
            return False

    def _dispatch_pending_worker_frame(self):
        """Dispatch pending latest frame to worker if available."""
        if self._pending_worker_frame is None:
            self._worker_frame_in_flight = False
            return

        if not (self._processing_worker and self._processing_thread and self._processing_thread.isRunning()):
            _, dropped_timestamp, _ = self._pending_worker_frame
            self._discard_original_frame(dropped_timestamp)
            self.stream_statistics.on_frame_dropped()
            self._pending_worker_frame = None
            self._worker_frame_in_flight = False
            return

        frame, timestamp, video_frame_pos = self._pending_worker_frame
        self._pending_worker_frame = None
        try:
            self._processing_worker.processFrameRequested.emit(frame, timestamp, video_frame_pos, self._frame_session)
            self._worker_frame_in_flight = True
        except RuntimeError:
            self._discard_original_frame(timestamp)
            self.stream_statistics.on_frame_dropped()
            self._worker_frame_in_flight = False

    @staticmethod
    def _detections_to_thumbnail_objects(detections: List[Dict]) -> List[SimpleNamespace]:
        """Convert detection dictionaries to object form required by thumbnail tracker."""
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

        return detection_objects

    @staticmethod
    def _get_resolution_metadata(detection_objects: List[SimpleNamespace]) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """Extract processing/original resolution metadata from detections."""
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

        return processing_resolution, original_resolution

    def _update_thumbnails(
            self,
            frame: np.ndarray,
            detections: List[Dict],
            timestamp: float,
            frame_index: int):
        """Update thumbnails for a processed frame."""
        detection_objects = self._detections_to_thumbnail_objects(detections or [])
        processing_resolution, original_resolution = self._get_resolution_metadata(detection_objects)

        thumbnail_frame = self._original_frames_queue.get(timestamp, frame)
        self._discard_original_frame(timestamp)

        self.thumbnail_widget.update_thumbnails(
            thumbnail_frame,
            detection_objects,
            processing_resolution=processing_resolution,
            original_resolution=original_resolution,
            frame_index=frame_index,
            timestamp=timestamp
        )

    @Slot(np.ndarray, list, float, float, bool, int, int)
    def _on_worker_frame_processed(
            self,
            frame: np.ndarray,
            detections: List[Dict],
            timestamp: float,
            processing_time_ms: float,
            was_skipped: bool = False,
            video_frame_pos: int = 0,
            session: int = 0):
        """Handle frame processed by worker thread."""
        # This runs on main thread (via QueuedConnection)
        self._worker_frame_in_flight = False
        try:
            # Reject results from a superseded stream session (disconnect /
            # replacement source) so a late queued callback cannot repaint a
            # stale frame over the placeholder or into a new source. The session
            # travels WITH the job (echoed by the worker), so per-job identity
            # is preserved even when newer jobs are dispatched meanwhile.
            if session != self._frame_session:
                self._discard_original_frame(timestamp)
                return

            self.stream_statistics.on_frame_processed(processing_time_ms, len(detections), was_skipped=was_skipped)
            self._latest_detections_for_rendering = detections

            rendered_frame = frame
            if not self.algorithm_renders_frame:
                # Render detections using the shared renderer (on main thread)
                rendered_frame = self.detection_renderer.render(frame, detections, copy_frame=False)
            # else: Frame already carries algorithm-rendered overlays.

            # Draw highlight box if a gallery track is selected
            if self._highlight_track is not None:
                rendered_frame = self._draw_gallery_highlight(rendered_frame)

            # Update display with rendered frame (applies any pending focus).
            presented = self._present_frame(rendered_frame, video_frame_pos, 'worker')

            if presented:
                # Gate presentation-coupled side effects: a frame rejected while
                # paused must not update thumbnails/recording (which would leave
                # thumbnails - and thumbnail zoom targets - representing a frame
                # the user is not viewing).
                self._update_thumbnails(frame, detections, timestamp, video_frame_pos)

                # Record exactly what is displayed.
                if self.stream_coordinator.is_recording:
                    self.stream_coordinator.record_frame(
                        rendered_frame, detections,
                        self._video_time_for_frame(video_frame_pos),
                    )
            else:
                self._discard_original_frame(timestamp)

            # Emit detections via controller (for compatibility with existing signal connections)
            if self.algorithm_widget:
                # Emit signal directly (we're already on main thread)
                self.algorithm_widget.detectionsReady.emit(detections)
        finally:
            self._dispatch_pending_worker_frame()

    @Slot(str)
    def _on_worker_error(self, error_msg: str):
        """Handle error from worker thread."""
        self.logger.error(f"Worker thread error: {error_msg}")
        self._worker_frame_in_flight = False
        self._dispatch_pending_worker_frame()

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
        """Return available streaming algorithms loaded from algorithms.conf."""
        config_path = self._get_algorithms_config_path()
        config_service = ConfigService(config_path)
        configured_algorithms = config_service.get_streaming_algorithms()

        system = platform.system()
        registry: Dict[str, Dict[str, Any]] = {}
        for algorithm in configured_algorithms:
            name = algorithm.get('name')
            controller = algorithm.get('controller')
            if not name or not controller:
                continue

            platforms = algorithm.get('platforms') or []
            if platforms and system not in platforms:
                continue

            module_name = algorithm.get('module') or f'algorithms.streaming.{name}.controllers.{controller}'
            registry[name] = {
                'label': algorithm.get('label', name),
                'controller': controller,
                'module': module_name
            }

        return registry

    def _get_algorithms_config_path(self) -> str:
        """Return the path to algorithms.conf for source and frozen builds."""
        if getattr(sys, 'frozen', False):
            app_root = sys._MEIPASS
        else:
            app_root = str(pathlib.Path(__file__).resolve().parents[3])
        return os.path.join(app_root, 'algorithms.conf')

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

    def _on_confirmation_threshold_changed(self, value: int):
        """Handle gallery confirmation threshold change.

        Args:
            value: Number of frames required before detection appears in gallery
        """
        if hasattr(self, 'thumbnail_widget'):
            self.thumbnail_widget.tracker.set_confirmation_threshold(value)
            self.logger.info(f"Gallery confirmation threshold set to {value} frames")

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
                self._apply_stream_resolution_to_mask_controls(resolution)
            except Exception as e:
                self.logger.error(f"Error notifying algorithm of active stream: {e}")
        config = self._get_algorithm_config(algorithm_name) or {}
        label = config.get("label", algorithm_name)
        self.ui.infoPanel.append(
            self.tr("Algorithm switched to {label}").format(label=label)
        )

    @Slot(str, object, object)
    def on_connect_requested(self, url: str, stream_type: StreamType,
                             hdmi_backend: Optional[int] = None):
        """Handle stream connection request."""
        fps_limit = self._get_target_fps_limit_from_widget()
        self._active_stream_fps_limit = fps_limit
        # Clear the previous source's HUD/map before the new one attaches.
        self._reset_telemetry_surfaces()
        connected = self.stream_coordinator.connect_stream(
            url,
            stream_type,
            hdmi_backend=hdmi_backend,
            fps_limit=fps_limit
        )
        if not connected:
            self._active_stream_fps_limit = None
            return

        # Load location data for the new source. For files this uses the
        # metadata file the operator selected, else a sidecar SRT, else the
        # track embedded in the video; live sources become available on
        # their first envelope.
        try:
            self.telemetry_coordinator.begin_source(
                url, stream_type, self._selected_metadata_path()
            )
        except Exception as e:
            self.logger.error(f"Error initializing telemetry for source: {e}")

        # A paused video is not a dropped feed, so the "stale Ns" badge only
        # applies to live sources.
        self.telemetry_hud.set_staleness_tracking(stream_type != StreamType.FILE)

    def _selected_metadata_path(self) -> str:
        """The metadata file chosen in the controls, if any.

        The controls own this value rather than it riding on
        ``connectRequested``: the signal is also emitted by the wizard's
        auto-connect path and by the pairing prompt, and widening it would
        make every caller responsible for a field only one source uses.
        Non-string results (a stubbed widget in tests) degrade to "".
        """
        try:
            value = self.stream_controls.get_metadata_path()
        except Exception:  # noqa: BLE001 - telemetry is never load-bearing
            return ""
        return value.strip() if isinstance(value, str) else ""

    @Slot()
    def open_flight_pairing_dialog(self):
        """Prompt for an ADIAT Flight pairing code and connect immediately.

        The code is deliberately *not* collected in the setup wizard: the
        signaling Worker evicts a session after 30 s of inactivity, and a
        pass through the wizard takes far longer than that, so a code
        entered up-front would routinely be dead by the time it was used.
        Prompting here puts a couple of seconds between the operator
        reading the code off the tablet and the handshake.

        Reuses the Flight Viewer's :class:`FlightPairingDialog` so both
        surfaces show the same negotiating/failed states.
        """
        if self._pairing_dialog is not None:
            self._pairing_dialog.raise_()
            self._pairing_dialog.activateWindow()
            return

        dialog = FlightPairingDialog(self)
        dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        dialog.codeSubmitted.connect(self._on_pairing_code_submitted)
        dialog.cancelled.connect(self._on_pairing_cancelled)
        dialog.destroyed.connect(self._on_pairing_dialog_destroyed)
        self._pairing_dialog = dialog
        dialog.show()

    def _on_pairing_code_submitted(self, code: str):
        """Start the handshake for a submitted code."""
        self._pairing_code = code
        if self._pairing_dialog is not None:
            self._pairing_dialog.show_negotiating(
                self.tr("Connecting to {code}...").format(code=code)
            )
        self.on_connect_requested(code, StreamType.WEBRTC)

    def _on_pairing_cancelled(self):
        """Operator dismissed the prompt — abandon any in-flight attempt."""
        if self.stream_coordinator.stream_manager is not None:
            self.stream_coordinator.disconnect_stream()
        self._pairing_code = None

    def _on_pairing_dialog_destroyed(self, *_args):
        self._pairing_dialog = None

    def _close_pairing_dialog(self):
        """Dismiss the prompt once a session is established."""
        dialog = self._pairing_dialog
        self._pairing_dialog = None
        if dialog is not None:
            dialog.accept()

    def _report_pairing_progress(self, message: str) -> bool:
        """Route a pre-connection status into the pairing prompt.

        Returns True when the message was a failure, so the caller knows
        the attempt is over rather than still in progress.
        """
        dialog = self._pairing_dialog
        if dialog is None:
            return False
        if message.startswith(ERROR_STATUS_PREFIX):
            dialog.show_failed(message[len(ERROR_STATUS_PREFIX):])
            return True
        if message:
            dialog.show_negotiating(message)
        return False

    def _has_known_stream_resolution(self) -> bool:
        """True once the source has reported a real frame size."""
        resolution = (self.stream_coordinator.stream_info or {}).get('resolution')
        try:
            width, height = resolution
            return int(width) > 0 and int(height) > 0
        except (TypeError, ValueError):
            return False

    def _start_pending_auto_record(self) -> None:
        """Fire the wizard's auto-record once, at a known resolution."""
        self._pending_auto_record = False
        default_recording_dir = os.path.expanduser("~")
        record_dir = (
            self._pending_record_dir
            or self.recording_dir_edit.text().strip()
            or default_recording_dir
        )
        self.on_start_recording_requested(record_dir)

    def _get_target_fps_limit_from_widget(self) -> Optional[int]:
        """Read target FPS from the loaded algorithm widget config."""
        if not self.algorithm_widget or not hasattr(self.algorithm_widget, 'get_config'):
            return None
        try:
            config = self.algorithm_widget.get_config()
            if not isinstance(config, dict):
                return None
            raw_fps_limit = config.get('target_fps')
            if raw_fps_limit is None:
                return None
            fps_limit = int(raw_fps_limit)
            return fps_limit if fps_limit > 0 else None
        except (TypeError, ValueError, AttributeError):
            return None

    @Slot()
    def on_disconnect_requested(self):
        """Handle stream disconnection request."""
        # Disconnect the stream first - this stops frame delivery
        # and signals the stream reader to stop
        self.stream_coordinator.disconnect_stream()
        self._active_stream_fps_limit = None
        # Then cleanup the processing worker (should be quick since no frames coming)
        self._cleanup_processing_worker()
        # Reset algorithm state for next video session (clears background models,
        # temporal history, etc. to prevent carryover between videos)
        if self.algorithm_widget:
            self.algorithm_widget.cleanup()

        # Reset video display to show "No Stream Connected" (clears cached
        # image + zoom) and drop any pending/highlight focus state.
        self.video_display.clear_display(self.tr("No Stream Connected"))
        self._reset_focus_state()
        self._reset_telemetry_surfaces()
        # The pairing code belonged to that session; a reconnect needs a
        # fresh prompt (and, in practice, a fresh code from the tablet).
        # Guarded so a File/RTMP disconnect never blanks its own URL field.
        if self._pairing_code:
            self._pairing_code = None
            self.stream_controls.set_paired_code("")

        # Clear thumbnails
        if hasattr(self, 'thumbnail_widget'):
            self.thumbnail_widget.clear_thumbnails()

    @Slot(bool, str)
    def on_connection_changed(self, connected: bool, message: str):
        """Handle connection status change.

        ``connected=False`` covers two very different things: an actual
        loss of a live stream, and *progress* reported while a connection
        is still being established. A WebRTC pair emits several of the
        latter ("Looking up pairing code...", "Connecting..."), and RTMP
        emits "Reconnecting... (attempt N)". Treating those as
        disconnections ran the full teardown mid-connect — which, among
        other things, discarded the wizard's pending processing
        resolution before the first frame could be capped with it.

        Teardown is therefore edge-triggered on a real
        connected -> disconnected transition.
        """
        was_connected = self._connection_established
        self._connection_established = bool(connected)
        # Only a genuine loss (or a hard failure of a live attempt) should
        # tear the session down.
        real_disconnect = was_connected and not connected

        # A new/replacement source or a connection loss invalidates any
        # gallery/thumbnail focus armed against the previous source, and starts
        # a new frame session so late async results from the old one are dropped.
        if connected or real_disconnect:
            self._frame_session += 1
            self._reset_focus_state()

        # Update bottom status bar with connection state. Pre-connection
        # progress is labelled as such rather than as "Disconnected".
        if connected:
            state = self.tr("Connected")
        elif was_connected:
            state = self.tr("Disconnected")
        else:
            state = self.tr("Connecting")
        status_text = self.tr("{state} - {message}").format(
            state=state, message=message
        )
        self.ui.statusbar.showMessage(status_text)
        # Update stream controls status section
        if hasattr(self, "stream_controls"):
            self.stream_controls.update_connection_status(connected, message)

        if connected:
            # Pairing succeeded — dismiss the prompt and show which drone
            # this session is on.
            self._close_pairing_dialog()
            if self._pairing_code:
                self.stream_controls.set_paired_code(self._pairing_code)

            if self._active_stream_fps_limit is None:
                self._active_stream_fps_limit = self._get_target_fps_limit_from_widget()
            self.ui.infoPanel.append(
                self.tr("✓ Connected: {message}").format(message=message)
            )

            # A new source is there to be watched, not reviewed: the Gallery
            # holds tracks from the session that just ended, so leave it for
            # the Live View where the incoming frames appear.
            if self.tab_widget.currentWidget() is self.gallery_widget:
                self.tab_widget.setCurrentIndex(0)

            # File streams get the full bar (timeline + recording); live
            # streams get the record-only strip - a live feed has no
            # timeline, but it is exactly what the operator records.
            if self.stream_coordinator.current_stream_type == StreamType.FILE:
                self.playback_controls.show_for_file()
            else:
                self.playback_controls.show_for_live()

            # Notify algorithm
            if self.algorithm_widget:
                # Get stream resolution from stream_info if available, otherwise use placeholder
                resolution = self.stream_coordinator.stream_info.get('resolution') or (1920, 1080)
                self.algorithm_widget.on_stream_connected(resolution)
                self._apply_stream_resolution_to_mask_controls(resolution)

            # Recreate processing worker if it was cleaned up during disconnect
            # This ensures second video also uses worker thread for processing
            if self.algorithm_widget and not self._processing_worker:
                self._setup_processing_worker()

            # Auto-record sizes its writer from the stream resolution, and
            # any mismatched frame is downscaled to it. File/RTMP report
            # resolution before reporting "connected", but a WebRTC pair
            # reports connected as soon as ICE completes — before any frame
            # exists — so starting here would silently record a 4K ADIAT
            # Flight feed at the 1280x720 fallback. Defer to the first frame
            # when the resolution isn't known yet.
            if self._pending_auto_record:
                if self._has_known_stream_resolution():
                    self._start_pending_auto_record()
        elif not real_disconnect:
            # Still connecting — report progress without tearing anything
            # down. The session has not started, so there is nothing to
            # reset, and resetting here would discard state the pending
            # connection still needs (e.g. the wizard's processing
            # resolution, applied when the first frame arrives).
            self._report_pairing_progress(message)
            if message:
                self.ui.infoPanel.append(
                    self.tr("… {message}").format(message=message)
                )
        else:
            self._active_stream_fps_limit = None
            self.ui.infoPanel.append(
                self.tr("✗ Disconnected: {message}").format(message=message)
            )

            # Hide playback controls
            self.playback_controls.hide_for_stream()

            # Notify algorithm
            if self.algorithm_widget:
                self.algorithm_widget.on_stream_disconnected()

            # Reset statistics
            self.stream_statistics.reset()

            # Reset the video display so an unexpected disconnect (or the
            # disconnect that precedes a replacement source) does not leave the
            # last frame + zoom behind. Clearing the cached image also forces a
            # same-resolution replacement source to rebuild via the full
            # setImage/reset path instead of inheriting old pan/zoom.
            self.video_display.clear_display(self.tr("No Stream Connected"))

            # Clear gallery and tracks on disconnect
            if hasattr(self, 'gallery_widget'):
                self.gallery_widget.clear()
            if hasattr(self, 'thumbnail_widget'):
                self.thumbnail_widget.clear_thumbnails()
                self.thumbnail_widget.tracker.tracks.clear()
            self._original_frames_queue.clear()
            self._pending_worker_frame = None
            # Do not clear the in-flight flag here. A job from the disconnected
            # session may still be running; its session-tagged callback will
            # release this slot and dispatch the latest pending frame from a
            # subsequently connected source. Clearing it early permits two
            # worker jobs to overlap after a fast reconnect.

            # Clear pending resolution (will be reapplied on next connection if wizard runs again)
            self._pending_processing_resolution = None

    @Slot(dict)
    def on_algorithm_config_changed(self, config: dict):
        """
        Apply runtime FPS-limit changes immediately while connected.

        Controllers emit this whenever controls change; only target_fps is handled here.
        """
        if not self.stream_coordinator.is_connected:
            return
        if not isinstance(config, dict):
            return
        raw_fps_limit = config.get('target_fps')
        if raw_fps_limit is None:
            fps_limit = None
        else:
            try:
                fps_limit = int(raw_fps_limit)
            except (TypeError, ValueError):
                return
            if fps_limit <= 0:
                fps_limit = None

        if fps_limit == self._active_stream_fps_limit:
            return

        if self.stream_coordinator.update_fps_limit(fps_limit):
            self._active_stream_fps_limit = fps_limit

    @Slot(np.ndarray, float, int)
    def on_frame_received(self, frame: np.ndarray, timestamp: float, video_frame_pos: int = 0):
        """Handle frame received from stream."""
        # A queued raw frame can arrive after an unexpected connection loss.
        # Keep direct no-manager test/preview use intact, but never let a
        # disconnected managed source repaint the placeholder.
        if (self.stream_coordinator.stream_manager is not None and
                not self.stream_coordinator.is_connected):
            return

        # Store timestamp and video frame position for track storage
        self._current_frame_timestamp = timestamp
        self._current_video_frame_pos = video_frame_pos

        # Record frame receipt in statistics
        self.stream_statistics.on_frame_received(timestamp)

        # Check if stream is paused (for file playback) - skip processing if paused
        is_paused = False
        if (self.stream_coordinator.stream_manager and
                hasattr(self.stream_coordinator.stream_manager, 'is_playing')):
            is_paused = not self.stream_coordinator.stream_manager.is_playing()

        if self.algorithm_widget and not is_paused:
            # Store original frame for thumbnails (before detection rendering)
            # This ensures thumbnails are crisp without detection overlays.
            self._original_frame_for_thumbnails = frame

            # Add to queue for synchronization with worker thread.
            self._original_frames_queue[timestamp] = self._original_frame_for_thumbnails

            # Prune queue aggressively to keep memory bounded under long sessions.
            if len(self._original_frames_queue) > self._MAX_ORIGINAL_FRAME_CACHE:
                oldest_ts = min(self._original_frames_queue.keys())
                del self._original_frames_queue[oldest_ts]
        else:
            self._original_frame_for_thumbnails = None

        # Auto-record deferred from connect because the source had not yet
        # reported a resolution (WebRTC connects before the first frame).
        if self._pending_auto_record and self._has_known_stream_resolution():
            self._start_pending_auto_record()

        # Apply resolution capping on first frame (to prevent upscaling)
        if self._pending_processing_resolution is not None:
            # Get native video resolution from frame
            native_height, native_width = frame.shape[:2]
            desired_width, desired_height = self._pending_processing_resolution

            if desired_width is not None and desired_height is not None and desired_width > 0 and desired_height > 0:
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

        # Process frame with algorithm if loaded and not paused
        if self.algorithm_widget and not is_paused:
            # Use worker thread if available, otherwise fall back to main thread
            use_worker = False
            # Check if worker is available, running, and not in the process of stopping
            if (self._processing_worker and self._processing_thread and
                    self._processing_thread.isRunning() and not self._is_stopping_worker):
                use_worker = self._queue_worker_frame(frame, timestamp, video_frame_pos)

            if not use_worker:
                # Fallback to main thread processing (for compatibility)
                start_time = time.time()

                try:
                    # Process frame
                    detections = self.algorithm_widget.process_frame(frame, timestamp)

                    # Record processing completion
                    processing_time_ms = (time.time() - start_time) * 1000
                    # Fallback path doesn't have access to was_skipped flag from timings
                    self.stream_statistics.on_frame_processed(processing_time_ms, len(detections), was_skipped=False)

                    self._latest_detections_for_rendering = detections

                    rendered_frame = None
                    if not self.algorithm_renders_frame:
                        # Render detections using the shared renderer
                        display_frame = frame.copy()
                        rendered_frame = self.detection_renderer.render(display_frame, detections, copy_frame=False)

                        # Draw highlight box if a gallery track is selected
                        if self._highlight_track is not None:
                            rendered_frame = self._draw_gallery_highlight(rendered_frame)

                        # Update display with rendered frame (applies any pending focus)
                        self._present_frame(rendered_frame, video_frame_pos, 'main')
                    # else: Algorithm provides custom rendering via on_algorithm_frame_processed

                    self._update_thumbnails(frame, detections, timestamp, video_frame_pos)

                    # Record frame if recording (when rendering is handled here)
                    if self.stream_coordinator.is_recording and not self.algorithm_renders_frame:
                        if rendered_frame is None:
                            rendered_frame = frame
                        self.stream_coordinator.record_frame(
                            rendered_frame, detections,
                            self._video_time_for_frame(video_frame_pos),
                        )

                except Exception as e:
                    self.logger.error(f"Error processing frame: {str(e)}")
                    self._discard_original_frame(timestamp)
        else:
            # No algorithm loaded (or stream paused), display raw frame.
            # This is the path the sought gallery frame travels while paused,
            # so it is authoritative for applying a pending focus.
            display_frame = frame
            if self._highlight_track is not None:
                display_frame = self._draw_gallery_highlight(display_frame)
            self._present_frame(display_frame, video_frame_pos, 'raw')
            self._discard_original_frame(timestamp)
            if self.stream_coordinator.is_recording:
                self.stream_coordinator.record_frame(
                    display_frame, [], self._video_time_for_frame(video_frame_pos)
                )

    @Slot(np.ndarray)
    def on_algorithm_frame_processed(self, annotated_frame: np.ndarray):
        """Handle frames rendered by the algorithm itself."""
        if not self.algorithm_renders_frame:
            return

        # Drop a late custom-render result after either an unexpected
        # connection loss (manager retained) or an explicit disconnect
        # (manager removed), so it cannot repaint over the placeholder.
        if (self.stream_coordinator.stream_manager is None or
                not self.stream_coordinator.is_connected):
            return

        # Only record what was actually presented (a frame rejected while paused
        # must not be recorded as if it were displayed).
        if self._present_frame(annotated_frame, self._current_video_frame_pos, 'custom'):
            if self.stream_coordinator.is_recording:
                detections = getattr(self, "_latest_detections_for_rendering", [])
                self.stream_coordinator.record_frame(
                    annotated_frame, detections,
                    self._video_time_for_frame(self._current_video_frame_pos),
                )

    @Slot(list)
    def on_detections_ready(self, detections: list):
        """Handle detections from algorithm."""
        # Update detection info panel with a concise summary
        self.ui.infoPanel.clear()
        if not detections:
            self.ui.infoPanel.setPlainText(self.tr("No detections found."))
            return

        self.ui.infoPanel.append(
            self.tr("Detection Results ({count} found):").format(
                count=len(detections)
            )
        )
        # Show a brief summary of up to first 5 detections
        for idx, det in enumerate(detections[:5], start=1):
            bbox = det.get("bbox") if isinstance(det, dict) else getattr(det, "bbox", None)
            cls = det.get("class_name") if isinstance(det, dict) else getattr(det, "class_name", "Detection")
            conf = det.get("confidence") if isinstance(det, dict) else getattr(det, "confidence", None)
            if bbox is not None:
                x, y, w, h = bbox
                summary = self.tr(
                    "#{index}: Type({cls}) Pos({x},{y}) Size({w}x{h})"
                ).format(
                    index=idx,
                    cls=cls,
                    x=x,
                    y=y,
                    w=w,
                    h=h
                )
            else:
                summary = self.tr("#{index}: Type({cls})").format(
                    index=idx,
                    cls=cls
                )
            if conf is not None:
                summary += self.tr(" Conf({confidence:.2f})").format(
                    confidence=conf
                )
            self.ui.infoPanel.append(summary)

    @Slot(str)
    def on_start_recording_requested(self, directory: str):
        """Start recording with provided directory."""
        default_recording_dir = os.path.expanduser("~")
        output_dir = directory or default_recording_dir
        self.settings.setValue("recording/output_dir", output_dir)
        self.settings.sync()
        self.stream_coordinator.start_recording(output_dir, self._recording_metadata())

    def _recording_metadata(self) -> Dict[str, Any]:
        """Describe what this recording should capture, and in what context."""
        # Deliberately not gated on telemetry being available *yet*: a live
        # feed reports its first fix after the stream is up, so gating here
        # would discard the flight of any recording started before it.
        # Capturing costs nothing when no fix ever arrives.
        save_map = (
            not hasattr(self, "save_map_check")
            or self.save_map_check.isChecked()
        )
        # StreamAlgorithmController's configuration accessor is get_config;
        # recorded purely as provenance, so a controller that cannot report
        # its settings costs the manifest a field, not the recording.
        options: Dict[str, Any] = {}
        if self.algorithm_widget is not None and hasattr(self.algorithm_widget, "get_config"):
            try:
                options = self.algorithm_widget.get_config() or {}
            except Exception as exc:  # noqa: BLE001 - context is optional
                self.logger.error(f"Could not read algorithm options for recording: {exc}")
        return {
            "save_detections": (
                not hasattr(self, "save_detections_check")
                or self.save_detections_check.isChecked()
            ),
            "save_flight_map": save_map,
            "frame_level_detections": self._settings_bool(
                "recording/frame_level_detections", False
            ),
            "algorithm": self.current_algorithm_name or "",
            "algorithm_options": options,
        }

    @Slot(dict)
    def on_recording_bundle_ready(self, result: dict):
        """Report the finished recording bundle and offer to open it."""
        if not isinstance(result, dict):
            return
        bundle_dir = result.get("bundle_dir")
        if not bundle_dir:
            return

        self._last_recording_bundle = bundle_dir
        if hasattr(self, "open_recording_btn"):
            self.open_recording_btn.setVisible(True)
        from core.services.streaming.RecordingLibrary import RecordingLibrary
        video = RecordingLibrary.first_video_in(bundle_dir)
        if video:
            self._last_recording_video = video
            if hasattr(self, "replay_recording_btn"):
                self.replay_recording_btn.setVisible(True)

        counts = result.get("counts") or {}
        detections = int(counts.get("detections_stored") or 0)
        fixes = int(counts.get("telemetry_fixes") or 0)
        self.ui.infoPanel.append(
            self.tr("Recording saved to {folder}").format(folder=bundle_dir)
        )
        self.ui.infoPanel.append(
            self.tr("Stored {detections} detections and {fixes} location fixes.").format(
                detections=detections, fixes=fixes
            )
        )
        artifacts = result.get("artifacts") or {}
        if artifacts.get("flight_map_html"):
            self.ui.infoPanel.append(
                self.tr("Flight map saved as {name}").format(
                    name=artifacts["flight_map_html"]
                )
            )
        for message in result.get("errors") or []:
            self.logger.error(f"Recording bundle warning: {message}")
            self.ui.infoPanel.append(
                self.tr("Could not save part of the recording: {reason}").format(
                    reason=message
                )
            )

    @Slot(bool)
    def _on_telemetry_availability_changed(self, available: bool):
        """Follow telemetry availability with the flight-map option."""
        self._update_map_option_hint()

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
            self.ui.statusbar.showMessage(
                self.tr("Recording started: {path}").format(path=path)
            )

            # Notify algorithm
            if self.algorithm_widget:
                self.algorithm_widget.on_recording_started(path)
        else:
            self.ui.statusbar.showMessage(self.tr("Recording stopped"))

            # Notify algorithm
            if self.algorithm_widget:
                self.algorithm_widget.on_recording_stopped(path)

    def _update_recording_state(self, recording: bool, path: str):
        """Update recording widget UI state.

        The single record toggle never disables, so - unlike the old
        Start/Stop pair - no focus handoff is needed here: nothing gets
        disabled under the user's focus, and the scroll area holds still.
        """
        self.playback_controls.set_recording_state(recording)
        if not hasattr(self, 'recording_status'):
            return
        if recording:
            self.recording_status.setText(
                self.tr("Status: Recording to {path}").format(path=path)
            )
            self.recording_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        else:
            self.recording_status.setText(self.tr("Status: Not Recording"))
            self.recording_status.setStyleSheet("QLabel { color: gray; }")
            self.recording_info.setText(self.tr("Duration: --"))

    @Slot(dict)
    def on_recording_stats_updated(self, stats: dict):
        """Render live recording statistics in the recording panel."""
        if not hasattr(self, 'recording_info') or not isinstance(stats, dict):
            return

        duration = float(stats.get('segment_duration', 0.0) or 0.0)
        fps = float(stats.get('recording_fps', 0.0) or 0.0)
        frames = int(stats.get('frame_count', 0) or 0)
        queue_size = int(stats.get('queue_size', 0) or 0)

        self.recording_info.setText(
            self.tr("Duration: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames} | Queue: {queue}").format(
                duration=duration,
                fps=fps,
                frames=frames,
                queue=queue_size
            )
        )

    @Slot(str)
    def on_status_update(self, message: str):
        """Handle status update from algorithm."""
        self.ui.statusbar.showMessage(message)

    @Slot(str)
    def on_error(self, error: str):
        """Handle error."""
        self.logger.error(error)
        self.ui.infoPanel.append(
            self.tr("✗ Error: {error}").format(error=error)
        )
        QMessageBox.warning(self, self.tr("Error"), error)

    @Slot(bool)
    def on_recording_request(self, start: bool):
        """Handle recording request from algorithm."""
        self.on_recording_toggled(start)

    @Slot()
    def on_play_pause_toggled(self):
        """Handle play/pause toggle (for file playback)."""
        # A manual play/pause (button or Space) cancels any pending gallery
        # focus and clears the highlight so a resume can't snap in a stale zoom.
        self._reset_focus_state()

        # Toggle play/pause on stream manager
        if self.stream_coordinator.stream_manager and hasattr(self.stream_coordinator.stream_manager, 'play_pause'):
            self.stream_coordinator.stream_manager.play_pause()

    @Slot(float)
    def on_seek_requested(self, time_seconds: float):
        """Handle seek request (for file playback)."""
        # A manual seek cancels any pending gallery focus/highlight (a gallery
        # click re-arms it afterwards via its own path).
        self._reset_focus_state()

        # Request seek from stream manager
        if self.stream_coordinator.stream_manager and hasattr(self.stream_coordinator.stream_manager, 'seek_to_time'):
            self.stream_coordinator.stream_manager.seek_to_time(time_seconds)

    def _on_gallery_track_clicked(self, track):
        """Handle click on gallery item - seek to detection frame and highlight.

        Args:
            track: Track object containing frame index and bbox for seeking/highlighting
        """
        # Check if we're playing a file (seekable) or live stream (not seekable)
        if self.stream_coordinator.current_stream_type == StreamType.FILE:
            stream_mgr = self.stream_coordinator.stream_manager
            if not stream_mgr:
                return

            # A newer selection supersedes any in-flight seek/focus. This bumps
            # the focus generation so an older delayed seek/timeout no-ops.
            generation = self._begin_focus_generation()

            # Pause video so user can see the highlighted detection.
            # (Direct play_pause, not on_play_pause_toggled, so it does not
            # reset the focus we are about to arm.)
            is_playing = stream_mgr.is_playing() if hasattr(stream_mgr, "is_playing") else True
            if is_playing:
                stream_mgr.play_pause()

            # Store track for highlighting
            self._highlight_track = track

            # Switch to Live View tab
            self.tab_widget.setCurrentIndex(0)

            # No delay before the seek: play_pause() flips _is_playing
            # synchronously under the same _playback_lock that seek_to_frame
            # and the capture loop take, and _awaiting_seek_frame lets the
            # sought frame be decoded while paused. There was never anything
            # to settle - and RTMPStreamService already documents the hazard
            # of a frame interval longer than the delay was.
            #
            # The zoom still lands event-driven, on seekCompleted for this
            # seek's request id.
            self._seek_to_track_frame(track, generation)
        else:
            # Live stream - cannot seek, show info dialog
            QMessageBox.information(
                self,
                self.tr("Live Stream"),
                self.tr(
                    "Cannot seek in live stream.\n\n"
                    "Detection was first seen at frame {frame}."
                ).format(frame=track.first_frame_index)
            )

    def _seek_to_track_frame(self, track, generation):
        """Seek to a gallery track's frame and arm the one-shot zoom focus.

        Uses the authoritative resolved frame from ``seek_to_frame`` (no FPS
        recomputation). ``first_frame_index`` is the position the service
        reports AFTER decoding the thumbnail's frame (OpenCV advances
        CAP_PROP_POS_FRAMES past the frame it just read), so it is one greater
        than that frame's own index. Seeking to ``first_frame_index - 1``
        re-decodes the exact thumbnail frame; the service then reports
        ``first_frame_index`` for it, so we correlate against
        ``{resolved, resolved + 1}``.
        """
        # Reject stale delayed callbacks from a superseded selection.
        if generation != self._focus_generation:
            return
        try:
            stream_mgr = self.stream_coordinator.stream_manager
            if not stream_mgr or not hasattr(stream_mgr, "seek_to_frame"):
                self._abandon_gallery_focus()
                return

            target_frame = max(0, int(track.first_frame_index) - 1)
            resolved = stream_mgr.seek_to_frame(target_frame)
            if resolved is None:
                self.logger.warning("Gallery seek failed; clearing pending focus")
                self._abandon_gallery_focus()
                return

            # Arm the one-shot focus, correlated to THIS seek's request id. The
            # service reports seekCompleted(request_id, ...) once the sought
            # frame is painted (success) or the seek fails.
            self._pending_focus_target = self._focus_target_from_track(track)
            self._pending_focus_seek_id = stream_mgr.last_seek_id if hasattr(stream_mgr, "last_seek_id") else 0
            self._pending_focus_positions = {int(resolved), int(resolved) + 1}
            self._pending_focus_generation = generation
            # 2.9: bounded give-up guard, not a settle wait. The real
            # completion event is seekCompleted, correlated by request id and
            # consumed above; this only fires if the seek never ends.
            QTimer.singleShot(
                self._FOCUS_TIMEOUT_MS,
                lambda g=generation: self._on_focus_timeout(g),
            )
        except Exception as e:
            self.logger.error(f"Error seeking to highlighted frame: {e}")
            self._abandon_gallery_focus()

    def _abandon_gallery_focus(self):
        """Drop a failed/timed-out gallery focus, including its highlight.

        A highlight only makes sense on the sought frame; if the seek never
        lands (failure, exception, or timeout) the highlight must be cleared so
        later frames are not circled for a detection that was never reached.
        """
        self._clear_pending_focus_state()
        self._clear_gallery_highlight()

    def _draw_gallery_highlight(self, frame: np.ndarray) -> np.ndarray:
        """Draw a highlight circle around the selected gallery track's detection.

        Args:
            frame: The frame to draw on

        Returns:
            Frame with highlight drawn (modifies in place for efficiency)
        """
        if self._highlight_track is None:
            return frame

        track = self._highlight_track
        x, y, w, h = track.bbox
        cx, cy = track.centroid

        # Scale coordinates if frame resolution differs from when detection was captured
        current_h, current_w = frame.shape[:2]
        stored_w, stored_h = track.frame_resolution

        if stored_w > 0 and stored_h > 0 and (stored_w != current_w or stored_h != current_h):
            # Calculate scale factors
            scale_x = current_w / stored_w
            scale_y = current_h / stored_h

            # Scale bbox and centroid
            x = int(x * scale_x)
            y = int(y * scale_y)
            w = int(w * scale_x)
            h = int(h * scale_y)
            cx = int(cx * scale_x)
            cy = int(cy * scale_y)

        # Use detection color if available, otherwise bright cyan
        if track.detection_color is not None:
            highlight_color = track.detection_color
        else:
            highlight_color = (255, 255, 0)  # Cyan in BGR as fallback

        # Calculate circle center and radius to encompass the detection
        # Radius should be large enough to circle the detection bbox
        radius = int(max(w, h) * 0.75)
        thickness = 4

        # Draw circle around the detection
        cv2.circle(frame, (cx, cy), radius, highlight_color, thickness)

        return frame

    def _clear_gallery_highlight(self):
        """Clear the gallery highlight (called on play, new seek, etc.)."""
        self._highlight_track = None

    # ------------------------------------------------------------------ #
    #  Zoom focus lifecycle (gallery + thumbnail)
    # ------------------------------------------------------------------ #
    def _begin_focus_generation(self):
        """Start a new focus generation, invalidating any in-flight focus.

        Rapid gallery clicks or a competing thumbnail click bump the generation
        so stale delayed seeks, focus-timeout callbacks and an armed pending
        focus from an earlier selection are ignored.
        """
        self._focus_generation += 1
        self._clear_pending_focus_state()
        return self._focus_generation

    def _clear_pending_focus_state(self):
        """Drop the armed one-shot gallery focus (leaves the highlight alone)."""
        self._pending_focus_target = None
        self._pending_focus_seek_id = 0
        self._pending_focus_positions.clear()
        self._pending_focus_generation = None

    def _reset_focus_state(self):
        """Idempotent reset of gallery pending focus + highlight state.

        Used on disconnect, connection loss, new/replacement source, seek
        failure, manual seek, resume, a newer gallery selection, and a competing
        thumbnail click. Does NOT reset the display's manual zoom (that survives
        normal frame replacement and pause/resume).

        It deliberately does NOT clear the thumbnail strip's click payloads:
        those stay valid as long as their visible pixmaps do, so pausing or
        seeking never makes a still-visible thumbnail unclickable. Thumbnail
        payloads are dropped by the strip when a slot empties or a newer frame
        arrives while it is hidden, and wholesale by ``clear_thumbnails`` on
        disconnect/new source.
        """
        self._focus_generation += 1
        self._clear_pending_focus_state()
        self._highlight_track = None

    def _focus_target_from_track(self, track) -> FocusTarget:
        """Build a source-space focus payload from a gallery track."""
        width, height = track.frame_resolution
        return FocusTarget(center_xy=tuple(track.centroid), reference_size=(width, height))

    def _is_file_playback_paused(self) -> bool:
        """True when a seekable file stream is currently paused."""
        if self.stream_coordinator.current_stream_type != StreamType.FILE:
            return False
        mgr = self.stream_coordinator.stream_manager
        if mgr is not None and hasattr(mgr, 'is_playing'):
            try:
                return not mgr.is_playing()
            except Exception:
                return False
        return False

    def _present_frame(self, frame: np.ndarray, frame_position: int, origin: str) -> bool:
        """Central display sink: update the view.

        While file playback is paused, only the raw path is authoritative (it
        carries the sought gallery frame); late worker/custom results are
        ignored so a pre-seek frame cannot overwrite the sought frame.

        The gallery zoom is NOT applied here: it is applied in
        :meth:`_on_seek_completed`, correlated by seek request id and emitted by
        the service AFTER this frame is painted.

        Returns True if the frame was actually presented. Callers MUST gate
        presentation-coupled side effects (thumbnail refresh, recording) on this
        so a rejected frame does not leave thumbnails/recordings representing a
        frame the user is not viewing.
        """
        if origin != 'raw' and self._is_file_playback_paused():
            return False
        self.video_display.update_frame(frame)
        return True

    @Slot(int, int, bool)
    def _on_seek_completed(self, request_id: int, frame_position: int, success: bool):
        """Apply (or abandon) the one-shot gallery focus for a completed seek.

        Correlated by seek REQUEST ID and the authoritative resolved position
        window, so neither an older seek nor an unrelated post-seek frame can
        consume the pending focus. The service emits this AFTER the sought frame
        is painted, so the scene rect is current when we focus.
        """
        if self._pending_focus_target is None:
            return
        if request_id != self._pending_focus_seek_id:
            return  # a superseded or unrelated seek
        if not success:
            self.logger.warning(f"Gallery seek {request_id} failed; clearing pending focus")
            self._abandon_gallery_focus()
            return
        if frame_position not in self._pending_focus_positions:
            self.logger.warning(
                f"Gallery seek {request_id} completed at unexpected frame "
                f"{frame_position}; expected one of "
                f"{sorted(self._pending_focus_positions)}. Clearing pending focus."
            )
            self._abandon_gallery_focus()
            return
        target = self._pending_focus_target
        self._clear_pending_focus_state()
        self.video_display.focus_on(target)

    def _on_focus_timeout(self, generation: int):
        """Backstop: cancel an armed focus if no seekCompleted ever arrives."""
        if generation != self._pending_focus_generation:
            return
        if self._pending_focus_target is None:
            return
        self.logger.warning(
            f"Gallery focus timed out (seek id {self._pending_focus_seek_id} never "
            "reported completion). Clearing pending focus and highlight."
        )
        self._abandon_gallery_focus()

    def _on_thumbnail_focus_requested(self, target: FocusTarget):
        """Immediate live focus from a thumbnail click (no pause, no seek).

        Cancels any armed gallery focus and clears the gallery highlight so the
        two focus sources cannot fight, then centers at 6x. Works while playing
        or paused.
        """
        self._begin_focus_generation()   # supersede any pending gallery focus
        self._clear_gallery_highlight()
        self.video_display.focus_on(target)

    @Slot(dict)
    def on_stream_info_updated(self, stream_info: dict):
        """Handle stream info updates (for playback position)."""
        # Update playback controls with video position if available
        if self.stream_coordinator.current_stream_type == StreamType.FILE:
            if 'current_time' in stream_info and 'total_time' in stream_info:
                self.playback_controls.update_time(stream_info['current_time'], stream_info['total_time'])
                # Drive file-derived telemetry from the playhead so the HUD
                # and map track the video, including while scrubbing.
                self.telemetry_coordinator.on_position_changed(stream_info['current_time'])
            if 'is_playing' in stream_info:
                is_playing = stream_info['is_playing']
                self.playback_controls.update_play_state(is_playing)

    @Slot(dict)
    def on_telemetry_updated(self, envelope: dict):
        """Render a telemetry envelope into the HUD and move the aircraft."""
        if not isinstance(envelope, dict):
            return

        self.telemetry_hud.apply_envelope(envelope)
        if not self.telemetry_hud.isVisible():
            self.telemetry_hud.setVisible(True)
        self._reposition_telemetry_hud()

        # For a file we replace the whole trail from ``trackUpdated`` (so
        # seeking backwards shortens it); for a live feed there is no track
        # to recompute, so each fix extends the path.
        is_live = self.stream_coordinator.current_stream_type != StreamType.FILE
        self.map_view.update_aircraft(envelope, extend_track=is_live)

        # An active recording gets the same fixes, which is what bounds its
        # flight map to the window that was actually recorded.
        self.stream_coordinator.append_telemetry(envelope)

    @Slot(list)
    def _on_flight_path_updated(self, path: list):
        """Replace the plotted flight path (file playback)."""
        self.map_view.set_track(path)

    @Slot(str)
    def _on_telemetry_status(self, message: str):
        """Report where location data came from, or that there is none."""
        if message:
            self.ui.infoPanel.append(message)

    def _resolve_track_position(self, track) -> Optional[Tuple[float, float]]:
        """``(lat, lon)`` for a confirmed detection, or None when unknown.

        Detections carry no coordinates of their own — the aircraft's
        position when the detection was captured is the best available
        geotag, which is the same approximation the image-analysis AOI
        pipeline starts from.

        Single source of truth on purpose: the live map pin and the stored
        detection record must agree about where a detection was, so both
        ask this rather than each resolving a position of their own.
        """
        if track is None or not self.telemetry_coordinator.is_available:
            return None

        position = None
        # For a file we can look up the exact frame time; for a live feed the
        # most recent fix is the closest we can get.
        if self.stream_coordinator.current_stream_type == StreamType.FILE:
            seconds = self._video_time_for_frame(getattr(track, "first_frame_index", None))
            if seconds is not None:
                position = self.telemetry_coordinator.position_at(seconds)
        if position is None:
            position = self.telemetry_coordinator.current_position()
        return position

    def _on_track_confirmed_for_map(self, track):
        """Pin a confirmed detection at the aircraft position of its frame.

        Silently skipped when the source has no location data, so
        non-telemetry videos behave exactly as before.
        """
        position = self._resolve_track_position(track)
        if position is None:
            return

        key = f"track-{getattr(track, 'track_id', id(track))}"
        self._gallery_tracks_by_key[key] = track
        self.map_view.add_detection({
            "track_key": key,
            "location": {"lat": position[0], "lon": position[1]},
            "class_name": getattr(track, "detection_type", "detection"),
            "confidence": getattr(track, "confidence", 0.0),
        })

    def _on_track_confirmed_for_recording(self, track):
        """Store a confirmed detection in the active recording's bundle.

        The confirmed track is the unit of record: it is what the Detection
        Gallery shows and what the operator reviews, where a per-frame log
        would mostly re-report the same blob. Nothing happens when no
        recording is running.
        """
        if track is None or not self.stream_coordinator.is_recording:
            return

        position = self._resolve_track_position(track)
        thumbnail = getattr(track, "thumbnail", None)
        record = DetectionRecord(
            track_id=int(getattr(track, "track_id", 0) or 0),
            bbox=tuple(getattr(track, "bbox", (0, 0, 0, 0)) or (0, 0, 0, 0)),
            centroid=getattr(track, "centroid", None),
            confidence=float(getattr(track, "confidence", 0.0) or 0.0),
            detection_type=str(getattr(track, "detection_type", "detection") or "detection"),
            pixel_area=float(getattr(track, "pixel_area", 0.0) or 0.0),
            frame_resolution=tuple(getattr(track, "frame_resolution", (0, 0)) or (0, 0)),
            first_frame_index=getattr(track, "first_frame_index", None),
            # Derived from the frame index, NOT from Track.first_timestamp:
            # that field carries the frame's time.perf_counter() reading,
            # which is an arbitrary origin rather than a position in the
            # video. Using it produced clock times that meant nothing and
            # could not be joined against telemetry.csv.
            video_time_seconds=self._video_time_for_frame(
                getattr(track, "first_frame_index", None)
            ),
            recorded_frame_index=self.stream_coordinator.recorded_frame_index(),
            latitude=position[0] if position else None,
            longitude=position[1] if position else None,
            detection_color=getattr(track, "detection_color", None),
            # The tracker already holds a private copy of this crop, but it
            # stays alive in the gallery for the whole session - copy so the
            # writer thread can never see it mutated or freed.
            thumbnail=thumbnail.copy() if thumbnail is not None and thumbnail.size else None,
            thumbnail_origin=tuple(getattr(track, "thumbnail_origin", (0, 0)) or (0, 0)),
        )
        self.stream_coordinator.append_detection_record(record)

    def _video_time_for_frame(self, frame_index) -> Optional[float]:
        """Convert a video frame index to seconds using the source FPS."""
        if not isinstance(frame_index, int) or frame_index < 0:
            return None
        info = self.stream_coordinator.stream_info or {}
        fps = info.get("source_fps") or info.get("fps") or 0
        try:
            fps = float(fps)
        except (TypeError, ValueError):
            return None
        if fps <= 0:
            return None
        return frame_index / fps

    def _on_map_pin_clicked(self, track_key: str):
        """Select the gallery track behind a clicked map pin."""
        track = self._gallery_tracks_by_key.get(track_key)
        if track is not None:
            self._on_gallery_track_clicked(track)

    def _reposition_telemetry_hud(self):
        """Anchor the HUD to the bottom edge of the video pane."""
        if not self.telemetry_hud.isVisible():
            return
        rect = self.video_display.rect()
        height = self.telemetry_hud.sizeHint().height()
        self.telemetry_hud.setGeometry(
            0,
            max(0, rect.height() - height),
            max(120, rect.width()),
            height,
        )

    def eventFilter(self, watched, event):
        """Keep the telemetry overlay pinned as the video pane resizes."""
        if watched is self.video_display and event.type() == QEvent.Resize:
            self._reposition_telemetry_hud()
        return super().eventFilter(watched, event)

    def _reset_telemetry_surfaces(self):
        """Clear HUD, aircraft marker, flight path, and detection pins."""
        self.telemetry_coordinator.reset()
        self.telemetry_hud.setVisible(False)
        self.map_view.reset()
        self._gallery_tracks_by_key.clear()

    def _restore_section_states(self):
        """Restore which right-panel sections were folded away last time."""
        for key, section in (
            ("stream_controls", self.ui.streamControlGroup),
            ("map", self.ui.mapGroup),
        ):
            saved = self.settings.value(f"panel/{key}_collapsed")
            if saved is None:
                continue
            # QSettings round-trips booleans as strings on some backends.
            collapsed = saved if isinstance(saved, bool) else str(saved).lower() == "true"
            section.setCollapsed(collapsed)

    def _save_section_state(self, key: str, collapsed: bool):
        self.settings.setValue(f"panel/{key}_collapsed", bool(collapsed))

    def update_statistics_display(self):
        """Update statistics display."""
        # Update performance section in stream controls
        stats_obj = self.stream_statistics.get_stats()

        # Get video info from stream coordinator
        stream_info = self.stream_coordinator.stream_info if self.stream_coordinator else {}
        video_resolution = stream_info.get('resolution')
        source_fps = stream_info.get('source_fps', stream_info.get('fps', 0))
        applied_source_fps = self._get_applied_source_fps(source_fps)

        # Get processing resolution from algorithm config
        processing_resolution = None
        if self.algorithm_widget:
            config = self.algorithm_widget.get_config()
            resolution_value = config.get('processing_resolution')
            if isinstance(resolution_value, tuple) and len(resolution_value) == 2:
                raw_width, raw_height = resolution_value
                if raw_width is not None and raw_height is not None:
                    try:
                        proc_width = int(raw_width)
                        proc_height = int(raw_height)
                    except (TypeError, ValueError):
                        proc_width = proc_height = 0
                    if proc_width > 0 and proc_height > 0:
                        processing_resolution = (proc_width, proc_height)

            if processing_resolution is None:
                proc_width = config.get('processing_width')
                proc_height = config.get('processing_height')
                if proc_width is None or proc_height is None:
                    processing_resolution = video_resolution
                else:
                    try:
                        proc_width = int(proc_width)
                        proc_height = int(proc_height)
                    except (TypeError, ValueError):
                        proc_width = proc_height = 0

                    if proc_width > 0 and proc_height > 0 and proc_width < 99999 and proc_height < 99999:
                        processing_resolution = (proc_width, proc_height)
                    elif video_resolution:
                        processing_resolution = video_resolution

        perf_payload = {
            "fps": stats_obj.fps,
            "avg_fps": stats_obj.processing_fps,
            "processing_fps": stats_obj.processing_fps,  # Actual frames processed per second
            "current_processing_time_ms": stats_obj.avg_processing_time_ms,
            "avg_processing_time_ms": stats_obj.avg_processing_time_ms,
            "latency_ms": stats_obj.latency_ms,
            "total_frames": stats_obj.total_frames,
            "detection_count": stats_obj.detection_count,
            "dropped_frames": stats_obj.dropped_frames,
            "video_resolution": video_resolution,
            "processing_resolution": processing_resolution,
            "video_fps": source_fps,
            "applied_source_fps": applied_source_fps,
        }
        self.stream_controls.update_performance(perf_payload)

    def _get_applied_source_fps(self, source_fps: float) -> float:
        """Estimate the runtime cadence applied to the current source."""
        explicit_limit = self._active_stream_fps_limit
        if explicit_limit is not None:
            if source_fps and source_fps > 0:
                return min(float(source_fps), float(explicit_limit))
            return float(explicit_limit)

        stream_type = self.stream_coordinator.current_stream_type if self.stream_coordinator else None
        if stream_type == StreamType.FILE:
            return float(source_fps or 0.0)
        if is_live_source(stream_type):
            if source_fps and source_fps > 0:
                return min(float(source_fps), 60.0)
            return 60.0
        return float(source_fps or 0.0)

    def update_theme(self, theme: str):
        """
        Apply the requested theme to the streaming viewer.

        Args:
            theme: Theme name ('Light' or 'Dark')
        """
        normalized = (theme or "dark").lower()
        self.theme = normalized
        try:
            # apply_theme installs the stylesheet AND the full palette so text
            # colours track the app theme rather than the OS light/dark setting.
            apply_theme(normalized)
        except Exception as e:
            self.logger.error(f"Error applying theme: {e}")

    def showEvent(self, event):
        """Ensure the viewer launches maximized on first show."""
        super().showEvent(event)
        self.update_controller.refresh_action_state()
        if not self._maximized_applied:
            self._maximized_applied = True
            self.showMaximized()
        # The automatic startup update check runs on the initial SelectionDialog;
        # here we only keep the manual "Check for Updates" menu action wired up.

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

        # Disconnect stream first - this stops frame delivery and signals stream to stop
        self.stream_coordinator.cleanup()

        # Stop the DEM lookup worker thread before the window goes away.
        self.telemetry_coordinator.cleanup()

        # Then cleanup processing worker (should be quick since no frames coming)
        self._cleanup_processing_worker()

        # Finally cleanup algorithm widget
        if self.algorithm_widget:
            self.algorithm_widget.cleanup()

        event.accept()
