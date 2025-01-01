import numpy as np
import cv2
from algorithms.Algorithm import AlgorithmService, AnalysisResult
from core.services.LoggerService import LoggerService
from core.services.ThermalParserService import ThermalParserService


class ThermalRangeService(AlgorithmService):
    """Service that executes the Thermal Range algorithm to detect and highlight areas of interest in thermal images."""

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """
        Initializes the ThermalRangeService with specific parameters for processing thermal images.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options, including 'minTemp', 'maxTemp', and 'colorMap'.
        """
        self.logger = LoggerService()
        super().__init__('MatchedFilter', identifier, min_area, max_area, aoi_radius, combine_aois, options, True)
        self.min_temp = options['minTemp']
        self.max_temp = options['maxTemp']
        self.color_map = options['colorMap']

    def processImage(self, img, full_path, input_dir, output_dir):
        """
        Processes a single thermal image using the Thermal Range algorithm, identifying and highlighting areas
        of interest based on temperature thresholds.

        Args:
            img (numpy.ndarray): The image to be processed.
            full_path (str): The path to the image being analyzed.
            input_dir (str): The base input folder.
            output_dir (str): The base output folder.

        Returns:
            AnalysisResult: Contains the processed image path, list of areas of interest, base contour count, and error message if any.
        """
        try:
            # Create an instance of ThermalParserService and parse the thermal image.
            thermal = ThermalParserService(dtype=np.float32)
            temperature_c, thermal_img = thermal.parseFile(full_path, self.color_map)

            # Create a mask to identify areas within the specified temperature range.
            mask = np.uint8(1 * ((temperature_c > self.min_temp) & (temperature_c < self.max_temp)))

            # Find contours of the identified areas and circle areas of interest.
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            augmented_image, areas_of_interest, base_contour_count = self.circleAreasOfInterest(thermal_img, contours)

            # Generate the output path and store the processed image.
            output_path = full_path.replace(input_dir, output_dir)
            if augmented_image is not None:
                self.storeImage(full_path, output_path, augmented_image, temperature_c)

            return AnalysisResult(full_path, output_path, areas_of_interest, base_contour_count)

        except Exception as e:
            # Log and return an error if processing fails.
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
