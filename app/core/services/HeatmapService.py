# HeatmapService.py
# Computes and caches a 2D density heatmap of AOI positions across all images.
# Used for spatial filtering of AOIs based on detection density patterns.

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter


class HeatmapService:
    """Service for computing and querying AOI detection density heatmaps.

    Builds a normalized 2D density grid from AOI center positions across all images.
    The grid is cached and used for spatial filtering (hot zone detection) and
    visualization in the heatmap viewer dialog.
    """

    # Grid resolution presets
    GRID_LOW = 100
    GRID_MEDIUM = 200
    GRID_HIGH = 400

    def __init__(self):
        self._grid = None
        self._gridSize = 200
        self._totalAois = 0
        self._totalImages = 0
        self._skippedAois = 0
        self._lastImages = None

    def compute_heatmap(self, images, gridSize=200):
        """Compute the heatmap grid from all AOIs across all images.

        Normalizes AOI center positions to [0, 1] using each image's width/height,
        builds a 2D histogram, and applies Gaussian smoothing.

        Args:
                images: List of image dicts from the viewer (must have 'width', 'height',
                        and 'areas_of_interest' keys).
                gridSize: Number of bins per dimension (default 200).
        """
        self._gridSize = gridSize
        self._lastImages = images
        self._totalImages = 0
        self._totalAois = 0
        self._skippedAois = 0

        normalizedPoints = []

        for image in images:
            width = image.get('width')
            height = image.get('height')
            aois = image.get('areas_of_interest', [])

            if not aois:
                continue

            self._totalImages += 1
            self._totalAois += len(aois)

            if width is None or height is None or width <= 0 or height <= 0:
                self._skippedAois += len(aois)
                continue

            for aoi in aois:
                center = aoi.get('center')
                if center is None:
                    self._skippedAois += 1
                    continue

                cx, cy = center
                normX = max(0.0, min(1.0, cx / width))
                normY = max(0.0, min(1.0, cy / height))
                normalizedPoints.append([normX, normY])

        if not normalizedPoints:
            self._grid = np.zeros((gridSize, gridSize), dtype=np.float64)
            return

        coords = np.array(normalizedPoints)
        sigma = gridSize / 60.0

        histogram, _, _ = np.histogram2d(
            coords[:, 0],
            coords[:, 1],
            bins=gridSize,
            range=[[0, 1], [0, 1]]
        )

        # Transpose: histogram2d returns (x, y) but image convention is (row, col) = (y, x)
        histogram = histogram.T

        self._grid = gaussian_filter(histogram, sigma=sigma)

    def is_valid(self):
        """Check whether a heatmap grid has been computed.

        Returns:
                True if a valid grid exists.
        """
        return self._grid is not None

    def has_data(self):
        """Check whether the heatmap has meaningful density data.

        Returns True only if the grid was computed and at least some AOIs
        had valid dimensions and positions. Returns False if never computed
        or if all AOIs were skipped due to missing dimensions/centers.
        """
        if self._grid is None:
            return False
        if self._totalAois == 0:
            return False
        return self._skippedAois < self._totalAois

    def invalidate(self):
        """Clear the cached heatmap grid."""
        self._grid = None
        self._lastImages = None
        self._totalAois = 0
        self._totalImages = 0
        self._skippedAois = 0

    def get_percentile_threshold(self, percentile):
        """Compute the density value at the given percentile.

        Args:
                percentile: Percentile value (0-100).

        Returns:
                The density value at the given percentile, or 0 if no grid exists.
        """
        if self._grid is None:
            return 0.0
        return float(np.percentile(self._grid, percentile))

    def get_density_at(self, center, imageWidth, imageHeight):
        """Look up the smoothed density value at a normalized AOI position.

        Args:
                center: (x, y) pixel coordinates of the AOI center.
                imageWidth: Width of the source image in pixels.
                imageHeight: Height of the source image in pixels.

        Returns:
                Density value at the position, or 0 if grid is not computed.
        """
        if self._grid is None or imageWidth <= 0 or imageHeight <= 0:
            return 0.0

        cx, cy = center
        normX = max(0.0, min(1.0, cx / imageWidth))
        normY = max(0.0, min(1.0, cy / imageHeight))

        gridSize = self._grid.shape[0]
        col = min(int(normX * gridSize), gridSize - 1)
        row = min(int(normY * gridSize), gridSize - 1)

        return float(self._grid[row, col])

    def is_in_hot_zone(self, center, imageWidth, imageHeight, percentile):
        """Check whether an AOI falls in a high-density zone.

        Args:
                center: (x, y) pixel coordinates of the AOI center.
                imageWidth: Width of the source image in pixels.
                imageHeight: Height of the source image in pixels.
                percentile: Threshold percentile (0-100).

        Returns:
                True if the density at the AOI position exceeds the percentile threshold.
        """
        if self._grid is None:
            return False

        threshold = self.get_percentile_threshold(percentile)
        density = self.get_density_at(center, imageWidth, imageHeight)
        return density > threshold

    def generate_heatmap_image(self, gridSize=None, thresholdPercentile=None):
        """Generate a BGR heatmap image with optional threshold mask overlay.

        Args:
                gridSize: Grid resolution to use. If different from cached, recomputes.
                        Pass None to use current cached grid.
                thresholdPercentile: If provided, dims areas below the threshold.
                        Value 0-100.

        Returns:
                Tuple of (BGR image as numpy array, stats dict).
                Stats dict has 'totalImages', 'totalAois', 'skippedAois', 'gridSize'.
        """
        if self._grid is None:
            # Return a blank image
            size = gridSize or 200
            blank = np.zeros((size, size, 3), dtype=np.uint8)
            stats = {
                'totalImages': 0,
                'totalAois': 0,
                'skippedAois': 0,
                'gridSize': size
            }
            return blank, stats

        # Normalize to 0-255
        normalized = np.zeros_like(self._grid, dtype=np.uint8)
        if self._grid.max() > 0:
            cv2.normalize(self._grid, normalized, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        colorMapped = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)

        # Apply threshold mask if specified
        if thresholdPercentile is not None and thresholdPercentile > 0:
            threshold = self.get_percentile_threshold(thresholdPercentile)
            mask = self._grid <= threshold
            # Dim below-threshold areas: blend with dark gray
            dimColor = np.array([40, 40, 40], dtype=np.uint8)
            colorMapped[mask] = dimColor

        stats = {
            'totalImages': self._totalImages,
            'totalAois': self._totalAois,
            'skippedAois': self._skippedAois,
            'gridSize': self._gridSize
        }

        return colorMapped, stats

    def get_stats(self):
        """Get statistics about the current heatmap.

        Returns:
                Dict with 'totalImages', 'totalAois', 'skippedAois', 'gridSize'.
        """
        return {
            'totalImages': self._totalImages,
            'totalAois': self._totalAois,
            'skippedAois': self._skippedAois,
            'gridSize': self._gridSize
        }
