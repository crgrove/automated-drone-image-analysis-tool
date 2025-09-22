import numpy as np
from ctypes import Structure, pointer, sizeof, c_float, POINTER, c_int, c_int8, c_int16, c_int32, c_uint8, c_uint32, cast, CDLL, c_void_p
import cv2
from typing import List
import os
import platform
import sys

DIRP_HANDLE = c_void_p
DIRP_VERBOSE_LEVEL_NONE = 0
DIRP_VERBOSE_LEVEL_DEBUG = 1
DIRP_VERBOSE_LEVEL_DETAIL = 2
DIRP_VERBOSE_LEVEL_NUM = 3


class dirp_rjpeg_version_t(Structure):
    """Structure representing the R-JPEG version information."""

    _fields_ = [
        ('rjpeg', c_uint32),   # Version of the R-JPEG itself
        ('header', c_uint32),  # Version of the header data in R-JPEG
        ('curve', c_uint32),   # Version of the curve LUT data in R-JPEG
    ]


class dirp_resolution_t(Structure):
    """Structure representing the resolution of the thermal image."""

    _fields_ = [
        ('width', c_uint32),   # Width of the image
        ('height', c_uint32),  # Height of the image
    ]


class dirp_measurement_params_t(Structure):
    """Structure representing temperature measurement parameters."""

    _fields_ = [
        ('distance', c_float),     # Distance to target (1-25 meters)
        ('humidity', c_float),     # Relative humidity of the environment (20-100%)
        ('emissivity', c_float),   # Surface emissivity (0.10-1.00)
        ('reflection', c_float),   # Reflected apparent temperature (-40.0 to 500.0°C)
    ]


