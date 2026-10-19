"""Linux DIRP must load the bundled linux/*.so files, not windows/*.so."""

import os
from unittest.mock import patch

from core.services.thermal.thermalParserServices.DjiThermalParserService import (
    DjiThermalParserService,
)


def test_linux64_dirp_paths_are_the_bundled_elf_libraries():
    parser = DjiThermalParserService.__new__(DjiThermalParserService)
    with patch(
        "core.services.thermal.thermalParserServices.DjiThermalParserService.platform.system",
        return_value="Linux",
    ), patch(
        "core.services.thermal.thermalParserServices.DjiThermalParserService.platform.architecture",
        return_value=("64bit", ""),
    ):
        paths = parser._get_default_filepaths()

    assert paths[0].endswith(
        "dji_thermal_sdk_v1.7_20241205/linux/release_x64/libdirp.so"
    )
    assert paths[1].endswith("linux/release_x64/libv_dirp.so")
    assert paths[2].endswith("linux/release_x64/libv_iirp.so")
    assert "windows/" not in paths[0]
    for library in paths[:3]:
        assert os.path.isfile(library)
