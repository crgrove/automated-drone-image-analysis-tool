"""MeasureDialog controller for distance measurement functionality."""

import math
from PySide6.QtCore import Qt, QPointF, Signal
from helpers.TranslationMixin import TranslationMixin
from PySide6.QtGui import QPen, QColor, QFont, QBrush
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QCheckBox
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPolygonItem
from PySide6.QtGui import QPolygonF

from core.services.shadow.ShadowHeightEstimator import ShadowHeightEstimator


class MeasureDialog(TranslationMixin, QDialog):
    """Dialog for measuring distances on images using GSD (Ground Sample Distance)."""

    gsdChanged = Signal(float)

    def __init__(self, parent, image_viewer, current_gsd, distance_unit):
        """Initialize the measure dialog.

        Args:
            parent: Parent widget (Viewer)
            image_viewer: QtImageViewer instance
            current_gsd: Current GSD value in cm/px (if any)
            distance_unit: User's preferred distance unit ('m' or 'ft')
        """
        super().__init__(parent)
        self.image_viewer = image_viewer
        self.distance_unit = distance_unit
        self.current_gsd = current_gsd

        # Measurement state
        self.first_point = None
        self.second_point = None
        self.measuring = False

        # Shadow-measurement state (additive — coexists with regular measurement
        # so toggling the checkbox doesn't lose graphics)
        self.shadow_mode = False
        self.shadow_estimator = None  # Lazy-init on first shadow measurement
        self.shadow_graphics = []  # All shadow-related QGraphics items, for bulk removal

        # Graphics items
        self.line_item = None
        self.point1_item = None
        self.point2_item = None
        self.temp_line_item = None
        self.distance_text_item = None

        # Fixed screen sizes (in pixels)
        self.fixed_point_radius = 5  # Radius in screen pixels
        self.fixed_line_width = 2    # Line width in screen pixels

        # Store original viewer settings and disable zoom/pan during measurement
        self.original_can_zoom = self.image_viewer.canZoom
        self.original_can_pan = self.image_viewer.canPan
        self.original_region_zoom_button = self.image_viewer.regionZoomButton

        # Disable zoom functionality to allow measurement clicks
        self.image_viewer.canZoom = False
        self.image_viewer.canPan = False
        self.image_viewer.regionZoomButton = None

        self.setupUi()
        self.connectSignals()
        self._apply_translations()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle(self.tr("Measure Distance"))
        self.setModal(False)

        # Set window flags to keep dialog on top (especially important on macOS)
        # Use WindowStaysOnTopHint to keep it visible when clicking on parent window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.setMinimumWidth(320)

        # Main layout
        layout = QVBoxLayout()

        # Mode toggle — drives whether the two clicks measure a length or
        # estimate an object's height from its shadow.
        self.shadow_mode_checkbox = QCheckBox(self.tr("Measure Shadow"))
        self.shadow_mode_checkbox.setToolTip(self.tr(
            "When checked, the two clicks estimate the height of a vertical "
            "object from its shadow. Click the base of the object first, "
            "then the tip of its shadow."
        ))
        layout.addWidget(self.shadow_mode_checkbox)

        # GSD input group
        self.gsd_group = QGroupBox(self.tr("Ground Sample Distance"))
        gsd_layout = QHBoxLayout()

        gsd_label = QLabel(self.tr("GSD:"))
        self.gsd_input = QLineEdit()
        self.gsd_input.setPlaceholderText(self.tr("Enter GSD value"))
        if self.current_gsd:
            self.gsd_input.setText(str(self.current_gsd))

        gsd_unit_label = QLabel(self.tr("cm/px"))

        gsd_layout.addWidget(gsd_label)
        gsd_layout.addWidget(self.gsd_input)
        gsd_layout.addWidget(gsd_unit_label)
        self.gsd_group.setLayout(gsd_layout)

        # Distance display group
        self.distance_group = QGroupBox(self.tr("Measurement"))
        distance_layout = QHBoxLayout()

        distance_label = QLabel(self.tr("Distance:"))
        self.distance_display = QLabel(self.tr("--"))
        self.distance_display.setStyleSheet("QLabel { font-weight: bold; font-size: 14pt; }")

        distance_layout.addWidget(distance_label)
        distance_layout.addWidget(self.distance_display)
        distance_layout.addStretch()
        self.distance_group.setLayout(distance_layout)

        # Shadow-height result group (hidden until shadow mode is on)
        self.shadow_group = QGroupBox(self.tr("Shadow Height Estimate"))
        shadow_layout = QVBoxLayout()
        self.shadow_height_display = QLabel(self.tr("--"))
        self.shadow_height_display.setStyleSheet("QLabel { font-weight: bold; font-size: 14pt; }")
        self.shadow_details = QLabel("")
        self.shadow_details.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        self.shadow_details.setWordWrap(True)
        self.shadow_warnings = QLabel("")
        self.shadow_warnings.setStyleSheet("QLabel { color: #b8860b; font-size: 9pt; }")
        self.shadow_warnings.setWordWrap(True)
        # "Use anyway" override appears only on an azimuth-band rejection.
        self.shadow_override_button = QPushButton(self.tr("Use Anyway"))
        self.shadow_override_button.setToolTip(self.tr(
            "Force the estimate with the current base/tip clicks even though "
            "the drawn line doesn't match the expected shadow direction. "
            "Use only when you're confident the geometry is correct."
        ))
        self.shadow_override_button.setVisible(False)
        self.shadow_override_button.clicked.connect(self._on_shadow_override_clicked)
        shadow_layout.addWidget(self.shadow_height_display)
        shadow_layout.addWidget(self.shadow_details)
        shadow_layout.addWidget(self.shadow_warnings)
        shadow_layout.addWidget(self.shadow_override_button)
        self.shadow_group.setLayout(shadow_layout)
        self.shadow_group.setVisible(False)

        # Instructions — text swaps with mode.
        self.instructions = QLabel("")
        self.instructions.setWordWrap(True)
        self.instructions.setStyleSheet("QLabel { color: gray; }")
        self._update_instructions_text()

        # Buttons
        button_layout = QHBoxLayout()
        self.clear_button = QPushButton(self.tr("Clear"))
        self.clear_button.clicked.connect(self.clearMeasurement)
        self.close_button = QPushButton(self.tr("Close"))
        self.close_button.clicked.connect(self.close)

        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        # Add all to main layout
        layout.addWidget(self.gsd_group)
        layout.addWidget(self.distance_group)
        layout.addWidget(self.shadow_group)
        layout.addWidget(self.instructions)
        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def _update_instructions_text(self):
        """Refresh the instruction copy for the active measurement mode."""
        if self.shadow_mode:
            self.instructions.setText(self.tr(
                "Click the BASE of the object first, then the TIP of its shadow."
            ))
        else:
            self.instructions.setText(self.tr(
                "Click on the image to place the first point,\n"
                "then click again to place the second point."
            ))

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, non-modal dialogs with WindowStaysOnTopHint need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the GSD input field so users can type immediately
        if hasattr(self, 'gsd_input'):
            self.gsd_input.setFocus()

    def connectSignals(self):
        """Connect signals and slots."""
        # Connect to image viewer mouse events
        self.image_viewer.leftMouseButtonPressed.connect(self.onImageClick)
        self.image_viewer.mousePositionOnImageChanged.connect(self.onMouseMove)

        # Connect GSD input
        self.gsd_input.textChanged.connect(self.onGsdChanged)

        # Connect to zoom changes to update item sizes
        self.image_viewer.zoomChanged.connect(self.onZoomChanged)

        # Shadow-mode toggle
        self.shadow_mode_checkbox.toggled.connect(self._on_shadow_mode_toggled)

        # Mouse tracking is already enabled in QtImageViewer

    def _on_shadow_mode_toggled(self, checked):
        """Switch the dialog between length and shadow-height modes.

        Toggling clears the current measurement and swaps which result
        groups are visible — keeps the GSD field and the shadow-result
        panel from being on screen at the same time.
        """
        self.shadow_mode = checked
        self.clearMeasurement()
        self.gsd_group.setVisible(not checked)
        self.distance_group.setVisible(not checked)
        self.shadow_group.setVisible(checked)
        self.setWindowTitle(self.tr("Measure Shadow Height") if checked else self.tr("Measure Distance"))
        self._update_instructions_text()

    def onGsdChanged(self, text):
        """Handle GSD value changes.

        Args:
            text: New text in the GSD input field
        """
        try:
            gsd_value = float(text)
            if gsd_value > 0:
                self.current_gsd = gsd_value
                self.gsdChanged.emit(gsd_value)
                # Recalculate distance if we have both points
                if self.first_point and self.second_point:
                    self.calculateDistance()
        except ValueError:
            pass  # Invalid input, ignore

    def onZoomChanged(self, zoom_level):
        """Handle zoom level changes to update item sizes.

        Args:
            zoom_level: Current zoom level
        """
        self.updateItemSizes()

    def onImageClick(self, x, y, viewer):
        """Handle mouse clicks on the image.

        Args:
            x: X coordinate in image space
            y: Y coordinate in image space
            viewer: The image viewer that was clicked
        """
        if viewer != self.image_viewer:
            return

        point = QPointF(x, y)
        zoom = self.image_viewer.getZoom() if hasattr(self.image_viewer, 'getZoom') else 1.0
        radius = self.fixed_point_radius / zoom
        pen_width = self.fixed_line_width / zoom

        if self.shadow_mode:
            # Gold for shadow base + tip; hollow circle on the tip helps
            # distinguish the two when zoomed out.
            colour = QColor(255, 215, 0)
            if not self.measuring:
                self.clearMeasurement()
                self.first_point = point
                self.measuring = True
                self.point1_item = self._make_point_marker(
                    x, y, radius, pen_width, fill=colour
                )
                self._add_shadow_label('B', x, y, radius, colour)
            else:
                self.second_point = point
                self.measuring = False
                if self.temp_line_item:
                    self.image_viewer.scene.removeItem(self.temp_line_item)
                    self.temp_line_item = None
                self.point2_item = self._make_point_marker(
                    x, y, radius, pen_width, fill=None, outline=colour
                )
                self._add_shadow_label('T', x, y, radius, colour)
                self.line_item = QGraphicsLineItem(
                    self.first_point.x(), self.first_point.y(),
                    self.second_point.x(), self.second_point.y()
                )
                self.line_item.setPen(QPen(colour, pen_width))
                self.image_viewer.scene.addItem(self.line_item)
                self._estimate_and_render_shadow_height(pen_width, colour)
            return

        if not self.measuring:
            # First click - place first point
            self.clearMeasurement()
            self.first_point = point
            self.measuring = True

            self.point1_item = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
            self.point1_item.setBrush(QColor(255, 0, 0))
            self.point1_item.setPen(QPen(QColor(255, 255, 255), pen_width))
            self.image_viewer.scene.addItem(self.point1_item)

        else:
            # Second click - place second point and complete measurement
            self.second_point = point
            self.measuring = False

            # Remove temporary line
            if self.temp_line_item:
                self.image_viewer.scene.removeItem(self.temp_line_item)
                self.temp_line_item = None

            self.point2_item = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
            self.point2_item.setBrush(QColor(255, 0, 0))
            self.point2_item.setPen(QPen(QColor(255, 255, 255), pen_width))
            self.image_viewer.scene.addItem(self.point2_item)

            # Draw final line
            self.line_item = QGraphicsLineItem(
                self.first_point.x(), self.first_point.y(),
                self.second_point.x(), self.second_point.y()
            )
            self.line_item.setPen(QPen(QColor(0, 255, 0), pen_width))
            self.image_viewer.scene.addItem(self.line_item)

            # Calculate and display distance
            self.calculateDistance()

    def _make_point_marker(self, x, y, radius, pen_width, fill=None, outline=None):
        """Create a circular marker on the image scene.

        Pass `fill` to make a filled disc (base point); pass only `outline`
        to make a hollow ring (shadow tip).
        """
        item = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
        if fill is not None:
            item.setBrush(fill)
            item.setPen(QPen(QColor(255, 255, 255), pen_width))
        else:
            item.setBrush(QBrush(Qt.NoBrush))
            item.setPen(QPen(outline or QColor(255, 215, 0), pen_width * 1.5))
        self.image_viewer.scene.addItem(item)
        return item

    def _add_shadow_label(self, letter, x, y, radius, colour):
        """Add a 'B' / 'T' glyph next to a shadow endpoint marker."""
        label = QGraphicsTextItem()
        label.setHtml(
            f'<div style="color: rgb({colour.red()},{colour.green()},{colour.blue()}); '
            f'font-weight: bold;">{letter}</div>'
        )
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        label.setFont(font)
        label.setPos(x + radius * 1.5, y - radius * 2.5)
        self.image_viewer.scene.addItem(label)
        self.shadow_graphics.append(label)

    def onMouseMove(self, pos):
        """Handle mouse movement for live line drawing.

        Args:
            pos: QPoint with mouse position in image coordinates
        """
        if self.measuring and self.first_point:
            # Update temporary line from first point to current mouse position
            if self.temp_line_item:
                self.image_viewer.scene.removeItem(self.temp_line_item)

            zoom = self.image_viewer.getZoom() if hasattr(self.image_viewer, 'getZoom') else 1.0
            pen_width = self.fixed_line_width / zoom

            colour = QColor(255, 215, 0) if self.shadow_mode else QColor(255, 255, 0)
            self.temp_line_item = QGraphicsLineItem(
                self.first_point.x(), self.first_point.y(),
                pos.x(), pos.y()
            )
            self.temp_line_item.setPen(QPen(colour, pen_width, Qt.DashLine))
            self.image_viewer.scene.addItem(self.temp_line_item)

    def _current_image_metadata(self):
        """Return the active image's metadata dict via the parent Viewer.

        Returns None when the viewer state is in transition (e.g. between
        image loads).
        """
        viewer = self.parent()
        if viewer is None:
            return None
        images = getattr(viewer, 'images', None)
        index = getattr(viewer, 'current_image', None)
        if images is None or index is None:
            return None
        try:
            return images[index]
        except (IndexError, TypeError):
            return None

    def _estimate_and_render_shadow_height(self, pen_width, colour, allow_azimuth_override=False):
        """Run the shadow-height estimator on the two clicks and update the UI."""
        image_dict = self._current_image_metadata()
        if image_dict is None or not image_dict.get('path'):
            self.shadow_height_display.setText(self.tr("Image metadata unavailable"))
            self.shadow_details.setText("")
            self.shadow_warnings.setText("")
            return

        if self.shadow_estimator is None:
            self.shadow_estimator = ShadowHeightEstimator()

        base_px = (self.first_point.x(), self.first_point.y())
        tip_px = (self.second_point.x(), self.second_point.y())
        # Honor the viewer's terrain-elevation preference (parent is the Viewer)
        use_terrain = bool(getattr(self.parent(), 'use_terrain_elevation', True))
        result = self.shadow_estimator.estimate(
            image_dict, base_px, tip_px,
            allow_azimuth_override=allow_azimuth_override,
            use_terrain=use_terrain,
        )

        self._render_shadow_result_in_dialog(result)
        self._render_shadow_result_on_image(result, pen_width, colour)

    def _on_shadow_override_clicked(self):
        """Re-run the most recent shadow measurement with the azimuth gate relaxed."""
        if self.first_point is None or self.second_point is None:
            return
        # Drop the previously rendered (rejected) overlay before redrawing.
        self._clear_shadow_overlays()
        zoom = self.image_viewer.getZoom() if hasattr(self.image_viewer, 'getZoom') else 1.0
        pen_width = self.fixed_line_width / zoom
        colour = QColor(255, 215, 0)
        self._estimate_and_render_shadow_height(
            pen_width, colour, allow_azimuth_override=True
        )

    def _clear_shadow_overlays(self):
        """Remove only the shadow-specific overlays, keep the B/T points + line."""
        for item in self.shadow_graphics:
            try:
                self.image_viewer.scene.removeItem(item)
            except Exception:
                pass
        self.shadow_graphics = []
        if self.distance_text_item is not None:
            try:
                self.image_viewer.scene.removeItem(self.distance_text_item)
            except Exception:
                pass
            self.distance_text_item = None

    def _render_shadow_result_in_dialog(self, result):
        """Update the sidebar group with the estimator's verdict."""
        if result.confidence == 'rejected':
            self.shadow_height_display.setText(self.tr("Rejected"))
            self.shadow_details.setText("")
            self.shadow_warnings.setText(result.rejection_reason or "")
            self.shadow_override_button.setVisible(bool(result.azimuth_override_available))
            return

        height_str = self._format_length(result.height_m)
        sigma_str = self._format_length(result.sigma_m) if result.sigma_m is not None else "?"
        self.shadow_height_display.setText(f"{height_str} ± {sigma_str}")

        details = (
            f"Sun: elev {result.sun_elev_deg:.1f}°, az {result.sun_az_deg:.1f}°\n"
            f"Shadow az measured {result.measured_shadow_az_deg:.1f}° "
            f"(Δ {result.delta_az_deg:+.1f}°)\n"
            f"Horizontal distance: {self._format_length(result.horizontal_dist_m)}, "
            f"terrain Δh: {self._format_length(result.elev_delta_m)}\n"
            f"DEM source: {result.dem_source or 'n/a'}"
        )
        if result.terrain_resolution_m:
            details += f" ({result.terrain_resolution_m:.1f} m)"
        self.shadow_details.setText(details)

        warnings = [w for w in result.warnings if w]
        self.shadow_warnings.setText("\n".join(warnings))
        self.shadow_override_button.setVisible(False)

    def _render_shadow_result_on_image(self, result, pen_width, colour):
        """Overlay the height label (and a direction arrow) on the image."""
        if self.first_point is None or self.second_point is None:
            return

        mid_x = (self.first_point.x() + self.second_point.x()) / 2.0
        mid_y = (self.first_point.y() + self.second_point.y()) / 2.0

        # Direction arrow at the midpoint, pointing base->tip.
        dx = self.second_point.x() - self.first_point.x()
        dy = self.second_point.y() - self.first_point.y()
        length = math.hypot(dx, dy)
        if length > 0:
            ux, uy = dx / length, dy / length
            arrow_size = max(8.0, pen_width * 4)
            tip_x = mid_x + ux * arrow_size
            tip_y = mid_y + uy * arrow_size
            left_x = mid_x - uy * arrow_size * 0.5
            left_y = mid_y + ux * arrow_size * 0.5
            right_x = mid_x + uy * arrow_size * 0.5
            right_y = mid_y - ux * arrow_size * 0.5
            polygon = QPolygonF([
                QPointF(tip_x, tip_y),
                QPointF(left_x, left_y),
                QPointF(right_x, right_y),
            ])
            arrow_item = QGraphicsPolygonItem(polygon)
            arrow_item.setBrush(colour)
            arrow_item.setPen(QPen(colour, pen_width))
            self.image_viewer.scene.addItem(arrow_item)
            self.shadow_graphics.append(arrow_item)

        label_text = self._build_image_label_text(result)
        label = QGraphicsTextItem()
        # Colour-code by confidence so a glance at the image tells you whether
        # to trust the number.
        if result.confidence == 'rejected':
            text_color = 'red'
        elif result.confidence == 'warning':
            text_color = '#ffcc00'
        else:
            text_color = '#ffd700'
        label.setHtml(
            f'<div style="background-color: rgba(0,0,0,180); '
            f'color: {text_color}; padding: 2px; font-weight: bold;">'
            f'{label_text}</div>'
        )
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        label.setFont(font)
        label.setPos(mid_x + pen_width * 4, mid_y + pen_width * 4)
        self.image_viewer.scene.addItem(label)
        self.shadow_graphics.append(label)
        # Reuse the existing distance_text_item slot so clearMeasurement
        # cleans up alongside everything else.
        self.distance_text_item = label

    def _build_image_label_text(self, result):
        if result.confidence == 'rejected':
            return self.tr("Rejected")
        return (
            f"H ≈ {self._format_length(result.height_m)} "
            f"± {self._format_length(result.sigma_m)}  "
            f"☉ {result.sun_elev_deg:.0f}° az {result.sun_az_deg:.0f}°"
        )

    def _format_length(self, value_m):
        """Format a length (in metres) per the user's distance-unit preference."""
        if value_m is None:
            return "?"
        if self.distance_unit == 'ft':
            v = value_m * 3.28084
            return f"{v:.2f} ft"
        if abs(value_m) < 1.0:
            return f"{value_m * 100:.1f} cm"
        return f"{value_m:.2f} m"

    def calculateDistance(self):
        """Calculate and display the distance between the two points."""
        if not self.first_point or not self.second_point:
            return

        if not self.current_gsd:
            self.distance_display.setText(self.tr("No GSD value"))
            return

        # Calculate pixel distance
        dx = self.second_point.x() - self.first_point.x()
        dy = self.second_point.y() - self.first_point.y()
        pixel_distance = math.sqrt(dx * dx + dy * dy)

        # Convert to real-world distance
        distance_cm = pixel_distance * self.current_gsd

        # Format based on user's preference
        if self.distance_unit == 'ft':
            distance_in = distance_cm / 2.54
            if distance_in >= 12:
                distance_str = f"{distance_in / 12:.2f} ft"
            else:
                distance_str = f"{distance_in:.2f} in"
        else:  # meters
            if distance_cm >= 100:
                distance_str = f"{distance_cm / 100:.2f} m"
            else:
                distance_str = f"{distance_cm:.1f} cm"

        self.distance_display.setText(distance_str)

        # Add distance text to the image
        if self.distance_text_item:
            self.image_viewer.scene.removeItem(self.distance_text_item)

        self.distance_text_item = QGraphicsTextItem(distance_str)
        self.distance_text_item.setDefaultTextColor(QColor(0, 255, 0))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.distance_text_item.setFont(font)

        # Position text at midpoint of line
        mid_x = (self.first_point.x() + self.second_point.x()) / 2
        mid_y = (self.first_point.y() + self.second_point.y()) / 2
        self.distance_text_item.setPos(mid_x, mid_y)

        # Add background for better visibility
        self.distance_text_item.setHtml(
            f'<div style="background-color: rgba(0, 0, 0, 180); color: #00ff00; padding: 2px;">{distance_str}</div>'
        )

        self.image_viewer.scene.addItem(self.distance_text_item)

    def clearMeasurement(self):
        """Clear all measurement graphics from the image."""
        # Remove all graphics items
        items_to_remove = [
            self.line_item, self.point1_item, self.point2_item,
            self.temp_line_item, self.distance_text_item
        ]

        for item in items_to_remove:
            if item:
                self.image_viewer.scene.removeItem(item)

        # Shadow overlays (labels / arrow) live in their own bucket so this
        # loop catches them whether or not a regular line was drawn.
        for item in self.shadow_graphics:
            try:
                self.image_viewer.scene.removeItem(item)
            except Exception:
                pass
        self.shadow_graphics = []

        # Reset state
        self.line_item = None
        self.point1_item = None
        self.point2_item = None
        self.temp_line_item = None
        self.distance_text_item = None
        self.first_point = None
        self.second_point = None
        self.measuring = False
        self.distance_display.setText("--")
        self.shadow_height_display.setText("--")
        self.shadow_details.setText("")
        self.shadow_warnings.setText("")
        self.shadow_override_button.setVisible(False)

    def updateItemSizes(self):
        """Update the sizes of all measurement items based on current zoom."""
        zoom = self.image_viewer.getZoom() if hasattr(self.image_viewer, 'getZoom') else 1.0
        radius = self.fixed_point_radius / zoom
        pen_width = self.fixed_line_width / zoom

        # Update first point
        if self.point1_item and self.first_point:
            self.image_viewer.scene.removeItem(self.point1_item)
            x, y = self.first_point.x(), self.first_point.y()
            self.point1_item = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
            self.point1_item.setBrush(QColor(255, 0, 0))
            self.point1_item.setPen(QPen(QColor(255, 255, 255), pen_width))
            self.image_viewer.scene.addItem(self.point1_item)

        # Update second point
        if self.point2_item and self.second_point:
            self.image_viewer.scene.removeItem(self.point2_item)
            x, y = self.second_point.x(), self.second_point.y()
            self.point2_item = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
            self.point2_item.setBrush(QColor(255, 0, 0))
            self.point2_item.setPen(QPen(QColor(255, 255, 255), pen_width))
            self.image_viewer.scene.addItem(self.point2_item)

        # Update line
        if self.line_item and self.first_point and self.second_point:
            self.image_viewer.scene.removeItem(self.line_item)
            self.line_item = QGraphicsLineItem(
                self.first_point.x(), self.first_point.y(),
                self.second_point.x(), self.second_point.y()
            )
            self.line_item.setPen(QPen(QColor(0, 255, 0), pen_width))
            self.image_viewer.scene.addItem(self.line_item)

    def closeEvent(self, event):
        """Handle dialog close event."""
        # Disconnect signals
        try:
            self.image_viewer.leftMouseButtonPressed.disconnect(self.onImageClick)
            self.image_viewer.mousePositionOnImageChanged.disconnect(self.onMouseMove)
            self.image_viewer.zoomChanged.disconnect(self.onZoomChanged)
        except Exception:
            pass  # Already disconnected

        # Restore original viewer settings
        self.image_viewer.canZoom = self.original_can_zoom
        self.image_viewer.canPan = self.original_can_pan
        self.image_viewer.regionZoomButton = self.original_region_zoom_button

        # Clear measurement
        self.clearMeasurement()

        super().closeEvent(event)
