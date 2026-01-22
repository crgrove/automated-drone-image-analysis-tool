#!/usr/bin/env python3
"""
Extract translatable strings from the project.

Usage:
    python scripts/extract_translations.py

Extracts strings from:
- All .ui files in resources/views/
- All self.tr() calls in Python files
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent.parent.resolve()
    os.chdir(project_root)

    translations_dir = project_root / "translations"
    translations_dir.mkdir(exist_ok=True)

    # Collect all source files
    ui_files = list((project_root / "resources" / "views").rglob("*.ui"))
    py_files = [f for f in (project_root / "app").rglob("*.py")
                if not f.name.endswith(("_ui.py", "_rc.py"))]

    all_files = [str(f.relative_to(project_root)).replace("\\", "/")
                 for f in ui_files + py_files]

    print(f"Sources: {len(ui_files)} .ui files, {len(py_files)} .py files")

    # Find or create .ts files
    ts_files = list(translations_dir.glob("*.ts")) or [translations_dir / "app_en.ts"]

    for ts_file in ts_files:
        print(f"\nUpdating {ts_file.name}...")
        result = subprocess.run(
            ["pyside6-lupdate"] + all_files + ["-ts", str(ts_file)],
            capture_output=True, text=True
        )
        if result.stderr:
            print(result.stderr.strip())

    print("\nDone! Open .ts files in Qt Linguist to translate.")


if __name__ == "__main__":
    main()
