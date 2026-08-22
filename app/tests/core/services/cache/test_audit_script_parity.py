"""Parity tests for scripts/audit_thumbnail_keys.py.

The audit script is deliberately stdlib-only so it runs on field machines
without the app environment, which forces it to re-implement two pieces of
production logic by hand: the thumbnail cache-key formula
(ThumbnailCacheService.get_cache_key) and the results-XML AOI shape
(XmlService.add_image_to_xml / get_images). Its verdict is only worth
anything while those mirrors stay byte-identical - a drifted mirror reports
'clean' on a dataset that does collide. These tests fail the moment either
side changes without the other.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from core.services.cache.ThumbnailCacheService import ThumbnailCacheService
from core.services.XmlService import XmlService

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PATH = REPO_ROOT / 'scripts' / 'audit_thumbnail_keys.py'


@pytest.fixture(scope='module')
def audit_script():
    spec = importlib.util.spec_from_file_location('audit_thumbnail_keys', SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_exists_where_the_field_docs_say():
    assert SCRIPT_PATH.is_file(), f"audit script missing at {SCRIPT_PATH}"


def test_cache_key_matches_production_formula(audit_script):
    """The script's key must equal ThumbnailCacheService.get_cache_key for
    XML-shaped AOI data (center tuple + int radius, as XmlService parses)."""
    service = ThumbnailCacheService(dataset_cache_dir=None)
    cases = [
        ('0_000_00_123.jpg', {'center': (500, 300), 'radius': 15}),
        ('DJI_0042.JPG', {'center': (0, 0), 'radius': 0}),
        ('img.png', {'center': (1234.5, 67.25), 'radius': 50}),
    ]
    for filename, aoi in cases:
        expected = service.get_cache_key(f"C:\\anywhere\\{filename}", aoi)
        actual = audit_script.cache_key(filename, aoi['center'], aoi['radius'])
        assert actual == expected, f"key drift for {filename} {aoi}"


def test_script_parses_xml_written_by_the_real_writer(tmp_path):
    """Round-trip: XML produced by XmlService.add_image_to_xml must be
    parsed by the script with matching image/AOI counts and a correctly
    detected collision (same basename + same center/radius across folders).
    """
    xml_path = tmp_path / 'ADIAT_Data.xml'
    service = XmlService()
    service.add_image_to_xml({
        'path': str(tmp_path / 'sortie1' / '0_000_00_001.jpg'),
        'aois': [
            {'center': (500, 300), 'radius': 15, 'area': 120.0, 'number': 1},
            {'center': (10, 20), 'radius': 15, 'area': 60.0, 'number': 2},
        ],
    })
    service.add_image_to_xml({
        'path': str(tmp_path / 'sortie2' / '0_000_00_001.jpg'),  # same basename
        'aois': [
            {'center': (500, 300), 'radius': 15, 'area': 90.0, 'number': 3},  # collides with #1
        ],
    })
    service.save_xml_file(str(xml_path))

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(xml_path)],
        capture_output=True, text=True,
    )

    assert 'Images: 2   AOIs: 3' in result.stdout, result.stdout
    assert 'Duplicate basenames: 1' in result.stdout, result.stdout
    assert 'COLLISIONS (cross-image, same key): 1' in result.stdout, result.stdout
    assert result.returncode == 1  # collisions found


def test_script_reports_clean_dataset(tmp_path):
    xml_path = tmp_path / 'ADIAT_Data.xml'
    service = XmlService()
    service.add_image_to_xml({
        'path': str(tmp_path / '0_000_00_001.jpg'),
        'aois': [{'center': (500, 300), 'radius': 15, 'area': 120.0, 'number': 1}],
    })
    service.add_image_to_xml({
        'path': str(tmp_path / '0_000_00_002.jpg'),
        'aois': [{'center': (500, 300), 'radius': 15, 'area': 90.0, 'number': 2}],
    })
    service.save_xml_file(str(xml_path))

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(xml_path)],
        capture_output=True, text=True,
    )

    assert 'Images: 2   AOIs: 2' in result.stdout, result.stdout
    assert 'RESULT: clean' in result.stdout, result.stdout
    assert result.returncode == 0
