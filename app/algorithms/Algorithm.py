import platform
import numpy as np
import cv2
import os
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

    def processImage(self, img, full_path, input_dir, output_dir):
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

    def circleAreasOfInterest(self, img, contours):
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

    def storeImage(self, input_file, output_file, augmented_image, temperature_data=None):
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
        cv2.imencode(".jpg", augmented_image)[1].tofile(output_file)
        if platform.system() == "Darwin":
            MetaDataHelper.transferExifPiexif(input_file, output_file)
        else:
            if temperature_data is not None:
                MetaDataHelper.transferAll(input_file, output_file)
                MetaDataHelper.transferTemperatureData(temperature_data, output_file)
            else:
                MetaDataHelper.transferExifPiexif(input_file, output_file)


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

    def getOptions(self):
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

    def loadOptions(self, options):
        """
        Sets UI elements based on provided options.

        Args:
            options (dict): Dictionary of options to set.
        """
        raise NotImplementedError


class AnalysisResult:
    """Class representing the result of an image processing operation."""

    def __init__(self, input_path=None, output_path=None, areas_of_interest=None, base_contour_count=None, error_message=None):
        """
        Initializes an AnalysisResult with the given parameters.

        Args:
            input_path (str, optional): Path to the input image. Defaults to None.
            output_path (str, optional): Path to the output image. Defaults to None.
            areas_of_interest (list, optional): List of detected areas of interest. Defaults to None.
            base_contour_count (int, optional): Count of base contours. Defaults to None.
            error_message (str, optional): Error message if processing failed. Defaults to None.
        """
        self.input_path = input_path
        self.output_path = output_path
        self.areas_of_interest = areas_of_interest
        self.base_contour_count = base_contour_count
        self.error_message = error_message
