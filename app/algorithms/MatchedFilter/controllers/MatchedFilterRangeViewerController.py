import numpy as np
import cv2
import spectral
import pandas as pd

from algorithms.Shared.views.RangeViewer_ui import Ui_ColorRangeViewer
from core.views.viewer.widgets.QtImageViewer import QtImageViewer

from PySide6.QtGui import QImage
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QDialog, QFrame


class MatchedFilterRangeViewer(QDialog, Ui_ColorRangeViewer):
    """Controller for the Color Match Range Viewer Dialog."""

    def __init__(self, ref_rgb, threshold):
        """
        Initializes the MatchedFilterRangeViewer dialog.

        Args:
            ref_rgb (tuple[int, int, int]): The reference color to be matched.
            threshold (float): The threshold a pixel score must meet to be flagged as a match.
        """
        QDialog.__init__(self)
        self.setupUi(self)
        palettes = self.generate_palettes(ref_rgb, threshold)
        self.populate_image(palettes["selected"][2], True)
        self.populate_image(palettes["selected"][1], True)
        self.populate_image(palettes["selected"][0], True)
        self.populate_image(palettes["unselected"][2], False)
        self.populate_image(palettes["unselected"][1], False)
        self.populate_image(palettes["unselected"][0], False)

    def generate_palettes(self, ref_rgb, threshold):
        """
        Generates color palettes as numpy arrays representing selected and unselected colors.

        Args:
            ref_rgb (tuple[int, int, int]): The reference color to be matched.
            threshold (float): The threshold a pixel score must meet to be flagged as a match.

        Returns:
            dict: A dictionary with numpy arrays for selected and unselected color ranges.
        """
        multiplier = 2
        x_range = 180 * multiplier
        y_range = 256 * multiplier

        high = self.generate_palette(x_range, y_range, multiplier, 255)
        med = self.generate_palette(x_range, y_range, multiplier, 128)
        low = self.generate_palette(x_range, y_range, multiplier, 64)

        high_mask = self.generate_mask(high, ref_rgb, threshold)
        med_mask = self.generate_mask(med, ref_rgb, threshold)
        low_mask = self.generate_mask(low, ref_rgb, threshold)

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

    def generate_mask(self, img, ref_rgb, threshold):
        """
        Generates a mask for pixels that match the reference color within the specified threshold.

        Args:
            img (numpy.ndarray): The image to be processed.
            ref_rgb (tuple[int, int, int]): The reference color to be matched.
            threshold (float): The threshold a pixel score must meet to be flagged as a match.

        Returns:
            numpy.ndarray: A mask representing pixels that match the reference color.
        """
        scores = spectral.matched_filter(img, np.array([ref_rgb[2], ref_rgb[1], ref_rgb[0]], dtype=np.uint8))
        mask = np.uint8((255 * (scores > threshold)))
        return mask

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
