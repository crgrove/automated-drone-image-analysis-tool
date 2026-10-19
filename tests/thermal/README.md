# Thermal fixture tests (Phase A macOS parity)

## What runs in CI / without proprietary samples

Unit tests under `tests/thermal/` use **synthetic float32 °C maps** only.
They exercise NumPy ports of Temperature Range / Anomaly / Residual Anomaly
and the Darwin open/sidecar decode adapter — no real Matrice 4T R-JPEG required.

```bash
# from repo root
PYTHONPATH=app pytest tests/thermal -q
```

## Real R-JPEG fixtures (offline, not committed)

Place user-supplied radiometric samples under:

```
fixtures/thermal/
  DJI_M4T_sample_T.JPG          # real R-JPEG (do not commit proprietary flights)
  DJI_M4T_sample_T.temps.npy    # optional sidecar float32 HxW °C (hybrid path)
  DJI_M4T_sample_T.thermal.json # optional metadata
```

`fixtures/thermal/` is intentionally kept local / gitignored for real imagery.
Spike decode on Apple Silicon:

```bash
PYTHONPATH=app python tools/thermal_decode.py fixtures/thermal/DJI_M4T_sample_T.JPG --print-stats --out-dir /tmp/m4t-decode
```

## Spike status (2026-10-20)

Native decode of the public `thermal_parser` M4T sample failed on Apple Silicon (`NotImplementedError: Darwin x64`). No real R-JPEG or DIRP-derived `.temps.npy` is committed. Hybrid sidecar remains the Darwin input.

`test_darwin_sidecar_algorithms.py` loads a synthetic sidecar through `DjiThermalParserService` on Darwin and checks Temperature Range / Anomaly / Residual Anomaly. It does not replace a Windows DIRP conversion.

## Hybrid converter (Windows → Mac)

On a Windows machine with DIRP available:

```bat
python tools/thermal_sidecar_convert.py path\to\R-JPEG-or-folder
```

Produces `<stem>.temps.npy` next to each image. Copy R-JPEG + sidecar to the Mac; Darwin decode uses the sidecar.

Converter unit tests (mocked decode, no DLL):

```bash
PYTHONPATH=app pytest tests/thermal/test_thermal_sidecar_convert.py -q
```

## Pending

- Parity check vs Windows DIRP on the same M4T fixture (AOI count ± tolerance).
- A Darwin-native °C decoder. `thermal_parser` does not provide one (Windows/Linux SDK only).
