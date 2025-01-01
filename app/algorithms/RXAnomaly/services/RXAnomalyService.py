import logging
import numpy as np
import math
import cv2
import spectral
import scipy
from scipy.stats import chi2
import traceback

from algorithms.Algorithm import AlgorithmService, AnalysisResult
from core.services.LoggerService import LoggerService
from helpers.ColorUtils import ColorUtils


class RXAnomalyService(AlgorithmService):
    """Service that executes the RX Anomaly algorithm for detecting anomalies in spectral images."""

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """
        Initializes the RXAnomalyService with specific parameters for anomaly detection.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options, including 'sensitivity' and 'segments'.
        """
        self.logger = LoggerService()
        super().__init__('RXAnomaly', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.chi_threshold = self.getThreshold(options['sensitivity'])
        self.segments = options['segments']

    def processImage(self, img, full_path, input_dir, output_dir):
        """
        Processes a single image using the RX Anomaly algorithm.

        Args:
            img (numpy.ndarray): The image to be processed.
            full_path (str): The path to the image being analyzed.
            input_dir (str): The base input folder.
            output_dir (str): The base output folder.

        Returns:
            AnalysisResult: Contains the processed image path, list of areas of interest, base contour count, and error message if any.
        """
        try:
            masks = pieces = self.splitImage(img, self.segments)
            for x in range(len(pieces)):
                for y in range(len(pieces[x])):
                    rx_values = spectral.rx(pieces[x][y])
                    chi_values = chi2.ppf(self.chi_threshold, pieces[x][y].shape[-1])
                    masks[x][y] = np.uint8((1 * (rx_values > chi_values)))
            combined_mask = self.glueImage(masks)

            # Find contours of the identified areas and circle areas of interest.
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            augmented_image, areas_of_interest, base_contour_count = self.circleAreasOfInterest(img, contours)

            # Generate the output path and store the processed image.
            output_path = full_path.replace(input_dir, output_dir)
            if augmented_image is not None:
                self.storeImage(full_path, output_path, augmented_image)

            return AnalysisResult(full_path, output_path, areas_of_interest, base_contour_count)

        except Exception as e:
            print(traceback.format_exc())
            return AnalysisResult(full_path, error_message=str(e))

    def getThreshold(self, sensitivity):
        """
        Calculates the chi-squared threshold based on a sensitivity value.

        Args:
            sensitivity (int): Sensitivity value to convert to chi-squared threshold.

        Returns:
            float: The calculated chi-squared threshold.
        """
        return 1 - float("." + ("1".zfill(sensitivity + 5)))

    def splitImage(self, img, segments):
        """
        Divides a single image into multiple segments based on the specified number of segments.

        Args:
            img (numpy.ndarray): The image to be divided into segments.
            segments (int): The number of segments to split the image into.

        Returns:
            list: A list of lists containing numpy.ndarrays representing the segments of the original image.
        """
        h, w, channels = img.shape
        pieces = []
        if segments == 2:
            w_size = math.ceil(w / 2)
            pieces.append([img[:, :w_size], img[:, w - w_size:]])
        elif segments == 4:
            w_size = math.ceil(w / 2)
            h_size = math.ceil(h / 2)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w - w_size:]],
                [img[h_size:, :w_size], img[h_size:, w - w_size:]]
            ])
        elif segments == 6:
            w_size = math.ceil(w / 3)
            h_size = math.ceil(h / 2)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w_size:w_size * 2], img[:h_size, w_size * 2:]],
                [img[h_size:, :w_size], img[h_size:, w_size:w_size * 2], img[h_size:, w_size * 2:]]
            ])
        elif segments == 9:
            w_size = math.ceil(w / 3)
            h_size = math.ceil(h / 3)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w_size:w_size * 2], img[:h_size, w_size * 2:]],
                [img[h_size:h_size * 2, :w_size], img[h_size:h_size * 2, w_size:w_size * 2], img[h_size:h_size * 2, w_size * 2:]],
                [img[h_size * 2:, :w_size], img[h_size * 2:, w_size:w_size * 2], img[h_size * 2:, w_size * 2:]]
            ])
        elif segments == 16:
            w_size = math.ceil(w / 4)
            h_size = math.ceil(h / 4)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w_size:w_size * 2], img[:h_size, w_size * 2:w_size * 3], img[:h_size, w_size * 3:]],
                [img[h_size:h_size * 2, :w_size], img[h_size:h_size * 2, w_size:w_size * 2], img[h_size:h_size * 2, w_size * 2:w_size * 3],
                 img[h_size:h_size * 2, w_size * 3:]],
                [img[h_size * 2:h_size * 3, :w_size], img[h_size * 2:h_size * 3, w_size:w_size * 2], img[h_size * 2:h_size * 3, w_size * 2:w_size * 3],
                 img[h_size * 2:h_size * 3, w_size * 3:]],
                [img[h_size * 3:, :w_size], img[h_size * 3:, w_size:w_size * 2], img[h_size * 3:, w_size * 2:w_size * 3], img[h_size * 3:, w_size * 3:]]
            ])
        elif segments == 25:
            w_size = math.ceil(w / 5)
            h_size = math.ceil(h / 5)
            pieces.extend([
                [img[:h_size, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size:h_size * 2, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size * 2:h_size * 3, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size * 3:h_size * 4, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size * 4:, i * w_size:(i + 1) * w_size] for i in range(5)]
            ])
        elif segments == 36:
            w_size = math.ceil(w / 6)
            h_size = math.ceil(h / 6)
            pieces.extend([
                [img[:h_size, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size:h_size * 2, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 2:h_size * 3, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 3:h_size * 4, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 4:h_size * 5, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 5:, i * w_size:(i + 1) * w_size] for i in range(6)]
            ])
        else:
            pieces.append([img])
        return pieces

    def glueImage(self, pieces):
        """
        Combines the segments of an image into a single image.

        Args:
            pieces (list): A list of lists containing numpy.ndarrays representing the segments of the image.

        Returns:
            numpy.ndarray: The combined image.
        """
        rows = [cv2.hconcat(row) for row in pieces]
        return cv2.vconcat(rows)
