import numpy as np
import cv2
import traceback
from core.services.LoggerService import LoggerService
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult


class ColorRangeService(AlgorithmService):
    """Service that executes the Color Range algorithm to detect and highlight areas within a specific RGB color range."""

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """
        Initializes the ColorRangeService with specific parameters for processing color ranges.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options, including 'color_range' (min and max RGB values).
        """
        self.logger = LoggerService()
        super().__init__('ColorRange', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.min_rgb = options['color_range'][0]
        self.max_rgb = options['color_range'][1]

    def process_image(self, img, full_path, input_dir, output_dir):
        """
        Processes a single image to identify areas within a specific RGB color range.

        Args:
            img (numpy.ndarray): The image to be processed.
            full_path (str): The path to the image being analyzed.
            input_dir (str): The base input folder.
            output_dir (str): The base output folder.

        Returns:
            AnalysisResult: Contains the processed image path, list of areas of interest, base contour count, and error message if any.
        """
        try:
            # Define the color range boundaries
            cv_lower_limit = np.array([self.min_rgb[2], self.min_rgb[1], self.min_rgb[0]], dtype=np.uint8)
            cv_upper_limit = np.array([self.max_rgb[2], self.max_rgb[1], self.max_rgb[0]], dtype=np.uint8)

            # Find pixels within the specified color range
            mask = cv2.inRange(img, cv_lower_limit, cv_upper_limit)

            # Identify contours in the masked image
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)
            output_path = self._construct_output_path(full_path, input_dir, output_dir)
            
            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                mask_path = self.store_mask(full_path, output_path, mask)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)
        
        except Exception as e:
            # Log and return an error if processing fails
            print(traceback.format_exc())
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
