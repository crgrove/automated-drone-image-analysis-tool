"""Tests for Darwin open/sidecar radiometric adapter (no real R-JPEG)."""

import json
import os
from unittest.mock import patch

import numpy as np
import pytest

from core.services.thermal.thermalParserServices.OpenThermalParserAdapter import (
    OpenThermalParserAdapter,
    sidecar_temps_path,
)


def test_sidecar_decode_returns_float32_map(tmp_path):
    image = tmp_path / "DJI_fake_T.JPG"
    image.write_bytes(b"not-a-real-jpeg")
    temps = np.linspace(10.0, 40.0, 32 * 48, dtype=np.float32).reshape(32, 48)
    np.save(sidecar_temps_path(str(image)), temps)
    meta_path = str(image).rsplit(".", 1)[0] + ".thermal.json"
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump({"camera": "M4T", "note": "synthetic"}, fh)

    adapter = OpenThermalParserAdapter(dtype=np.float32)
    out, preview, meta = adapter.decode(str(image))

    assert out.dtype == np.float32
    assert out.shape == (32, 48)
    assert preview.shape == (32, 48, 3)
    assert meta["min_c"] == pytest.approx(float(temps.min()), rel=1e-5)
    assert meta["max_c"] == pytest.approx(float(temps.max()), rel=1e-5)
    assert meta["camera"] == "M4T"
    assert meta["decode_backend"] == "sidecar_npy"


def test_missing_sidecar_raises_importerror(tmp_path):
    image = tmp_path / "missing.JPG"
    image.write_bytes(b"x")
    adapter = OpenThermalParserAdapter(dtype=np.float32)
    with patch.object(adapter, "_Thermal", None):
        with pytest.raises(ImportError) as exc:
            adapter.temperatures(str(image))
    msg = str(exc.value).lower()
    assert "sidecar" in msg or "temps.npy" in msg or "hybrid" in msg or "macos radiometric" in msg


def test_dji_parser_uses_adapter_on_darwin(tmp_path):
    image = tmp_path / "DJI_fake_T.JPG"
    image.write_bytes(b"x")
    temps = np.full((16, 16), 25.0, dtype=np.float32)
    np.save(sidecar_temps_path(str(image)), temps)

    with patch("platform.system", return_value="Darwin"):
        # Re-import path: construct service under Darwin patch
        from core.services.thermal.thermalParserServices.DjiThermalParserService import (
            DjiThermalParserService,
        )

        # Force Darwin adapter path even if this host is Linux
        parser = DjiThermalParserService.__new__(DjiThermalParserService)
        parser._dtype = np.float32
        parser._use_open_adapter = True
        parser._open_adapter = OpenThermalParserAdapter(dtype=np.float32)

        got = parser.temperatures(filepath_image=str(image))
        assert got.shape == (16, 16)
        assert float(got.mean()) == pytest.approx(25.0)
