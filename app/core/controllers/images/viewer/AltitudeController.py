"""
AltitudeController - Handles altitude override and custom AGL altitude management.

Manages custom altitude settings for GSD calculations when GPS altitude is unreliable.
"""

from PySide6.QtWidgets import QInputDialog
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin


class AltitudeController(TranslationMixin):
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
        self.custom_agl_altitude_ft = None  # Store in feet internally for GSD calculations

    def _get_distance_unit(self):
        """
        Get the user's preferred distance unit.

        Returns:
            str: 'm' for meters, 'ft' for feet
        """
        # Always read from settings_service to get current preference (not parent.distance_unit which may be stale)
        if hasattr(self.parent, 'settings_service'):
            distance_unit = self.parent.settings_service.get_setting('DistanceUnit', 'Feet')
            if distance_unit:
                # Handle both 'Meters'/'Feet' (from UI) and 'm'/'ft' (legacy/internal) formats
                if distance_unit in ('Meters', 'm'):
                    return 'm'
                elif distance_unit in ('Feet', 'ft'):
                    return 'ft'

        # Final fallback to feet
        return 'ft'

    def _convert_feet_to_preferred_unit(self, value_ft):
        """
        Convert altitude from feet to user's preferred unit.

        Args:
            value_ft (float): Altitude in feet

        Returns:
            float: Altitude in user's preferred unit
        """
        unit = self._get_distance_unit()
        if unit == 'm':
            return value_ft / 3.28084
        return value_ft

    def _convert_preferred_unit_to_feet(self, value):
        """
        Convert altitude from user's preferred unit to feet.

        Args:
            value (float): Altitude in user's preferred unit

        Returns:
            float: Altitude in feet
        """
        unit = self._get_distance_unit()
        if unit == 'm':
            return value * 3.28084
        return value

    def _get_unit_label(self):
        """
        Get the unit label for display.

        Returns:
            str: Unit label ('ft' or 'm')
        """
        return self._get_distance_unit()

    def _get_unit_name(self):
        """
        Get the full unit name for display.

        Returns:
            str: Unit name ('feet' or 'meters')
        """
        unit = self._get_distance_unit()
        return self.tr("meters") if unit == 'm' else self.tr("feet")

    def prompt_for_custom_altitude(self, auto_triggered=True):
        """
        Prompt user for custom AGL altitude when negative altitude is detected.

        Args:
            auto_triggered (bool): If True, sets flag to -1 on cancel (don't show again)
        """
        unit_name = self._get_unit_name()
        self._show_altitude_override_dialog(
            self.tr("Negative Altitude Detected"),
            self.tr(
                "WARNING! Relative Altitude is negative. "
                "Enter an AGL altitude to be used for GSD calculations (in {unit}):"
            ).format(unit=unit_name),
            auto_triggered=auto_triggered
        )

    def manual_altitude_override(self):
        """Prompt user to manually override altitude for all images."""
        # Get current altitude if set, convert to preferred unit for display
        unit = self._get_distance_unit()

        if self.custom_agl_altitude_ft and self.custom_agl_altitude_ft > 0:
            current_alt_display = self._convert_feet_to_preferred_unit(self.custom_agl_altitude_ft)
        else:
            # Default to 100 feet or equivalent in meters
            current_alt_display = 30.48 if unit == 'm' else 100.0

        unit_name = self._get_unit_name()
        self._show_altitude_override_dialog(
            self.tr("Override Altitude"),
            self.tr(
                "Enter a custom AGL altitude to be used for GSD calculations for all images (in {unit}):"
            ).format(unit=unit_name),
            auto_triggered=False,
            default_value=current_alt_display
        )

    def _show_altitude_override_dialog(self, title, message, auto_triggered=True, default_value=100.0):
        """
        Show altitude override dialog and update custom altitude.

        Args:
            title: Dialog window title
            message: Dialog message text
            auto_triggered: If True, sets flag to -1 on cancel (don't show again). If False, allows cancellation.
            default_value: Default altitude value to show (in user's preferred unit)
        """
        # Determine min/max values based on unit
        unit = self._get_distance_unit()
        if unit == 'm':
            min_value = 0.1
            max_value = 3048.0  # ~10000 ft in meters
        else:
            min_value = 0.1
            max_value = 10000.0

        # Show dialog with input (value is in user's preferred unit)
        altitude_display, ok = QInputDialog.getDouble(
            self.parent,
            title,
            message,
            default_value,  # Default value in user's preferred unit
            min_value,      # Minimum value
            max_value,      # Maximum value
            1               # Decimals
        )

        if ok and altitude_display > 0:
            # Convert from user's preferred unit to feet for internal storage
            altitude_ft = self._convert_preferred_unit_to_feet(altitude_display)
            old_altitude = self.custom_agl_altitude_ft
            self.custom_agl_altitude_ft = altitude_ft

            unit_label = self._get_unit_label()
            # self.logger.info(f"Custom AGL altitude set to {altitude_display} {unit_label} ({altitude_ft:.2f} ft)")

            # Show confirmation toast with user's preferred unit
            if hasattr(self.parent, 'status_controller'):
                self.parent.status_controller.show_toast(
                    self.tr("Custom AGL set to {value:.1f} {unit}").format(
                        value=altitude_display,
                        unit=unit_label
                    ),
                    3000,
                    color="#00C853"
                )

            # If altitude changed and we have a current image, reload it to update GSD
            if old_altitude != altitude_ft and hasattr(self.parent, 'current_image'):
                if hasattr(self.parent, 'image_load_controller'):
                    self.parent.image_load_controller.load_image()
        else:
            if auto_triggered:
                # User canceled automatic prompt - don't show dialog again for this session
                # Set a flag value to indicate user chose to skip
                self.custom_agl_altitude_ft = -1
                # self.logger.info("User declined to set custom AGL altitude")
            else:
                # User canceled manual override - just log it
                # self.logger.info("User canceled altitude override")
                pass

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
        # unit_label = self._get_unit_label()
        # altitude_display = self._convert_feet_to_preferred_unit(altitude_ft)
        # self.logger.info(f"Custom AGL altitude set to {altitude_display:.2f} {unit_label} ({altitude_ft:.2f} ft)")

    def clear_custom_altitude(self):
        """Clear the custom altitude setting."""
        self.custom_agl_altitude_ft = None
        # self.logger.info("Custom AGL altitude cleared")
