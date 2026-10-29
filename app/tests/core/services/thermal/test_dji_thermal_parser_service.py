"""
Tests for DjiThermalParserService's Linux support: the measurement-params struct and the SDK dependency preload.

None of these call the SDK, so they run in CI on every OS.
"""

import ctypes
import os
import platform
from unittest.mock import patch

import pytest

from core.services.thermal.thermalParserServices.DjiThermalParserService import DjiThermalParserService, dirp_measurement_params_t

DJI_PARSER = 'core.services.thermal.thermalParserServices.DjiThermalParserService'


def _libraries_loaded_on(system, architecture):
    """Construct the parser as if on `system` and `architecture`, with CDLL mocked; return the paths it loaded, in order."""
    with patch(f'{DJI_PARSER}.platform.system', return_value=system), \
            patch(f'{DJI_PARSER}.platform.architecture', return_value=(architecture, '')), \
            patch(f'{DJI_PARSER}.CDLL') as MockCdll:
        DjiThermalParserService()
    return [call.args[0] for call in MockCdll.call_args_list]


def test_measurement_params_struct_has_ambient_on_linux_only():
    # The SDK's struct is five floats; Windows and macOS keep the original four (see the TODO on the struct).
    assert ctypes.sizeof(dirp_measurement_params_t) == (20 if platform.system() == 'Linux' else 16)


@pytest.mark.parametrize('architecture, arch', [('64bit', 'x64'), ('32bit', 'x86')])
def test_linux_loads_sdk_dependencies_first_from_sdk_folder(architecture, arch):
    paths = _libraries_loaded_on('Linux', architecture)

    assert [os.path.basename(p) for p in paths] == [
        'libexif.so.12', f'libMicroIA_Release_{arch}.so', f'libMicroTA_Release_{arch}.so', f'libMicroJPEG_Release_{arch}.so',
        'libdirp.so', 'libv_dirp.so', 'libv_iirp.so']
    assert {os.path.dirname(p) for p in paths} == {os.path.dirname(paths[-1])}
    assert os.path.dirname(paths[-1]).endswith(f'release_{arch}')


def test_windows_loads_only_the_sdk_libraries():
    paths = _libraries_loaded_on('Windows', '64bit')

    assert [os.path.basename(p) for p in paths] == ['libdirp.dll', 'libv_dirp.dll', 'libv_iirp.dll']
