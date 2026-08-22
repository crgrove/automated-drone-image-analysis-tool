"""
AOICompositeService - Builds the multi-zoom AOI composite image.

Produces the single image used by the PDF report for each flagged AOI: the
north-up rotated full image on top, with 6x and 3x zoomed views of the AOI
below it, joined by connector lines. Shared by the PDF generator and the
CalTopo photo export so both produce identical composites.
"""

import math
import cv2
import numpy as np

from core.services.LoggerService import LoggerService


class AOICompositeService:
    """
    Service for creating multi-zoom composite images of AOIs.

    All image arrays are BGR (OpenCV convention). Rotated full images are
    cached per (cache_key, bearing) so multiple AOIs on the same image only
    rotate once; call clear_cache_for() after finishing an image to free memory.
    """

    def __init__(self, logger=None):
        """
        Initialize the composite service.

        Args:
            logger: Optional LoggerService instance.
        """
        self.logger = logger or LoggerService()
        self._rotated_image_cache = {}

    def create_composite(self, img_array, aoi, bearing, identifier_color, cache_key=None):
        """
        Create the full multi-zoom composite for an AOI (same layout as the PDF report).

        Args:
            img_array: Original image as numpy array (BGR)
            aoi: AOI dictionary with 'center' and 'radius'
            bearing: Drone bearing in degrees for north-up rotation
            identifier_color: RGB tuple for the AOI circle
            cache_key: Optional cache key for rotated image caching

        Returns:
            Composite image array (BGR), or None if it could not be created
        """
        full_img, full_aoi_pos = self.create_full_rotated_image(
            img_array, aoi, bearing, identifier_color, cache_key=cache_key
        )
        medium_img, medium_aoi_pos = self.create_zoomed_aoi_image(
            img_array, aoi, 3, bearing, identifier_color, draw_circle=False, cache_key=cache_key
        )
        closeup_img, closeup_aoi_pos = self.create_zoomed_aoi_image(
            img_array, aoi, 6, bearing, identifier_color, draw_circle=False, cache_key=cache_key
        )

        if full_img is None or medium_img is None or closeup_img is None:
            return None

        return self.create_composite_with_connectors(
            full_img, full_aoi_pos,
            medium_img, medium_aoi_pos,
            closeup_img, closeup_aoi_pos,
            aoi['radius']
        )

    def rotate_image_north_up(self, img_array, bearing, cache_key=None):
        """
        Rotate image so north is up. Uses caching to avoid re-rotating the same image.

        Args:
            img_array: Image as numpy array
            bearing: Drone bearing in degrees (0-360)
            cache_key: Optional cache key for this image (to enable caching)

        Returns:
            Rotated image array
        """
        if bearing is None:
            return img_array

        # Check cache if cache_key provided
        if cache_key is not None:
            cache_entry = (cache_key, bearing)
            if cache_entry in self._rotated_image_cache:
                return self._rotated_image_cache[cache_entry]

        height, width = img_array.shape[:2]
        center = (width / 2, height / 2)

        # Rotate by -bearing to make north up
        rotation_matrix = cv2.getRotationMatrix2D(center, -bearing, 1.0)

        # Calculate new dimensions to fit rotated image
        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))

        # Adjust rotation matrix for translation
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]

        # Perform rotation
        rotated = cv2.warpAffine(img_array, rotation_matrix, (new_width, new_height),
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

        # Cache the result if cache_key provided
        if cache_key is not None:
            cache_entry = (cache_key, bearing)
            self._rotated_image_cache[cache_entry] = rotated

        return rotated

    def transform_aoi_center(self, aoi_center, bearing, img_width, img_height):
        """
        Transform AOI center coordinates after image rotation using the same matrix as cv2.warpAffine.

        Args:
            aoi_center: Original (x, y) center
            bearing: Rotation angle in degrees
            img_width: Original image width
            img_height: Original image height

        Returns:
            Transformed (x, y) center in rotated image
        """
        if bearing is None:
            return aoi_center

        # Create the same rotation matrix as used in rotate_image_north_up
        center = (img_width / 2, img_height / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, -bearing, 1.0)

        # Calculate new dimensions
        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])
        new_width = int((img_height * sin) + (img_width * cos))
        new_height = int((img_height * cos) + (img_width * sin))

        # Adjust rotation matrix for translation (same as image rotation)
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]

        # Apply the transformation to the AOI point
        aoi_point = np.array([[aoi_center]], dtype=np.float32)
        transformed_point = cv2.transform(aoi_point, rotation_matrix)
        new_x, new_y = transformed_point[0][0]

        return (int(new_x), int(new_y))

    def create_full_rotated_image(self, img_array, aoi, bearing, identifier_color, cache_key=None):
        """
        Create a full rotated image (0x zoom) with AOI marked, cropped to fit without stretching.

        Args:
            img_array: Original full image array
            aoi: AOI dictionary
            bearing: Drone bearing for north rotation
            identifier_color: RGB tuple for AOI circle
            cache_key: Optional cache key for rotated image caching

        Returns:
            Tuple of (cropped_rotated_image, aoi_position_in_cropped_image)
        """
        try:
            # Rotate the full image (will use cache if available)
            rotated_img = self.rotate_image_north_up(img_array, bearing, cache_key=cache_key)
            height, width = img_array.shape[:2]
            rot_height, rot_width = rotated_img.shape[:2]

            # Transform AOI center to rotated coordinates
            transformed_center = self.transform_aoi_center(aoi['center'], bearing, width, height)
            x, y = transformed_center
            radius = aoi['radius']

            # Calculate crop to fit page width while maintaining aspect ratio
            # Target: 7.5 inch width, ~3.5 inch height (for top half of page)
            target_aspect = 7.5 / 3.5  # Width / Height ratio

            # Calculate crop dimensions maintaining aspect ratio
            crop_width = rot_width
            crop_height = int(crop_width / target_aspect)

            # If calculated height exceeds image, adjust
            if crop_height > rot_height:
                crop_height = rot_height
                crop_width = int(crop_height * target_aspect)

            # Ensure AOI is in the crop - center crop around AOI
            crop_x = max(0, min(x - crop_width // 2, rot_width - crop_width))
            crop_y = max(0, min(y - crop_height // 2, rot_height - crop_height))

            # Crop the rotated image
            cropped = rotated_img[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width].copy()

            # Calculate AOI position in cropped image
            aoi_x_in_crop = x - crop_x
            aoi_y_in_crop = y - crop_y

            # Draw AOI circle on the cropped image
            color_bgr = (identifier_color[2], identifier_color[1], identifier_color[0])
            cv2.circle(cropped, (aoi_x_in_crop, aoi_y_in_crop), radius, color_bgr, 3)

            return cropped, (aoi_x_in_crop, aoi_y_in_crop)

        except Exception as e:
            self.logger.error(f"Error creating full rotated image: {e}")
            return None, None

    def create_zoomed_aoi_image(self, img_array, aoi, zoom_level, bearing, identifier_color, draw_circle=True, cache_key=None):
        """
        Create a zoomed view of an AOI with optional connector line.

        Args:
            img_array: Original image array
            aoi: AOI dictionary
            zoom_level: Zoom factor (2, 3, 4, 10, or 'closeup')
            bearing: Drone bearing for north rotation
            identifier_color: RGB tuple for AOI circle
            draw_circle: Whether to draw the AOI circle
            cache_key: Optional cache key for rotated image caching

        Returns:
            Tuple of (zoomed_image_array, aoi_position_in_crop) or None
        """
        try:
            # First rotate the image (will use cache if available)
            rotated_img = self.rotate_image_north_up(img_array, bearing, cache_key=cache_key)
            height, width = img_array.shape[:2]
            rot_height, rot_width = rotated_img.shape[:2]

            # Transform AOI center to rotated coordinates
            transformed_center = self.transform_aoi_center(aoi['center'], bearing, width, height)
            x, y = transformed_center
            radius = aoi['radius']

            # Calculate crop size based on zoom level
            # Use larger multipliers for better context
            if zoom_level == 2:
                crop_radius = radius * 8  # Show good context around AOI
            elif zoom_level == 3:
                crop_radius = radius * 3
            elif zoom_level == 4:
                crop_radius = radius * 5  # Moderate zoom
            elif zoom_level == 6:
                crop_radius = radius * 6  # Moderate zoom for 6x
            elif zoom_level == 10:
                crop_radius = int(radius * 1.5)
            else:  # closeup
                crop_radius = int(radius * 1.1)

            # Calculate crop bounds centered on AOI
            sx = max(0, int(x - crop_radius))
            sy = max(0, int(y - crop_radius))
            ex = min(rot_width, int(x + crop_radius))
            ey = min(rot_height, int(y + crop_radius))

            # Crop the image
            cropped = rotated_img[sy:ey, sx:ex].copy()

            # Calculate AOI position in cropped image
            aoi_x_in_crop = int(x - sx)
            aoi_y_in_crop = int(y - sy)

            # Draw AOI circle on the image (if requested)
            if draw_circle:
                color_bgr = (identifier_color[2], identifier_color[1], identifier_color[0])  # RGB to BGR
                cv2.circle(cropped, (aoi_x_in_crop, aoi_y_in_crop), radius, color_bgr, 3)

            return cropped, (aoi_x_in_crop, aoi_y_in_crop)

        except Exception as e:
            self.logger.error(f"Error creating zoomed AOI image: {e}")
            return None, None

    def create_composite_with_connectors(self, full_img, full_aoi_pos, medium_img, medium_aoi_pos, closeup_img, closeup_aoi_pos, aoi_radius):
        """
        Create a composite image with all three zoom levels and connector lines between them.

        Args:
            full_img: 0x full rotated image
            full_aoi_pos: AOI position in full image
            medium_img: 3x zoomed image
            medium_aoi_pos: AOI position in medium image
            closeup_img: 6x zoomed image
            closeup_aoi_pos: AOI position in closeup image
            aoi_radius: Radius of the AOI circle

        Returns:
            Composite image with connector lines
        """
        try:
            # Get dimensions
            full_h, full_w = full_img.shape[:2]
            medium_h, medium_w = medium_img.shape[:2]
            closeup_h, closeup_w = closeup_img.shape[:2]

            # Calculate composite dimensions
            # Use full image width as reference
            composite_w = full_w

            # Calculate target dimensions for bottom images (each takes half width)
            bottom_target_w = composite_w // 2

            # Scale medium image to fit half width while maintaining aspect ratio
            medium_scale = bottom_target_w / medium_w
            medium_scaled_h = int(medium_h * medium_scale)
            medium_scaled_w = bottom_target_w
            medium_scaled = cv2.resize(medium_img, (medium_scaled_w, medium_scaled_h), interpolation=cv2.INTER_AREA)
            medium_aoi_scaled = (int(medium_aoi_pos[0] * medium_scale), int(medium_aoi_pos[1] * medium_scale))

            # Scale closeup image to fit half width while maintaining aspect ratio
            closeup_scale = bottom_target_w / closeup_w
            closeup_scaled_h = int(closeup_h * closeup_scale)
            closeup_scaled_w = bottom_target_w
            closeup_scaled = cv2.resize(closeup_img, (closeup_scaled_w, closeup_scaled_h), interpolation=cv2.INTER_AREA)
            closeup_aoi_scaled = (int(closeup_aoi_pos[0] * closeup_scale), int(closeup_aoi_pos[1] * closeup_scale))

            # Calculate composite height
            max_bottom_h = max(medium_scaled_h, closeup_scaled_h)
            composite_h = full_h + max_bottom_h + 20  # 20px gap

            # Create white canvas
            composite = np.ones((composite_h, composite_w, 3), dtype=np.uint8) * 255

            # Place full image at top (already full width)
            composite[0:full_h, 0:full_w] = full_img

            # Place closeup (6x) image bottom left (fill left half)
            closeup_y = full_h + 20
            closeup_x = 0
            composite[closeup_y:closeup_y + closeup_scaled_h, closeup_x:closeup_x + closeup_scaled_w] = closeup_scaled

            # Place medium (3x) image bottom right (fill right half)
            medium_y = full_h + 20
            medium_x = composite_w // 2
            composite[medium_y:medium_y + medium_scaled_h, medium_x:medium_x + medium_scaled_w] = medium_scaled

            # Calculate AOI positions in composite image
            full_aoi_composite = (full_aoi_pos[0], full_aoi_pos[1])
            medium_aoi_composite = (medium_x + medium_aoi_scaled[0], medium_y + medium_aoi_scaled[1])
            closeup_aoi_composite = (closeup_x + closeup_aoi_scaled[0], closeup_y + closeup_aoi_scaled[1])

            # Helper function to calculate line endpoint at circle edge
            def calculate_circle_edge_point(start_pt, circle_center, circle_radius):
                # Calculate direction vector
                dx = circle_center[0] - start_pt[0]
                dy = circle_center[1] - start_pt[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance == 0:
                    return circle_center

                # Normalize and scale to circle edge
                scale = (distance - circle_radius) / distance
                end_x = int(start_pt[0] + dx * scale)
                end_y = int(start_pt[1] + dy * scale)
                return (end_x, end_y)

            # Draw connector lines to edge of AOI circle
            # Medium to full (straight line to circle edge)
            medium_line_end = calculate_circle_edge_point(medium_aoi_composite, full_aoi_composite, aoi_radius)
            cv2.line(composite, medium_aoi_composite, medium_line_end, (255, 0, 255), 3)

            # Closeup to full (straight line to circle edge)
            closeup_line_end = calculate_circle_edge_point(closeup_aoi_composite, full_aoi_composite, aoi_radius)
            cv2.line(composite, closeup_aoi_composite, closeup_line_end, (255, 0, 255), 3)

            return composite

        except Exception as e:
            self.logger.error(f"Error creating composite image: {e}")
            # Return full image as fallback
            return full_img

    def clear_cache_for(self, cache_key):
        """
        Clear cached rotated images for a specific source image.

        Args:
            cache_key: The cache key used when rotating (typically the image path)
        """
        keys_to_remove = [key for key in self._rotated_image_cache.keys() if key[0] == cache_key]
        for key in keys_to_remove:
            del self._rotated_image_cache[key]

    def clear_cache(self):
        """Clear all cached rotated images."""
        self._rotated_image_cache.clear()