class DjiThermalParserService:
    """Parser service for processing DJI thermal images."""

    DIRP_SUCCESS = 0
    DIRP_ERROR_MALLOC = -1
    DIRP_ERROR_POINTER_NULL = -2
    DIRP_ERROR_INVALID_PARAMS = -3
    DIRP_ERROR_INVALID_RAW = -4
    DIRP_ERROR_INVALID_HEADER = -5
    DIRP_ERROR_INVALID_CURVE = -6
    DIRP_ERROR_RJPEG_PARSE = -7
    DIRP_ERROR_SIZE = -8
    DIRP_ERROR_INVALID_HANDLE = -9
    DIRP_ERROR_FORMAT_INPUT = -10
    DIRP_ERROR_FORMAT_OUTPUT = -11
    DIRP_ERROR_UNSUPPORTED_FUNC = -12
    DIRP_ERROR_NOT_READY = -13
    DIRP_ERROR_ACTIVATION = -14
    DIRP_ERROR_ADVANCED = -32

    def __init__(self, dtype=np.float32):
        """
        Initialize the DjiThermalParserService with the specified data type.

        Args:
            dtype (type, optional): Data type for temperature arrays. Defaults to np.float32.
        """
        self._dtype = dtype
        (
            self._filepath_dirp,
            self._filepath_dirp_sub,
            self._filepath_iirp,
            self._filepath_exiftool,
        ) = self._get_default_filepaths()

        self._dll_dirp = CDLL(self._filepath_dirp)
        self._dll_dirp_sub = CDLL(self._filepath_dirp_sub)
        self._dll_iirp = CDLL(self._filepath_iirp)

        self._dirp_set_verbose_level = self._dll_dirp.dirp_set_verbose_level
        self._dirp_set_verbose_level.argtypes = [c_int]
        self._dirp_set_verbose_level(DIRP_VERBOSE_LEVEL_NONE)

        self._dirp_create_from_rjpeg = self._dll_dirp.dirp_create_from_rjpeg
        self._dirp_create_from_rjpeg.argtypes = [POINTER(c_uint8), c_int32, POINTER(DIRP_HANDLE)]
        self._dirp_create_from_rjpeg.restype = c_int32

        self._dirp_destroy = self._dll_dirp.dirp_destroy
        self._dirp_destroy.argtypes = [DIRP_HANDLE]
        self._dirp_destroy.restype = c_int32

        self._dirp_get_rjpeg_version = self._dll_dirp.dirp_get_rjpeg_version
        self._dirp_get_rjpeg_version.argtypes = [DIRP_HANDLE, POINTER(dirp_rjpeg_version_t)]
        self._dirp_get_rjpeg_version.restype = c_int32

        self._dirp_get_rjpeg_resolution = self._dll_dirp.dirp_get_rjpeg_resolution
        self._dirp_get_rjpeg_resolution.argtypes = [DIRP_HANDLE, POINTER(dirp_resolution_t)]
        self._dirp_get_rjpeg_resolution.restype = c_int32

        self._dirp_get_measurement_params = self._dll_dirp.dirp_get_measurement_params
        self._dirp_get_measurement_params.argtypes = [DIRP_HANDLE, POINTER(dirp_measurement_params_t)]
        self._dirp_get_measurement_params.restype = c_int32

        self._dirp_set_measurement_params = self._dll_dirp.dirp_set_measurement_params
        self._dirp_set_measurement_params.argtypes = [DIRP_HANDLE, POINTER(dirp_measurement_params_t)]
        self._dirp_set_measurement_params.restype = c_int32

        self._dirp_measure = self._dll_dirp.dirp_measure
        self._dirp_measure.argtypes = [DIRP_HANDLE, POINTER(c_int16), c_int32]
        self._dirp_measure.restype = c_int32

        self._dirp_measure_ex = self._dll_dirp.dirp_measure_ex
        self._dirp_measure_ex.argtypes = [DIRP_HANDLE, POINTER(c_float), c_int32]
        self._dirp_measure_ex.restype = c_int32

        self._dirp_set_pseudo_color = self._dll_dirp.dirp_set_pseudo_color
        self._dirp_set_pseudo_color.argtypes = [DIRP_HANDLE, c_int]
        self._dirp_set_pseudo_color.restype = c_int32

        self._dirp_process = self._dll_dirp.dirp_process
        self._dirp_process.argtypes = [DIRP_HANDLE, POINTER(c_uint8), c_int32]
        self._dirp_process.restype = c_int32

    def temperatures(self, filepath_image: str, image_height: int = 512, image_width: int = 640,
                     object_distance: float = 5.0, relative_humidity: float = 70.0,
                     emissivity: float = 1.0, reflected_apparent_temperature: float = 23.0,
                     m2ea_mode: bool = False):
        """
        Parse thermal image data to extract temperature values.

        Args:
            filepath_image (str): Path to the R-JPEG image file.
            image_height (int): Height of the image.
            image_width (int): Width of the image.
            object_distance (float): Distance to target (1-25 meters).
            relative_humidity (float): Relative humidity (20-100%).
            emissivity (float): Emissivity of the target surface (0.10-1.00).
            reflected_apparent_temperature (float): Reflected temperature in Celsius (-40.0 to 500.0).
            m2ea_mode (bool): Mode setting specific to some DJI models.

        Returns:
            np.ndarray: 2D array of temperature values.

        References:
            * [DJI Thermal SDK](https://www.dji.com/cn/downloads/softwares/dji-thermal-sdk)
        """
        with open(filepath_image, 'rb') as file:
            raw = file.read()
            raw_size = c_int32(len(raw))
            raw_c_uint8 = cast(raw, POINTER(c_uint8))

        handle = DIRP_HANDLE()
        rjpeg_version = dirp_rjpeg_version_t()
        rjpeg_resolution = dirp_resolution_t()

        return_status = self._dirp_create_from_rjpeg(raw_c_uint8, raw_size, handle)
        assert return_status == self.DIRP_SUCCESS, f'dirp_create_from_rjpeg error {filepath_image}:{return_status}'
        assert self._dirp_get_rjpeg_version(handle, rjpeg_version) == self.DIRP_SUCCESS
        assert self._dirp_get_rjpeg_resolution(handle, rjpeg_resolution) == self.DIRP_SUCCESS

        if not m2ea_mode:
            params = dirp_measurement_params_t()
            params_point = pointer(params)
            return_status = self._dirp_get_measurement_params(handle, params_point)
            assert return_status == self.DIRP_SUCCESS, f'dirp_get_measurement_params error {filepath_image}:{return_status}'

            params.distance = object_distance
            params.humidity = relative_humidity
            params.emissivity = emissivity
            params.reflection = reflected_apparent_temperature

            return_status = self._dirp_set_measurement_params(handle, params)
            assert return_status == self.DIRP_SUCCESS, f'dirp_set_measurement_params error {filepath_image}:{return_status}'

        if self._dtype == np.float32:
            data = np.zeros(image_width * image_height, dtype=np.float32)
            data_ptr = data.ctypes.data_as(POINTER(c_float))
            data_size = c_int32(image_width * image_height * sizeof(c_float))
            return_status = self._dirp_measure_ex(handle, data_ptr, data_size)
            assert return_status == self.DIRP_SUCCESS, f'_dirp_measure_ex error {filepath_image}:{return_status}'
            temp = np.reshape(data, (image_height, image_width))
        elif self._dtype == np.int16:
            data = np.zeros(image_width * image_height, dtype=np.int16)
            data_ptr = data.ctypes.data_as(POINTER(c_int16))
            data_size = c_int32(image_width * image_height * sizeof(c_int16))
            return_status = self._dirp_measure(handle, data_ptr, data_size)
            assert return_status == self.DIRP_SUCCESS, f'_dirp_measure error {filepath_image}:{return_status}'
            temp = np.reshape(data, (image_height, image_width)) / 10
        else:
            raise ValueError("Unsupported data type for temperature extraction.")
        return np.array(temp, dtype=self._dtype)

    def image(self, filepath_image: str, palette: int):
        """
        Generate a color-mapped thermal image from temperature data.

        Args:
            filepath_image (str): Path to the R-JPEG image file.
            palette (int): Color palette to apply to the thermal image.

        Returns:
            np.ndarray: Color-mapped thermal image.
        """
        color_map = self._get_color_map(palette)
        with open(filepath_image, 'rb') as file:
            raw = file.read()
            raw_size = c_int32(len(raw))
            raw_c_uint8 = cast(raw, POINTER(c_uint8))

        handle = DIRP_HANDLE()
        rjpeg_version = dirp_rjpeg_version_t()
        rjpeg_resolution = dirp_resolution_t()

        return_status = self._dirp_create_from_rjpeg(raw_c_uint8, raw_size, handle)
        assert return_status == self.DIRP_SUCCESS, f'dirp_create_from_rjpeg error {filepath_image}:{return_status}'
        assert self._dirp_get_rjpeg_version(handle, rjpeg_version) == self.DIRP_SUCCESS
        assert self._dirp_get_rjpeg_resolution(handle, rjpeg_resolution) == self.DIRP_SUCCESS

        return_status = self._dirp_set_pseudo_color(handle, color_map)
        assert return_status == self.DIRP_SUCCESS

        data = np.zeros(rjpeg_resolution.width * rjpeg_resolution.height * 3, dtype=np.uint8)
        data_ptr = data.ctypes.data_as(POINTER(c_uint8))
        data_size = c_int32(rjpeg_resolution.height * rjpeg_resolution.width * 3 * sizeof(c_uint8))

        assert self._dirp_process(handle, data_ptr, data_size) == self.DIRP_SUCCESS
        img = np.reshape(data, (rjpeg_resolution.height, rjpeg_resolution.width, 3))

        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def _get_color_map(self, palette: str):
        """
        Map a generic palette name to a platform-specific color map value.

        Args:
            palette (str): Name of the color palette.

        Returns:
            int: Platform-specific color map code.
        """
        match palette:
            case "Inferno (Iron Red)":
                return 2
            case "White Hot":
                return 0
            case "Black Hot":
                return 9
            case "Hot (Fulgurite)":
                return 1
            case "Jet (Rainbow2)":
                return 7
            case _:
                return 0

    def _get_default_filepaths(self) -> List[str]:
        """
        Get the default file paths for required libraries based on platform and architecture.

        Returns:
            list[str]: List of file paths to required DLLs or shared libraries.

        Raises:
            NotImplementedError: If the platform or architecture is unsupported.
        """
        # Determine the base path based on whether we're running from a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running from a PyInstaller bundle
            app_root = sys._MEIPASS
        else:
            # Running from source code
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        folder_plugin = os.path.join(app_root, 'external')
        system = platform.system()
        architecture = platform.architecture()[0]

        if system == "Windows":
            if architecture == "32bit":
                return [os.path.join(folder_plugin, v) for v in [
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x86/libdirp.dll',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x86/libv_dirp.dll',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x86/libv_iirp.dll',
                        'exiftool.exe',
                        ]
                        ]
            elif architecture == "64bit":
                return [os.path.join(folder_plugin, v) for v in [
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x64/libdirp.dll',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x64/libv_dirp.dll',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x64/libv_iirp.dll',
                        'exiftool.exe',
                        ]
                        ]
        elif system == "Linux":
            if architecture == "32bit":
                return [
                    *[os.path.join(folder_plugin, v) for v in [
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x86/libdirp.so',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x86/libv_dirp.so',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x86/libv_iirp.so',
                    ]],
                    'exiftool'
                ]
            elif architecture == "64bit":
                return [
                    *[os.path.join(folder_plugin, v) for v in [
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x64/libdirp.so',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x64/libv_dirp.so',
                        'dji_thermal_sdk_v1.7_20241205/windows/release_x64/libv_iirp.so',
                    ]],
                    'exiftool'
                ]

        raise NotImplementedError(f'currently not supported for running on this platform {system}:{architecture}')
