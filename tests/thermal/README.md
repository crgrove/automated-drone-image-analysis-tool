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

## Pending

- Parity check vs Windows DIRP on the same M4T fixture (AOI count ± tolerance).
- Confirm SanNianYiSi/thermal_parser once Darwin natives exist (or stick with sidecar / Phase B dylib).
