import numpy as np
import cv2
import os
import math
import shutil
import json
from pathlib import Path
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

    def identify_areas_of_interest(self, img, contours):
        areas_of_interest = []

        for cnt in contours:
            # Get bounding box to limit rasterization
            x, y, w, h = cv2.boundingRect(cnt)
            roi_mask = np.zeros((h, w), dtype=np.uint8)

            # Shift contour to ROI coords
            cnt_roi = cnt - np.array([[[x, y]]], dtype=cnt.dtype)

            # Fill contour in ROI
            cv2.drawContours(roi_mask, [cnt_roi], -1, 255, thickness=-1)
            # Get all pixel coordinates in ROI
            pts = cv2.findNonZero(roi_mask)
            if pts is None:
                continue

            # Convert to image coordinates
            pts = pts.reshape(-1, 2)
            pts[:, 0] += x
            pts[:, 1] += y

            area = pts.shape[0]  # pixel-accurate area
            if area >= self.min_area and (self.max_area == 0 or area <= self.max_area):
                areas_of_interest.append(pts)  # keep as NumPy array for speed

        return areas_of_interest

    def store_image(self, input_file, output_file, areas_of_interest, temperature_data=None):
        """
        Duplicates the input image to the output location and stores AOIs and temperature data in XMP.

        Args:
            input_file (str): Path to the input image file.
            output_file (str): Path to save the output image.
            areas_of_interest (list or np.ndarray): List/array of AOI pixel coordinates.
            temperature_data (np.ndarray or list, optional): Temperature matrix to store.
        """
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Step 1: Duplicate file with all metadata intact
        shutil.copy2(input_file, output_file)

        # Step 2: Store AOIs in a custom namespace
        aoi_json = json.dumps(
            areas_of_interest,
            default=lambda x: x.tolist() if hasattr(x, 'tolist') else x
        )
        
        MetaDataHelper.add_xmp_field(
            output_file,
            namespace_uri="http://example.com/aoi/1.0/",
            tag_name="AreasOfInterest",
            value_str=json.dumps(areas_of_interest, default=lambda x: x.tolist() if hasattr(x, "tolist") else x)
        )

        # Step 3: Store temperature data in a separate custom namespace (if provided)
        if temperature_data is not None:
            temp_json = json.dumps(
                temperature_data,
                default=lambda x: x.tolist() if hasattr(x, 'tolist') else x
            )
            MetaDataHelper.add_xmp_field(
                output_file,
                namespace_uri="http://example.com/thermal/1.0/",
                tag_name="TemperatureData",
                value_str= json.dumps(temperature_data.tolist())
            )

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

    def __init__(self, input_path=None, output_path=None, output_dir=None, areas_of_interest=[], error_message=None):
        """
        Initializes an AnalysisResult with the given parameters.

        Args:
            input_path (str, optional): Path to the input image. Defaults to None.
            output_path (str, optional): Path to the output image. Defaults to None.
            output_dir (str, optional): Path to the output directory. Defaults to None.
            areas_of_interest (list, optional): List of detected areas of interest. Defaults to [].
            error_message (str, optional): Error message if processing failed. Defaults to None.
        """
        self.input_path = input_path
        # Turn the output path into a relative path.
        if output_path is not None:
            if os.path.isabs(output_path):
                self.output_path = output_path.replace(output_dir, '')
                self.output_path = self.output_path[1:]
            else:
                self.output_path = output_path
        else:
            self.output_path = output_path
        self.areas_of_interest = areas_of_interest
        self.error_message = error_message
