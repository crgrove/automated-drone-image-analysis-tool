"""
ImageHighlightController - Handles highlighting of detected pixels and masks in images.

This controller provides functionality for overlaying highlights on images to visualize
detection results, including mask-based highlighting and pixel-based highlighting.
"""

import os
import cv2
import numpy as np
import tifffile


class ImageHighlightController:
    """
    Controller for applying visual highlights to images for detection visualization.
    
    Handles both mask-based highlighting (efficient for large detection areas) and
    pixel-based highlighting (for individual detected pixels).
    """

    @staticmethod
    def apply_mask_highlight(image_array, mask_path, identifier_color=(255, 0, 255), areas_of_interest=None):
        """
        Applies a mask overlay to highlight detected pixels.

        Args:
            image_array (np.ndarray): The input image array in BGR format.
            mask_path (str): Path to the mask file (.tif or .png).
            identifier_color (tuple): RGB color tuple for highlighting (uses Object Identifier color).
            areas_of_interest (list, optional): Not used currently, but kept for future filtering.

        Returns:
            np.ndarray: The image array with mask applied.
        """
        if not mask_path or not os.path.exists(mask_path):
            return image_array

        # Load the mask depending on format
        if mask_path.lower().endswith((".tif", ".tiff")):
            # Read multi-band GeoTIFF and pull first band as mask
            data = tifffile.imread(mask_path)
            if data.ndim == 3:  # (bands, height, width)
                mask = data[0].astype(np.uint8)
            else:
                mask = data.astype(np.uint8)
        else:
            # Fallback: load grayscale PNG
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

        if mask is None:
            return image_array

        # Resize mask if needed to match image dimensions
        if mask.shape[:2] != image_array.shape[:2]:
            mask = cv2.resize(mask, (image_array.shape[1], image_array.shape[0]), interpolation=cv2.INTER_NEAREST)

        highlighted_image = image_array.copy()

        # Apply the mask - blend highlight color with original image
        # Image is in BGR format, identifier_color is RGB, so convert
        bgr_color = np.array([int(identifier_color[2]), int(identifier_color[1]), int(identifier_color[0])], dtype=np.uint8)

        # Create a blended overlay where mask pixels are highlighted
        mask_indices = mask > 0
        if np.any(mask_indices):
            # Blend with 70% original image and 30% highlight color for visibility
            alpha = 0.7  # Highlight strength
            highlighted_image[mask_indices] = (
                highlighted_image[mask_indices] * (1 - alpha) + bgr_color * alpha
            ).astype(np.uint8)

        return highlighted_image

    @staticmethod
    def highlight_aoi_pixels(image_array, areas_of_interest, highlight_color=(255, 0, 255)):
        """
        Highlights detected pixels within areas of interest.

        Args:
            image_array (np.ndarray): The input image array.
            areas_of_interest (list): List of AOI dictionaries with detected_pixels.
            highlight_color (tuple): RGB color tuple for highlighting (default: magenta).

        Returns:
            np.ndarray: The image array with highlighted pixels.
        """
        highlighted_image = image_array.copy()

        # Convert highlight color to numpy array
        highlight_color_array = np.array(highlight_color, dtype=np.uint8)

        for aoi in areas_of_interest or []:
            if "detected_pixels" in aoi and aoi["detected_pixels"]:
                for pixel in aoi["detected_pixels"]:
                    if isinstance(pixel, (list, tuple)) and len(pixel) >= 2:
                        x, y = int(pixel[0]), int(pixel[1])
                        # Check bounds
                        if 0 <= y < highlighted_image.shape[0] and 0 <= x < highlighted_image.shape[1]:
                            # Convert from BGR to RGB for display if needed
                            if len(highlighted_image.shape) == 3 and highlighted_image.shape[2] == 3:
                                highlighted_image[y, x] = highlight_color_array

        return highlighted_image

