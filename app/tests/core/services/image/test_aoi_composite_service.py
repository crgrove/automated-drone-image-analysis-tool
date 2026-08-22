"""
Tests for AOICompositeService.

Covers generation of the multi-zoom composite images shared by the PDF report
and the CalTopo photo export.
"""

from unittest.mock import MagicMock

import numpy as np
import pytest

from core.services.image.AOICompositeService import AOICompositeService


@pytest.fixture
def service():
    """Provide a composite service with a mocked logger."""
    return AOICompositeService(logger=MagicMock())


@pytest.fixture
def source_array():
    """A BGR image array with a distinct patch where the AOI sits."""
    array = np.zeros((600, 800, 3), dtype=np.uint8)
    array[290:310, 390:410] = (0, 255, 0)
    return array


@pytest.fixture
def aoi():
    """A simple AOI in the middle of the source array."""
    return {'center': (400, 300), 'radius': 20}


def test_create_composite_returns_image(service, source_array, aoi):
    """The composite is a valid BGR image."""
    composite = service.create_composite(source_array, aoi, 0, (255, 255, 0))

    assert composite is not None
    assert composite.ndim == 3
    assert composite.shape[2] == 3


def test_create_composite_layout(service, source_array, aoi):
    """The composite stacks the full view on top of the zoom insets."""
    full_img, _ = service.create_full_rotated_image(source_array, aoi, 0, (255, 255, 0))
    composite = service.create_composite(source_array, aoi, 0, (255, 255, 0))

    # Same width as the full view, and taller than it (insets + 20px gap below)
    assert composite.shape[1] == full_img.shape[1]
    assert composite.shape[0] > full_img.shape[0]


def test_create_composite_with_bearing(service, source_array, aoi):
    """A non-zero bearing still produces a composite (north-up rotation)."""
    composite = service.create_composite(source_array, aoi, 45, (255, 255, 0))

    assert composite is not None


def test_create_composite_uses_rotation_cache(service, source_array, aoi):
    """Rotated images are cached per (cache_key, bearing)."""
    service.create_composite(source_array, aoi, 45, (255, 255, 0), cache_key='img1')

    assert ('img1', 45) in service._rotated_image_cache


def test_clear_cache_for_removes_only_that_image(service, source_array, aoi):
    """clear_cache_for drops one image's rotations and keeps the rest."""
    service.create_composite(source_array, aoi, 45, (255, 255, 0), cache_key='img1')
    service.create_composite(source_array, aoi, 90, (255, 255, 0), cache_key='img2')

    service.clear_cache_for('img1')

    assert ('img1', 45) not in service._rotated_image_cache
    assert ('img2', 90) in service._rotated_image_cache

    service.clear_cache()
    assert service._rotated_image_cache == {}


def test_create_composite_invalid_aoi_returns_none(service, source_array):
    """An AOI without the required keys returns None instead of raising."""
    assert service.create_composite(source_array, {}, 0, (255, 255, 0)) is None


def test_zoomed_image_is_centered_on_aoi(service, source_array, aoi):
    """The zoomed crop covers the region around the AOI."""
    zoomed, aoi_pos = service.create_zoomed_aoi_image(source_array, aoi, 3, 0, (255, 255, 0), draw_circle=False)

    # 3x zoom crops radius*3 around the center: 120px on each side
    assert zoomed.shape[0] == 120
    assert zoomed.shape[1] == 120
    assert aoi_pos == (60, 60)
    # The green AOI patch sits at the center of the crop
    assert zoomed[60, 60, 1] == 255
