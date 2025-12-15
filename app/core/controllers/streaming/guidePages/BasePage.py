"""Base class for streaming wizard pages."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BasePage(ABC):
    """Abstract base class for streaming setup pages."""

    def __init__(self, wizard_data: Dict[str, Any], settings_service, dialog):
        self.wizard_data = wizard_data
        self.settings_service = settings_service
        self.dialog = dialog

    @abstractmethod
    def setup_ui(self) -> None:
        """Initialize UI elements for the page."""

    @abstractmethod
    def connect_signals(self) -> None:
        """Connect UI signals to handlers."""

    @abstractmethod
    def load_data(self) -> None:
        """Load existing data into the UI."""

    def validate(self) -> bool:
        return True

    def save_data(self) -> None:
        """Persist UI data into the shared wizard_data dict."""

    def on_enter(self) -> None:
        """Invoked when a page becomes visible."""

    def on_exit(self) -> None:
        """Invoked before leaving the page."""
