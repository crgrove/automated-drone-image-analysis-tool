"""
Open / Darwin radiometric decode adapter for DJI R-JPEG.

Windows ADIAT uses DjiThermalParserService + DIRP ctypes (libdirp.dll under
app/external/dji_thermal_sdk_v1.7_*). SanNianYiSi/thermal_parser wraps the same
SDK (.dll/.so only) — there is no official macOS .dylib.

This adapter (used when platform.system() == "Darwin"):
1. Tries optional package ``thermal_parser`` if importable and it can load natives.
2. Falls back to a sidecar float32 map: ``<stem>.temps.npy`` next to the R-JPEG
   (hybrid / precomputed workflow).
3. Otherwise raises ImportError with clear next steps.

TODO(Phase B): when DJI ships Darwin ARM64 dylibs, mirror Windows ctypes here
or extend DjiThermalParserService._get_default_filepaths().
Do not redistribute DJI proprietary SDK beyond upstream's existing packaging.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np

_THERMAL_PARSER_IMPORT_ERROR = (
    "Darwin radiometric DJI decode is unavailable: neither an installable open "
    "parser with native macOS libs nor a sidecar temperature map was found.\n"
    "Options:\n"
    "  1) Place a float32 HxW °C map next to the R-JPEG as '<stem>.temps.npy'\n"
    "     (optional '<stem>.thermal.json' for metadata).\n"
    "  2) Install SanNianYiSi/thermal_parser if your platform has SDK natives "
    "(currently Windows/Linux only; see plans/phase-a-windows-dirp-notes.md).\n"
    "  3) Wait for DJI Thermal SDK Darwin dylibs (Phase B).\n"
    "Original import/error detail: {detail}"
)


def sidecar_temps_path(filepath_image: str) -> str:
    stem, _ = os.path.splitext(filepath_image)
    return f"{stem}.temps.npy"


def sidecar_meta_path(filepath_image: str) -> str:
    stem, _ = os.path.splitext(filepath_image)
    return f"{stem}.thermal.json"


def try_import_thermal_parser():
    """Return the Thermal class from thermal_parser, or None if unavailable."""
    try:
        from thermal_parser import Thermal  # type: ignore
        return Thermal
    except Exception:
        try:
            from thermal import Thermal  # type: ignore
            return Thermal
        except Exception:
            return None


class OpenThermalParserAdapter:
    """Decode DJI R-JPEG to float32 °C without Windows DIRP on Darwin."""

    def __init__(self, dtype=np.float32):
        self._dtype = dtype
        self._Thermal = try_import_thermal_parser()
        self._last_backend = "unavailable"

    def temperatures(
        self,
        filepath_image: str,
        image_height: int = 512,
        image_width: int = 640,
        object_distance: float = 5.0,
        relative_humidity: float = 70.0,
        emissivity: float = 1.0,
        reflected_apparent_temperature: float = 23.0,
        m2ea_mode: bool = False,
    ) -> np.ndarray:
        del image_height, image_width, object_distance, relative_humidity
        del emissivity, reflected_apparent_temperature, m2ea_mode  # kwargs kept for API parity

        temps = self._try_thermal_parser(filepath_image)
        if temps is not None:
            self._last_backend = "thermal_parser"
            return np.asarray(temps, dtype=self._dtype)

        temps = self._try_sidecar(filepath_image)
        if temps is not None:
            self._last_backend = "sidecar_npy"
            return np.asarray(temps, dtype=self._dtype)

        self._last_backend = "unavailable"

        detail = (
            "thermal_parser not importable or failed on this platform; "
            f"no sidecar at {sidecar_temps_path(filepath_image)}"
        )
        raise ImportError(_THERMAL_PARSER_IMPORT_ERROR.format(detail=detail))

    def image(self, filepath_image: str, palette: str = "White Hot") -> np.ndarray:
        """Build a BGR preview from the temperature map (OpenCV colormap)."""
        temps = self.temperatures(filepath_image)
        return render_temperature_preview(temps, palette)

    def decode(
        self, filepath_image: str, palette: str = "White Hot"
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Return (temps float32 °C, preview BGR uint8, metadata dict)."""
        temps = self.temperatures(filepath_image)
        preview = render_temperature_preview(temps, palette)
        meta = self._load_metadata(filepath_image, temps)
        return temps, preview, meta

    def _try_thermal_parser(self, filepath_image: str) -> Optional[np.ndarray]:
        if self._Thermal is None:
            return None
        try:
            parser = self._Thermal(dtype=self._dtype)
            temps = parser.parse(filepath_image=filepath_image)
            if temps is None:
                return None
            return np.asarray(temps, dtype=self._dtype)
        except Exception:
            # Parser present but natives missing (typical on Darwin) — fall through.
            return None

    def _try_sidecar(self, filepath_image: str) -> Optional[np.ndarray]:
        path = sidecar_temps_path(filepath_image)
        if not os.path.isfile(path):
            return None
        temps = np.load(path)
        return np.asarray(temps, dtype=self._dtype)

    def _load_metadata(self, filepath_image: str, temps: np.ndarray) -> Dict[str, Any]:
        meta: Dict[str, Any] = {
            "source_path": filepath_image,
            "shape": list(temps.shape),
            "dtype": str(temps.dtype),
            "min_c": float(np.nanmin(temps)) if temps.size else None,
            "max_c": float(np.nanmax(temps)) if temps.size else None,
            "mean_c": float(np.nanmean(temps)) if temps.size else None,
            "decode_backend": self._infer_backend(filepath_image),
        }
        meta_path = sidecar_meta_path(filepath_image)
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as fh:
                    extra = json.load(fh)
                if isinstance(extra, dict):
                    meta.update(extra)
            except (OSError, json.JSONDecodeError):
                pass
        return meta

    def _infer_backend(self, filepath_image: str) -> str:
        del filepath_image
        return self._last_backend


def render_temperature_preview(temps: np.ndarray, palette: str = "White Hot") -> np.ndarray:
    """Map float °C array to a BGR uint8 image using an OpenCV colormap."""
    arr = np.asarray(temps, dtype=np.float32)
    finite = np.isfinite(arr)
    if not np.any(finite):
        return np.zeros((*arr.shape[:2], 3), dtype=np.uint8)

    lo = float(np.nanmin(arr[finite]))
    hi = float(np.nanmax(arr[finite]))
    if hi <= lo:
        norm = np.zeros(arr.shape, dtype=np.uint8)
    else:
        scaled = (arr - lo) / (hi - lo)
        scaled = np.clip(scaled, 0.0, 1.0)
        scaled[~finite] = 0.0
        norm = (scaled * 255.0).astype(np.uint8)

    cmap = _palette_to_cv2(palette)
    colored = cv2.applyColorMap(norm, cmap)
    if palette.strip().lower() in ("black hot", "blackhot"):
        colored = cv2.bitwise_not(colored)
    return colored


def _palette_to_cv2(palette: str) -> int:
    name = (palette or "White Hot").strip().lower()
    if "inferno" in name or "iron" in name:
        return cv2.COLORMAP_INFERNO
    if "jet" in name or "rainbow" in name:
        return cv2.COLORMAP_JET
    if "hot" in name and "white" not in name and "black" not in name:
        return cv2.COLORMAP_HOT
    # White Hot / Black Hot / default: grayscale then inverted for black hot above
    return cv2.COLORMAP_BONE
