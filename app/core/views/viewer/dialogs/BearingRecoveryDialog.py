"""
BearingRecoveryDialog - UI for recovering missing image bearings.

Presents user with options to:
1. Load a track file (KML/GPX/CSV)
2. Auto-calculate from image GPS
3. Skip bearing recovery
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFileDialog, QMessageBox, QWidget, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from core.services.BearingCalculationService import BearingCalculationService, BearingResult
from core.services.LoggerService import LoggerService


class BearingCalculationWorker(QThread):
    """Worker thread for bearing calculation to avoid blocking UI."""

    finished = Signal(dict)  # results
    error = Signal(str)
    progress = Signal(int, int, str)
    cancelled = Signal()

    def __init__(self, service: BearingCalculationService, mode: str, images: List[Dict[str, Any]], track_file: Optional[str] = None):
        super().__init__()
        self.service = service
        self.mode = mode
        self.images = images
        self.track_file = track_file

    def run(self):
        """Run bearing calculation in background thread."""
        # Connect signals
        self.service.progress_updated.connect(self.progress.emit)
        self.service.calculation_complete.connect(self.finished.emit)
        self.service.calculation_error.connect(self.error.emit)
        self.service.calculation_cancelled.connect(self.cancelled.emit)

        # Start calculation
        if self.mode == 'track':
            self.service.calculate_from_track(self.images, self.track_file)
        elif self.mode == 'auto':
            self.service.calculate_auto(self.images)


class BearingRecoveryDialog(QDialog):
    """
    Dialog for recovering missing image bearings.

    Allows user to:
    - Load external track file (KML/GPX/CSV)
    - Auto-calculate from image GPS
    - Skip recovery
    """

    def __init__(self, parent=None, images: List[Dict[str, Any]] = None):
        super().__init__(parent)
        self.images = images or []
        self.results: Optional[Dict[str, BearingResult]] = None
        self.service = BearingCalculationService()
        self.worker: Optional[BearingCalculationWorker] = None
        self._logger = LoggerService()

        self.setWindowTitle("Missing Bearings Detected")
        self.setModal(True)
        self.setMinimumWidth(500)

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title and description
        title_label = QLabel("Missing Bearings Detected")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        desc_label = QLabel(
            "Some images are missing bearing/heading information. "
            "We can estimate bearings from a flight track file (KML/GPX/CSV) "
            "or calculate them automatically from image GPS coordinates."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Mode selection buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)

        # Track file button
        self.track_button = QPushButton("📁 Load Track File (KML/GPX/CSV)")
        self.track_button.setMinimumHeight(50)
        self.track_button.clicked.connect(self._on_load_track)
        button_layout.addWidget(self.track_button)

        # Auto-calculate button
        self.auto_button = QPushButton("🧭 Auto-Calculate from Image GPS")
        self.auto_button.setMinimumHeight(50)
        self.auto_button.clicked.connect(self._on_auto_calculate)
        button_layout.addWidget(self.auto_button)

        layout.addLayout(button_layout)

        # Help link
        help_label = QLabel('<a href="#" style="color: #6ab0de;">What\'s this?</a>')
        help_label.setOpenExternalLinks(False)
        help_label.linkActivated.connect(self._show_help)
        layout.addWidget(help_label)

        # Progress section (hidden initially)
        self.progress_widget = QWidget()
        progress_layout = QVBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)

        self.progress_label = QLabel("Preparing...")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.progress_widget.setVisible(False)
        layout.addWidget(self.progress_widget)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        self.cancel_button.setVisible(False)
        bottom_layout.addWidget(self.cancel_button)

        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.reject)
        bottom_layout.addWidget(self.skip_button)

        layout.addLayout(bottom_layout)

    def _apply_styles(self):
        """Apply custom styles matching application theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 10px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border: 1px solid #6ab0de;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #777777;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #6ab0de;
                border-radius: 3px;
            }
            QFrame {
                color: #555555;
            }
        """)

    def _on_load_track(self):
        """Handle load track file button click."""
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Track File",
            "",
            "Track Files (*.kml *.gpx *.csv);;KML Files (*.kml);;GPX Files (*.gpx);;CSV Files (*.csv);;All Files (*.*)"
        )

        if file_path:
            self._start_calculation('track', track_file=file_path)

    def _on_auto_calculate(self):
        """Handle auto-calculate button click."""
        # Skip pre-validation - let the service extract GPS and validate
        # This allows deferred GPS extraction for better performance
        self._start_calculation('auto')

    def _start_calculation(self, mode: str, track_file: Optional[str] = None):
        """Start bearing calculation in background thread."""
        # Hide mode selection, show progress
        self.track_button.setEnabled(False)
        self.auto_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.progress_widget.setVisible(True)
        self.cancel_button.setVisible(True)

        # Create worker thread
        self.worker = BearingCalculationWorker(self.service, mode, self.images, track_file)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_calculation_complete)
        self.worker.error.connect(self._on_calculation_error)
        self.worker.cancelled.connect(self._on_calculation_cancelled)

        # Start calculation
        self.worker.start()

    def _on_progress(self, current: int, total: int, message: str):
        """Update progress bar."""
        self.progress_label.setText(f"{message} ({current}/{total})")
        progress_pct = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress_pct)

    def _on_calculation_complete(self, results: Dict[str, BearingResult]):
        """Handle successful calculation completion."""
        self.results = results

        # Count results by source and quality
        sources = {}
        qualities = {}
        for result in results.values():
            sources[result.source] = sources.get(result.source, 0) + 1
            qualities[result.quality] = qualities.get(result.quality, 0) + 1

        # Build summary message
        source_names = {
            'kml': 'KML', 'gpx': 'GPX', 'csv': 'CSV',
            'auto_prev_next': 'Auto', 'auto_prev_leg': 'Auto', 'auto_next_leg': 'Auto'
        }
        primary_source = max(sources.keys(), key=lambda k: sources[k])
        source_display = source_names.get(primary_source, primary_source.upper())

        turns_flagged = qualities.get('turn_inferred', 0)
        hover_estimates = qualities.get('hover_estimate', 0)
        gaps = qualities.get('gap', 0)

        summary = f"Bearings set for {len(results)} images ({source_display})"
        if turns_flagged > 0:
            summary += f", {turns_flagged} flagged near turns"
        if hover_estimates > 0:
            summary += f", {hover_estimates} hover estimates"
        if gaps > 0:
            summary += f", {gaps} time gaps"

        self._logger.info(summary)

        # Show completion message
        QMessageBox.information(
            self,
            "Bearing Calculation Complete",
            summary + "."
        )

        # Accept dialog
        self.accept()

    def _on_calculation_error(self, error_msg: str):
        """Handle calculation error."""
        self._logger.error(f"Bearing calculation failed: {error_msg}")

        # Reset UI
        self.track_button.setEnabled(True)
        self.auto_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        self.progress_widget.setVisible(False)
        self.cancel_button.setVisible(False)

        # Show error message
        QMessageBox.critical(
            self,
            "Bearing Calculation Failed",
            f"An error occurred during bearing calculation:\n\n{error_msg}\n\n"
            "Please check your input files and try again."
        )

    def _on_calculation_cancelled(self):
        """Handle calculation cancellation."""
        self._logger.info("Bearing calculation cancelled by user")

        # Reset UI
        self.track_button.setEnabled(True)
        self.auto_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        self.progress_widget.setVisible(False)
        self.cancel_button.setVisible(False)

        self.progress_label.setText("Cancelled")

    def _on_cancel(self):
        """Handle cancel button click during calculation."""
        if self.worker and self.worker.isRunning():
            self.service.cancel()
            self.cancel_button.setEnabled(False)
            self.progress_label.setText("Cancelling...")

    def _show_help(self):
        """Show help dialog explaining bearing recovery."""
        help_text = """
<h3>What is Bearing Recovery?</h3>

<p><b>Bearing</b> (also called heading, yaw, or course) is the direction the drone/camera
was pointing when an image was captured, measured in degrees clockwise from North (0-360°).</p>

<h4>Why is it important?</h4>
<p>Bearings are essential for:</p>
<ul>
<li>Accurate georeferencing and mapping</li>
<li>Proper image alignment and stitching</li>
<li>Understanding camera field of view</li>
<li>Analysis of detected objects in geographic context</li>
</ul>

<h4>Recovery Methods:</h4>

<p><b>Load Track File (KML/GPX/CSV)</b><br/>
Uses an external GPS track log from your drone or flight controller. The track contains
timestamped positions that allow precise bearing interpolation. Most accurate method.</p>

<p><b>Auto-Calculate from Image GPS</b><br/>
Estimates bearings using only the GPS coordinates embedded in your images. Analyzes the
flight pattern to determine direction of travel. Works well for systematic flight patterns
like lawn-mower surveys.</p>

<p><b>Skip</b><br/>
Proceed without bearing recovery. Some features may not work correctly.</p>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("About Bearing Recovery")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def get_results(self) -> Optional[Dict[str, BearingResult]]:
        """Get calculation results after dialog is accepted."""
        return self.results
