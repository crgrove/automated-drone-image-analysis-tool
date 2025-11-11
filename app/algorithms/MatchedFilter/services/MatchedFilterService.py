import numpy as np
import cv2
import spectral
from core.services.LoggerService import LoggerService
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult


class MatchedFilterService(AlgorithmService):
    """Service that executes the Matched Filter algorithm to detect and highlight areas matching a specific color."""

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """
        Initializes the MatchedFilterService with specific parameters for the matched filter algorithm.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options, including 'selected_color' and 'match_filter_threshold'.
        """
        self.logger = LoggerService()
        super().__init__('MatchedFilter', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.match_color = options['selected_color']
        self.threshold = options['match_filter_threshold']

    def process_image(self, img, full_path, input_dir, output_dir):
        """
        Processes a single image using the Matched Filter algorithm to identify areas matching the specified color.

        Args:
            img (numpy.ndarray): The image to be processed.
            full_path (str): The path to the image being analyzed.
            input_dir (str): The base input folder.
            output_dir (str): The base output folder.

        Returns:
            AnalysisResult: Contains the processed image path, list of areas of interest, base contour count, and error message if any.
        """
        try:
            # Calculate the matched filter scores based on the specified color.
            scores = spectral.matched_filter(img, np.array([self.match_color[2], self.match_color[1], self.match_color[0]], dtype=np.uint8))
            mask = np.uint8((1 * (scores > self.threshold)))

            # Identify contours in the masked image
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)

            # Apply hue expansion if enabled
            hue_expansion_enabled = self.options.get('hue_expansion_enabled', False)
            hue_expansion_range = self.options.get('hue_expansion_range', 0)

            if hue_expansion_enabled and hue_expansion_range > 0 and areas_of_interest:
                # Convert mask to 0-255 range for hue expansion
                mask_255 = mask * 255

                # Apply hue expansion to the mask
                mask_255 = self.apply_hue_expansion(img, mask_255, areas_of_interest, hue_expansion_range)

                # Convert back to 0-1 range
                mask = (mask_255 / 255).astype(np.uint8)

                # Re-find contours with expanded mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                # Re-identify areas of interest with expanded mask
                areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)

            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                # Convert mask to 0-255 range for storage
                mask_255 = mask * 255
                mask_path = self.store_mask(full_path, output_path, mask_255)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            # Log and return an error if processing fails.
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
