"""
CachePathService - Manages cache directory detection and path updates.

This service handles checking for cache directories and updating cache paths
for controllers when alternative cache locations are provided.
"""

from pathlib import Path
from core.services.LoggerService import LoggerService


class CachePathService:
    """
    Service for managing cache directory paths.

    Handles detection of cache directories and updating controller cache paths.
    """

    def __init__(self):
        """Initialize the cache path service."""
        self.logger = LoggerService()

    def get_missing_caches(self, xml_path):
        """
        Check which cache directories are missing.

        Args:
            xml_path: Path to XML file (used to determine expected cache location)

        Returns:
            list: Names of missing cache directories (empty if all present).
        """
        try:
            results_dir = Path(xml_path).parent
            thumbnail_cache_dir = results_dir / '.thumbnails'

            missing_caches = []
            if not thumbnail_cache_dir.exists():
                missing_caches.append('Thumbnails')

            return missing_caches

        except Exception as e:
            self.logger.error(f"Error checking caches: {e}")
            return []

    def update_cache_paths(self, cache_dir, viewer):
        """
        Update cache directory paths for all controllers to use an alternative location.

        Args:
            cache_dir: Path to the directory containing cache subdirectories
            viewer: Viewer instance to update controllers on
        """
        try:
            # Update gallery controller's model cache paths
            if hasattr(viewer, 'gallery_controller') and viewer.gallery_controller:
                model = viewer.gallery_controller.model

                # Update dataset directory reference
                model.dataset_dir = cache_dir

                # Update thumbnail loader cache path
                thumbnail_cache_path = cache_dir / '.thumbnails'
                if thumbnail_cache_path.exists() and hasattr(model, 'thumbnail_loader'):
                    model.thumbnail_loader.set_dataset_cache_dir(str(thumbnail_cache_path))

            # Update thumbnail controller for main image thumbnails (now unified in .thumbnails)
            if hasattr(viewer, 'thumbnail_controller') and viewer.thumbnail_controller:
                thumbnail_path = cache_dir / '.thumbnails'
                if thumbnail_path.exists():
                    # Store the alternative cache path for thumbnail loader to use
                    viewer.thumbnail_controller.alternative_cache_dir = str(cache_dir)
                    # If loader is already created, update it
                    if hasattr(viewer.thumbnail_controller, 'loader') and viewer.thumbnail_controller.loader:
                        viewer.thumbnail_controller.loader.results_dir = str(cache_dir)

        except Exception as e:
            self.logger.error(f"Error updating cache paths: {e}")
