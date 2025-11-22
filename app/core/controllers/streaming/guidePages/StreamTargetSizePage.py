"""
Target Size page for the Streaming Guide wizard.
"""

from PySide6.QtWidgets import QVBoxLayout

from .BasePage import BasePage
from core.views.components.RangeSlider import RangeSlider


class StreamTargetSizePage(BasePage):
    """Page for selecting target object size range for streaming."""

    def setup_ui(self):
        """Initialize UI components."""
        # Replace the placeholder widget with custom range slider
        initial_min = self.wizard_data.get('object_size_min', 1)
        initial_max = self.wizard_data.get('object_size_max', 6)

        self.objectSizeRangeSlider = RangeSlider(
            self.dialog.objectSizeRangeSliderWidget,
            minimum=1,
            maximum=1000,
            min_value=initial_min,
            max_value=initial_max
        )
        # Update wizard data with snapped values
        self.wizard_data['object_size_min'] = self.objectSizeRangeSlider.minValue()
        self.wizard_data['object_size_max'] = self.objectSizeRangeSlider.maxValue()
        # Set the range slider to fill the widget
        layout = QVBoxLayout(self.dialog.objectSizeRangeSliderWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.objectSizeRangeSlider)

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.objectSizeRangeSlider.rangeChanged.connect(self._on_object_size_range_changed)

    def load_data(self):
        """Load object size preferences if available."""
        # Values are already set in setup_ui from wizard_data
        pass

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

