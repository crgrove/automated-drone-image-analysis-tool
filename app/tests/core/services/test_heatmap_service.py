"""Unit tests for HeatmapService."""

import numpy as np
import pytest

from core.services.HeatmapService import HeatmapService


def _image(width=1000, height=800, centers=()):
    """Build an image dict with AOIs at the given pixel centers."""
    return {
        "width": width,
        "height": height,
        "areas_of_interest": [{"center": c} for c in centers],
    }


@pytest.fixture
def service():
    return HeatmapService()


def test_initial_state(service):
    assert service.is_valid() is False
    assert service.has_data() is False
    stats = service.get_stats()
    assert stats == {
        "totalImages": 0,
        "totalAois": 0,
        "skippedAois": 0,
        "gridSize": 200,
    }


def test_compute_heatmap_with_empty_list(service):
    service.compute_heatmap(images=[])
    assert service.is_valid() is True
    # Empty grid; no data
    assert service.has_data() is False
    assert service._grid.shape == (200, 200)
    assert service._grid.sum() == 0


def test_compute_heatmap_skips_images_without_aois(service):
    images = [
        _image(centers=[]),
        _image(centers=[(100, 100)]),
    ]
    service.compute_heatmap(images, gridSize=100)
    stats = service.get_stats()
    assert stats["totalImages"] == 1
    assert stats["totalAois"] == 1
    assert stats["skippedAois"] == 0
    assert stats["gridSize"] == 100


def test_compute_heatmap_skips_aois_without_dimensions(service):
    images = [
        {"width": None, "height": None, "areas_of_interest": [{"center": (1, 1)}]},
        {"width": 0, "height": 100, "areas_of_interest": [{"center": (1, 1)}]},
    ]
    service.compute_heatmap(images)
    stats = service.get_stats()
    assert stats["totalAois"] == 2
    assert stats["skippedAois"] == 2
    assert service.has_data() is False


def test_compute_heatmap_skips_aois_without_center(service):
    images = [
        {
            "width": 1000,
            "height": 800,
            "areas_of_interest": [{"center": None}, {"center": (100, 100)}],
        }
    ]
    service.compute_heatmap(images, gridSize=100)
    stats = service.get_stats()
    assert stats["totalAois"] == 2
    assert stats["skippedAois"] == 1


def test_compute_heatmap_has_data_when_points_valid(service):
    images = [_image(centers=[(100, 100), (200, 200), (300, 300)])]
    service.compute_heatmap(images, gridSize=100)
    assert service.has_data() is True
    assert service._grid.sum() > 0


def test_compute_heatmap_clamps_out_of_bounds_centers(service):
    # Centers outside image bounds should clamp to [0, 1] without error
    images = [_image(width=100, height=100, centers=[(-50, -50), (200, 200)])]
    service.compute_heatmap(images, gridSize=50)
    # Both points should land in corner bins (top-left and bottom-right)
    assert service._grid[0, 0] > 0 or service._grid[-1, -1] > 0


def test_invalidate_resets_state(service):
    service.compute_heatmap([_image(centers=[(10, 10)])])
    assert service.is_valid() is True

    service.invalidate()
    assert service.is_valid() is False
    assert service.has_data() is False
    assert service.get_stats()["totalAois"] == 0


def test_get_percentile_threshold_no_grid(service):
    assert service.get_percentile_threshold(50) == 0.0


def test_get_percentile_threshold_computed(service):
    service.compute_heatmap([_image(centers=[(100, 100)] * 10)], gridSize=50)
    p100 = service.get_percentile_threshold(100)
    p0 = service.get_percentile_threshold(0)
    assert p100 >= p0
    assert p100 > 0


def test_get_density_at_no_grid(service):
    assert service.get_density_at((50, 50), 100, 100) == 0.0


def test_get_density_at_invalid_dims(service):
    service.compute_heatmap([_image(centers=[(50, 50)])])
    assert service.get_density_at((50, 50), 0, 100) == 0.0
    assert service.get_density_at((50, 50), 100, 0) == 0.0


def test_get_density_at_returns_positive_near_cluster(service):
    # Cluster all AOIs near (100, 100) in a 1000x1000 image
    centers = [(100 + i, 100 + i) for i in range(20)]
    service.compute_heatmap([_image(width=1000, height=1000, centers=centers)], gridSize=100)

    near = service.get_density_at((100, 100), 1000, 1000)
    far = service.get_density_at((900, 900), 1000, 1000)
    assert near > far


def test_is_in_hot_zone_no_grid(service):
    assert service.is_in_hot_zone((10, 10), 100, 100, percentile=50) is False


def test_is_in_hot_zone_cluster_vs_cold(service):
    centers = [(100, 100)] * 30
    service.compute_heatmap([_image(width=1000, height=1000, centers=centers)], gridSize=100)

    # Point near cluster should be hot; far corner should not.
    assert service.is_in_hot_zone((100, 100), 1000, 1000, percentile=50) is True
    assert service.is_in_hot_zone((990, 990), 1000, 1000, percentile=99) is False


def test_generate_heatmap_image_no_grid(service):
    image, stats = service.generate_heatmap_image()
    assert image.shape == (200, 200, 3)
    assert image.dtype == np.uint8
    assert image.sum() == 0
    assert stats["totalAois"] == 0


def test_generate_heatmap_image_returns_bgr(service):
    service.compute_heatmap([_image(centers=[(100, 100)] * 5)], gridSize=50)
    image, stats = service.generate_heatmap_image()
    assert image.shape == (50, 50, 3)
    assert image.dtype == np.uint8
    assert stats["totalAois"] == 5
    assert stats["gridSize"] == 50


def test_generate_heatmap_image_applies_threshold_mask(service):
    centers = [(100, 100)] * 50
    service.compute_heatmap([_image(width=1000, height=1000, centers=centers)], gridSize=50)

    image_full, _ = service.generate_heatmap_image()
    image_thresh, _ = service.generate_heatmap_image(thresholdPercentile=90)

    # Threshold version should have large dim (gray) regions
    dim_mask = np.all(image_thresh == [40, 40, 40], axis=-1)
    assert dim_mask.sum() > 0
    # And it should differ from the unmasked image
    assert not np.array_equal(image_full, image_thresh)


def test_grid_size_presets_exist():
    assert HeatmapService.GRID_LOW == 100
    assert HeatmapService.GRID_MEDIUM == 200
    assert HeatmapService.GRID_HIGH == 400


def test_recompute_changes_grid_size(service):
    service.compute_heatmap([_image(centers=[(10, 10)])], gridSize=100)
    assert service._grid.shape == (100, 100)
    service.compute_heatmap([_image(centers=[(10, 10)])], gridSize=200)
    assert service._grid.shape == (200, 200)
