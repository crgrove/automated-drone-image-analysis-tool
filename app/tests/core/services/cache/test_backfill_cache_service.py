"""
Comprehensive tests for BackfillCacheService.

Tests cache regeneration functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QObject
from core.services.cache.BackfillCacheService import BackfillCacheService


@pytest.fixture
def backfill_cache_service():
    """Fixture providing a BackfillCacheService instance."""
    return BackfillCacheService()


def test_backfill_cache_service_initialization(backfill_cache_service):
    """Test BackfillCacheService initialization."""
    assert backfill_cache_service is not None
    assert backfill_cache_service.cancelled is False


def test_backfill_cache_service_signals(backfill_cache_service):
    """Test that signals are properly defined."""
    assert hasattr(backfill_cache_service, 'progress_message')
    assert hasattr(backfill_cache_service, 'progress_percent')
    assert hasattr(backfill_cache_service, 'complete')
    assert hasattr(backfill_cache_service, 'error')


def test_regenerate_cache_invalid_path(backfill_cache_service):
    """Test regenerating cache with invalid XML path."""
    result = backfill_cache_service.regenerate_cache('/nonexistent/path.xml')

    assert result is False


def test_backfill_cache_service_cancellation(backfill_cache_service):
    """Test cancellation functionality."""
    assert backfill_cache_service.cancelled is False
    backfill_cache_service.cancelled = True
    assert backfill_cache_service.cancelled is True
