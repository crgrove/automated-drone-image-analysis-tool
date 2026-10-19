"""Unit tests for NumPy Temperature* cores using synthetic float32 maps."""

import numpy as np
import pytest

from helpers.ThermalAlgorithms import (
    contours_from_mask,
    temperature_anomaly_mask,
    temperature_range_mask,
    temperature_residual_anomaly_mask,
)


def _hot_blob(h=64, w=64, bg=20.0, hot=36.0):
    temps = np.full((h, w), bg, dtype=np.float32)
    temps[20:35, 20:35] = hot
    return temps


def test_temperature_range_mask_selects_hot_blob():
    temps = _hot_blob()
    mask = temperature_range_mask(temps, min_temp=30.0, max_temp=40.0)
    assert mask.dtype == np.uint8
    assert int(mask.sum()) == 15 * 15
    assert mask[25, 25] == 1
    assert mask[0, 0] == 0


def test_temperature_range_mask_empty_when_out_of_range():
    temps = _hot_blob()
    mask = temperature_range_mask(temps, min_temp=100.0, max_temp=200.0)
    assert int(mask.sum()) == 0


def test_temperature_anomaly_above_mean():
    temps = _hot_blob(bg=20.0, hot=50.0)
    mask = temperature_anomaly_mask(temps, threshold=2.0, segments=1, direction="Above Mean")
    assert mask[25, 25] == 1
    assert mask[0, 0] == 0
    contours = contours_from_mask(mask)
    assert len(contours) >= 1


def test_temperature_residual_anomaly_detects_local_hotspot():
    temps = _hot_blob(h=96, w=96, bg=22.0, hot=55.0)
    mask, residual = temperature_residual_anomaly_mask(
        temps,
        delta_t_threshold=2.0,
        background_kernel=31,
        direction="Hot",
        score_sigma_multiplier=1.0,
    )
    assert residual.shape == temps.shape
    assert mask.dtype == np.uint8
    assert int(mask.sum()) > 0
    # Hot blob center should be warmer than local background residual
    assert float(residual[27, 27]) > 5.0
