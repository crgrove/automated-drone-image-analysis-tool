"""
StatusController - Handles status bar and messaging functionality.

This controller manages status bar updates, toast messages, mouse position
tracking, and scale bar functionality.
"""

import colorsys
import numpy as np
from PySide6.QtWidgets import QLabel, QMessageBox
from PySide6.QtCore import Qt

from core.services.LoggerService import LoggerService
from core.services.image.ImageService import ImageService


class StatusController:
    """
    Controller for managing status bar and messaging functionality.

    Handles status bar updates, toast messages, mouse position tracking,
    and scale bar functionality.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the status controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()  # Create our own logger


    def message_listener(self, key, value):
        """Updates the status bar with all key-value pairs from self.messages, skipping None values."""
        status_bar = self.parent.statusBar
        if not status_bar:
            return

        status_items = []

        # GPS Coordinates first (with hyperlink)
        messages = self.parent.messages
        gps_value = messages.get("GPS Coordinates")
        if gps_value:
            # Use the GPS coordinates as the href value so "Copy Link Location" copies the coordinates
            status_items.append(f'<a href="{gps_value}">GPS Coordinates: {gps_value}</a>')

        # Add all other messages
        for k, v in messages.items():
            if v is not None and k != "GPS Coordinates":
                status_items.append(f"{k}: {v}")

        # Update status bar
        if status_items:
            status_bar.setText(" | ".join(status_items))
        else:
            status_bar.setText("")

    def show_toast(self, text: str, msec: int = 3000, color: str = "#00C853"):
        """Show a toast message.

        Args:
            text: The message text to display
            msec: Duration in milliseconds
            color: Background color for the toast
        """
        toast_label = self.parent._toastLabel
        toast_timer = self.parent._toastTimer
        if not toast_label or not toast_timer:
            return

        try:
            toast_label.setText(text)
            toast_label.setStyleSheet(
                f"QLabel{{background-color:{color}; color:white; border-radius:6px; padding:6px 10px; font-weight:bold;}}"
            )
            toast_label.adjustSize()
            sb_w = self.parent.statusBarWidget.width()
            sb_h = self.parent.statusBarWidget.height()
            tw = toast_label.width()
            th = toast_label.height()
            x = max(4, (sb_w - tw) // 2)
            y = max(2, (sb_h - th) // 2)
            toast_label.move(x, y)
            toast_label.raise_()
            toast_label.setVisible(True)
            toast_timer.start(max(1, msec))
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
