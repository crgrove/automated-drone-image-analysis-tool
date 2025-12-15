"""
ThermalDataController - Handles thermal data management and temperature operations.

Manages loading, parsing, and querying thermal data from thermal images.
"""

import numpy as np
from core.services.LoggerService import LoggerService
from core.services.thermal.ThermalParserService import ThermalParserService


class ThermalDataController:
    """
    Controller for managing thermal data from thermal images.

    Handles thermal data loading from XMP metadata or direct parsing,
    temperature unit conversion, and temperature queries at specific positions.
    """

    def __init__(self, parent_viewer):
        """
        Initialize the thermal data controller.

        Args:
            parent_viewer: The main Viewer instance
        """
        self.parent = parent_viewer
        self.logger = LoggerService()
        self.temperature_data = None

    def load_thermal_data(self, image_service, image_path, temperature_unit):
        """
        Load thermal data from an image.

        First tries to get thermal data from XMP metadata, then falls back to
        direct parsing from the thermal image file.

        Args:
            image_service: ImageService instance for the current image
            image_path (str): Path to the image file
            temperature_unit (str): Desired temperature unit ('F' or 'C')

        Returns:
            np.ndarray or None: Temperature data array or None if unavailable
        """
        # First try to get thermal data from XMP metadata
        self.temperature_data = image_service.get_thermal_data(temperature_unit)

        # If no thermal data in XMP, try to parse it directly from the thermal image
        if self.temperature_data is None:
            try:
                # Check if this is a thermal image file
                if image_path.lower().endswith(('.jpg', '.jpeg', '.rjpeg')):
                    thermal_parser = ThermalParserService(dtype=np.float32)
                    temperature_c, _ = thermal_parser.parse_file(image_path)

                    # Convert to the desired unit
                    if temperature_unit == 'F' and temperature_c is not None:
                        self.temperature_data = temperature_c * 1.8 + 32.0
                    else:
                        self.temperature_data = temperature_c
            except Exception as e:
                self.logger.error(f"Failed to parse thermal data from image: {e}")
                self.temperature_data = None

        return self.temperature_data

    def get_temperature_at_point(self, x, y):
        """
        Get the temperature value at a specific point.

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Returns:
            float or None: Temperature value at the point, or None if unavailable
        """
        if self.temperature_data is None:
            return None

        # Check if cursor is within valid bounds
        if x < 0 or y < 0:
            return None

        shape = self.temperature_data.shape
        # Ensure position is within temperature data array bounds
        if (0 <= y < shape[0]) and (0 <= x < shape[1]):
            return self.temperature_data[y][x]

        return None

    def clear_temperature_data(self):
        """Clear the current temperature data."""
        self.temperature_data = None

    @staticmethod
    def convert_temperature(value, from_unit, to_unit):
        """
        Convert temperature between units.

        Args:
            value (float): Temperature value
            from_unit (str): Source unit ('C' or 'F')
            to_unit (str): Target unit ('C' or 'F')

        Returns:
            float: Converted temperature value
        """
        if from_unit == to_unit:
            return value

        if from_unit == 'C' and to_unit == 'F':
            return value * 1.8 + 32.0
        elif from_unit == 'F' and to_unit == 'C':
            return (value - 32.0) / 1.8

        return value
