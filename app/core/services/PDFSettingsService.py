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
        """Initialize the PDF settings service."""
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
            dict: Dictionary with 'organization' and 'search_name' keys,
                  or empty dict if loading fails
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                    return {
                        'organization': settings.get('organization', ''),
                        'search_name': settings.get('search_name', '')
                    }
        except Exception:
            # If loading fails, return empty values
            pass
        
        return {'organization': '', 'search_name': ''}

    def save_settings(self, organization, search_name):
        """Save settings to config file.

        Args:
            organization (str): Organization name
            search_name (str): Search name

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            settings = {
                'organization': organization.strip(),
                'search_name': search_name.strip()
            }
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception:
            # If saving fails, return False
            return False

