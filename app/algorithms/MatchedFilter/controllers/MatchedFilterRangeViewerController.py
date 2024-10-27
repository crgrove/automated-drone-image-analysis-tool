import numpy as np
import cv2
import spectral
import pandas as pd

from algorithms.Shared.views.RangeViewer_ui import Ui_ColorRangeViewer
from core.views.components.QtImageViewer import QtImageViewer

from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QFrame


class MatchedFilterRangeViewer(QDialog, Ui_ColorRangeViewer):
    """Controller for the Color Match Ranger Viewer Dialog"""

    def __init__(self, ref_rgb, threshold):
        """
        __init__ constructor for the dialog

        :Tuple(int, int, int) ref_rgb: The reference color to be matched
        :float threshold: The threshold a pixel score must meet to be flagged as a match
        """
        QDialog.__init__(self)
        self.setupUi(self)
        palettes = self.generatePalettes(ref_rgb, threshold)
        self.populateImage(palettes["selected"][2], True)
        self.populateImage(palettes["selected"][1], True)
        self.populateImage(palettes["selected"][0], True)
        self.populateImage(palettes["unselected"][2], False)
        self.populateImage(palettes["unselected"][1], False)
        self.populateImage(palettes["unselected"][0], False)

    def generatePalettes(self, ref_rgb, threshold):
        """
        generatePalettes generates numpy.ndarrays representing selected and unselected colors

        :Tuple(int, int, int) ref_rgb: The reference color to be matched
        :float threshold: The threshold a pixel score must meet to be flagged as a match
        :return Dictionary: numpy.ndarrays representing the selected and unselected color ranges
        """

        # How big do we want the palettes to be
        multiplier = 2
        # 180 Hue values
        x_range = 180 * multiplier
        # 256 Light values
        y_range = 256 * multiplier

        # generate the base palettes
        high = self.generatePalette(x_range, y_range, multiplier, 255)
        med = self.generatePalette(x_range, y_range, multiplier, 128)
        low = self.generatePalette(x_range, y_range, multiplier, 64)

        # create the masks representing the selected and unselected colors
        high_mask = self.generateMask(high, ref_rgb, threshold)
        med_mask = self.generateMask(med, ref_rgb, threshold)
        low_mask = self.generateMask(low, ref_rgb, threshold)

        inverse_high_mask = cv2.bitwise_not(high_mask)
        inverse_med_mask = cv2.bitwise_not(med_mask)
        inverse_low_mask = cv2.bitwise_not(low_mask)
        # apply the masks to the base palettes
        selected_high = cv2.bitwise_and(high, high, mask=high_mask)
        unselected_high = cv2.bitwise_and(high, high, mask=inverse_high_mask)
        selected_med = cv2.bitwise_and(med, med, mask=med_mask)
        unselected_med = cv2.bitwise_and(med, med, mask=inverse_med_mask)
        selected_low = cv2.bitwise_and(low, low, mask=low_mask)
        unselected_low = cv2.bitwise_and(low, low, mask=inverse_low_mask)
        return {"selected": [selected_high, selected_med, selected_low], "unselected": [unselected_high, unselected_med, unselected_low]}

    def generateMask(self, img, ref_rgb, threshold):
        """
        generateMask generates numpy.ndarrays with a mask representing pixels that are a match for the reference color

        :numpy.ndarray img: numpy.ndarray representing the subject image
        Tuple(int, int, int) ref_rgb: The reference color to be matched
        :float threshold: The threshold a pixel score must meet to be flagged as a match
        :return numpy.ndarray: numpy.ndarray representing the selected pixels
        """
        scores = spectral.matched_filter(img, np.array([ref_rgb[2], ref_rgb[1], ref_rgb[0]], dtype=np.uint8))
        mask = np.uint8((255 * (scores > threshold)))
        return mask

    def generatePalette(self, x_range, y_range, multiplier, saturation):
        """
        generatePalette generate numpy.ndarray representing the HSL palette at a given saturation

        :Int x_range: the height of the palette
        :Int y_range: the width of the palette
        :return numpy.ndarray: numpy.ndarray representing the HSL palette
        """
        img = np.zeros((x_range, y_range, 3), np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        for x in range(0, x_range):
            for y in range(0, y_range):
                height = round(x / multiplier, 0)
                length = round(y / multiplier, 0)
                img[x, y] = [height, length, saturation]
        return cv2.cvtColor(img, cv2.COLOR_HLS2BGR)

    def populateImage(self, img, selected):
        """
        populateImage generates a QtImageViewer and adds it to an existing layout

        :numpy.ndarray img: numpy.ndarray representation of the image
        :Boolean selected: determines which layout to add the widget to
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
