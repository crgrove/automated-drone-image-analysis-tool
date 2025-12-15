"""
VideoTimelineWidget - Shared video playback timeline control.

Provides playback controls (play/pause, seek, timeline scrubbing) for video file playback
in streaming detection algorithms.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PySide6.QtCore import Qt, Signal


class VideoTimelineWidget(QWidget):
    """
    Video timeline widget with playback controls.

    Provides play/pause button, timeline slider, and time labels for video file playback.
    Emits signals for play/pause and seek operations.
    """

    # Signals
    playPauseRequested = Signal()  # Play/pause toggle requested
    seekRequested = Signal(float)  # Seek to position (0.0 to 1.0)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

        # State
        self.is_playing = False
        self.total_duration = 0.0
        self.current_time = 0.0
        self._seeking = False  # Track if user is actively seeking

        # Hide by default (shown only for file playback)
        self.setVisible(False)

    def setup_ui(self):
        """Setup the timeline UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Play/Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedWidth(40)
        self.play_pause_btn.setToolTip("Play/Pause (Space)")
        layout.addWidget(self.play_pause_btn)

        # Current time label
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setFixedWidth(50)
        self.current_time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.current_time_label)

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1000)
        self.timeline_slider.setValue(0)
        self.timeline_slider.setToolTip("Drag to seek through video")
        layout.addWidget(self.timeline_slider, 1)  # Stretch

        # Total duration label
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setFixedWidth(50)
        self.total_time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.total_time_label)

    def connect_signals(self):
        """Connect internal signals."""
        self.play_pause_btn.clicked.connect(self.on_play_pause_clicked)
        self.timeline_slider.sliderPressed.connect(self.on_slider_pressed)
        self.timeline_slider.sliderMoved.connect(self.on_slider_moved)
        self.timeline_slider.sliderReleased.connect(self.on_slider_released)

    def on_play_pause_clicked(self):
        """Handle play/pause button click."""
        self.playPauseRequested.emit()

    def on_slider_pressed(self):
        """Handle slider press (start seeking)."""
        self._seeking = True

    def on_slider_moved(self, value):
        """Handle slider movement (update time label while seeking)."""
        if self.total_duration > 0:
            position = value / 1000.0  # 0.0 to 1.0
            time_seconds = position * self.total_duration
            self.current_time_label.setText(self._format_time(time_seconds))

    def on_slider_released(self):
        """Handle slider release (emit seek signal)."""
        self._seeking = False
        position = self.timeline_slider.value() / 1000.0  # 0.0 to 1.0
        self.seekRequested.emit(position)

    def set_playing(self, playing: bool):
        """Update play/pause button state."""
        self.is_playing = playing
        self.play_pause_btn.setText("⏸" if playing else "▶")
        self.play_pause_btn.setToolTip("Pause (Space)" if playing else "Play (Space)")

    def set_duration(self, duration_seconds: float):
        """Set total video duration."""
        self.total_duration = duration_seconds
        self.total_time_label.setText(self._format_time(duration_seconds))

    def update_position(self, time_seconds: float):
        """
        Update timeline position.

        Args:
            time_seconds: Current playback time in seconds
        """
        self.current_time = time_seconds

        # Update time label
        self.current_time_label.setText(self._format_time(time_seconds))

        # Update slider (only if not currently seeking)
        if not self._seeking and self.total_duration > 0:
            position = time_seconds / self.total_duration
            slider_value = int(position * 1000)
            self.timeline_slider.blockSignals(True)  # Prevent triggering seek
            self.timeline_slider.setValue(slider_value)
            self.timeline_slider.blockSignals(False)

    def show_for_file(self):
        """Show timeline (called when file is loaded)."""
        self.setVisible(True)
        self.set_playing(True)
        self.timeline_slider.setValue(0)
        self.current_time_label.setText("00:00")

    def hide_for_stream(self):
        """Hide timeline (called for live streams)."""
        self.setVisible(False)

    def reset(self):
        """Reset timeline to initial state."""
        self.is_playing = False
        self.total_duration = 0.0
        self.current_time = 0.0
        self._seeking = False
        self.timeline_slider.setValue(0)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")
        self.play_pause_btn.setText("▶")
        self.setVisible(False)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format time in seconds as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
