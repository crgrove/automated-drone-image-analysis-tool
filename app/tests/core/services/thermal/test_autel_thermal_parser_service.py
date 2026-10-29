"""
Tests for AutelThermalImageParser's DLL path.

The DLL is committed and CDLL is mocked, so this runs in CI on every OS.
"""

import os
from unittest.mock import patch

from core.services.thermal.thermalParserServices.AutelThermalParserService import AutelThermalImageParser

AUTEL_PARSER = 'core.services.thermal.thermalParserServices.AutelThermalParserService'


def test_loads_the_committed_dll_when_running_from_source():
    with patch(f'{AUTEL_PARSER}.CDLL') as MockCdll:
        parser = AutelThermalImageParser()

    path = parser._filepath_dll
    MockCdll.assert_called_once_with(path)
    assert os.path.isfile(path)
    assert os.path.normpath(path).endswith(os.path.join('app', 'external', 'autel', 'AutelBridge.dll'))
