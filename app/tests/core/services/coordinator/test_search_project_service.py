"""
Comprehensive tests for SearchProjectService.

Tests search project management and coordination functionality.
"""

import pytest
import tempfile
import os
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
from core.services.coordinator.SearchProjectService import SearchProjectService


@pytest.fixture
def search_project_service():
    """Fixture providing a SearchProjectService instance."""
    return SearchProjectService()


def test_search_project_service_initialization(search_project_service):
    """Test SearchProjectService initialization."""
    assert search_project_service is not None
    assert search_project_service.logger is not None
    assert 'metadata' in search_project_service.project_data
    assert 'batches' in search_project_service.project_data
    assert 'consolidated_aois' in search_project_service.project_data


def test_create_new_project(search_project_service):
    """Test creating a new search project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        batch_xml = os.path.join(tmpdir, 'batch1.xml')

        # Create a minimal XML file
        with open(batch_xml, 'w') as f:
            f.write('<?xml version="1.0"?><data><settings/><images/></data>')

        with patch('core.services.coordinator.SearchProjectService.XmlService') as MockXmlService:
            mock_service = MagicMock()
            mock_service.get_settings.return_value = ({'algorithm': 'ColorRange'}, 10)
            mock_service.get_images.return_value = [
                {'path': 'test1.jpg', 'areas_of_interest': []}
            ]
            MockXmlService.return_value = mock_service

            result = search_project_service.create_new_project(
                'Test Project',
                [batch_xml],
                'Test Coordinator'
            )

            assert result is True
            assert search_project_service.project_data['metadata']['name'] == 'Test Project'


def test_load_project(search_project_service):
    """Test loading an existing project."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp_file:
        tmp_file.write('<?xml version="1.0"?><search_project><metadata><name>Test</name></metadata><batches/><consolidated_aois/></search_project>')
        tmp_path = tmp_file.name

    try:
        result = search_project_service.load_project(tmp_path)
        assert result is True
        assert search_project_service.project_path == tmp_path
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_get_project_summary(search_project_service):
    """Test getting project summary."""
    summary = search_project_service.get_project_summary()

    # Should return None if no batches
    assert summary is None or isinstance(summary, dict)


def test_get_batch_status(search_project_service):
    """Test getting batch status."""
    status = search_project_service.get_batch_status()

    assert isinstance(status, list)

# --------------------------------------------------------------------------- #
#  Merge hardening: no eval() on file content, cross-machine path matching     #
# --------------------------------------------------------------------------- #


def _project_with_consolidated(*aoi_specs):
    """Build a service whose consolidated_aois holds the given entries.

    Each spec: (image_path, center_text, flag_count)
    """
    service = SearchProjectService()
    root = ET.Element('search_project')
    ET.SubElement(root, 'batches')
    consolidated = ET.SubElement(root, 'consolidated_aois')
    for image_path, center_text, flag_count in aoi_specs:
        aoi = ET.SubElement(consolidated, 'aoi')
        ET.SubElement(aoi, 'image_path').text = image_path
        ET.SubElement(aoi, 'center').text = center_text
        ET.SubElement(aoi, 'radius').text = '20'
        ET.SubElement(aoi, 'area').text = '400'
        ET.SubElement(aoi, 'flag_count').text = str(flag_count)
        ET.SubElement(aoi, 'reviews')
    service.xml = ET.ElementTree(root)
    return service, consolidated


_REVIEW_META = {'review_id': 'r1', 'reviewer_name': 'Reviewer One'}


def test_parse_center_reads_legacy_tuple_format():
    """Old projects store centers as str((x, y)); they must keep parsing."""
    assert SearchProjectService._parse_center('(100, 200)') == (100.0, 200.0)
    assert SearchProjectService._parse_center('[15, 25]') == (15.0, 25.0)


def test_parse_center_never_executes_content(tmp_path):
    """A crafted center must be inert data, not code."""
    marker = tmp_path / 'pwned.txt'
    payload = f"__import__('pathlib').Path(r'{marker}').write_text('x')"

    result = SearchProjectService._parse_center(payload)

    assert result == (0.0, 0.0)
    assert not marker.exists()


