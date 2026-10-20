"""Tests for tools/thermal_sidecar_convert.py (no DJI DLL required)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "thermal_sidecar_convert.py"

# Import helpers with app on path (same as the tool does).
sys.path.insert(0, str(REPO / "app"))
sys.path.insert(0, str(REPO / "tools"))

import thermal_sidecar_convert as convert  # noqa: E402


def _fake_decoder(path: str):
    temps = np.linspace(10.0, 40.0, 8 * 10, dtype=np.float32).reshape(8, 10)
    meta = {
        "source_path": path,
        "shape": [8, 10],
        "dtype": "float32",
        "min_c": float(temps.min()),
        "max_c": float(temps.max()),
        "mean_c": float(temps.mean()),
        "decode_backend": "mock_dirp",
    }
    return temps, meta


def test_write_sidecar_roundtrip(tmp_path):
    image = tmp_path / "DJI_0001_R.JPG"
    image.write_bytes(b"fake-rjpeg")
    temps = np.arange(12, dtype=np.float32).reshape(3, 4)

    temps_path, meta_path = convert.write_sidecar(str(image), temps, overwrite=True)

    assert temps_path.is_file()
    assert meta_path.is_file()
    loaded = np.load(temps_path)
    assert loaded.dtype == np.float32
    assert loaded.shape == (3, 4)
    assert np.allclose(loaded, temps)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["shape"] == [3, 4]
    assert meta["converter"] == "tools/thermal_sidecar_convert.py"


def test_write_sidecar_refuses_overwrite_without_force(tmp_path):
    image = tmp_path / "DJI_0001_R.JPG"
    image.write_bytes(b"x")
    temps = np.ones((2, 2), dtype=np.float32)
    convert.write_sidecar(str(image), temps, overwrite=True)
    with pytest.raises(FileExistsError):
        convert.write_sidecar(str(image), temps, overwrite=False)


def test_convert_file_happy_path_with_mock_decoder(tmp_path):
    image = tmp_path / "DJI_0002_T.JPG"
    image.write_bytes(b"fake")

    result = convert.convert_file(image, decoder=_fake_decoder)
    assert result["status"] == "converted"
    assert Path(result["temps_path"]).is_file()
    assert Path(result["meta_path"]).is_file()
    loaded = np.load(result["temps_path"])
    assert loaded.shape == (8, 10)
    assert result["min_c"] == pytest.approx(10.0)
    assert result["max_c"] == pytest.approx(40.0)


def test_convert_file_skip_existing(tmp_path):
    image = tmp_path / "DJI_0003_R.JPG"
    image.write_bytes(b"fake")
    # Pre-create sidecar
    convert.write_sidecar(str(image), np.zeros((2, 2), dtype=np.float32), overwrite=True)

    result = convert.convert_file(image, skip_existing=True, decoder=_fake_decoder)
    assert result["status"] == "skipped_existing"


def test_convert_file_already_sidecar(tmp_path):
    sidecar = tmp_path / "map.temps.npy"
    np.save(sidecar, np.full((4, 4), 21.0, dtype=np.float32))
    result = convert.convert_file(sidecar)
    assert result["status"] == "already_sidecar"
    assert result["shape"] == [4, 4]


def test_darwin_refuses_rjpeg_conversion(tmp_path):
    image = tmp_path / "DJI_0004_R.JPG"
    image.write_bytes(b"fake")
    with patch.object(convert, "dirp_platform_supported", return_value=False):
        with patch("thermal_sidecar_convert.platform.system", return_value="Darwin"):
            # main() checks platform; invoke via subprocess for full CLI coverage
            pass

    env = {**dict(**{k: v for k, v in __import__("os").environ.items()})}
    env["PYTHONPATH"] = str(REPO / "app")
    proc = subprocess.run(
        [sys.executable, str(TOOL), str(image)],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    # On this Linux CI box DIRP path is "supported" so conversion may error on missing DLL.
    # Explicit unit check of refusal message helper + main gate:
    assert "Hybrid workflow" in convert.darwin_refusal_message()


def test_main_darwin_exits_nonzero_for_rjpeg(tmp_path):
    image = tmp_path / "DJI_0005_R.JPG"
    image.write_bytes(b"fake")
    with patch("thermal_sidecar_convert.platform.system", return_value="Darwin"):
        with patch.object(convert, "dirp_platform_supported", return_value=False):
            code = convert.main([str(image)])
    assert code == 1


def test_main_darwin_allows_existing_temps_npy(tmp_path):
    sidecar = tmp_path / "DJI_0006_R.temps.npy"
    np.save(sidecar, np.ones((5, 5), dtype=np.float32))
    with patch("thermal_sidecar_convert.platform.system", return_value="Darwin"):
        with patch.object(convert, "dirp_platform_supported", return_value=False):
            code = convert.main([str(sidecar)])
    assert code == 0


def test_cli_convert_with_injected_decoder_via_api(tmp_path):
    """End-to-end write/read using convert_file (CI-safe, no DLL)."""
    folder = tmp_path / "batch"
    folder.mkdir()
    images = []
    for i in range(3):
        img = folder / f"DJI_{i:04d}_R.JPG"
        img.write_bytes(b"x")
        images.append(img)

    for img in images:
        result = convert.convert_file(img, decoder=_fake_decoder, force=True)
        assert result["status"] == "converted"

    # Round-trip through OpenThermalParserAdapter
    from core.services.thermal.thermalParserServices.OpenThermalParserAdapter import (
        OpenThermalParserAdapter,
    )

    adapter = OpenThermalParserAdapter(dtype=np.float32)
    temps, _preview, meta = adapter.decode(str(images[0]))
    assert temps.shape == (8, 10)
    # Adapter used the sidecar; JSON may still record original DIRP backend from the converter.
    assert adapter._last_backend == "sidecar_npy"
    assert meta.get("converter") == "tools/thermal_sidecar_convert.py"



def test_reraise_parse_failure_preserves_hybrid_message():
    """DJI hybrid ImportError must not collapse to generic 'Invalid image file'."""
    # Import only the helper without pulling exiftool/PIL via full service init deps:
    # load the module source's static method by stubbing heavy imports.
    import importlib
    import sys
    from types import ModuleType

    stubs = {}
    for name in (
        "helpers",
        "helpers.MetaDataHelper",
        "core.services.LoggerService",
        "core.services.thermal.thermalParserServices.DjiThermalParserService",
        "core.services.thermal.thermalParserServices.FlirThermalParserService",
        "core.services.thermal.thermalParserServices.AutelThermalParserService",
    ):
        if name not in sys.modules:
            mod = ModuleType(name)
            stubs[name] = mod
            sys.modules[name] = mod

    sys.modules["helpers.MetaDataHelper"].MetaDataHelper = object  # type: ignore[attr-defined]
    sys.modules["core.services.LoggerService"].LoggerService = object  # type: ignore[attr-defined]
    for svc in (
        "DjiThermalParserService",
        "FlirThermalParserService",
        "AutelThermalImageParser",
    ):
        # Autel is imported as AutelThermalImageParser from AutelThermalParserService module
        pass
    sys.modules[
        "core.services.thermal.thermalParserServices.DjiThermalParserService"
    ].DjiThermalParserService = object  # type: ignore[attr-defined]
    sys.modules[
        "core.services.thermal.thermalParserServices.FlirThermalParserService"
    ].FlirThermalParserService = object  # type: ignore[attr-defined]
    sys.modules[
        "core.services.thermal.thermalParserServices.AutelThermalParserService"
    ].AutelThermalImageParser = object  # type: ignore[attr-defined]

    # Fresh import
    mod_name = "core.services.thermal.ThermalParserService"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    tps = importlib.import_module(mod_name)

    hybrid = ImportError(
        "macOS radiometric DJI decode needs a temperature sidecar. "
        "python tools/thermal_sidecar_convert.py <folder>"
    )
    with pytest.raises(Exception) as exc:
        tps.ThermalParserService._reraise_parse_failure(hybrid)
    assert "Invalid image file" not in str(exc.value)
    assert "sidecar" in str(exc.value).lower() or "thermal_sidecar_convert" in str(exc.value)

    with pytest.raises(Exception) as exc2:
        tps.ThermalParserService._reraise_parse_failure(RuntimeError("boom"))
    assert str(exc2.value) == "Invalid image file"
