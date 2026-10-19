#!/usr/bin/env python3
"""
Batch-convert DJI R-JPEG / R-JPG frames to adjacent float32 °C sidecar maps.

Hybrid workflow (Option A2)
---------------------------
Apple Silicon cannot load DJI DIRP (no Darwin .dylib). On a Windows (or Linux)
machine where DIRP / DjiThermalParserService works, run this tool once per
folder of radiometric JPEGs. It writes:

  <stem>.temps.npy      — HxW float32 °C (required by OpenThermalParserAdapter)
  <stem>.thermal.json   — optional metadata (min/max/mean, backend, source)

Copy the R-JPEGs **and** the sidecar files to the Mac. ADIAT on Darwin then
reads the sidecar without needing DIRP.

Usage (from repo root, on Windows / Linux with DIRP available)::

  # Single file
  python tools/thermal_sidecar_convert.py path\\to\\DJI_0001_R.JPG

  # Folder
  python tools/thermal_sidecar_convert.py D:\\flights\\m4t\\ --glob "*_R.JPG" --glob "*_T.JPG"

  # Skip or overwrite existing sidecars
  python tools/thermal_sidecar_convert.py D:\\flights\\m4t\\ --skip-existing
  python tools/thermal_sidecar_convert.py D:\\flights\\m4t\\ --force

On Darwin this exits non-zero with instructions to run on Windows/VM, unless
every input path is already a ``.temps.npy`` file (then it validates and exits 0).

Does **not** redistribute DJI proprietary SDK binaries.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[1]
_APP = _REPO_ROOT / "app"
if str(_APP) not in sys.path:
    sys.path.insert(0, str(_APP))

from core.services.thermal.thermalParserServices.OpenThermalParserAdapter import (  # noqa: E402
    sidecar_meta_path,
    sidecar_temps_path,
)

DEFAULT_GLOBS = ("*_R.JPG", "*_R.JPEG", "*_T.JPG", "*_T.JPEG", "*.RJPEG", "*.rjpeg")
RJPEG_SUFFIXES = {".jpg", ".jpeg", ".rjpeg"}

DecoderFn = Callable[[str], Tuple[np.ndarray, dict]]


def dirp_platform_supported(system: Optional[str] = None) -> bool:
    """Return True when native DIRP CDLL loading is expected (Windows/Linux)."""
    sysname = system or platform.system()
    return sysname in ("Windows", "Linux")


def write_sidecar(
    image_path: str,
    temps: np.ndarray,
    *,
    meta: Optional[dict] = None,
    overwrite: bool = False,
) -> Tuple[Path, Path]:
    """
    Write ``<stem>.temps.npy`` and ``<stem>.thermal.json`` next to ``image_path``.

    Returns (temps_path, meta_path).
    """
    image_path = os.fspath(image_path)
    temps_path = Path(sidecar_temps_path(image_path))
    meta_path = Path(sidecar_meta_path(image_path))

    if temps_path.is_file() and not overwrite:
        raise FileExistsError(
            f"Sidecar already exists (use --force to overwrite): {temps_path}"
        )

    arr = np.asarray(temps, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"Temperature map must be 2-D HxW, got shape {arr.shape}")

    np.save(temps_path, arr)

    payload = {
        "source_path": image_path,
        "shape": list(arr.shape),
        "dtype": "float32",
        "min_c": float(np.nanmin(arr)) if arr.size else None,
        "max_c": float(np.nanmax(arr)) if arr.size else None,
        "mean_c": float(np.nanmean(arr)) if arr.size else None,
        "decode_backend": (meta or {}).get("decode_backend", "dji_dirp"),
        "converter": "tools/thermal_sidecar_convert.py",
    }
    if meta:
        for key, value in meta.items():
            if key not in payload:
                payload[key] = value

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    return temps_path, meta_path


def decode_temps_with_dirp(image_path: str) -> Tuple[np.ndarray, dict]:
    """Decode one R-JPEG via DjiThermalParserService (Windows/Linux DIRP)."""
    from core.services.thermal.thermalParserServices.DjiThermalParserService import (
        DjiThermalParserService,
    )

    parser = DjiThermalParserService(dtype=np.float32)
    if getattr(parser, "_use_open_adapter", False):
        raise RuntimeError(
            "DjiThermalParserService selected the Darwin open/sidecar adapter; "
            "native DIRP is required for sidecar conversion."
        )
    temps = np.asarray(parser.temperatures(filepath_image=image_path), dtype=np.float32)
    meta = {
        "source_path": image_path,
        "shape": list(temps.shape),
        "dtype": str(temps.dtype),
        "min_c": float(np.nanmin(temps)) if temps.size else None,
        "max_c": float(np.nanmax(temps)) if temps.size else None,
        "mean_c": float(np.nanmean(temps)) if temps.size else None,
        "decode_backend": "dji_dirp",
    }
    return temps, meta


def collect_inputs(
    paths: Sequence[str],
    *,
    globs: Sequence[str],
    recursive: bool,
) -> List[Path]:
    """Expand files and directories into a sorted list of candidate paths."""
    found: List[Path] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"Path not found: {p}")
        if p.is_file():
            found.append(p.resolve())
            continue
        patterns = globs or DEFAULT_GLOBS
        for pattern in patterns:
            iterator: Iterable[Path] = p.rglob(pattern) if recursive else p.glob(pattern)
            for match in iterator:
                if match.is_file():
                    found.append(match.resolve())

    seen = set()
    unique: List[Path] = []
    for item in found:
        key = str(item)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def darwin_refusal_message() -> str:
    return (
        "thermal_sidecar_convert.py: native radiometric decode is not available "
        f"on this platform ({platform.system()} {platform.machine()}).\n"
        "DJI DIRP ships Windows .dll / Linux .so only — no Darwin .dylib.\n\n"
        "Hybrid workflow:\n"
        "  1) On Windows (or Linux with DIRP), from the ADIAT repo root run:\n"
        "       python tools/thermal_sidecar_convert.py <folder-or-R-JPEG>\n"
        "  2) Copy each R-JPEG together with its sibling:\n"
        "       <stem>.temps.npy   (and optional <stem>.thermal.json)\n"
        "  3) On macOS, open the folder in ADIAT — Temperature* algorithms read the sidecar.\n\n"
        "See plans/macos-thermal-parity.md and plans/phase-a-windows-dirp-notes.md."
    )


def convert_file(
    image_path: Path,
    *,
    force: bool = False,
    skip_existing: bool = False,
    decoder: Optional[DecoderFn] = None,
) -> dict:
    """Convert or validate one path; errors are returned in result['error']."""
    image_path = Path(image_path)
    base: dict = {
        "source": str(image_path),
        "status": "pending",
        "temps_path": None,
        "meta_path": None,
        "error": None,
    }

    try:
        name_lower = image_path.name.lower()
        if name_lower.endswith(".temps.npy"):
            temps = np.load(str(image_path))
            base["status"] = "already_sidecar"
            base["temps_path"] = str(image_path)
            base["shape"] = list(np.asarray(temps).shape)
            return base

        suffix = image_path.suffix.lower()
        if suffix not in RJPEG_SUFFIXES:
            base["status"] = "skipped"
            base["error"] = f"Unsupported suffix {suffix}"
            return base

        out_temps = Path(sidecar_temps_path(str(image_path)))
        if out_temps.is_file() and skip_existing and not force:
            base["status"] = "skipped_existing"
            base["temps_path"] = str(out_temps)
            return base

        if out_temps.is_file() and not force:
            base["status"] = "error"
            base["error"] = (
                f"Sidecar already exists (use --force to overwrite): {out_temps}"
            )
            return base

        decode = decoder or decode_temps_with_dirp
        temps, meta = decode(str(image_path))
        temps_path, meta_path = write_sidecar(
            str(image_path), temps, meta=meta, overwrite=True
        )
        base["status"] = "converted"
        base["temps_path"] = str(temps_path)
        base["meta_path"] = str(meta_path)
        base["min_c"] = meta.get("min_c")
        base["max_c"] = meta.get("max_c")
        base["mean_c"] = meta.get("mean_c")
        base["shape"] = meta.get("shape")
        return base
    except Exception as exc:
        base["status"] = "error"
        base["error"] = str(exc)
        return base


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Batch-convert DJI R-JPEG frames to adjacent .temps.npy sidecars "
            "(Windows/Linux DIRP → Mac hybrid workflow)."
        )
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="R-JPEG file(s), folder(s), or existing .temps.npy to validate",
    )
    parser.add_argument(
        "--glob",
        dest="globs",
        action="append",
        default=None,
        help="Glob when a path is a directory (repeatable). "
        "Default: *_R.JPG, *_T.JPG, *.RJPEG, …",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Recurse into subfolders when expanding directories",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .temps.npy / .thermal.json",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip images that already have a sibling .temps.npy",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List targets only; do not decode or write",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        inputs = collect_inputs(
            args.paths,
            globs=args.globs or list(DEFAULT_GLOBS),
            recursive=args.recursive,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not inputs:
        print("No matching input files found.", file=sys.stderr)
        return 2

    system = platform.system()
    all_already_sidecars = all(p.name.lower().endswith(".temps.npy") for p in inputs)

    if not dirp_platform_supported(system) and not all_already_sidecars:
        print(darwin_refusal_message(), file=sys.stderr)
        print(
            f"\nRefusing to convert {len(inputs)} file(s) on {system}.",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        for path in inputs:
            print(f"DRY-RUN {path} -> {sidecar_temps_path(str(path))}")
        return 0

    converted = skipped = errors = already = 0
    for path in inputs:
        result = convert_file(
            path,
            force=args.force,
            skip_existing=args.skip_existing,
        )
        status = result["status"]
        if status == "converted":
            converted += 1
            print(
                f"OK  {result['source']} -> {result['temps_path']} "
                f"shape={result.get('shape')} "
                f"min={result.get('min_c')} max={result.get('max_c')} "
                f"mean={result.get('mean_c')}"
            )
        elif status == "already_sidecar":
            already += 1
            print(
                f"OK  already sidecar {result['temps_path']} "
                f"shape={result.get('shape')}"
            )
        elif status in ("skipped", "skipped_existing"):
            skipped += 1
            print(f"SKIP {result['source']} ({result.get('error') or status})")
        else:
            errors += 1
            print(f"ERR {result['source']}: {result.get('error')}", file=sys.stderr)

    print(
        f"Done: converted={converted} already_sidecar={already} "
        f"skipped={skipped} errors={errors}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
