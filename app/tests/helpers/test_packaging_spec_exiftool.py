"""The macOS build bundles ExifTool, which thermal images need (app.spec).

A 2024 change dropped ExifTool from the macOS build while thermal was
Windows-only. Thermal now runs on macOS, and without ExifTool every thermal
image would fail in the packaged app. The ExifTool script finds its Perl
modules in a lib folder beside it, so both must ship.
"""

import ast
import os

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SPEC_PATH = os.path.join(REPO_ROOT, 'app.spec')


def _darwin_entries(keyword):
    """The (source, destination) pairs listed under ``keyword`` in the macOS Analysis() call."""
    with open(SPEC_PATH, encoding='utf-8') as handle:
        tree = ast.parse(handle.read(), filename=SPEC_PATH)
    for node in ast.walk(tree):
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and any(isinstance(c, ast.Constant) and c.value == 'Darwin' for c in node.test.comparators)):
            for call in ast.walk(node):
                if isinstance(call, ast.Call) and getattr(call.func, 'id', None) == 'Analysis':
                    for kw in call.keywords:
                        if kw.arg == keyword:
                            return [ast.literal_eval(t) for t in ast.walk(kw.value) if isinstance(t, ast.Tuple)]
    pytest.fail(f"app.spec's macOS Analysis() has no {keyword}")


def test_the_exiftool_script_is_bundled():
    assert ('app/external/exiftool', 'external') in _darwin_entries('binaries')


def test_its_lib_folder_is_bundled_beside_it():
    assert ('app/external/lib', 'external/lib') in _darwin_entries('datas')
