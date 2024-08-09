import numpy as np
from ctypes import *
import cv2
from typing import List
import os
import platform

DIRP_HANDLE = c_void_p
DIRP_VERBOSE_LEVEL_NONE = 0  # 0: Print none
DIRP_VERBOSE_LEVEL_DEBUG = 1  # 1: Print debug log
DIRP_VERBOSE_LEVEL_DETAIL = 2  # 2: Print all log
DIRP_VERBOSE_LEVEL_NUM = 3  # 3: Total number

class dirp_rjpeg_version_t(Structure):
	"""
	References:
		* [DJI Thermal SDK](https://www.dji.com/cn/downloads/softwares/dji-thermal-sdk)
	"""

	_fields_ = [
		# Version number of the opened R-JPEG itself.
		('rjpeg', c_uint32),
		# Version number of the header data in R-JPEG
		('header', c_uint32),
		# Version number of the curve LUT data in R-JPEG
		('curve', c_uint32),
	]


class dirp_resolution_t(Structure):
	"""
	References:
		* [DJI Thermal SDK](https://www.dji.com/cn/downloads/softwares/dji-thermal-sdk)
	"""

	_fields_ = [
		# Horizontal size
		('width', c_uint32),
		# Vertical size
		('height', c_uint32),
	]


class dirp_measurement_params_t(Structure):
	"""
	References:
		* [DJI Thermal SDK](https://www.dji.com/cn/downloads/softwares/dji-thermal-sdk)
	"""

	_fields_ = [
		# The distance to the target. Value range is [1~25] meters.
		('distance', c_float),
		# How strongly the target surface is emitting energy as thermal radiation. Value range is [0.10~1.00].
		('humidity', c_float),
		# The relative humidity of the environment. Value range is [20~100] percent. Defualt value is 70%.
		('emissivity', c_float),
		# Reflected temperature in Celsius.
		# The surface of the target that is measured could reflect the energy radiated by the surrounding objects.
		# Value range is [-40.0~500.0]
		('reflection', c_float),
	]

