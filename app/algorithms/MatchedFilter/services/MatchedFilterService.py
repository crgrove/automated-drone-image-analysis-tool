import numpy as np
import cv2
import spectral
import traceback
from core.services.LoggerService import LoggerService
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult


class MatchedFilterService(AlgorithmService):
    """Service that executes the Matched Filter algorithm to detect and highlight areas matching
    one or more specific color signatures."""

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """
        Initializes the MatchedFilterService with specific parameters for the matched filter algorithm.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options. Supports:
                - 'color_configs': List of color configs (new format)
                - 'selected_color' + 'match_filter_threshold': Single color (legacy format)
        """
        self.logger = LoggerService()
        super().__init__('MatchedFilter', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        
        # Support both new multi-color format and legacy single-color format
        self.color_configs = []
        
        if 'color_configs' in options and options['color_configs']:
            # New format: multiple color configurations
            self.color_configs = options['color_configs']
        elif 'selected_color' in options and 'match_filter_threshold' in options:
            # Legacy format: single color configuration
            self.color_configs = [{
                'selected_color': options['selected_color'],
                'match_filter_threshold': options['match_filter_threshold']
            }]
        else:
            # Fallback: use identifier as single color with default threshold
            self.color_configs = [{
                'selected_color': identifier,
                'match_filter_threshold': 0.3
            }]

    def process_image(self, img, full_path, input_dir, output_dir):
        """
        Processes a single image using the Matched Filter algorithm to identify areas matching
        one or more specified color signatures.

        Args:
            img (numpy.ndarray): The image to be processed.
            full_path (str): The path to the image being analyzed.
            input_dir (str): The base input folder.
            output_dir (str): The base output folder.

        Returns:
            AnalysisResult: Contains the processed image path, list of areas of interest,
                base contour count, and error message if any.
        """
        try:
            # Start with an empty mask and combined scores
            combined_mask = np.zeros(img.shape[:2], dtype=np.uint8)
            combined_scores = np.zeros(img.shape[:2], dtype=np.float32)
            
            # Process each color configuration and combine masks with OR logic
            for color_config in self.color_configs:
                match_color = color_config.get('selected_color')
                threshold = color_config.get('match_filter_threshold', 0.3)
                
                if not match_color:
                    continue
                
                # Calculate the matched filter scores based on the specified color
                # spectral.matched_filter expects BGR format
                color_bgr = np.array([match_color[2], match_color[1], match_color[0]], dtype=np.uint8)
                scores = spectral.matched_filter(img, color_bgr)
                
                # Create mask for this color (threshold applied)
                mask = np.uint8((1 * (scores > threshold)))
                
                # Combine masks using OR logic
                combined_mask = cv2.bitwise_or(combined_mask, mask)
                
                # Keep track of maximum scores across all colors for confidence calculation
                combined_scores = np.maximum(combined_scores, scores * mask.astype(np.float32))
            
            # Identify contours in the combined masked image
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            
            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)
            
            # Add confidence scores to AOIs based on matched filter scores
            if areas_of_interest:
                areas_of_interest = self._add_confidence_scores(areas_of_interest, combined_scores, combined_mask)
            
            output_path = self._construct_output_path(full_path, input_dir, output_dir)
            
            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                # Convert mask to 0-255 range for storage
                mask_255 = combined_mask * 255
                mask_path = self.store_mask(full_path, output_path, mask_255)
            
            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)
            
        except Exception as e:
            # Log and return an error if processing fails.
            print(traceback.format_exc())
            self.logger.error(f"Error processing image {full_path}: {e}")
            return AnalysisResult(full_path, error_message=str(e))

    def _add_confidence_scores(self, areas_of_interest, filter_scores, mask):
        """
        Adds confidence scores to AOIs based on matched filter correlation values.

        Args:
            areas_of_interest (list): List of AOI dictionaries
            filter_scores (numpy.ndarray): Combined matched filter scores for each pixel
            mask (numpy.ndarray): Binary detection mask

        Returns:
            list: AOIs with added confidence scores
        """
        # Get all filter scores from detected pixels to find max for normalization
        detected_scores = filter_scores[mask > 0]
        if len(detected_scores) == 0:
            return areas_of_interest

        max_score = np.max(detected_scores)
        min_score = np.min(detected_scores)
        score_range = max_score - min_score if max_score > min_score else 1.0

        # Add confidence to each AOI
        for aoi in areas_of_interest:
            detected_pixels = aoi.get('detected_pixels', [])
            if len(detected_pixels) > 0:
                # Extract filter scores for this AOI's pixels
                # NOTE: detected_pixels are in ORIGINAL resolution, but filter_scores are in PROCESSING resolution
                # Need to transform coordinates back to processing resolution for lookup
                aoi_scores = []
                for pixel in detected_pixels:
                    x_orig, y_orig = int(pixel[0]), int(pixel[1])

                    # Transform back to processing resolution
                    if self.scale_factor != 1.0:
                        x = int(x_orig * self.scale_factor)
                        y = int(y_orig * self.scale_factor)
                    else:
                        x, y = x_orig, y_orig

                    if 0 <= y < filter_scores.shape[0] and 0 <= x < filter_scores.shape[1]:
                        aoi_scores.append(filter_scores[y, x])

                if len(aoi_scores) > 0:
                    # Calculate mean filter score for this AOI
                    mean_score = np.mean(aoi_scores)

                    # Normalize to 0-100 scale (higher score = better match = higher confidence)
                    normalized_score = ((mean_score - min_score) / score_range) * 100.0

                    # Add confidence fields to AOI
                    aoi['confidence'] = round(normalized_score, 1)
                    aoi['score_type'] = 'match'
                    aoi['raw_score'] = round(float(mean_score), 3)
                    aoi['score_method'] = 'mean'
                else:
                    # No valid pixels, set low confidence
                    aoi['confidence'] = 0.0
                    aoi['score_type'] = 'match'
                    aoi['raw_score'] = 0.0
                    aoi['score_method'] = 'mean'
            else:
                # No detected pixels, set low confidence
                aoi['confidence'] = 0.0
                aoi['score_type'] = 'match'
                aoi['raw_score'] = 0.0
                aoi['score_method'] = 'mean'

        return areas_of_interest
