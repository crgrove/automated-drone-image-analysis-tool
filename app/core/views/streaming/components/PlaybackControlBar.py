"""
PlaybackControlBar - Advanced video playback controls.

Provides comprehensive playback controls including play/pause, seek,
and timeline scrubbing for video file playback.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PySide6.QtCore import Qt, Signal


class PlaybackControlBar(QWidget):
    """
    Advanced playback control bar for video files.

    Provides play/pause, seek controls, and timeline display.
    Combines functionality of basic timeline with additional controls.
    """

    # Signals
    playPauseToggled = Signal()
    seekRequested = Signal(float)  # Seek to time in seconds

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

        # State
        self.is_playing = False
        self.total_duration = 0.0
        self.current_time = 0.0
        self._seeking = False

        # Hide by default
        self.setVisible(False)

    def setup_ui(self):
        """Setup the control bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Play/Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(50, 40)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                font-size: 20pt;
                font-weight: bold;
            }
        """)
        self.play_pause_btn.setToolTip("Play/Pause (Space)")
        layout.addWidget(self.play_pause_btn)

        # Current time
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setFixedWidth(50)
        self.current_time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.current_time_label)

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1000)
        self.timeline_slider.setValue(0)
        self.timeline_slider.setToolTip("Seek through video")
        layout.addWidget(self.timeline_slider, 1)

        # Total duration
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
        self.playPauseToggled.emit()

    def on_slider_pressed(self):
        """Handle slider press."""
        self._seeking = True

    def on_slider_moved(self, value):
        """Handle slider movement."""
        if self.total_duration > 0:
            position = value / 1000.0
            time_seconds = position * self.total_duration
            self.current_time_label.setText(self._format_time(time_seconds))

    def on_slider_released(self):
        """Handle slider release."""
        self._seeking = False
        if self.total_duration > 0:
            position = self.timeline_slider.value() / 1000.0
            time_seconds = position * self.total_duration
            self.seekRequested.emit(time_seconds)

    def update_play_state(self, playing: bool):
        """Update play/pause button state."""
        self.is_playing = playing
        self.play_pause_btn.setText("⏸" if playing else "▶")

    def update_time(self, current_seconds: float, total_seconds: float):
        """Update time display and slider."""
        self.current_time = current_seconds
        self.total_duration = total_seconds

        # Update labels
        self.current_time_label.setText(self._format_time(current_seconds))
        self.total_time_label.setText(self._format_time(total_seconds))

        # Update slider (only if not seeking)
        if not self._seeking and total_seconds > 0:
            position = current_seconds / total_seconds
            slider_value = int(position * 1000)
            self.timeline_slider.blockSignals(True)
            self.timeline_slider.setValue(slider_value)
            self.timeline_slider.blockSignals(False)

    def show_for_file(self):
        """Show controls for file playback."""
        self.setVisible(True)
        self.update_play_state(True)

    def hide_for_stream(self):
        """Hide controls for live stream."""
        self.setVisible(False)

    def reset(self):
        """Reset to initial state."""
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
        """Format seconds as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
