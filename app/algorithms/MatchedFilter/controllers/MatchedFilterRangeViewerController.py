import numpy as np
import cv2
import spectral
import pandas as pd

from algorithms.Shared.views.RangeViewer_ui import Ui_ColorRangeViewer
from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer

from PySide6.QtGui import QImage
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QDialog, QFrame


class MatchedFilterRangeViewer(QDialog, Ui_ColorRangeViewer):
    """Controller for the Matched Filter Range Viewer Dialog supporting multiple colors."""

    def __init__(self, color_configs):
        """
        Initialize the MatchedFilterRangeViewer dialog.

        Args:
            color_configs (list[dict]): List of configs with keys:
                'selected_color': (r,g,b), 'match_filter_threshold': float
        """
        QDialog.__init__(self)
        self.setupUi(self)
        palettes = self.generate_palettes(color_configs)
        self.populate_image(palettes["selected"][2], True)
        self.populate_image(palettes["selected"][1], True)
        self.populate_image(palettes["selected"][0], True)
        self.populate_image(palettes["unselected"][2], False)
        self.populate_image(palettes["unselected"][1], False)
        self.populate_image(palettes["unselected"][0], False)

    def generate_palettes(self, color_configs):
        """
        Generates color palettes as numpy arrays representing selected and unselected colors.

        Args:
            color_configs (list[dict]): List of color configs

        Returns:
            dict: A dictionary with numpy arrays for selected and unselected color ranges.
        """
        multiplier = 2
        x_range = 180 * multiplier
        y_range = 256 * multiplier

        high = self.generate_palette(x_range, y_range, multiplier, 255)
        med = self.generate_palette(x_range, y_range, multiplier, 128)
        low = self.generate_palette(x_range, y_range, multiplier, 64)

        high_mask = self.generate_combined_mask(high, color_configs)
        med_mask = self.generate_combined_mask(med, color_configs)
        low_mask = self.generate_combined_mask(low, color_configs)

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

    def generate_combined_mask(self, img, color_configs):
        """
        Generates a combined mask for pixels that match ANY of the configured colors.

        Args:
            img (numpy.ndarray): Palette image to be processed.
            color_configs (list[dict]): List with 'selected_color' and 'match_filter_threshold'.

        Returns:
            numpy.ndarray: Combined mask (0/255) where any color meets its threshold.
        """
        combined = np.zeros(img.shape[:2], dtype=np.uint8)
        for cfg in color_configs:
            rgb = cfg.get('selected_color')
            threshold = float(cfg.get('match_filter_threshold', 0.3))
            if rgb is None:
                continue
            scores = spectral.matched_filter(img, np.array([rgb[2], rgb[1], rgb[0]], dtype=np.uint8))
            mask = (scores > threshold).astype(np.uint8) * 255
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
