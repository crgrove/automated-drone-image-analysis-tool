"""
Wizard controller for AI Person Detector algorithm.

Provides a simplified, guided interface for configuring AI person detection parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout

from algorithms.AlgorithmController import AlgorithmController
from core.views.components.LabeledSlider import TextLabeledSlider
from algorithms.images.AIPersonDetector.views.AIPersonDetectorWizard_ui import Ui_AIPersonDetectorWizard


class AIPersonDetectorWizardController(QWidget, Ui_AIPersonDetectorWizard, AlgorithmController):
    """Wizard controller for AI Person Detector algorithm."""

    def __init__(self, config, theme):
        """Initialize the wizard controller."""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme
        self.cpu_only = False

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults."""
        # Confidence slider with text labels matching mockup
        self.confidenceSlider = TextLabeledSlider(
            self,
            presets=[
                self.tr("Very \nConfident"),
                self.tr("Confident"),
                self.tr("Balanced"),
                self.tr("Permissive"),
                self.tr("Very \nPermissive"),
            ]
        )
        placeholder = self.confidenceSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.confidenceSlider)

    def _read_ui_state(self):
        """Read current UI selections into simple values."""
        confidence_index = self.confidenceSlider.value()
        aggr_label, aggr_value = self.confidenceSlider.getCurrentPreset()
        return confidence_index, aggr_label, aggr_value

    def get_options(self):
        """Get algorithm options."""
        options = dict()
        confidence_index, aggr_label, aggr_value = self._read_ui_state()

        # Map slider index to confidence value (0 - 100)
        # Index 0 (Very Confident) = 90, Index 4 (Very Permissive) = 10
        confidence_map = {
            0: 90,   # Very Confident
            1: 70,   # Confident
            2: 50,   # Balanced
            3: 30,   # Permissive
            4: 10    # Very Permissive
        }

        # Service-expected fields
        options['person_detector_confidence'] = confidence_map.get(confidence_index, 50)
        options['cpu_only'] = self.cpu_only

        # Wizard fields retained for reference
        options['confidence_index'] = confidence_index
        options['confidence_label'] = aggr_label

        return options

    def validate(self):
        """Validate configuration."""
        # Always valid - no required inputs
        return None

    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return

        if 'confidence_index' in options:
            confidence_index = options.get('confidence_index')
            if isinstance(confidence_index, int):
                self.confidenceSlider.setValue(max(0, min(4, confidence_index)))
        elif 'person_detector_confidence' in options:
            # Reverse map confidence to index. Saved values are percent (90/70/...),
            # but older configs may hold a 0-1 fraction; normalize to percent first.
            try:
                confidence = float(options['person_detector_confidence'])
            except (TypeError, ValueError):
                return
            if confidence <= 1.0:
                confidence *= 100.0
            if confidence >= 80:
                index = 0  # Very Confident
            elif confidence >= 60:
                index = 1  # Confident
            elif confidence >= 40:
                index = 2  # Balanced
            elif confidence >= 20:
                index = 3  # Permissive
            else:
                index = 4  # Very Permissive
            self.confidenceSlider.setValue(index)
