import numpy as np
from ctypes import Structure, c_float, c_int, c_uint16, c_char_p, c_char, CDLL, POINTER
import cv2
from typing import List
import os


# Define the data structures
class Autel_IR_INFO_S(Structure):
    """Data structure for storing Autel IR information."""
    _fields_ = [
        ('tag', c_uint16),
        ('len', c_uint16),
        ('show_value', c_char_p),
        ('str_value', c_char * 512),
        ('num_value', c_int)
    ]


class QPointF(Structure):
    """Data structure for storing a point with integer x and y coordinates."""
    _fields_ = [
        ('x', c_int),
        ('y', c_int)
    ]


class TempStatInfo(Structure):
    """Data structure for storing temperature statistics with max, min, and average values."""
    _fields_ = [
        ('max', c_float),
        ('min', c_float),
        ('avg', c_float),
        ('maxPoint', QPointF),
        ('minPoint', QPointF)
    ]


class AutelThermalImageParser:
    """Parser for processing thermal images from Autel cameras."""

    def __init__(self, dtype=np.float32):
        """
        Initialize the AutelThermalImageParser with specified data type and load the Autel DLL.

        Args:
            dtype (type, optional): Data type for temperature arrays. Defaults to np.float32.
        """
        self._dtype = dtype
        self._filepath_dll = self.get_default_filepaths()
        self.ir_temp_parse = CDLL(self._filepath_dll)

        # Define the function prototypes for the DLL
        self.ir_temp_parse.GetIrPhotoTempInfo_Bridge.argtypes = [
            c_char_p,  # filepath
            c_int,     # width
            c_int,     # height
            POINTER(c_float)  # temperature array
        ]
        self.ir_temp_parse.GetIrPhotoTempInfo_Bridge.restype = c_int

    def temperatures(self, filepath_image: str, image_height: int = 512, image_width: int = 640):
        """
        Extract temperature data from a thermal image.

        Args:
            filepath_image (str): Path to the thermal image file.
            image_height (int, optional): Height of the image. Defaults to 512.
            image_width (int, optional): Width of the image. Defaults to 640.

        Returns:
            np.ndarray or None: 2D array of temperature values if successful, otherwise None.
        """
        data = np.zeros(image_width * image_height, dtype=np.float32)
        data_ptr = data.ctypes.data_as(POINTER(c_float))
        ret = self.ir_temp_parse.GetIrPhotoTempInfo_Bridge(filepath_image.encode('utf-8'), image_width, image_height, data_ptr)

        if ret == 0:
            return np.reshape(data, (image_height, image_width))
        return None

    def image(self, temperatures: np.ndarray, palette: str):
        """
        Generate a color-mapped thermal image from temperature data.

        Args:
            temperatures (np.ndarray): 2D array of temperature values.
            palette (str): The color palette to use for the thermal image.

        Returns:
            np.ndarray: Color-mapped thermal image.
        """
        color_map = self.getColorMap(palette)
        normed = cv2.normalize(temperatures, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        grey = cv2.cvtColor(normed, cv2.COLOR_GRAY2BGR)

        if color_map == -1:
            colorized_img = 255 - grey
        elif color_map == 1:
            colorized_img = grey
        else:
            colorized_img = cv2.applyColorMap(grey, color_map)
        return colorized_img

    def getColorMap(self, palette: str):
        """
        Get the OpenCV color map for the specified palette.

        Args:
            palette (str): Name of the color palette.

        Returns:
            int: OpenCV colormap constant or custom value for grayscale maps.
        """
        match palette:
            case "Inferno (Iron Red)":
                return cv2.COLORMAP_INFERNO
            case "White Hot":
                return 1
            case "Black Hot":
                return -1
            case "Hot (Fulgurite)":
                return cv2.COLORMAP_HOT
            case "cv2.COLORMAP_JET":
                return cv2.COLORMAP_JET
            case _:
                return 1

    def get_default_filepaths(self):
        """
        Get the default file path for the Autel DLL.

        Returns:
            str: Path to the Autel DLL file.
        """
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'external/autel/AutelBridge.dll')
