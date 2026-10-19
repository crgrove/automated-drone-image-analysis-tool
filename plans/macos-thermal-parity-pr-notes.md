# Paste into Cursor (Composer / Agent)

Follow `/Users/dfrnc/Desktop/CURSOR-PLAN-mac-thermal-parity.md`.

Work in `/Users/dfrnc/Desktop/adiat-mac-thermal` (local clone of upstream ADIAT).

## First spike (do this before any UI work)
1. Find Windows Temperature* algorithms and DJI DIRP ctypes usage.
2. On macOS Apple Silicon, try to decode one Matrice 4T R-JPEG to a °C float32 map **without** Windows DLLs (evaluate `SanNianYiSi/thermal_parser` and similar open parsers).
3. Print min / max / mean °C. If it fails, stop and document why; propose hybrid converter path.
4. If it works, implement NumPy ports of Temperature Range, Temperature Anomaly, Temperature Residual Anomaly and enable them on Darwin only.
5. Add fixture tests under `tests/thermal/` (user will supply sample R-JPEGs if missing).
6. Do not redistribute DJI proprietary SDK beyond upstream’s existing Windows packaging.
7. Keep AI Person Detector / colour / anomaly unchanged on both platforms.

When the spike succeeds, open a PR against `crgrove/automated-drone-image-analysis-tool` using the template below.

---

# Pull request template (English)

**Title:** feat(macOS): native radiometric thermal algorithms without Windows DJI DLLs

## Summary
Windows ADIAT can run Temperature Range / Anomaly / Residual Anomaly because it bundles the DJI Thermal SDK (Windows `.dll` only). Official macOS builds omit those libraries, so Mac users cannot read real °C from Matrice 4T R-JPEG. This PR adds a Darwin path that decodes radiometric frames with an open parser and reimplements the three temperature AOI algorithms in NumPy, aiming for feature parity on Apple Silicon.

## Motivation
- TEXSAR docs: thermal algorithms “Available On – Windows” due to 3rd-party library limits.
- Mac ADIAT still has person / colour / anomaly detection, but not radiometric warm-body search needed for SAR / lost-pet work with Matrice 4T.

## Approach
- Phase A from plan: decode R-JPEG → float32 °C map on Darwin without DIRP DLLs.
- Port Temperature Range, Temperature Anomaly, Temperature Residual Anomaly.
- Gate with `platform.system() == "Darwin"` (Windows keeps existing SDK path).
- Fixtures + parity checks vs Windows outputs where available.

## Test plan
- [ ] Decode sample Matrice 4T R-JPEG on Apple Silicon; min/max/mean °C look sane
- [ ] Temperature Range (e.g. 30–40 °C) produces AOIs on fixture set
- [ ] Temperature Anomaly + Residual Anomaly run without crash
- [ ] AI Person Detector / colour algorithms unchanged on Mac
- [ ] Windows build still uses DJI SDK path (no regression)
- [ ] Export PDF / KML / CalTopo still works after thermal AOIs

## Out of scope
- Autel / FLIR / Skydio full parity until fixture-tested
- Shipping Wine/Parallels inside the .app
- Reverse-engineering closed DJI binaries beyond published APIs

## References
- https://www.texsar.org/automated-drone-image-analysis-tool/
- Plan: `CURSOR-PLAN-mac-thermal-parity.md`
- https://github.com/SanNianYiSi/thermal_parser
