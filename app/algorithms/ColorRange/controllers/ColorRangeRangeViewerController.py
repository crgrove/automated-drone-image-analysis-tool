import numpy as np
import cv2

from algorithms.Shared.views.RangeViewer_ui import Ui_ColorRangeViewer
from core.views.viewer.components.QtImageViewer import QtImageViewer

from PySide6.QtGui import QImage
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QDialog, QFrame


class ColorRangeRangeViewer(QDialog, Ui_ColorRangeViewer):
    """Controller for the Color Range Range Viewer Dialog."""

    def __init__(self, min_rgb, max_rgb):
        """
        Initializes the ColorRangeRangeViewer dialog.

        Args:
            min_rgb (tuple[int, int, int]): The minimum color in the selected range.
            max_rgb (tuple[int, int, int]): The maximum color in the selected range.
        """
        QDialog.__init__(self)
        self.setupUi(self)
        palettes = self.generate_palettes(min_rgb, max_rgb)
        self.populate_image(palettes["selected"][2], True)
        self.populate_image(palettes["selected"][1], True)
        self.populate_image(palettes["selected"][0], True)
        self.populate_image(palettes["unselected"][2], False)
        self.populate_image(palettes["unselected"][1], False)
        self.populate_image(palettes["unselected"][0], False)

    def generate_palettes(self, min_rgb, max_rgb):
        """
        Generates color palettes as numpy arrays representing selected and unselected colors.

        Args:
            min_rgb (tuple[int, int, int]): The minimum color in the selected range.
            max_rgb (tuple[int, int, int]): The maximum color in the selected range.

        Returns:
            dict: A dictionary with numpy arrays for selected and unselected color ranges.
        """
        cv_lower_limit = np.array([min_rgb[2], min_rgb[1], min_rgb[0]], dtype=np.uint8)
        cv_upper_limit = np.array([max_rgb[2], max_rgb[1], max_rgb[0]], dtype=np.uint8)

        multiplier = 2
        x_range = 180 * multiplier
        y_range = 256 * multiplier

        high = self.generate_palette(x_range, y_range, multiplier, 255)
        med = self.generate_palette(x_range, y_range, multiplier, 128)
        low = self.generate_palette(x_range, y_range, multiplier, 64)

        high_mask = cv2.inRange(high, cv_lower_limit, cv_upper_limit)
        med_mask = cv2.inRange(med, cv_lower_limit, cv_upper_limit)
        low_mask = cv2.inRange(low, cv_lower_limit, cv_upper_limit)

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
