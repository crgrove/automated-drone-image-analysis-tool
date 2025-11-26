"""
Comprehensive tests for CachePathService.

Tests cache path detection and management.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.services.cache.CachePathService import CachePathService


@pytest.fixture
def cache_path_service():
    """Fixture providing a CachePathService instance."""
    return CachePathService()


def test_cache_path_service_initialization(cache_path_service):
    """Test CachePathService initialization."""
    assert cache_path_service is not None
    assert cache_path_service.logger is not None


def test_check_and_prompt_for_caches_all_exist(cache_path_service):
    """Test when all caches exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, 'ADIAT_Data.xml')
        thumbnail_cache = Path(tmpdir) / '.thumbnails'
        thumbnail_cache.mkdir(exist_ok=True)

        with patch('core.services.cache.CachePathService.CacheLocationDialog'):
            alt_dir, success = cache_path_service.check_and_prompt_for_caches(
                xml_path, None
            )

            assert success is True


def test_check_and_prompt_for_caches_missing(cache_path_service):
    """Test when caches are missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, 'ADIAT_Data.xml')

        mock_dialog = MagicMock()
        mock_dialog.exec.return_value = 0  # Rejected
        mock_dialog.get_selected_path.return_value = None

        with patch('core.services.cache.CachePathService.CacheLocationDialog', return_value=mock_dialog):
            alt_dir, success = cache_path_service.check_and_prompt_for_caches(
                xml_path, None
            )

            assert success is True  # Should continue anyway


def test_update_cache_paths(cache_path_service):
    """Test updating cache paths for viewer controllers."""
    mock_viewer = MagicMock()
    mock_viewer.gallery_controller = MagicMock()
    mock_viewer.gallery_controller.model = MagicMock()
    mock_viewer.gallery_controller.model.thumbnail_loader = MagicMock()
    mock_viewer.gallery_controller.model.thumbnail_loader.set_dataset_cache_dir = MagicMock()

    mock_viewer.thumbnail_controller = MagicMock()
    mock_viewer.thumbnail_controller.loader = MagicMock()

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path_service.update_cache_paths(Path(tmpdir), mock_viewer)

        # Verify paths were updated
        assert mock_viewer.gallery_controller.model.dataset_dir == Path(tmpdir)
