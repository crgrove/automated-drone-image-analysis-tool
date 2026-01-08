import numpy as np
import cv2
import os
import math
import shutil
import json
import zlib
import base64
import tifffile
from pathlib import Path
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from helpers.MetaDataHelper import MetaDataHelper

from core.services.cache.ThumbnailCacheService import ThumbnailCacheService
from core.services.cache.ColorCacheService import ColorCacheService
from core.services.cache.TemperatureCacheService import TemperatureCacheService
from core.services.LoggerService import LoggerService


class AlgorithmService:
    """Base class for algorithm services that provides methods for processing images."""

    def __init__(self, name, identifier_color, min_area, max_area, aoi_radius, combine_aois, options, is_thermal=False):
        """
        Initializes the AlgorithmService with the necessary parameters.

        Args:
            name (str): The name of the algorithm to be used for analysis.
            identifier_color (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options.
            is_thermal (bool, optional): Indicates if this is a thermal image algorithm. Defaults to False.
        """
        self.logger = LoggerService()
        self.name = name
        self.identifier_color = identifier_color
        self.min_area = min_area
        self.max_area = max_area
        self.aoi_radius = aoi_radius
        self.combine_aois = combine_aois
        self.options = options
        self.is_thermal = is_thermal
        self.scale_factor = 1.0  # Default: no scaling

    def set_scale_factor(self, scale_factor):
        """
        Set the scale factor for coordinate transformation from processing to original resolution.

        Args:
            scale_factor: The scale factor used when downscaling the image for processing.
                A value of 1.0 means no scaling, 0.5 means half resolution, etc.
        """
        self.scale_factor = scale_factor

    def transform_to_original_coords(self, x, y):
        """
        Transform coordinates from processing resolution back to original resolution.

        Args:
            x: X coordinate in processing resolution.
            y: Y coordinate in processing resolution.

        Returns:
            Tuple[int, int]: Tuple of (x, y) coordinates in original resolution as integers.
        """
        if self.scale_factor == 1.0:
            return int(x), int(y)
        inverse_scale = 1.0 / self.scale_factor
        return int(x * inverse_scale), int(y * inverse_scale)

    def transform_contour_to_original(self, contour):
        """
        Transform a contour from processing resolution back to original resolution.

        Args:
            contour: Contour in processing resolution as numpy array.

        Returns:
            numpy.ndarray: Contour scaled to original resolution as numpy array of int32.
        """
        if self.scale_factor == 1.0:
            return contour
        inverse_scale = 1.0 / self.scale_factor
        return (contour * inverse_scale).astype(np.int32)

    def process_image(self, img, full_path, input_dir, output_dir):
        """
        Processes a single image file using the algorithm.

        Args:
            img (numpy.ndarray): The image to be processed.
            full_path (str): The path to the image being analyzed.
            input_dir (str): The base input directory.
            output_dir (str): The base output directory.

        Returns:
            tuple: A tuple containing:
                - numpy.ndarray: Processed image.
                - list: List of areas of interest.
        """
        raise NotImplementedError

    def collect_pixels_of_interest(self, mask):
        """
        Collect pixel coordinates from a binary mask.

        Args:
            mask: Binary mask array where non-zero values indicate pixels of interest.

        Returns:
            numpy.ndarray: Array of (x, y) coordinates of pixels of interest.
                Shape is (N, 2) where N is the number of pixels.
        """
        coords = np.argwhere(mask > 0)
        return coords[:, [1, 0]]

    def identify_areas_of_interest(self, img_or_shape, contours):
        """
        Calculates areas of interest from contours without modifying the input image.

        Args:
            img_or_shape (numpy.ndarray | tuple | list): The image array or its shape (H, W, [C]).
            contours (list): List of contours.

        Returns:
            tuple: (areas_of_interest, base_contour_count)
                - areas_of_interest (list): Final list of AOIs after optional combining.
                - base_contour_count (int): Count of original valid contours before combining.
        """
        if len(contours) == 0:
            return None, None

        # Robustly derive height and width whether we received an image or a shape tuple
        try:
            if hasattr(img_or_shape, 'shape'):
                height, width = int(img_or_shape.shape[0]), int(img_or_shape.shape[1])
            else:
                height, width = int(img_or_shape[0]), int(img_or_shape[1])
        except Exception:
            # Fallback: try tuple conversion then slice
            h_w = tuple(img_or_shape)[:2]
            height, width = int(h_w[0]), int(h_w[1])
        areas_of_interest = []
        temp_mask = np.zeros((height, width), dtype=np.uint8)
        base_contour_count = 0

        # Store original detected pixels for each valid contour
        original_pixels_mask = np.zeros((height, width), dtype=np.uint8)

        # First pass: filter contours and optionally mark them for combining
        for cnt in contours:
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, thickness=-1)
            contour_area = cv2.countNonZero(mask)

            if contour_area >= self.min_area and (self.max_area == 0 or contour_area <= self.max_area):
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius) + self.aoi_radius
                base_contour_count += 1

                # Add to mask for later combining
                cv2.circle(temp_mask, center, radius, 255, -1)

                # Also keep track of original pixels
                original_pixels_mask = cv2.bitwise_or(original_pixels_mask, mask)

                if not self.combine_aois:
                    # Store the contour points for drawing the boundary
                    contour_points = cnt.reshape(-1, 2).tolist()

                    # Get the detected pixels for this AOI
                    detected_pixels = np.argwhere(mask > 0)
                    detected_pixels_list = detected_pixels[:, [1, 0]].tolist() if len(detected_pixels) > 0 else []

                    # Use actual detected pixel count for area
                    area = len(detected_pixels_list)

                    areas_of_interest.append({
                        'center': center,
                        'radius': radius,
                        'area': area,
                        'contour': contour_points,
                        'detected_pixels': detected_pixels_list
                    })

        # Second pass: combine AOIs if needed
        if self.combine_aois:
            while True:
                new_contours, _ = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                for cnt in new_contours:
                    (x, y), radius = cv2.minEnclosingCircle(cnt)
                    center = (int(x), int(y))
                    radius = int(radius)
                    cv2.circle(temp_mask, center, radius, 255, -1)
                if len(new_contours) == len(contours):
                    contours = new_contours
                    break
                contours = new_contours

            for cnt in contours:
                mask = np.zeros((height, width), dtype=np.uint8)
                cv2.drawContours(mask, [cnt], -1, 255, thickness=-1)
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                # Store the contour points for drawing the boundary
                contour_points = cnt.reshape(-1, 2).tolist()

                # Get the original detected pixels that belong to this combined AOI
                aoi_pixels_mask = cv2.bitwise_and(original_pixels_mask, mask)
                aoi_pixels = np.argwhere(aoi_pixels_mask > 0)
                aoi_pixels_list = aoi_pixels[:, [1, 0]].tolist() if len(aoi_pixels) > 0 else []

                # Use actual detected pixel count, not the expanded circle area
                area = len(aoi_pixels_list)

                areas_of_interest.append({
                    'center': center,
                    'radius': radius,
                    'area': area,
                    'contour': contour_points,
                    'detected_pixels': aoi_pixels_list
                })

        # Sort for consistent ordering
        areas_of_interest.sort(key=lambda item: (item['center'][1], item['center'][0]))

        return areas_of_interest, base_contour_count

    def transform_aois_to_original_resolution(self, areas_of_interest):
        """
        Transform AOI coordinates from processing resolution back to original resolution.

        This should be called at the end of process_image() after all processing that
        requires processing-resolution coordinates is complete (e.g., hue expansion,
        confidence score calculation).

        Args:
            areas_of_interest: List of AOI dictionaries with coordinates at processing resolution.

        Returns:
            List of AOI dictionaries with coordinates transformed to original resolution.
        """
        if self.scale_factor == 1.0 or not areas_of_interest:
            return areas_of_interest

        inverse_scale = 1.0 / self.scale_factor
        transformed_aois = []

        for aoi in areas_of_interest:
            transformed_aoi = aoi.copy()

            # Transform center coordinates
            if 'center' in transformed_aoi:
                x, y = transformed_aoi['center']
                transformed_aoi['center'] = self.transform_to_original_coords(x, y)

            # Transform radius (radius scales linearly)
            if 'radius' in transformed_aoi:
                transformed_aoi['radius'] = int(transformed_aoi['radius'] * inverse_scale)

            # Transform contour points
            if 'contour' in transformed_aoi and transformed_aoi['contour']:
                # Convert list to numpy array, transform, then convert back
                contour_array = np.array(transformed_aoi['contour'], dtype=np.float32)
                transformed_contour = self.transform_contour_to_original(contour_array)
                transformed_aoi['contour'] = transformed_contour.tolist()

            # Transform detected pixels
            if 'detected_pixels' in transformed_aoi and transformed_aoi['detected_pixels']:
                transformed_pixels = []
                for pixel in transformed_aoi['detected_pixels']:
                    x, y = pixel[0], pixel[1]
                    transformed_pixels.append(self.transform_to_original_coords(x, y))
                transformed_aoi['detected_pixels'] = transformed_pixels

            transformed_aois.append(transformed_aoi)

        return transformed_aois

    def apply_hue_expansion(self, img, mask, areas_of_interest, hue_range):
        """
        Expands the pixel detection mask based on hue similarity within AOI circles.

        This method analyzes each AOI's detected pixels, calculates their average hue,
        and then finds all pixels within the AOI circle that have a similar hue value
        (within the specified range). This is useful for capturing color variations
        that might have been missed by the initial detection algorithm.

        Args:
            img (numpy.ndarray): The original BGR image.
            mask (numpy.ndarray): The current detection mask (binary, 0 or 255).
            areas_of_interest (list): List of AOI dictionaries with 'center', 'radius', and 'detected_pixels'.
            hue_range (int): The +/- hue range in OpenCV format (0-179).

        Returns:
            numpy.ndarray: Expanded mask with additional pixels.
        """
        if areas_of_interest is None or len(areas_of_interest) == 0:
            return mask

        # Convert image to HSV once for efficiency
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Create expanded mask starting with the original
        expanded_mask = mask.copy()

        for aoi in areas_of_interest:
            detected_pixels = aoi.get('detected_pixels', [])
            if len(detected_pixels) == 0:
                continue

            # Calculate average hue of detected pixels
            hue_values = []
            for px, py in detected_pixels:
                # Ensure pixel coordinates are within image bounds
                if 0 <= py < hsv_img.shape[0] and 0 <= px < hsv_img.shape[1]:
                    hue_values.append(hsv_img[py, px, 0])  # H channel

            if len(hue_values) == 0:
                continue

            avg_hue = int(np.mean(hue_values))

            # Calculate hue range with wraparound handling
            hue_min = avg_hue - hue_range
            hue_max = avg_hue + hue_range

            # Create circular ROI mask for this AOI
            center = aoi['center']
            radius = aoi['radius']
            roi_mask = np.zeros(mask.shape[:2], dtype=np.uint8)
            cv2.circle(roi_mask, center, radius, 255, -1)

            # Get all pixels within the circular ROI
            roi_y, roi_x = np.where(roi_mask == 255)

            # Check each pixel in ROI for hue match
            for py, px in zip(roi_y, roi_x):
                pixel_hue = hsv_img[py, px, 0]

                # Handle hue wraparound (hue is circular: 0-179 in OpenCV)
                if hue_min < 0:
                    # Wraparound at lower bound (e.g., hue=5, range=10 -> -5 to 15)
                    # Matches if hue >= (180 + hue_min) OR hue <= hue_max
                    if pixel_hue >= (180 + hue_min) or pixel_hue <= hue_max:
                        expanded_mask[py, px] = 255
                elif hue_max >= 180:
                    # Wraparound at upper bound (e.g., hue=175, range=10 -> 165 to 185)
                    # Matches if hue >= hue_min OR hue <= (hue_max - 180)
                    if pixel_hue >= hue_min or pixel_hue <= (hue_max - 180):
                        expanded_mask[py, px] = 255
                else:
                    # No wraparound - simple range check
                    if hue_min <= pixel_hue <= hue_max:
                        expanded_mask[py, px] = 255

        return expanded_mask

    def generate_aoi_cache(
        self,
        img: np.ndarray,
        image_path: str,
        areas_of_interest: list,
        output_dir: str,
        thermal: bool = False
    ) -> None:
        """Generate and cache thumbnails and color information for all AOIs.

        Called after process_image() while the image is still in memory, allowing
        for efficient thumbnail extraction without reloading the image from disk.

        Args:
            img: The image array (already in memory from detection).
            image_path: Path to the source image file.
            areas_of_interest: List of AOI dictionaries from detection.
            output_dir: Output directory where cache folders will be created.
            thermal: Whether this is a thermal image. Defaults to False.
        """
        import colorsys

        try:
            if not areas_of_interest:
                return

            # Set up thumbnail cache directory (still needed for disk storage)
            thumbnail_cache_dir = Path(output_dir) / '.thumbnails'
            thumbnail_cache_dir.mkdir(parents=True, exist_ok=True)

            # Initialize cache services
            # Note: Color and temperature cache data goes to XML, not JSON files
            thumbnail_service = ThumbnailCacheService(dataset_cache_dir=str(thumbnail_cache_dir))
            color_service = ColorCacheService()  # In-memory only - data goes to XML
            temperature_service = TemperatureCacheService() if thermal else None  # In-memory only - data goes to XML

            # Convert BGR to RGB for color calculations
            # The img from detection is typically in BGR (OpenCV default)
            if len(img.shape) == 3 and img.shape[2] == 3:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img_rgb = img

            height, width = img_rgb.shape[:2]

            # Process each AOI
            for aoi in areas_of_interest:
                try:
                    # Extract thumbnail from in-memory image
                    center = aoi.get('center')
                    radius = aoi.get('radius', 50)

                    if not center:
                        continue

                    cx, cy = center
                    crop_radius = radius + 10  # Add padding

                    # Calculate crop bounds
                    x1 = max(0, int(cx - crop_radius))
                    y1 = max(0, int(cy - crop_radius))
                    x2 = min(width, int(cx + crop_radius))
                    y2 = min(height, int(cy + crop_radius))

                    # Extract region from in-memory image
                    thumbnail_region = img[y1:y2, x1:x2]

                    if thumbnail_region.size == 0:
                        continue

                    # Resize to target thumbnail size
                    # Use INTER_AREA for downscaling - faster and better quality than INTER_LANCZOS4
                    thumbnail_resized = cv2.resize(thumbnail_region, (180, 180), interpolation=cv2.INTER_AREA)

                    # Convert to RGB if needed (some algorithms work in different color spaces)
                    if len(thumbnail_resized.shape) == 2:
                        # Grayscale
                        thumbnail_rgb = cv2.cvtColor(thumbnail_resized, cv2.COLOR_GRAY2RGB)
                    elif thumbnail_resized.shape[2] == 4:
                        # RGBA
                        thumbnail_rgb = cv2.cvtColor(thumbnail_resized, cv2.COLOR_BGRA2RGB)
                    else:
                        # BGR to RGB
                        thumbnail_rgb = cv2.cvtColor(thumbnail_resized, cv2.COLOR_BGR2RGB)

                    # Save thumbnail to dataset cache
                    thumbnail_service.save_thumbnail_from_array(image_path, aoi, thumbnail_rgb, thumbnail_cache_dir)

                    # Calculate representative color directly from in-memory image
                    # This avoids creating AOIService/ImageService which reads metadata from disk
                    color_result = self._calculate_aoi_representative_color(img_rgb, aoi)
                    if color_result:
                        color_info = {
                            'rgb': color_result['rgb'],
                            'hex': color_result['hex'],
                            'hue_degrees': color_result['hue_degrees']
                        }
                        # Store color info directly in AOI dict for XML export (no JSON file)
                        aoi['color_info'] = color_info
                        # Also store in cache service for memory tracking (will be written to XML later)
                        color_service.save_color_info(image_path, aoi, color_info)

                    # Temperature is already in aoi dict, just track in cache service
                    if 'temperature' in aoi and aoi['temperature'] is not None:
                        temperature_service.save_temperature(image_path, aoi, aoi['temperature'])

                except Exception as e:
                    # Log error but continue processing other AOIs
                    self.logger.error(f"Error caching AOI at {center}: {e}")
                    continue

            # Note: Color and temperature cache data is now stored in AOI dicts and will be written to XML
            # No need to save JSON files - data goes directly to XML via AnalyzeService

        except Exception as e:
            # Don't fail the entire detection if cache generation fails
            self.logger.error(f"Error generating AOI cache: {e}")

    def _calculate_aoi_representative_color(self, img_rgb: np.ndarray, aoi: dict) -> dict:
        """
        Calculate a representative color for an AOI directly from the in-memory image.

        This method avoids creating AOIService/ImageService which would read metadata
        from disk and potentially cause memory errors on large files.

        Args:
            img_rgb: RGB image array (not BGR).
            aoi: AOI dictionary with 'center', 'radius', and optionally 'detected_pixels'.

        Returns:
            dict or None: {
                'rgb': (r, g, b),           # Vibrant marker color (0-255)
                'hex': '#rrggbb',           # Hex color string
                'hue_degrees': int,         # Hue in degrees (0-360)
                'avg_rgb': (r, g, b)        # Original average RGB
            } or None if calculation fails.
        """
        import colorsys

        try:
            height, width = img_rgb.shape[:2]

            center = aoi.get('center', [0, 0])
            radius = aoi.get('radius', 0)
            cx, cy = int(center[0]), int(center[1])

            # Collect RGB values within the AOI
            colors = []

            # If we have detected pixels, use those
            if 'detected_pixels' in aoi and aoi['detected_pixels']:
                for pixel in aoi['detected_pixels']:
                    if isinstance(pixel, (list, tuple)) and len(pixel) >= 2:
                        px, py = int(pixel[0]), int(pixel[1])
                        if 0 <= py < height and 0 <= px < width:
                            colors.append(img_rgb[py, px])
            # Otherwise sample within the circle
            else:
                y_min = max(0, cy - radius)
                y_max = min(height, cy + radius + 1)
                x_min = max(0, cx - radius)
                x_max = min(width, cx + radius + 1)

                for y in range(y_min, y_max):
                    for x in range(x_min, x_max):
                        if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                            colors.append(img_rgb[y, x])

            if not colors:
                return None

            # Calculate average RGB
            avg_rgb = np.mean(colors, axis=0).astype(int)
            r, g, b = int(avg_rgb[0]), int(avg_rgb[1]), int(avg_rgb[2])

            # Convert to HSV
            h, _, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

            # Create full saturation and full value version for vibrant marker
            full_sat_rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            marker_rgb = tuple(int(c * 255) for c in full_sat_rgb)

            # Format color info
            hex_color = '#{:02x}{:02x}{:02x}'.format(*marker_rgb)
            hue_degrees = int(h * 360)

            return {
                'rgb': marker_rgb,
                'hex': hex_color,
                'hue_degrees': hue_degrees,
                'avg_rgb': (r, g, b)
            }

        except Exception as e:
            self.logger.error(f"Failed to calculate AOI color: {e}")
            return None

    def _construct_output_path(self, full_path, input_dir, output_dir):
        """
        Construct an output path by replacing the input directory with the output directory.

        Args:
            full_path (str): Full path to the input file
            input_dir (str): Input directory path
            output_dir (str): Output directory path

        Returns:
            str: Properly constructed output path
        """
        # Convert all paths to Path objects for proper handling
        full_path_obj = Path(full_path)
        input_dir_obj = Path(input_dir)
        output_dir_obj = Path(output_dir)

        # Get the relative path from input_dir to the file
        try:
            relative_path = full_path_obj.relative_to(input_dir_obj)
        except ValueError:
            # If the file is not under input_dir, just use the filename
            relative_path = full_path_obj.name

        # Construct the output path
        output_path = output_dir_obj / relative_path

        return str(output_path)

    def store_mask(self, input_file, output_file, mask, temperature_data=None, target_shape=None):
        """
        Saves the detection mask as a TIFF file with temperature data embedded as additional bands.

        Args:
            input_file (str): Path to the input image file.
            output_file (str): Path to save the mask (will be saved as .tif extension).
            mask (np.ndarray): Binary mask of detected pixels (0 or 255).
            temperature_data (np.ndarray or list, optional): Temperature matrix to store as additional bands.
            target_shape (tuple, optional): Target (height, width) to resize mask and thermal data to.
                Used when visual image is upscaled (e.g., DJI 1280x1024) vs thermal (640x512).
        """
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Change extension to .tif for mask
        mask_file = path.with_suffix('.tif')

        # Ensure mask is single channel grayscale
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        # If target_shape provided, upscale mask and thermal data to match visual image resolution
        # This handles DJI upscaled images where visual (1280x1024) != thermal (640x512)
        if target_shape is not None and target_shape[:2] != mask.shape[:2]:
            # self.logger.info(f"Info: Upscaling mask from {mask.shape[:2]} to visual image resolution {target_shape[:2]}")
            # self.logger.info("      (DJI upscaled image: ensuring viewer can query all pixels)")
            mask = cv2.resize(
                mask,
                (target_shape[1], target_shape[0]),
                interpolation=cv2.INTER_NEAREST  # Use NEAREST for binary mask
            )

        bands = []

        # First band: mask (uint8)
        bands.append(mask.astype(np.uint8))

        if temperature_data is not None:
            # Convert to numpy if needed
            if not isinstance(temperature_data, np.ndarray):
                temperature_data = np.array(temperature_data)

            # Upscale temperature data to match mask resolution (which matches visual image)
            if temperature_data.shape[:2] != mask.shape[:2]:
                # self.logger.info(f"Info: Upscaling thermal data from {temperature_data.shape[:2]} to {mask.shape[:2]}")
                # self.logger.info("      Using bilinear interpolation to preserve temperature values")
                temperature_data = cv2.resize(
                    temperature_data.astype(np.float32),
                    (mask.shape[1], mask.shape[0]),
                    interpolation=cv2.INTER_LINEAR  # Bilinear for smooth temperature interpolation
                )

            # Always float32 for thermal
            temp_scaled = temperature_data.astype(np.float32)

            # If 2D, add channel dimension
            if temp_scaled.ndim == 2:
                temp_scaled = np.expand_dims(temp_scaled, axis=2)

            # Add each channel as its own band
            for i in range(temp_scaled.shape[2]):
                bands.append(temp_scaled[:, :, i])

        # Stack into shape (bands, height, width)
        stacked = np.stack(bands, axis=0)

        # Save with tifffile (multi-band, compressed)
        tifffile.imwrite(
            str(mask_file),
            stacked,
            photometric='minisblack',
            metadata={'axes': 'CYX'},  # Channels, Y, X
            compression='deflate'  # or 'zlib' / 'lzma' if you prefer
        )

        return str(mask_file)

    def split_image(self, img, segments, overlap=0):
        """
        Splits an image into a grid of segments with optional overlap.

        Args:
            img (numpy.ndarray): The image to be divided.
            segments (int): Number of segments in the grid.
            overlap (int or float): Overlap between segments in pixels or as a percentage (0-1).

        Returns:
            list: A 2D list of numpy.ndarrays representing the segments.
        """
        rows, cols = self._get_rows_cols_from_segments(segments)
        if len(img.shape) == 2:  # Grayscale image
            h, w = img.shape
        elif len(img.shape) == 3:  # Color image
            h, w, _ = img.shape
        row_height = math.ceil(h / rows)
        col_width = math.ceil(w / cols)

        # Calculate overlap in pixels
        overlap_h = int(row_height * overlap) if overlap < 1 else int(overlap)
        overlap_w = int(col_width * overlap) if overlap < 1 else int(overlap)

        pieces = []
        for i in range(rows):
            row_pieces = []
            for j in range(cols):
                # Calculate slice boundaries with overlap
                y_start = max(i * row_height - overlap_h, 0)
                y_end = min((i + 1) * row_height + overlap_h, h)
                x_start = max(j * col_width - overlap_w, 0)
                x_end = min((j + 1) * col_width + overlap_w, w)

                # Extract segment
                row_pieces.append(img[y_start:y_end, x_start:x_end])
            pieces.append(row_pieces)

        return pieces

    def glue_image(self, pieces):
        """
        Combines the segments of an image into a single image.

        Args:
            pieces (list): A list of lists containing numpy.ndarrays representing the segments of the image.

        Returns:
            numpy.ndarray: The combined image.
        """
        rows = [cv2.hconcat(row) for row in pieces]
        return cv2.vconcat(rows)

    def _get_rows_cols_from_segments(self, segments):
        """
        Get the number of rows and columns for a number of segments

        Args:
            segments (int): The number of segments in which to divide the image.

        Returns:
            int, int: The number of rows and columns.
        """
        if segments == 2:
            return 1, 2
        elif segments == 6:
            return 2, 3
        else:
            return int(segments ** .5), int(segments ** .5)


class AnalysisResult:
    """Class representing the result of an image processing operation."""

    def __init__(self, input_path=None, output_path=None, output_dir=None,
                 areas_of_interest=None, base_contour_count=None, error_message=None):
        """
        Initializes an AnalysisResult with the given parameters.

        Args:
            input_path (str, optional): Path to the input image. Defaults to None.
            output_path (str, optional): Path to the output image. Defaults to None.
            output_dir (str, optional): Path to the output directory. Defaults to None.
            areas_of_interest (list, optional): List of detected areas of interest. Defaults to None.
            base_contour_count (int, optional): Count of base contours. Defaults to None.
            error_message (str, optional): Error message if processing failed. Defaults to None.
        """
        self.input_path = input_path

        if output_path is not None:
            if os.path.isabs(output_path):
                self.output_path = output_path.replace(output_dir, '')
                self.output_path = self.output_path[1:]
            else:
                self.output_path = output_path
        else:
            self.output_path = output_path

        self.areas_of_interest = areas_of_interest
        self.base_contour_count = base_contour_count
        self.error_message = error_message
