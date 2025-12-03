import logging
import numpy as np
import cv2
import math
import traceback

from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from core.services.LoggerService import LoggerService
from collections import deque

MAX_SHADES = 256
NUMBER_OF_QUANTIZED_HISTOGRAM_BINS = 26


class MRMapService(AlgorithmService):
    """Service that executes the MRMap algorithm for detecting anomalies in spectral images.

    Uses Multi-Resolution Map (MRMap) algorithm to detect rare color combinations
    based on histogram analysis and bin count thresholds.

    Attributes:
        segments: Number of image segments for processing.
        threshold: Bin count threshold for anomaly detection.
        window_size: Window size for processing.
    """

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """Initialize the MRMapService with specific parameters for anomaly detection.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options, including 'threshold', 'segments', 'window', and 'colorspace'.
        """
        self.logger = LoggerService()
        super().__init__('MRMap', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.segments = options['segments']
        self.threshold = options['threshold']
        self.window_size = options['window']
        self.colorspace = options.get('colorspace', 'RGB')

    def process_image(self, img, full_path, input_dir, output_dir):
        """Process a single image using the MR Map algorithm.

        Analyzes image using histogram-based bin counting to identify rare
        color combinations. Adds confidence scores based on bin count rarity.

        Args:
            img: The image to be processed as numpy array.
            full_path: The path to the image being analyzed.
            input_dir: The base input folder.
            output_dir: The base output folder.

        Returns:
            AnalysisResult containing the processed image path, list of areas
            of interest, base contour count, and error message if any.
        """
        try:
            height, width = img.shape[:2]

            # Convert to selected colorspace
            if self.colorspace == 'HSV':
                img_converted = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            elif self.colorspace == 'LAB':
                img_converted = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            else:  # RGB (default)
                img_converted = img

            hist = Histogram(img_converted)

            # Extract channels (order depends on colorspace)
            # For all colorspaces, channels are in order [0, 1, 2]
            ch0, ch1, ch2 = img_converted[:, :, 0], img_converted[:, :, 1], img_converted[:, :, 2]
            # Compute bin counts for each pixel
            bin_counts = hist.bin_count(ch0, ch1, ch2)
            bin_counts = bin_counts * ((8000 * 6000) / (width * height))
            # Adjust counts based on image size
            # adjusted_counts = bin_counts * (STANDARD_IMAGE_SIZE / (width * height))

            # Identify anomalous pixels
            pixel_anom = (0 < bin_counts) & (bin_counts < self.threshold)

            mask, contours = self._getMRMapsContours(pixel_anom)

            # Identify contours in the masked image
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)

            # Add confidence scores to AOIs based on bin counts (rarity scores)
            if areas_of_interest:
                areas_of_interest = self._add_confidence_scores(areas_of_interest, bin_counts, mask)

            output_path = self._construct_output_path(full_path, input_dir, output_dir)

            # Store mask instead of duplicating image
            mask_path = None
            if areas_of_interest:
                mask_path = self.store_mask(full_path, output_path, mask)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            # print(traceback.format_exc())
            return AnalysisResult(full_path, error_message=str(e))

    def _getADIATContours(self, pixel_anom):
        """Get contours from pixel anomaly mask using standard method.

        Args:
            pixel_anom: Boolean array indicating anomalous pixels.

        Returns:
            List of contours from cv2.findContours.
        """
        mask = pixel_anom.astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def _getMRMapsContours(self, pixel_anom):
        """Get contours from pixel anomaly mask using MRMap-specific method.

        Uses connected component analysis with window-based connectivity
        to merge nearby anomalies into rectangles.

        Args:
            pixel_anom: Boolean array indicating anomalous pixels.

        Returns:
            Tuple of (mask, contours) where mask is the combined mask and
            contours is the list of contours.
        """
        visited = np.zeros_like(pixel_anom, dtype=bool)
        anomaly_rectangles = []
        mask = np.zeros_like(pixel_anom, dtype=np.uint8)
        height, width = pixel_anom.shape

        for y, x in zip(*np.where(pixel_anom & ~visited)):
            count, rect = self._find_connected_pixels(pixel_anom, visited, x, y, width, height)
            if count >= self.min_area:
                merged = False
                for i, existing_rect in enumerate(anomaly_rectangles):
                    if self._rectangles_overlap(existing_rect, rect):
                        anomaly_rectangles[i] = self._merge_rectangles(existing_rect, rect)
                        merged = True
                        break

                if not merged:
                    anomaly_rectangles.append(rect)

        # Draw all combined rectangles
        for rect in anomaly_rectangles:
            mask[rect[1]:rect[3] + 1, rect[0]:rect[2] + 1] = 255

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        return mask, contours

    def _find_connected_pixels(self, pixel_anom, visited, start_x, start_y, width, height):
        """Find connected pixels using BFS with window-based connectivity.

        Args:
            pixel_anom: Boolean array indicating anomalous pixels.
            visited: Boolean array tracking visited pixels.
            start_x: Starting X coordinate.
            start_y: Starting Y coordinate.
            width: Image width.
            height: Image height.

        Returns:
            Tuple of (count, rect) where count is the number of connected
            pixels and rect is [min_x, min_y, max_x, max_y].
        """
        queue = deque([(start_x, start_y)])
        rect = [start_x, start_y, start_x, start_y]
        count = 0

        while queue:
            x, y = queue.popleft()

            if visited[y, x] or not pixel_anom[y, x]:
                continue  # Skip if already visited or not an anomaly

            visited[y, x] = True
            count += 1
            rect[0] = min(rect[0], x)
            rect[1] = min(rect[1], y)
            rect[2] = max(rect[2], x)
            rect[3] = max(rect[3], y)

            # Vectorized neighbor selection
            x_range = np.clip([x - self.window_size, x + self.window_size + 1], 0, width)
            y_range = np.clip([y - self.window_size, y + self.window_size + 1], 0, height)

            neighbors = np.argwhere(
                pixel_anom[y_range[0]:y_range[1], x_range[0]:x_range[1]] &
                ~visited[y_range[0]:y_range[1], x_range[0]:x_range[1]]
            )

            for dy, dx in neighbors:
                queue.append((x_range[0] + dx, y_range[0] + dy))

        return count, rect

    def _merge_rectangles(self, rect1, rect2):
        """Merge two overlapping rectangles into one.

        Args:
            rect1: First rectangle as [min_x, min_y, max_x, max_y].
            rect2: Second rectangle as [min_x, min_y, max_x, max_y].

        Returns:
            Merged rectangle as [min_x, min_y, max_x, max_y].
        """
        return [
            min(rect1[0], rect2[0]),  # left
            min(rect1[1], rect2[1]),  # top
            max(rect1[2], rect2[2]),  # right
            max(rect1[3], rect2[3])   # bottom
        ]

    def _rectangles_overlap(self, rect1, rect2):
        """Check if two rectangles overlap.

        Args:
            rect1: First rectangle as [min_x, min_y, max_x, max_y].
            rect2: Second rectangle as [min_x, min_y, max_x, max_y].

        Returns:
            True if rectangles overlap, False otherwise.
        """
        return not (
            rect1[2] < rect2[0] or  # rect1 right < rect2 left
            rect1[0] > rect2[2] or  # rect1 left > rect2 right
            rect1[3] < rect2[1] or  # rect1 bottom < rect2 top
            rect1[1] > rect2[3]     # rect1 top > rect2 bottom
        )

    def _add_confidence_scores(self, areas_of_interest, bin_counts, mask):
        """Add confidence scores to AOIs based on histogram bin counts (rarity scores).

        Lower bin count = rarer color = higher confidence. Normalizes scores
        to 0-100 range based on detected pixel bin counts.

        Args:
            areas_of_interest: List of AOI dictionaries.
            bin_counts: Histogram bin counts for each pixel as numpy array.
            mask: Binary detection mask as numpy array.

        Returns:
            List of AOIs with added confidence scores.
        """
        # Get all bin counts from detected pixels to find max for normalization
        detected_bin_counts = bin_counts[mask > 0]
        if len(detected_bin_counts) == 0:
            return areas_of_interest

        max_bin_count = np.max(detected_bin_counts)
        min_bin_count = np.min(detected_bin_counts)
        bin_range = max_bin_count - min_bin_count if max_bin_count > min_bin_count else 1.0

        # Add confidence to each AOI
        for aoi in areas_of_interest:
            detected_pixels = aoi.get('detected_pixels', [])
            if len(detected_pixels) > 0:
                # Extract bin counts for this AOI's pixels
                # NOTE: detected_pixels are in ORIGINAL resolution, but bin_counts are in PROCESSING resolution
                # Need to transform coordinates back to processing resolution for lookup
                aoi_bin_counts = []
                for pixel in detected_pixels:
                    x_orig, y_orig = int(pixel[0]), int(pixel[1])

                    # Transform back to processing resolution
                    if self.scale_factor != 1.0:
                        x = int(x_orig * self.scale_factor)
                        y = int(y_orig * self.scale_factor)
                    else:
                        x, y = x_orig, y_orig

                    if 0 <= y < bin_counts.shape[0] and 0 <= x < bin_counts.shape[1]:
                        aoi_bin_counts.append(bin_counts[y, x])

                if len(aoi_bin_counts) > 0:
                    # Calculate mean bin count for this AOI
                    mean_bin_count = np.mean(aoi_bin_counts)

                    # Normalize to 0-100 scale (INVERTED: lower bin count = rarer = higher confidence)
                    normalized_score = ((max_bin_count - mean_bin_count) / bin_range) * 100.0

                    # Add confidence fields to AOI
                    aoi['confidence'] = round(normalized_score, 1)
                    aoi['score_type'] = 'rarity'
                    aoi['raw_score'] = round(float(mean_bin_count), 3)
                    aoi['score_method'] = 'mean'
                else:
                    # No valid pixels, set low confidence
                    aoi['confidence'] = 0.0
                    aoi['score_type'] = 'rarity'
                    aoi['raw_score'] = 0.0
                    aoi['score_method'] = 'mean'
            else:
                # No detected pixels, set low confidence
                aoi['confidence'] = 0.0
                aoi['score_type'] = 'rarity'
                aoi['raw_score'] = 0.0
                aoi['score_method'] = 'mean'

        return areas_of_interest


