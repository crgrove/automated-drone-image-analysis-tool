import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from skimage import exposure
from core.services.LoggerService import LoggerService


class HistogramNormalizationService:
    """Service to adjust the histogram of a source image to match that of a reference image."""

    def __init__(self, hist_ref_path):
        """
        Initialize the HistogramNormalizationService with a reference image.

        Args:
            hist_ref_path (str): The file path to the reference image.

        Raises:
            Exception: If the file at hist_ref_path is not a valid image.
        """
        self.logger = LoggerService()
        try:
            with Image.open(hist_ref_path) as img:
                img.verify()  # Verifies it's a valid image
            # If no exception, proceed with OpenCV decoding
            self.hist_ref_img = cv2.imdecode(np.fromfile(hist_ref_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        except (UnidentifiedImageError, OSError):
            self.hist_ref_img = None  # Or handle the error as needed
        else:
            raise Exception("The reference image path is not a valid image file.")

    def match_histograms(self, src):
        """
        Match the histogram of a source image to that of the reference image.

        Args:
            src (numpy.ndarray): The source image as a numpy array.

        Returns:
            numpy.ndarray: The source image with a histogram matched to the reference image.

        Raises:
            Exception: If an error occurs during histogram matching.
        """
        try:
            return exposure.match_histograms(src, self.hist_ref_img, channel_axis=-1)
        except Exception as e:
            self.logger.error(e)
            raise
