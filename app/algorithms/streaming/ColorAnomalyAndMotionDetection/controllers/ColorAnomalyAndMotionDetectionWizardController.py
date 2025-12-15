"""
Wizard controller for Color Anomaly & Motion Detection algorithm.

Provides a simplified, guided interface for configuring combined detection.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup
from PySide6.QtCore import Qt, Signal

from algorithms.streaming.ColorAnomalyAndMotionDetection.views.ColorAnomalyAndMotionDetectionWizard_ui import Ui_ColorAnomalyAndMotionDetectionWizard
from core.views.components.LabeledSlider import TextLabeledSlider


class ColorAnomalyAndMotionDetectionWizardController(QWidget, Ui_ColorAnomalyAndMotionDetectionWizard):
    """Wizard controller for Color Anomaly & Motion Detection algorithm."""

    # Signal emitted when validation state changes
    validation_changed = Signal()

    def __init__(self, config, theme):
        """Initialize the wizard controller.

        Args:
            config: Algorithm configuration dictionary.
            theme: Theme name for UI styling.
        """
        super().__init__()
        self.config = config
        self.theme = theme
        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Connect signals and set defaults."""
        # Motion detection yes/no radio buttons
        motion_group = QButtonGroup(self)
        motion_group.addButton(self.radioMotionNo)
        motion_group.addButton(self.radioMotionYes)
        self.radioMotionNo.setChecked(True)  # Default to No

        # Color detection checkbox
        self.enableColorCheckBox.setChecked(True)

        # Aggressiveness slider with preset text labels
        self.aggressivenessSlider = TextLabeledSlider(
            self,
            presets=["Very \nConservative", "Conservative", "Moderate", "Aggressive", "Very \nAggressive"],
        )
        placeholder = self.aggressivenessSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.aggressivenessSlider)

        # Set default to Moderate (index 2)
        self.aggressivenessSlider.setValue(2)

    def get_options(self):
        """Get algorithm options.

        Converts UI state into algorithm-specific options dictionary.
        Maps aggressiveness presets to color_rarity_percentile values.

        Returns:
            Dictionary containing algorithm options including color_rarity_percentile,
            and wizard-specific metadata.
        """
        options = {
            'enable_motion': self.radioMotionYes.isChecked(),
            'enable_color_quantization': self.enableColorCheckBox.isChecked(),
            'motion_algorithm': 'MOG2 Background',  # Default algorithm
        }

        # Map aggressiveness index to color_rarity_percentile
        # Lower percentile = more conservative (only very rare colors, fewer detections)
        # Higher percentile = more aggressive (includes more common colors, more detections)
        aggr_index = self.aggressivenessSlider.value()
        aggr_label, _ = self.aggressivenessSlider.getCurrentPreset()

        # Map aggressiveness index (0-4) to percentile values
        # Very Conservative (0) -> 5 (only very rare colors, fewer detections)
        # Conservative (1) -> 15
        # Moderate (2) -> 30 (default)
        # Aggressive (3) -> 50
        # Very Aggressive (4) -> 80 (includes more common colors, more detections)
        percentile_map = {0: 5.0, 1: 15.0, 2: 30.0, 3: 50.0, 4: 80.0}
        color_rarity_percentile = percentile_map.get(aggr_index, 30.0)

        options['color_rarity_percentile'] = color_rarity_percentile

        # Additional wizard fields retained for reference
        options['aggressiveness_index'] = aggr_index
        options['aggressiveness_label'] = aggr_label

        return options

    def validate(self):
        """Validate configuration."""
        # At least one detection method should be enabled
        if not self.radioMotionYes.isChecked() and not self.enableColorCheckBox.isChecked():
            return "Please enable at least one detection method (Motion or Color)."
        return None

    def load_options(self, options):
        """Load options into UI.

        Restores UI state from a previously saved options dictionary.
        Handles both old format (direct color_rarity_percentile) and new format
        (aggressiveness_index).
        """
        if not isinstance(options, dict):
            return

        if 'enable_motion' in options:
            enable_motion = bool(options['enable_motion'])
            self.radioMotionYes.setChecked(enable_motion)
            self.radioMotionNo.setChecked(not enable_motion)

        if 'enable_color_quantization' in options:
            self.enableColorCheckBox.setChecked(options['enable_color_quantization'])

        # Load aggressiveness - prefer aggressiveness_index if available
        if 'aggressiveness_index' in options:
            aggr_index = options['aggressiveness_index']
            if isinstance(aggr_index, int):
                self.aggressivenessSlider.setValue(max(0, min(4, aggr_index)))
        elif 'color_rarity_percentile' in options:
            # Reverse map percentile to aggressiveness index for backward compatibility
            # Lower percentile = conservative, higher percentile = aggressive
            percentile = float(options['color_rarity_percentile'])
            if percentile <= 10:
                index = 0  # Very Conservative
            elif percentile <= 20:
                index = 1  # Conservative
            elif percentile <= 40:
                index = 2  # Moderate
            elif percentile <= 60:
                index = 3  # Aggressive
            else:
                index = 4  # Very Aggressive
            self.aggressivenessSlider.setValue(index)