def test_parse_center_malformed_degrades_to_origin():
    assert SearchProjectService._parse_center('') == (0.0, 0.0)
    assert SearchProjectService._parse_center('garbage') == (0.0, 0.0)
    assert SearchProjectService._parse_center('(1,)') == (0.0, 0.0)


def test_merge_matches_same_image_across_machines():
    """A Windows-authored path and a POSIX path to the same capture merge."""
    service, consolidated = _project_with_consolidated(
        (r'C:\Search\Batch1\DJI_0042.JPG', '(100, 200)', 1),
    )
    images = [{
        'path': '/mnt/usb/Batch1/DJI_0042.JPG',
        'areas_of_interest': [{'center': (103, 198), 'flagged': True}],
    }]

    service._merge_aoi_data('batch1', images, _REVIEW_META)

    aois = consolidated.findall('aoi')
    assert len(aois) == 1  # merged, not duplicated
    assert aois[0].findtext('flag_count') == '2'


def test_merge_still_separates_different_filenames():
    service, consolidated = _project_with_consolidated(
        (r'C:\Search\Batch1\DJI_0042.JPG', '(100, 200)', 1),
    )
    images = [{
        'path': r'C:\Search\Batch1\DJI_0043.JPG',
        'areas_of_interest': [{'center': (100, 200), 'flagged': False}],
    }]

    service._merge_aoi_data('batch1', images, _REVIEW_META)

    assert len(consolidated.findall('aoi')) == 2


def test_merge_separates_distant_centers_on_same_image():
    service, consolidated = _project_with_consolidated(
        (r'C:\Search\Batch1\DJI_0042.JPG', '(100, 200)', 0),
    )
    images = [{
        'path': r'C:\Search\Batch1\DJI_0042.JPG',
        'areas_of_interest': [{'center': (400, 500), 'flagged': True}],
    }]

    service._merge_aoi_data('batch1', images, _REVIEW_META)

    assert len(consolidated.findall('aoi')) == 2


def test_merge_matches_within_review_after_new_aoi_created():
    """Two reviewers' rows arriving in one merge call still consolidate."""
    service, consolidated = _project_with_consolidated()
    images = [{
        'path': r'C:\Search\Batch1\DJI_0042.JPG',
        'areas_of_interest': [{'center': (100, 200), 'flagged': True}],
    }]
    service._merge_aoi_data('batch1', images, _REVIEW_META)

    # Second review of the same AOI from another machine
    images2 = [{
        'path': '/home/rev2/Batch1/DJI_0042.JPG',
        'areas_of_interest': [{'center': (98, 202), 'flagged': True}],
    }]
    service._merge_aoi_data('batch1', images2, {'review_id': 'r2', 'reviewer_name': 'Reviewer Two'})

    aois = consolidated.findall('aoi')
    assert len(aois) == 1
    assert aois[0].findtext('flag_count') == '2'
    reviews = aois[0].find('reviews').findall('review')
    assert {r.get('review_id') for r in reviews} == {'r1', 'r2'}


def test_merge_survives_malicious_center_in_project_file(tmp_path):
    """A hostile center in the stored project neither runs nor kills the merge."""
    marker = tmp_path / 'pwned.txt'
    payload = f"__import__('pathlib').Path(r'{marker}').write_text('x')"
    service, consolidated = _project_with_consolidated(
        (r'C:\Search\Batch1\DJI_0042.JPG', payload, 0),
    )
    images = [{
        'path': r'C:\Search\Batch1\DJI_0042.JPG',
        'areas_of_interest': [{'center': (5, 5), 'flagged': False}],
    }]

    service._merge_aoi_data('batch1', images, _REVIEW_META)

    assert not marker.exists()
    # (5,5) is within 10px of the degraded (0,0) center, so it merges there
    assert len(consolidated.findall('aoi')) == 1
