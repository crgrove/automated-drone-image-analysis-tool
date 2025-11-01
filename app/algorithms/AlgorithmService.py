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
        Sets the scale factor for coordinate transformation from processing to original resolution.

        Args:
            scale_factor (float): The scale factor used when downscaling the image for processing.
        """
        self.scale_factor = scale_factor

    def transform_to_original_coords(self, x, y):
        """
        Transforms coordinates from processing resolution back to original resolution.

        Args:
            x (float): X coordinate in processing resolution.
            y (float): Y coordinate in processing resolution.

        Returns:
            tuple[int, int]: (x, y) coordinates in original resolution.
        """
        if self.scale_factor == 1.0:
            return int(x), int(y)
        inverse_scale = 1.0 / self.scale_factor
        return int(x * inverse_scale), int(y * inverse_scale)

    def transform_contour_to_original(self, contour):
        """
        Transforms a contour from processing resolution back to original resolution.

        Args:
            contour (numpy.ndarray): Contour in processing resolution.

        Returns:
            numpy.ndarray: Contour scaled to original resolution.
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
                - areas_of_interest (list): Final list of AOI dictionaries with structure:
                    {
                        'center': (x, y),              # Tuple of pixel coordinates
                        'radius': int,                  # Radius in pixels
                        'area': float,                  # Pixel area
                        'contour': [[x, y], ...],      # List of contour points
                        'detected_pixels': [[x, y], ...], # List of detected pixel coordinates
                        'confidence': float (optional), # 0-100 normalized confidence score
                        'score_type': str (optional),   # 'anomaly', 'match', 'rarity', 'color_distance'
                        'raw_score': float (optional),  # Algorithm-specific raw value
                        'score_method': str (optional)  # 'mean', 'max', 'median'
                    }
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
            area = cv2.countNonZero(mask)

            if area >= self.min_area and (self.max_area == 0 or area <= self.max_area):
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius) + self.aoi_radius
                base_contour_count += 1

                # Add to mask for later combining
                cv2.circle(temp_mask, center, radius, 255, -1)

                # Also keep track of original pixels
                original_pixels_mask = cv2.bitwise_or(original_pixels_mask, mask)

                if not self.combine_aois:
                    # Transform coordinates to original resolution
                    orig_center = self.transform_to_original_coords(center[0], center[1])
                    orig_radius = int(radius / self.scale_factor)
                    orig_area = int(area / (self.scale_factor * self.scale_factor))

                    # Store the contour points for drawing the boundary (transformed)
                    if self.scale_factor != 1.0:
                        cnt_transformed = self.transform_contour_to_original(cnt)
                        contour_points = cnt_transformed.reshape(-1, 2).tolist()
                    else:
                        contour_points = cnt.reshape(-1, 2).tolist()

                    # Get the detected pixels for this AOI (transformed)
                    detected_pixels = np.argwhere(mask > 0)
                    if len(detected_pixels) > 0:
                        if self.scale_factor != 1.0:
                            inverse_scale = 1.0 / self.scale_factor
                            detected_pixels_transformed = (detected_pixels[:, [1, 0]] * inverse_scale).astype(int)
                            detected_pixels_list = detected_pixels_transformed.tolist()
                        else:
                            detected_pixels_list = detected_pixels[:, [1, 0]].tolist()
                    else:
                        detected_pixels_list = []

                    areas_of_interest.append({
                        'center': orig_center,
                        'radius': orig_radius,
                        'area': orig_area,
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
                area = cv2.countNonZero(mask)
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)

                # Transform coordinates to original resolution
                orig_center = self.transform_to_original_coords(center[0], center[1])
                orig_radius = int(radius / self.scale_factor)
                orig_area = int(area / (self.scale_factor * self.scale_factor))

                # Store the contour points for drawing the boundary (transformed)
                if self.scale_factor != 1.0:
                    cnt_transformed = self.transform_contour_to_original(cnt)
                    contour_points = cnt_transformed.reshape(-1, 2).tolist()
                else:
                    contour_points = cnt.reshape(-1, 2).tolist()

                # Get the original detected pixels that belong to this combined AOI (transformed)
                aoi_pixels_mask = cv2.bitwise_and(original_pixels_mask, mask)
                aoi_pixels = np.argwhere(aoi_pixels_mask > 0)
                if len(aoi_pixels) > 0:
                    if self.scale_factor != 1.0:
                        inverse_scale = 1.0 / self.scale_factor
                        aoi_pixels_transformed = (aoi_pixels[:, [1, 0]] * inverse_scale).astype(int)
                        aoi_pixels_list = aoi_pixels_transformed.tolist()
                    else:
                        aoi_pixels_list = aoi_pixels[:, [1, 0]].tolist()
                else:
                    aoi_pixels_list = []

                areas_of_interest.append({
                    'center': orig_center,
                    'radius': orig_radius,
                    'area': orig_area,
                    'contour': contour_points,
                    'detected_pixels': aoi_pixels_list
                })

        # Sort for consistent ordering
        areas_of_interest.sort(key=lambda item: (item['center'][1], item['center'][0]))

        return areas_of_interest, base_contour_count

    def generate_aoi_cache(self, img: np.ndarray, image_path: str, areas_of_interest: list, output_dir: str) -> None:
        """
        Generate and cache thumbnails and color information for all AOIs.

        Called after process_image() while the image is still in memory, allowing for efficient
        thumbnail extraction without reloading the image from disk.

        Args:
            img: The image array (already in memory from detection)
            image_path: Path to the source image file
            areas_of_interest: List of AOI dictionaries from detection
            output_dir: Output directory where cache folders will be created
        """
        try:
            from core.services.ThumbnailCacheService import ThumbnailCacheService
            from core.services.ColorCacheService import ColorCacheService
            from core.services.TemperatureCacheService import TemperatureCacheService
            from core.services.AOIService import AOIService

            if not areas_of_interest:
                return

            # Set up cache directories
            thumbnail_cache_dir = Path(output_dir) / '.thumbnails'
            color_cache_dir = Path(output_dir) / '.color_cache'
            temperature_cache_dir = Path(output_dir) / '.temperature_cache'
            thumbnail_cache_dir.mkdir(parents=True, exist_ok=True)
            color_cache_dir.mkdir(parents=True, exist_ok=True)
            temperature_cache_dir.mkdir(parents=True, exist_ok=True)

            # Initialize cache services
            thumbnail_service = ThumbnailCacheService(dataset_cache_dir=str(thumbnail_cache_dir))
            color_service = ColorCacheService(cache_dir=str(color_cache_dir))
            temperature_service = TemperatureCacheService(cache_dir=str(temperature_cache_dir))

            # Load existing cache files to avoid overwriting data from other processes
            color_service.load_cache_file()
            temperature_service.load_cache_file()

            # Create AOIService for color calculation
            image_data = {
                'path': image_path,
                'is_thermal': self.is_thermal
            }
            aoi_service = AOIService(image_data)

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
                    height, width = img.shape[:2]
                    x1 = max(0, int(cx - crop_radius))
                    y1 = max(0, int(cy - crop_radius))
                    x2 = min(width, int(cx + crop_radius))
                    y2 = min(height, int(cy + crop_radius))

                    # Extract region from in-memory image
                    thumbnail_region = img[y1:y2, x1:x2]

                    if thumbnail_region.size == 0:
                        continue

                    # Resize to target thumbnail size
                    thumbnail_resized = cv2.resize(thumbnail_region, (180, 180), interpolation=cv2.INTER_LANCZOS4)

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

                    # Calculate and cache color information
                    color_result = aoi_service.get_aoi_representative_color(aoi)
                    if color_result:
                        color_info = {
                            'rgb': color_result['rgb'],
                            'hex': color_result['hex'],
                            'hue_degrees': color_result['hue_degrees']
                        }
                        color_service.save_color_info(image_path, aoi, color_info)

                    # Cache temperature information if present (for thermal datasets)
                    if 'temperature' in aoi and aoi['temperature'] is not None:
                        temperature_service.save_temperature(image_path, aoi, aoi['temperature'])

                except Exception as e:
                    # Log error but continue processing other AOIs
                    print(f"Error caching AOI at {center}: {e}")
                    continue

            # Save color cache to disk
            color_service.save_cache_file()

            # Save temperature cache to disk (for thermal datasets)
            temperature_service.save_cache_file()

        except Exception as e:
            # Don't fail the entire detection if cache generation fails
            print(f"Error generating AOI cache: {e}")

    def _construct_output_path(self, full_path, input_dir, output_dir):
        """
        Properly constructs an output path by replacing the input directory with the output directory.

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

    def store_mask(self, input_file, output_file, mask, temperature_data=None):
        """
        Saves the detection mask as a TIFF file with temperature data embedded as additional bands.

        Args:
            input_file (str): Path to the input image file.
            output_file (str): Path to save the mask (will be saved as .tif extension).
            mask (np.ndarray): Binary mask of detected pixels (0 or 255).
            temperature_data (np.ndarray or list, optional): Temperature matrix to store as additional bands.
        """
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Change extension to .tif for mask
        mask_file = path.with_suffix('.tif')

        # Ensure mask is single channel grayscale
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        bands = []

        # First band: mask (uint8)
        bands.append(mask.astype(np.uint8))

        if temperature_data is not None:
            # Convert to numpy if needed
            if not isinstance(temperature_data, np.ndarray):
                temperature_data = np.array(temperature_data)

            # Resize if mismatch
            if temperature_data.shape[:2] != mask.shape[:2]:
                print(f"Warning: Temperature data shape {temperature_data.shape} doesn't match mask shape {mask.shape}")
                temperature_data = cv2.resize(
                    temperature_data.astype(np.float32),
                    (mask.shape[1], mask.shape[0]),
                    interpolation=cv2.INTER_LINEAR
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
