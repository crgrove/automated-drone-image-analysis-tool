import numpy as np
import cv2
from core.services.LoggerService import LoggerService


class KMeansClustersService:
    """Service to generate an image with a limited number of colors using K-Means clustering."""

    def __init__(self, clusters):
        """
        Initialize the KMeansClustersService with the specified number of color clusters.

        Args:
            clusters (int): The number of color clusters for the K-Means Clustering algorithm.
        """
        self.logger = LoggerService()
        self.num_clusters = clusters

    def generateClusters(self, src):
        """
        Process an image and return a version with the specified number of color clusters.

        Args:
            src (numpy.ndarray): The input image as a numpy array.

        Returns:
            numpy.ndarray: The processed image with a reduced number of colors based on the specified clusters.

        Raises:
            Exception: If an error occurs during K-Means clustering.
        """
        try:
            Z = src.reshape((-1, 3))

            # Convert to np.float32
            Z = np.float32(Z)

            # Define criteria, number of clusters (K), and apply k-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 3, 0.2)
            ret, label, center = cv2.kmeans(Z, self.num_clusters, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)

            # Convert back into uint8 and reshape
            center = np.uint8(center)
            res = center[label.flatten()]
            res2 = res.reshape(src.shape)
            return res2
        except Exception as e:
            self.logger.error(e)
