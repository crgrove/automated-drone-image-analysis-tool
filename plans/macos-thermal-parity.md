# Cursor plan: ADIAT macOS thermal parity (Windows → macOS)

## Goal
Give ADIAT on Apple Silicon the same radiometric thermal features Windows has today:
- Temperature Range
- Temperature Anomaly
- Temperature Residual Anomaly
…reading real °C from DJI Matrice 4T / 4TD R-JPEG (and other supported cameras), then flagging AOIs.

Upstream: https://github.com/crgrove/automated-drone-image-analysis-tool (GPL-3.0)
Official note: thermal is Windows-only “due to 3rd-party library limitations”.
Windows build bundles `app/external/dji_thermal_sdk_v1.7_20241205` (DLLs) + Autel libs; macOS `app_debug.spec` does **not** ship those binaries.

## Why a naive “port the DLLs” fails
DJI Thermal SDK ships **Windows `.dll` only** (libdirp, libv_dirp, …). No official macOS/Linux `.dylib`. Loading the Windows DLLs natively on Darwin is impossible. Wine/Parallels is a product workaround, not a native Mac build.

## Recommended strategy (pick Phase A first; B is the long-term native path)

### Phase A — Ship a Mac “thermal sidecar” (fastest usable parity)
Build a small helper that turns each R-JPEG into a float32 temperature map + a rendered JPG, then feed ADIAT’s existing AOI logic (or a thin Mac algorithm wrapper).

**Option A1 (preferred engineering path): pure-Python / open parsers**
1. Evaluate `SanNianYiSi/thermal_parser` and any active forks for Matrice 4T R-JPEG / XMP radiometric extraction on Darwin.
2. Also evaluate `lyuhaitao/dji_thermal_sdk` **only as a Windows reference API**; do not depend on its DLLs for Mac.
3. Write `tools/thermal_decode.py` that for each input file returns:
   - `temps.npy` (H×W float32 °C)
   - `preview.jpg` (palette render)
   - metadata JSON (GPS/XMP if present)
4. Unit-test against a small fixture set of real M4T R-JPEGs (user-supplied, keep offline under `fixtures/thermal/`).
5. Reimplement the three algorithms in NumPy (already used elsewhere in ADIAT):
   - Range: mask `min ≤ T ≤ max`, connected components, min area
   - Anomaly: per-image or per-segment mean/std threshold
   - Residual anomaly: local background (box/gaussian) residual threshold
6. Wire as Mac-only algorithm backends in `algorithms.conf` / algorithm service layer, gated by `platform.system() == "Darwin"`.
7. Acceptance: same AOI count ±tolerance vs Windows ADIAT on the fixture set; export PDF/KML still works.

**Option A2 (if open parsers fail on M4T): decode via DJI Windows tool in a VM, then analyze on Mac**
1. Automate a headless Windows VM (Parallels/UTM) or containerized Wine **only if DIRP works under Wine** (often flaky; treat as experiment).
2. Batch-convert R-JPEG → temperature TIFF/CSV with DJI Thermal Analysis Tool 3 / DIRP CLI if available.
3. ADIAT Mac reads the converted maps. Document this as “hybrid workflow”, not true native.

### Phase B — Native Mac DJI Thermal SDK (blocked unless DJI ships dylib)
1. Check current DJI Enterprise Thermal SDK release notes for macOS ARM64 binaries.
2. If DJI publishes `.dylib`, mirror the Windows ctypes bindings used by ADIAT, add them under `app/external/dji_thermal_sdk_*` for Darwin in the PyInstaller spec, enable the three Temperature algorithms on Mac.
3. If DJI never ships Mac libs: open an upstream issue + PR to TEXSAR proposing the Phase A pure-Python path (contribute back under GPL-3.0).

### Phase C — Packaging
1. Update `app_debug.spec` / release spec Darwin branch to include any new native libs or ONNX deps.
2. Build Apple Silicon DMG, codesign + notarize (TEXSAR’s current process).
3. Update User Guide: remove “Windows only” for Temperature algorithms when Phase A/B passes.
4. CI: matrix job `macos-14` + `windows-latest` running thermal fixture tests.

## Concrete Cursor work order
1. Clone upstream; locate Temperature* algorithm modules and the DJI DIRP ctypes wrapper on Windows.
2. Spike: decode one M4T R-JPEG on macOS without DLLs; print min/max/mean °C; fail fast if impossible.
3. If spike OK → implement NumPy ports of the three algorithms + Mac UI enablement.
4. If spike fails → implement hybrid converter workflow + clear UI messaging; file upstream issue summarizing the DLL gap.
5. Do **not** redistribute DJI SDK binaries beyond upstream’s existing Windows packaging rules; respect DJI and Autel licenses.
6. Keep AI Person Detector / colour / anomaly on both platforms unchanged.

## Out of scope
- Cracking or reverse-engineering DJI’s closed SDK beyond published APIs.
- Claiming full Autel/FLIR/Skydio parity until each format is fixture-tested on Mac.
- Shipping Wine inside the .app as the “native” solution.

## Success criteria
- On Apple Silicon Mac, user can run Temperature Range on Matrice 4T R-JPEG and get AOIs without a Windows VM.
- Fixture parity tests documented in `tests/thermal/README.md`.
- PR description links TEXSAR pages + notes the 3rd-party DLL limitation and how this plan removes it for Mac.

## References
- https://www.texsar.org/automated-drone-image-analysis-tool/
- https://github.com/crgrove/automated-drone-image-analysis-tool
- https://github.com/SanNianYiSi/thermal_parser
- https://github.com/lyuhaitao/dji_thermal_sdk (Windows DLL wrapper; reference only)