class DjiThermalParserService:

	# dirp_ret_code_e
	DIRP_SUCCESS = 0  # 0: Success (no error)
	DIRP_ERROR_MALLOC = -1  # -1: Malloc error
	DIRP_ERROR_POINTER_NULL = -2  # -2: NULL pointer input
	DIRP_ERROR_INVALID_PARAMS = -3  # -3: Invalid parameters input
	DIRP_ERROR_INVALID_RAW = -4  # -4: Invalid RAW in R-JPEG
	DIRP_ERROR_INVALID_HEADER = -5  # -5: Invalid header in R-JPEG
	DIRP_ERROR_INVALID_CURVE = -6  # -6: Invalid curve LUT in R-JPEG
	DIRP_ERROR_RJPEG_PARSE = -7  # -7: Parse error for R-JPEG data
	DIRP_ERROR_SIZE = -8  # -8: Wrong size input
	DIRP_ERROR_INVALID_HANDLE = -9  # -9: Invalid handle input
	DIRP_ERROR_FORMAT_INPUT = -10  # -10: Wrong input image format
	DIRP_ERROR_FORMAT_OUTPUT = -11  # -11: Wrong output image format
	DIRP_ERROR_UNSUPPORTED_FUNC = -12  # -12: Unsupported function called
	DIRP_ERROR_NOT_READY = -13  # -13: Some preliminary conditions not meet
	DIRP_ERROR_ACTIVATION = -14  # -14: SDK activate failed
	DIRP_ERROR_ADVANCED = -32  # -32: Advanced error codes which may be smaller than this value

	def __init__(
			self,
			dtype=np.float32,
	):
		self._dtype = dtype
		(
		self._filepath_dirp,
		self._filepath_dirp_sub,
		self._filepath_iirp,
		self._filepath_exiftool,
		) = self.get_default_filepaths()

		self._dll_dirp = CDLL(self._filepath_dirp)
		self._dll_dirp_sub = CDLL(self._filepath_dirp_sub)
		self._dll_iirp = CDLL(self._filepath_iirp)
		
		self._dirp_set_verbose_level = self._dll_dirp.dirp_set_verbose_level
		self._dirp_set_verbose_level.argtypes = [c_int]
		self._dirp_set_verbose_level(DIRP_VERBOSE_LEVEL_NONE)

		# Create a new DIRP handle with specified R-JPEG binary data.
		# The R-JPEG binary data buffer must remain valid until the handle is destroyed.
		# The DIRP API library will create some alloc buffers for inner usage.
		# So the application should reserve enough stack size for the library.
		self._dirp_create_from_rjpeg = self._dll_dirp.dirp_create_from_rjpeg
		self._dirp_create_from_rjpeg.argtypes = [POINTER(c_uint8), c_int32, POINTER(DIRP_HANDLE)]
		self._dirp_create_from_rjpeg.restype = c_int32

		# Destroy the DIRP handle.
		self._dirp_destroy = self._dll_dirp.dirp_destroy
		self._dirp_destroy.argtypes = [DIRP_HANDLE]
		self._dirp_destroy.restype = c_int32

		self._dirp_get_rjpeg_version = self._dll_dirp.dirp_get_rjpeg_version
		self._dirp_get_rjpeg_version.argtypes = [DIRP_HANDLE, POINTER(dirp_rjpeg_version_t)]
		self._dirp_get_rjpeg_version.restype = c_int32

		self._dirp_get_rjpeg_resolution = self._dll_dirp.dirp_get_rjpeg_resolution
		self._dirp_get_rjpeg_resolution.argtypes = [DIRP_HANDLE, POINTER(dirp_resolution_t)]
		self._dirp_get_rjpeg_resolution.restype = c_int32

		# Get orignial/custom temperature measurement parameters.
		self._dirp_get_measurement_params = self._dll_dirp.dirp_get_measurement_params
		self._dirp_get_measurement_params.argtypes = [DIRP_HANDLE, POINTER(dirp_measurement_params_t)]
		self._dirp_get_measurement_params.restype = c_int32

		# Set custom temperature measurement parameters.
		self._dirp_set_measurement_params = self._dll_dirp.dirp_set_measurement_params
		self._dirp_set_measurement_params.argtypes = [DIRP_HANDLE, POINTER(dirp_measurement_params_t)]
		self._dirp_set_measurement_params.restype = c_int32

		# Measure temperature of whole thermal image with RAW data in R-JPEG.
		# Each INT16 pixel value represents ten times the temperature value in Celsius. In other words,
		# each LSB represents 0.1 degrees Celsius.
		self._dirp_measure = self._dll_dirp.dirp_measure
		self._dirp_measure.argtypes = [DIRP_HANDLE, POINTER(c_int16), c_int32]
		self._dirp_measure.restype = c_int32

		# Measure temperature of whole thermal image with RAW data in R-JPEG.
		# Each float32 pixel value represents the real temperature in Celsius.
		self._dirp_measure_ex = self._dll_dirp.dirp_measure_ex
		self._dirp_measure_ex.argtypes = [DIRP_HANDLE, POINTER(c_float), c_int32]
		self._dirp_measure_ex.restype = c_int32
		
		self._dirp_set_pseudo_color = self._dll_dirp.dirp_set_pseudo_color
		self._dirp_set_pseudo_color.argtypes = [DIRP_HANDLE, c_int]
		self._dirp_set_pseudo_color.restype = c_int32
		
		self._dirp_process = self._dll_dirp.dirp_process
		self._dirp_process.argtypes = [DIRP_HANDLE, POINTER(c_uint8), c_int32]
		self._dirp_process.restype = c_int32
		
	def temperatures(
			self,
			filepath_image: str,
			image_height: int = 512,
			image_width: int = 640,
			object_distance: float = 5.0,
			relative_humidity: float = 70.0,
			emissivity: float = 1.0,
			reflected_apparent_temperature: float = 23.0,
			m2ea_mode: bool = False,
	):
		"""
		Parser infrared camera data as `NumPy` data`.
		`dirp2` means `DJI IR Processing Version 2nd`.

		Args:
			filepath_image: str, relative path of R-JPEG image
			image_height: float, image height
			image_width: float, image width
			object_distance: float, The distance to the target. Value range is [1~25] meters.
			relative_humidity: float, The relative humidity of the environment. Value range is [20~100] percent. Defualt value is 70%.
			emissivity: float, How strongly the target surface is emitting energy as thermal radiation. Value range is [0.10~1.00].
			reflected_apparent_temperature: float, Reflected temperature in Celsius. The surface of the target that is measured could reflect the energy radiated by the surrounding objects. Value range is [-40.0~500.0]
			m2ea_mode: bool

		Returns:
			np.ndarray: temperature array

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
		assert return_status == self.DIRP_SUCCESS, 'dirp_create_from_rjpeg error {}:{}'.format(filepath_image, return_status)
		assert self._dirp_get_rjpeg_version(handle, rjpeg_version) == self.DIRP_SUCCESS
		assert self._dirp_get_rjpeg_resolution(handle, rjpeg_resolution) == self.DIRP_SUCCESS

		if not m2ea_mode:
			params = dirp_measurement_params_t()
			params_point = pointer(params)
			return_status = self._dirp_get_measurement_params(handle, params_point)
			assert return_status == self.DIRP_SUCCESS, 'dirp_get_measurement_params error {}:{}'.format(filepath_image, return_status)

			if isinstance(object_distance, (float, int)):
				params.distance = object_distance
			if isinstance(relative_humidity, (float, int)):
				params.humidity = relative_humidity
			if isinstance(emissivity, (float, int)):
				params.emissivity = emissivity
			if isinstance(reflected_apparent_temperature, (float, int)):
				params.reflection = reflected_apparent_temperature
			
			return_status = self._dirp_set_measurement_params(handle, params)
			assert return_status == self.DIRP_SUCCESS, 'dirp_set_measurement_params error {}:{}'.format(filepath_image, return_status)
		if self._dtype.__name__ == np.float32.__name__:
			data = np.zeros(image_width * image_height, dtype=np.float32)
			data_ptr = data.ctypes.data_as(POINTER(c_float))
			data_size = c_int32(image_width * image_height * sizeof(c_float))
			return_status = self._dirp_measure_ex(handle, data_ptr, data_size) 
			assert return_status == self.DIRP_SUCCESS, '_dirp_measure_ex error {}:{}'.format(filepath_image, return_status)
			temp = np.reshape(data, (image_height, image_width))
		elif self._dtype.__name__ == np.int16.__name__:
			data = np.zeros(image_width * image_height, dtype=np.int16)
			data_ptr = data.ctypes.data_as(POINTER(c_int16))
			data_size = c_int32(image_width * image_height * sizeof(c_int16))
			return_status = self._dirp_measure(handle, data_ptr, data_size)
			assert return_status == self.DIRP_SUCCESS, '_dirp_measure error {}:{}'.format(filepath_image, return_status)
			temp = np.reshape(data, (image_height, image_width)) / 10
		else:
			raise ValueError
		#assert self._dirp_destroy(handle) == self.DIRP_SUCCESS
		return np.array(temp, dtype=self._dtype)

	def image(self, filepath_image: str, palette:int):
		"""
		 Generates a numpy array representing the thermal image for DJI cameras
		 :String filepath_image: file path of original jpg
		 :String palette: the name of palette
		 :return numpy.ndarray
		"""
		color_map = self.getColorMap(palette)
		with open(filepath_image, 'rb') as file:
			raw = file.read()
			raw_size = c_int32(len(raw))
			raw_c_uint8 = cast(raw, POINTER(c_uint8))

		handle = DIRP_HANDLE()
		rjpeg_version = dirp_rjpeg_version_t()
		rjpeg_resolution = dirp_resolution_t()

		return_status = self._dirp_create_from_rjpeg(raw_c_uint8, raw_size, handle)
		assert return_status == self.DIRP_SUCCESS, 'dirp_create_from_rjpeg error {}:{}'.format(filepath_image, return_status)
		assert self._dirp_get_rjpeg_version(handle, rjpeg_version) == self.DIRP_SUCCESS
		assert self._dirp_get_rjpeg_resolution(handle, rjpeg_resolution) == self.DIRP_SUCCESS
		
		palette = c_int(color_map)
		return_status = self._dirp_set_pseudo_color(handle, palette)
		assert return_status == self.DIRP_SUCCESS

		data = np.zeros(rjpeg_resolution.width  * rjpeg_resolution.height * 3, dtype=np.uint8)
		data_ptr = data.ctypes.data_as(POINTER(c_uint8))
		data_size = c_int32(rjpeg_resolution.height * rjpeg_resolution.width * 3 * sizeof(c_uint8))

		assert self._dirp_process(handle, data_ptr, data_size) == self.DIRP_SUCCESS
		img = np.reshape(data, (rjpeg_resolution.height, rjpeg_resolution.width, 3))
		
		return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
	   
	def getColorMap(self, palette:str):
		"""
		Takes in a generic name for the palette and returns the platform-specific variation
		:String palette: the name of palette

		:return mixed: returns the int or string representing the color map that can be processed for the indicated camera type.
			
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
	def get_default_filepaths(self) -> List[str]:
		folder_plugin = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'external')
		system = platform.system()
		architecture = platform.architecture()[0]
		if system == "Windows":
			if architecture == "32bit":
				return [os.path.join(folder_plugin, v) for v in [
					'dji_thermal_sdk_v1.5_20240507/windows/release_x86/libdirp.dll',
					'dji_thermal_sdk_v1.5_20240507/windows/release_x86/libv_dirp.dll',
					'dji_thermal_sdk_v1.5_20240507/windows/release_x86/libv_iirp.dll',
					'exiftool.exe',
				]]
			elif architecture == "64bit":
				return [os.path.join(folder_plugin, v) for v in [
					'dji_thermal_sdk_v1.5_20240507/windows/release_x64/libdirp.dll',
					'dji_thermal_sdk_v1.5_20240507/windows/release_x64/libv_dirp.dll',
					'dji_thermal_sdk_v1.5_20240507/windows/release_x64/libv_iirp.dll',
					'exiftool.exe',
				]]
		elif system == "Linux":
			if architecture == "32bit":
				return [
					*[os.path.join(folder_plugin, v) for v in [
						'dji_thermal_sdk_v1.5_20240507/windows/release_x86/libdirp.so',
						'dji_thermal_sdk_v1.5_20240507/windows/release_x86/libv_dirp.so',
						'dji_thermal_sdk_v1.5_20240507/windows/release_x86/libv_iirp.so',
					]],
					'exiftool'
				]
			elif architecture == "64bit":
				return [
					*[os.path.join(folder_plugin, v) for v in [
						'dji_thermal_sdk_v1.5_20240507/windows/release_x64/libdirp.so',
						'dji_thermal_sdk_v1.5_20240507/windows/release_x64/libv_dirp.so',
						'dji_thermal_sdk_v1.5_20240507/windows/release_x64/libv_iirp.so',
					]],
					'exiftool'
				]

		raise NotImplementedError(f'currently not supported for running on this platform {system}:{architecture}')