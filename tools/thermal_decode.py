#!/usr/bin/env python3
"""
Decode a DJI (or sidecar-backed) radiometric frame to float32 °C.

Usage (from repo root, with PYTHONPATH=app):

  python tools/thermal_decode.py path/to/DJI_XXXX_T.JPG --out-dir /tmp/out

Writes:
  temps.npy     — HxW float32 °C
  preview.jpg   — palette render
  metadata.json — min/max/mean and any sidecar meta

On Darwin this uses OpenThermalParserAdapter (optional thermal_parser, else
`<stem>.temps.npy` sidecar). On Windows/Linux it prefers DIRP via
DjiThermalParserService when available.

Does not redistribute DJI proprietary SDK binaries.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

# Allow running from repo root without installing the package.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_APP = _REPO_ROOT / "app"
if str(_APP) not in sys.path:
    sys.path.insert(0, str(_APP))


def decode_rjpeg(path: str, palette: str = "White Hot"):
    """Return (temps float32, preview BGR uint8, metadata dict)."""
    import platform
    from core.services.thermal.thermalParserServices.OpenThermalParserAdapter import (
        OpenThermalParserAdapter,
    )

    path = os.fspath(path)
    if platform.system() == "Darwin":
        adapter = OpenThermalParserAdapter(dtype=np.float32)
        return adapter.decode(path, palette=palette)

    # Windows / Linux: try DIRP first, fall back to open adapter (sidecar / thermal_parser).
    try:
        from core.services.thermal.thermalParserServices.DjiThermalParserService import (
            DjiThermalParserService,
        )

        parser = DjiThermalParserService(dtype=np.float32)
        temps = parser.temperatures(filepath_image=path)
        preview = parser.image(path, palette)
        meta = {
            "source_path": path,
            "shape": list(temps.shape),
            "dtype": str(temps.dtype),
            "min_c": float(np.nanmin(temps)),
            "max_c": float(np.nanmax(temps)),
            "mean_c": float(np.nanmean(temps)),
            "decode_backend": "dji_dirp",
        }
        return np.asarray(temps, dtype=np.float32), preview, meta
    except Exception as dirp_err:
        adapter = OpenThermalParserAdapter(dtype=np.float32)
        try:
            return adapter.decode(path, palette=palette)
        except Exception as open_err:
            raise ImportError(
                f"Radiometric decode failed.\nDIRP error: {dirp_err}\n"
                f"Open/sidecar error: {open_err}"
            ) from open_err


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Decode R-JPEG / sidecar to float32 °C map")
    parser.add_argument("image", help="Path to R-JPEG (or any path with sibling .temps.npy)")
    parser.add_argument("--out-dir", default=None, help="Directory for temps.npy / preview / metadata")
    parser.add_argument("--palette", default="White Hot")
    parser.add_argument("--print-stats", action="store_true", help="Print min/max/mean °C")
    args = parser.parse_args(argv)

    temps, preview, meta = decode_rjpeg(args.image, palette=args.palette)

    if args.print_stats or args.out_dir is None:
        print(
            f"shape={temps.shape} min={meta.get('min_c'):.3f} "
            f"max={meta.get('max_c'):.3f} mean={meta.get('mean_c'):.3f} "
            f"backend={meta.get('decode_backend')}"
        )

    if args.out_dir:
        out = Path(args.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        np.save(out / "temps.npy", temps)
        import cv2

        cv2.imwrite(str(out / "preview.jpg"), preview)
        with open(out / "metadata.json", "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)
        print(f"Wrote {out / 'temps.npy'}, {out / 'preview.jpg'}, {out / 'metadata.json'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
