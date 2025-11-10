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
        # Store for backward compatibility
        selected_color = self.options.get('selected_color')
        if selected_color is not None:
            # Ensure shape (1,1,3) for cv2.cvtColor
            rgb_color = np.uint8([[selected_color]])
            self.target_color_hsv = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)[0][0]

    def _create_mask_from_hsv_ranges(self, hsv_image, hsv_ranges):
        """
        Create a mask from HSV range data.
        
        Args:
            hsv_image: Image in HSV color space
            hsv_ranges: Dict with h, s, v, h_minus, h_plus, s_minus, s_plus, v_minus, v_plus
        
        Returns:
            numpy.ndarray: Binary mask
        """
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
            return cv2.bitwise_or(mask1, mask2)
        else:
            lower_bound = np.array([h_low, s_low, v_low], dtype=np.uint8)
            upper_bound = np.array([h_high, s_high, v_high], dtype=np.uint8)
            return cv2.inRange(hsv_image, lower_bound, upper_bound)

    def process_image(self, img, full_path, input_dir, output_dir):
        try:
            # Convert the image from BGR to HSV color space
            hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Check if we have multiple HSV configs (new format)
            hsv_configs = self.options.get('hsv_configs')
            if hsv_configs:
                # Handle string format
                if isinstance(hsv_configs, str):
                    from ast import literal_eval
                    hsv_configs = literal_eval(hsv_configs)
                
                # Combine multiple HSV ranges with OR logic
                mask = None
                for hsv_config in hsv_configs:
                    if isinstance(hsv_config, dict):
                        hsv_ranges = hsv_config.get('hsv_ranges')
                        if isinstance(hsv_ranges, str):
                            from ast import literal_eval
                            hsv_ranges = literal_eval(hsv_ranges)
                        
                        if hsv_ranges:
                            this_mask = self._create_mask_from_hsv_ranges(hsv_image, hsv_ranges)
                            if mask is None:
                                mask = this_mask
                            else:
                                mask = cv2.bitwise_or(mask, this_mask)
                
                if mask is None:
                    return AnalysisResult(full_path, error_message="No valid HSV ranges configured")
                
                # Use first color for confidence scoring (backward compatibility)
                if hsv_configs and isinstance(hsv_configs[0], dict):
                    first_config = hsv_configs[0]
                    selected_color = first_config.get('selected_color')
                    if selected_color:
                        if isinstance(selected_color, str):
                            from ast import literal_eval
                            selected_color = literal_eval(selected_color)
                        rgb_color = np.uint8([[selected_color]])
                        self.target_color_hsv = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)[0][0]

            # Check if we have single HSV ranges data (legacy format)
            elif 'hsv_ranges' in self.options and self.options.get('hsv_ranges'):
                hsv_ranges = self.options.get('hsv_ranges')
                if isinstance(hsv_ranges, str):
                    from ast import literal_eval
                    hsv_ranges = literal_eval(hsv_ranges)
                
                if hsv_ranges:
                    mask = self._create_mask_from_hsv_ranges(hsv_image, hsv_ranges)

            # Check for old HSV window data (backward compatibility)
            elif 'hsv_window' in self.options and self.options.get('hsv_window'):
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
                # Fallback to old method (requires target_color_hsv)
                if self.target_color_hsv is None:
                    return AnalysisResult(full_path, error_message="No color selected for HSV Filter")
                
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
            
            # Ensure mask is defined
            if mask is None:
                return AnalysisResult(full_path, error_message="No valid HSV configuration found")

            # Calculate HSV distance for confidence scoring
            # Only calculate for detected pixels to save computation
            hsv_distances = self._calculate_hsv_distances(hsv_image, self.target_color_hsv, mask)

            # Identify contours in the masked image
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img, contours)

            # Add confidence scores to AOIs based on HSV distance
            if areas_of_interest:
                areas_of_interest = self._add_confidence_scores(areas_of_interest, hsv_distances, mask)

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

    def _calculate_hsv_distances(self, hsv_image, target_hsv, mask):
        """
        Calculate HSV distance from each pixel to the target color.
        Only calculates for detected pixels (where mask > 0).

        Args:
            hsv_image (numpy.ndarray): Image in HSV color space
            target_hsv (numpy.ndarray): Target HSV color [H, S, V]
            mask (numpy.ndarray): Binary detection mask

        Returns:
            numpy.ndarray: Distance values for each pixel (same shape as mask)
        """
        # Initialize distance array
        distances = np.zeros(hsv_image.shape[:2], dtype=np.float32)

        # Extract HSV channels
        h, s, v = hsv_image[:, :, 0], hsv_image[:, :, 1], hsv_image[:, :, 2]
        target_h, target_s, target_v = target_hsv

        # Calculate hue distance (circular, 0-179 in OpenCV)
        # Use circular distance for hue
        h_diff = np.abs(h.astype(np.float32) - float(target_h))
        h_diff = np.minimum(h_diff, 179 - h_diff)  # Circular distance
        h_dist = h_diff / 179.0  # Normalize to 0-1

        # Calculate saturation and value distances (linear, 0-255)
        s_dist = np.abs(s.astype(np.float32) - float(target_s)) / 255.0
        v_dist = np.abs(v.astype(np.float32) - float(target_v)) / 255.0

        # Combined Euclidean distance in HSV space
        # Weight hue more heavily as it's the primary discriminator
        distances = np.sqrt(2.0 * h_dist**2 + s_dist**2 + v_dist**2)

        # Only keep distances for detected pixels
        distances = distances * (mask > 0)

        return distances

    def _add_confidence_scores(self, areas_of_interest, hsv_distances, mask):
        """
        Adds confidence scores to AOIs based on HSV color distances.
        Lower distance = better color match = higher confidence.

        Args:
            areas_of_interest (list): List of AOI dictionaries
            hsv_distances (numpy.ndarray): HSV distance values for each pixel
            mask (numpy.ndarray): Binary detection mask

        Returns:
            list: AOIs with added confidence scores
        """
        # Get all distances from detected pixels to find max for normalization
        detected_distances = hsv_distances[mask > 0]
        if len(detected_distances) == 0:
            return areas_of_interest

        max_distance = np.max(detected_distances)
        min_distance = np.min(detected_distances)
        distance_range = max_distance - min_distance if max_distance > min_distance else 1.0

        # Add confidence to each AOI
        for aoi in areas_of_interest:
            detected_pixels = aoi.get('detected_pixels', [])
            if len(detected_pixels) > 0:
                # Extract distances for this AOI's pixels
                # NOTE: detected_pixels are in ORIGINAL resolution, but hsv_distances are in PROCESSING resolution
                # Need to transform coordinates back to processing resolution for lookup
                aoi_distances = []
                for pixel in detected_pixels:
                    x_orig, y_orig = int(pixel[0]), int(pixel[1])

                    # Transform back to processing resolution
                    if self.scale_factor != 1.0:
                        x = int(x_orig * self.scale_factor)
                        y = int(y_orig * self.scale_factor)
                    else:
                        x, y = x_orig, y_orig

                    if 0 <= y < hsv_distances.shape[0] and 0 <= x < hsv_distances.shape[1]:
                        aoi_distances.append(hsv_distances[y, x])

                if len(aoi_distances) > 0:
                    # Calculate mean distance for this AOI
                    mean_distance = np.mean(aoi_distances)

                    # Normalize to 0-100 scale (INVERTED: lower distance = better match = higher confidence)
                    normalized_score = ((max_distance - mean_distance) / distance_range) * 100.0

                    # Add confidence fields to AOI
                    aoi['confidence'] = round(normalized_score, 1)
                    aoi['score_type'] = 'color_distance'
                    aoi['raw_score'] = round(float(mean_distance), 3)
                    aoi['score_method'] = 'mean'
                else:
                    # No valid pixels, set low confidence
                    aoi['confidence'] = 0.0
                    aoi['score_type'] = 'color_distance'
                    aoi['raw_score'] = 0.0
                    aoi['score_method'] = 'mean'
            else:
                # No detected pixels, set low confidence
                aoi['confidence'] = 0.0
                aoi['score_type'] = 'color_distance'
                aoi['raw_score'] = 0.0
                aoi['score_method'] = 'mean'

        return areas_of_interest
