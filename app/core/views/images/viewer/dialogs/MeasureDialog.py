"""MeasureDialog controller for distance measurement functionality."""

import math
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPen, QColor, QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem


class MeasureDialog(QDialog):
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

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Measure Distance")
        self.setModal(False)

        # Set window flags to keep dialog on top (especially important on macOS)
        # Use WindowStaysOnTopHint to keep it visible when clicking on parent window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, non-modal dialogs with WindowStaysOnTopHint need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the GSD input field so users can type immediately
        if hasattr(self, 'gsd_input'):
            self.gsd_input.setFocus()

        self.setMinimumWidth(300)

        # Main layout
        layout = QVBoxLayout()

        # GSD input group
        gsd_group = QGroupBox("Ground Sample Distance")
        gsd_layout = QHBoxLayout()

        gsd_label = QLabel("GSD:")
        self.gsd_input = QLineEdit()
        self.gsd_input.setPlaceholderText("Enter GSD value")
        if self.current_gsd:
            self.gsd_input.setText(str(self.current_gsd))

        gsd_unit_label = QLabel("cm/px")

        gsd_layout.addWidget(gsd_label)
        gsd_layout.addWidget(self.gsd_input)
        gsd_layout.addWidget(gsd_unit_label)
        gsd_group.setLayout(gsd_layout)

        # Distance display group
        distance_group = QGroupBox("Measurement")
        distance_layout = QHBoxLayout()

        distance_label = QLabel("Distance:")
        self.distance_display = QLabel("--")
        self.distance_display.setStyleSheet("QLabel { font-weight: bold; font-size: 14pt; }")

        distance_layout.addWidget(distance_label)
        distance_layout.addWidget(self.distance_display)
        distance_layout.addStretch()
        distance_group.setLayout(distance_layout)

        # Instructions
        instructions = QLabel("Click on the image to place the first point,\nthen click again to place the second point.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("QLabel { color: gray; }")

        # Buttons
        button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clearMeasurement)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        # Add all to main layout
        layout.addWidget(gsd_group)
        layout.addWidget(distance_group)
        layout.addWidget(instructions)
        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def connectSignals(self):
        """Connect signals and slots."""
        # Connect to image viewer mouse events
        self.image_viewer.leftMouseButtonPressed.connect(self.onImageClick)
        self.image_viewer.mousePositionOnImageChanged.connect(self.onMouseMove)

        # Connect GSD input
        self.gsd_input.textChanged.connect(self.onGsdChanged)

        # Connect to zoom changes to update item sizes
        self.image_viewer.zoomChanged.connect(self.onZoomChanged)

        # Mouse tracking is already enabled in QtImageViewer

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

        if not self.measuring:
            # First click - place first point
            self.clearMeasurement()
            self.first_point = point
            self.measuring = True

            # Draw first point with size adjusted for current zoom
            zoom = self.image_viewer.getZoom() if hasattr(self.image_viewer, 'getZoom') else 1.0
            radius = self.fixed_point_radius / zoom
            pen_width = self.fixed_line_width / zoom

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

            # Draw second point with size adjusted for current zoom
            zoom = self.image_viewer.getZoom() if hasattr(self.image_viewer, 'getZoom') else 1.0
            radius = self.fixed_point_radius / zoom
            pen_width = self.fixed_line_width / zoom

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

            self.temp_line_item = QGraphicsLineItem(
                self.first_point.x(), self.first_point.y(),
                pos.x(), pos.y()
            )
            self.temp_line_item.setPen(QPen(QColor(255, 255, 0), pen_width, Qt.DashLine))
            self.image_viewer.scene.addItem(self.temp_line_item)

    def calculateDistance(self):
        """Calculate and display the distance between the two points."""
        if not self.first_point or not self.second_point:
            return

        if not self.current_gsd:
            self.distance_display.setText("No GSD value")
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
