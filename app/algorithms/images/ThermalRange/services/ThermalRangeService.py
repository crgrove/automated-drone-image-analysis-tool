import numpy as np
import cv2
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from core.services.LoggerService import LoggerService
from core.services.thermal.ThermalParserService import ThermalParserService


class ThermalRangeService(AlgorithmService):
    """Service that executes the Thermal Range algorithm.

    Detects and highlights areas of interest in thermal images based on
    temperature range thresholds. Extracts temperature data for detected AOIs.

    Attributes:
        min_temp: Minimum temperature threshold in Celsius.
        max_temp: Maximum temperature threshold in Celsius.
    """

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """Initialize the ThermalRangeService with specific parameters for processing thermal images.

        Args:
            identifier: RGB values for the color to highlight areas of interest.
            min_area: Minimum area in pixels for an object to qualify as an area of interest.
            max_area: Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius: Radius added to the minimum enclosing circle around an area of interest.
            combine_aois: If True, overlapping areas of interest will be combined.
            options: Additional algorithm-specific options, including 'minTemp' and 'maxTemp'.
        """
        self.logger = LoggerService()
        super().__init__('MatchedFilter', identifier, min_area, max_area, aoi_radius, combine_aois, options, True)
        self.min_temp = options['minTemp']
        self.max_temp = options['maxTemp']

    def process_image(self, img, full_path, input_dir, output_dir):
        """Process a single thermal image using the Thermal Range algorithm.

        Identifies and highlights areas of interest based on temperature
        thresholds. Extracts temperature data for each detected AOI.

        Args:
            img: The image to be processed as numpy array.
            full_path: The path to the image being analyzed.
            input_dir: The base input folder.
            output_dir: The base output folder.

        Returns:
            AnalysisResult containing the processed image path, list of areas
            of interest with temperature data, base contour count, and error
            message if any.
        """
        try:
            # Create an instance of ThermalParserService and parse the thermal image.
            thermal = ThermalParserService(dtype=np.float32)
            temperature_c, thermal_img = thermal.parse_file(full_path)

            # Create a mask to identify areas within the specified temperature range.
            mask = np.uint8(1 * ((temperature_c > self.min_temp) & (temperature_c < self.max_temp)))

            # Find contours of the identified areas and circle areas of interest.
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # Use thermal data shape (not visual image shape) for coordinate calculations
            # DJI images may be upscaled (e.g., 1280x1024) but thermal data is native (e.g., 640x512)
            areas_of_interest, base_contour_count = self.identify_areas_of_interest(temperature_c.shape, contours)

            # Extract average temperature from detected pixels for each AOI
            # Note: This must happen BEFORE coordinate scaling since pixels are in thermal space
            temps_extracted = 0
            if areas_of_interest:
                for aoi in areas_of_interest:
                    detected_pixels = aoi.get('detected_pixels', [])

                    if len(detected_pixels) > 0:
                        # Extract temperatures for all detected pixels (in thermal coordinate space)
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
                                self.logger.debug(
                                    f"AOI at {aoi['center']}: avg temperature="
                                    f"{temp_value:.2f}°C (from {len(temps)} pixels)"
                                )
                        else:
                            aoi['temperature'] = None
                            self.logger.warning(f"AOI at {aoi['center']}: all detected pixels out of bounds")
                    else:
                        # Fallback: no detected pixels (shouldn't happen in normal flow)
                        aoi['temperature'] = None
                        self.logger.warning(f"AOI at {aoi['center']}: no detected pixels available")

                self.logger.info(f"Extracted temperature for {temps_extracted}/{len(areas_of_interest)} AOIs from {full_path}")

            # Calculate scale factors if thermal resolution != visual resolution
            thermal_h, thermal_w = temperature_c.shape[:2]
            visual_h, visual_w = img.shape[:2]
            scale_x = visual_w / thermal_w
            scale_y = visual_h / thermal_h

            # Scale AOI coordinates from thermal resolution to visual resolution
            # This ensures viewer can display AOIs at correct positions
            if areas_of_interest and (scale_x != 1.0 or scale_y != 1.0):
                print(f"Info: Scaling AOI coordinates from thermal {thermal_w}x{thermal_h} to visual {visual_w}x{visual_h}")
                for aoi in areas_of_interest:
                    # Scale center coordinates
                    if 'center' in aoi:
                        aoi['center'] = (int(aoi['center'][0] * scale_x), int(aoi['center'][1] * scale_y))
                    # Scale radius
                    if 'radius' in aoi:
                        aoi['radius'] = int(aoi['radius'] * max(scale_x, scale_y))
                    # Scale detected pixels
                    if 'detected_pixels' in aoi:
                        aoi['detected_pixels'] = [(int(x * scale_x), int(y * scale_y)) for x, y in aoi['detected_pixels']]

            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image (with temperature data for thermal)
            mask_path = None
            if areas_of_interest:
                # Convert mask to 0-255 range for storage
                mask_255 = mask * 255
                # Pass visual image shape to upscale mask and thermal data for viewer compatibility
                mask_path = self.store_mask(full_path, output_path, mask_255, temperature_c, target_shape=img.shape)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)
        except Exception as e:
            # Log and return an error if processing fails.
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
