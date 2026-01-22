"""Algorithm Parameters page for the Streaming Guide wizard."""

import importlib

from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from core.services.LoggerService import LoggerService

from .BasePage import BasePage


class StreamAlgorithmParametersPage(BasePage):
    """Page for configuring streaming algorithm-specific parameters."""

    def __init__(self, wizard_data, settings_service, dialog):
        """Initialize the page."""
        super().__init__(wizard_data, settings_service, dialog)
        self.algorithm_widget = None
        self.active_algorithm = None
        self._last_algorithm_name = None

    def setup_ui(self):
        """Initialize UI components."""
        # The UI is set up in on_enter when we know which algorithm is selected
        pass

    def connect_signals(self):
        """Connect UI signals to handlers."""
        # Algorithm widget signals are connected when the widget is loaded
        # Connect skip guide checkbox if it exists
        if hasattr(self.dialog, "skipGuideCheckBox"):
            self.dialog.skipGuideCheckBox.stateChanged.connect(self._on_skip_changed)

    def load_data(self):
        """Load algorithm parameters if available."""
        # Parameters are loaded when the algorithm widget is created
        # Load skip guide preference
        if hasattr(self.dialog, "skipGuideCheckBox"):
            skip_raw = self.settings_service.get_setting("SkipStreamingGuide", "No")
            skip_val = self.wizard_data.get("skip_guide")
            if skip_val is None:
                skip_val = str(skip_raw).strip().lower() == "yes"
            self.dialog.skipGuideCheckBox.setChecked(skip_val)

    def save_data(self):
        """Save algorithm parameters to wizard_data."""
        # Ensure object size (min_area/max_area) is applied before saving
        # This handles cases where object size was changed after visiting this page
        if self.algorithm_widget:
            self._apply_object_size_to_algorithm()

        if self.algorithm_widget and self.active_algorithm:
            # Get options from the algorithm widget (wizard controllers use get_options)
            if hasattr(self.algorithm_widget, 'get_options'):
                options = self.algorithm_widget.get_options()
                self.wizard_data['algorithm_options'] = options
            elif hasattr(self.algorithm_widget, 'get_config'):
                # Fallback to get_config for compatibility
                config = self.algorithm_widget.get_config()
                self.wizard_data['algorithm_config'] = config
            # Store algorithm name for reference
            self.wizard_data['algorithm_name'] = self.active_algorithm

        # Save skip guide preference
        if hasattr(self.dialog, "skipGuideCheckBox"):
            self.wizard_data["skip_guide"] = self.dialog.skipGuideCheckBox.isChecked()

    def on_enter(self):
        """Called when entering the page."""
        # Get the selected algorithm from wizard_data
        selected_algorithm = self.wizard_data.get('algorithm')
        if not selected_algorithm:
            return

        # The algorithm is already stored as a key (ColorDetection, etc.)
        # but might be a display name, so map it if needed
        algorithm_map = {
            "Color Detection": "ColorDetection",
            "Color Anomaly & Motion Detection": "ColorAnomalyAndMotionDetection"
        }

        # If it's a display name, convert to key; otherwise use as-is
        algorithm_key = algorithm_map.get(selected_algorithm, selected_algorithm)
        self.active_algorithm = algorithm_key

        # Load the algorithm widget
        self._load_algorithm_widget()

    def on_exit(self):
        """Called when leaving the page."""
        # Save algorithm parameters
        self.save_data()

    def _load_algorithm_widget(self):
        """Load the algorithm-specific widget based on the selected algorithm."""
        if not self.active_algorithm:
            return

        current_algorithm_name = self.active_algorithm

        # Check if we already have a widget for this algorithm
        if self.algorithm_widget and self._last_algorithm_name == current_algorithm_name:
            # Algorithm hasn't changed, widget is already loaded - keep it
            return

        # Clear existing widget (only if algorithm changed or no widget exists)
        if self.algorithm_widget:
            # Remove from layout
            container = self.dialog.algorithmParametersContainer
            layout = container.layout()
            if layout:
                layout.removeWidget(self.algorithm_widget)
            self.algorithm_widget.deleteLater()
            self.algorithm_widget = None

        try:
            # Import the algorithm wizard controller dynamically
            algorithm_wizard_modules = {
                "ColorDetection": (
                    "algorithms.streaming.ColorDetection.controllers."
                    "ColorDetectionWizardController"
                ),
                "ColorAnomalyAndMotionDetection": (
                    "algorithms.streaming.ColorAnomalyAndMotionDetection.controllers."
                    "ColorAnomalyAndMotionDetectionWizardController"
                )
            }

            module_path = algorithm_wizard_modules.get(current_algorithm_name)
            if not module_path:
                raise ValueError(f"Unknown algorithm: {current_algorithm_name}")

            # Import the module and get the wizard controller class
            # The module_path is the full path to the module (e.g., algorithms.streaming.MotionDetection.controllers.MotionDetectionWizardController)
            # The class name is the same as the module name (last part)
            module_parts = module_path.split('.')
            module_name = module_path  # Import the full module path
            class_name = module_parts[-1]  # Class name is the last part

            logger = LoggerService()
            # logger.info(f"Importing module: {module_name}, looking for class: {class_name}")

            # Import the module (the .py file)
            try:
                module = importlib.import_module(module_name)
                # logger.info(f"Successfully imported module: {module}, type: {type(module)}")
                # logger.info(f"Module attributes: {[attr for attr in dir(module) if not attr.startswith('_')]}")
            except Exception as e:
                logger.error(f"Failed to import module {module_name}: {e}")
                raise

            # Get the class from the module (class name matches module name)
            if not hasattr(module, class_name):
                # List all attributes to help debug
                all_attrs = [attr for attr in dir(module) if not attr.startswith('_')]
                available_classes = [attr for attr in all_attrs if isinstance(getattr(module, attr, None), type)]
                raise ValueError(
                    f"Class '{class_name}' not found in module '{module_name}'. Available classes: {available_classes}, All attributes: {all_attrs[:20]}")

            controller_class = getattr(module, class_name)
            # logger.info(f"Got controller_class: {controller_class}, type: {type(controller_class)}, callable: {callable(controller_class)}")

            # Check if it's a module (common mistake)
            if isinstance(controller_class, type(module)):
                raise ValueError(f"'{class_name}' from '{module_name}' is a module, not a class. This usually means there's a package/namespace conflict.")

            # Verify it's actually a class
            if not isinstance(controller_class, type):
                raise ValueError(f"'{class_name}' from '{module_name}' is not a class (got {type(controller_class)}, value: {controller_class})")
            if not callable(controller_class):
                raise ValueError(f"'{class_name}' from '{module_name}' is not callable (got {type(controller_class)})")

            # Get theme
            theme = self.settings_service.get_setting('Theme', 'Dark')

            # Update the page title
            try:
                page_title_widget = getattr(self.dialog, 'labelPageAlgorithmParametersTitle', None)
                if page_title_widget is not None:
                    algorithm_labels = {
                        "ColorDetection": self.tr("Color Detection"),
                        "ColorAnomalyAndMotionDetection": self.tr("Color Anomaly & Motion Detection")
                    }
                    algo_label = algorithm_labels.get(current_algorithm_name, self.tr("Algorithm"))
                    page_title_widget.setText(
                        self.tr("{algorithm} Parameters").format(algorithm=algo_label)
                    )
            except Exception:
                # Best-effort only; ignore if not available
                pass

            # Logger already created above
            # logger.info(f"Loading streaming algorithm wizard controller: {controller_class} for {current_algorithm_name}")

            # Create algorithm config dict
            algorithm_config = {
                'name': current_algorithm_name,
                'label': algorithm_labels.get(current_algorithm_name, current_algorithm_name)
            }

            # Create the algorithm wizard widget
            self.algorithm_widget = controller_class(algorithm_config, theme)

            # Connect validation_changed signal if available
            if hasattr(self.algorithm_widget, 'validation_changed'):
                self.algorithm_widget.validation_changed.connect(self._on_validation_changed)

            # Track which algorithm we just loaded
            self._last_algorithm_name = current_algorithm_name

            # Add to the container layout
            container = self.dialog.algorithmParametersContainer
            layout = container.layout()
            if layout is None:
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(self.algorithm_widget)

            # Calculate and set min/max area from object size and GSD
            self._apply_object_size_to_algorithm()

            # Load saved options if they match the current algorithm
            saved_algorithm_name = self.wizard_data.get('algorithm_name')
            if (saved_algorithm_name == current_algorithm_name and
                    'algorithm_options' in self.wizard_data and
                    hasattr(self.algorithm_widget, 'load_options')):
                self.algorithm_widget.load_options(self.wizard_data['algorithm_options'])

        except Exception as e:
            # Log error and show a message
            logger = LoggerService()
            logger.error(f"Error loading algorithm widget: {e}")

            # Show error label
            error_label = QLabel(f"Error loading algorithm parameters: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red;")

            container = self.dialog.algorithmParametersContainer
            layout = container.layout()
            if layout is None:
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(error_label)

    def _on_validation_changed(self):
        """Handle validation state change from algorithm widget."""
        # Trigger navigation button update to reflect new validation state
        if hasattr(self.dialog, '_update_navigation_buttons'):
            self.dialog._update_navigation_buttons()

    def validate(self) -> bool:
        """Validate that algorithm parameters are valid."""
        if not self.algorithm_widget:
            return False

        # Use the algorithm widget's validation
        if hasattr(self.algorithm_widget, 'validate'):
            validation_error = self.algorithm_widget.validate()
            if validation_error:
                return False

        return True

    def _on_skip_changed(self, state: int) -> None:
        """Handle skip guide checkbox change."""
        self.wizard_data["skip_guide"] = state == Qt.Checked

    def _apply_object_size_to_algorithm(self):
        """Calculate and apply min/max area from object size and GSD to algorithm widget.

        If GSD cannot be calculated, this method returns early and the algorithm widget
        will use its default min/max area values (same behavior as Image Analysis Guide).
        """
        if not self.algorithm_widget:
            return

        # Get object size from wizard_data
        object_size_min_ft = self.wizard_data.get('object_size_min')
        object_size_max_ft = self.wizard_data.get('object_size_max')

        if not object_size_min_ft or not object_size_max_ft:
            # No object size specified - algorithm will use defaults
            return

        # Get GSD from wizard_data
        gsd_list = self.wizard_data.get('gsd_list', [])
        if not gsd_list:
            # No GSD available - algorithm will use default min/max area values
            return

        # Use the first GSD value from the list
        gsd_values = [item.get('gsd') for item in gsd_list if item.get('gsd')]
        if not gsd_values:
            # No valid GSD values - algorithm will use default min/max area values
            return

        gsd_cm_per_pixel = gsd_values[0]

        # Convert object size from square feet to pixels using GSD
        # Formula: object_size_cm = object_size_ft * 30.48 (ft to cm)
        # pixels = object_size_cm / gsd_cm_per_pixel
        # area_pixels = pixels^2
        min_pixels = (object_size_min_ft * 30.48) / gsd_cm_per_pixel
        max_pixels = (object_size_max_ft * 30.48) / gsd_cm_per_pixel

        # Calculate area in pixels (square the linear dimension)
        # For min_area, use the same formula as MainWindow (divide by 250 for scaling)
        min_area = max(10, int((min_pixels * min_pixels) / 250))
        max_area = max(100, int(max_pixels * max_pixels))

        # Apply to algorithm widget if it has load_options
        if hasattr(self.algorithm_widget, 'load_options'):
            # Get existing options or create new dict
            existing_options = {}
            if hasattr(self.algorithm_widget, 'get_options'):
                existing_options = self.algorithm_widget.get_options() or {}

            # Update with calculated min/max area
            existing_options['min_area'] = min_area
            existing_options['max_area'] = max_area

            # Load the updated options
            self.algorithm_widget.load_options(existing_options)
