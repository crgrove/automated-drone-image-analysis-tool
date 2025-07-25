import numpy as np
import cv2

from helpers.ColorUtils import ColorUtils
from algorithms.Algorithm import AlgorithmService, AnalysisResult
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

            # Get thresholds safely
            hue_threshold = self.options.get('hue_threshold', 10)
            saturation_threshold = self.options.get('saturation_threshold', 30)
            value_threshold = self.options.get('value_threshold', 30)

            # Convert the image from BGR to HSV color space
            hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

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

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            augmented_image, areas_of_interest, base_contour_count = self.circle_areas_of_interest(img, contours)

            output_path = full_path.replace(input_dir, output_dir)
            if augmented_image is not None:
                self.store_image(full_path, output_path, augmented_image)

            return AnalysisResult(full_path, output_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
