"""
Base class for wizard pages.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePage(ABC):
    """Abstract base class for wizard pages.

    Each page manages its own UI and logic, but shares wizard_data
    with the main wizard coordinator. Provides a consistent interface
    for page lifecycle management.

    Attributes:
        wizard_data: Shared dictionary containing all wizard configuration data.
        settings_service: SettingsService instance for loading/saving preferences.
        dialog: The main ImageAnalysisGuide dialog instance (for accessing UI widgets).
    """

    def __init__(self, wizard_data: Dict[str, Any], settings_service, dialog):
        """Initialize the page.

        Args:
            wizard_data: Shared dictionary containing all wizard data.
            settings_service: SettingsService instance for loading/saving preferences.
            dialog: The main ImageAnalysisGuide dialog instance (for accessing UI widgets).
        """
        self.wizard_data = wizard_data
        self.settings_service = settings_service
        self.dialog = dialog

    @abstractmethod
    def setup_ui(self):
        """Initialize UI components for this page.

        Must be implemented by subclasses to set up page-specific UI elements.
        """
        pass

    @abstractmethod
    def connect_signals(self):
        """Connect UI signals to handlers.

        Must be implemented by subclasses to connect UI signals to appropriate
        handler methods.
        """
        pass

    @abstractmethod
    def load_data(self):
        """Load data from wizard_data or preferences into UI.

        Must be implemented by subclasses to populate UI with existing data
        from wizard_data or saved preferences.
        """
        pass

    def validate(self) -> bool:
        """Validate that the page is ready to proceed.

        Returns:
            True if page is valid and can proceed, False otherwise.
            Default implementation returns True.
        """
        return True

    def save_data(self):
        """Save data from UI into wizard_data.

        Default implementation does nothing. Subclasses should override
        to persist UI state to wizard_data.
        """
        pass

    def on_enter(self):
        """Called when the page is entered (shown).

        Default implementation does nothing. Subclasses can override to
        perform actions when the page becomes visible.
        """
        pass

    def on_exit(self):
        """Called when leaving the page.

        Default implementation does nothing. Subclasses can override to
        perform cleanup actions when leaving the page.
        """
        pass
