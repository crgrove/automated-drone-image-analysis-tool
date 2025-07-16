import numpy as np
import cv2

from helpers.ColorUtils import ColorUtils
from algorithms.Shared.views.RangeViewer_ui import Ui_ColorRangeViewer
from core.views.components.QtImageViewer import QtImageViewer

from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QFrame


class HSVColorRangeRangeViewer(QDialog, Ui_ColorRangeViewer):
    """Controller for the HSV Color Range Range Viewer Dialog."""

    def __init__(self, target_rgb_color, h_range, s_range, v_range):
        """
        Args:
            target_rgb_color (tuple[int, int, int]): The base RGB color.
            h_range (int): Hue range.
            s_range (int): Saturation range.
            v_range (int): Value range.
        """
        QDialog.__init__(self)
        self.setupUi(self)

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
            "selected":   [selected_high, selected_med, selected_low],
            "unselected": [unselected_high, unselected_med, unselected_low]
        }

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
