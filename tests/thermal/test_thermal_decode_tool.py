"""Smoke tests for tools/thermal_decode.py using a sidecar map."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "thermal_decode.py"


def test_thermal_decode_cli_sidecar(tmp_path):
    image = tmp_path / "sample_T.JPG"
    image.write_bytes(b"fake")
    temps = np.arange(20, dtype=np.float32).reshape(4, 5)
    np.save(str(image).rsplit(".", 1)[0] + ".temps.npy", temps)
    out_dir = tmp_path / "out"

    env = {**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(REPO / "app")}
    proc = subprocess.run(
        [sys.executable, str(TOOL), str(image), "--out-dir", str(out_dir), "--print-stats"],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert (out_dir / "temps.npy").is_file()
    assert (out_dir / "preview.jpg").is_file()
    meta = json.loads((out_dir / "metadata.json").read_text(encoding="utf-8"))
    assert meta["shape"] == [4, 5]
