"""
PDFSettingsService - Handles persistence of PDF export settings.

This service manages loading and saving of PDF export preferences
(organization name, search name) to a local configuration file.
"""

import os
import json


class PDFSettingsService:
    """Service for managing PDF export settings persistence."""

    def __init__(self):
        """
        Initialize the PDF settings service.

        Sets up the service and determines the path to the configuration file.
        """
        self.config_path = self._get_config_path()

    def _get_config_path(self):
        """Get the path to the PDF export config file.

        Returns:
            str: Path to the config JSON file
        """
        # Store config in user's home directory
        config_dir = os.path.join(os.path.expanduser("~"), ".adiat")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "pdf_export_settings.json")

    def load_settings(self):
        """Load previously saved settings from config file.

        Returns:
            dict: Dictionary with persisted PDF export settings
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                    return {
                        'organization': settings.get('organization', ''),
                        'search_name': settings.get('search_name', ''),
                        'include_images_without_flagged_aois': settings.get('include_images_without_flagged_aois', False),
                        'map_tile_source': settings.get('map_tile_source', 'map')
                    }
        except Exception:
            # If loading fails, return empty values
            pass

        return {
            'organization': '',
            'search_name': '',
            'include_images_without_flagged_aois': False,
            'map_tile_source': 'map'
        }

    def save_settings(self, organization, search_name, include_images_without_flagged_aois=False, map_tile_source='map'):
        """Save settings to config file.

        Args:
            organization (str): Organization name
            search_name (str): Search name
            include_images_without_flagged_aois (bool): Whether to include images without flagged AOIs
            map_tile_source (str): Tile source for overview map ('map' or 'satellite')

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            settings = {
                'organization': organization.strip(),
                'search_name': search_name.strip(),
                'include_images_without_flagged_aois': include_images_without_flagged_aois,
                'map_tile_source': map_tile_source if map_tile_source in ('map', 'satellite') else 'map'
            }
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception:
            # If saving fails, return False
            return False
