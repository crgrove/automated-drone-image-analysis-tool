import numpy as np
import cv2

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

            # Target HSV values
            target_h, target_s, target_v = [int(x) for x in self.target_color_hsv]

            # Calculate S/V ranges
            lower_s = max(0, target_s - saturation_threshold)
            upper_s = min(255, target_s + saturation_threshold)
            lower_v = max(0, target_v - value_threshold)
            upper_v = min(255, target_v + value_threshold)

            # Calculate hue range and handle wraparound (OpenCV: H ∈ [0,179])
            if hue_threshold >= 90:
                # Select all hues
                lower_bound = np.array([0, lower_s, lower_v])
                upper_bound = np.array([179, upper_s, upper_v])
                mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
            else:
                lower_h = target_h - hue_threshold
                upper_h = target_h + hue_threshold

                if lower_h < 0:
                    # Wraps around, e.g., H=5, threshold=10
                    lower_bound1 = np.array([180 + lower_h, lower_s, lower_v])
                    upper_bound1 = np.array([179, upper_s, upper_v])
                    mask1 = cv2.inRange(hsv_image, lower_bound1, upper_bound1)

                    lower_bound2 = np.array([0, lower_s, lower_v])
                    upper_bound2 = np.array([upper_h, upper_s, upper_v])
                    mask2 = cv2.inRange(hsv_image, lower_bound2, upper_bound2)

                    mask = cv2.bitwise_or(mask1, mask2)
                elif upper_h > 179:
                    # Wraps around, e.g., H=175, threshold=10
                    lower_bound1 = np.array([lower_h, lower_s, lower_v])
                    upper_bound1 = np.array([179, upper_s, upper_v])
                    mask1 = cv2.inRange(hsv_image, lower_bound1, upper_bound1)

                    lower_bound2 = np.array([0, lower_s, lower_v])
                    upper_bound2 = np.array([upper_h - 180, upper_s, upper_v])
                    mask2 = cv2.inRange(hsv_image, lower_bound2, upper_bound2)

                    mask = cv2.bitwise_or(mask1, mask2)
                else:
                    # No wraparound
                    lower_bound = np.array([lower_h, lower_s, lower_v])
                    upper_bound = np.array([upper_h, upper_s, upper_v])
                    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            augmented_image, areas_of_interest, base_contour_count = self.circle_areas_of_interest(img, contours)

            output_path = full_path.replace(input_dir, output_dir)
            if augmented_image is not None:
                self.store_image(full_path, output_path, augmented_image)

            return AnalysisResult(full_path, output_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            print(e)
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))
