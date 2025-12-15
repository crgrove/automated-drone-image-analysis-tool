"""
Wizard controller for RX Anomaly algorithm.

Provides a simplified, guided interface for configuring RX anomaly detection parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from algorithms.AlgorithmController import AlgorithmController
from core.views.components.LabeledSlider import TextLabeledSlider
from algorithms.images.RXAnomaly.views.RXAnomalyWizard_ui import Ui_RXAnomalyWizard


class RXAnomalyWizardController(QWidget, Ui_RXAnomalyWizard, AlgorithmController):
    """Wizard controller for RX Anomaly algorithm.

    Provides a simplified, guided interface for configuring RX anomaly detection
    parameters. Maps user-friendly presets to algorithm-specific options.

    Attributes:
        theme: Theme name for UI styling.
        aggressivenessSlider: TextLabeledSlider for selecting detection aggressiveness.
    """

    def __init__(self, config, theme):
        """Initialize the wizard controller.

        Args:
            config: Algorithm configuration dictionary.
            theme: Theme name for UI styling.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults to match mockup.

        Creates and configures the aggressiveness slider with preset text labels
        and sets up the UI layout.
        """
        # Aggressiveness slider with preset text labels
        self.aggressivenessSlider = TextLabeledSlider(
            self,
            presets=["Very \nConservative", "Conservative", "Moderate", "Aggressive", "Very \nAggressive"],
        )
        placeholder = self.aggressivenessSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.aggressivenessSlider)
        # Default: Complex scenes = No (set in .ui); nothing else to wire

    def _read_ui_state(self):
        """Read current UI selections into simple values.

        Returns:
            Tuple containing (complex_scene, aggressiveness_index, aggressiveness_label).
        """
        aggr_index = self.aggressivenessSlider.value()
        aggr_label, _ = self.aggressivenessSlider.getCurrentPreset()
        complex_scene = self.radioComplexYes.isChecked()
        return complex_scene, aggr_index, aggr_label

    def get_options(self):
        """Get algorithm options.

        Converts UI state into algorithm-specific options dictionary.
        Maps aggressiveness presets to sensitivity values and complex scene
        selection to segment count.

        Returns:
            Dictionary containing algorithm options including sensitivity,
            segments, and wizard-specific metadata.
        """
        options = dict()
        complex_scene, aggr_index, aggr_label = self._read_ui_state()

        # Map aggressiveness text index to numeric sensitivity (best-guess mapping)
        sensitivity_map = {0: 9, 1: 7, 2: 5, 3: 3, 4: 1}
        sensitivity = sensitivity_map.get(aggr_index, 5)

        # Map complex scene to segments (best guess)
        segments = 4 if complex_scene else 1

        # Service-expected fields (matches non-wizard controller)
        options['sensitivity'] = sensitivity
        options['segments'] = segments

        # Additional wizard fields retained for reference
        options['complex_scene'] = complex_scene
        options['aggressiveness_index'] = aggr_index
        options['aggressiveness_label'] = aggr_label

        return options

    def validate(self):
        """Validate configuration.

        Returns:
            None, as all inputs are optional and have defaults.
        """
        # Always valid - no required inputs
        return None

    def load_options(self, options):
        """Load options into UI.

        Restores UI state from a previously saved options dictionary.

        Args:
            options: Dictionary containing algorithm options to load.
        """
        if not isinstance(options, dict):
            return
        # Complex scene
        if 'complex_scene' in options:
            complex_scene = bool(options.get('complex_scene'))
            self.radioComplexYes.setChecked(complex_scene)
            self.radioComplexNo.setChecked(not complex_scene)
        # Aggressiveness
        aggr_index = options.get('aggressiveness_index')
        if isinstance(aggr_index, int):
            self.aggressivenessSlider.setValue(max(0, min(4, aggr_index)))
