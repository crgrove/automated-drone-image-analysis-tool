"""
CoordinateController - Handles GPS coordinate and mapping functionality.

This controller manages GPS coordinate display, sharing, mapping integration,
and north-oriented image viewing.
"""

import os
import tempfile
import math
import cv2
import numpy as np
from urllib.parse import quote_plus

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QDialog, QApplication
from PySide6.QtCore import Qt, QObject, QEvent, QTimer, QUrl, QPoint
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QThread

from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer
from core.services.image.ImageService import ImageService
from core.services.LoggerService import LoggerService
import qimage2ndarray


class CoordinateController:
    """
    Controller for managing GPS coordinate and mapping functionality.

    Handles coordinate display, sharing, mapping integration, and
    north-oriented image viewing.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the coordinate controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()  # Create our own logger

        # Coordinate state
        self.current_decimal_coords = None

        # North-oriented image popup window
        self.north_oriented_popup = None

        # Track current coordinates popup
        self.current_coords_popup = None

    def on_coordinates_clicked(self, link):
        """Handle clicks on GPS coordinates in the status bar."""
        # Get coordinates from messages
        coord_text = self.parent.messages.get('GPS Coordinates')
        if not coord_text:
            return

        # Show coordinates popup
        self.show_coordinates_popup(coord_text)

    def show_coordinates_popup(self, coord_text, anchor_widget=None, anchor_point=None):
        """Show a small popup with coordinate sharing options.

        Args:
            coord_text: Formatted coordinate string to display
            anchor_widget: Optional widget to anchor the popup to (for single-image mode)
            anchor_point: Optional QPoint in global coordinates to anchor the popup to (for gallery mode)
        """
        # Close any existing popup
        if self.current_coords_popup:
            self.current_coords_popup.close()
            self.current_coords_popup = None

        # Create popup widget
        popup = QWidget(self.parent, Qt.Popup)
        popup.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                border-radius: 8px;
                color: white;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 4px;
                color: white;
                padding: 8px 12px;
                min-width: 120px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QLabel {
                padding: 8px 12px;
                border-bottom: 1px solid #555555;
                font-weight: bold;
            }
        """)

        # Create layout
        layout = QVBoxLayout(popup)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel(f"GPS Coordinates: {coord_text}")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Helper function to close popup after action
        def close_popup():
            if popup:
                popup.close()
                if self.current_coords_popup == popup:
                    self.current_coords_popup = None

        # Buttons with close handlers
        def make_action_handler(action_func, *args):
            def handler():
                action_func(*args)
                close_popup()
            return handler

        copy_btn = QPushButton("📋 Copy coordinates")
        copy_btn.clicked.connect(make_action_handler(self.copy_coords_to_clipboard, coord_text))
        layout.addWidget(copy_btn)

        maps_btn = QPushButton("🗺️ Open in Google Maps")
        maps_btn.clicked.connect(make_action_handler(self.open_in_maps))
        layout.addWidget(maps_btn)

        earth_btn = QPushButton("🌍 View in Google Earth")
        earth_btn.clicked.connect(make_action_handler(self.open_in_earth))
        layout.addWidget(earth_btn)

        whatsapp_btn = QPushButton("📱 Send via WhatsApp")
        whatsapp_btn.clicked.connect(make_action_handler(self.share_whatsapp))
        layout.addWidget(whatsapp_btn)

        telegram_btn = QPushButton("📨 Send via Telegram")
        telegram_btn.clicked.connect(make_action_handler(self.share_telegram))
        layout.addWidget(telegram_btn)

        # Position popup near anchor point/widget or status bar
        popup.adjustSize()

        if anchor_point:
            # Use provided global anchor point (gallery mode)
            popup_x = anchor_point.x() - popup.width()  # Position to the left of anchor
            popup_y = anchor_point.y() - popup.height()  # Position above anchor
        elif anchor_widget:
            # Use provided widget (single-image mode)
            widget_global_pos = anchor_widget.mapToGlobal(anchor_widget.rect().bottomRight())
            popup_x = widget_global_pos.x() - popup.width()  # Position to the left of widget
            popup_y = widget_global_pos.y() - popup.height()  # Position above widget
        else:
            # Default: position near the status bar
            statusbar_pos = self.parent.statusBarWidget.mapToGlobal(self.parent.statusBarWidget.rect().bottomLeft())
            popup_pos = self.parent.mapFromGlobal(statusbar_pos)
            popup_x = popup_pos.x()
            popup_y = popup_pos.y() - popup.height()

        # Ensure popup doesn't go off-screen
        screen_geometry = self.parent.screen().geometry()
        popup_x = max(screen_geometry.x(), min(popup_x, screen_geometry.right() - popup.width()))
        popup_y = max(screen_geometry.y(), min(popup_y, screen_geometry.bottom() - popup.height()))

        popup.move(popup_x, popup_y)

        # Store reference to current popup
        self.current_coords_popup = popup

        # Show popup
        popup.show()

        # Auto-close when clicking outside
        popup.setFocus()

        # Install a simple event filter to close popup when clicking outside
        popup.installEventFilter(self.create_simple_popup_filter(popup, self))

    def create_simple_popup_filter(self, popup, parent_controller):
        """Create a simple event filter to close the popup when clicking outside."""
        class SimplePopupFilter(QObject):
            def __init__(self, popup_widget, controller):
                super().__init__()
                self.popup = popup_widget
                self.parent_controller = controller

            def eventFilter(self, obj, event):
                if event.type() == QEvent.MouseButtonPress:
                    if not self.popup.geometry().contains(event.globalPos()):
                        self.popup.close()
                        # Clear reference if this popup is closed
                        if hasattr(self, 'parent_controller'):
                            if self.parent_controller.current_coords_popup == self.popup:
                                self.parent_controller.current_coords_popup = None
                        return True
                return False

        return SimplePopupFilter(popup, parent_controller)

    def copy_coords_to_clipboard(self, coord_text=None):
        """Copy coordinates to clipboard."""
        if coord_text is None:
            if hasattr(self.parent, 'messages') and hasattr(self.parent.messages, 'data'):
                coord_text = self.parent.messages.data.get('GPS Coordinates')
        if not coord_text:
            return
        QApplication.clipboard().setText(str(coord_text))
        self.parent.status_controller.show_toast("Coordinates copied", 3000, color="#00C853")

    def open_in_maps(self):
        """Open coordinates in Google Maps."""
        lat_lon = self.get_decimals_or_parse()
        if not lat_lon:
            self.parent.status_controller.show_toast("Coordinates unavailable", 3000, color="#F44336")
            return
        lat, lon = lat_lon
        url = QUrl(f"https://www.google.com/maps?q={lat},{lon}")
        QDesktopServices.openUrl(url)

    def open_in_earth(self):
        """Open coordinates in Google Earth."""
        lat_lon = self.get_decimals_or_parse()
        if not lat_lon:
            self.parent.status_controller.show_toast("Coordinates unavailable", 3000, color="#F44336")
            return

        lat, lon = lat_lon
        image = self.parent.images[self.parent.current_image]
        image_path = image['path']
        mask_path = image.get('mask_path', '')
        calculated_bearing = image.get('bearing', None)
        image_service = ImageService(image_path, mask_path, calculated_bearing=calculated_bearing)
        yaw = image_service.get_camera_yaw()
        pitch = image_service.get_camera_pitch()
        altitude = image_service.get_asl_altitude('m')
        hfov = image_service.get_camera_hfov()

        if yaw is None:
            yaw = 0.0
        if pitch is None:
            pitch = -90.0
        if altitude is None:
            altitude = 100.0
        if hfov is None:
            hfov = 60.0

        range_val = 50
        tilt = max(0, min(180, 90 + pitch))

        kml = (
            "<?xml version='1.0' encoding='UTF-8'?>\n"
            "<kml xmlns='http://www.opengis.net/kml/2.2'>\n"
            "  <Document>\n"
            "    <name>ADIAT View</name>\n"
            "    <open>1</open>\n"
            "    <LookAt>\n"
            f"      <longitude>{lon}</longitude>\n"
            f"      <latitude>{lat}</latitude>\n"
            f"      <altitude>{altitude}</altitude>\n"
            f"      <heading>{yaw}</heading>\n"
            f"      <tilt>{tilt}</tilt>\n"
            "      <altitudeMode>absolute</altitudeMode>\n"
            f"      <range>{range_val}</range>\n"
            "    </LookAt>\n"
            "    <Placemark>\n"
            "      <name>Photo Location</name>\n"
            f"      <Point><coordinates>{lon},{lat},0</coordinates></Point>\n"
            "    </Placemark>\n"
            "  </Document>\n"
            "</kml>\n"
        )

        fd, kml_path = tempfile.mkstemp(suffix='.kml')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(kml)

        QDesktopServices.openUrl(QUrl.fromLocalFile(kml_path))

    def share_whatsapp(self):
        """Share coordinates via WhatsApp."""
        lat_lon = self.get_decimals_or_parse()
        if not lat_lon:
            self.parent.status_controller.show_toast("Coordinates unavailable", 3000, color="#F44336")
            return
        lat, lon = lat_lon
        maps = f"https://www.google.com/maps?q={lat},{lon}"
        text = f"Coordinate: {lat}, {lon} — {maps}"
        wa_url = f"https://wa.me/?text={quote_plus(text)}"
        QDesktopServices.openUrl(QUrl(wa_url))

    def share_telegram(self):
        """Share coordinates via Telegram."""
        lat_lon = self.get_decimals_or_parse()
        if not lat_lon:
            self.parent.status_controller.show_toast("Coordinates unavailable", 3000, color="#F44336")
            return
        lat, lon = lat_lon
        maps = f"https://www.google.com/maps?q={lat},{lon}"
        tg_url = f"https://t.me/share/url?url={quote_plus(maps)}&text={quote_plus(f'Coordinates: {lat}, {lon}')}"
        QDesktopServices.openUrl(QUrl(tg_url))

    def get_decimals_or_parse(self):
        """Get decimal coordinates from current state or parse from messages."""
        # Prefer decimal coords captured from EXIF
        if getattr(self, 'current_decimal_coords', None):
            return self.current_decimal_coords
        coord_text = None
        if hasattr(self.parent, 'messages') and hasattr(self.parent.messages, 'data'):
            coord_text = self.parent.messages.data.get('GPS Coordinates')
        if coord_text and "," in str(coord_text):
            try:
                lat_s, lon_s = str(coord_text).split(",", 1)
                return float(lat_s.strip()), float(lon_s.strip())
            except Exception:
                return None
        return None

    def show_north_oriented_image(self):
        """Show a popup window with the current image rotated to true north based on bearing info."""
        try:
            # Get the current image's bearing/yaw information
            if not hasattr(self.parent, 'current_image') or self.parent.current_image < 0:
                return

            image = self.parent.images[self.parent.current_image]
            image_path = image.get('path', '')
            mask_path = image.get('mask_path', '')
            calculated_bearing = image.get('bearing', None)

            # Get the drone orientation (yaw/bearing)
            image_service = ImageService(image_path, mask_path, calculated_bearing=calculated_bearing)
            # Use get_drone_orientation() to match the Drone Orientation shown in the status bar
            direction = image_service.get_camera_yaw()

            if direction is None:
                # Show message that no bearing info is available
                self.parent.status_controller.show_toast("No bearing info available", 3000, color="#F44336")
                return

            # Get the current image array
            if not hasattr(self.parent, 'current_image_array') or self.parent.current_image_array is None:
                return

            img_array = self.parent.current_image_array.copy()

            # Calculate rotation angle to orient to north
            # If drone is facing east (90°), we need to rotate -90° to face north
            rotation_angle = -direction

            # Rotate the image
            h, w = img_array.shape[:2]
            center = (w // 2, h // 2)

            # Get rotation matrix
            M = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)

            # Calculate new image bounds after rotation
            cos = abs(M[0, 0])
            sin = abs(M[0, 1])
            new_w = int((h * sin) + (w * cos))
            new_h = int((h * cos) + (w * sin))

            # Adjust rotation matrix to prevent cropping
            M[0, 2] += (new_w / 2) - center[0]
            M[1, 2] += (new_h / 2) - center[1]

            # Perform rotation
            rotated_img = cv2.warpAffine(img_array, M, (new_w, new_h),
                                         borderMode=cv2.BORDER_CONSTANT,
                                         borderValue=(128, 128, 128))

            # Create popup window
            popup = QDialog(self.parent)
            popup.setWindowTitle(f"North-Oriented View (Rotated {rotation_angle:.1f}°)")
            popup.setModal(False)  # Non-modal so user can still interact with main window

            # Store reference for cleanup when viewer closes
            self.north_oriented_popup = popup

            # Connect to dialog close event to update button state
            popup.finished.connect(self.on_rotate_dialog_closed)

            # Update button state to show window is open
            if hasattr(self.parent, 'rotate_image_open'):
                self.parent.rotate_image_open = True
                if hasattr(self.parent, 'ui_style_controller'):
                    self.parent.ui_style_controller.update_rotate_image_button_style()

            # Create layout
            layout = QVBoxLayout(popup)

            # Create image viewer widget
            image_viewer = QtImageViewer(self.parent)
            image_viewer.setMinimumSize(800, 600)

            # Convert rotated image to QImage and display
            qimg = qimage2ndarray.array2qimage(rotated_img)
            image_viewer.setImage(qimg)

            # Add label showing rotation info
            info_label = QLabel(f"Original bearing: {direction:.1f}° | Rotation applied: {rotation_angle:.1f}°")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("QLabel { background-color: rgba(0,0,0,150); color: white; padding: 5px; }")

            # Add north arrow indicator
            north_label = QLabel("↑ NORTH")
            north_label.setAlignment(Qt.AlignCenter)
            north_label.setStyleSheet("QLabel { color: red; font-size: 16px; font-weight: bold; }")

            layout.addWidget(north_label)
            layout.addWidget(image_viewer)
            layout.addWidget(info_label)

            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(popup.close)
            layout.addWidget(close_btn)

            # Show the popup
            popup.resize(1000, 800)
            popup.show()

        except Exception as e:
            self.logger.error(f"Error showing north-oriented image: {e}")
            self.parent.status_controller.show_toast(f"Error: {str(e)}", 3000, color="#F44336")

    def update_current_coordinates(self, decimal_coords):
        """Update the current decimal coordinates.

        Args:
            decimal_coords: Tuple of (latitude, longitude) or None
        """
        self.current_decimal_coords = decimal_coords

    def on_rotate_dialog_closed(self):
        """Handle north-oriented image dialog close event."""
        if hasattr(self.parent, 'rotate_image_open'):
            self.parent.rotate_image_open = False
            if hasattr(self.parent, 'ui_style_controller'):
                self.parent.ui_style_controller.update_rotate_image_button_style()

    def cleanup(self):
        """Clean up resources when viewer is closing."""
        # Close north-oriented image popup if it's open
        if self.north_oriented_popup and self.north_oriented_popup.isVisible():
            self.north_oriented_popup.close()
            self.north_oriented_popup = None
