"""Mac hybrid path: a sibling .temps.npy feeds the three Temperature* cores.

This does not call DJI DIRP. A Windows/Linux run of
tools/thermal_sidecar_convert.py is what produces a real °C map; here the
map is a known hot blob so Apple Silicon can still prove the algorithms run.
"""

from unittest.mock import patch

import numpy as np
import pytest

from core.services.thermal.thermalParserServices.DjiThermalParserService import (
    DjiThermalParserService,
)
from helpers.ThermalAlgorithms import (
    contours_from_mask,
    temperature_anomaly_mask,
    temperature_range_mask,
    temperature_residual_anomaly_mask,
)


def _pair(tmp_path):
    image = tmp_path / "DJI_M4T_synthetic_T.JPG"
    image.write_bytes(b"placeholder-rjpeg")
    temps = np.full((64, 64), 22.0, dtype=np.float32)
    temps[24:40, 24:40] = 37.0
    np.save(str(image).rsplit(".", 1)[0] + ".temps.npy", temps)
    return image


def test_darwin_sidecar_runs_temperature_range_anomaly_and_residual(tmp_path):
    image = _pair(tmp_path)
    with patch("platform.system", return_value="Darwin"):
        parser = DjiThermalParserService(dtype=np.float32)
        assert parser._use_open_adapter is True
        loaded = np.asarray(parser.temperatures(str(image)), dtype=np.float32)

    assert loaded.shape == (64, 64)
    assert float(loaded[30, 30]) == pytest.approx(37.0)
    assert float(loaded[0, 0]) == pytest.approx(22.0)

    range_mask = temperature_range_mask(loaded, min_temp=30.0, max_temp=40.0)
    assert int(range_mask.sum()) == 16 * 16
    assert len(contours_from_mask(range_mask)) >= 1

    anomaly = temperature_anomaly_mask(
        loaded, threshold=2.0, segments=1, direction="Above Mean"
    )
    assert anomaly[30, 30] == 1
    assert anomaly[0, 0] == 0
    assert len(contours_from_mask(anomaly)) >= 1

    residual_mask, residual = temperature_residual_anomaly_mask(
        loaded,
        delta_t_threshold=2.0,
        background_kernel=15,
        direction="Hot",
        score_sigma_multiplier=1.0,
    )
    assert residual.shape == loaded.shape
    assert int(residual_mask.sum()) > 0
    assert float(residual[30, 30]) > float(residual[0, 0])
