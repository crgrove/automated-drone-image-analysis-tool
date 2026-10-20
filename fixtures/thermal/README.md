# Offline thermal fixtures

Put real Matrice 4T / 4TD R-JPEGs here for local spike testing.
Do **not** commit proprietary flight imagery.

## Hybrid decode without DIRP on macOS

1. On **Windows** (ADIAT repo with DIRP DLLs):

   ```bat
   python tools/thermal_sidecar_convert.py path\to\DJI_M4T_sample_T.JPG
   ```

2. Place next to the R-JPEG (same stem):

   - `<stem>.temps.npy` — HxW float32 °C
   - `<stem>.thermal.json` — optional metadata (GPS/XMP notes)

3. On **macOS**, open the folder in ADIAT or spike with:

   ```bash
   PYTHONPATH=app python tools/thermal_decode.py fixtures/thermal/DJI_M4T_sample_T.JPG --print-stats
   ```

See `tests/thermal/README.md` and `plans/phase-a-windows-dirp-notes.md`.
