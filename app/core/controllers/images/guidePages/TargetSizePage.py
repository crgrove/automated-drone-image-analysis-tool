"""
Target Size page for the Image Analysis Guide wizard.
"""

from PySide6.QtWidgets import QVBoxLayout

from .BasePage import BasePage
from core.views.components.RangeSlider import RangeSlider


class TargetSizePage(BasePage):
    """Page for selecting target object size range."""

    def setup_ui(self):
        """Initialize UI components."""
        # Get distance unit preference
        # Handle both 'Meters'/'Feet' (from UI) and 'm'/'ft' (legacy/internal) formats
        distance_unit = self.settings_service.get_setting('DistanceUnit', 'Feet')
        unit = 'm' if distance_unit in ('Meters', 'm') else 'ft'

        # Replace the placeholder widget with custom range slider
        initial_min = self.wizard_data.get('object_size_min', 1)
        initial_max = self.wizard_data.get('object_size_max', 6)

        self.objectSizeRangeSlider = RangeSlider(
            self.dialog.objectSizeRangeSliderWidget,
            minimum=1,
            maximum=1000,
            min_value=initial_min,
            max_value=initial_max,
            unit=unit
        )
        # Update wizard data with snapped values
        self.wizard_data['object_size_min'] = self.objectSizeRangeSlider.minValue()
        self.wizard_data['object_size_max'] = self.objectSizeRangeSlider.maxValue()
        # Set the range slider to fill the widget
        layout = QVBoxLayout(self.dialog.objectSizeRangeSliderWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.objectSizeRangeSlider)

        # Update examples label based on unit
        self._update_examples_label(unit)

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.objectSizeRangeSlider.rangeChanged.connect(self._on_object_size_range_changed)

    def load_data(self):
        """Load object size preferences if available."""
        # Values are already set in setup_ui from wizard_data
        # Update examples label if unit preference changed
        distance_unit = self.settings_service.get_setting('DistanceUnit', 'Feet')
        unit = 'm' if distance_unit in ('Meters', 'm') else 'ft'
        self._update_examples_label(unit)
        if hasattr(self, 'objectSizeRangeSlider'):
            self.objectSizeRangeSlider.setUnit(unit)

    def validate(self) -> bool:
        """Validate that object size range is set."""
        return True  # Range slider always has valid values

    def save_data(self):
        """Save object size range to wizard_data."""
        self.wizard_data['object_size_min'] = self.objectSizeRangeSlider.minValue()
        self.wizard_data['object_size_max'] = self.objectSizeRangeSlider.maxValue()

    def _on_object_size_range_changed(self, min_value, max_value):
        """Handle object size range slider change."""
        self.wizard_data['object_size_min'] = min_value
        self.wizard_data['object_size_max'] = max_value

    def _update_examples_label(self, unit):
        """Update the examples label with the correct unit."""
        if not hasattr(self.dialog, 'labelExamples'):
            return

        # Conversion factor: 1 sqft = 0.092903 sqm
        examples = [
            (1, "Hat, Helmet, Plastic Bag"),
            (3, "Cat, Daypack"),
            (6, "Large Pack, Medium Dog"),
            (12, "Sleeping Bag, Large Dog"),
            (50, "Small Boat, 2-Person Tent"),
            (200, "Car/SUV, Small Pickup Truck, Large Tent"),
            (1000, "House")
        ]

        html_parts = ['<html><head/><body><p><span style=" font-weight:700;">More Examples:</span></p><ul>']

        for value_sqft, description in examples:
            if unit == 'm':
                value_sqm = value_sqft * 0.092903
                if value_sqm < 1:
                    value_str = f"{value_sqm:.2f}"
                elif value_sqm < 10:
                    value_str = f"{value_sqm:.2f}"
                else:
                    value_str = f"{value_sqm:.1f}"
                unit_str = "sqm"
            else:
                value_str = str(value_sqft)
                unit_str = "sqft"

            html_parts.append(f'<li>&nbsp;&nbsp;{value_str} {unit_str} – {description} </li>')

        html_parts.append('</ul></body></html>')
        self.dialog.labelExamples.setText(''.join(html_parts))
