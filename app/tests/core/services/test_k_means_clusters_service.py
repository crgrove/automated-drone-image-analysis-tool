import pytest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from app.core.services.KMeansClustersService import KMeansClustersService  # Adjust the import according to your project structure
from app.core.services.LoggerService import LoggerService  # Adjust the import according to your project structure


@pytest.fixture
def mock_source_image():
    return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)


def test_kmeans_clusters_service_initialization():
    num_clusters = 5
    service = KMeansClustersService(num_clusters)
    assert service.num_clusters == num_clusters


def test_generateClusters(mock_source_image):
    num_clusters = 5
    service = KMeansClustersService(num_clusters)

    mock_labels = np.random.randint(0, num_clusters, mock_source_image.shape[:2])
    mock_centers = np.random.randint(0, 256, (num_clusters, 3), dtype=np.uint8)

    with patch("cv2.kmeans", return_value=(None, mock_labels, mock_centers)):
        result = service.generateClusters(mock_source_image)

        assert result.shape == mock_source_image.shape
        assert result.dtype == np.uint8
