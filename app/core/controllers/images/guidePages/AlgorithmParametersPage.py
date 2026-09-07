"""
Algorithm Parameters page for the Image Analysis Guide wizard.

This page dynamically loads and displays the algorithm-specific parameter widget
based on the algorithm selected in the previous page.
"""

from core.services.LoggerService import LoggerService
import os
import sys
import pathlib
import platform
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

from .BasePage import BasePage
from core.services.ConfigService import ConfigService
from core.services.SettingsService import SettingsService
from helpers.WidgetHelper import retire_widget

# Algorithm and wizard controllers are NOT imported here. They are resolved
# from algorithms.conf by ConfigService.resolve_image_algorithm_class, so a
# new algorithm needs a config entry and nothing else - the eighteen imports
# that used to sit here existed only to populate globals() for a lookup.


class AlgorithmParametersPage(BasePage):
    """Page for configuring algorithm-specific parameters."""

    def __init__(self, wizard_data, settings_service, dialog):
        """Initialize the page."""
        super().__init__(wizard_data, settings_service, dialog)
        self.algorithm_widget = None
        self.active_algorithm = None
        self.algorithms = []
        self._last_algorithm_name = None  # Track the last algorithm we loaded
        self._load_algorithms()

    def _load_algorithms(self):
        """Load algorithm configurations from algorithms.conf."""
        # Get program root directory (app/)
        if getattr(sys, 'frozen', False):
            # Running from a PyInstaller bundle
            app_root = sys._MEIPASS
        else:
            # Running from source code
            app_root = str(pathlib.Path(__file__).resolve().parents[4])
        config_path = os.path.join(app_root, 'algorithms.conf')
        config_service = ConfigService(config_path)
        self.algorithms = config_service.get_algorithms()

    def setup_ui(self):
        """Initialize UI components."""
        # The UI is set up in on_enter when we know which algorithm is selected
        pass

    def connect_signals(self):
        """Connect UI signals to handlers."""
        # Algorithm widget signals are connected when the widget is loaded
        pass

    def load_data(self):
        """Load algorithm parameters if available."""
        # Parameters are loaded when the algorithm widget is created
        pass

    def validate(self) -> bool:
        """Validate that algorithm parameters are valid."""
        if not self.algorithm_widget:
            return False

        # Use the algorithm widget's validation
        validation_error = self.algorithm_widget.validate()
        if validation_error:
            return False

        return True

    def save_data(self):
        """Save algorithm parameters to wizard_data."""
        if self.algorithm_widget and self.active_algorithm:
            # Get options from the algorithm widget
            options = self.algorithm_widget.get_options()
            self.wizard_data['algorithm_options'] = options
            self.wizard_data['algorithm_config'] = self.active_algorithm

    def on_enter(self):
        """Called when entering the page."""
        # Get the selected algorithm from wizard_data
        selected_algorithm = self.wizard_data.get('algorithm')
        if not selected_algorithm:
            return

        # Find the algorithm config. The name is the identity; the label is
        # accepted too, for wizard data built before the switch to stable
        # names (the same dual match BatchCLI._resolve_algorithm makes).
        # Matching on the label alone meant a translated selection page
        # would find no algorithm at all.
        self.active_algorithm = None
        system = platform.system()
        for algo in self.algorithms:
            # The platform filter stays: without it a Windows-only thermal
            # algorithm becomes loadable on macOS.
            if system in algo['platforms'] and selected_algorithm in (
                    algo.get('name'), algo.get('label')):
                self.active_algorithm = algo
                break

        if not self.active_algorithm:
            return

        # Load the algorithm widget
        self._load_algorithm_widget()

    def on_exit(self):
        """Called when leaving the page."""
        # Save algorithm parameters
        self.save_data()

    def _load_algorithm_widget(self):
        """Load the algorithm-specific widget based on the selected algorithm."""
        if not self.active_algorithm:
            return

        current_algorithm_name = self.active_algorithm.get('name')

        # Check if we already have a widget for this algorithm
        # Only recreate if the algorithm has changed
        if self.algorithm_widget and self._last_algorithm_name == current_algorithm_name:
            # Algorithm hasn't changed, widget is already loaded - keep it
            return

        # Clear existing widget (only if algorithm changed or no widget exists)
        if self.algorithm_widget:
            # Remove from layout
            layout = self.dialog.algorithmParametersContainer.layout()
            retire_widget(self.algorithm_widget, layout)
            self.algorithm_widget = None

        try:
            # Try to use wizard controller first, fall back to regular controller
            wizard_controller_name = self.active_algorithm.get('wizard_controller')

            theme = self.settings_service.get_setting('Theme', 'Dark')

            # Update the page title above the HR to be algorithm-specific
            try:
                page_title_widget = getattr(self.dialog, 'labelPage5Title_AlgorithmParameters', None)
                if page_title_widget is not None:
                    # A config value cannot be extracted for translation,
                    # so the label passes through untranslated inside a
                    # translated sentence. Noted rather than wrapped in
                    # tr(): tr() over a runtime string is a no-op that
                    # reads as compliance.
                    algo_label = self.active_algorithm.get('label', 'Algorithm')
                    page_title_widget.setText(
                        self.tr("{algorithm} Algorithm Settings").format(algorithm=algo_label)
                    )
            except Exception:
                # Best-effort only; ignore if not available
                pass

            logger = LoggerService()

            # Prefer the wizard controller; fall back to the algorithm's
            # ordinary controller. Both are imported by dotted path from
            # the config, so the set of available algorithms is what
            # algorithms.conf says it is.
            cls = None
            if wizard_controller_name:
                try:
                    cls = ConfigService.resolve_image_algorithm_class(
                        self.active_algorithm, 'wizard_controller')
                except Exception as exc:
                    # A missing wizard controller is recoverable - the
                    # ordinary controller renders the same options - but it
                    # must be said, or the fallback looks deliberate.
                    logger.error(
                        f"Wizard controller unavailable for "
                        f"{current_algorithm_name}: {exc}")
            if cls is None:
                # No try/except: with neither controller resolvable there is
                # nothing to show, and the handler below renders the error
                # to the operator.
                cls = ConfigService.resolve_image_algorithm_class(
                    self.active_algorithm, 'controller')

            # logger.info(f"Instantiating controller: {cls} with config: {self.active_algorithm}, theme: {theme}")
            # Create the algorithm widget
            self.algorithm_widget = cls(self.active_algorithm, theme)

            # Track which algorithm we just loaded
            self._last_algorithm_name = current_algorithm_name

            # Add to the container layout
            container = self.dialog.algorithmParametersContainer
            layout = container.layout()
            if layout is None:
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(self.algorithm_widget)

            # Connect validation_changed signal if the widget has it (for color detectors)
            if hasattr(self.algorithm_widget, 'validation_changed'):
                self.algorithm_widget.validation_changed.connect(self._on_validation_changed)

            # Only load options if they match the current algorithm
            saved_algorithm_config = self.wizard_data.get('algorithm_config')
            if (saved_algorithm_config and
                    saved_algorithm_config.get('name') == current_algorithm_name and
                    'algorithm_options' in self.wizard_data):
                self.algorithm_widget.load_options(self.wizard_data['algorithm_options'])
            else:
                # Clear options for different algorithm
                if 'algorithm_options' in self.wizard_data:
                    del self.wizard_data['algorithm_options']
                if 'algorithm_config' in self.wizard_data:
                    del self.wizard_data['algorithm_config']

        except Exception as e:
            # Log error and show a message
            logger = LoggerService()
            logger.error(f"Error loading algorithm widget: {e}")

            # Show error label
            error_label = QLabel(f"Error loading algorithm parameters: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red;")

            container = self.dialog.algorithmParametersContainer
            layout = container.layout()
            if layout is None:
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(error_label)

    def _on_validation_changed(self):
        """Handle validation state change from algorithm widget (e.g., when color rows are added/removed)."""
        # Trigger navigation button update to reflect new validation state
        if hasattr(self.dialog, '_update_navigation_buttons'):
            self.dialog._update_navigation_buttons()
