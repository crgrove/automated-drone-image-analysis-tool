"""
AltitudeController - Handles altitude override and custom AGL altitude management.

Manages custom altitude settings for GSD calculations when GPS altitude is unreliable.
"""

from PySide6.QtWidgets import QInputDialog
from core.services.LoggerService import LoggerService


class AltitudeController:
    """
    Controller for managing custom altitude settings.

    Handles custom AGL altitude input and management for images with
    negative or unreliable altitude data.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the altitude controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()
        self.custom_agl_altitude_ft = None  # Store in feet as entered by user

    def prompt_for_custom_altitude(self, auto_triggered=True):
        """
        Prompt user for custom AGL altitude when negative altitude is detected.

        Args:
            auto_triggered (bool): If True, sets flag to -1 on cancel (don't show again)
        """
        self._show_altitude_override_dialog(
            "Negative Altitude Detected",
            "WARNING! Relative Altitude is negative. Enter an AGL altitude to be used for GSD calculations (in feet):",
            auto_triggered=auto_triggered
        )

    def manual_altitude_override(self):
        """Prompt user to manually override altitude for all images."""
        # Get current altitude if set
        current_alt = self.custom_agl_altitude_ft if self.custom_agl_altitude_ft and self.custom_agl_altitude_ft > 0 else 100.0

        self._show_altitude_override_dialog(
            "Override Altitude",
            "Enter a custom AGL altitude to be used for GSD calculations for all images (in feet):",
            auto_triggered=False,
            default_value=current_alt
        )

    def _show_altitude_override_dialog(self, title, message, auto_triggered=True, default_value=100.0):
        """
        Show altitude override dialog and update custom altitude.

        Args:
            title: Dialog window title
            message: Dialog message text
            auto_triggered: If True, sets flag to -1 on cancel (don't show again). If False, allows cancellation.
            default_value: Default altitude value to show
        """
        # Show dialog with input
        altitude_ft, ok = QInputDialog.getDouble(
            self.parent,
            title,
            message,
            default_value,  # Default value
            0.1,            # Minimum value
            10000.0,        # Maximum value
            1               # Decimals
        )

        if ok and altitude_ft > 0:
            # Store the custom altitude in feet
            old_altitude = self.custom_agl_altitude_ft
            self.custom_agl_altitude_ft = altitude_ft
            self.logger.info(f"Custom AGL altitude set to {altitude_ft} ft")

            # Show confirmation toast
            if hasattr(self.parent, 'status_controller'):
                self.parent.status_controller.show_toast(f"Custom AGL set to {altitude_ft} ft", 3000, color="#00C853")

            # If altitude changed and we have a current image, reload it to update GSD
            if old_altitude != altitude_ft and hasattr(self.parent, 'current_image'):
                if hasattr(self.parent, 'image_load_controller'):
                    self.parent.image_load_controller.load_image()
        else:
            if auto_triggered:
                # User canceled automatic prompt - don't show dialog again for this session
                # Set a flag value to indicate user chose to skip
                self.custom_agl_altitude_ft = -1
                self.logger.info("User declined to set custom AGL altitude")
            else:
                # User canceled manual override - just log it
                self.logger.info("User canceled altitude override")

    def get_effective_altitude(self):
        """
        Get the effective altitude for GSD calculations.

        Returns:
            float or None: Custom altitude in feet if set and positive, otherwise None
        """
        if self.custom_agl_altitude_ft and self.custom_agl_altitude_ft > 0:
            return self.custom_agl_altitude_ft
        return None

    def set_custom_altitude(self, altitude_ft):
        """
        Set custom altitude directly.

        Args:
            altitude_ft (float): Altitude in feet
        """
        self.custom_agl_altitude_ft = altitude_ft
        self.logger.info(f"Custom AGL altitude set to {altitude_ft} ft")

    def clear_custom_altitude(self):
        """Clear the custom altitude setting."""
        self.custom_agl_altitude_ft = None
        self.logger.info("Custom AGL altitude cleared")
