import numpy as np
from ctypes import Structure,  c_float, c_int, c_uint16, c_char_p, c_char, CDLL, POINTER
import cv2
from typing import List
import os

# Define the data structures


class Autel_IR_INFO_S(Structure):
    _fields_ = [
        ('tag', c_uint16),
        ('len', c_uint16),
        ('show_value', c_char_p),
        ('str_value', c_char * 512),
        ('num_value', c_int)
    ]


class QPointF(Structure):
    _fields_ = [
        ('x', c_int),
        ('y', c_int)
    ]


class TempStatInfo(Structure):
    _fields_ = [
        ('max', c_float),
        ('min', c_float),
        ('avg', c_float),
        ('maxPoint', QPointF),
        ('minPoint', QPointF)
    ]


class AutelThermalImageParser:
    def __init__(
        self,
        dtype=np.float32,
    ):
        self._dtype = dtype
        self._filepath_dll = self.get_default_filepaths()
        self.ir_temp_parse = CDLL(self._filepath_dll)
        # Define the function prototypes
        self.ir_temp_parse.GetIrPhotoTempInfo_Bridge.argtypes = [
            c_char_p,  # filepath
            c_int,     # w
            c_int,     # h
            POINTER(c_float)  # tempArray (2D array)
        ]
        self.ir_temp_parse.GetIrPhotoTempInfo_Bridge.restype = c_int

    def temperatures(
        self,
        filepath_image: str,
        image_height: int = 512,
        image_width: int = 640,
    ):
        data = np.zeros(image_width * image_height, dtype=np.float32)
        data_ptr = data.ctypes.data_as(POINTER(c_float))
        ret = self.ir_temp_parse.GetIrPhotoTempInfo_Bridge(filepath_image.encode('utf-8'), image_width, image_height, data_ptr)
        temp = None
        if ret == 0:
            temp = np.reshape(data, (image_height, image_width))
        return temp

    def image(self, temperatures: np.ndarray, palette: int):
        """
         Generates a numpy array representing the thermal image for FLIR cameras
         :String filepath_image: file path of original jpg
         :String palette: the name of palette
         :return numpy.ndarray
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
        Takes in a generic name for the palette and returns the platform-specific variation
        :String palette: the name of palette

        :return mixed: returns the int or string representing the color map that can be processed for the indicated camera type.

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
                return 7
            case _:
                return 1

    def get_default_filepaths(self):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'external/autel/AutelBridge.dll')
