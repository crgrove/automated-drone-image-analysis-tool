"""
Tests for AOIThumbnailService.

Covers generation of zoomed AOI images used by map exports.
"""

import os
from unittest.mock import MagicMock

import numpy as np
import pytest
from PIL import Image

from core.services.export.AOIThumbnailService import AOIThumbnailService


@pytest.fixture
def source_image(tmp_path):
    """Create a source image with a distinct patch where the AOI sits."""
    array = np.zeros((600, 800, 3), dtype=np.uint8)
    array[290:310, 390:410] = (0, 255, 0)
    path = tmp_path / "IMG_0001.jpg"
    Image.fromarray(array).save(path)
    return str(path)


@pytest.fixture
def service():
    """Provide a service instance and clean up its temp directory afterwards."""
    svc = AOIThumbnailService(logger=MagicMock())
    yield svc
    svc.cleanup()


def test_generate_thumbnail_creates_file(service, source_image):
    """A thumbnail is written to disk for a valid AOI."""
    path = service.generate_thumbnail(source_image, {'center': (400, 300), 'radius': 20})

    assert path is not None
    assert os.path.exists(path)
    assert path.endswith('.jpg')


def test_generate_thumbnail_is_zoomed_in(service, source_image):
    """The generated image covers only the region around the AOI, not the whole image."""
    path = service.generate_thumbnail(source_image, {'center': (400, 300), 'radius': 20})

    with Image.open(path) as generated:
        width, height = generated.size

    # Crop is radius * DEFAULT_CONTEXT_MULTIPLIER on each side, then scaled up to
    # at least MIN_OUTPUT_SIZE, so it must be square and within the output bounds.
    assert width == height
    assert AOIThumbnailService.MIN_OUTPUT_SIZE <= width <= AOIThumbnailService.MAX_OUTPUT_SIZE


def test_generate_thumbnail_clamps_to_image_bounds(service, source_image):
    """An AOI near the edge still produces an image."""
    path = service.generate_thumbnail(source_image, {'center': (5, 5), 'radius': 30})

    assert path is not None
    assert os.path.exists(path)


def test_generate_thumbnail_large_aoi_is_capped(service, source_image):
    """A large AOI crop is scaled down to the maximum output size."""
    path = service.generate_thumbnail(source_image, {'center': (400, 300), 'radius': 400})

    with Image.open(path) as generated:
        assert max(generated.size) <= AOIThumbnailService.MAX_OUTPUT_SIZE


def test_generate_thumbnail_uses_output_name(service, source_image):
    """The requested output name is used (sanitized) for the generated file."""
    path = service.generate_thumbnail(
        source_image, {'center': (400, 300), 'radius': 20}, output_name="IMG_0001_AOI2_closeup"
    )

    assert os.path.basename(path) == "IMG_0001_AOI2_closeup.jpg"


def test_generate_thumbnail_unique_names(service, source_image):
    """Repeated generation with the same name does not overwrite the previous file."""
    first = service.generate_thumbnail(source_image, {'center': (400, 300), 'radius': 20}, output_name="dup")
    second = service.generate_thumbnail(source_image, {'center': (200, 200), 'radius': 20}, output_name="dup")

    assert first != second
    assert os.path.exists(first)
    assert os.path.exists(second)


def test_generate_thumbnail_missing_file(service):
    """A missing source image returns None instead of raising."""
    assert service.generate_thumbnail("/does/not/exist.jpg", {'center': (10, 10), 'radius': 5}) is None


def test_generate_thumbnail_missing_center(service, source_image):
    """An AOI without a center returns None."""
    assert service.generate_thumbnail(source_image, {'radius': 5}) is None


def test_generate_thumbnail_center_outside_image(service, source_image):
    """An AOI center outside the image bounds returns None."""
    assert service.generate_thumbnail(source_image, {'center': (5000, 5000), 'radius': 10}) is None


def test_generate_thumbnail_custom_output_dir(tmp_path, source_image):
    """A caller-supplied output directory is used and left in place by cleanup."""
    output_dir = tmp_path / "thumbs"
    svc = AOIThumbnailService(output_dir=str(output_dir), logger=MagicMock())

    path = svc.generate_thumbnail(source_image, {'center': (400, 300), 'radius': 20})
    assert os.path.dirname(path) == str(output_dir)

    svc.cleanup()
    assert output_dir.exists()  # Not owned by the service, so it is preserved


def test_cleanup_removes_temp_directory(source_image):
    """Cleanup removes the temporary directory the service created."""
    svc = AOIThumbnailService(logger=MagicMock())
    path = svc.generate_thumbnail(source_image, {'center': (400, 300), 'radius': 20})
    temp_dir = os.path.dirname(path)

    svc.cleanup()

    assert not os.path.exists(temp_dir)


def test_cleanup_is_idempotent(source_image):
    """Cleanup can be called repeatedly without error."""
    svc = AOIThumbnailService(logger=MagicMock())
    svc.generate_thumbnail(source_image, {'center': (400, 300), 'radius': 20})
    svc.cleanup()
    svc.cleanup()
