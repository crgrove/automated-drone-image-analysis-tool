from ast import literal_eval

from algorithms.AlgorithmController import AlgorithmController
from algorithms.MatchedFilter.views.MatchedFilter_ui import Ui_MatchedFilter
from algorithms.MatchedFilter.controllers.MatchedFilterRangeViewerController import MatchedFilterRangeViewer
from core.services.LoggerService import LoggerService

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QColorDialog, QCheckBox, QSlider, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class MatchedFilterController(QWidget, Ui_MatchedFilter, AlgorithmController):
    """Controller for the Matched Filter algorithm widget."""

    def __init__(self, config):
        """
        Initializes the MatchedFilterController widget and sets up the UI.

        Connects UI elements like threshold slider and color selection button
        to their respective event handlers.

        Args:
            config (dict): Algorithm config information.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)
        self.viewRangeButton.hide()
        self.selectedColor = None

        # Add hue expansion controls
        self._setup_hue_expansion_controls()

        self.thresholdSlider.valueChanged.connect(self.update_threshold)
        self.colorButton.clicked.connect(self.color_button_clicked)
        self.viewRangeButton.clicked.connect(self.view_range_button_clicked)

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

    def color_button_clicked(self):
        """
        Handles the color selection button click.

        Opens a color picker dialog to allow the user to select a color.
        Updates the selected color if a valid color is chosen.
        """
        try:
            if self.selectedColor is not None:
                color = QColorDialog.getColor(self.selectedColor)
            else:
                color = QColorDialog.getColor()
            if color.isValid():
                self.selectedColor = color
                self.update_colors()
        except Exception as e:
            self.logger.error(e)

    def view_range_button_clicked(self):
        """
        Handles the view range button click.

        Opens the View Range dialog, displaying the selected color and
        threshold value.
        """
        rangeDialog = MatchedFilterRangeViewer(
            (self.selectedColor.red(),
             self.selectedColor.green(),
             self.selectedColor.blue()),
            float(self.thresholdValueLabel.text()))
        rangeDialog.exec()

    def update_colors(self):
        """
        Updates the color of the selected color box and shows the view range button.
        """
        if self.selectedColor is not None:
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

    def update_threshold(self):
        """
        Handles the threshold slider value change event.

        Updates the threshold value label based on the current slider position.
        """
        if self.thresholdSlider.value() == .1:
            self.thresholdValueLabel.setText('.1')
        elif self.thresholdSlider.value() == 10:
            self.thresholdValueLabel.setText('1')
        else:
            self.thresholdValueLabel.setText("." + str(self.thresholdSlider.value()))

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing selected options, including 'selected_color' and 'match_filter_threshold'.
        """
        options = dict()
        options['selected_color'] = (self.selectedColor.red(), self.selectedColor.green(), self.selectedColor.blue())
        options['match_filter_threshold'] = float(self.thresholdValueLabel.text())

        # Add hue expansion settings
        options['hue_expansion_enabled'] = self.hueExpansionCheckBox.isChecked()
        options['hue_expansion_range'] = self.hueExpansionSlider.value()

        return options

    def validate(self):
        """
        Validates that the required values have been provided.

        Returns:
            str: An error message if validation fails, otherwise None.
        """
        if self.selectedColor is None:
            return "Please select a search color."
        return None

    def load_options(self, options):
        """
        Sets UI elements based on the provided options.

        Args:
            options (dict): The options to use to set UI attributes, including 'selected_color' and 'match_filter_threshold'.
        """
        if 'selected_color' in options:
            selected_color = literal_eval(options['selected_color'])
            self.selectedColor = QColor(selected_color[0], selected_color[1], selected_color[2])
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()
        if 'match_filter_threshold' in options:
            self.thresholdValueLabel.setText(str(options['match_filter_threshold']))
            self.thresholdSlider.setProperty("value", int(float(options['match_filter_threshold']) * 10))

        # Load hue expansion settings
        if 'hue_expansion_enabled' in options:
            self.hueExpansionCheckBox.setChecked(options['hue_expansion_enabled'])
        if 'hue_expansion_range' in options:
            self.hueExpansionSlider.setValue(int(options['hue_expansion_range']))
