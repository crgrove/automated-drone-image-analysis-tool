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
    """Service for parsing and extracting thermal data from FLIR thermal images."""

    def __init__(self, dtype=np.float32):
        """
        Initialize the FlirThermalParserService.

        Args:
            dtype (type, optional): Data type for temperature arrays. Defaults to np.float32.
        """
        self._dtype = dtype

    def temperatures(self, filepath_image: str, emissivity: float = 1.0, object_distance: float = 1.0,
                     atmospheric_temperature: float = 20.0, reflected_apparent_temperature: float = 20.0,
                     ir_window_temperature: float = 20.0, ir_window_transmission: float = 1.0,
                     relative_humidity: float = 50.0, planck_r1: float = 21106.77, planck_b: float = 1501.0,
                     planck_f: float = 1.0, planck_o: float = -7340.0, planck_r2: float = 0.012545258,
                     ata1: float = 0.006569, ata2: float = 0.01262, atb1: float = -0.002276,
                     atb2: float = -0.00667, atx: float = 1.9) -> np.ndarray:
        """
        Convert FLIR thermal image data to temperature values.

        Args:
            filepath_image (str): Path to the thermal image file.
            emissivity (float): Emissivity of the object.
            object_distance (float): Distance to the object in meters.
            atmospheric_temperature (float): Atmospheric temperature in °C.
            reflected_apparent_temperature (float): Reflected temperature in °C.
            ir_window_temperature (float): Temperature of IR window in °C.
            ir_window_transmission (float): Transmission of IR window.
            relative_humidity (float): Relative humidity in %.
            planck_r1, planck_b, planck_f, planck_o, planck_r2 (float): FLIR calibration constants.
            ata1, ata2, atb1, atb2, atx (float): Constants for calculating humidity effects on transmission.

        Returns:
            np.ndarray: Array of temperature values in °C.
        """
        thermal_img_bytes = MetaDataHelper.get_raw_temperature_data(filepath_image)
        thermal_img_stream = BytesIO(thermal_img_bytes)
        thermal_img = Image.open(thermal_img_stream)
        img_format = thermal_img.format

        if img_format == 'TIFF':
            raw = np.array(thermal_img)
        elif img_format == 'PNG':
            raw = self.unpack(filepath_image)
        else:
            raise ValueError("Unsupported image format")

        # Compute temperature from raw data and transmission parameters
        emiss_wind = 1 - ir_window_transmission
        refl_wind = 0
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
        raw_refl1 = planck_r1 / (planck_r2 * (np.exp(planck_b / (reflected_apparent_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o
        raw_refl1_attn = (1 - emissivity) / emissivity * raw_refl1
        raw_atm1 = planck_r1 / (planck_r2 * (np.exp(planck_b / (atmospheric_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o
        raw_atm1_attn = (1 - tau1) / emissivity / tau1 * raw_atm1
        raw_wind = planck_r1 / (planck_r2 * (np.exp(planck_b / (ir_window_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o
        raw_wind_attn = emiss_wind / emissivity / tau1 / ir_window_transmission * raw_wind
        raw_refl2 = planck_r1 / (planck_r2 * (np.exp(planck_b / (reflected_apparent_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o
        raw_refl2_attn = refl_wind / emissivity / tau1 / ir_window_transmission * raw_refl2
        raw_atm2 = planck_r1 / (planck_r2 * (np.exp(planck_b / (atmospheric_temperature + ABSOLUTE_ZERO)) - planck_f)) - planck_o
        raw_atm2_attn = (1 - tau2) / emissivity / tau1 / ir_window_transmission / tau2 * raw_atm2
        raw_obj = raw / emissivity / tau1 / ir_window_transmission / tau2 - raw_atm1_attn - raw_atm2_attn - raw_wind_attn - raw_refl1_attn - raw_refl2_attn
        val_to_log = planck_r1 / (planck_r2 * (raw_obj + planck_o)) + planck_f

        if any(val_to_log.ravel() < 0):
            raise ValueError(f'Image appears to be corrupted: {filepath_image}')

        temperature = planck_b / np.log(val_to_log) - ABSOLUTE_ZERO
        return np.array(temperature, self._dtype)

    def image(self, temperatures: np.ndarray, palette: int):
        """
        Generate a color-mapped thermal image from temperature data.

        Args:
            temperatures (np.ndarray): 2D array of temperature values.
            palette (int): Color palette for the thermal image.

        Returns:
            np.ndarray: Color-mapped thermal image.
        """
        color_map = self._get_color_map(palette)
        normed = cv2.normalize(temperatures, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        grey = cv2.cvtColor(normed, cv2.COLOR_GRAY2BGR)

        if color_map == -1:
            colorized_img = 255 - grey
        elif color_map == 1:
            colorized_img = grey
        else:
            colorized_img = cv2.applyColorMap(grey, color_map)

        return colorized_img

    def _get_color_map(self, palette: str):
        """
        Map a generic palette name to an OpenCV color map code.

        Args:
            palette (str): Name of the color palette.

        Returns:
            int: OpenCV color map code.
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
        """
        Unpack the thermal data from a FLIR image.

        Args:
            path_or_stream (Union[str, BinaryIO]): Path to FLIR file or byte stream.

        Returns:
            np.ndarray: Array of raw thermal data.
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
            raise ValueError('Invalid input for unpacking thermal data.')

    def extract_flir_app1(self, stream: BinaryIO) -> BinaryIO:
        """
        Extract APP1 segments from FLIR JPEG file.

        Args:
            stream (BinaryIO): Byte stream of JPEG file.

        Returns:
            BinaryIO: Byte stream containing APP1 FLIR segments.

        Raises:
            ValueError: If file is invalid or segments are inconsistent.
        """
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
            if chunks.get(chunk_num, None) is not None:
                raise ValueError('Invalid FLIR: duplicate chunk number')
            chunks[chunk_num] = chunk

            if chunk_num == chunks_count:
                break

        if chunks_count is None:
            raise ValueError('Invalid FLIR: no metadata encountered')

        flir_app1_bytes = b''.join(chunks[chunk_num] for chunk_num in range(chunks_count + 1))
        flir_app1_stream = BytesIO(flir_app1_bytes)
        flir_app1_stream.seek(0)
        return flir_app1_stream

    def parse_flir_chunk(self, stream: BinaryIO, chunks_count: Optional[int]) -> Optional[Tuple[int, int, bytes]]:
        """
        Parse a single FLIR chunk.

        Args:
            stream (BinaryIO): Byte stream of JPEG file.
            chunks_count (Optional[int]): Total number of chunks.

        Returns:
            Optional[Tuple[int, int, bytes]]: Parsed chunk data.
        """
        marker = stream.read(CHUNK_APP1_BYTES_COUNT)
        length_bytes = stream.read(CHUNK_LENGTH_BYTES_COUNT)
        length = int.from_bytes(length_bytes, 'big') - CHUNK_METADATA_LENGTH
        magic_flir = stream.read(CHUNK_MAGIC_BYTES_COUNT)

        if not (marker == APP1_MARKER and magic_flir == MAGIC_FLIR_DEF):
            stream.seek(-len(marker) - len(length_bytes) - len(magic_flir), 1)
            return None

        stream.seek(1, 1)
        chunk_num = int.from_bytes(stream.read(CHUNK_NUM_BYTES_COUNT), 'big')
        chunks_tot = int.from_bytes(stream.read(CHUNK_TOT_BYTES_COUNT), 'big')

        if chunks_count is None:
            chunks_count = chunks_tot

        if (chunks_tot is None or chunk_num < 0 or chunk_num > chunks_tot or chunks_tot != chunks_count):
            raise ValueError(f'Invalid FLIR: inconsistent total chunks, expected 0 or greater, found {chunks_tot}')

        return chunks_tot, chunk_num, stream.read(length + 1)

    def parse_thermal(self, stream: BinaryIO, records: Dict[int, Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Parse the thermal data from the APP1 segment.

        Args:
            stream (BinaryIO): Byte stream containing APP1 FLIR segments.
            records (Dict[int, Tuple[int, int, int, int]]): FLIR records metadata.

        Returns:
            np.ndarray: Raw thermal data array.
        """
        record_idx_raw_data = 1
        raw_data_md = records[record_idx_raw_data]
        _, _, raw_data = self.parse_raw_data(stream, raw_data_md)
        return raw_data

    def parse_flir_app1(self, stream: BinaryIO) -> Dict[int, Tuple[int, int, int, int]]:
        """
        Parse APP1 segment metadata.

        Args:
            stream (BinaryIO): Byte stream of APP1 FLIR segment.

        Returns:
            Dict[int, Tuple[int, int, int, int]]: Parsed record metadata.
        """
        _ = stream.read(4)
        stream.seek(16, 1)
        record_dir_offset = int.from_bytes(stream.read(4), 'big')
        record_dir_entries_count = int.from_bytes(stream.read(4), 'big')
        stream.seek(record_dir_offset)

        record_dir_stream = BytesIO(stream.read(32 * record_dir_entries_count))
        record_details: Dict[int, Tuple[int, int, int, int]] = {}

        for record_nr in range(record_dir_entries_count):
            record_dir_stream.seek(0)
            details = self.parse_flir_record_metadata(stream, record_nr)
            if details:
                record_details[details[1]] = details

        return record_details

    def parse_flir_record_metadata(self, stream: BinaryIO, record_nr: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Parse FLIR record metadata.

        Args:
            stream (BinaryIO): Byte stream of FLIR data.
            record_nr (int): Record index.

        Returns:
            Optional[Tuple[int, int, int, int]]: Parsed record metadata.
        """
        entry = 32 * record_nr
        stream.seek(entry)
        record_type = int.from_bytes(stream.read(2), 'big')
        if record_type < 1:
            return None

        record_offset = int.from_bytes(stream.read(4), 'big')
        record_length = int.from_bytes(stream.read(4), 'big')
        return entry, record_type, record_offset, record_length

    def parse_raw_data(self, stream: BinaryIO, metadata: Tuple[int, int, int, int]):
        """
        Parse raw thermal data from FLIR metadata.

        Args:
            stream (BinaryIO): Byte stream containing raw thermal data.
            metadata (Tuple[int, int, int, int]): Metadata for thermal data.

        Returns:
            Tuple[int, int, np.ndarray]: Width, height, and thermal data array.
        """
        (_, _, offset, length) = metadata
        stream.seek(offset)

        stream.seek(2, 1)
        width = int.from_bytes(stream.read(2), 'little')
        height = int.from_bytes(stream.read(2), 'little')

        stream.seek(offset + 32)
        thermal_bytes = stream.read(length)
        thermal_stream = BytesIO(thermal_bytes)
        thermal_img = Image.open(thermal_stream)
        thermal_np = np.array(thermal_img)

        if thermal_np.shape != (height, width):
            raise ValueError("Image dimensions don't match metadata")

        fix_byte_order = np.vectorize(lambda x: (x >> 8) + ((x & 0x00FF) << 8))
        thermal_np = fix_byte_order(thermal_np)

        return width, height, thermal_np
