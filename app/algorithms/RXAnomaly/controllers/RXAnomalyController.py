from algorithms.AlgorithmController import AlgorithmController
from algorithms.RXAnomaly.views.RXAnomaly_ui import Ui_RXAnomaly

from PySide6.QtWidgets import QWidget, QCheckBox, QSlider, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class RXAnomalyController(QWidget, Ui_RXAnomaly, AlgorithmController):
    """Controller for the RX Anomaly algorithm widget."""

    def __init__(self, config, theme):
        """
        Initializes the RXAnomalyController widget and sets up the UI.

        Connects the sensitivity slider to the update_sensitivity handler.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.setupUi(self)

        # Add hue expansion controls
        self._setup_hue_expansion_controls()

        self.sensitivitySlider.valueChanged.connect(self.update_sensitivity)

    def _setup_hue_expansion_controls(self):
        """Add hue expansion controls to the UI."""
        # Create hue expansion checkbox
        self.hueExpansionCheckBox = QCheckBox("Enable Hue Expansion")
        self.hueExpansionCheckBox.setToolTip("Expand detected pixels to include nearby pixels with similar hue values")

        # Create hue expansion range slider and label
        hue_expansion_layout = QHBoxLayout()
        hue_expansion_label = QLabel("Hue Range (±):")
        self.hueExpansionSlider = QSlider(Qt.Horizontal)
        self.hueExpansionSlider.setMinimum(0)
        self.hueExpansionSlider.setMaximum(30)
        self.hueExpansionSlider.setValue(10)
        self.hueExpansionSlider.setTickPosition(QSlider.TicksBelow)
        self.hueExpansionSlider.setTickInterval(5)
        self.hueExpansionSlider.setEnabled(False)  # Disabled until checkbox is checked

        self.hueExpansionValueLabel = QLabel("±10")
        self.hueExpansionValueLabel.setMinimumWidth(35)

        hue_expansion_layout.addWidget(hue_expansion_label)
        hue_expansion_layout.addWidget(self.hueExpansionSlider)
        hue_expansion_layout.addWidget(self.hueExpansionValueLabel)

        # Add to main layout
        self.verticalLayout.addWidget(self.hueExpansionCheckBox)
        self.verticalLayout.addLayout(hue_expansion_layout)

        # Connect signals
        self.hueExpansionCheckBox.toggled.connect(self._on_hue_expansion_toggled)
        self.hueExpansionSlider.valueChanged.connect(self._on_hue_expansion_range_changed)

    def _on_hue_expansion_toggled(self, checked):
        """Handle hue expansion checkbox toggle."""
        self.hueExpansionSlider.setEnabled(checked)

    def _on_hue_expansion_range_changed(self, value):
        """Handle hue expansion range slider change."""
        self.hueExpansionValueLabel.setText(f"±{value}")

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing the selected option values, including 'sensitivity' and 'segments'.
        """
        options = dict()
        options['sensitivity'] = int(self.sensitivityValueLabel.text())
        options['segments'] = int(self.segmentsComboBox.currentText())

        # Add hue expansion settings
        options['hue_expansion_enabled'] = self.hueExpansionCheckBox.isChecked()
        options['hue_expansion_range'] = self.hueExpansionSlider.value()

        return options

    def update_sensitivity(self):
        """
        Handles changes to the sensitivity slider.

        Updates the sensitivity value label based on the current slider position.
        """
        self.sensitivityValueLabel.setText(str(self.sensitivitySlider.value()))

    def validate(self):
        """
        Validates that the required values have been provided.

        Returns:
            str: An error message if validation fails, otherwise None.
        """
        return None

    def load_options(self, options):
        """
        Sets UI elements based on the provided options.

        Args:
            options (dict): The options to use to set UI attributes, including 'sensitivity' and 'segments'.
        """
        if 'sensitivity' in options:
            self.sensitivityValueLabel.setText(str(options['sensitivity']))
            self.sensitivitySlider.setProperty("value", int(options['sensitivity']))
        if 'segments' in options:
            self.segmentsComboBox.setCurrentText(str(options['segments']))

        # Load hue expansion settings
        if 'hue_expansion_enabled' in options:
            self.hueExpansionCheckBox.setChecked(options['hue_expansion_enabled'])
        if 'hue_expansion_range' in options:
            self.hueExpansionSlider.setValue(int(options['hue_expansion_range']))
