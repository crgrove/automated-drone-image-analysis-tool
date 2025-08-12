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
    """Service that executes the MRMap algorithm for detecting anomalies in spectral images."""

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        """
        Initializes the MRMapService with specific parameters for anomaly detection.

        Args:
            identifier (tuple[int, int, int]): RGB values for the color to highlight areas of interest.
            min_area (int): Minimum area in pixels for an object to qualify as an area of interest.
            max_area (int): Maximum area in pixels for an object to qualify as an area of interest.
            aoi_radius (int): Radius added to the minimum enclosing circle around an area of interest.
            combine_aois (bool): If True, overlapping areas of interest will be combined.
            options (dict): Additional algorithm-specific options, including 'threshold', 'segments', and 'window'.
        """
        self.logger = LoggerService()
        super().__init__('MRMap', identifier, min_area, max_area, aoi_radius, combine_aois, options)
        self.segments = options['segments']
        self.threshold = options['threshold']
        self.window_size = options['window']

    def process_image(self, img, full_path, input_dir, output_dir):
        """
        Processes a single image using the MR Map algorithm.

        Args:
            img (numpy.ndarray): The image to be processed.
            full_path (str): The path to the image being analyzed.
            input_dir (str): The base input folder.
            output_dir (str): The base output folder.

        Returns:
            AnalysisResult: Contains the processed image path, list of areas of interest, base contour count, and error message if any.
        """
        try:
            height, width = img.shape[:2]
            hist = Histogram(img)

            r, g, b = img[:, :, 2], img[:, :, 1], img[:, :, 0]
            # Compute bin counts for each pixel
            bin_counts = hist.bin_count(r, g, b)
            bin_counts = bin_counts * ((8000*6000) / (width * height))
            # Adjust counts based on image size
            # adjusted_counts = bin_counts * (STANDARD_IMAGE_SIZE / (width * height))

            # Identify anomalous pixels
            pixel_anom = (0 < bin_counts) & (bin_counts < self.threshold)

            contours = self._getMRMapsContours(pixel_anom)

            areas_of_interest, base_contour_count = self.identify_areas_of_interest(img, contours)
            output_path = full_path.replace(input_dir, output_dir)
            if areas_of_interest:
                self.store_image(full_path, output_path, areas_of_interest)

            return AnalysisResult(full_path, output_path, output_dir, areas_of_interest, base_contour_count)


        except Exception as e:
            # print(traceback.format_exc())
            return AnalysisResult(full_path, error_message=str(e))

    def _getADIATContours(self, pixel_anom):
        mask = pixel_anom.astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def _getMRMapsContours(self, pixel_anom):
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
            mask[rect[1]:rect[3]+1, rect[0]:rect[2]+1] = 255

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        return contours

    def _find_connected_pixels(self, pixel_anom, visited, start_x, start_y, width, height):
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

            neighbors = np.argwhere(pixel_anom[y_range[0]:y_range[1], x_range[0]:x_range[1]] & ~visited[y_range[0]:y_range[1], x_range[0]:x_range[1]])

            for dy, dx in neighbors:
                queue.append((x_range[0] + dx, y_range[0] + dy))

        return count, rect

    def _merge_rectangles(self, rect1, rect2):
        """Merge two overlapping rectangles into one."""
        return [
            min(rect1[0], rect2[0]),  # left
            min(rect1[1], rect2[1]),  # top
            max(rect1[2], rect2[2]),  # right
            max(rect1[3], rect2[3])   # bottom
        ]

    def _rectangles_overlap(self, rect1, rect2):
        """Check if two rectangles overlap."""
        return not (
            rect1[2] < rect2[0] or  # rect1 right < rect2 left
            rect1[0] > rect2[2] or  # rect1 left > rect2 right
            rect1[3] < rect2[1] or  # rect1 bottom < rect2 top
            rect1[1] > rect2[3]     # rect1 top > rect2 bottom
        )


class Histogram:
    def __init__(self, image):
        self.image_array = image

        # Use a smaller integer type for bin mapping
        bin_size = math.ceil(MAX_SHADES / NUMBER_OF_QUANTIZED_HISTOGRAM_BINS)
        self.mapping = (np.arange(MAX_SHADES) / bin_size).astype(np.uint8)  # Reduce dtype size

        self.q_histogram = None
        self.create_histogram()

    def create_histogram(self):
        # Directly map pixel values to quantized bins
        r_mapped = self.mapping[self.image_array[:, :, 2]]
        g_mapped = self.mapping[self.image_array[:, :, 1]]
        b_mapped = self.mapping[self.image_array[:, :, 0]]

        # Compute histogram directly without storing a large intermediate array
        self.q_histogram, _ = np.histogramdd(
            (r_mapped.ravel(), g_mapped.ravel(), b_mapped.ravel()),  # Direct ravel to avoid memory overhead
            bins=(NUMBER_OF_QUANTIZED_HISTOGRAM_BINS,) * 3,
            range=((0, NUMBER_OF_QUANTIZED_HISTOGRAM_BINS),) * 3
        )

    def bin_count(self, r, g, b):
        qr = self.mapping[r]
        qg = self.mapping[g]
        qb = self.mapping[b]

        return self.q_histogram[qr, qg, qb]
