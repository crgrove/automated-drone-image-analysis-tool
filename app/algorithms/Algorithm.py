import platform
import numpy as np
import cv2
import os
import math
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

    def circle_areas_of_interest(self, img, contours):
        """
        Augments the input image with circles around areas of interest based on contours.

        Args:
            img (numpy.ndarray): The image in which areas of interest are to be highlighted.
            contours (numpy.ndarray): Array representing areas of interest in the image.

        Returns:
            tuple: A tuple containing:
                - numpy.ndarray: Image with circles around areas of interest.
                - list: List of detected areas of interest.
                - int: Count of original areas of interest before combining overlapping ones.
        """
        found = False

        if len(contours) > 0:
            areas_of_interest = []
            temp_mask = np.zeros(img.shape[:2], dtype=np.uint8)
            base_contour_count = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area >= self.min_area and (self.max_area == 0 or area <= self.max_area):
                    (x, y), radius = cv2.minEnclosingCircle(cnt)
                    center = (int(x), int(y))
                    radius = int(radius) + self.aoi_radius
                    found = True
                    cv2.circle(temp_mask, center, radius, (255), -1)
                    base_contour_count += 1
                    if not self.combine_aois:
                        item = {'center': center, 'radius': radius, 'area': area}
                        areas_of_interest.append(item)
                        image_copy = cv2.circle(
                            img, center, radius,
                            (self.identifier_color[2], self.identifier_color[1], self.identifier_color[0]), 2
                        )

        if found:
            if self.combine_aois:
                while True:
                    new_contours, hierarchy = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    for cnt in new_contours:
                        area = cv2.contourArea(cnt)
                        (x, y), radius = cv2.minEnclosingCircle(cnt)
                        center = (int(x), int(y))
                        radius = int(radius)
                        cv2.circle(temp_mask, center, radius, (255), -1)
                    if len(new_contours) == len(contours):
                        contours = new_contours
                        break
                    contours = new_contours
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    (x, y), radius = cv2.minEnclosingCircle(cnt)
                    center = (int(x), int(y))
                    radius = int(radius)
                    item = {'center': center, 'radius': radius, 'area': area}
                    areas_of_interest.append(item)
                    image_copy = cv2.circle(
                        img, center, radius,
                        (self.identifier_color[2], self.identifier_color[1], self.identifier_color[0]), 2
                    )
            areas_of_interest.sort(key=lambda item: (item['center'][1], item['center'][0]))
            return image_copy, areas_of_interest, base_contour_count
        else:
            return None, None, None

    def store_image(self, input_file, output_file, augmented_image, temperature_data=None):
        """
        Stores the processed image to the specified output file and transfers metadata.

        Args:
            input_file (str): Path to the input image file.
            output_file (str): Path to save the output image.
            augmented_image (numpy.ndarray): The augmented image to be saved.
            temperature_data (optional): Temperature data to transfer if applicable.
        """
        path = Path(output_file)
        if not os.path.exists(path.parents[0]):
            os.makedirs(path.parents[0])

        # Save the image first
        cv2.imencode(".jpg", augmented_image)[1].tofile(output_file)

        # Get XMP data from input file
        xmp_data = MetaDataHelper.extract_xmp(input_file)

        if platform.system() == "Darwin":
            MetaDataHelper.transfer_exif(input_file, output_file)
        else:
            if temperature_data is not None:
                MetaDataHelper.transfer_all_exiftool(input_file, output_file)
                MetaDataHelper.transfer_temperature_data(temperature_data, output_file)
            else:
                MetaDataHelper.transfer_exif(input_file, output_file)

        # Add XMP data if it exists in the input file
        if xmp_data:
            MetaDataHelper.embed_xmp(xmp_data, output_file)

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


class AlgorithmController:
    """Base class for algorithm controllers that manages algorithm options and validation."""

    def __init__(self, name, thermal=False):
        """
        Initializes the AlgorithmController with the given name and thermal flag.

        Args:
            name (str): Name of the algorithm.
            thermal (bool, optional): Indicates if the algorithm is for thermal images. Defaults to False.
        """
        self.name = name
        self.is_thermal = thermal

    def get_options(self):
        """
        Populates and returns options based on user-selected values.

        Returns:
            dict: A dictionary of option names and their values.
        """
        raise NotImplementedError

    def validate(self):
        """
        Validates that the required values have been provided.

        Returns:
            str: An error message if validation fails, else None.
        """
        raise NotImplementedError

    def load_options(self, options):
        """
        Sets UI elements based on provided options.

        Args:
            options (dict): Dictionary of options to set.
        """
        raise NotImplementedError


class AnalysisResult:
    """Class representing the result of an image processing operation."""

    def __init__(self, input_path=None, output_path=None, output_dir=None, areas_of_interest=None, base_contour_count=None, error_message=None):
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
        self.base_contour_count = base_contour_count
        self.error_message = error_message