class Histogram:
    """Histogram class for quantized RGB color analysis.

    Creates a quantized 3D histogram of RGB color values for efficient
    bin counting and rarity analysis.

    Attributes:
        image_array: Original image array.
        mapping: Quantization mapping from 256 shades to bins.
        q_histogram: Quantized 3D histogram array.
    """

    def __init__(self, image):
        """Initialize histogram with image data.

        Args:
            image: Image array to analyze.
        """
        self.image_array = image

        # Use a smaller integer type for bin mapping
        bin_size = math.ceil(MAX_SHADES / NUMBER_OF_QUANTIZED_HISTOGRAM_BINS)
        self.mapping = (np.arange(MAX_SHADES) / bin_size).astype(np.uint8)  # Reduce dtype size

        self.q_histogram = None
        self.create_histogram()

    def create_histogram(self):
        """Create quantized 3D histogram from image.

        Maps RGB pixel values to quantized bins and computes histogram
        for efficient bin count lookups.
        """
        # Directly map pixel values to quantized bins
        # Works with any 3-channel colorspace (BGR, HSV, LAB, etc.)
        ch0_mapped = self.mapping[self.image_array[:, :, 0]]
        ch1_mapped = self.mapping[self.image_array[:, :, 1]]
        ch2_mapped = self.mapping[self.image_array[:, :, 2]]

        # Compute histogram directly without storing a large intermediate array
        self.q_histogram, _ = np.histogramdd(
            (ch0_mapped.ravel(), ch1_mapped.ravel(), ch2_mapped.ravel()),  # Direct ravel to avoid memory overhead
            bins=(NUMBER_OF_QUANTIZED_HISTOGRAM_BINS,) * 3,
            range=((0, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS),) * 3
        )

    def bin_count(self, ch0, ch1, ch2):
        """
        Get the histogram bin count for each pixel.

        Args:
            ch0, ch1, ch2: Channel values for each pixel (can be RGB, HSV, LAB, etc.)

        Returns:
            numpy.ndarray: Bin counts for each pixel
        """
        q0 = self.mapping[ch0]
        q1 = self.mapping[ch1]
        q2 = self.mapping[ch2]

        return self.q_histogram[q0, q1, q2]
