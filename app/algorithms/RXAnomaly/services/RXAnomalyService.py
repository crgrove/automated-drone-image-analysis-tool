import logging
import numpy as np
import cv2
import spectral
from scipy.stats import chi2
import traceback

from algorithms.Algorithm import AlgorithmService, AnalysisResult
from algorithms.MRMap.services.MRMapService import MRHistogram
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
                    """
                    rx_values = spectral.rx(pieces[x][y])
                    chi_values = chi2.ppf(self.chi_threshold, pieces[x][y].shape[-1])
                    masks[x][y] = np.uint8((1 * (rx_values > chi_values)))
                    """
                    histogram = MRHistogram(pieces[x][y])
                    pixels = np.array(pieces[x][y])
                    width, height = pieces[x][y].shape[:2]

                    # Quantize pixels
                    r_quantized = histogram.mapping[pixels[:, :, 0]]
                    g_quantized = histogram.mapping[pixels[:, :, 1]]
                    b_quantized = histogram.mapping[pixels[:, :, 2]]
                    quantized_pixels = np.stack((r_quantized, g_quantized, b_quantized), axis=-1)
                    reshaped_quantized_pixels = quantized_pixels.reshape((-1, 3))
                    # Reshape back to the original shape for display

                    # Calculate RX anomaly scores for quantized values
                    rx_scores = spectral.rx(reshaped_quantized_pixels, cov=np.cov(reshaped_quantized_pixels, rowvar=False))
                    rx_scores = rx_scores.reshape((width, height))

                    # Calculate chi-squared threshold for comparison
                    chi_values = chi2.ppf(self.chi_threshold, 3)  # 3 degrees of freedom for RGB

                    # Create a binary mask of anomalous pixels based on RX scores
                    masks[x][y] = np.uint8((rx_scores > chi_values)) * 255
                    histogram = None
            combined_mask = self.glueImage(masks)

            # Find contours of the identified areas and circle areas of interest.
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            augmented_image, areas_of_interest, base_contour_count = self.circleAreasOfInterest(img, contours)

            # Generate the output path and store the processed image.
            output_path = full_path.replace(input_dir, output_dir)
            if augmented_image is not None:
                self.storeImage(full_path, output_path, augmented_image)

            return AnalysisResult(full_path, output_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
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
