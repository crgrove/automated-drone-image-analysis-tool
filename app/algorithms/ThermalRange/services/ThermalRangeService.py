import numpy as np
import cv2
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
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
            options (dict): Additional algorithm-specific options, including 'minTemp' and 'maxTemp'.
        """
        self.logger = LoggerService()
        super().__init__('MatchedFilter', identifier, min_area, max_area, aoi_radius, combine_aois, options, True)
        self.min_temp = options['minTemp']
        self.max_temp = options['maxTemp']

    def process_image(self, img, full_path, input_dir, output_dir):
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
            temperature_c, thermal_img = thermal.parse_file(full_path)

            # Create a mask to identify areas within the specified temperature range.
            mask = np.uint8(1 * ((temperature_c > self.min_temp) & (temperature_c < self.max_temp)))

            # Find contours of the identified areas and circle areas of interest.
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)

            # Extract average temperature from detected pixels for each AOI
            temps_extracted = 0
            if areas_of_interest:
                for aoi in areas_of_interest:
                    detected_pixels = aoi.get('detected_pixels', [])

                    if len(detected_pixels) > 0:
                        # Extract temperatures for all detected pixels
                        temps = []
                        for pixel in detected_pixels:
                            x_orig, y_orig = int(pixel[0]), int(pixel[1])

                            # Transform to processing resolution if needed
                            if self.scale_factor != 1.0:
                                x = int(x_orig * self.scale_factor)
                                y = int(y_orig * self.scale_factor)
                            else:
                                x, y = x_orig, y_orig

                            # Bounds check and extract temperature
                            if 0 <= y < temperature_c.shape[0] and 0 <= x < temperature_c.shape[1]:
                                temps.append(temperature_c[y, x])

                        if len(temps) > 0:
                            # Calculate mean temperature across all detected pixels
                            temp_value = float(np.mean(temps))
                            aoi['temperature'] = temp_value
                            temps_extracted += 1
                            # Debug: Log first few temperatures
                            if temps_extracted <= 3:
                                self.logger.debug(f"AOI at {aoi['center']}: avg temperature={temp_value:.2f}°C (from {len(temps)} pixels)")
                        else:
                            aoi['temperature'] = None
                            self.logger.warning(f"AOI at {aoi['center']}: all detected pixels out of bounds")
                    else:
                        # Fallback: no detected pixels (shouldn't happen in normal flow)
                        aoi['temperature'] = None
                        self.logger.warning(f"AOI at {aoi['center']}: no detected pixels available")

                self.logger.info(f"Extracted temperature for {temps_extracted}/{len(areas_of_interest)} AOIs from {full_path}")

            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image (with temperature data for thermal)
            mask_path = None
            if areas_of_interest:
                # Convert mask to 0-255 range for storage
                mask_255 = mask * 255
                mask_path = self.store_mask(full_path, output_path, mask_255, temperature_c)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)
        except Exception as e:
            # Log and return an error if processing fails.
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
