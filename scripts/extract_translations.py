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


def extract(project_root: Path, translations_dir: Path):
    """Extract translatable strings from source files."""
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
        print(f"  Updating {ts_file.name}...")
        result = subprocess.run(
            ["pyside6-lupdate"] + all_files + ["-ts", str(ts_file)],
            capture_output=True, text=True
        )
        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if 'source text' in line.lower():
                    print(f"    {line.strip()}")


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
            capture_output=True, text=True
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
