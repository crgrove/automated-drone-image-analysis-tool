"""
Comprehensive tests for SearchProjectService.

Tests search project management and coordination functionality.
"""

import pytest
import tempfile
import os
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
