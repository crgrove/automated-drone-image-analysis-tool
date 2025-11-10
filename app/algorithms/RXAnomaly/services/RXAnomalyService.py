import logging
import numpy as np
import cv2
import spectral
from scipy.stats import chi2
import traceback

from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from core.services.LoggerService import LoggerService


class RXAnomalyService(AlgorithmService):
    """Service that executes the RX Anomaly algorithm for detecting anomalies in spectral images.

    Uses Reed-Xiaoli (RX) anomaly detection algorithm to identify anomalous
    pixels based on statistical analysis in CIE LAB color space.

    Attributes:
        chi_threshold: Chi-squared threshold for anomaly detection.
        segments: Number of image segments for processing.
    """

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """Initialize the RXAnomalyService with specific parameters for anomaly detection.

        Args:
            identifier: RGB values for the color to highlight areas of interest.
            min_area: Minimum area in pixels for an object to qualify as an area of interest.
            max_area: Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius: Radius added to the minimum enclosing circle around an area of interest.
            combine_aois: If True, overlapping areas of interest will be combined.
            options: Additional algorithm-specific options, including 'sensitivity' and 'segments'.
        """
        self.logger = LoggerService()
        super().__init__('RXAnomaly', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.chi_threshold = self.get_threshold(options['sensitivity'])
        self.segments = options['segments']

    def process_image(self, img, full_path, input_dir, output_dir):
        """Process a single image using the RX Anomaly algorithm.

        Converts image to CIE LAB color space, splits into segments, applies
        RX anomaly detection, and identifies areas of interest with confidence scores.

        Args:
            img: The image to be processed as numpy array.
            full_path: The path to the image being analyzed.
            input_dir: The base input folder.
            output_dir: The base output folder.

        Returns:
            AnalysisResult containing the processed image path, list of areas
            of interest, base contour count, and error message if any.
        """
        try:
            # Convert to CIE LAB color space for more perceptually uniform analysis
            lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

            # Split the LAB image into segments for RX processing
            masks = pieces = self.split_image(lab_img, self.segments)
            rx_values_segments = [[None for _ in range(len(pieces[0]))] for _ in range(len(pieces))]

            for x in range(len(pieces)):
                for y in range(len(pieces[x])):
                    rx_values = spectral.rx(pieces[x][y])
                    chi_values = chi2.ppf(self.chi_threshold, pieces[x][y].shape[-1])
                    masks[x][y] = np.uint8((1 * (rx_values > chi_values)))
                    # Store RX values for confidence calculation
                    rx_values_segments[x][y] = rx_values

            combined_mask = self.glue_image(masks)
            # Glue RX values together for confidence scoring
            combined_rx_values = self.glue_image(rx_values_segments)

            # Find contours of the identified areas and circle areas of interest.
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)

            # Add confidence scores to AOIs based on RX values
            if areas_of_interest:
                areas_of_interest = self._add_confidence_scores(areas_of_interest, combined_rx_values, combined_mask)
            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                mask_path = self.store_mask(full_path, output_path, combined_mask)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            # print(traceback.format_exc())
            return AnalysisResult(full_path, error_message=str(e))

    def get_threshold(self, sensitivity):
        """Calculate the chi-squared threshold based on a sensitivity value.

        Args:
            sensitivity: Sensitivity value to convert to chi-squared threshold.

        Returns:
            The calculated chi-squared threshold as float.
        """
        return 1 - float("." + ("1".zfill(sensitivity + 5)))

    def _add_confidence_scores(self, areas_of_interest, rx_values, mask):
        """Add confidence scores to AOIs based on RX anomaly detector values.

        Args:
            areas_of_interest: List of AOI dictionaries.
            rx_values: RX detector values for each pixel as numpy array.
            mask: Binary detection mask as numpy array.

        Returns:
            List of AOIs with added confidence scores.
        """
        # Get all RX values from detected pixels to find max for normalization
        detected_rx_values = rx_values[mask > 0]
        if len(detected_rx_values) == 0:
            return areas_of_interest

        max_rx_value = np.max(detected_rx_values)
        min_rx_value = np.min(detected_rx_values)
        rx_range = max_rx_value - min_rx_value if max_rx_value > min_rx_value else 1.0

        # Add confidence to each AOI
        for aoi in areas_of_interest:
            detected_pixels = aoi.get('detected_pixels', [])
            if len(detected_pixels) > 0:
                # Extract RX values for this AOI's pixels
                # NOTE: detected_pixels are in ORIGINAL resolution, but rx_values are in PROCESSING resolution
                # Need to transform coordinates back to processing resolution for lookup
                aoi_rx_values = []
                for pixel in detected_pixels:
                    x_orig, y_orig = int(pixel[0]), int(pixel[1])

                    # Transform back to processing resolution
                    if self.scale_factor != 1.0:
                        x = int(x_orig * self.scale_factor)
                        y = int(y_orig * self.scale_factor)
                    else:
                        x, y = x_orig, y_orig

                    if 0 <= y < rx_values.shape[0] and 0 <= x < rx_values.shape[1]:
                        aoi_rx_values.append(rx_values[y, x])

                if len(aoi_rx_values) > 0:
                    # Calculate mean RX value for this AOI
                    mean_rx = np.mean(aoi_rx_values)

                    # Normalize to 0-100 scale (higher RX value = higher anomaly confidence)
                    normalized_score = ((mean_rx - min_rx_value) / rx_range) * 100.0

                    # Add confidence fields to AOI
                    aoi['confidence'] = round(normalized_score, 1)
                    aoi['score_type'] = 'anomaly'
                    aoi['raw_score'] = round(float(mean_rx), 3)
                    aoi['score_method'] = 'mean'
                else:
                    # No valid pixels, set low confidence
                    aoi['confidence'] = 0.0
                    aoi['score_type'] = 'anomaly'
                    aoi['raw_score'] = 0.0
                    aoi['score_method'] = 'mean'
            else:
                # No detected pixels, set low confidence
                aoi['confidence'] = 0.0
                aoi['score_type'] = 'anomaly'
                aoi['raw_score'] = 0.0
                aoi['score_method'] = 'mean'

        return areas_of_interest
