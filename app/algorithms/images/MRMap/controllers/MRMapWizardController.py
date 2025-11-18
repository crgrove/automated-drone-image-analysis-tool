"""
Wizard controller for MRMap algorithm.

Provides a simplified, guided interface for configuring MRMap detection parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup

from algorithms.AlgorithmController import AlgorithmController
from core.views.components.LabeledSlider import TextLabeledSlider
from algorithms.images.MRMap.views.MRMapWizard_ui import Ui_MRMapWizard


class MRMapWizardController(QWidget, Ui_MRMapWizard, AlgorithmController):
    """Wizard controller for MRMap algorithm."""

    def __init__(self, config, theme):
        """Initialize the wizard controller."""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults."""
        # Radio button group for complex scenes
        complex_group = QButtonGroup(self)
        complex_group.addButton(self.radioComplexNo)
        complex_group.addButton(self.radioComplexYes)

        # Aggressiveness slider with text labels matching mockup
        self.aggressivenessSlider = TextLabeledSlider(
            self,
            presets=["Very \nConservative", "Conservative", "Moderate", "Aggressive", "Very \nAggressive"]
        )
        placeholder = self.aggressivenessSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.aggressivenessSlider)

    def _read_ui_state(self):
        """Read current UI selections into simple values."""
        complex_scene = self.radioComplexYes.isChecked()
        aggr_index = self.aggressivenessSlider.value()
        aggr_label, aggr_value = self.aggressivenessSlider.getCurrentPreset()
        return complex_scene, aggr_index, aggr_label, aggr_value

    def get_options(self):
        """Get algorithm options."""
        options = dict()
        complex_scene, aggr_index, aggr_label, aggr_value = self._read_ui_state()

        # Map to threshold and other params based on aggressiveness
        # Index 0 (Very Conservative) = low threshold, Index 4 (Very Aggressive) = high threshold
        threshold_map = {
            0: 200,  # Very Conservative
            1: 150,  # Conservative
            2: 100,  # Moderate
            3: 50,  # Aggressive
            4: 10   # Very Aggressive
        }
        threshold = threshold_map.get(aggr_index, 50)

        # Set default segments and window (can be adjusted based on complexity)
        segments = 4 if complex_scene else 1
        window = 5

        # Service-expected fields
        options['threshold'] = threshold
        options['segments'] = segments
        options['window'] = window

        # Wizard fields retained for reference
        options['complex_scene'] = complex_scene
        options['aggressiveness_index'] = aggr_index
        options['aggressiveness_label'] = aggr_label
        options['aggressiveness_value'] = aggr_value

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
        if 'complex_scene' in options:
            complex_scene = options.get('complex_scene', False)
            self.radioComplexYes.setChecked(bool(complex_scene))
            self.radioComplexNo.setChecked(not bool(complex_scene))

        # Aggressiveness
        if 'aggressiveness_index' in options:
            aggr_index = options.get('aggressiveness_index')
            if isinstance(aggr_index, int):
                self.aggressivenessSlider.setValue(max(0, min(4, aggr_index)))
        elif 'threshold' in options:
            # Reverse map threshold to index
            threshold = int(options['threshold'])
            if threshold <= 25:
                index = 0  # Very Conservative
            elif threshold <= 45:
                index = 1  # Conservative
            elif threshold <= 55:
                index = 2  # Moderate
            elif threshold <= 70:
                index = 3  # Aggressive
            else:
                index = 4  # Very Aggressive
            self.aggressivenessSlider.setValue(index)
