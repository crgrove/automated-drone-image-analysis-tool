"""
Wizard controller for Motion Detection algorithm.

Provides a simplified, guided interface for configuring motion detection.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

from algorithms.streaming.MotionDetection.views.MotionDetectionWizard_ui import Ui_MotionDetectionWizard


class MotionDetectionWizardController(QWidget, Ui_MotionDetectionWizard):
    """Wizard controller for Motion Detection algorithm."""

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
        # Set default values
        self.modeComboBox.setCurrentText('Auto')
        self.algorithmComboBox.setCurrentText('MOG2 Background')
        self.sensitivitySlider.setValue(50)
        self.minAreaSpinBox.setValue(500)
        self.maxAreaSpinBox.setValue(100000)

        # Connect signals
        self.sensitivitySlider.valueChanged.connect(self._on_sensitivity_changed)

    def _on_sensitivity_changed(self, value):
        """Update sensitivity label."""
        self.labelSensitivity.setText(f"Sensitivity: {value}%")

    def get_options(self):
        """Get algorithm options."""
        options = {
            'mode': self.modeComboBox.currentText(),
            'algorithm': self.algorithmComboBox.currentText(),
            'sensitivity': self.sensitivitySlider.value(),
            'min_area': self.minAreaSpinBox.value(),
            'max_area': self.maxAreaSpinBox.value(),
        }
        return options

    def validate(self):
        """Validate configuration."""
        # Motion detection is always valid
        return None

    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return

        if 'mode' in options:
            mode = options['mode']
            index = self.modeComboBox.findText(mode)
            if index >= 0:
                self.modeComboBox.setCurrentIndex(index)

        if 'algorithm' in options:
            algorithm = options['algorithm']
            index = self.algorithmComboBox.findText(algorithm)
            if index >= 0:
                self.algorithmComboBox.setCurrentIndex(index)

        if 'sensitivity' in options:
            self.sensitivitySlider.setValue(options['sensitivity'])

        if 'min_area' in options:
            self.minAreaSpinBox.setValue(options['min_area'])

        if 'max_area' in options:
            self.maxAreaSpinBox.setValue(options['max_area'])

