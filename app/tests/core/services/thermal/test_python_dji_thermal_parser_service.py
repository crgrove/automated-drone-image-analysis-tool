"""
Tests for PythonDjiThermalParserService and for thermal parser selection in ThermalParserService.

None of these read sample data, so they run in CI on every OS.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from core.services.thermal.ThermalParserService import ThermalParserService
from core.services.thermal.thermalParserServices.PythonDjiThermalParserService import (
    DirpH20TConverter, GirpConverter, HirpConverter, IirpConverter, MeasurementParams, PythonDjiThermalParserService, RjpegParameterError,
    RjpegUndefinedOutputError, RjpegUnsupportedError, _DirpConverter)

PARSER_SERVICE = 'core.services.thermal.ThermalParserService'
PYTHON_PARSER = 'core.services.thermal.thermalParserServices.PythonDjiThermalParserService'
M3T_METADATA = {'EXIF:Make': 'DJI', 'EXIF:Model': 'M3T', 'APP3:ThermalData': '(Binary data 655360 bytes)'}
AUTEL_METADATA = {'EXIF:Make': 'Autel Robotics', 'EXIF:Model': 'XL726', 'File:ImageWidth': 640, 'File:ImageHeight': 512}


def _parse_m3t_file_on(system, machine, python_error=None):
    """
    Run parse_file on an M3T file as if on `system` and `machine` (sys.platform and platform.machine() values), with both
    DJI parsers mocked and the Python one raising `python_error`, if given; return the two mocks.
    """
    service = ThermalParserService(dtype=np.float32)
    with patch(f'{PARSER_SERVICE}.MetaDataHelper.get_meta_data_exiftool', return_value=M3T_METADATA), \
            patch(f'{PARSER_SERVICE}.sys.platform', system), \
            patch(f'{PARSER_SERVICE}.platform.machine', return_value=machine), \
            patch(f'{PARSER_SERVICE}.DjiThermalParserService') as MockSdk, \
            patch(f'{PARSER_SERVICE}.PythonDjiThermalParserService') as MockPython:
        MockPython.return_value.temperatures.side_effect = python_error
        service.parse_file('dji.jpg')
    return MockSdk, MockPython


def _parse_autel_file_on(system):
    """
    Run parse_file on an Autel file as if on `system` (a sys.platform value), with the Autel parser mocked; return the
    mock and the exception parse_file raised, or None.
    """
    service = ThermalParserService(dtype=np.float32)
    with patch(f'{PARSER_SERVICE}.MetaDataHelper.get_meta_data_exiftool', return_value=AUTEL_METADATA), \
            patch(f'{PARSER_SERVICE}.sys.platform', system), \
            patch(f'{PARSER_SERVICE}.AutelThermalImageParser') as MockAutel:
        try:
            service.parse_file('autel.jpg')
        except Exception as e:
            return MockAutel, e
    return MockAutel, None


@pytest.fixture
def open_rjpeg():
    """Patch open_rjpeg to return a converter whose file stores 5 m, 50 %, 0.95, 23 C reflected and 21.5 C ambient."""
    with patch(f'{PYTHON_PARSER}.open_rjpeg') as mock:
        mock.return_value.stored.return_value = MeasurementParams(5.0, 50.0, 0.95, 23.0, 21.5)
        yield mock


@pytest.mark.parametrize('system, machine', [('darwin', 'arm64'), ('darwin', 'x86_64'), ('linux', 'aarch64'), ('linux', 'armv7l')])
def test_parse_file_uses_python_parser_on_macos_and_non_x86_linux(system, machine):
    MockSdk, MockPython = _parse_m3t_file_on(system, machine)

    MockSdk.assert_not_called()
    MockPython.assert_called_once_with(np.float32)
    MockPython.return_value.temperatures.assert_called_once_with(filepath_image='dji.jpg', m2ea_mode=True)
    MockPython.return_value.image.assert_called_once_with('dji.jpg', 'White Hot')


# Windows ignores the processor: its routing is unchanged, whatever platform.machine() reports.
@pytest.mark.parametrize('system, machine', [('win32', 'AMD64'), ('win32', 'ARM64'), ('linux', 'x86_64'), ('linux', 'i686')])
def test_parse_file_uses_sdk_parser_on_windows_and_x86_linux(system, machine):
    MockSdk, MockPython = _parse_m3t_file_on(system, machine)

    MockPython.assert_not_called()
    MockSdk.assert_called_once_with(np.float32)
    MockSdk.return_value.temperatures.assert_called_once_with(filepath_image='dji.jpg', m2ea_mode=True)


def test_parse_file_names_the_camera_the_python_parser_does_not_support():
    error = RjpegUnsupportedError('hirp high-gain container from DJI M4T: validated only on DJI M3TD')
    with pytest.raises(Exception, match='^M3T thermal images are not supported on this computer$'):
        _parse_m3t_file_on('darwin', 'arm64', python_error=error)


@pytest.mark.parametrize('error', [RjpegParameterError('distance 30 outside the SDK range 1..25 for M30T'), ValueError('corrupt')])
def test_parse_file_keeps_invalid_image_file_for_other_python_parser_errors(error):
    with pytest.raises(Exception, match='^Invalid image file$'):
        _parse_m3t_file_on('darwin', 'arm64', python_error=error)


@pytest.mark.parametrize('system', ['linux', 'darwin'])
def test_parse_file_refuses_autel_off_windows(system):
    MockAutel, error = _parse_autel_file_on(system)

    MockAutel.assert_not_called()
    assert isinstance(error, AssertionError)
    assert str(error) == 'Autel thermal images can only be processed on Windows'


def test_parse_file_uses_autel_parser_on_windows():
    MockAutel, error = _parse_autel_file_on('win32')

    assert error is None
    MockAutel.assert_called_once_with(np.float32)
    MockAutel.return_value.temperatures.assert_called_once_with(filepath_image='autel.jpg', image_height=512, image_width=640)


def test_temperatures_uses_stored_settings_in_m2ea_mode(open_rjpeg):
    temperature = PythonDjiThermalParserService().temperatures('dji.jpg', m2ea_mode=True)

    open_rjpeg.assert_called_once_with('dji.jpg')
    open_rjpeg.return_value.celsius.assert_called_once_with(None)
    assert temperature is open_rjpeg.return_value.celsius.return_value


def test_temperatures_overrides_four_settings_outside_m2ea_mode(open_rjpeg):
    PythonDjiThermalParserService().temperatures('dji.jpg', object_distance=10, relative_humidity=60, emissivity=0.9,
                                                 reflected_apparent_temperature=30)

    # Ambient is not one of the four: it keeps the stored 21.5 C, as the SDK's get-then-set does.
    open_rjpeg.return_value.celsius.assert_called_once_with(MeasurementParams(10.0, 60.0, 0.9, 30.0, 21.5))


def test_temperatures_refuses_dtype_other_than_float32(open_rjpeg):
    with pytest.raises(ValueError, match='Unsupported data type'):
        PythonDjiThermalParserService(np.float64).temperatures('dji.jpg', m2ea_mode=True)

    open_rjpeg.assert_not_called()


# An unsupported file is refused when opened; the other two refusals come from the conversion.
@pytest.mark.parametrize('error, from_celsius', [
    pytest.param(RjpegUnsupportedError('hirp high-gain container from DJI M4T: validated only on DJI M3TD'), False, id='unsupported'),
    pytest.param(RjpegParameterError('stored settings outside the SDK limits (dirp_measure_ex fails with rc -32)'), True, id='parameter'),
    pytest.param(RjpegUndefinedOutputError('no pixel keeps a valid temperature (the SDK fails dirp_measure_ex with rc -65)'), True,
                 id='undefined-output'),
])
def test_temperatures_logs_and_reraises_refusal(open_rjpeg, error, from_celsius):
    (open_rjpeg.return_value.celsius if from_celsius else open_rjpeg).side_effect = error
    with patch(f'{PYTHON_PARSER}.LoggerService') as MockLogger:
        with pytest.raises(type(error)) as raised:
            PythonDjiThermalParserService().temperatures('dji.jpg', m2ea_mode=True)

    assert raised.value is error
    MockLogger.return_value.warning.assert_called_once_with(f'dji.jpg: {error}')


# The converters' own rules, without sample files: each converter is built around a stand-in for the file's fields.

def _fields(values):
    """A stand-in RjpegFile whose field() returns values[offset] (0 for any other offset)."""
    rjpeg = MagicMock()
    rjpeg.field.side_effect = lambda marker, offset, fmt: values.get(offset, 0)
    rjpeg.u16.return_value = np.zeros(4, np.uint16)
    return rjpeg


def test_h20t_applies_the_output_gain_and_offset_words():
    conv = object.__new__(DirpH20TConverter)
    conv.rjpeg = _fields({84: 110, 86: -50})                # gain 110 %, offset -5.0 C
    with patch.object(_DirpConverter, 'convert', return_value=np.array([10.0, 20.0])):
        out = conv.convert(MeasurementParams(5.0, 70.0, 1.0, 23.0, 0.0), api=True)

    np.testing.assert_allclose(out, [10.0 * 1.1 - 5.0, 20.0 * 1.1 - 5.0])


def _girp():
    conv = object.__new__(GirpConverter)
    conv.rjpeg = _fields({})
    return conv


def test_girp_holds_the_curve_between_minus_30_and_160_c():
    with patch.object(GirpConverter, 'index', return_value=np.array([-1e5, 5000.0, 14000.0])):      # the curve: far below -30, 66, 164 C
        t = _girp().convert(MeasurementParams(5.0, 50.0, 1.0, 23.0, 0.0), api=False)

    assert t[0] == pytest.approx(-30.0)
    assert -30.0 < t[1] < 160.0
    assert t[2] == pytest.approx(160.0)


def test_girp_api_truncates_distance_humidity_emissivity_and_reflected():
    with patch.object(GirpConverter, 'index', return_value=np.array([5000.0])) as index, \
            patch(f'{PYTHON_PARSER}._t4_mix', side_effect=lambda t, w, tr, invalid: t) as mix:
        _girp().convert(MeasurementParams(10.9, 50.9, 0.779, 45.19, 0.0), api=True)

    assert index.call_args.args[1:] == (10.0, 50.0)
    _, weight, reflected, _ = mix.call_args.args
    assert weight == pytest.approx(0.78)                    # 0.77 + 0.01
    assert reflected == pytest.approx(45.1)


HIRP_FIELDS = {80: 8192, 108: 198, 120: 2000, 122: 2}       # transmittance 1, the validated words, a 20 C camera core


@pytest.mark.parametrize('variant, name, value, accepted', [
    ('high-gain', 'distance', 200.0, True), ('high-gain', 'distance', 200.01, False), ('high-gain', 'distance', -0.01, False),
    ('high-gain', 'humidity', -0.4999999701976776, True), ('high-gain', 'humidity', -0.5, False), ('high-gain', 'humidity', 100.5, False),
    ('high-gain', 'emissivity', 0.001, True), ('high-gain', 'emissivity', 1.001, False), ('high-gain', 'reflection', -273.16, False),
    ('high-gain', 'ambient', -100.0, True), ('high-gain', 'ambient', -100.01, False), ('low-gain', 'ambient', -273.0, True),
])
def test_hirp_enforces_the_sdks_ranges(variant, name, value, accepted):
    conv = HirpConverter(_fields({**HIRP_FIELDS, 124: 0 if variant == 'high-gain' else 1}), variant)
    params = MeasurementParams(**dict(dict(distance=10.0, humidity=50.0, emissivity=0.95, reflection=20.0, ambient=20.0), **{name: value}))

    if accepted:
        conv.check(params)
    else:
        with pytest.raises(RjpegParameterError):
            conv.check(params)


def test_hirp_converts_a_lower_emissivity_as_the_minimum():
    conv = HirpConverter(_fields({**HIRP_FIELDS, 124: 0}), 'high-gain')
    with patch.object(HirpConverter, '_high', return_value=np.zeros(4)) as high:
        conv.convert(MeasurementParams(10.0, 50.0, 0.001, 20.0, 20.0), api=True)

    assert high.call_args.args[1].emissivity == HirpConverter.MIN_EMISSIVITY


@pytest.mark.parametrize('variant', ['0.1.0', '0.2.0', '0.3.0'])
@pytest.mark.parametrize('emissivity, accepted', [(0.01, True), (0.05, True), (0.0099, False)])
def test_iirp_accepts_emissivity_down_to_0_01(variant, emissivity, accepted):
    conv = IirpConverter(MagicMock(), variant, 128, 32, (56, 64))
    params = MeasurementParams(10.0, 50.0, emissivity, 20.0, 20.0)

    if accepted:
        conv.check(params)
    else:
        with pytest.raises(RjpegParameterError):
            conv.check(params)
