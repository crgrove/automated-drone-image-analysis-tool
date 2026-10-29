"""PythonDjiThermalParserService: Convert DJI R-JPEG thermal images to Celsius arrays in pure Python/numpy.

This pure Python/numpy converter is compatible with the MIT-licensed `dji_irp` utility for four of its plugins:
iirp (InfiRay cores), girp (Guide), hirp (HIKMICRO), and dirp (DJI). No other closed-source code, binaries,
sample images, or SDK outputs were used during development.

Development began with public information including radiometric physics (Planck, Wien, Stefan-Boltzmann;
Sakuma-Hattori band radiance), published formulas (Bolton's vapor pressure, FLIR's atmospheric water content),
ExifTool's R-JPEG tag documentation, and InfiRay's libirtemp documentation for the tau table's layout and
distance grid (read in the GPL-3.0 danjulio/iCam project). Approximately 800k+ synthetic conversions were obtained
by the `dji_irp` v1.9 utility used as an oracle to generate training output. `Claude as a researcher` was then
utilized to refine formula shapes for each sensor and fit their coefficients to target accuracies within reasonable
input constraints. This process was iterative.

The accuracy is scored for each camera per raw code against the synthetic output only in the typical SAR
region of settings as follows: 10...120m, ambient -20...50C, RH 10...90%, emissivity 0.5...1.0, reflected
-20...50C, aiming for more than 99% of results within 0.5C and none beyond 1.0C. Note that several sensors have
tighter input range constraints than these typical SAR figures (and one M3TD result entry misses the target).
Accuracy is not measured outside these ranges, as well as for outputs beyond -20..80C. Additional measurements were
then made on held-out SAR sample images at their stored settings. For reference, many radiometric sensors rate
their temperature measurement accuracy at ±2°C (or greater) under optimal conditions.

  Camera      Sensor            Synthetic w/in 0.5C (max Δ)     SAR Samples w/in 0.5C (max Δ)
  H20N        iirp 0.2.1        100%   (0.24C)                  100% (0.00C)
  H20T        dirp              100%   (0.18C)                  100% (0.06C)
  H30T        iirp 0.3.0        100%   (0.10C)                  100% (0.00C)
  M2EA        iirp 0.1.0        100%   (0.16C)                  100% (0.03C)
  M3T         iirp 0.2.0        100%   (0.17C)                  100% (0.00C)
  M30T        iirp 0.2.0        100%   (0.16C)                  100% (0.00C)
  M30T        girp              100%   (0.37C)                  100% (0.16C)
  M3TD        iirp 0.2.0        100%   (0.16C)                  100% (0.00C)
  M3TD        hirp high         99.99% (0.79C)                  100% (0.15C)
  M3TD        hirp low          97.49% (4.12C)                  100% (0.49C)
  XT S        dirp              100%   (0.44C)                  100% (0.15C)

Next steps TODO: We need to test far more SAR Samples to sufficiently increase confidence. On Windows or Linux, this
can be easily accomplished by explicitly running:
`pytest --no-cov app/tests/core/services/thermal/accuracy_python_dji_thermal_parser_service.py` which will test all
of the images present in the app/tests/data/thermal/input/* subdirectories (where data.zip normally expands into).
This test will not otherwise automatically run, so the entirety of the tests are wholly undisturbed.
"""
import os
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from core.services.LoggerService import LoggerService

# In the comments and messages here, "the SDK" is DJI Thermal SDK v1.9, as its dji_irp utility behaves.
APP1, APP2, APP3, APP4, APP5 = 0xE1, 0xE2, 0xE3, 0xE4, 0xE5
K0 = 273.15
Source = Union[str, 'os.PathLike[str]', bytes, bytearray, memoryview]     # a file path or the JPEG's bytes


def _t4_mix(t: Union[np.ndarray, float], weight: Union[np.ndarray, float], t_ref: float, invalid: float = -K0) -> np.ndarray:
    """Solve Stefan-Boltzmann mixing (T_obs + K0)^4 = w (T + K0)^4 + (1 - w)(T_ref + K0)^4 for T, `invalid` where nothing is left."""
    num = ((np.asarray(t, np.float64) + K0) ** 4 - (1.0 - weight) * (t_ref + K0) ** 4) / weight    # (T + K0)^4
    return np.where(num > 0, np.abs(num) ** 0.25 - K0, invalid)       # abs: np.where evaluates both branches


def _trunc_f32(value: float, step: float) -> float:
    """trunc(value / step) * step on the float32 the SDK receives, multiplied in float32 (0.779 -> 0.77, 45.19 -> 45.1; 0.77 and 45.1 stay, as in the SDK)."""
    v = np.float32(value)                                # the SDK takes its settings as float32
    return float(np.trunc(v * np.float32(1.0 / step))) * step     # float() first: a float64 product


class RjpegUnsupportedError(ValueError):
    """Not an R-JPEG this module can convert (unknown container, or a field outside what was validated)."""


class RjpegParameterError(ValueError):
    """
    A setting the SDK itself refuses: when set (dirp_set_measurement_params, including a reflected radiance above the hottest
    code's), or when measuring (stored settings outside its limits).
    """


class RjpegUndefinedOutputError(ValueError):
    """Settings for which the SDK's own output is not a temperature (an iirp refusal rc)."""


@dataclass(frozen=True)
class MeasurementParams:
    """SDK measurement parameters: distance m, humidity %, emissivity, reflected C, ambient C."""
    distance: float
    humidity: float
    emissivity: float
    reflection: float
    ambient: float


