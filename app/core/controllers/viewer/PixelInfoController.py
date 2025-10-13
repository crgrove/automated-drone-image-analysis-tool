"""
PixelInfoController - Handles pixel information display at cursor position.

Manages temperature, color value, and coordinate display based on cursor position.
"""

import colorsys
from PySide6.QtCore import QPoint
from core.services.LoggerService import LoggerService


class PixelInfoController:
    """
    Controller for displaying pixel information at the cursor position.
    
    Handles temperature display for thermal images, RGB/HSV color values
    for non-thermal images, and coordinates tracking.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the pixel info controller.
        
        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()

    def update_cursor_info(self, pos):
        """
        Update cursor information display based on mouse position.
        
        Args:
            pos (QPoint): The current mouse position in image coordinates.
                         Will be (-1, -1) when cursor is outside the image.
        """
        # Clear previous cursor position message
        if "Cursor Position" in self.parent.messages:
            self.parent.messages["Cursor Position"] = None
        # Clear previous color values message
        if "Color Values" in self.parent.messages:
            self.parent.messages["Color Values"] = None

        # Handle thermal data display
        if hasattr(self.parent, 'thermal_controller') and self.parent.thermal_controller.temperature_data is not None:
            self._update_temperature_display(pos)
        else:
            # Handle color value display for non-thermal images
            self._update_color_value_display(pos)

    def _update_temperature_display(self, pos):
        """
        Update temperature display at cursor position.
        
        Args:
            pos (QPoint): Cursor position in image coordinates
        """
        # Check if cursor is within valid image bounds
        if pos.x() >= 0 and pos.y() >= 0:
            temp_value = self.parent.thermal_controller.get_temperature_at_point(pos.x(), pos.y())
            if temp_value is not None:
                # Format temperature with 1 decimal place for cleaner display
                temp_display = f"{temp_value:.1f}° {self.parent.temperature_unit} at ({pos.x()}, {pos.y()})"
                self.parent.messages["Temperature"] = temp_display
            else:
                # Cursor is on image but outside temperature data bounds
                self.parent.messages["Temperature"] = None
        else:
            # Cursor is outside the image
            self.parent.messages["Temperature"] = None

    def _update_color_value_display(self, pos):
        """
        Update color value display at cursor position for non-thermal images.
        
        Args:
            pos (QPoint): Cursor position in image coordinates
        """
        # No temperature data available (non-thermal image)
        self.parent.messages["Temperature"] = None

        # Display color values for non-thermal images only
        # Check if this is actually a non-thermal algorithm
        algorithm_name = self.parent.settings.get('algorithm', '')
        if algorithm_name not in ['ThermalRange', 'ThermalAnomaly']:
            if pos.x() >= 0 and pos.y() >= 0:
                # Only show color values if cursor is on the image
                if hasattr(self.parent, 'main_image') and self.parent.main_image and self.parent.main_image.hasImage():
                    try:
                        # Use the image array from parent (already loaded by ImageLoadController)
                        img_array = self.parent.current_image_array

                        if img_array is not None:
                            # Check bounds
                            if (0 <= pos.y() < img_array.shape[0]) and (0 <= pos.x() < img_array.shape[1]):
                                # Get RGB values at cursor position
                                r, g, b = img_array[pos.y(), pos.x()]

                                # Format display based on algorithm
                                color_display = self._format_color_display_for_algorithm(
                                    algorithm_name, r, g, b, pos.x(), pos.y()
                                )
                                self.parent.messages["Color Values"] = color_display
                    except Exception as e:
                        # Log error but don't show to user
                        self.logger.error(f"Error getting pixel values: {e}")

    def _format_color_display_for_algorithm(self, algorithm_name, r, g, b, x, y):
        """
        Format color value display based on the algorithm type.
        
        Args:
            algorithm_name (str): Name of the current algorithm
            r (int): Red value (0-255)
            g (int): Green value (0-255)
            b (int): Blue value (0-255)
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            str: Formatted color display string
        """
        if algorithm_name in ['HSVColorRange', 'RXAnomaly', 'MRMap']:
            # Display HSV values
            # Convert RGB to HSV
            r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)

            # Convert to standard ranges: H (0-360), S (0-100), V (0-100)
            h_deg = int(h * 360)
            s_pct = int(s * 100)
            v_pct = int(v * 100)

            return f"H: {h_deg}°, S: {s_pct}%, V: {v_pct}% at ({x}, {y})"
        else:
            # Display RGB values for ColorRange, MatchedFilter, AIPersonDetector, and unknown algorithms
            return f"R: {r}, G: {g}, B: {b} at ({x}, {y})"

