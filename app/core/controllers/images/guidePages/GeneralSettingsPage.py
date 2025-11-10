"""
General Settings page for the Image Analysis Guide wizard.
"""

import os
import math
from PySide6.QtWidgets import QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from .BasePage import BasePage
from core.views.components.LabeledSlider import LabeledSlider, TextLabeledSlider
from core.services.CPUService import CPUService
from core.services.image.ImageService import ImageService


class GeneralSettingsPage(BasePage):
    """Page for general settings (color, processes, normalize)."""
    
    def setup_ui(self):
        """Initialize UI components."""
        # Prevent buttons from getting focus by default
        self.dialog.colorPickerButton.setFocusPolicy(Qt.NoFocus)
        self.dialog.benchmarkButton.setFocusPolicy(Qt.NoFocus)
        
        # Replace the placeholder widget with custom labeled slider
        initial_max_processes = self.wizard_data.get('max_processes', 4)
        self.maxProcessesSlider = LabeledSlider(
            self.dialog.maxProcessesSliderWidget,
            minimum=1,
            maximum=20,
            value=initial_max_processes
        )
        # Set the labeled slider to fill the widget
        layout = QVBoxLayout(self.dialog.maxProcessesSliderWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.maxProcessesSlider)
        
        # Setup processing resolution slider
        self._setup_processing_resolution_slider()
        
        # Set default color preview
        self._update_color_preview()

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.dialog.colorPickerButton.clicked.connect(self._on_color_picker)
        self.maxProcessesSlider.valueChanged.connect(self._on_max_processes_changed)
        self.dialog.benchmarkButton.clicked.connect(self._on_benchmark)
        self.dialog.radioNormalizeNo.toggled.connect(self._on_normalize_changed)
        self.dialog.radioNormalizeYes.toggled.connect(self._on_normalize_changed)
        # Save skip preference immediately when toggled
        self.dialog.skipCheckBox.toggled.connect(self._on_skip_toggled)
        # Connect processing resolution slider
        if hasattr(self, 'processingResolutionSlider'):
            self.processingResolutionSlider.valueChanged.connect(self._on_processing_resolution_changed)

    def load_data(self):
        """Load preferences if available."""
        # Load max processes
        max_proc = self.settings_service.get_setting('MaxProcesses', '4')
        try:
            max_proc = int(max_proc)
            if 1 <= max_proc <= 20:
                self.maxProcessesSlider.setValue(max_proc)
        except ValueError:
            pass
        
        # Load normalize histogram
        normalize = self.settings_service.get_setting('NormalizeHistogram', 'No')
        if normalize == 'Yes':
            self.dialog.radioNormalizeYes.setChecked(True)
        else:
            self.dialog.radioNormalizeNo.setChecked(True)
        
        # Load identifier color
        color_str = self.settings_service.get_setting('IdentifierColor', '255,0,0')
        try:
            r, g, b = map(int, color_str.split(','))
            self.wizard_data['identifier_color'] = QColor(r, g, b)
            self._update_color_preview()
        except (ValueError, AttributeError):
            pass
        
        # Load skip wizard preference
        skip_wizard = self.settings_service.get_setting('SkipImageAnalysisGuide', 'No')
        self.dialog.skipCheckBox.setChecked(str(skip_wizard).strip() == 'Yes')
        
        # Load processing resolution
        resolution_text = self.settings_service.get_setting('ProcessingResolution', '50%')
        if hasattr(self, 'processingResolutionSlider'):
            # Map resolution text to slider index
            resolution_presets = ["10%", "25%", "33%", "50%", "75%", "100%"]
            try:
                index = resolution_presets.index(resolution_text)
                self.processingResolutionSlider.setValue(index)
            except ValueError:
                # Default to 50% if not found
                self.processingResolutionSlider.setValue(2)
                self.wizard_data['processing_resolution'] = '50%'

    def validate(self) -> bool:
        """Validate that settings are valid."""
        return True  # All settings have defaults

    def save_data(self):
        """Save settings to wizard_data and preferences."""
        # Max processes is already saved via signal handler
        # Normalize histogram is already saved via signal handler
        # Identifier color is already saved via signal handler
        # Skip preference is saved via signal handler
        pass

    def _on_color_picker(self):
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(
            self.wizard_data['identifier_color'],
            self.dialog,
            "Select AOI Highlight Color"
        )
        if color.isValid():
            self.wizard_data['identifier_color'] = color
            self._update_color_preview()
        # Remove focus from the button after returning from the picker
        try:
            self.dialog.colorPickerButton.clearFocus()
        except Exception:
            pass

    def _update_color_preview(self):
        """Update color preview label."""
        color = self.wizard_data['identifier_color']
        self.dialog.labelColorPreview.setStyleSheet(
            f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
            "border: 1px solid black;"
        )

    def _on_max_processes_changed(self, value):
        """Handle max processes slider change."""
        self.wizard_data['max_processes'] = value

    def _on_benchmark(self):
        """Run benchmark to determine optimal number of processes."""
        # Get recommended process count (CPU cores - 1)
        recommended_count = CPUService.get_recommended_process_count()
        cpu_count = CPUService.get_cpu_count()
        
        # Clamp to slider range (1-20)
        recommended_count = max(1, min(20, recommended_count))
        
        # Update slider (this will trigger valueChanged signal and update wizard_data)
        self.maxProcessesSlider.setValue(recommended_count)
        
        # Show informational message
        QMessageBox.information(
            self.dialog,
            "Benchmark Complete",
            f"Detected {cpu_count} CPU core(s).\n\n"
            f"Recommended number of processes: {recommended_count}\n\n"
            f"The slider has been set to {recommended_count} processes."
        )

    def _on_normalize_changed(self):
        """Handle normalize histogram radio button change."""
        self.wizard_data['normalize_histogram'] = self.dialog.radioNormalizeYes.isChecked()

    def on_enter(self):
        """Called when entering the page - recalculate recommended processing resolution."""
        # Recalculate recommended resolution now that first_image_path should be available
        if hasattr(self, 'processingResolutionSlider'):
            recommended_index = self._calculate_recommended_resolution()
            resolution_presets = ["10%", "25%", "33%", "50%", "75%", "100%"]
            
            # Update slider value
            self.processingResolutionSlider.setValue(recommended_index)
            
            # Update wizard_data
            self.wizard_data['processing_resolution'] = resolution_presets[recommended_index]

    def _on_skip_toggled(self, checked: bool) -> None:
        """Persist the SkipImageAnalysisGuide preference as soon as the user toggles it."""
        try:
            self._save_skip_preference()
        except Exception as e:
            # Non-fatal; preference will still be saved on close/complete
            print(f"Warning: failed saving SkipImageAnalysisGuide immediately: {e}")

    def _save_skip_preference(self) -> None:
        """Persist the 'SkipImageAnalysisGuide' setting based on the checkbox state."""
        skip_value = 'Yes' if self.dialog.skipCheckBox.isChecked() else 'No'
        self.settings_service.set_setting('SkipImageAnalysisGuide', skip_value)
        # Optional: verify
        verify = self.settings_service.get_setting('SkipImageAnalysisGuide', 'No')
        if str(verify).strip() != skip_value:
            print(
                f"Warning: SkipImageAnalysisGuide setting may not have saved correctly. "
                f"Expected '{skip_value}', got '{verify}'"
            )
    
    def _setup_processing_resolution_slider(self):
        """Setup the processing resolution slider with default value."""
        # Resolution presets matching MainWindow (ordered from lowest to highest)
        resolution_presets = ["10%", "25%", "33%", "50%", "75%", "100%"]
        
        # Default to 50% (index 3) - will be recalculated in on_enter()
        default_index = 3
        
        # Create labeled slider with text labels
        self.processingResolutionSlider = TextLabeledSlider(
            self.dialog.processingResolutionSliderWidget,
            presets=resolution_presets
        )
        
        # Set default value (will be updated in on_enter() if image is available)
        self.processingResolutionSlider.setValue(default_index)
        
        # Set the labeled slider to fill the widget
        layout = QVBoxLayout(self.dialog.processingResolutionSliderWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.processingResolutionSlider)
        
        # Store default value in wizard_data
        self.wizard_data['processing_resolution'] = resolution_presets[default_index]
    
    def _calculate_recommended_resolution(self):
        """Calculate recommended processing resolution based on image size (20MP threshold)."""
        # Resolution presets ordered from lowest to highest: ["10%", "25%", "33%", "50%", "75%", "100%"]
        # Default to 50% (index 3) if no image available
        default_index = 3
        
        first_image_path = self.wizard_data.get('first_image_path')
        if not first_image_path or not os.path.exists(first_image_path):
            return default_index
        
        try:
            # Load image to get dimensions
            image_service = ImageService(first_image_path)
            img_array = image_service.img_array
            
            if img_array is None or len(img_array.shape) < 2:
                return default_index
            
            # Get image dimensions
            height, width = img_array.shape[:2]
            
            # Calculate megapixels
            megapixels = (width * height) / 1_000_000
            
            # If <= 20MP, recommend 100% (index 5 in new order)
            if megapixels <= 20:
                return 5  # 100%
            
            # If > 20MP, calculate percentage to get to 20MP
            # target_MP = actual_MP * (resolution_percentage / 100)^2
            # 20 = actual_MP * (resolution_percentage / 100)^2
            # (resolution_percentage / 100)^2 = 20 / actual_MP
            # resolution_percentage = 100 * sqrt(20 / actual_MP)
            resolution_percentage = 100 * math.sqrt(20 / megapixels)
            
            # Map to nearest preset (ordered from lowest to highest)
            resolution_presets = [10, 25, 33, 50, 75, 100]
            closest_index = 5  # Start with 100% (index 5)
            closest_diff = abs(resolution_percentage - 100)
            
            for i, preset in enumerate(resolution_presets):
                diff = abs(resolution_percentage - preset)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_index = i
            
            return closest_index
            
        except Exception as e:
            print(f"Error calculating recommended resolution: {e}")
            return default_index
    
    def _on_processing_resolution_changed(self, index):
        """Handle processing resolution slider change."""
        resolution_presets = ["10%", "25%", "33%", "50%", "75%", "100%"]
        if 0 <= index < len(resolution_presets):
            self.wizard_data['processing_resolution'] = resolution_presets[index]

