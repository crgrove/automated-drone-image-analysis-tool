import numpy as np
import cv2

from algorithms.Shared.views.RangeViewer_ui import Ui_ColorRangeViewer
from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer

from PySide6.QtGui import QImage
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QDialog, QFrame


class ColorRangeRangeViewer(QDialog, Ui_ColorRangeViewer):
    """Controller for the Color Range Range Viewer Dialog supporting multiple colors."""

    def __init__(self, color_ranges):
        """
        Initializes the ColorRangeRangeViewer dialog.

        Args:
            color_ranges (list[dict]): List of color range configs, each with:
                'color_range': [min_rgb, max_rgb] where min_rgb and max_rgb are (r, g, b) tuples
                OR for backward compatibility: (min_rgb, max_rgb) tuple pair
        """
        QDialog.__init__(self)
        self.setupUi(self)
        palettes = self.generate_palettes(color_ranges)
        self.populate_image(palettes["selected"][2], True)
        self.populate_image(palettes["selected"][1], True)
        self.populate_image(palettes["selected"][0], True)
        self.populate_image(palettes["unselected"][2], False)
        self.populate_image(palettes["unselected"][1], False)
        self.populate_image(palettes["unselected"][0], False)

    def generate_palettes(self, color_ranges):
        """
        Generates color palettes as numpy arrays representing selected and unselected colors.

        Args:
            color_ranges (list[dict] | tuple): List of color range configs or legacy (min_rgb, max_rgb) tuple

        Returns:
            dict: A dictionary with numpy arrays for selected and unselected color ranges.
        """
        # Handle backward compatibility: if it's a tuple, convert to list format
        if isinstance(color_ranges, tuple) and len(color_ranges) == 2:
            # Legacy format: (min_rgb, max_rgb)
            color_ranges = [{'color_range': [color_ranges[0], color_ranges[1]]}]
        elif not isinstance(color_ranges, list):
            color_ranges = [color_ranges]

        multiplier = 2
        x_range = 180 * multiplier
        y_range = 256 * multiplier

        high = self.generate_palette(x_range, y_range, multiplier, 255)
        med = self.generate_palette(x_range, y_range, multiplier, 128)
        low = self.generate_palette(x_range, y_range, multiplier, 64)

        # Generate combined mask for all color ranges (OR logic)
        high_mask = self.generate_combined_mask(high, color_ranges)
        med_mask = self.generate_combined_mask(med, color_ranges)
        low_mask = self.generate_combined_mask(low, color_ranges)

        inverse_high_mask = cv2.bitwise_not(high_mask)
        inverse_med_mask = cv2.bitwise_not(med_mask)
        inverse_low_mask = cv2.bitwise_not(low_mask)

        selected_high = cv2.bitwise_and(high, high, mask=high_mask)
        unselected_high = cv2.bitwise_and(high, high, mask=inverse_high_mask)
        selected_med = cv2.bitwise_and(med, med, mask=med_mask)
        unselected_med = cv2.bitwise_and(med, med, mask=inverse_med_mask)
        selected_low = cv2.bitwise_and(low, low, mask=low_mask)
        unselected_low = cv2.bitwise_and(low, low, mask=inverse_low_mask)

        return {"selected": [selected_high, selected_med, selected_low],
                "unselected": [unselected_high, unselected_med, unselected_low]}

    def generate_combined_mask(self, img, color_ranges):
        """
        Generates a combined mask for pixels that match ANY of the configured color ranges.

        Args:
            img (numpy.ndarray): Palette image to be processed.
            color_ranges (list[dict]): List of color range configs with 'color_range' key.

        Returns:
            numpy.ndarray: Combined mask (0/255) where any color range matches.
        """
        combined = np.zeros(img.shape[:2], dtype=np.uint8)

        for color_config in color_ranges:
            # Handle both dict format and direct tuple format
            if isinstance(color_config, dict):
                color_range = color_config.get('color_range')
            else:
                color_range = color_config

            if not color_range or len(color_range) != 2:
                continue

            min_rgb = color_range[0]
            max_rgb = color_range[1]

            # Convert RGB to BGR for OpenCV
            cv_lower_limit = np.array([min_rgb[2], min_rgb[1], min_rgb[0]], dtype=np.uint8)
            cv_upper_limit = np.array([max_rgb[2], max_rgb[1], max_rgb[0]], dtype=np.uint8)

            # Generate mask for this color range
            mask = cv2.inRange(img, cv_lower_limit, cv_upper_limit)

            # Combine with OR logic
            combined = cv2.bitwise_or(combined, mask)

        return combined

    def generate_palette(self, x_range, y_range, multiplier, saturation):
        """
        Generates an HSL palette with a specified saturation level.

        Args:
            x_range (int): The height of the palette.
            y_range (int): The width of the palette.
            multiplier (int): Determines the size of the palette.
            saturation (int): The saturation level for the palette.

        Returns:
            numpy.ndarray: An HSL palette with the given saturation.
        """
        img = np.zeros((x_range, y_range, 3), np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        for x in range(x_range):
            for y in range(y_range):
                height = min(max(round(x / multiplier, 0), 0), 255)
                length = min(max(round(y / multiplier, 0), 0), 255)
                img[x, y] = [height, length, saturation]
        return cv2.cvtColor(img, cv2.COLOR_HLS2BGR)

    def populate_image(self, img, selected):
        """
        Adds an image to the layout as a QtImageViewer widget.

        Args:
            img (numpy.ndarray): The image to display.
            selected (bool): Determines if the image should be added to the selected or unselected layout.
        """
        image = QtImageViewer(self)
        image.setMinimumSize(QSize(190, 190))
        image.aspectRatioMode = Qt.KeepAspectRatio
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        image.setImage(qImg)
        image.setFrameShape(QFrame.NoFrame)
        if selected:
            self.selectedLayout.addWidget(image)
        else:
            self.unselectedLayout.addWidget(image)
