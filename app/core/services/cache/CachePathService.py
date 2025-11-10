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

    def check_and_prompt_for_caches(self, xml_path, parent_widget):
        """
        Check if cache directories exist, and if not, prompt user to locate them.
        
        Args:
            xml_path: Path to XML file (used to determine expected cache location)
            parent_widget: Parent widget for dialogs
            
        Returns:
            tuple: (alternative_cache_dir or None, bool indicating success)
        """
        try:
            from core.views.images.viewer.dialogs.CacheLocationDialog import CacheLocationDialog
            from PySide6.QtWidgets import QDialog

            # Get the expected cache directory from xml_path
            results_dir = Path(xml_path).parent
            thumbnail_cache_dir = results_dir / '.thumbnails'

            # Check which caches are missing (only thumbnails now - color/temp data is in XML)
            missing_caches = []
            if not thumbnail_cache_dir.exists():
                missing_caches.append('Thumbnails')

            # If all caches exist, no need to prompt
            if not missing_caches:
                return None, True

            # Show dialog to prompt user
            dialog = CacheLocationDialog(parent_widget, missing_caches)
            result = dialog.exec()

            if result == QDialog.Accepted:
                # User selected a cache folder
                selected_path = dialog.get_selected_path()
                if selected_path:
                    self.logger.info(f"Using cache from: {selected_path}")
                    return str(selected_path), True

            # User declined - proceed without cache
            return None, True

        except Exception as e:
            self.logger.error(f"Error checking caches: {e}")
            return None, True  # Continue anyway

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
                    self.logger.info(f"Using AOI thumbnail cache from: {thumbnail_cache_path}")

            # Update thumbnail controller for main image thumbnails (now unified in .thumbnails)
            if hasattr(viewer, 'thumbnail_controller') and viewer.thumbnail_controller:
                thumbnail_path = cache_dir / '.thumbnails'
                if thumbnail_path.exists():
                    # Store the alternative cache path for thumbnail loader to use
                    viewer.thumbnail_controller.alternative_cache_dir = str(cache_dir)
                    # If loader is already created, update it
                    if hasattr(viewer.thumbnail_controller, 'loader') and viewer.thumbnail_controller.loader:
                        viewer.thumbnail_controller.loader.results_dir = str(cache_dir)
                    self.logger.info(f"Using thumbnail cache from: {thumbnail_path}")

        except Exception as e:
            self.logger.error(f"Error updating cache paths: {e}")



