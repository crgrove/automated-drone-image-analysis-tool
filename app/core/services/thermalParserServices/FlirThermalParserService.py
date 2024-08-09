import os
import numpy as np
import cv2
from io import BufferedIOBase, BytesIO
from PIL import Image
from typing import BinaryIO, Dict, Optional, Tuple, Union
import exiftool

from helpers.MetaDataHelper import MetaDataHelper

ABSOLUTE_ZERO = 273.15

SEGMENT_SEP = b'\xff'
APP1_MARKER = b'\xe1'
MAGIC_FLIR_DEF = b'FLIR\x00'

CHUNK_APP1_BYTES_COUNT = len(APP1_MARKER)
CHUNK_LENGTH_BYTES_COUNT = 2
CHUNK_MAGIC_BYTES_COUNT = len(MAGIC_FLIR_DEF)
CHUNK_SKIP_BYTES_COUNT = 1
CHUNK_NUM_BYTES_COUNT = 1
CHUNK_TOT_BYTES_COUNT = 1
CHUNK_PARTIAL_METADATA_LENGTH = CHUNK_APP1_BYTES_COUNT + CHUNK_LENGTH_BYTES_COUNT + CHUNK_MAGIC_BYTES_COUNT
CHUNK_METADATA_LENGTH = (
		CHUNK_PARTIAL_METADATA_LENGTH + CHUNK_SKIP_BYTES_COUNT + CHUNK_NUM_BYTES_COUNT + CHUNK_TOT_BYTES_COUNT
)

