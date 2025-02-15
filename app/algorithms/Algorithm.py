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
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius) + self.aoi_radius

                if area >= self.min_area and area <= self.max_area:
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
        xmp_data = MetaDataHelper.get_xmp_data(input_file)
        
        if platform.system() == "Darwin":
            MetaDataHelper.transfer_exif_piexif(input_file, output_file)
        else:
            if temperature_data is not None:
                MetaDataHelper.transfer_all(input_file, output_file)
                MetaDataHelper.transfer_temperature_data(temperature_data, output_file)
            else:
                MetaDataHelper.transfer_exif_piexif(input_file, output_file)
        
        # Add XMP data if it exists in the input file
        if xmp_data:
            MetaDataHelper.set_xmp_data(output_file, xmp_data)

    def split_image(self, img, segments):
        """
        Divides a single image into multiple segments based on the specified number of segments.

        Args:
            img (numpy.ndarray): The image to be divided into segments.
            segments (int): The number of segments to split the image into.

        Returns:
            list: A list of lists containing numpy.ndarrays representing the segments of the original image.
        """
        h, w, channels = img.shape
        pieces = []
        if segments == 2:
            w_size = math.ceil(w / 2)
            pieces.append([img[:, :w_size], img[:, w - w_size:]])
        elif segments == 4:
            w_size = math.ceil(w / 2)
            h_size = math.ceil(h / 2)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w - w_size:]],
                [img[h_size:, :w_size], img[h_size:, w - w_size:]]
            ])
        elif segments == 6:
            w_size = math.ceil(w / 3)
            h_size = math.ceil(h / 2)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w_size:w_size * 2], img[:h_size, w_size * 2:]],
                [img[h_size:, :w_size], img[h_size:, w_size:w_size * 2], img[h_size:, w_size * 2:]]
            ])
        elif segments == 9:
            w_size = math.ceil(w / 3)
            h_size = math.ceil(h / 3)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w_size:w_size * 2], img[:h_size, w_size * 2:]],
                [img[h_size:h_size * 2, :w_size], img[h_size:h_size * 2, w_size:w_size * 2], img[h_size:h_size * 2, w_size * 2:]],
                [img[h_size * 2:, :w_size], img[h_size * 2:, w_size:w_size * 2], img[h_size * 2:, w_size * 2:]]
            ])
        elif segments == 16:
            w_size = math.ceil(w / 4)
            h_size = math.ceil(h / 4)
            pieces.extend([
                [img[:h_size, :w_size], img[:h_size, w_size:w_size * 2], img[:h_size, w_size * 2:w_size * 3], img[:h_size, w_size * 3:]],
                [img[h_size:h_size * 2, :w_size], img[h_size:h_size * 2, w_size:w_size * 2], img[h_size:h_size * 2, w_size * 2:w_size * 3],
                 img[h_size:h_size * 2, w_size * 3:]],
                [img[h_size * 2:h_size * 3, :w_size], img[h_size * 2:h_size * 3, w_size:w_size * 2], img[h_size * 2:h_size * 3, w_size * 2:w_size * 3],
                 img[h_size * 2:h_size * 3, w_size * 3:]],
                [img[h_size * 3:, :w_size], img[h_size * 3:, w_size:w_size * 2], img[h_size * 3:, w_size * 2:w_size * 3], img[h_size * 3:, w_size * 3:]]
            ])
        elif segments == 25:
            w_size = math.ceil(w / 5)
            h_size = math.ceil(h / 5)
            pieces.extend([
                [img[:h_size, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size:h_size * 2, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size * 2:h_size * 3, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size * 3:h_size * 4, i * w_size:(i + 1) * w_size] for i in range(5)],
                [img[h_size * 4:, i * w_size:(i + 1) * w_size] for i in range(5)]
            ])
        elif segments == 36:
            w_size = math.ceil(w / 6)
            h_size = math.ceil(h / 6)
            pieces.extend([
                [img[:h_size, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size:h_size * 2, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 2:h_size * 3, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 3:h_size * 4, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 4:h_size * 5, i * w_size:(i + 1) * w_size] for i in range(6)],
                [img[h_size * 5:, i * w_size:(i + 1) * w_size] for i in range(6)]
            ])
        else:
            pieces.append([img])
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
