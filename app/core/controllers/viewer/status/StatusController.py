"""
StatusController - Handles status bar and messaging functionality.

This controller manages status bar updates, toast messages, mouse position
tracking, and scale bar functionality.
"""

import colorsys
import numpy as np
from PySide6.QtWidgets import QLabel, QMessageBox
from PySide6.QtCore import Qt, QTimer

from core.services.LoggerService import LoggerService
from core.services.ImageService import ImageService


class StatusController:
    """
    Controller for managing status bar and messaging functionality.

    Handles status bar updates, toast messages, mouse position tracking,
    and scale bar functionality.
    """

    def __init__(self, parent_viewer, logger=None):
        """
        Initialize the status controller.

        Args:
            parent_viewer: The main Viewer instance
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_viewer
        self.logger = logger or LoggerService()

        # UI elements (will be set by parent)
        self.statusBar = None
        self.toastLabel = None
        self.toastTimer = None
        self.messages = None

    def set_ui_elements(self, status_bar, toast_label, toast_timer, messages):
        """Set references to UI elements.

        Args:
            status_bar: The QStatusBar widget
            toast_label: The QLabel for toast messages
            toast_timer: The QTimer for toast auto-hide
            messages: The StatusDict for message management
        """
        self.statusBar = status_bar
        self.toastLabel = toast_label
        self.toastTimer = toast_timer
        self.messages = messages

    def message_listener(self, key, value):
        """Updates the status bar with all key-value pairs from self.messages, skipping None values."""
        if not self.statusBar:
            return

        status_items = []

        # GPS Coordinates first (with hyperlink)
        gps_value = self.messages.get("GPS Coordinates")
        if gps_value:
            # Use the GPS coordinates as the href value so "Copy Link Location" copies the coordinates
            status_items.append(f'<a href="{gps_value}">GPS Coordinates: {gps_value}</a>')

        # Add all other messages
        for k, v in self.messages.items():
            if v is not None and k != "GPS Coordinates":
                status_items.append(f"{k}: {v}")

        # Update status bar
        if status_items:
            self.statusBar.setText(" | ".join(status_items))
        else:
            self.statusBar.setText("")

    def show_toast(self, text: str, msec: int = 3000, color: str = "#00C853"):
        """Show a toast message.

        Args:
            text: The message text to display
            msec: Duration in milliseconds
            color: Background color for the toast
        """
        if not self.toastLabel or not self.toastTimer:
            return

        try:
            self.toastLabel.setText(text)
            self.toastLabel.setStyleSheet(
                f"QLabel{{background-color:{color}; color:white; border-radius:6px; padding:6px 10px; font-weight:bold;}}"
            )
            self.toastLabel.adjustSize()
            sb_w = self.parent.statusBarWidget.width()
            sb_h = self.parent.statusBarWidget.height()
            tw = self.toastLabel.width()
            th = self.toastLabel.height()
            x = max(4, (sb_w - tw) // 2)
            y = max(2, (sb_h - th) // 2)
            self.toastLabel.move(x, y)
            self.toastLabel.raise_()
            self.toastLabel.setVisible(True)
            self.toastTimer.start(max(1, msec))
        except Exception:
            pass

    def show_error(self, text):
        """Displays an error message box.

        Args:
            text (str): Error message to display.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error Loading Images")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def show_no_images_message(self):
        """Displays an error message when there are no available images."""
        self.show_error("No active images available.")

    def show_additional_images_message(self):
        """Displays an error message when there are no additional images."""
        self.show_error("No other images available.")
