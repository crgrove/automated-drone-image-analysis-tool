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
from core.services.image.AOIService import AOIService


class AlgorithmService:
    """Base class for algorithm services that provides methods for processing images.

    Provides common functionality for image processing algorithms including
    coordinate transformation, area of interest identification, and caching.

    Attributes:
        name: Name of the algorithm.
        identifier_color: RGB tuple for highlighting areas of interest.
        min_area: Minimum area in pixels for an object to qualify as an AOI.
        max_area: Maximum area in pixels for an object to qualify as an AOI.
        aoi_radius: Radius added to the minimum enclosing circle around an AOI.
        combine_aois: If True, overlapping areas of interest will be combined.
        options: Dictionary of algorithm-specific options.
        is_thermal: Whether this is a thermal image algorithm.
        scale_factor: Scale factor for coordinate transformation.
    """

    def __init__(self, name, identifier_color, min_area, max_area, aoi_radius, combine_aois, options, is_thermal=False):
        """Initialize the AlgorithmService with the necessary parameters.

        Args:
            name: The name of the algorithm to be used for analysis.
            identifier_color: RGB values for the color to highlight areas of interest.
            min_area: Minimum area in pixels for an object to qualify as an area of interest.
            max_area: Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius: Radius added to the minimum enclosing circle around an area of interest.
            combine_aois: If True, overlapping areas of interest will be combined.
            options: Additional algorithm-specific options.
            is_thermal: Indicates if this is a thermal image algorithm. Defaults to False.
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
        """Set the scale factor for coordinate transformation from processing to original resolution.

        Args:
            scale_factor: The scale factor used when downscaling the image for processing.
        """
        self.scale_factor = scale_factor

    def transform_to_original_coords(self, x, y):
        """Transform coordinates from processing resolution back to original resolution.

        Args:
            x: X coordinate in processing resolution.
            y: Y coordinate in processing resolution.

        Returns:
            Tuple of (x, y) coordinates in original resolution as integers.
        """
        if self.scale_factor == 1.0:
            return int(x), int(y)
        inverse_scale = 1.0 / self.scale_factor
        return int(x * inverse_scale), int(y * inverse_scale)

    def transform_contour_to_original(self, contour):
        """Transform a contour from processing resolution back to original resolution.

        Args:
            contour: Contour in processing resolution as numpy array.

        Returns:
            Contour scaled to original resolution as numpy array of int32.
        """
        if self.scale_factor == 1.0:
            return contour
        inverse_scale = 1.0 / self.scale_factor
        return (contour * inverse_scale).astype(np.int32)

    def process_image(self, img, full_path, input_dir, output_dir):
        """Process a single image file using the algorithm.

        Must be implemented by subclasses to perform algorithm-specific processing.

        Args:
            img: The image to be processed as numpy array.
            full_path: The path to the image being analyzed.
            input_dir: The base input directory.
            output_dir: The base output directory.

        Returns:
            AnalysisResult containing processed image path, areas of interest,
            and error message if any.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def collect_pixels_of_interest(self, mask):
        """Collect pixel coordinates from a binary mask.

        Args:
            mask: Binary mask where non-zero pixels are of interest.

        Returns:
            Array of (x, y) coordinates of pixels where mask > 0.
        """
        coords = np.argwhere(mask > 0)
        return coords[:, [1, 0]]

    def identify_areas_of_interest(self, img_or_shape, contours):
        """Calculate areas of interest from contours without modifying the input image.

        Args:
            img_or_shape: The image array or its shape (H, W, [C]).
            contours: List of contours from cv2.findContours.

        Returns:
            Tuple of (areas_of_interest, base_contour_count) where:
                - areas_of_interest: List of AOI dictionaries with structure:
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
                - base_contour_count: Count of original valid contours before combining.
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

                    # Calculate and cache color information
                    color_result = aoi_service.get_aoi_representative_color(aoi)
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
                    print(f"Error caching AOI at {center}: {e}")
                    continue

            # Note: Color and temperature cache data is now stored in AOI dicts and will be written to XML
            # No need to save JSON files - data goes directly to XML via AnalyzeService

        except Exception as e:
            # Don't fail the entire detection if cache generation fails
            print(f"Error generating AOI cache: {e}")

    def _construct_output_path(self, full_path, input_dir, output_dir):
        """Construct an output path by replacing the input directory with the output directory.

        Args:
            full_path: Full path to the input file.
            input_dir: Input directory path.
            output_dir: Output directory path.

        Returns:
            Properly constructed output path as string.
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
        """Save the detection mask as a TIFF file with temperature data embedded as additional bands.

        Args:
            input_file: Path to the input image file.
            output_file: Path to save the mask (will be saved as .tif extension).
            mask: Binary mask of detected pixels (0 or 255) as numpy array.
            temperature_data: Temperature matrix to store as additional bands.
                Optional, can be numpy array or list.

        Returns:
            Path to the saved mask file as string.
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
        # Try 'lzw' first (faster), fall back to 'deflate' if imagecodecs is not available
        try:
            tifffile.imwrite(
                str(mask_file),
                stacked,
                photometric='minisblack',
                metadata={'axes': 'CYX'},  # Channels, Y, X
                compression='lzw'  # Faster than 'deflate' while maintaining good compression
            )
        except (ValueError, RuntimeError) as e:
            # Fall back to 'deflate' if 'lzw' requires imagecodecs package
            if 'imagecodecs' in str(e) or 'lzw' in str(e).lower():
                tifffile.imwrite(
                    str(mask_file),
                    stacked,
                    photometric='minisblack',
                    metadata={'axes': 'CYX'},  # Channels, Y, X
                    compression='deflate'  # Fallback compression that works without imagecodecs
                )
            else:
                raise

        return str(mask_file)

    def split_image(self, img, segments, overlap=0):
        """Split an image into a grid of segments with optional overlap.

        Args:
            img: The image to be divided as numpy array.
            segments: Number of segments in the grid.
            overlap: Overlap between segments in pixels or as a percentage (0-1).
                Defaults to 0.

        Returns:
            A 2D list of numpy arrays representing the segments.
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
        """Combine the segments of an image into a single image.

        Args:
            pieces: A list of lists containing numpy arrays representing the segments.

        Returns:
            The combined image as a numpy array.
        """
        rows = [cv2.hconcat(row) for row in pieces]
        return cv2.vconcat(rows)

    def _get_rows_cols_from_segments(self, segments):
        """Get the number of rows and columns for a number of segments.

        Args:
            segments: The number of segments in which to divide the image.

        Returns:
            Tuple of (rows, columns) as integers.
        """
        if segments == 2:
            return 1, 2
        elif segments == 6:
            return 2, 3
        else:
            return int(segments ** .5), int(segments ** .5)


class AnalysisResult:
    """Class representing the result of an image processing operation.

    Attributes:
        input_path: Path to the input image.
        output_path: Path to the output image (relative to output_dir).
        areas_of_interest: List of detected areas of interest.
        base_contour_count: Count of base contours before combining.
        error_message: Error message if processing failed.
    """

    def __init__(self, input_path=None, output_path=None, output_dir=None,
                 areas_of_interest=None, base_contour_count=None, error_message=None):
        """Initialize an AnalysisResult with the given parameters.

        Args:
            input_path: Path to the input image. Defaults to None.
            output_path: Path to the output image. Defaults to None.
            output_dir: Path to the output directory. Defaults to None.
            areas_of_interest: List of detected areas of interest. Defaults to None.
            base_contour_count: Count of base contours. Defaults to None.
            error_message: Error message if processing failed. Defaults to None.
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