class FlirThermalParserService:	
	def __init__(
			self,
			dtype=np.float32,
	):
		self._dtype = dtype

	def temperatures(
			self,
			filepath_image: str,
			# params
			emissivity: float = 1.0,
			object_distance: float = 1.0,
			atmospheric_temperature: float = 20.0,
			reflected_apparent_temperature: float = 20.0,
			ir_window_temperature: float = 20.0,
			ir_window_transmission: float = 1.0,
			relative_humidity: float = 50.0,
			# planck constants
			planck_r1: float = 21106.77,
			planck_b: float = 1501.0,
			planck_f: float = 1.0,
			planck_o: float = -7340.0,
			planck_r2: float = 0.012545258,
			# constants
			ata1: float = 0.006569,
			ata2: float = 0.01262,
			atb1: float = -0.002276,
			atb2: float = -0.00667,
			atx: float = 1.9,
	) -> np.ndarray:
		"""
		Parser infrared camera data as `NumPy` data`.

		Equations to convert to temperature see http://130.15.24.88/exiftool/forum/index.php/topic,4898.60.html or https://github.com/gtatters/Thermimage/blob/master/R/raw2temp.R

		Args:
			filepath_image: str, relative path of R-JPEG image
			emissivity: float, E: Emissivity - default 1, should be ~0.95 to 0.97 depending on source
			object_distance: float, OD: Object distance in metres
			atmospheric_temperature: float, ATemp: atmospheric temperature for tranmission loss - one value from FLIR file (oC) - default = RTemp
			reflected_apparent_temperature: float, RTemp: apparent reflected temperature - one value from FLIR file (oC), default 20C
			ir_window_temperature: float, Infrared Window Temperature - default = RTemp (oC)
			ir_window_transmission: float, Infrared Window transmission - default 1.  likely ~0.95-0.96. Should be empirically determined.
			relative_humidity: float, Relative humidity - default 50%
			Calibration Constants                                          (A FLIR SC660, A FLIR T300(25o), T300(telephoto), A Mikron 7515)
			planck_r1: float, PlanckR1 calibration constant from FLIR file  21106.77       14364.633         14906.216       21106.77
			planck_b: float, PlanckB calibration constant from FLIR file    1501           1385.4            1396.5          9758.743281
			planck_f: float, PlanckF calibration constant from FLIR file    1              1                 1               29.37648768
			planck_o: float, PlanckO calibration constant from FLIR file    -7340          -5753             -7261           1278.907078
			planck_r2: float, PlanckR2 calibration constant form FLIR file  0.012545258    0.010603162       0.010956882     0.0376637583528285
			ata1: float, Atmospheric Trans Alpha 1  0.006569 constant for calculating humidity effects on transmission
			ata2: float, Atmospheric Trans Alpha 2  0.012620 constant for calculating humidity effects on transmission
			atb1: float, Atmospheric Trans Beta 1  -0.002276 constant for calculating humidity effects on transmission
			atb2: float, Atmospheric Trans Beta 2  -0.006670 constant for calculating humidity effects on transmission
			atx: float, Atmospheric Trans X        1.900000 constant for calculating humidity effects on transmission

		Returns:
			np.ndarray: temperature array

		References:
			* from https://github.com/gtatters/Thermimage/blob/master/R/raw2temp.R
			* from https://github.com/detecttechnologies/thermal_base
			* from https://github.com/aloisklink/flirextractor/blob/1fc759808c747ad5562a9ddb3cd75c4def8a3f69/flirextractor/raw_temp_to_celcius.py
		"""
		"""
		thermal_img_bytes = subprocess.check_output([
			self._filepath_exiftool, '-RawThermalImage', '-b', filepath_image
		])
		"""
		thermal_img_bytes = MetaDataHelper.getRawTemperatureData(filepath_image)
		thermal_img_stream = BytesIO(thermal_img_bytes)
		thermal_img = Image.open(thermal_img_stream)
		img_format = thermal_img.format

		# checking for the type of the decoded images
		if img_format == 'TIFF':
			raw = np.array(thermal_img)
		elif img_format == 'PNG':
			raw = self.unpack(filepath_image)
		else:
			raise ValueError

		# transmission through window (calibrated)
		emiss_wind = 1 - ir_window_transmission
		refl_wind = 0
		# transmission through the air
		h2o = (relative_humidity / 100) * np.exp(
			1.5587
			+ 0.06939 * atmospheric_temperature
			- 0.00027816 * atmospheric_temperature ** 2
			+ 0.00000068455 * atmospheric_temperature ** 3
		)
		tau1 = atx * np.exp(-np.sqrt(object_distance / 2) * (ata1 + atb1 * np.sqrt(h2o))) + (1 - atx) * np.exp(
			-np.sqrt(object_distance / 2) * (ata2 + atb2 * np.sqrt(h2o))
		)
		tau2 = atx * np.exp(-np.sqrt(object_distance / 2) * (ata1 + atb1 * np.sqrt(h2o))) + (1 - atx) * np.exp(
			-np.sqrt(object_distance / 2) * (ata2 + atb2 * np.sqrt(h2o))
		)
		# radiance from the environment
		raw_refl1 = planck_r1 / (planck_r2 * (np.exp(planck_b / (reflected_apparent_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o
		# Reflected component
		raw_refl1_attn = (1 - emissivity) / emissivity * raw_refl1

		# Emission from atmosphere 1
		raw_atm1 = (planck_r1 / (planck_r2 * (np.exp(planck_b / (atmospheric_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o)
		# attenuation for atmospheric 1 emission
		raw_atm1_attn = (1 - tau1) / emissivity / tau1 * raw_atm1

		# Emission from window due to its own temp
		raw_wind = (planck_r1 / (planck_r2 * (np.exp(planck_b / (ir_window_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o)
		# Componen due to window emissivity
		raw_wind_attn = (emiss_wind / emissivity / tau1 / ir_window_transmission * raw_wind)

		# Reflection from window due to external objects
		raw_refl2 = (planck_r1 / (planck_r2 * (np.exp(planck_b / (reflected_apparent_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o)
		# component due to window reflectivity
		raw_refl2_attn = (refl_wind / emissivity / tau1 / ir_window_transmission * raw_refl2)

		# Emission from atmosphere 2
		raw_atm2 = (planck_r1 / (planck_r2 * (np.exp(planck_b / (atmospheric_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o)
		# attenuation for atmospheric 2 emission
		raw_atm2_attn = ((1 - tau2) / emissivity / tau1 / ir_window_transmission / tau2 * raw_atm2)

		raw_obj = (
				raw / emissivity / tau1 / ir_window_transmission / tau2
				- raw_atm1_attn
				- raw_atm2_attn
				- raw_wind_attn
				- raw_refl1_attn
				- raw_refl2_attn
		)
		val_to_log = planck_r1 / (planck_r2 * (raw_obj + planck_o)) + planck_f
		if any(val_to_log.ravel() < 0):
			raise ValueError('Image seems to be corrupted:{}'.format(filepath_image))
		# temperature from radiance
		temperature = planck_b / np.log(val_to_log) - ABSOLUTE_ZERO
		return np.array(temperature, self._dtype)
	
	def image(self, temperatures: np.ndarray, palette:int):
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
	
	def getColorMap(self, palette:str):
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
			
	def unpack(self, path_or_stream: Union[str, BinaryIO]) -> np.ndarray:
		"""Unpacks the FLIR image, meaning that it will return the thermal data embedded in the image.

		Parameters
		----------
		path_or_stream : Union[str, BinaryIO]
			Either a path (string) to a FLIR file, or a byte stream such as
			BytesIO or file opened as `open(file_path, 'rb')`.

		Returns
		-------
		FlyrThermogram
			When successful, a FlyrThermogram object containing thermogram data.
		"""
		if isinstance(path_or_stream, str) and os.path.isfile(path_or_stream):
			with open(path_or_stream, 'rb') as flirh:
				return self.unpack(flirh)
		elif isinstance(path_or_stream, (BufferedIOBase, BinaryIO)):
			stream = path_or_stream
			flir_app1_stream = self.extract_flir_app1(stream)
			flir_records = self.parse_flir_app1(flir_app1_stream)
			raw_np = self.parse_thermal(flir_app1_stream, flir_records)

			return raw_np
		else:
			raise ValueError('Incorrect input')

	def extract_flir_app1(self, stream: BinaryIO) -> BinaryIO:
		"""Extracts the FLIR APP1 bytes.

		Parameters
		---------
		stream : BinaryIO
			A full bytes stream of a JPEG file, expected to be a FLIR file.

		Raises
		------
		ValueError
			When the file is invalid in one the next ways, a
			ValueError is thrown.

			* File is not a JPEG
			* A FLIR chunk number occurs more than once
			* The total chunks count is inconsistent over multiple chunks
			* No APP1 segments are successfully parsed

		Returns
		-------
		BinaryIO
			A bytes stream of the APP1 FLIR segments
		"""
		# Check JPEG-ness
		_ = stream.read(2)

		chunks_count: Optional[int] = None
		chunks: Dict[int, bytes] = {}
		while True:
			b = stream.read(1)
			if b == b'':
				break

			if b != SEGMENT_SEP:
				continue

			parsed_chunk = self.parse_flir_chunk(stream, chunks_count)
			if not parsed_chunk:
				continue

			chunks_count, chunk_num, chunk = parsed_chunk
			chunk_exists = chunks.get(chunk_num, None) is not None
			if chunk_exists:
				raise ValueError('Invalid FLIR: duplicate chunk number')
			chunks[chunk_num] = chunk

			# Encountered all chunks, break out of loop to process found metadata
			if chunk_num == chunks_count:
				break

		if chunks_count is None:
			raise ValueError('Invalid FLIR: no metadata encountered')

		flir_app1_bytes = b''
		for chunk_num in range(chunks_count + 1):
			flir_app1_bytes += chunks[chunk_num]

		flir_app1_stream = BytesIO(flir_app1_bytes)
		flir_app1_stream.seek(0)
		return flir_app1_stream


	def parse_flir_chunk(self, stream: BinaryIO, chunks_count: Optional[int]) -> Optional[Tuple[int, int, bytes]]:
		"""Parse flir chunk."""
		# Parse the chunk header. Headers are as follows (definition with example):
		#
		#     \xff\xe1<length: 2 bytes>FLIR\x00\x01<chunk nr: 1 byte><chunk count: 1 byte>
		#     \xff\xe1\xff\xfeFLIR\x00\x01\x01\x0b
		#
		# Meaning: Exif APP1, 65534 long, FLIR chunk 1 out of 12
		marker = stream.read(CHUNK_APP1_BYTES_COUNT)

		length_bytes = stream.read(CHUNK_LENGTH_BYTES_COUNT)
		length = int.from_bytes(length_bytes, 'big')
		length -= CHUNK_METADATA_LENGTH
		magic_flir = stream.read(CHUNK_MAGIC_BYTES_COUNT)

		if not (marker == APP1_MARKER and magic_flir == MAGIC_FLIR_DEF):
			# Seek back to just after byte b and continue searching for chunks
			stream.seek(-len(marker) - len(length_bytes) - len(magic_flir), 1)
			return None

		stream.seek(1, 1)  # skip 1 byte, unsure what it is for

		chunk_num = int.from_bytes(stream.read(CHUNK_NUM_BYTES_COUNT), 'big')
		chunks_tot = int.from_bytes(stream.read(CHUNK_TOT_BYTES_COUNT), 'big')

		# Remember total chunks to verify metadata consistency
		if chunks_count is None:
			chunks_count = chunks_tot

		if (  # Check whether chunk metadata is consistent
				chunks_tot is None or chunk_num < 0 or chunk_num > chunks_tot or chunks_tot != chunks_count
		):
			raise ValueError(f'Invalid FLIR: inconsistent total chunks, should be 0 or greater, but is {chunks_tot}')

		return chunks_tot, chunk_num, stream.read(length + 1)


	def parse_thermal(self, stream: BinaryIO, records: Dict[int, Tuple[int, int, int, int]]) -> np.ndarray:
		"""Parse thermal."""
		record_idx_raw_data = 1
		raw_data_md = records[record_idx_raw_data]
		_, _, raw_data = self.parse_raw_data(stream, raw_data_md)
		return raw_data


	def parse_flir_app1(self, stream: BinaryIO) -> Dict[int, Tuple[int, int, int, int]]:
		"""Parse flir app1."""
		# 0x00 - string[4] file format ID = 'FFF\0'
		# 0x04 - string[16] file creator: seen '\0','MTX IR\0','CAMCTRL\0'
		# 0x14 - int32u file format version = 100
		# 0x18 - int32u offset to record directory
		# 0x1c - int32u number of entries in record directory
		# 0x20 - int32u next free index ID = 2
		# 0x24 - int16u swap pattern = 0 (?)
		# 0x28 - int16u[7] spares
		# 0x34 - int32u[2] reserved
		# 0x3c - int32u checksum

		# 1. Read 0x40 bytes and verify that its contents equals AFF\0 or FFF\0
		_ = stream.read(4)

		# 2. Read FLIR record directory metadata (ref 3)
		stream.seek(16, 1)
		_ = int.from_bytes(stream.read(4), 'big')
		record_dir_offset = int.from_bytes(stream.read(4), 'big')
		record_dir_entries_count = int.from_bytes(stream.read(4), 'big')
		stream.seek(28, 1)
		_ = int.from_bytes(stream.read(4), 'big')

		# 3. Read record directory (which is a FLIR record entry repeated
		# `record_dir_entries_count` times)
		stream.seek(record_dir_offset)
		record_dir_stream = BytesIO(stream.read(32 * record_dir_entries_count))

		# First parse the record metadata
		record_details: Dict[int, Tuple[int, int, int, int]] = {}
		for record_nr in range(record_dir_entries_count):
			record_dir_stream.seek(0)
			details = self.parse_flir_record_metadata(stream, record_nr)
			if details:
				record_details[details[1]] = details

		# Then parse the actual records
		# for (entry_idx, type, offset, length) in record_details:
		#     parse_record = record_parsers[type]
		#     stream.seek(offset)
		#     record = BytesIO(stream.read(length + 36))  # + 36 needed to find end
		#     parse_record(record, offset, length)

		return record_details


	def parse_flir_record_metadata(self, stream: BinaryIO, record_nr: int) -> Optional[Tuple[int, int, int, int]]:
		"""Parse flir record metadata."""
		# FLIR record entry (ref 3):
		# 0x00 - int16u record type
		# 0x02 - int16u record subtype: RawData 1=BE, 2=LE, 3=PNG; 1 for other record types
		# 0x04 - int32u record version: seen 0x64,0x66,0x67,0x68,0x6f,0x104
		# 0x08 - int32u index id = 1
		# 0x0c - int32u record offset from start of FLIR data
		# 0x10 - int32u record length
		# 0x14 - int32u parent = 0 (?)
		# 0x18 - int32u object number = 0 (?)
		# 0x1c - int32u checksum: 0 for no checksum
		entry = 32 * record_nr
		stream.seek(entry)
		record_type = int.from_bytes(stream.read(2), 'big')
		if record_type < 1:
			return None

		_ = int.from_bytes(stream.read(2), 'big')
		_ = int.from_bytes(stream.read(4), 'big')
		_ = int.from_bytes(stream.read(4), 'big')
		record_offset = int.from_bytes(stream.read(4), 'big')
		record_length = int.from_bytes(stream.read(4), 'big')
		_ = int.from_bytes(stream.read(4), 'big')
		_ = int.from_bytes(stream.read(4), 'big')
		_ = int.from_bytes(stream.read(4), 'big')
		return entry, record_type, record_offset, record_length


	def parse_raw_data(self, stream: BinaryIO, metadata: Tuple[int, int, int, int]):
		"""Parse raw data."""
		(_, _, offset, length) = metadata
		stream.seek(offset)

		stream.seek(2, 1)
		width = int.from_bytes(stream.read(2), 'little')
		height = int.from_bytes(stream.read(2), 'little')

		stream.seek(offset + 32)

		# Read the bytes with the raw thermal data and decode using PIL
		thermal_bytes = stream.read(length)
		thermal_stream = BytesIO(thermal_bytes)
		thermal_img = Image.open(thermal_stream)
		thermal_np = np.array(thermal_img)

		# Check shape
		if thermal_np.shape != (height, width):
			msg = 'Invalid FLIR: metadata\'s width and height don\'t match thermal data\'s actual width ' \
				'and height ({} vs ({}, {})'
			msg = msg.format(thermal_np.shape, height, width)
			raise ValueError(msg)

		# FLIR PNG data is in the wrong byte order, fix that
		fix_byte_order = np.vectorize(lambda x: (x >> 8) + ((x & 0x00FF) << 8))
		thermal_np = fix_byte_order(thermal_np)

		return width, height, thermal_np