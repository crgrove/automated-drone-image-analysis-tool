"""
Comprehensive tests for ImageHighlightService.

Tests image highlighting and augmentation functionality.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from core.services.image.ImageHighlightService import ImageHighlightService


@pytest.fixture
def image_highlight_service():
    """Fixture providing an ImageHighlightService instance."""
    return ImageHighlightService()


@pytest.fixture
def test_image():
    """Create a test image."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[50:150, 50:150] = [255, 255, 255]  # White square
    return img


def test_image_highlight_service_initialization(image_highlight_service):
    """Test ImageHighlightService initialization."""
    assert image_highlight_service is not None


def test_highlight_aois(image_highlight_service, test_image):
    """Test highlighting AOIs on an image."""
    aois = [
        {
            'center': (100, 100),
            'radius': 20,
            'area': 400
        }
    ]

    highlighted = ImageHighlightService.highlight_aoi_pixels(
        test_image,
        aois,
        highlight_color=(255, 0, 0)
    )

    assert highlighted.shape == test_image.shape
    assert highlighted.dtype == test_image.dtype
