"""
Wizard controller for streaming AI Person Detector.

Provides the same simplified, guided interface as the image-analysis AI Person
Detector wizard: a single confidence preset slider. All other streaming
parameters (processing resolution, rendering, temporal voting, masking, etc.)
are intentionally not exposed here and fall back to the control widget's
defaults when the Stream Viewer applies these options.
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from algorithms.streaming.AIPersonDetector.views.AIPersonDetectorWizard_ui import Ui_AIPersonDetectorWizard
from core.views.components.LabeledSlider import TextLabeledSlider

# Slider index -> confidence percent, matching the image-analysis wizard.
_CONFIDENCE_MAP = {
    0: 90,   # Very Confident
    1: 70,   # Confident
    2: 50,   # Balanced
    3: 30,   # Permissive
    4: 10,   # Very Permissive
}


class AIPersonDetectorWizardController(QWidget, Ui_AIPersonDetectorWizard):
    """Wizard controller for the streaming AI Person Detector algorithm."""

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
        """Attach custom widgets and set defaults."""
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

        self.confidenceSlider.valueChanged.connect(lambda _index: self.validation_changed.emit())

    def get_options(self) -> Dict[str, Any]:
        """Get algorithm options.

        Only the confidence preset is set explicitly; everything else uses the
        streaming control widget's logical defaults.
        """
        confidence_index = self.confidenceSlider.value()
        confidence_label, _ = self.confidenceSlider.getCurrentPreset()

        options = {
            # Consumed by AIPersonDetectorControlWidget.set_config (percent, 1-100).
            'person_detector_confidence': _CONFIDENCE_MAP.get(confidence_index, 50),
            'cpu_only': False,
            # Wizard fields retained for round-tripping the slider position.
            'confidence_index': confidence_index,
            'confidence_label': confidence_label,
        }
        return options

    def validate(self):
        """Validate configuration. Always valid - no required inputs."""
        return None

    def load_options(self, options):
        """Load options into UI.

        Prefers the wizard's own confidence_index; otherwise maps equivalent
        settings from saved streaming configs (person_detector_confidence as a
        percent, or confidence_threshold as a 0-1 fraction) onto the nearest
        preset. Unrelated streaming keys are ignored.
        """
        if not isinstance(options, dict):
            return

        if isinstance(options.get('confidence_index'), int):
            self.confidenceSlider.setValue(max(0, min(4, options['confidence_index'])))
            return

        confidence = self._extract_confidence_percent(options)
        if confidence is None:
            return

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

    @staticmethod
    def _extract_confidence_percent(options: Dict[str, Any]) -> Optional[float]:
        """Normalize saved confidence settings to a 0-100 percent value."""
        for key in ('person_detector_confidence', 'confidence_threshold'):
            if key in options:
                try:
                    value = float(options[key])
                except (TypeError, ValueError):
                    continue
                # confidence_threshold is a 0-1 fraction; percent values are > 1.
                return value * 100.0 if value <= 1.0 else value
        return None
