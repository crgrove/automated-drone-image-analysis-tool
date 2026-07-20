#!/usr/bin/env python3
"""
Translation management script.

Usage:
    python scripts/extract_translations.py           # Extract strings only
    python scripts/extract_translations.py --compile # Extract and compile

Extracts strings from:
- All .ui files in resources/views/
- All self.tr() calls in Python files
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


LANGUAGES = ["en", "it", "es", "nl"]


def extract(project_root: Path, translations_dir: Path):
    """Extract translatable strings from source files.

    Uses lupdate's ``@lst-file`` argument syntax (one path per line in a
    temporary text file) to sidestep the Windows ``CreateProcess``
    command-line length limit (~32 K chars). With ~550+ source files,
    the legacy "pass every path on argv" approach overflows on Windows;
    lupdate reads the list file directly so size is no longer a
    constraint, and the syntax is officially supported (``.pro`` files
    are documented as deprecated for new code).
    """
    # Collect all source files
    ui_files = list((project_root / "resources" / "views").rglob("*.ui"))
    py_files = [f for f in (project_root / "app").rglob("*.py")
                if not f.name.endswith(("_ui.py", "_rc.py"))]

    print(f"Sources: {len(ui_files)} .ui files, {len(py_files)} .py files")

    # Ensure every supported language has a .ts file in the list
    # (pyside6-lupdate creates missing ones).
    ts_files = [translations_dir / f"app_{lang}.ts" for lang in LANGUAGES]
    for ts_file in ts_files:
        if not ts_file.exists():
            ts_file.write_text(
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<!DOCTYPE TS>\n<TS version="2.1"></TS>\n',
                encoding="utf-8",
            )

    sources_lst = translations_dir / "_lupdate_sources.lst"
    ts_lst = translations_dir / "_lupdate_ts.lst"
    _write_list_file(sources_lst, py_files + ui_files)
    _write_list_file(ts_lst, ts_files)

    try:
        result = subprocess.run(
            [
                "pyside6-lupdate",
                "-no-obsolete",
                f"@{sources_lst}",
                "-ts", f"@{ts_lst}",
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        for ts_file in ts_files:
            print(f"  Updated {ts_file.name}")
        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line and ('error' in line.lower() or 'warning' in line.lower()):
                    print(f"    {line.strip()}")
        if result.returncode != 0:
            print(f"  pyside6-lupdate returned exit code {result.returncode}")
    finally:
        for tmp in (sources_lst, ts_lst):
            try:
                tmp.unlink()
            except OSError:
                pass


def _write_list_file(lst_path: Path, paths) -> None:
    """Write a newline-delimited list file consumed by lupdate's ``@``-prefix.

    Paths are written as absolute strings on the local file system so
    lupdate doesn't have to resolve them relative to its own CWD.
    """
    with lst_path.open("w", encoding="utf-8") as f:
        for p in paths:
            f.write(str(Path(p).resolve()) + "\n")


def compile_translations(translations_dir: Path):
    """Compile .ts files to .qm binary files."""
    ts_files = list(translations_dir.glob("*.ts"))

    if not ts_files:
        print("No .ts files found to compile.")
        return

    print(f"\nCompiling {len(ts_files)} translation file(s)...")

    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        result = subprocess.run(
            ["pyside6-lrelease", str(ts_file)],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if qm_file.exists():
            print(f"  {ts_file.name} -> {qm_file.name}")
        else:
            print(f"  Failed to compile {ts_file.name}")
            if result.stderr:
                print(f"    {result.stderr.strip()}")


def main():
    parser = argparse.ArgumentParser(description="Manage translations")
    parser.add_argument("--compile", "-c", action="store_true",
                        help="Compile .ts files to .qm after extraction")
    parser.add_argument("--compile-only", action="store_true",
                        help="Only compile, don't extract")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.resolve()
    os.chdir(project_root)

    translations_dir = project_root / "translations"
    translations_dir.mkdir(exist_ok=True)

    if not args.compile_only:
        print("Extracting translatable strings...")
        extract(project_root, translations_dir)

    if args.compile or args.compile_only:
        compile_translations(translations_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
