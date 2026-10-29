"""Where ADIAT finds ExifTool on macOS.

Thermal images need ExifTool for their metadata on every OS. The macOS build
bundles it in external/; running from source without that copy, an installed
ExifTool on PATH (e.g. Homebrew's) is used. With neither, the bundled path is
still the answer, so the error names where the build expects ExifTool.
"""

import os
from unittest.mock import patch

import pytest

import helpers.MetaDataHelper as metadata_module
from helpers.MetaDataHelper import MetaDataHelper

BUNDLED = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(metadata_module.__file__)), 'external/exiftool'))
INSTALLED = '/opt/homebrew/bin/exiftool'


@pytest.fixture
def macos():
    with patch('platform.system', return_value='Darwin'):
        yield


def _resolve(bundled_present, installed):
    with patch('os.path.isfile', side_effect=lambda p: bundled_present and p == BUNDLED), \
            patch('shutil.which', return_value=installed):
        return MetaDataHelper._get_exif_tool_path()


def test_the_bundled_copy_comes_first(macos):
    assert _resolve(bundled_present=True, installed=INSTALLED) == BUNDLED


def test_an_installed_copy_is_used_without_the_bundled_one(macos):
    assert _resolve(bundled_present=False, installed=INSTALLED) == INSTALLED


def test_with_neither_the_bundled_path_is_returned(macos):
    assert _resolve(bundled_present=False, installed=None) == BUNDLED
