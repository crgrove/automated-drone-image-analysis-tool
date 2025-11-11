from ast import literal_eval

from algorithms.AlgorithmController import AlgorithmController
from algorithms.HSVColorRange.views.HSVColorRange_ui import Ui_HSVColorRange
from algorithms.HSVColorRange.controllers.HSVColorRangeViewerController import HSVColorRangeRangeViewer
from algorithms.HSVColorRange.views.color_range_dialog import ColorRangeDialog
from core.services.LoggerService import LoggerService

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QColorDialog, QCheckBox, QSlider, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class HSVColorRangeController(QWidget, Ui_HSVColorRange, AlgorithmController):
    """Controller for the HSV Filter algorithm widget."""

    def __init__(self, config):
        """
        Initializes the HSVColorRangeController widget and sets up the UI.

        Connects UI elements like threshold spinboxs and color selection button
        to their respective event handlers.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)
        self.viewRangeButton.hide()
        self.selectedColor = None

        # Add hue expansion controls
        self._setup_hue_expansion_controls()

        # Connect button events
        self.colorButton.clicked.connect(self.color_button_clicked)
        self.viewRangeButton.clicked.connect(self.view_range_button_clicked)

        # Connect spinbox events for separate ranges
        self.hueMinusSpinBox.valueChanged.connect(self.on_ranges_changed)
        self.huePlusSpinBox.valueChanged.connect(self.on_ranges_changed)
        self.saturationMinusSpinBox.valueChanged.connect(self.on_ranges_changed)
        self.saturationPlusSpinBox.valueChanged.connect(self.on_ranges_changed)
        self.valueMinusSpinBox.valueChanged.connect(self.on_ranges_changed)
        self.valuePlusSpinBox.valueChanged.connect(self.on_ranges_changed)

        # HSV window data from new dialog
        self._hsv_window = None

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

    def on_ranges_changed(self):
        """Handle changes to the individual range spinboxes."""
        if self.selectedColor and self._hsv_window:
            # Update the HSV window data with new ranges

            # Convert spinbox values to 0-1 range
            self._hsv_window['h_minus'] = self.hueMinusSpinBox.value() / 179
            self._hsv_window['h_plus'] = self.huePlusSpinBox.value() / 179
            self._hsv_window['s_minus'] = self.saturationMinusSpinBox.value() / 255
            self._hsv_window['s_plus'] = self.saturationPlusSpinBox.value() / 255
            self._hsv_window['v_minus'] = self.valueMinusSpinBox.value() / 255
            self._hsv_window['v_plus'] = self.valuePlusSpinBox.value() / 255

    def color_button_clicked(self):
        """
        Handles the color selection button click.

        Opens the new HSV color range dialog for advanced color selection.
        """

        try:
            # Prepare initial values
            initial_hsv = (0, 1, 1)  # Default red
            initial_ranges = None

            # Set current values if available
            if self._hsv_window:
                # Use existing HSV window data (new format with h, s, v values directly)
                h, s, v = self._hsv_window['h'], self._hsv_window['s'], self._hsv_window['v']
                initial_hsv = (h, s, v)

                initial_ranges = {
                    'h_minus': self._hsv_window['h_minus'],
                    'h_plus': self._hsv_window['h_plus'],
                    's_minus': self._hsv_window['s_minus'],
                    's_plus': self._hsv_window['s_plus'],
                    'v_minus': self._hsv_window['v_minus'],
                    'v_plus': self._hsv_window['v_plus']
                }

            elif self.selectedColor and self.selectedColor.isValid():
                # Convert existing color to initial values
                h, s, v, _ = self.selectedColor.getHsvF()
                initial_hsv = (h, s, v)

                # Convert spinbox ranges to 0-1 format (use separate ranges if available)
                if hasattr(self, 'hueMinusSpinBox'):
                    h_minus_range = self.hueMinusSpinBox.value() / 179
                    h_plus_range = self.huePlusSpinBox.value() / 179
                    s_minus_range = self.saturationMinusSpinBox.value() / 255
                    s_plus_range = self.saturationPlusSpinBox.value() / 255
                    v_minus_range = self.valueMinusSpinBox.value() / 255
                    v_plus_range = self.valuePlusSpinBox.value() / 255
                else:
                    # Fallback to default values
                    h_minus_range = h_plus_range = 20/179
                    s_minus_range = s_plus_range = 50/255
                    v_minus_range = v_plus_range = 50/255

                initial_ranges = {
                    'h_minus': h_minus_range, 'h_plus': h_plus_range,
                    's_minus': s_minus_range, 's_plus': s_plus_range,
                    'v_minus': v_minus_range, 'v_plus': v_plus_range
                }

            # Create and show dialog
            dialog = ColorRangeDialog(None, initial_hsv, initial_ranges, self)

            if dialog.exec() == ColorRangeDialog.Accepted:
                hsv_data = dialog.get_hsv_ranges()

                # Store the data in our format for the service
                self._hsv_window = hsv_data

                # Save any custom colors that may have been modified
                from core.services.CustomColorsService import get_custom_colors_service
                custom_colors_service = get_custom_colors_service()
                custom_colors_service.sync_with_dialog()

                # Update the old UI elements for compatibility
                h, s, v = hsv_data['h'], hsv_data['s'], hsv_data['v']
                picked_color = QColor.fromHsvF(h, s, v)
                self.selectedColor = picked_color

                # Update the separate range spinboxes with actual ranges
                # The picker returns fractional offsets that represent how much to subtract/add
                # from the center value. These are position-dependent (can't exceed 0-1 bounds).
                # Convert these fractions to absolute range values in OpenCV scale.

                # For consistency, we'll show the actual range values that will be used,
                # not the constrained offsets from the picker

                # Calculate actual ranges in normalized space (0-1)
                h_range_minus = hsv_data['h_minus']
                h_range_plus = hsv_data['h_plus']
                s_range_minus = hsv_data['s_minus']
                s_range_plus = hsv_data['s_plus']
                v_range_minus = hsv_data['v_minus']
                v_range_plus = hsv_data['v_plus']

                # Convert to OpenCV scale for spinboxes
                # These represent the actual threshold values to be applied
                self.hueMinusSpinBox.setValue(int(h_range_minus * 179))
                self.huePlusSpinBox.setValue(int(h_range_plus * 179))
                self.saturationMinusSpinBox.setValue(int(s_range_minus * 255))
                self.saturationPlusSpinBox.setValue(int(s_range_plus * 255))
                self.valueMinusSpinBox.setValue(int(v_range_minus * 255))
                self.valuePlusSpinBox.setValue(int(v_range_plus * 255))

                self.update_colors()

        except Exception as e:
            self.logger.error(f"Error in color button click: {e}")

    def view_range_button_clicked(self):
        """
        Handles the view range button click.

        Opens the View Range dialog, displaying the selected color and
        threshold values for H, S, V.
        """
        # Use average of plus/minus ranges for the old dialog
        hue_avg = int((self.hueMinusSpinBox.value() + self.huePlusSpinBox.value()) / 2)
        sat_avg = int((self.saturationMinusSpinBox.value() + self.saturationPlusSpinBox.value()) / 2)
        val_avg = int((self.valueMinusSpinBox.value() + self.valuePlusSpinBox.value()) / 2)

        rangeDialog = HSVColorRangeRangeViewer(
            (self.selectedColor.red(),
             self.selectedColor.green(),
             self.selectedColor.blue()),
            hue_avg,
            sat_avg,
            val_avg)
        rangeDialog.exec()

    def update_colors(self):
        """
        Updates the color of the selected color box and shows the view range button.
        """
        if self.selectedColor is not None:
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

    def get_options(self):
        options = dict()
        if self._hsv_window is not None:
            # Use new HSV range data
            options['hsv_ranges'] = self._hsv_window
            # Keep backward compatibility for old format
            h, s, v = self._hsv_window['h'], self._hsv_window['s'], self._hsv_window['v']
            picked_color = QColor.fromHsvF(h, s, v)
            options['selected_color'] = (picked_color.red(), picked_color.green(), picked_color.blue())
            # For backward compatibility, provide average values
            options['hue_threshold'] = int((self._hsv_window['h_minus'] + self._hsv_window['h_plus']) * 90)
            options['saturation_threshold'] = int((self._hsv_window['s_minus'] + self._hsv_window['s_plus']) * 127)
            options['value_threshold'] = int((self._hsv_window['v_minus'] + self._hsv_window['v_plus']) * 127)
        elif self.selectedColor is not None:
            # Use separate range values if available, otherwise use defaults
            if hasattr(self, 'hueMinusSpinBox'):
                # Create HSV window data from separate spinboxes
                h, s, v, _ = self.selectedColor.getHsvF()
                options['hsv_ranges'] = {
                    'h': h, 's': s, 'v': v,
                    'h_minus': self.hueMinusSpinBox.value() / 179,
                    'h_plus': self.huePlusSpinBox.value() / 179,
                    's_minus': self.saturationMinusSpinBox.value() / 255,
                    's_plus': self.saturationPlusSpinBox.value() / 255,
                    'v_minus': self.valueMinusSpinBox.value() / 255,
                    'v_plus': self.valuePlusSpinBox.value() / 255
                }
            options['selected_color'] = (self.selectedColor.red(), self.selectedColor.green(),
                                          self.selectedColor.blue())
            # For backward compatibility
            if hasattr(self, 'hueMinusSpinBox'):
                options['hue_threshold'] = int((self.hueMinusSpinBox.value() + self.huePlusSpinBox.value()) / 2)
                options['saturation_threshold'] = int((self.saturationMinusSpinBox.value() +
                                                       self.saturationPlusSpinBox.value()) / 2)
                options['value_threshold'] = int((self.valueMinusSpinBox.value() + self.valuePlusSpinBox.value()) / 2)
            else:
                options['hue_threshold'] = 20
                options['saturation_threshold'] = 50
                options['value_threshold'] = 50
        else:
            options['selected_color'] = None
            options['hue_threshold'] = None
            options['saturation_threshold'] = None
            options['value_threshold'] = None

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
        if self._hsv_window is None and self.selectedColor is None:
            return "Please select a search color."
        return None

    def load_options(self, options):
        """
        Sets UI elements based on the provided options.

        Args:
            options (dict): The options to use to set UI attributes, including 'selected_color' and HSV thresholds.
        """
        # Load HSV ranges if available (new format)
        if 'hsv_ranges' in options:
            if isinstance(options['hsv_ranges'], str):
                self._hsv_window = literal_eval(options['hsv_ranges'])
            else:
                self._hsv_window = options['hsv_ranges']

            # Update UI from HSV ranges
            h, s, v = self._hsv_window['h'], self._hsv_window['s'], self._hsv_window['v']
            picked_color = QColor.fromHsvF(h, s, v)
            self.selectedColor = picked_color
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

            # Update separate range spinboxes with actual ranges
            if hasattr(self, 'hueMinusSpinBox'):
                self.hueMinusSpinBox.setValue(int(self._hsv_window['h_minus'] * 179))
                self.huePlusSpinBox.setValue(int(self._hsv_window['h_plus'] * 179))
                self.saturationMinusSpinBox.setValue(int(self._hsv_window['s_minus'] * 255))
                self.saturationPlusSpinBox.setValue(int(self._hsv_window['s_plus'] * 255))
                self.valueMinusSpinBox.setValue(int(self._hsv_window['v_minus'] * 255))
                self.valuePlusSpinBox.setValue(int(self._hsv_window['v_plus'] * 255))

        # Load old HSV window format (backward compatibility)
        elif 'hsv_window' in options:
            if isinstance(options['hsv_window'], str):
                hsv_window_old = literal_eval(options['hsv_window'])
            else:
                hsv_window_old = options['hsv_window']

            # Convert old format to new format
            picked_color = QColor(hsv_window_old['picked_hex'])
            h, s, v, _ = picked_color.getHsvF()

            # Convert old window to new ranges format
            h_center = h * 360
            s_center = s * 100
            v_center = v * 100

            self._hsv_window = {
                'h': h, 's': s, 'v': v,
                'h_minus': max(0, (h_center - hsv_window_old['h_min']) / 360),
                'h_plus': max(0, (hsv_window_old['h_max'] - h_center) / 360),
                's_minus': max(0, (s_center - hsv_window_old['s_min']) / 100),
                's_plus': max(0, (hsv_window_old['s_max'] - s_center) / 100),
                'v_minus': max(0, (v_center - hsv_window_old['v_min']) / 100),
                'v_plus': max(0, (hsv_window_old['v_max'] - v_center) / 100)
            }

            self.selectedColor = picked_color
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

            # Update separate range spinboxes with actual ranges
            if hasattr(self, 'hueMinusSpinBox'):
                self.hueMinusSpinBox.setValue(int(self._hsv_window['h_minus'] * 179))
                self.huePlusSpinBox.setValue(int(self._hsv_window['h_plus'] * 179))
                self.saturationMinusSpinBox.setValue(int(self._hsv_window['s_minus'] * 255))
                self.saturationPlusSpinBox.setValue(int(self._hsv_window['s_plus'] * 255))
                self.valueMinusSpinBox.setValue(int(self._hsv_window['v_minus'] * 255))
                self.valuePlusSpinBox.setValue(int(self._hsv_window['v_plus'] * 255))

        elif 'selected_color' in options:
            # Fallback to old method
            selected_color = literal_eval(options['selected_color'])
            self.selectedColor = QColor(selected_color[0], selected_color[1], selected_color[2])
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

            # Set separate range spinboxes if available
            if hasattr(self, 'hueMinusSpinBox'):
                if 'hue_threshold' in options:
                    hue_val = int(options['hue_threshold'])
                    self.hueMinusSpinBox.setValue(hue_val)
                    self.huePlusSpinBox.setValue(hue_val)

                if 'saturation_threshold' in options:
                    sat_val = int(options['saturation_threshold'])
                    self.saturationMinusSpinBox.setValue(sat_val)
                    self.saturationPlusSpinBox.setValue(sat_val)

                if 'value_threshold' in options:
                    val_val = int(options['value_threshold'])
                    self.valueMinusSpinBox.setValue(val_val)
                    self.valuePlusSpinBox.setValue(val_val)

        # Load hue expansion settings
        if 'hue_expansion_enabled' in options:
            self.hueExpansionCheckBox.setChecked(options['hue_expansion_enabled'])
        if 'hue_expansion_range' in options:
            self.hueExpansionSlider.setValue(int(options['hue_expansion_range']))
