"""
GPSMapDialog - Dialog window for displaying GPS map visualization.

This dialog shows all image GPS locations as connected points on an interactive map.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QComboBox, QSlider
)
from PySide6.QtCore import Qt, Signal, QPointF, QTimer
from helpers.TranslationMixin import TranslationMixin
from PySide6.QtGui import QKeySequence, QShortcut, QColor
from core.views.images.viewer.widgets.GPSMapView import GPSMapView


class GPSMapDialog(TranslationMixin, QDialog):
    """
    Dialog window containing the GPS map visualization.

    Displays GPS points for all images, connects them chronologically,
    and allows interactive navigation.
    """

    # Signal emitted when an image is selected from the map
    image_selected = Signal(int)

    # Signal emitted when user right-clicks on the map (lat, lon)
    gps_right_clicked = Signal(float, float)

    # Signal emitted when the POD overlay display changes (enabled, mode, opacity 0-100)
    pod_display_changed = Signal(bool, str, int)

    # Signal emitted when the user requests a DEM/canopy tile download for the mission
    canopy_download_requested = Signal()

    # Signal emitted when the user requests the POD coverage calculation
    pod_calculate_requested = Signal()

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

        self.setWindowTitle(self.tr("GPS Map View"))
        self.setModal(False)  # Non-modal so user can interact with main window

        # Use Qt.Tool so the dialog floats above its parent viewer but not
        # above unrelated OS apps, and so modal children of the viewer (e.g.
        # comment/creation dialogs) are not covered by the map.
        self.setWindowFlags(self.windowFlags() | Qt.Tool)

        self.resize(800, 600)

        self.setup_ui()
        self._apply_translations()
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
        self.map_view.gps_right_clicked.connect(self.gps_right_clicked.emit)

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
        self.zoom_in_btn = QPushButton(self.tr("Zoom In (+)"))
        self.zoom_in_btn.clicked.connect(self.map_view.zoom_in)
        controls_layout.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton(self.tr("Zoom Out (-)"))
        self.zoom_out_btn.clicked.connect(self.map_view.zoom_out)
        controls_layout.addWidget(self.zoom_out_btn)

        self.fit_btn = QPushButton(self.tr("Fit All (F)"))
        self.fit_btn.clicked.connect(self.map_view.fit_all_points)
        controls_layout.addWidget(self.fit_btn)

        self.rotate_btn = QPushButton(self.tr("Rotate (R)"))
        self.rotate_btn.clicked.connect(self.map_view.toggle_rotation)
        controls_layout.addWidget(self.rotate_btn)

        # Add separator
        controls_layout.addSpacing(20)

        # Toggle map/satellite view button
        self.toggle_view_btn = QPushButton(self.tr("Satellite View"))
        self.toggle_view_btn.setCheckable(True)
        self.toggle_view_btn.toggled.connect(self.on_toggle_view)
        controls_layout.addWidget(self.toggle_view_btn)

        # POD coverage overlay controls (enabled once a POD result is cached).
        controls_layout.addSpacing(20)
        self.pod_toggle_btn = QPushButton(self.tr("POD Overlay"))
        self.pod_toggle_btn.setCheckable(True)
        self.pod_toggle_btn.setEnabled(False)
        self.pod_toggle_btn.setToolTip(self.tr(
            "Run a map export with the POD option to generate this overlay"))
        self.pod_toggle_btn.toggled.connect(self._emit_pod_display_changed)
        controls_layout.addWidget(self.pod_toggle_btn)

        self.pod_mode_combo = QComboBox()
        self.pod_mode_combo.addItem(self.tr("POD (beta)"), "pod")   # itemData = stable key
        self.pod_mode_combo.addItem(self.tr("Look count"), "looks")
        self.pod_mode_combo.addItem(self.tr("Canopy height"), "canopy")
        self.pod_mode_combo.setEnabled(False)
        self.pod_mode_combo.currentIndexChanged.connect(self._emit_pod_display_changed)
        controls_layout.addWidget(self.pod_mode_combo)

        self.pod_opacity_slider = QSlider(Qt.Horizontal)
        self.pod_opacity_slider.setRange(0, 100)
        self.pod_opacity_slider.setValue(70)
        self.pod_opacity_slider.setFixedWidth(110)
        self.pod_opacity_slider.setEnabled(False)
        self.pod_opacity_slider.setToolTip(self.tr("POD overlay opacity"))
        self.pod_opacity_slider.valueChanged.connect(self._on_pod_opacity_changed)
        controls_layout.addWidget(self.pod_opacity_slider)

        # Download elevation/canopy tiles for this mission's footprint. Needs the
        # network, so it is disabled in Offline Only mode (see _apply_canopy_fetch_enabled).
        self.canopy_fetch_btn = QPushButton(self.tr("Download Canopy Tiles"))
        self.canopy_fetch_btn.clicked.connect(self.canopy_download_requested.emit)
        controls_layout.addWidget(self.canopy_fetch_btn)
        self._apply_canopy_fetch_enabled()

        # Compute the POD coverage raster for this mission without leaving the
        # map: it feeds the POD / Look count overlay modes above.
        self.pod_calc_btn = QPushButton(self.tr("Calculate POD"))
        self.pod_calc_btn.setToolTip(self.tr(
            "Compute the terrain-aware probability-of-detection heatmap for this "
            "mission (may take several minutes)"))
        self.pod_calc_btn.clicked.connect(self.pod_calculate_requested.emit)
        controls_layout.addWidget(self.pod_calc_btn)

        controls_layout.addStretch()

        # Help text
        help_label = QLabel(self.tr("Click point to select • Drag to pan • Scroll to zoom"))
        help_label.setStyleSheet("font-size: 10px; color: gray;")
        controls_layout.addWidget(help_label)

        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def set_pod_available(self, available):
        """Enable/disable the POD overlay controls based on a cached result."""
        self.set_overlay_availability(available, getattr(self, '_canopy_available', False))

    def set_overlay_availability(self, pod_available, canopy_available):
        """Gate the overlay controls: the POD/look-count modes need a cached POD
        result, while the canopy mode only needs a configured canopy source."""
        self._pod_available = bool(pod_available)
        self._canopy_available = bool(canopy_available)
        any_available = self._pod_available or self._canopy_available

        model = self.pod_mode_combo.model()
        for i in range(self.pod_mode_combo.count()):
            item = model.item(i)
            if item is not None:
                key = self.pod_mode_combo.itemData(i)
                item.setEnabled(self._canopy_available if key == 'canopy'
                                else self._pod_available)

        # If the current mode just became unavailable, hop to the first enabled one.
        cur = model.item(self.pod_mode_combo.currentIndex())
        if cur is None or not cur.isEnabled():
            for i in range(self.pod_mode_combo.count()):
                item = model.item(i)
                if item is not None and item.isEnabled():
                    self.pod_mode_combo.setCurrentIndex(i)
                    break

        self.pod_toggle_btn.setEnabled(any_available)
        self.pod_mode_combo.setEnabled(any_available and self.pod_toggle_btn.isChecked())
        self.pod_opacity_slider.setEnabled(any_available and self.pod_toggle_btn.isChecked())
        if not any_available and self.pod_toggle_btn.isChecked():
            self.pod_toggle_btn.setChecked(False)

    def activate_pod_overlay(self, mode='pod'):
        """Programmatically turn the overlay on after a Calculate POD run.

        Marks POD available, selects ``mode`` (if that mode is enabled), and
        checks the toggle so the button, dropdown, and slider all reflect the
        active overlay — not just the map. The overlay is painted by the
        resulting ``pod_display_changed`` emission, keeping the widgets the
        single source of truth (the bug this fixes: the map showed the overlay
        while the controls stayed inert).
        """
        self.set_pod_available(True)
        model = self.pod_mode_combo.model()
        idx = self.pod_mode_combo.findData(mode)
        if idx >= 0 and model.item(idx) is not None and model.item(idx).isEnabled():
            # Switch mode without a mid-way emit; the toggle below emits once.
            self.pod_mode_combo.blockSignals(True)
            self.pod_mode_combo.setCurrentIndex(idx)
            self.pod_mode_combo.blockSignals(False)
        if self.pod_toggle_btn.isChecked():
            # Already on (re-activation) — no toggled signal will fire, so emit
            # explicitly to repaint with the (possibly new) mode.
            self._emit_pod_display_changed()
        else:
            self.pod_toggle_btn.setChecked(True)  # -> toggled -> _emit_pod_display_changed

    def _emit_pod_display_changed(self):
        enabled = self.pod_toggle_btn.isChecked()
        self.pod_mode_combo.setEnabled(enabled and self.pod_toggle_btn.isEnabled())
        self.pod_opacity_slider.setEnabled(enabled and self.pod_toggle_btn.isEnabled())
        self.pod_display_changed.emit(enabled, self.pod_mode_combo.currentData(),
                                      self.pod_opacity_slider.value())

    def _on_pod_opacity_changed(self, value):
        # Opacity is pure view state -> update the view directly (no recompute).
        self.map_view.set_pod_overlay_opacity(value / 100.0)

    def _apply_canopy_fetch_enabled(self):
        """Gate the download button: fetching tiles needs the network, so it is
        disabled while Offline Only is on (with an explanatory tooltip)."""
        if not hasattr(self, 'canopy_fetch_btn'):
            return
        self.canopy_fetch_btn.setEnabled(not self.offline_only)
        self.canopy_fetch_btn.setToolTip(
            self.tr("Downloading tiles is disabled in Offline Only mode")
            if self.offline_only
            else self.tr("Download elevation and canopy-height tiles for this mission's area"))

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

        # Rotate (toggle north-up / bearing-aligned). Registered at the dialog
        # level so the shortcut fires regardless of which child widget has focus.
        QShortcut(QKeySequence(Qt.Key.Key_R), self, self.map_view.toggle_rotation)

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
            self.toggle_view_btn.setText(self.tr("Map View"))
            self.map_view.set_tile_source('satellite')
        else:
            self.toggle_view_btn.setText(self.tr("Satellite View"))
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
        self.status_label.setText(self.tr("⚠ {error}").format(error=error_msg))
        self.status_label.setVisible(True)

        # Auto-hide after 10 seconds
        self.status_timer.start(10000)

        # For critical errors (rate limiting), also show a dialog
        if "rate limit" in error_msg.lower() or "access denied" in error_msg.lower():
            QMessageBox.warning(
                self,
                self.tr("Map Tile Loading Issue"),
                self.tr(
                    "{error}\n\nThe map will continue to work with cached tiles where available."
                ).format(error=error_msg),
                QMessageBox.StandardButton.Ok
            )

    def set_offline_mode(self, offline_only: bool):
        """Update offline mode on the map view."""
        self.offline_only = bool(offline_only)
        if hasattr(self, "map_view"):
            self.map_view.set_offline_mode(self.offline_only)
        self._apply_canopy_fetch_enabled()

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

    def update_zoom_fov(self, visible_rect):
        """
        Update the zoom FOV box on the map.

        Args:
            visible_rect: QRectF in image pixel coordinates, or None to clear.
        """
        self.map_view.update_zoom_fov_box(visible_rect)
