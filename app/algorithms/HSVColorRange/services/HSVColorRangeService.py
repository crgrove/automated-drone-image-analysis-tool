import numpy as np
import cv2

from helpers.ColorUtils import ColorUtils
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from core.services.LoggerService import LoggerService


class HSVColorRangeService(AlgorithmService):
    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        self.logger = LoggerService()
        super().__init__('HSVColorRange', identifier, min_area, max_area, aoi_radius, combine_aois, options)

        self.target_color_hsv = None
        selected_color = self.options.get('selected_color')
        if selected_color is not None:
            # Ensure shape (1,1,3) for cv2.cvtColor
            rgb_color = np.uint8([[selected_color]])
            self.target_color_hsv = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)[0][0]

    def process_image(self, img, full_path, input_dir, output_dir):
        try:
            if self.target_color_hsv is None:
                return AnalysisResult(full_path, error_message="No color selected for HSV Filter")

            # Convert the image from BGR to HSV color space
            hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Check if we have new HSV ranges data
            hsv_ranges = self.options.get('hsv_ranges')
            if hsv_ranges:
                # Use precise HSV ranges from the new picker
                h, s, v = hsv_ranges['h'], hsv_ranges['s'], hsv_ranges['v']
                h_minus, h_plus = hsv_ranges['h_minus'], hsv_ranges['h_plus']
                s_minus, s_plus = hsv_ranges['s_minus'], hsv_ranges['s_plus']
                v_minus, v_plus = hsv_ranges['v_minus'], hsv_ranges['v_plus']

                # Calculate bounds in OpenCV format (H: 0-179, S: 0-255, V: 0-255)
                h_center = int(h * 179)
                s_center = int(s * 255)
                v_center = int(v * 255)

                h_low = max(0, h_center - int(h_minus * 179))
                h_high = min(179, h_center + int(h_plus * 179))
                s_low = max(0, s_center - int(s_minus * 255))
                s_high = min(255, s_center + int(s_plus * 255))
                v_low = max(0, v_center - int(v_minus * 255))
                v_high = min(255, v_center + int(v_plus * 255))

                # Handle hue wrapping if necessary
                if h_low > h_high:
                    # Hue wraps around (e.g., 350° to 10°)
                    mask1 = cv2.inRange(hsv_image,
                                        np.array([h_low, s_low, v_low], dtype=np.uint8),
                                        np.array([179, s_high, v_high], dtype=np.uint8))
                    mask2 = cv2.inRange(hsv_image,
                                        np.array([0, s_low, v_low], dtype=np.uint8),
                                        np.array([h_high, s_high, v_high], dtype=np.uint8))
                    mask = cv2.bitwise_or(mask1, mask2)
                else:
                    lower_bound = np.array([h_low, s_low, v_low], dtype=np.uint8)
                    upper_bound = np.array([h_high, s_high, v_high], dtype=np.uint8)
                    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

            # Check for old HSV window data (backward compatibility)
            elif 'hsv_window' in self.options:
                hsv_window = self.options.get('hsv_window')
                # Use precise HSV ranges from the old dialog format
                lower_bound = np.array([hsv_window['h_min'] / 2, hsv_window['s_min'] * 255 / 100,
                                       hsv_window['v_min'] * 255 / 100], dtype=np.uint8)
                upper_bound = np.array([hsv_window['h_max'] / 2, hsv_window['s_max'] * 255 / 100,
                                       hsv_window['v_max'] * 255 / 100], dtype=np.uint8)

                # Handle hue wrapping if necessary
                if hsv_window['h_min'] > hsv_window['h_max']:
                    # Hue wraps around (e.g., 350° to 10°)
                    mask1 = cv2.inRange(hsv_image,
                                        np.array([hsv_window['h_min'] / 2, hsv_window['s_min'] * 255 / 100,
                                                 hsv_window['v_min'] * 255 / 100], dtype=np.uint8),
                                        np.array([179, hsv_window['s_max'] * 255 / 100,
                                                 hsv_window['v_max'] * 255 / 100], dtype=np.uint8))
                    mask2 = cv2.inRange(hsv_image,
                                        np.array([0, hsv_window['s_min'] * 255 / 100,
                                                 hsv_window['v_min'] * 255 / 100], dtype=np.uint8),
                                        np.array([hsv_window['h_max'] / 2, hsv_window['s_max'] * 255 / 100,
                                                 hsv_window['v_max'] * 255 / 100], dtype=np.uint8))
                    mask = cv2.bitwise_or(mask1, mask2)
                else:
                    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

            else:
                # Fallback to old method
                hue_threshold = self.options.get('hue_threshold', 10)
                saturation_threshold = self.options.get('saturation_threshold', 30)
                value_threshold = self.options.get('value_threshold', 30)

                # Use the staticmethod to get HSV bounds
                hsv_ranges = ColorUtils.get_hsv_color_range(
                    self.target_color_hsv, hue_threshold, saturation_threshold, value_threshold
                )

                # Create mask(s) and combine if necessary
                mask = None
                for lower_bound, upper_bound in hsv_ranges:
                    this_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
                    if mask is None:
                        mask = this_mask
                    else:
                        mask = cv2.bitwise_or(mask, this_mask)

            # Identify contours in the masked image
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img, contours)

            # Apply hue expansion if enabled
            hue_expansion_enabled = self.options.get('hue_expansion_enabled', False)
            hue_expansion_range = self.options.get('hue_expansion_range', 0)

            if hue_expansion_enabled and hue_expansion_range > 0 and areas_of_interest:
                # Apply hue expansion to the mask
                mask = self.apply_hue_expansion(img, mask, areas_of_interest, hue_expansion_range)

                # Re-find contours with expanded mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                # Re-identify areas of interest with expanded mask
                areas_of_interest, base_contour_count = self.identify_areas_of_interest(img, contours)

            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                mask_path = self.store_mask(full_path, output_path, mask)

            # Return the mask path instead of output image path
            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
