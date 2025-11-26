"""
Comprehensive tests for PDFSettingsService.

Tests PDF export settings persistence.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch
from core.services.export.PDFSettingsService import PDFSettingsService


@pytest.fixture
def pdf_settings_service():
    """Fixture providing a PDFSettingsService instance."""
    with patch('os.path.expanduser', return_value=tempfile.gettempdir()):
        service = PDFSettingsService()
        yield service


def test_pdf_settings_service_initialization(pdf_settings_service):
    """Test PDFSettingsService initialization."""
    assert pdf_settings_service is not None
    assert pdf_settings_service.config_path is not None


def test_load_settings_default(pdf_settings_service):
    """Test loading default settings when no config exists."""
    # Ensure config file doesn't exist
    if os.path.exists(pdf_settings_service.config_path):
        os.remove(pdf_settings_service.config_path)

    settings = pdf_settings_service.load_settings()

    assert settings['organization'] == ''
    assert settings['search_name'] == ''
    assert settings['include_images_without_flagged_aois'] is False


def test_save_and_load_settings(pdf_settings_service):
    """Test saving and loading settings."""
    # Save settings
    result = pdf_settings_service.save_settings(
        organization='Test Org',
        search_name='Test Search',
        include_images_without_flagged_aois=True
    )

    assert result is True

    # Load settings
    settings = pdf_settings_service.load_settings()

    assert settings['organization'] == 'Test Org'
    assert settings['search_name'] == 'Test Search'
    assert settings['include_images_without_flagged_aois'] is True


def test_save_settings_strips_whitespace(pdf_settings_service):
    """Test that settings are stripped of whitespace."""
    pdf_settings_service.save_settings(
        organization='  Test Org  ',
        search_name='  Test Search  '
    )

    settings = pdf_settings_service.load_settings()

    assert settings['organization'] == 'Test Org'
    assert settings['search_name'] == 'Test Search'
