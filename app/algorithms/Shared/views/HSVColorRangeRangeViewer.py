import numpy as np
import cv2

from helpers.ColorUtils import ColorUtils
from algorithms.Shared.views.RangeViewer_ui import Ui_ColorRangeViewer
from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer

from PySide6.QtGui import QImage
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QDialog, QFrame


class HSVColorRangeRangeViewer(QDialog, Ui_ColorRangeViewer):
    """Controller for the HSV Color Range Range Viewer Dialog.

    Supports both single color (backward compatible) and multiple color ranges.
    """

    def __init__(self, target_rgb_color=None, h_range=None, s_range=None, v_range=None, hsv_ranges_list=None):
        """
        Args:
            target_rgb_color (tuple[int, int, int], optional): The base RGB color (for single color mode).
            h_range (int, optional): Hue range (for single color mode).
            s_range (int, optional): Saturation range (for single color mode).
            v_range (int, optional): Value range (for single color mode).
            hsv_ranges_list (list[dict], optional): List of HSV range configs for multi-color mode.
                Each dict should have: 'rgb', 'hue_minus', 'hue_plus', 'sat_minus', 'sat_plus', 'val_minus', 'val_plus'
                Values should be in OpenCV format (hue: 0-179, sat/val: 0-255)
        """
        QDialog.__init__(self)
        self.setupUi(self)

        # Support multiple color ranges (new mode)
        if hsv_ranges_list is not None and len(hsv_ranges_list) > 0:
            palettes = self.generate_palettes_multi(hsv_ranges_list)
        else:
            # Single color mode (backward compatible)
            if target_rgb_color is None:
                target_rgb_color = (255, 0, 0)  # Default to red
            if h_range is None:
                h_range = 20
            if s_range is None:
                s_range = 50
            if v_range is None:
                v_range = 50

            target_rgb_color = np.uint8([[target_rgb_color]])  # Shape: (1,1,3)
            target_color_hsv = cv2.cvtColor(target_rgb_color, cv2.COLOR_RGB2HSV)[0][0]
            palettes = self.generate_palettes(target_color_hsv, h_range, s_range, v_range)

        self.populate_image(palettes["selected"][2], True)
        self.populate_image(palettes["selected"][1], True)
        self.populate_image(palettes["selected"][0], True)
        self.populate_image(palettes["unselected"][2], False)
        self.populate_image(palettes["unselected"][1], False)
        self.populate_image(palettes["unselected"][0], False)

    def generate_palettes(self, target_hsv, h_range, s_range, v_range):
        """
        Generates color palettes as numpy arrays representing selected and unselected colors.

        Args:
            target_hsv (tuple[int, int, int]): The base HSV color (OpenCV range).
            h_range (int): Hue range.
            s_range (int): Saturation range.
            v_range (int): Value range.

        Returns:
            dict: A dictionary with numpy arrays for selected and unselected color ranges.
        """
        multiplier = 2
        x_range = 180 * multiplier
        y_range = 256 * multiplier

        # Assume these are HSV images
        high = self.generate_palette(x_range, y_range, multiplier, 255)
        med = self.generate_palette(x_range, y_range, multiplier, 128)
        low = self.generate_palette(x_range, y_range, multiplier, 64)

        bounds = ColorUtils.get_hsv_color_range(target_hsv, h_range, s_range, v_range)

        # Utility to combine multiple range masks
        def multi_in_range(img, bounds):
            mask = None
            for lower, upper in bounds:
                partial_mask = cv2.inRange(img, lower, upper)
                mask = partial_mask if mask is None else cv2.bitwise_or(mask, partial_mask)
            return mask

        # Generate masks for each level
        high_mask = multi_in_range(high, bounds)
        med_mask = multi_in_range(med, bounds)
        low_mask = multi_in_range(low, bounds)

        inverse_high_mask = cv2.bitwise_not(high_mask)
        inverse_med_mask = cv2.bitwise_not(med_mask)
        inverse_low_mask = cv2.bitwise_not(low_mask)

        selected_high = cv2.bitwise_and(high, high, mask=high_mask)
        unselected_high = cv2.bitwise_and(high, high, mask=inverse_high_mask)
        selected_med = cv2.bitwise_and(med, med, mask=med_mask)
        unselected_med = cv2.bitwise_and(med, med, mask=inverse_med_mask)
        selected_low = cv2.bitwise_and(low, low, mask=low_mask)
        unselected_low = cv2.bitwise_and(low, low, mask=inverse_low_mask)

        return {
            "selected": [selected_high, selected_med, selected_low],
            "unselected": [unselected_high, unselected_med, unselected_low]
        }

    def generate_palettes_multi(self, hsv_ranges_list):
        """
        Generates color palettes for multiple HSV color ranges, combining them with OR logic.

        Args:
            hsv_ranges_list (list[dict]): List of HSV range configs. Each dict should have:
                'rgb': (r, g, b) tuple
                'hue_minus', 'hue_plus': int (0-179)
                'sat_minus', 'sat_plus': int (0-255)
                'val_minus', 'val_plus': int (0-255)

        Returns:
            dict: A dictionary with numpy arrays for selected and unselected color ranges.
        """
        multiplier = 2
        x_range = 180 * multiplier
        y_range = 256 * multiplier

        # Generate base palettes
        high = self.generate_palette(x_range, y_range, multiplier, 255)
        med = self.generate_palette(x_range, y_range, multiplier, 128)
        low = self.generate_palette(x_range, y_range, multiplier, 64)

        # Generate combined mask for all color ranges (OR logic)
        high_mask = self.generate_combined_hsv_mask(high, hsv_ranges_list)
        med_mask = self.generate_combined_hsv_mask(med, hsv_ranges_list)
        low_mask = self.generate_combined_hsv_mask(low, hsv_ranges_list)

        inverse_high_mask = cv2.bitwise_not(high_mask)
        inverse_med_mask = cv2.bitwise_not(med_mask)
        inverse_low_mask = cv2.bitwise_not(low_mask)

        selected_high = cv2.bitwise_and(high, high, mask=high_mask)
        unselected_high = cv2.bitwise_and(high, high, mask=inverse_high_mask)
        selected_med = cv2.bitwise_and(med, med, mask=med_mask)
        unselected_med = cv2.bitwise_and(med, med, mask=inverse_med_mask)
        selected_low = cv2.bitwise_and(low, low, mask=low_mask)
        unselected_low = cv2.bitwise_and(low, low, mask=inverse_low_mask)

        return {
            "selected": [selected_high, selected_med, selected_low],
            "unselected": [unselected_high, unselected_med, unselected_low]
        }

    def generate_combined_hsv_mask(self, img, hsv_ranges_list):
        """
        Generates a combined mask for pixels that match ANY of the configured HSV ranges.

        Args:
            img (numpy.ndarray): HSV palette image to be processed.
            hsv_ranges_list (list[dict]): List of HSV range configs.

        Returns:
            numpy.ndarray: Combined mask (0/255) where any HSV range matches.
        """
        combined = np.zeros(img.shape[:2], dtype=np.uint8)

        for hsv_config in hsv_ranges_list:
            rgb = hsv_config.get('rgb', (255, 0, 0))
            hue_minus = hsv_config.get('hue_minus', 20)
            hue_plus = hsv_config.get('hue_plus', 20)
            sat_minus = hsv_config.get('sat_minus', 50)
            sat_plus = hsv_config.get('sat_plus', 50)
            val_minus = hsv_config.get('val_minus', 50)
            val_plus = hsv_config.get('val_plus', 50)

            # Convert RGB to HSV
            rgb_array = np.uint8([[rgb]])  # Shape: (1,1,3)
            target_hsv = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)[0][0]

            # Calculate HSV bounds
            h_center = int(target_hsv[0])
            s_center = int(target_hsv[1])
            v_center = int(target_hsv[2])

            h_low = max(0, h_center - hue_minus)
            h_high = min(179, h_center + hue_plus)
            s_low = max(0, s_center - sat_minus)
            s_high = min(255, s_center + sat_plus)
            v_low = max(0, v_center - val_minus)
            v_high = min(255, v_center + val_plus)

            # Handle hue wrapping if necessary
            if h_low > h_high:
                # Hue wraps around (e.g., 350° to 10°) - create two ranges
                bounds = [
                    (np.array([h_low, s_low, v_low], dtype=np.uint8),
                     np.array([179, s_high, v_high], dtype=np.uint8)),
                    (np.array([0, s_low, v_low], dtype=np.uint8),
                     np.array([h_high, s_high, v_high], dtype=np.uint8))
                ]
            else:
                # Normal range - single range
                bounds = [
                    (np.array([h_low, s_low, v_low], dtype=np.uint8),
                     np.array([h_high, s_high, v_high], dtype=np.uint8))
                ]

            # Generate mask for this color range
            mask = None
            for lower, upper in bounds:
                partial_mask = cv2.inRange(img, lower, upper)
                mask = partial_mask if mask is None else cv2.bitwise_or(mask, partial_mask)

            # Combine with OR logic
            if mask is not None:
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
        bgr_img = cv2.cvtColor(img, cv2.COLOR_HLS2BGR)
        return cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

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
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        image.setImage(qImg)
        image.setFrameShape(QFrame.NoFrame)
        if selected:
            self.selectedLayout.addWidget(image)
        else:
            self.unselectedLayout.addWidget(image)
