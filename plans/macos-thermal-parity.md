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

**Option A2 (active after spike failure): Windows/Linux DIRP → `.temps.npy` sidecar → analyze on Mac**
1. On Windows (or Linux with DIRP), from the ADIAT repo root run:
   `python tools/thermal_sidecar_convert.py <folder-or-R-JPEG>`
   This uses `DjiThermalParserService` / DIRP and writes `<stem>.temps.npy` (+ `.thermal.json`) next to each R-JPEG.
2. Copy the R-JPEGs **and** sidecars to the Mac (same folder layout).
3. ADIAT on Darwin reads sidecars via `OpenThermalParserAdapter` — Temperature Range / Anomaly / Residual Anomaly run without DIRP.
4. On Darwin, `thermal_sidecar_convert.py` exits non-zero with instructions (unless validating existing `.temps.npy`).
5. Document as “hybrid workflow”, not true native radiometric decode.

### Phase B — Native Mac DJI Thermal SDK (blocked unless DJI ships dylib)
1. Check current DJI Enterprise Thermal SDK release notes for macOS ARM64 binaries.
2. If DJI publishes `.dylib`, mirror the Windows ctypes bindings used by ADIAT, add them under `app/external/dji_thermal_sdk_*` for Darwin in the PyInstaller spec, enable the three Temperature algorithms on Mac.
3. If DJI never ships Mac libs: open an upstream issue + PR to TEXSAR proposing the Phase A pure-Python path (contribute back under GPL-3.0).

### Phase C — Packaging
1. Update `app_debug.spec` / release spec Darwin branch to include any new native libs or ONNX deps.
2. Build Apple Silicon DMG, codesign + notarize (TEXSAR’s current process).
3. Update User Guide: remove “Windows only” for Temperature algorithms when Phase A/B passes.
4. CI: matrix job `macos-14` + `windows-latest` running thermal fixture tests.

## Spike result (2026-10-20)

Native Matrice 4T decode on Apple Silicon **failed**. `SanNianYiSi/thermal_parser` raises `NotImplementedError` on Darwin (`Darwin x64`) because it only loads Windows `.dll` / Linux `.so` DIRP libraries. `tools/thermal_decode.py` did not print °C for `images/M4T/DJI_0001_R.JPG` without a sidecar. Details: `plans/phase-a-windows-dirp-notes.md`.

Kept / implemented the hybrid converter (`tools/thermal_sidecar_convert.py`): Darwin still reads `<stem>.temps.npy` and does not load DIRP. Windows DIRP path is unchanged. Mac UI / ImportError messages point users at the Windows converter.

## Concrete Cursor work order
1. Clone upstream; locate Temperature* algorithm modules and the DJI DIRP ctypes wrapper on Windows.
2. Spike: decode one M4T R-JPEG on macOS without DLLs; print min/max/mean °C; fail fast if impossible.
3. If spike OK → implement NumPy ports of the three algorithms + Mac UI enablement.
4. If spike fails → implement hybrid converter workflow + clear UI messaging (**done**: `tools/thermal_sidecar_convert.py` + Darwin ImportError / AlgorithmSelection tip); file upstream issue summarizing the DLL gap.
5. Do **not** redistribute DJI SDK binaries beyond upstream’s existing Windows packaging rules; respect DJI and Autel licenses.
6. Keep AI Person Detector / colour / anomaly on both platforms unchanged.

## Out of scope
- Cracking or reverse-engineering DJI’s closed SDK beyond published APIs.
- Claiming full Autel/FLIR/Skydio parity until each format is fixture-tested on Mac.
- Shipping Wine inside the .app as the “native” solution.

## Success criteria
- On Apple Silicon Mac, user can run Temperature Range on Matrice 4T R-JPEG **with sidecar** `.temps.npy` (from Windows converter) and get AOIs; true native decode remains Phase B.
- Fixture parity tests documented in `tests/thermal/README.md`.
- PR description links TEXSAR pages + notes the 3rd-party DLL limitation and how this plan removes it for Mac.

## References
- https://www.texsar.org/automated-drone-image-analysis-tool/
- https://github.com/crgrove/automated-drone-image-analysis-tool
- https://github.com/SanNianYiSi/thermal_parser
- https://github.com/lyuhaitao/dji_thermal_sdk (Windows DLL wrapper; reference only)
