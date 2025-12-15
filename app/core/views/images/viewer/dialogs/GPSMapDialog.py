"""
GPSMapDialog - Dialog window for displaying GPS map visualization.

This dialog shows all image GPS locations as connected points on an interactive map.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, Signal, QPointF, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QColor
from core.views.images.viewer.widgets.GPSMapView import GPSMapView


class GPSMapDialog(QDialog):
    """
    Dialog window containing the GPS map visualization.

    Displays GPS points for all images, connects them chronologically,
    and allows interactive navigation.
    """

    # Signal emitted when an image is selected from the map
    image_selected = Signal(int)

    def __init__(self, parent, gps_data, current_image_index, offline_only=False):
        """
        Initialize the GPS map dialog.

        Args:
            parent: Parent widget (main viewer)
            gps_data: List of GPS data dictionaries
            current_image_index: Currently selected image index
        """
        super().__init__(parent)
        self.gps_data = gps_data
        self.current_image_index = current_image_index
        self.offline_only = bool(offline_only)

        self.setWindowTitle("GPS Map View")
        self.setModal(False)  # Non-modal so user can interact with main window

        # Set window flags to keep dialog on top (especially important on macOS)
        # Use WindowStaysOnTopHint to keep it visible when clicking on parent window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.resize(800, 600)

        self.setup_ui()
        self.setup_shortcuts()

        # Get AOI color from parent if available
        self.aoi_color = self.get_aoi_color()

        # Initialize map view with data
        self.map_view.set_gps_data(gps_data, current_image_index, self.aoi_color)

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()

        # Add info label at top
        self.info_label = QLabel(f"Showing {len(self.gps_data)} GPS locations")
        self.info_label.setStyleSheet("padding: 5px; font-size: 11px;")
        layout.addWidget(self.info_label)

        # Create and add map view
        self.map_view = GPSMapView(self, offline_only=self.offline_only)
        self.map_view.point_clicked.connect(self.on_point_clicked)

        # Connect to tile error signals
        self.map_view.tile_loader.tile_error.connect(self.on_tile_error)

        # Status label for tile loading errors
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: orange; padding: 2px; font-size: 10px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        layout.addWidget(self.map_view)

        # Timer to auto-hide status messages
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(lambda: self.status_label.setVisible(False))

        # Add control buttons at bottom
        controls_layout = QHBoxLayout()

        # Zoom controls
        self.zoom_in_btn = QPushButton("Zoom In (+)")
        self.zoom_in_btn.clicked.connect(self.map_view.zoom_in)
        controls_layout.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton("Zoom Out (-)")
        self.zoom_out_btn.clicked.connect(self.map_view.zoom_out)
        controls_layout.addWidget(self.zoom_out_btn)

        self.fit_btn = QPushButton("Fit All (F)")
        self.fit_btn.clicked.connect(self.map_view.fit_all_points)
        controls_layout.addWidget(self.fit_btn)

        # Add separator
        controls_layout.addSpacing(20)

        # Toggle map/satellite view button
        self.toggle_view_btn = QPushButton("Satellite View")
        self.toggle_view_btn.setCheckable(True)
        self.toggle_view_btn.toggled.connect(self.on_toggle_view)
        controls_layout.addWidget(self.toggle_view_btn)

        controls_layout.addStretch()

        # Help text
        help_label = QLabel("Click point to select • Drag to pan • Scroll to zoom")
        help_label.setStyleSheet("font-size: 10px; color: gray;")
        controls_layout.addWidget(help_label)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # ESC to close
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

        # Zoom shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Plus), self, self.map_view.zoom_in)
        QShortcut(QKeySequence(Qt.Key.Key_Minus), self, self.map_view.zoom_out)
        QShortcut(QKeySequence(Qt.Key.Key_Equal), self, self.map_view.zoom_in)  # For + without shift

        # Fit all
        QShortcut(QKeySequence(Qt.Key.Key_F), self, self.map_view.fit_all_points)

        # Arrow keys for panning
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, lambda: self.map_view.pan(-50, 0))
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, lambda: self.map_view.pan(50, 0))
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, lambda: self.map_view.pan(0, -50))
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, lambda: self.map_view.pan(0, 50))

    def get_aoi_color(self):
        """
        Get the AOI highlight color from the parent viewer.

        Returns:
            QColor object for the AOI highlight color
        """
        # Default to orange if not available
        default_color = QColor(255, 140, 0)

        try:
            # Try to get from current image's AOI if it exists
            if hasattr(self.parent(), 'images') and hasattr(self.parent(), 'current_image'):
                current_img = self.parent().images[self.parent().current_image]
                if 'areas_of_interest' in current_img and current_img['areas_of_interest']:
                    # Could extract actual AOI color if stored, for now use orange
                    return default_color
        except (KeyError, IndexError, TypeError):
            pass

        return default_color

    def on_point_clicked(self, image_index):
        """
        Handle click on a GPS point.

        Args:
            image_index: Original image index from the viewer's image list
        """
        self.image_selected.emit(image_index)
        # Find the gps_data list index for this image
        for i, data in enumerate(self.gps_data):
            if data['index'] == image_index:
                self.current_image_index = i
                self.map_view.set_current_image(i)
                break

    def on_toggle_view(self, checked):
        """
        Toggle between map and satellite view.

        Args:
            checked: True for satellite view, False for map view
        """
        if checked:
            self.toggle_view_btn.setText("Map View")
            self.map_view.set_tile_source('satellite')
        else:
            self.toggle_view_btn.setText("Satellite View")
            self.map_view.set_tile_source('map')

    def update_gps_data(self, gps_data, current_image_index):
        """
        Update the map with new GPS data.

        Args:
            gps_data: Updated list of GPS data dictionaries
            current_image_index: New current image index
        """
        self.gps_data = gps_data
        self.current_image_index = current_image_index
        self.info_label.setText(f"Showing {len(gps_data)} GPS locations")
        self.map_view.set_gps_data(gps_data, current_image_index, self.aoi_color)

    def set_current_image(self, gps_list_index):
        """
        Update the currently highlighted image.

        Args:
            gps_list_index: Index in the gps_data list of the image to highlight
        """
        self.current_image_index = gps_list_index
        self.map_view.set_current_image(gps_list_index)

    def on_tile_error(self, error_msg):
        """
        Handle tile loading errors.

        Args:
            error_msg: Error message to display
        """
        # Show status message
        self.status_label.setText(f"⚠ {error_msg}")
        self.status_label.setVisible(True)

        # Auto-hide after 10 seconds
        self.status_timer.start(10000)

        # For critical errors (rate limiting), also show a dialog
        if "rate limit" in error_msg.lower() or "access denied" in error_msg.lower():
            QMessageBox.warning(
                self,
                "Map Tile Loading Issue",
                f"{error_msg}\n\nThe map will continue to work with cached tiles where available.",
                QMessageBox.StandardButton.Ok
            )

    def set_offline_mode(self, offline_only: bool):
        """Update offline mode on the map view."""
        self.offline_only = bool(offline_only)
        if hasattr(self, "map_view"):
            self.map_view.set_offline_mode(self.offline_only)

    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        # Fit all points when shown (viewport is now valid)
        self.map_view.fit_all_points()
        # Compass will be created automatically in map view's resize/paint events

    def update_aoi_marker(self, aoi_gps_data, identifier_color):
        """
        Update the AOI marker on the map.

        Args:
            aoi_gps_data: Dict with AOI GPS data or None to clear
            identifier_color: List [r, g, b] for the marker color
        """
        if aoi_gps_data:
            self.map_view.set_aoi_marker(aoi_gps_data, identifier_color)
        else:
            self.map_view.clear_aoi_marker()