class RjpegFile:
    """A JPEG's segments before start-of-scan: segments lists (marker, payload offset, payload length)."""

    def __init__(self, source: Source) -> None:
        """
        Read the segments of a file path or JPEG bytes.

        Args:
            source (str | os.PathLike | bytes): Path to the R-JPEG image file, or its bytes.

        Raises:
            RjpegUnsupportedError: If the data is not a JPEG.
        """
        if isinstance(source, (bytes, bytearray, memoryview)):
            self.data = bytes(source)
        else:
            with open(source, 'rb') as file:
                self.data = file.read()
        if self.data[:2] != b'\xff\xd8':
            raise RjpegUnsupportedError('not a JPEG file')
        self.segments: List[Tuple[int, int, int]] = []
        self._apps: Dict[int, bytes] = {}
        i = 2                                            # past the start-of-image marker FF D8
        while i + 4 <= len(self.data) and self.data[i] == 0xFF and self.data[i + 1] != 0xDA:      # FF xx segments, until start-of-scan
            length = struct.unpack('>H', self.data[i + 2:i + 4])[0]     # big-endian, counting its own two bytes
            self.segments.append((self.data[i + 1], i + 4, length - 2))
            i += 2 + length

    def app(self, marker: int) -> bytes:
        """
        Return the payloads of every segment with this marker, concatenated (APP3 and APP4 can span several).

        Args:
            marker (int): The segment marker, e.g. APP4.

        Returns:
            bytes: The concatenated payloads, empty if the file has none.
        """
        if marker not in self._apps:
            self._apps[marker] = b''.join(self.data[offset:offset + length] for m, offset, length in self.segments if m == marker)
        return self._apps[marker]

    def u16(self, marker: int) -> np.ndarray:
        """
        Return the marker's payload as little-endian uint16 words.

        Args:
            marker (int): The segment marker, e.g. APP3.

        Returns:
            np.ndarray: The payload's uint16 words.
        """
        payload = self.app(marker)
        return np.frombuffer(payload[:len(payload) // 2 * 2], '<u2')

    def field(self, marker: int, offset: int, fmt: str) -> int:
        """
        Return one field of the marker's payload.

        Args:
            marker (int): The segment marker, e.g. APP4.
            offset (int): The field's byte offset in the payload.
            fmt (str): The field's struct format, e.g. '<h'.

        Returns:
            int: The field's value.
        """
        return struct.unpack_from(fmt, self.app(marker), offset)[0]

    def camera(self) -> Tuple[str, str]:
        """
        Return the EXIF Make and Model (TIFF IFD0 tags 0x010F and 0x0110).

        Returns:
            tuple[str, str]: Make and Model, or empty strings where the file has none.
        """
        for marker, offset, length in self.segments:
            exif = self.data[offset:offset + length]
            if marker != APP1 or exif[:6] != b'Exif\x00\x00':     # APP1 also holds XMP
                continue
            tiff = exif[6:]
            if tiff[:2] not in (b'II', b'MM'):
                return '', ''
            order = '<' if tiff[:2] == b'II' else '>'    # byte order: Intel or Motorola
            found: Dict[int, str] = {}
            try:
                ifd = struct.unpack_from(order + 'I', tiff, 4)[0]
                for i in range(struct.unpack_from(order + 'H', tiff, ifd)[0]):
                    tag, kind, count, value = struct.unpack_from(order + 'HHII', tiff, ifd + 2 + 12 * i)    # 12-byte IFD entries
                    if tag in (0x010F, 0x0110) and kind == 2:                # ASCII, inline if it fits in 4 bytes
                        at = ifd + 10 + 12 * i if count <= 4 else value
                        found[tag] = tiff[at:at + count].split(b'\x00')[0].decode('ascii', 'replace')
            except struct.error:                         # a damaged IFD: no camera
                return '', ''
            return found.get(0x010F, ''), found.get(0x0110, '')
        return '', ''


class _RjpegConverter(ABC):
    """
    One SDK plugin's conversion.

    Subclasses set family, variant, models, shape, ranges and RAW (the raw image's marker), and define detect, stored and
    convert.
    """
    family: str = '?'
    variant: str = '?'
    models: Tuple[str, ...] = ()                                 # the EXIF camera models (Make DJI) it was validated on
    shape: Tuple[int, int] = (512, 640)                          # the image (rows, cols) it was validated on
    ranges: Dict[str, Tuple[float, float]] = {}                  # API ranges as dirp_get_measurement_params_range reports them
    accepted: Optional[Dict[str, Tuple[float, float]]] = None    # the ranges the SDK enforces, where they differ from those it reports
    RAW: int = APP3

    def __init__(self, rjpeg: RjpegFile) -> None:
        """
        Initialize the converter for a parsed file.

        Args:
            rjpeg (RjpegFile): The parsed R-JPEG.
        """
        self.rjpeg = rjpeg

    @classmethod
    @abstractmethod
    def detect(cls, rjpeg: RjpegFile) -> Optional['_RjpegConverter']:
        """
        Return the converter for this family's container.

        Args:
            rjpeg (RjpegFile): The parsed R-JPEG.

        Returns:
            _RjpegConverter or None: The converter, or None for another container.
        """

    @abstractmethod
    def stored(self) -> MeasurementParams:
        """
        Return the settings the file holds, as the SDK reports them.

        Returns:
            MeasurementParams: The stored settings.
        """

    @abstractmethod
    def convert(self, params: MeasurementParams, api: bool) -> np.ndarray:
        """
        Convert the raw image to temperatures.

        Args:
            params (MeasurementParams): The settings to measure at.
            api (bool): True for settings passed through the API, False for the stored path.

        Returns:
            np.ndarray: Temperatures in Celsius, one per raw code.
        """

    def validate(self) -> None:
        """
        Check the file is from a camera model this family was validated on, at the validated size.

        Raises:
            RjpegUnsupportedError: If the camera model or the image size was not validated.
        """
        make, model = self.rjpeg.camera()
        if make != 'DJI' or model not in self.models:   # e.g. the M4T, whose HIKMICRO files share the M3TD's container
            raise RjpegUnsupportedError(f"{self.family} {self.variant} container from {make or 'no make'} {model or 'no model'}: "
                                        f"validated only on DJI {', '.join(self.models)}")
        if len(self.rjpeg.app(self.RAW)) != 2 * self.shape[0] * self.shape[1]:     # 16-bit raw codes
            raise RjpegUnsupportedError(f"{self.family} {self.variant}: {len(self.rjpeg.app(self.RAW))} raw bytes, "
                                        f"not the validated {self.shape[1]} x {self.shape[0]} image")

    def check(self, params: MeasurementParams) -> None:
        """
        Check the settings are inside the ranges the SDK enforces.

        Args:
            params (MeasurementParams): The settings passed through the API.

        Raises:
            RjpegParameterError: If a setting is outside its range.
        """
        for name, (low, high) in (self.accepted or self.ranges).items():
            value = getattr(params, name)
            if not (low <= value <= high):
                raise RjpegParameterError(f"{name} {value:g} outside the SDK range {low:g}..{high:g} for {self.variant}")

    def celsius(self, params: Optional[MeasurementParams] = None) -> np.ndarray:
        """
        Convert the file to a Celsius image.

        Args:
            params (MeasurementParams, optional): Complete settings for an API call, or None for the stored settings.

        Returns:
            np.ndarray: float32 temperatures in Celsius, shaped (rows, cols).
        """
        if params is not None:
            self.check(params)
        t = self.convert(self.stored() if params is None else params, api=params is not None)
        return np.asarray(t, np.float32).reshape(self.shape)     # float32, as dirp_measure_ex returns


# --------------------------------------------------------------------------------------------- iirp

class IirpConverter(_RjpegConverter):
    """
    InfiRay-core plugin.

    Raw: APP3 >> 2 is kelvin x 16. Transmittance: a Q14 tau(T, d) table in APP5 (rows -25 + 25 r C) looked up twice (at
    the raw temperature, then at the pass-1 result), times a humidity factor; then T^4 mixing of the atmosphere (weight
    transmittance) at the ambient and the surface (weight emissivity) at the reflected temperature. The 0.1/0.2 containers
    use one temperature for both (the API's reflected value, or the stored ambient), so their two mixings act as one with
    weight emissivity x transmittance; the H30T's emissivity is per pixel, from band radiance. Outputs stop at -20 C, as
    in SDK v1.9.
    """
    family = 'iirp'
    ranges = {'distance': (1, 25), 'humidity': (1, 100), 'emissivity': (0.1, 1.0), 'reflection': (-40, 100), 'ambient': (-40, 80)}
    MAGIC = bytes.fromhex('ffd2d1ff') + b'iirp'
    # what each container version was validated on: EXIF camera models, and the image (rows, cols)
    VALIDATED: Dict[str, Tuple[Tuple[str, ...], Tuple[int, int]]] = {
        '0.1.0': (('MAVIC2-ENTERPRISE-ADVANCED',), (512, 640)), '0.2.0': (('M3T', 'M30T', 'M3TD'), (512, 640)),
        '0.2.1': (('ZH20N',), (512, 640)), '0.3.0': (('H30T',), (1024, 1280))}
    VERSIONS_021 = (8, 65, 66)                           # the 0.2.1 table versions seen in real files
    H30T_HEADER = (1, 281, 65535, 65535, 1, 3, 0, 1, 0, 0, 1, 1)     # APP5 words 0-11 (the M4T's has version 300)
    H30T_TR_REF = 25.0     # the H30T's emissivity reference (C): InfiRay's default reflected temperature, stored in every file
    E0 = 14.24959          # vapour-pressure reference, hPa: about e_s(25 C) at 45 % RH
    FLOOR = -20.0          # the SDK's lowest output, C
    # InfiRay's distance grid, in 1-2-5 steps between these edges: 64-column tables use the first 64 points (0.25-50 m),
    # 88-column ones all 83 (to 500 m; their last 5 columns are never read)
    DIST_EDGES = (0.25, 1.2, 2, 4, 8, 14, 30, 50, 100, 300, 500)
    DIST_STEPS = (0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50)
    GRID88 = np.r_[np.concatenate([a + s * np.arange(round((b - a) / s)) for a, b, s in zip(DIST_EDGES, DIST_EDGES[1:], DIST_STEPS)]),
                   DIST_EDGES[-1]]
    GRID64 = GRID88[:64]
    # humidity sensitivity G(T) = c0 + L (a1 + L (a2 + a3 L)), L = ln(1 + max(T, 0) / K0), held below 0 C (c0 straddles the SDK's step there)
    G_COEF = (1.329765e-4, -0.2666994, 0.3924915, -0.2020751)
    # 8-14 um band radiance as Planck's law at an effective wavelength A + B / T (Sakuma-Hattori; Saunders & White 2003)
    C2 = 14387.769                     # second radiation constant, um K
    SH_A, SH_B = 11.0 * (1 - 6 * 3.0 / 11.0 ** 2), C2 * 3.0 / (2 * 11.0 ** 2)     # A (um), B (um K): band mean 11 um, variance 6^2/12
    # The SDK's default table (M2EA files without one): class A rows (up to 50 C) tabulated in Q14 on GRID64, flat beyond 4.5 m
    # (their irregularities decide the cold-code refusals); class B rows (from 150 C) a quintic in ln(min(d, 5 m)), 12789 at 5 m.
    M2EA_A = (16384, 16224, 16069, 15923, 15792, 15679, 15590, 15520, 15466, 15422, 15385, 15350, 15316, 15281, 15244, 15204,
              15160, 15112, 15062, 15010, 14908, 14816, 14746, 14703, 14677, 14648, 14601, 14516, 14247, 14079, 13958, 13898,
              13943, 13831, 13724, 13676, 13638, 13599, 13517)
    M2EA_B = (33.38386374104661, -65.76368913466096, -151.98549093767213, 161.9765490002136, -995.601481271199, 14686.15282630499)

    def __init__(self, rjpeg: RjpegFile, variant: str, tau_offset: Optional[int], floats_offset: int, tau_shape: Tuple[int, int]) -> None:
        """
        Initialize the converter for one iirp container version.

        Args:
            rjpeg (RjpegFile): The parsed R-JPEG.
            variant (str): The container version, e.g. '0.2.1-v8'.
            tau_offset (int or None): APP5 word offset of the transmittance table, or None for the SDK's default table.
            floats_offset (int): APP4 byte offset of the stored settings.
            tau_shape (tuple[int, int]): The table's (rows, cols).
        """
        super().__init__(rjpeg)
        self.variant, self.tau_offset, self.floats_offset, self.tau_shape = variant, tau_offset, floats_offset, tau_shape
        self.models, self.shape = self.VALIDATED[variant[:5]]
        if tau_shape[1] == 88 and tau_offset is not None:    # 88-column file tables accept up to 300 m
            self.ranges = dict(self.ranges, distance=(1, 300))
        self.accepted = dict(self.ranges, emissivity=(0.01, 1.0))    # the SDK accepts emissivity down to 0.01, below the reported 0.1
        if variant != '0.3.0':                               # the 0.1/0.2 containers do not check the API ambient
            del self.accepted['ambient']

    @classmethod
    def detect(cls, rjpeg: RjpegFile) -> Optional['IirpConverter']:
        """
        Return the converter for an InfiRay file.

        Raises:
            RjpegUnsupportedError: If the container version was not validated.
        """
        app4, words = rjpeg.app(APP4), rjpeg.u16(APP5)    # words: APP5 as uint16 words, a header and then the table
        app5_size = len(rjpeg.app(APP5))
        if len(app4) == 256 and app4[:8] == cls.MAGIC and app5_size in (23818, 24586):     # 0.2.x; words[1], the table version, sets the layout
            version = int(words[1])
            known = version in cls.VERSIONS_021 if app5_size == 24586 else version < 64
            if not known or np.any(words[2:128] != 0xFFFF):  # an unseen version, or the header's 0xFFFF padding broken
                raise RjpegUnsupportedError(f"iirp 0.2 with APP5 table version {version} (padding intact: {bool(np.all(words[2:128] == 0xFFFF))}): "
                                            f"only 0.2.0 below 64 and 0.2.1 {cls.VERSIONS_021} were validated")
            return cls(rjpeg, '0.2.0' if app5_size == 23818 else f'0.2.1-v{version}', tau_offset=128, floats_offset=32,
                       tau_shape=(42, 88) if version >= 64 else (56, 64))
        if len(app4) == 1280 and app4[:8] == cls.MAGIC and app5_size == 8176:     # 0.3.0: the H30T
            if tuple(int(v) for v in words[:12]) == cls.H30T_HEADER and np.all(words[12:128] == 0xFFFF):
                return cls(rjpeg, '0.3.0', tau_offset=128, floats_offset=32, tau_shape=(45, 88))
            raise RjpegUnsupportedError(f"iirp 0.3.0 with header {words[:12].tolist()}: only {cls.H30T_HEADER} with 0xFFFF padding was validated")
        if len(app4) == 224 and app4[:4] != cls.MAGIC[:4] and app5_size == 23818:     # 0.1.0: the M2EA, whose APP4 has no magic
            if np.all(words[:4] == 0xFFFF):                                     # four 0xFFFF words: no table, use the SDK's
                return cls(rjpeg, '0.1.0-fallback', tau_offset=None, floats_offset=0, tau_shape=(56, 88))
            return cls(rjpeg, '0.1.0', tau_offset=0, floats_offset=0, tau_shape=(56, 64))
        return None

    def stored(self) -> MeasurementParams:
        """Return the settings the file holds: five APP4 floats, RH as a fraction."""
        ambient, distance, emissivity, humidity, reflection = struct.unpack_from('<5f', self.rjpeg.app(APP4), self.floats_offset)    # five float32s
        return MeasurementParams(float(distance), float(np.float32(humidity) * np.float32(100)), float(emissivity), float(reflection),
                                 float(ambient))

    def tau_table(self) -> np.ndarray:
        """
        Return the Q14 transmittance table: the file's, or the SDK's default for an M2EA file without one.

        Returns:
            np.ndarray: The table as float64, 16384 = 1.
        """
        if self.tau_offset is None:
            # the SDK reads its 77 rows of 64 distances as 56 rows of 88 (the middle class at 100 C and the SDK's rounding to
            # whole counts are not modelled)
            a = np.r_[self.M2EA_A, np.full(64 - len(self.M2EA_A), self.M2EA_A[-1])]             # class A, flat to 64 distances
            b = np.polyval(self.M2EA_B, np.log(np.minimum(self.GRID64, 5.0)))                  # class B
            w = np.clip((-25.0 + 25.0 * np.arange(77)[:, None] - 50.0) / 100.0, 0.0, 1.0)      # row r (-25 + 25 r C): A to 50 C, B from 150 C
            return (a + w * (b - a)).reshape(56, 88)
        rows, cols = self.tau_shape
        return self.rjpeg.u16(APP5)[self.tau_offset:self.tau_offset + rows * cols].reshape(rows, cols).astype(np.float64)   # 16384 = 1

    @staticmethod
    def _q14(x: np.ndarray) -> np.ndarray:
        """
        Cast a Q14 lookup as the SDK does: x + 0.5 truncated to uint16 and wrapped.

        Args:
            x (np.ndarray): Q14 transmittances.

        Returns:
            np.ndarray: The cast values.

        Raises:
            RjpegUndefinedOutputError: If any value casts to zero, where the SDK fails (rc -32).
        """
        v = np.trunc(x + 0.5) % 65536            # an extrapolated negative lookup wraps to a large value, as the cast does
        if not np.all(v):
            raise RjpegUndefinedOutputError('a pixel transmittance casts to 0 (the SDK fails dirp_measure_ex with rc -32)')
        return v

    def tau_lookup(self, table: np.ndarray, temp: np.ndarray, d: float) -> np.ndarray:
        """
        Look up the table bilinearly in temperature rows and the distance grid.

        Linear below the first row and the first distance, clamped at the last row and the last distance.

        Args:
            table (np.ndarray): The Q14 transmittance table.
            temp (np.ndarray): Temperatures in Celsius.
            d (float): Distance in meters.

        Returns:
            np.ndarray: The Q14 transmittance at each temperature.
        """
        grid = self.GRID64 if table.shape[1] == 64 else self.GRID88
        k = int(np.clip(np.searchsorted(grid, d, side='right') - 1, 0, len(grid) - 2))     # the grid interval holding d
        col = table[:, k] + min(d - grid[k], grid[k + 1] - grid[k]) / (grid[k + 1] - grid[k]) * (table[:, k + 1] - table[:, k])   # each row at d
        x = (temp + 25.0) / 25.0                         # each pixel's fractional row (rows are -25 + 25 r C)
        r = np.clip(np.trunc(x).astype(int), 0, table.shape[0] - 2)     # the row below it, kept inside the table
        w = np.minimum(x - r, 1.0)                       # weight of the row above: negative below row 0, at most 1 at the top
        return col[r] + w * (col[r + 1] - col[r])

    def eps_eff(self, eps: float, t0: np.ndarray) -> np.ndarray:
        """
        Return the H30T's per-pixel emissivity that makes T^4 mixing reproduce band-radiance mixing against its 25 C reference.

        Args:
            eps (float): The emissivity setting.
            t0 (np.ndarray): Raw temperatures in Celsius.

        Returns:
            np.ndarray: The effective emissivity of each pixel.
        """
        e = max(eps, 0.78)                               # below 0.78 the SDK scales the 0.78 value by eps / 0.78 (last line)
        tk, tr = np.asarray(t0, np.float64) + K0, self.H30T_TR_REF + K0     # kelvin; t0 is a whole 1/16 K, never tr itself (0/0)
        with np.errstate(invalid='ignore', divide='ignore'):
            c2, a, b = self.C2, self.SH_A, self.SH_B
            lk, lr = (1.0 / np.expm1(c2 / (a * t + b)) for t in (tk, tr))     # band radiances
            tb = (c2 / np.log1p(1.0 / np.maximum((lk - (1 - e) * lr) / e, 1e-30)) - b) / a    # the inverse, closed form
            out = (tk ** 4 - tr ** 4) / (tb ** 4 - tr ** 4)
        return out * min(1.0, eps / 0.78)

    def convert(self, params: MeasurementParams, api: bool) -> np.ndarray:
        """
        Convert the raw image: two table passes and the humidity factor give the transmittance, then T^4 mixing of atmosphere and surface.

        Raises:
            RjpegUnsupportedError: If the M2EA table mode or the distance has no model.
            RjpegParameterError: If stored settings are outside the SDK's limits.
            RjpegUndefinedOutputError: If the SDK's own output is not a temperature.
        """
        if self.variant.startswith('0.1.0'):
            mode = self.rjpeg.app(APP4)[96]             # APP4 byte 96 selects the built-in table; 3 fails (rc -64)
            if mode == 3 or (self.tau_offset is None and mode != 1):
                raise RjpegUnsupportedError(f"M2EA APP4 byte 96 = {mode}: only built-in table 1 is modelled (3 fails in the SDK)")
        if not api and not (-K0 <= params.ambient <= 100 and -K0 <= params.reflection <= 100 and 1e-4 <= params.emissivity <= 1     # the SDK's
                            and 0 <= params.humidity <= 100):                                                                # own limits
            raise RjpegParameterError('stored settings outside the SDK limits (dirp_measure_ex fails, rc -3; rc -32 for an emissivity below 1e-4)')
        if self.tau_shape[1] == 88 and self.variant != '0.3.0' and params.distance > self.GRID88[-1]:
            raise RjpegUnsupportedError(f"distance {params.distance:.0f} m beyond the 88-column grid (500 m): the SDK does not clamp there")
        t0 = (self.rjpeg.u16(APP3) >> 2) / 16.0 - K0      # raw: kelvin x 16 above two low bits the SDK ignores
        table = self.tau_table()
        eps = float(np.float32(params.emissivity))        # as the float32 the SDK receives
        d = float(params.distance)
        e: Union[np.ndarray, float]        # the surface's weight: per pixel on the H30T
        if self.variant == '0.3.0':        # atmosphere at the ambient, surface at the reflected, band-radiance eps
            ta, tr, e = params.ambient, params.reflection, self.eps_eff(eps, t0)
            path, vp_max = 0.3042903 * np.log(min(max(d, 1.0), 9.814835)), 39.01712     # humidity path 1-9.8 m, vapour clamp
        else:                              # the same with one temperature; the API passes the reflected as ambient
            ta = tr = params.reflection if api else params.ambient
            e, path, vp_max = eps, np.log(max(d, 1.0)), 30.00583         # no humidity effect inside 1 m

        def mix(tau: np.ndarray) -> np.ndarray:
            """T^4 mixing: the atmosphere (weight tau) at ta, then the surface (weight e) at tr."""
            return _t4_mix(_t4_mix(t0, tau / 16384.0, ta), e, tr)
        t1 = mix(self._q14(self.tau_lookup(table, t0, d)))         # pass 1 at the raw temperature
        tau = self._q14(self.tau_lookup(table, t1, d))             # pass 2 at the pass-1 temperature
        if self.tau_offset is not None:    # times the humidity factor exp(G(T1) path ln(vp / E0)) (the fallback path has none)
            with np.errstate(over='ignore', divide='ignore'):     # e_s (Bolton 1980, hPa) is inf below its pole, as in the SDK
                vp = np.clip(params.humidity / 100.0 * (6.112 * np.exp(17.67 * ta / (ta + 243.5))), 7.997714, vp_max)
            c0, a1, a2, a3 = self.G_COEF
            L = np.log1p(np.maximum(t1, 0.0) / K0)        # ln(T_K / 273.15), held at 0 below 0 C
            # the SDK truncates this corrected transmittance; here it stays a float
            tau = tau * np.exp((c0 + L * (a1 + L * (a2 + L * a3))) * path * np.log(vp / self.E0))
        t = mix(tau)
        if np.all(t <= -K0):
            raise RjpegUndefinedOutputError('no pixel keeps a valid temperature (the SDK fails dirp_measure_ex with rc -65)')
        return np.maximum(t, self.FLOOR)


# --------------------------------------------------------------------------------------------- girp

class GirpConverter(_RjpegConverter):
    """
    Guide-core plugin.

    Raw counts -> curve index by an affine map whose gain and offset come from APP4 and from distance and humidity; one
    built-in curve (a quadratic spline); then T^4 mixing with emissivity + 0.01.
    """
    family, variant = 'girp', 'M30T'
    ranges = {'distance': (1, 25), 'humidity': (20, 100), 'emissivity': (0.1, 1.0), 'reflection': (-40, 500)}
    models = ('M30T',)
    MAGIC = bytes.fromhex('ffd2d1ff') + b'girp'
    # The SDK's one built-in curve (it ignores APP5 and the curve version byte 266) as a continuous quadratic spline in the
    # index: a + b idx + c idx^2, plus db u + dc u^2 with u = max(idx - e, 0) at each knot e (where the curve reaches 47, 87
    # and 130 C).
    CURVE = (-132.2026, 0.05457412, -3.501010e-06)
    KNOTS = ((4710.190, 0.0005467299, 1.949158e-06), (6847.825, -0.0007119645, 1.141166e-06), (10036.97, 0.001440627, -8.802024e-07))
    HOLD = (-30.0, 160.0)                                # the SDK holds the curve inside this range, C

    @classmethod
    def detect(cls, rjpeg: RjpegFile) -> Optional['GirpConverter']:
        """
        Return the converter for a Guide-core file.

        Raises:
            RjpegUnsupportedError: If the file is in low-gain mode.
        """
        app4 = rjpeg.app(APP4)
        if app4[:8] == cls.MAGIC and len(app4) == 316 and app4[32:36] == bytes.fromhex('aa553800') and len(rjpeg.app(APP5)) == 32768:
            if app4[68] or app4[69]:
                raise RjpegUnsupportedError('girp low-gain mode (byte 68 set; up to 530 C on a built-in curve) not modelled')
            return cls(rjpeg)
        return None

    def word(self, offset: int, fmt: str = '<h') -> int:
        """Return an APP4 field, int16 unless fmt says otherwise."""
        return self.rjpeg.field(APP4, offset, fmt)

    def stored(self) -> MeasurementParams:
        """Return the settings the file holds, as APP4 words."""
        return MeasurementParams(self.word(38) / 10.0, float(self.word(36)), self.word(40) / 100.0, self.word(42) / 10.0, 0.0)

    def index(self, raw: np.ndarray, dist: float, rh: float) -> np.ndarray:
        """Map raw counts to the curve index by the file's affine map, at distance dist (m) and relative humidity rh (%)."""
        # In floats and unclipped: the SDK's integer arithmetic sits a few indices lower, and its int16 clip acts like the
        # curve's -30 C hold.
        x = dist - 5.169099                              # distance from the reference
        c272, c276, c282, c286 = (self.word(o, '<i') for o in (272, 276, 282, 286))     # quadratic (1e-2) and linear (1e-3) distance terms
        gain = (self.word(280) + c276 * x / 1000 + c272 * x * x / 100) * (1 + (63.842 - rh) / 5021.56) / 1000.0   # per mille, at d and RH
        return (gain * (raw * self.word(292) / 8192.0 + self.word(294, '<i')) + self.word(290) + self.word(298)
                + c286 * x / 1000 + c282 * x * x / 100)  # gain x (scaled raw + offset), plus intercepts that move with distance

    def convert(self, params: MeasurementParams, api: bool) -> np.ndarray:
        """Convert the raw image: the curve index, the built-in curve and its offset, then T^4 mixing with emissivity + 0.01."""
        dist, rh, eps, tr = params.distance, params.humidity, params.emissivity, params.reflection
        if api:             # the API truncates distance and humidity to whole units, eps to 0.01 and reflected to 0.1 (float32)
            dist, rh, eps, tr = float(int(dist)), float(int(rh)), _trunc_f32(eps, 0.01), _trunc_f32(tr, 0.1)
        idx = self.index(self.rjpeg.u16(APP3).astype(np.float64), dist, rh)
        a, b, c = self.CURVE
        t = a + b * idx + c * idx * idx                  # the spline's first piece
        for e, db, dc in self.KNOTS:
            u = np.maximum(idx - e, 0)                   # 0 below the knot
            t = t + db * u + dc * u * u
        t = np.clip(t, *self.HOLD) + self.word(54) / 10.0   # the SDK's holds, then the file's offset (0.1 C)
        tr = 23.0 if 21.0 <= tr < 25.1 else tr       # the SDK reads 21.0-25.0 C (after its 0.1 C truncation) as 23 C
        # emissivity + 0.01, and 0.0 where nothing is left (the SDK also floors emissivity at 0.5; not modelled, as it acts only below 0.5)
        return _t4_mix(t, min(eps + 0.01, 1.0), tr, 0.0)


# --------------------------------------------------------------------------------------------- hirp

class HirpConverter(_RjpegConverter):
    """
    HIKMICRO-core plugin, analytic approximation.

    A calibration curve with a cavity-temperature correction, then the environment. The low-gain cavity stage rounds an
    offset to whole raw codes per 0.01 C of cavity; the smooth surface here cannot follow that, which leaves about 2.5 % of
    codes beyond 0.5 C, and up to about 4.1 C in sub-bands near 13.4-13.9 and 41.0-42.4 C.
    """
    family = 'hirp'
    ranges = {'distance': (0, 1000), 'humidity': (0, 100), 'emissivity': (0.1, 1.0), 'reflection': (-40, 1000), 'ambient': (-100, 100)}
    # what the SDK accepts (set rc -3 outside): humidity strictly inside -0.5...100.5 (bounds: the float32 values next inside),
    # and ambient from -273 C in low gain and about -100.5 C in high gain (it varies by file; -100 here). It accepts any
    # distance, emissivity and reflected, but its output saturates at a negative distance, an emissivity above 1 or a
    # reflected below -273.15 C, so those stay refused; distance stops at 200 m, the range fitted for SAR flights.
    accepted = {'distance': (0, 200), 'humidity': (-0.4999999701976776, 100.49999237060547), 'emissivity': (-np.inf, 1.0),
                'reflection': (-273.15, np.inf), 'ambient': (-273, 100)}
    MIN_EMISSIVITY = 78 / 8192                           # the SDK computes a lower emissivity as this one
    models = ('M3TD',)                                   # not the M4T, whose HIKMICRO files share the container
    MAGIC = bytes.fromhex('ffd2d1ff') + b'hirp'
    # APP4 fields: (offset, struct format); _q13 values are x 8192, _m values x 1000, the cavity in 0.01 C
    FIELDS = {'transmittance_q13': (80, '<I'), 'emissivity_q13': (88, '<I'), 'distance_q13': (92, '<I'), 'reflect_q13': (96, '<i'),
              'reflect_enabled': (100, '<B'), 'word108': (108, '<H'), 'ambient_m': (112, '<i'), 'humidity_m': (116, '<i'),
              'cavity': (120, '<H'), 'word122': (122, '<H'), 'fpga_gain': (124, '<H')}
    # high gain: a normalised index u = g (raw - s T_a + k t - C) + cubic(t), t the cavity in C, on the calibration curve
    # u = exp(-B / T) (Wien's form of Planck's law)
    # the SDK refuses a hotter cavity for passed settings (set rc -3) and computes at stored ones, where nothing was fitted
    # (cores 0-55 C), so both refuse here; low gain has no limit
    HIGH_CAVITY_MAX = 62.42
    HIGH_WIEN_B = 1493.883
    HIGH_GAIN_POLY = (-34.87741, -5439.459, 479390.1)                  # 1 / g, a quadratic in the cavity class
    HIGH_GAIN_BANDS = ((673, 930, -0.003471538), (1917, 2174, -0.004034))     # g x (1 + factor) for cavity words in [lo, hi)
    HIGH_AMBIENT = (7.998436, 16.22401)                                # s, raw codes per C of ambient; k, per C of cavity
    HIGH_OFFSET = (5515.732, -1.805017e-09, 2.317106e-06, 0.0001698376, 0.004212759)     # C, then the cubic in t
    HIGH_BIAS = -0.16552                                               # output bias: the SDK's re-quantisation
    HIGH_CLAMP = (-30.0, 165.0)                                        # the SDK's output range, C
    # the mixing weight against distance, piecewise linear to 200 m and flat beyond (the 140-200 m values fitted after the rest)
    HIGH_TAU_NODES = (0.0, 0.7590888, 2.440362, 3.312713, 4.232165, 5.168957, 7.399548, 8.249933, 12.47200, 20.89037, 37.63026,
                      87.90961, 120.0, 140.0, 160.0, 180.0, 200.0)
    HIGH_TAU_VALUES = (1.198568, 1.184067, 1.121947, 1.083186, 1.024041, 0.9868083, 0.9300337, 0.9190884, 0.8653592, 0.8103866,
                       0.7444172, 0.6430447, 0.6136326, 0.5949570, 0.5759995, 0.5613082, 0.5535556)
    # ln(w / tau(d)) = H2O (h0 - h1 d), H2O FLIR's water content (its values track water-vapour density, g/m^3): h0, h1
    HIGH_HUMIDITY = (6.614682e-05, 1.549309e-05)
    # low gain: first stage raw -> T1 on Planck's curve, then T^4 mixing, then a linear distance stretch in C
    LOW_CURVE_B = 1534.714         # the first stage's curve g = 1 / (exp(B / T) - 1), Planck's law at c2 / B = 9.37 um
    # g = quadratic in x = (raw' - 4000) / 4000 (x^2 first), each coefficient a cubic in t = (cavity - 30) / 30 (t^3 first)
    LOW_SURFACE = ((-0.005126043, -0.01080466, -0.005947140, -0.006582543),
                   (-0.003290972, -0.002394947, 0.02111628, 0.07932995),
                   (-0.0008479527, 0.0008060896, 0.01398339, 0.03932289))
    LOW_KNEE = (0.9992344, 5.022066, 37.73306)      # raw' = raw - (a T_a - b cavity + c): a per C of ambient, b per C of cavity; an offset, despite the name
    LOW_WEIGHT = (0.03005648, 1.968622e-06)         # T^4 weight ln w = h0 + h1 T_a (no humidity term)
    # k0 and f = T_ref / T_a, then the quadratic P(d) (highest power first) in k(d) = k0 / min(1, P(d));
    # P < 1 only for about 2.9-26.4 m
    LOW_STRETCH = (0.9613222, 1.100781, 0.001034368, -0.03036000, 1.079499)
    LOW_BIAS = -0.1488369                           # output bias: the SDK's re-quantisation
    LOW_CLAMP = (-30.0, 600.0)                      # the SDK's output range, C

    @classmethod
    def detect(cls, rjpeg: RjpegFile) -> Optional['HirpConverter']:
        """Return the converter for a HIKMICRO file in high or low gain."""
        app4, app5 = rjpeg.app(APP4), rjpeg.app(APP5)
        if app4[:8] == cls.MAGIC and len(app4) == 144 and len(app5) == 16485 and app5[:4] == b'HIDR':     # APP5: the HIDR block
            return cls(rjpeg, 'high-gain' if rjpeg.field(APP4, 124, '<H') == 0 else 'low-gain')
        return None

    def __init__(self, rjpeg: RjpegFile, variant: str) -> None:
        """
        Read the APP4 fields and refuse values outside what was validated.

        Args:
            rjpeg (RjpegFile): The parsed R-JPEG.
            variant (str): 'high-gain' or 'low-gain'.

        Raises:
            RjpegUnsupportedError: If a field is outside what was validated.
        """
        super().__init__(rjpeg)
        self.variant = variant
        if variant == 'high-gain':
            self.accepted = dict(self.accepted, ambient=(-100, 100))
        self.fields: Dict[str, int] = {k: rjpeg.field(APP4, offset, fmt) for k, (offset, fmt) in self.FIELDS.items()}
        if self.fields['fpga_gain'] not in (0, 1):
            raise RjpegUnsupportedError(f"hirp gain selector {self.fields['fpga_gain']}")
        if self.fields['transmittance_q13'] != 8192:
            raise RjpegUnsupportedError(f"hirp optical transmittance {self.fields['transmittance_q13'] / 8192:.4f}: only 1.0 was studied")
        if variant == 'high-gain' and self.fields['cavity'] / 100.0 > self.HIGH_CAVITY_MAX:
            raise RjpegUnsupportedError(f"hirp high-gain cavity above {self.HIGH_CAVITY_MAX:g} C (the SDK refuses it for passed settings; not fitted)")
        if self.fields['word108'] != 198 or self.fields['word122'] != 2:
            raise RjpegUnsupportedError('hirp words 108/122 must be 198/2 (the SDK refuses other 108s and outputs nothing for other 122s)')

    def stored(self) -> MeasurementParams:
        """Return the settings the file holds; the reflected temperature counts only when its flag is exactly 1."""
        f = self.fields
        amb = f['ambient_m'] / 1000.0
        refl = f['reflect_q13'] / 8192.0 if f['reflect_enabled'] == 1 else amb  # for any other value the SDK uses the ambient
        return MeasurementParams(f['distance_q13'] / 8192.0, f['humidity_m'] / 1000.0, f['emissivity_q13'] / 8192.0, refl, amb)

    def convert(self, params: MeasurementParams, api: bool) -> np.ndarray:
        """Convert the raw image in high or low gain."""
        params = replace(params, emissivity=max(params.emissivity, self.MIN_EMISSIVITY))
        raw = self.rjpeg.u16(APP3).astype(np.float64)
        return self._high(raw, params) if self.variant == 'high-gain' else self._low(raw, params)

    def _high(self, raw: np.ndarray, params: MeasurementParams) -> np.ndarray:
        """
        Convert in high gain: an index on Wien's form of the calibration curve, then T^4 mixing of atmosphere and surface.

        Args:
            raw (np.ndarray): Raw codes.
            params (MeasurementParams): The settings to measure at.

        Returns:
            np.ndarray: Temperatures in Celsius.
        """
        d, rh, ta, cav = params.distance, params.humidity, params.ambient, self.fields['cavity']
        t = cav / 100.0                                  # camera-core (cavity) temperature, C
        g = 1.0 / np.polyval(self.HIGH_GAIN_POLY, ((cav - 3) // 10 * 10 + 3) / 100.0)     # index gain, per 0.1 C class from x.x3 C
        for lo, hi, factor in self.HIGH_GAIN_BANDS:      # the SDK's gain is lower over these bands of cavities
            if lo <= cav < hi:
                g *= 1.0 + factor
        s, k = self.HIGH_AMBIENT
        c0, *c = self.HIGH_OFFSET
        u = np.clip(g * (raw - s * ta + k * t - c0) + np.polyval(c, t), 1e-300, 1.0 - 1e-12)     # the index, inside (0, 1)
        h0, h1 = self.HIGH_HUMIDITY
        h2o = rh / 100.0 * np.exp(1.5587 + 0.06939 * ta - 0.00027816 * ta ** 2 + 6.8455e-7 * ta ** 3)     # FLIR's water content, ~g/m^3
        w = np.interp(d, self.HIGH_TAU_NODES, self.HIGH_TAU_VALUES) * np.exp(h2o * (h0 - h1 * d))     # atmosphere weight
        tm = _t4_mix(_t4_mix(-self.HIGH_WIEN_B / np.log(u) - K0, w, ta), params.emissivity, params.reflection)   # u = exp(-B / T) inverted, then mixed
        return np.clip(tm + self.HIGH_BIAS, *self.HIGH_CLAMP)                # nothing left (-K0) reads as the SDK's floor

    def _low(self, raw: np.ndarray, params: MeasurementParams) -> np.ndarray:
        """
        Convert in low gain: a raw x cavity surface on Planck's curve, then T^4 mixing, then a linear distance stretch in Celsius.

        Args:
            raw (np.ndarray): Raw codes.
            params (MeasurementParams): The settings to measure at.

        Returns:
            np.ndarray: Temperatures in Celsius.
        """
        ta, e, d, cav = params.ambient, params.emissivity, params.distance, self.fields['cavity'] / 100.0
        a, b, c = self.LOW_KNEE
        x = (raw - (a * ta - b * cav + c) - 4000.0) / 4000.0                    # the ambient and cavity offset, then normalised
        g = np.polyval([np.polyval(co, (cav - 30) / 30) for co in self.LOW_SURFACE], x)     # the raw^2 x cavity^3 surface
        t1 = self.LOW_CURVE_B / np.log1p(1.0 / np.maximum(g, 1e-30)) - K0       # Planck's curve inverted
        w = float(np.exp(self.LOW_WEIGHT[0] + self.LOW_WEIGHT[1] * ta))
        num = ((t1 + K0) ** 4 - (1 - w) * (ta + K0) ** 4 - w * (1 - e) * (params.reflection + K0) ** 4) / (w * e)   # T1^4 mixing for Y^4
        y = np.where(num > 0, np.abs(num) ** 0.25 - K0, -K0)
        # the distance stretch out = T_ref + k(d) (Y - T_ref), T_ref = f T_a, k(d) = k0 / min(1, P(d)) (so k = k0 outside about 2.9-26.4 m)
        k0, f, *q = self.LOW_STRETCH
        r = f * ta
        return np.clip(r + k0 / min(1.0, float(np.polyval(q, d))) * (y - r) + self.LOW_BIAS, *self.LOW_CLAMP)


# --------------------------------------------------------------------------------------------- dirp

class _DirpConverter(_RjpegConverter):
    """
    DJI's own plugin.

    A camera-specific index into the camera's temperature table (int16, 0.1 C, read from the file), then T^4 emissivity
    mixing at the reflected temperature. Ambient is accepted and unused, and the stored path measures at the SDK's defaults
    whatever the file holds.
    """
    family = 'dirp'
    TABLE: int                     # the marker holding the temperature table
    RAW_MAX = 65535

    def __init__(self, rjpeg: RjpegFile) -> None:
        """
        Read the camera's temperature table and refuse one that decreases anywhere, as the SDK does.

        Args:
            rjpeg (RjpegFile): The parsed R-JPEG.

        Raises:
            RjpegUnsupportedError: If the table decreases anywhere.
        """
        super().__init__(rjpeg)
        self.table = np.frombuffer(rjpeg.app(self.TABLE), '<i2').astype(np.int64)
        if np.any(np.diff(self.table) < 0):
            raise RjpegUnsupportedError(f"{self.variant} temperature table decreases somewhere (the SDK refuses it or crashes)")

    def stored(self) -> MeasurementParams:
        """
        Return the SDK's defaults, which its stored path uses whatever the file holds.

        Returns:
            MeasurementParams: The SDK's default settings.
        """
        return MeasurementParams(5.0, 70.0, 1.0, 23.0, 0.0)

    @abstractmethod
    def index(self, d: float, rh: float, raw: np.ndarray) -> np.ndarray:
        """
        Return the continuous table index of each raw code.

        Args:
            d (float): Distance in meters.
            rh (float): Relative humidity in percent.
            raw (np.ndarray): Raw codes.

        Returns:
            np.ndarray: The table index of each raw code.
        """

    def convert(self, params: MeasurementParams, api: bool) -> np.ndarray:
        """
        Convert the raw image: the API truncations, the table read at the camera's index, the SDK's radiance refusal and T^4 mixing.

        Args:
            params (MeasurementParams): The settings to measure at.
            api (bool): True for settings passed through the API, False for the stored path.

        Returns:
            np.ndarray: Temperatures in Celsius, one per raw code.

        Raises:
            RjpegParameterError: If the reflected radiance exceeds that of the hottest raw code.
        """
        # the API truncates emissivity to 0.01 and reflected to 0.1 in float32, and distance and humidity to integers (below);
        # the stored defaults lie on that grid
        e, tr = _trunc_f32(params.emissivity, 0.01), _trunc_f32(params.reflection, 0.1)
        if self.variant == 'XT S':         # girp's emissivity stage: emissivity + 0.01, reflected 21-25 C read as 23 C
            e, tr = min(e + 0.01, 1.0), (23.0 if 21.0 <= tr <= 25.0 else tr)
        # The table is interpolated at the continuous index, where the SDK floors it (at most one 0.1 C level apart). RAW_MAX
        # rides along as a last pixel: the SDK refuses a reflected radiance above that of its hottest raw code.
        idx = self.index(np.trunc(params.distance), np.trunc(params.humidity),
                         np.append(self.rjpeg.u16(self.RAW), self.RAW_MAX).astype(np.int64))
        t = np.interp(idx, np.arange(len(self.table)), self.table) / 10.0       # the table holds 0.1 C steps
        if (1 - e) * (tr + K0) ** 4 > (t[-1] + K0) ** 4:     # reflected radiance against the hottest code's
            raise RjpegParameterError(f"{self.variant}: reflected radiance above that of the hottest raw code (the SDK refuses)")
        return _t4_mix(t[:-1], e, tr)


class DirpH20TConverter(_DirpConverter):
    """Zenmuse H20T. APP3 raw u16, APP5 the temperature table, APP4 calibration floats and words."""
    variant = 'H20T'
    models = ('ZH20T',)
    ranges = {'distance': (1, 25), 'humidity': (20, 100), 'emissivity': (0.1, 1.0), 'reflection': (-40, 500)}
    RAW, TABLE = APP3, APP5

    @classmethod
    def detect(cls, rjpeg: RjpegFile) -> Optional['DirpH20TConverter']:
        """Return the converter for an H20T file."""
        app4 = rjpeg.app(APP4)
        return cls(rjpeg) if len(app4) == 2560 and app4[:4] == bytes.fromhex('aa551206') and len(rjpeg.app(APP5)) == 32768 else None

    def index(self, d: float, rh: float, raw: np.ndarray) -> np.ndarray:
        """Return the table index: raw against a reference plus internal-temperature drift, divided by a distance and humidity factor."""
        app4 = self.rjpeg.app(APP4)
        f = np.frombuffer(app4, '<f4').astype(np.float64)    # APP4 as float32 fields
        u = np.frombuffer(app4, '<u2')                       # ... and as uint16 words
        c2, c1 = np.frombuffer(app4, '<i4')[19:21]           # distance coefficients, 1e-5 (21 and -945 in every sample)
        t0, y = u[44] / 10.0, 49.9985 - d                # calibration temperature (C); distance from 49.9985 m
        c = np.searchsorted(self.table, np.round(f[41] * 10)) + 0.250033 * (f[15] + (f[42] - f[34]) * (f[10] * (f[42] + f[34] - 2 * t0) + f[11])
                                                                            - f[9] * (f[41] - t0))     # index of t41, plus drift
        g = (1 + (c1 * y + c2 * y * y) / 1e5) * (1 + (rh - 70) / 448.021)   # 1 at 5 m and 70 % RH (to 2e-5)
        return (f[13] / 316.0085 * (raw - u[163]) + c) / g    # gain x (raw - reference) + C, over g

    def convert(self, params: MeasurementParams, api: bool) -> np.ndarray:
        """Convert as dirp does, then apply the file's output gain (APP4 word 42, %) and offset (word 43, int16, 0.1 C)."""
        return super().convert(params, api) * (self.rjpeg.field(APP4, 84, '<H') / 100.0) + self.rjpeg.field(APP4, 86, '<h') / 10.0   # 100 and 0 in every sample


class DirpXtsConverter(_DirpConverter):
    """
    Zenmuse XT S.

    APP3 the temperature table (-45...160 C), the 11 APP4 segments the raw image, APP2 a 1,260 B 'Plug' block of u16
    calibration fields. Distance (5-25 m) is accepted and unused.
    """
    variant = 'XT S'
    models = ('XT S',)
    ranges = {'distance': (5, 25), 'humidity': (20, 100), 'emissivity': (0.1, 1.0), 'reflection': (-40, 500)}
    RAW, TABLE, RAW_MAX = APP4, APP3, 16383          # a 14-bit core (the refusal's hottest code)
    UNMODELLED = (1170, 1196, 1210, 1240, 1242)      # zero in every sample and active when set
    UNMODELLED_API = (1200, 1202, 1204, 1206)        # zero in every sample, read only through the API

    @classmethod
    def detect(cls, rjpeg: RjpegFile) -> Optional['DirpXtsConverter']:
        """Return the converter for an XT S file."""
        app2 = rjpeg.app(APP2)
        return (cls(rjpeg) if app2[:4] == b'Plug' and len(app2) == 1260 and len(rjpeg.app(APP3)) == 32768 and len(rjpeg.app(APP4)) == 655360
                else None)

    def __init__(self, rjpeg: RjpegFile) -> None:
        """
        Refuse set fields that were never modelled, and size words the image contradicts (the SDK fails those, rc -1).

        Args:
            rjpeg (RjpegFile): The parsed R-JPEG.

        Raises:
            RjpegUnsupportedError: If an unmodelled field is set or the size words do not match the image.
        """
        super().__init__(rjpeg)
        if any(self.word(k) for k in self.UNMODELLED):
            raise RjpegUnsupportedError(f"XT S APP2 fields {self.UNMODELLED} must be zero (not modelled)")
        if self.word(1164) * self.word(1168) * 2 > len(rjpeg.app(APP4)):
            raise RjpegUnsupportedError(f"XT S size words {self.word(1164)} x {self.word(1168)} do not match the image")

    def word(self, offset: int, signed: bool = False) -> int:
        """Return an APP2 field, uint16 unless signed."""
        return self.rjpeg.field(APP2, offset, '<h' if signed else '<H')

    def check(self, params: MeasurementParams) -> None:
        """
        Check the SDK's ranges, and refuse API settings while fields read only through the API are set.

        Args:
            params (MeasurementParams): The settings passed through the API.

        Raises:
            RjpegParameterError: If a setting is outside its range.
            RjpegUnsupportedError: If a field read only through the API is set.
        """
        super().check(params)
        if any(self.word(k) for k in self.UNMODELLED_API):
            raise RjpegUnsupportedError(f"XT S APP2 fields {self.UNMODELLED_API} must be zero for API settings (not modelled)")

    def index(self, d: float, rh: float, raw: np.ndarray) -> np.ndarray:
        """Return the table index: raw against a reference and a four-temperature drift, the gain, the FFC index and the humidity slope (d unused)."""
        # In floats, without the SDK's integer truncations, but wrapping to int16 at each step as it does (edited calibration
        # states reach the wraps).
        def w(v: np.ndarray) -> np.ndarray:
            """Wrap to int16."""
            return (v + 32768) % 65536 - 32768
        u = self.word
        t24, t28, t44, t58 = (u(k) / 100 for k in (1224, 1228, 1244, 1258))     # internal temperatures, 0.01 C
        dt = t24 - t44                                   # camera now against at FFC; 35 counts/C more when cooler
        k = u(1254) * (u(1236) - u(1238) * (t58 - t44) / 10) / 10000     # drift slope, counts/C
        drift = u(1188) + u(1190) * (t24 - t28) + 35 * min(dt, 0) - k * dt - (u(1192) * t44 ** 2 + u(1194, True) * t44) / 1000
        y = w(u(1186) * w(raw - u(1234) + u(1214) - drift) / 100 + u(1256) + np.searchsorted(self.table, u(1244) / 10))   # gain, + FFC index
        return w(y * (5049 - rh) / 4994)                 # the humidity slope


# --------------------------------------------------------------------------------------------- entry point

def open_rjpeg(source: Source) -> _RjpegConverter:
    """
    Return the family converter for an R-JPEG.

    Args:
        source (str | os.PathLike | bytes): Path to the R-JPEG image file, or its bytes.

    Returns:
        _RjpegConverter: The converter for the file's container, validated against its camera model and image size.

    Raises:
        RjpegUnsupportedError: For anything not recognised or not validated.
    """
    rjpeg = RjpegFile(source)
    for family in (IirpConverter, GirpConverter, HirpConverter, DirpH20TConverter, DirpXtsConverter):
        converter = family.detect(rjpeg)
        if converter is not None:
            converter.validate()                         # the camera model and image size it was validated on
            return converter
    app4 = rjpeg.app(APP4)
    raise RjpegUnsupportedError(f"no supported R-JPEG container (APP2 {len(rjpeg.app(APP2))} B, APP3 {len(rjpeg.app(APP3))} B, "
                                f"APP4 {len(app4)} B {app4[:8].hex()}, APP5 {len(rjpeg.app(APP5))} B)")


class PythonDjiThermalParserService:
    """Parser service for DJI thermal images that converts in Python, without the DJI Thermal SDK."""

    def __init__(self, dtype=np.float32):
        """
        Initialize the PythonDjiThermalParserService with the specified data type.

        Args:
            dtype (type, optional): Data type for temperature arrays. Defaults to np.float32.
        """
        self.logger = LoggerService()
        self._dtype = dtype

    def temperatures(self, filepath_image: str, image_height: int = 512, image_width: int = 640,
                     object_distance: float = 5.0, relative_humidity: float = 70.0,
                     emissivity: float = 1.0, reflected_apparent_temperature: float = 23.0,
                     m2ea_mode: bool = False):
        """
        Parse thermal image data to extract temperature values.

        Args:
            filepath_image (str): Path to the R-JPEG image file.
            image_height (int): Unused; the image size is read from the file.
            image_width (int): Unused; the image size is read from the file.
            object_distance (float): Distance to target in meters.
            relative_humidity (float): Relative humidity in percent.
            emissivity (float): Emissivity of the target surface (0.10-1.00).
            reflected_apparent_temperature (float): Reflected temperature in Celsius.
            m2ea_mode (bool): Measure at the settings stored in the file, ignoring the four settings above.

        Returns:
            np.ndarray: 2D float32 array of temperature values.

        Raises:
            ValueError: If dtype is not np.float32.
            RjpegUnsupportedError: If the file is not one the converter was validated on.
            RjpegParameterError: If the DJI Thermal SDK would refuse the settings.
            RjpegUndefinedOutputError: If the DJI Thermal SDK's output would not be a temperature.
        """
        if self._dtype != np.float32:
            raise ValueError("Unsupported data type for temperature extraction.")
        try:
            converter = open_rjpeg(filepath_image)
            if m2ea_mode:
                return converter.celsius(None)
            return converter.celsius(replace(converter.stored(), distance=float(object_distance), humidity=float(relative_humidity),
                                             emissivity=float(emissivity), reflection=float(reflected_apparent_temperature)))
        except (RjpegUnsupportedError, RjpegParameterError, RjpegUndefinedOutputError) as e:
            self.logger.warning(f"{filepath_image}: {e}")
            raise

    def image(self, filepath_image: str, palette: str):
        """
        Return the thermal picture the camera embedded in the R-JPEG.

        No caller uses this picture; ThermalParserService.parse_file asks every parser for one. The camera rendered it in
        its own palette, so palette is ignored.

        Args:
            filepath_image (str): Path to the R-JPEG image file.
            palette (str): Unused.

        Returns:
            np.ndarray: The embedded picture as a BGR image.
        """
        return cv2.imread(filepath_image)
