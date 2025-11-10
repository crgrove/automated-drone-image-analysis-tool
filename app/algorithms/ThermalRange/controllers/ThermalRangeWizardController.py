"""
Wizard controller for Thermal Range algorithm.

Provides a simplified, guided interface for configuring thermal temperature range parameters.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from algorithms.AlgorithmController import AlgorithmController
from core.services.SettingsService import SettingsService
from algorithms.ThermalRange.views.ThermalRangeWizard_ui import Ui_ThermalRangeWizard
from core.views.components.RangeSlider import RangeSlider


class TemperatureRangeSlider(RangeSlider):
    """Custom RangeSlider for temperature selection."""
    
    def __init__(self, parent=None, is_fahrenheit=True):
        """Initialize temperature range slider with appropriate unit."""
        self.is_fahrenheit = is_fahrenheit
        
        if is_fahrenheit:
            # Fahrenheit: 0-150°F with 10-degree increments
            snap_points = [
                (0, "0°F"),
                (10, "10°F"),
                (20, "20°F"),
                (30, "30°F"),
                (40, "40°F"),
                (50, "50°F"),
                (60, "60°F"),
                (70, "70°F"),
                (80, "80°F"),
                (90, "90°F"),
                (100, "100°F"),
                (110, "110°F"),
                (120, "120°F"),
                (130, "130°F"),
                (140, "140°F"),
                (150, "150°F")
            ]
            # Default to 95-105°F
            min_val, max_val = 90, 110
        else:
            # Celsius: -18 to 65°C (roughly equivalent to 0-150°F) with 5-degree increments
            snap_points = [
                (-18, "-18°C"),
                (-13, "-13°C"),
                (-8, "-8°C"),
                (-3, "-3°C"),
                (2, "2°C"),
                (7, "7°C"),
                (12, "12°C"),
                (17, "17°C"),
                (22, "22°C"),
                (27, "27°C"),
                (32, "32°C"),
                (37, "37°C"),
                (42, "42°C"),
                (47, "47°C"),
                (52, "52°C"),
                (57, "57°C"),
                (62, "62°C"),
                (65, "65°C")
            ]
            # Default to 32-43°C (roughly 90-110°F)
            min_val, max_val = 32, 43
        
        # Override SNAP_POINTS before calling parent init
        TemperatureRangeSlider.SNAP_POINTS = snap_points
        
        super().__init__(parent, minimum=snap_points[0][0], maximum=snap_points[-1][0], 
                        min_value=min_val, max_value=max_val)


class ThermalRangeWizardController(QWidget, Ui_ThermalRangeWizard, AlgorithmController):
    """Wizard controller for Thermal Range algorithm."""
    
    def __init__(self, config, theme):
        """Initialize the wizard controller."""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme
        self.settings_service = SettingsService()
        
        self.setupUi(self)
        self._wire_up_ui()
    
    def _wire_up_ui(self):
        """Configure UI and set defaults based on temperature unit."""
        # Check temperature unit from settings
        is_fahrenheit = self.settings_service.get_setting('TemperatureUnit') == 'Fahrenheit'
        
        # Create custom temperature range slider
        self.rangeSlider = TemperatureRangeSlider(self, is_fahrenheit=is_fahrenheit)
        
        # Insert into placeholder
        placeholder = self.rangeSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.rangeSlider)
    
    def get_options(self):
        """Get algorithm options."""
        options = dict()
        is_fahrenheit = self.settings_service.get_setting('TemperatureUnit') == 'Fahrenheit'
        
        min_val = self.rangeSlider.minValue()
        max_val = self.rangeSlider.maxValue()
        
        # Convert to Celsius if in Fahrenheit
        if is_fahrenheit:
            options['minTemp'] = self._convert_fahrenheit_to_celsius(min_val)
            options['maxTemp'] = self._convert_fahrenheit_to_celsius(max_val)
        else:
            options['minTemp'] = min_val
            options['maxTemp'] = max_val
        
        return options
    
    def validate(self):
        """Validate configuration."""
        # Always valid - no required inputs
        return None
    
    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return
        
        is_fahrenheit = self.settings_service.get_setting('TemperatureUnit') == 'Fahrenheit'
        
        if 'minTemp' in options and 'maxTemp' in options:
            min_temp_c = float(options['minTemp'])
            max_temp_c = float(options['maxTemp'])
            
            if is_fahrenheit:
                min_val = int(self._convert_celsius_to_fahrenheit(min_temp_c))
                max_val = int(self._convert_celsius_to_fahrenheit(max_temp_c))
            else:
                min_val = int(min_temp_c)
                max_val = int(max_temp_c)
            
            self.rangeSlider.setMinValue(min_val)
            self.rangeSlider.setMaxValue(max_val)
    
    def _convert_fahrenheit_to_celsius(self, value):
        """Convert Fahrenheit to Celsius."""
        return (value - 32) / 1.8000
    
    def _convert_celsius_to_fahrenheit(self, value):
        """Convert Celsius to Fahrenheit."""
        return (value * 1.8000) + 32

