"""
Algorithm Parameters page for the Image Analysis Guide wizard.

This page dynamically loads and displays the algorithm-specific parameter widget
based on the algorithm selected in the previous page.
"""

from algorithms.images.ThermalAnomaly.controllers.ThermalAnomalyWizardController import ThermalAnomalyWizardController
from algorithms.images.ThermalRange.controllers.ThermalRangeWizardController import ThermalRangeWizardController
from algorithms.images.HSVColorRange.controllers.HSVColorRangeWizardController import HSVColorRangeWizardController
from algorithms.images.AIPersonDetector.controllers.AIPersonDetectorWizardController import AIPersonDetectorWizardController
from algorithms.images.MRMap.controllers.MRMapWizardController import MRMapWizardController
from algorithms.images.MatchedFilter.controllers.MatchedFilterWizardController import MatchedFilterWizardController
from algorithms.images.RXAnomaly.controllers.RXAnomalyWizardController import RXAnomalyWizardController
from algorithms.images.ColorRange.controllers.ColorRangeWizardController import ColorRangeWizardController
from algorithms.images.ThermalAnomaly.controllers.ThermalAnomalyController import ThermalAnomalyController
from algorithms.images.ThermalRange.controllers.ThermalRangeController import ThermalRangeController
from algorithms.images.HSVColorRange.controllers.HSVColorRangeController import HSVColorRangeController
from algorithms.images.AIPersonDetector.controllers.AIPersonDetectorController import AIPersonDetectorController
from algorithms.images.MRMap.controllers.MRMapController import MRMapController
from algorithms.images.MatchedFilter.controllers.MatchedFilterController import MatchedFilterController
from algorithms.images.RXAnomaly.controllers.RXAnomalyController import RXAnomalyController
from algorithms.images.ColorRange.controllers.ColorRangeController import ColorRangeController
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

"""****Import Algorithm Controllers (for fallback)****"""
"""****End Algorithm Import****"""

"""****Import Wizard Controllers****"""
"""****End Wizard Controller Import****"""


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
        selected_algorithm_label = self.wizard_data.get('algorithm')
        if not selected_algorithm_label:
            return

        # Find the algorithm config
        self.active_algorithm = None
        system = platform.system()
        for algo in self.algorithms:
            if system in algo['platforms'] and algo['label'] == selected_algorithm_label:
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
            if layout:
                layout.removeWidget(self.algorithm_widget)
            self.algorithm_widget.deleteLater()
            self.algorithm_widget = None

        try:
            # Try to use wizard controller first, fall back to regular controller
            wizard_controller_name = self.active_algorithm.get('wizard_controller')
            controller_class_name = self.active_algorithm['controller']

            theme = self.settings_service.get_setting('Theme', 'Dark')

            # Update the page title above the HR to be algorithm-specific
            try:
                page_title_widget = getattr(self.dialog, 'labelPage5Title_AlgorithmParameters', None)
                if page_title_widget is not None:
                    algo_label = self.active_algorithm.get('label', 'Algorithm')
                    page_title_widget.setText(f"{algo_label} Algorithm Settings")
            except Exception:
                # Best-effort only; ignore if not available
                pass

            # Debug logging
            logger = LoggerService()
            logger.info(
                f"Algorithm: {self.active_algorithm.get('name')}, "
                f"Wizard Controller: {wizard_controller_name}, "
                f"Regular Controller: {controller_class_name}"
            )

            # Prefer wizard controller if available
            cls = None
            if wizard_controller_name and wizard_controller_name in globals():
                cls = globals()[wizard_controller_name]
                logger.info(f"Using wizard controller: {cls}")

            # Fall back to regular controller if wizard controller not available
            if cls is None:
                if controller_class_name in globals():
                    cls = globals()[controller_class_name]
                    logger.info(f"Using regular controller: {cls}")
                else:
                    raise ValueError(f"Controller class '{controller_class_name}' not found in globals()")

            # Verify the class is callable
            if not callable(cls):
                raise ValueError(f"Class '{cls}' is not callable")

            logger.info(f"Instantiating controller: {cls} with config: {self.active_algorithm}, theme: {theme}")
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
