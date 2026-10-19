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
