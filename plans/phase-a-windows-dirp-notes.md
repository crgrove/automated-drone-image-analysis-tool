# Phase A notes: Windows Temperature* algorithms + DJI DIRP

## Where Windows radiometric decode lives

| Piece | Path |
|-------|------|
| Algorithm registration (Windows-only until Phase A) | `app/algorithms.conf` → `ThermalRange`, `ThermalAnomaly`, `ThermalResidualAnomaly` |
| Temperature Range | `app/algorithms/images/ThermalRange/services/ThermalRangeService.py` |
| Temperature Anomaly | `app/algorithms/images/ThermalAnomaly/services/ThermalAnomalyService.py` |
| Temperature Residual Anomaly | `app/algorithms/images/ThermalResidualAnomaly/services/ThermalResidualAnomalyService.py` |
| Camera routing (FLIR / DJI / Autel) | `app/core/services/thermal/ThermalParserService.py` |
| DJI DIRP ctypes wrapper | `app/core/services/thermal/thermalParserServices/DjiThermalParserService.py` |
| Bundled DJI SDK binaries | `app/external/dji_thermal_sdk_v1.7_20241205/{windows,linux}/` (`.dll` / `.so` only — **no Darwin `.dylib`**) |

## DIRP usage (Windows)

`DjiThermalParserService` loads `libdirp`, `libv_dirp`, `libv_iirp` via `ctypes.CDLL`, then:

1. `dirp_create_from_rjpeg` — open R-JPEG bytes
2. `dirp_get_rjpeg_resolution` / `dirp_get_measurement_params`
3. `dirp_measure_ex` — float32 °C map (or `dirp_measure` int16 / 10)
4. `dirp_set_pseudo_color` + `dirp_process` — palette preview

`_get_default_filepaths()` raises `NotImplementedError` on Darwin.

## Phase A Darwin path (this PR)

- Enable the three Thermal* algorithms on Darwin in `algorithms.conf`.
- On Darwin, DJI decode goes through `OpenThermalParserAdapter` (optional `thermal_parser` if present; else sidecar `*.temps.npy`; else clear `ImportError`).
- AOI logic stays NumPy/OpenCV (same services); pure helpers in `helpers/ThermalAlgorithms.py` for unit tests without R-JPEG.
- Do **not** redistribute additional DJI proprietary SDK binaries.

## Evaluated open parser

[SanNianYiSi/thermal_parser](https://github.com/SanNianYiSi/thermal_parser) also wraps the DJI Thermal SDK (win/linux natives only). Useful as a Windows/Linux reference and optional dependency; it does **not** remove the Darwin dylib gap by itself.

## Spike (2026-10-20, Apple Silicon) — native decode failed

Host: Darwin, `platform.architecture()` reports `64bit` (so the library names the platform `Darwin x64`).

Sample (not committed): `SanNianYiSi/thermal_parser` `images/M4T/DJI_0001_R.JPG`.
ExifTool dump in that repo: Make `DJI`, Camera Model Name `M4T`, 640×512, software `10.00.08.09`.

What ran:

1. `Thermal()` from `thermal_parser` (SDK 1.7 plugins, `.dll` / `.so` only).
   Raised before any pixel was read:

   `NotImplementedError: currently not supported for running on this platform: Darwin x64`

   `get_default_filepaths()` only accepts Windows and Linux, and looks for `libdirp.dll` or `libdirp.so`. There is no Darwin `.dylib` in DJI Thermal SDK 1.7 or in that repo’s `plugins/`.

2. `python tools/thermal_decode.py` on the same R-JPEG, with no sidecar.
   Raised `ImportError` from `OpenThermalParserAdapter`. No min/max/mean °C was produced from the file.

Hybrid path still works: a sibling `<stem>.temps.npy` (synthetic 2×2 map, not temperatures from this R-JPEG) printed `min=10 max=40 mean=25` with `decode_backend=sidecar_npy`. Windows/Linux DIRP `CDLL` loading is unchanged. No extra DJI SDK binaries were added to this repo.

Stopped here. Do not treat the three Temperature algorithms as native radiometric on macOS until a real °C map can be produced without Windows/Linux SDK binaries. The NumPy AOI helpers stay unit-tested on synthetic maps only.

## Hybrid sidecar converter (Option A2) — implemented

Tool: `tools/thermal_sidecar_convert.py`

| Host | Behavior |
|------|----------|
| Windows / Linux | Decode each R-JPEG via `DjiThermalParserService` (DIRP), write `<stem>.temps.npy` + `<stem>.thermal.json` next to the image |
| Darwin | Exit non-zero with hybrid instructions (unless every input is already `.temps.npy`, which is validated only) |

### CLI (Windows example)

```bat
cd automated-drone-image-analysis-tool
python tools/thermal_sidecar_convert.py D:\flights\m4t\ --glob *_R.JPG --glob *_T.JPG
python tools/thermal_sidecar_convert.py D:\flights\m4t\DJI_0001_R.JPG --force
```

Then copy the R-JPEGs together with the new `.temps.npy` / `.thermal.json` files to the Mac and open that folder in ADIAT.

### Mac UX when sidecar is missing

- `OpenThermalParserAdapter` raises `ImportError` with the hybrid workflow steps (mentions `thermal_sidecar_convert.py`).
- `ThermalParserService.parse_file` preserves that message instead of collapsing to generic "Invalid image file" for DJI.
- Image Analysis Guide (`AlgorithmSelectionPage`) appends a short macOS sidecar note when a Temperature* algorithm is selected on Darwin.

Do **not** redistribute additional DJI SDK binaries; the converter uses the SDK already bundled under `app/external/dji_thermal_sdk_v1.7_*` on Windows/Linux.
