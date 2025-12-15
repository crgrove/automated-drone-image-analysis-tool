"""
Wizard controller for Thermal Anomaly algorithm.

Builds the UI to match the Temperature Anomaly mockups:
- Complex scenes Yes/No
- Anomaly type: Warmer / Cooler / Both
- Aggressiveness slider with labeled presets and an explanatory note
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup

from algorithms.AlgorithmController import AlgorithmController
from core.views.components.LabeledSlider import TextLabeledSlider
from algorithms.images.ThermalAnomaly.views.ThermalAnomalyWizard_ui import Ui_ThermalAnomalyWizard


class ThermalAnomalyWizardController(QWidget, Ui_ThermalAnomalyWizard, AlgorithmController):
    """Wizard controller for Thermal Anomaly algorithm."""

    def __init__(self, config, theme):
        """Initialize the wizard controller."""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme
        self.config = config

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults."""
        # Radio button groups (for mutual exclusivity)
        complex_group = QButtonGroup(self)
        complex_group.addButton(self.radioComplexNo)
        complex_group.addButton(self.radioComplexYes)

        type_group = QButtonGroup(self)
        type_group.addButton(self.radioTypeHot)
        type_group.addButton(self.radioTypeCold)
        type_group.addButton(self.radioTypeBoth)

        # Labeled preset slider (Very Conservative .. Very Aggressive)
        # Allow labels to be overridden from config; default to desired set
        default_labels = [
            "Very \nConservative", "Conservative", "Moderate",
            "Aggressive", "Very \nAggressive"
        ]
        labels = self.config.get('aggressiveness_labels', default_labels)
        # Add space between "Very" and next word with line break if not already present
        labels = [label.replace("Very\n", "Very \n") if "\n" in label and "Very \n" not in label else label for label in labels]
        # Pass presets to constructor so multiline is detected at init time (like RXAnomaly)
        self.aggressivenessSlider = TextLabeledSlider(self, presets=labels)
        # Put slider into placeholder
        placeholder = self.aggressivenessSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.aggressivenessSlider)

    def _read_ui_state(self):
        """Read current UI selections into simple values."""
        complex_scene = self.radioComplexYes.isChecked()
        if self.radioTypeHot.isChecked():
            anomaly_type = 'Hot'
        elif self.radioTypeCold.isChecked():
            anomaly_type = 'Cold'
        else:
            anomaly_type = 'Both'
        aggr_index = self.aggressivenessSlider.value()
        aggr_label, aggr_value = self.aggressivenessSlider.getCurrentPreset()
        return complex_scene, anomaly_type, aggr_index, aggr_label, aggr_value

    def get_options(self):
        """Get algorithm options mapped to service-expected keys (like non-wizard)."""
        options = dict()
        complex_scene, anomaly_type, aggr_index, aggr_label, _ = self._read_ui_state()

        # Map aggressiveness index (0..4) to standard deviation threshold
        # Threshold is the width of the range (in standard deviations) that can be labeled as an anomaly
        threshold_map = {0: 8, 1: 6, 2: 4, 3: 2, 4: 1}
        threshold = threshold_map.get(aggr_index, 4)

        # Map complex scene to segments (best guess)
        segments = 4 if complex_scene else 1

        # Map anomaly_type to service 'type' values
        type_map = {'Hot': 'Hot', 'Cold': 'Cold', 'Both': 'Both'}
        type_value = type_map.get(anomaly_type, 'Both')

        # Service-expected keys
        options['threshold'] = threshold
        options['segments'] = segments
        options['type'] = type_value

        # Retain wizard fields for reference
        options['complex_scene'] = complex_scene
        options['anomaly_type'] = anomaly_type
        options['aggressiveness_index'] = aggr_index
        options['aggressiveness_label'] = aggr_label

        return options

    def validate(self):
        """Validate configuration."""
        # Always valid - no required inputs
        return None

    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return

        # Complex scene
        complex_scene = options.get('complex_scene', False)
        self.radioComplexYes.setChecked(bool(complex_scene))
        self.radioComplexNo.setChecked(not bool(complex_scene))

        # Anomaly type
        anomaly_type = options.get('anomaly_type', 'Both')
        if anomaly_type == 'Hot':
            self.radioTypeHot.setChecked(True)
        elif anomaly_type == 'Cold':
            self.radioTypeCold.setChecked(True)
        else:
            self.radioTypeBoth.setChecked(True)

        # Aggressiveness
        aggr_index = options.get('aggressiveness_index')
        if isinstance(aggr_index, int):
            self.aggressivenessSlider.setValue(max(0, min(4, aggr_index)))
