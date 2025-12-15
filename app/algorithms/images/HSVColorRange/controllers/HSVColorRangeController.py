import qtawesome as qta

from ast import literal_eval

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.HSVColorRange.views.HSVColorRange_ui import Ui_HSVColorRange
from algorithms.Shared.views import HSVColorRowWidget
from algorithms.images.HSVColorRange.controllers.HSVColorRangeViewerController import HSVColorRangeRangeViewer
from core.services.LoggerService import LoggerService
from algorithms.images.Shared.views.ColorSelectionMenu import ColorSelectionMenu
from core.services.color.CustomColorsService import get_custom_colors_service
from core.services.color.RecentColorsService import get_recent_colors_service
from helpers.IconHelper import IconHelper

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QColorDialog, QLabel, QSizePolicy, QScrollArea,
                               QVBoxLayout, QPushButton, QHBoxLayout, QSpacerItem)
from PySide6.QtCore import Qt


class HSVColorRangeController(QWidget, Ui_HSVColorRange, AlgorithmController):
    """Controller for the HSV Filter algorithm widget supporting multiple colors."""

    def __init__(self, config, theme):
        """
        Initializes the HSVColorRangeController widget and sets up the UI.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)

        # Match RGB Color Range layout spacing and margins
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # Hide old single-color UI elements (hide widgets, not layouts)
        if hasattr(self, 'colorSample'):
            self.colorSample.hide()
        # Remove legacy layouts to eliminate extra vertical space
        try:
            if hasattr(self, 'ColorSelectionLayout'):
                self.verticalLayout.removeItem(self.ColorSelectionLayout)
            if hasattr(self, 'ColorRangeLayout'):
                self.verticalLayout.removeItem(self.ColorRangeLayout)
        except Exception:
            pass
        # Note: colorButton will be reused as addColorButton, so don't hide it
        # Hide widgets in SpinBoxLayout
        if hasattr(self, 'hueSensitivityLabel'):
            self.hueSensitivityLabel.hide()
        if hasattr(self, 'hueMinusLabel'):
            self.hueMinusLabel.hide()
        if hasattr(self, 'hueMinusSpinBox'):
            self.hueMinusSpinBox.hide()
        if hasattr(self, 'huePlusLabel'):
            self.huePlusLabel.hide()
        if hasattr(self, 'huePlusSpinBox'):
            self.huePlusSpinBox.hide()
        if hasattr(self, 'saturationSensitivityLabel'):
            self.saturationSensitivityLabel.hide()
        if hasattr(self, 'saturationMinusLabel'):
            self.saturationMinusLabel.hide()
        if hasattr(self, 'saturationMinusSpinBox'):
            self.saturationMinusSpinBox.hide()
        if hasattr(self, 'saturationPlusLabel'):
            self.saturationPlusLabel.hide()
        if hasattr(self, 'saturationPlusSpinBox'):
            self.saturationPlusSpinBox.hide()
        if hasattr(self, 'valueSensitivityLabel'):
            self.valueSensitivityLabel.hide()
        if hasattr(self, 'valueMinusLabel'):
            self.valueMinusLabel.hide()
        if hasattr(self, 'valueMinusSpinBox'):
            self.valueMinusSpinBox.hide()
        if hasattr(self, 'valuePlusLabel'):
            self.valuePlusLabel.hide()
        if hasattr(self, 'valuePlusSpinBox'):
            self.valuePlusSpinBox.hide()

        # Create scroll area for multiple color rows (if not in UI)
        if not hasattr(self, 'scrollArea'):
            self._create_scroll_area()

        # List of color row widgets
        self.color_rows = []

        # Empty state label
        self.emptyLabel = QLabel("No Colors Selected", self.scrollAreaWidgetContents)
        self.emptyLabel.setAlignment(Qt.AlignCenter)
        self.emptyLabel.setStyleSheet("color: #888; font-style: italic;")
        self.emptyLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Add as the first item so it sits in the center when there are no rows
        self.colorsLayout.addWidget(self.emptyLabel, 1, Qt.AlignCenter)

        # Connect signals
        self.viewRangeButton.clicked.connect(self.view_range_button_clicked)
        self.viewRangeButton.hide()  # Hide until at least one color is added

        # Move viewRangeButton to top (like ColorRange algorithm)
        # Remove it from ColorRangeLayout (bottom) and add to button layout at top
        if hasattr(self, 'ColorRangeLayout'):
            self.ColorRangeLayout.removeWidget(self.viewRangeButton)

        # Common color selection menu with HSV picker support
        # Rename colorButton to addColorButton for consistency
        if hasattr(self, 'colorButton'):
            self.addColorButton = self.colorButton
            self.addColorButton.setText("Add Color")  # Update button text
        elif not hasattr(self, 'addColorButton'):
            # Create add button if it doesn't exist
            self.addColorButton = QPushButton("Add Color")

        # Create button layout at top (like ColorRange)
        if not hasattr(self, 'buttonLayout'):
            self.buttonLayout = QHBoxLayout()
            # Match RGB margins/spacing
            try:
                self.buttonLayout.setContentsMargins(0, 0, 0, 0)
                self.buttonLayout.setSpacing(6)
            except Exception:
                pass
            self.buttonLayout.addWidget(self.addColorButton)
            spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.buttonLayout.addItem(spacer)
            self.buttonLayout.addWidget(self.viewRangeButton)
            # Insert at the top of verticalLayout
            self.verticalLayout.insertLayout(0, self.buttonLayout)

        self.color_selection_menu = ColorSelectionMenu(
            self,
            on_color_selected=self._on_color_selected_from_menu,
            get_default_qcolor=self._get_default_qcolor,
            on_hsv_selected=self._on_hsv_selected_from_menu,
            get_initial_hsv=self._get_initial_hsv,
            get_initial_ranges=self._get_initial_ranges,
            on_recent_color_selected=self._on_recent_color_selected,
            mode='HSV'
        )
        self.color_selection_menu.attach_to(self.addColorButton)

        # Recent colors service
        self.recent_colors_service = get_recent_colors_service()

        self._apply_icons(theme)

        # Enable scrolling when more than 3 colors
        self._update_scroll_area()
        # Update empty state visibility
        self._update_empty_state()

    def _create_scroll_area(self):
        """Create scroll area for color rows if not in UI file."""
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.scrollAreaWidgetContents = QWidget()
        self.colorsLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.colorsLayout.setSpacing(6)
        self.colorsLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        # Add scroll area now; the top button bar will be inserted later at index 0
        self.verticalLayout.addWidget(self.scrollArea)

    def _get_default_qcolor(self):
        """Return the most recent color or a sensible default."""
        if self.color_rows:
            return self.color_rows[-1].get_color()
        return QColor(255, 0, 0)

    def _get_initial_hsv(self):
        """Get initial HSV values for HSV picker."""
        if self.color_rows:
            return self.color_rows[-1].get_hsv_ranges()['h'], \
                self.color_rows[-1].get_hsv_ranges()['s'], \
                self.color_rows[-1].get_hsv_ranges()['v']
        return (0, 1, 1)  # Default red

    def _get_initial_ranges(self):
        """Get initial range values for HSV picker."""
        if self.color_rows:
            hsv_ranges = self.color_rows[-1].get_hsv_ranges()
            return {
                'h_minus': hsv_ranges['h_minus'],
                'h_plus': hsv_ranges['h_plus'],
                's_minus': hsv_ranges['s_minus'],
                's_plus': hsv_ranges['s_plus'],
                'v_minus': hsv_ranges['v_minus'],
                'v_plus': hsv_ranges['v_plus']
            }
        # Default ranges
        return {
            'h_minus': 20 / 179,
            'h_plus': 20 / 179,
            's_minus': 50 / 255,
            's_plus': 50 / 255,
            'v_minus': 50 / 255,
            'v_plus': 50 / 255
        }

    def _on_color_selected_from_menu(self, color: QColor):
        """Handle color selection from standard color pickers (QColor)."""
        if not color.isValid():
            return
        self.add_color_row(color)

        # Don't track immediately - let user adjust ranges first
        # Colors will be tracked when actually used (via get_options)

    def _on_hsv_selected_from_menu(self, hsv_data: dict):
        """Handle HSV range selection from HSV picker."""
        try:
            # Save any custom colors that may have been modified
            custom_colors_service = get_custom_colors_service()
            custom_colors_service.sync_with_dialog()

            # Add color row with HSV ranges
            h, s, v = hsv_data['h'], hsv_data['s'], hsv_data['v']
            color = QColor.fromHsvF(h, s, v)
            self.add_color_row(color, hsv_ranges=hsv_data)

            # Don't track immediately - colors will be tracked when actually used (via get_options)
        except Exception as e:
            self.logger.error(f"Error handling HSV selection: {e}")

    def _on_recent_color_selected(self, color_data: dict):
        """Handle selection from recent colors list."""
        try:
            selected_color = color_data.get('selected_color', (255, 0, 0))
            r, g, b = selected_color
            color = QColor(r, g, b)
            hsv_ranges = color_data.get('hsv_ranges')
            self.add_color_row(color, hsv_ranges=hsv_ranges)
        except Exception as e:
            self.logger.error(f"Error handling recent color selection: {e}")

    def add_color_row(self, color, h_minus=None, h_plus=None, s_minus=None, s_plus=None,
                      v_minus=None, v_plus=None, hsv_ranges=None):
        """
        Add a new HSV color row widget.

        Args:
            color: QColor or tuple (r, g, b) for the target color
            h_minus, h_plus: Hue range in OpenCV scale (0-179), converted to fractional internally
            s_minus, s_plus: Saturation range as percentage (0-100), converted to fractional internally
            v_minus, v_plus: Value range as percentage (0-100), converted to fractional internally
            hsv_ranges: Dict with HSV range data in fractional format (0-1) with keys:
                h, s, v (center values, fractional 0-1)
                h_minus, h_plus, s_minus, s_plus, v_minus, v_plus (range values, fractional 0-1)
        """
        row = HSVColorRowWidget(self.scrollAreaWidgetContents, color, h_minus, h_plus,
                                s_minus, s_plus, v_minus, v_plus, hsv_ranges)
        row.delete_requested.connect(self.remove_color_row)
        row.changed.connect(self._on_color_changed)

        self.color_rows.append(row)
        self.colorsLayout.addWidget(row)

        self._update_view_range_button()
        self._update_scroll_area()
        self._update_empty_state()

    def remove_color_row(self, row):
        """
        Remove a color row widget.

        Args:
            row: HSVColorRowWidget instance to remove
        """
        if row in self.color_rows:
            self.color_rows.remove(row)
            self.colorsLayout.removeWidget(row)
            row.deleteLater()

            self._update_view_range_button()
            self._update_scroll_area()
            self._update_empty_state()

    def _on_color_changed(self):
        """Handle when any color row changes."""
        self._update_view_range_button()

    def _update_view_range_button(self):
        """Show/hide view range button based on whether colors are configured."""
        if self.color_rows:
            self.viewRangeButton.show()
        else:
            self.viewRangeButton.hide()

    def _update_empty_state(self):
        """Show a centered message when no colors are configured."""
        if self.color_rows:
            self.emptyLabel.hide()
        else:
            self.emptyLabel.show()

    def _update_scroll_area(self):
        """Enable scrolling when more than 3 colors are present."""
        # Calculate approximate height per row (swatch 35px + margins/spacing ~45px total)
        row_height = 45
        spacing = 6

        if len(self.color_rows) > 3:
            # Fixed height to show exactly 3 rows, enable scrolling for more
            fixed_height = 3 * row_height + 2 * spacing + 10
            self.scrollArea.setMinimumHeight(fixed_height)
            self.scrollArea.setMaximumHeight(fixed_height)
            self.scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            # Expand to fit all rows (up to 3), no scrolling needed
            if self.color_rows:
                total_height = len(self.color_rows) * row_height + (len(self.color_rows) - 1) * spacing + 10
                self.scrollArea.setMinimumHeight(total_height)
                self.scrollArea.setMaximumHeight(total_height)
                self.scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            else:
                # No rows - match ColorRange behavior (fill available space)
                self.scrollArea.setMinimumHeight(0)
                self.scrollArea.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

    def view_range_button_clicked(self):
        """
        Handles the view range button click.

        Opens the View Range dialog, displaying detection regions for all
        configured HSV colors. For multiple colors, the viewer combines them (OR).
        """
        if not self.color_rows:
            return

        # Build HSV ranges list for viewer (multi-color mode)
        hsv_ranges_list = []
        for row in self.color_rows:
            hsv_ranges = row.get_hsv_ranges()
            rgb = row.get_rgb()

            # Convert fractional ranges (0-1) to OpenCV format (0-179 for hue, 0-255 for sat/val)
            hsv_ranges_list.append({
                'rgb': rgb,
                'hue_minus': int(hsv_ranges['h_minus'] * 179),  # Convert fractional to OpenCV (0-179)
                'hue_plus': int(hsv_ranges['h_plus'] * 179),
                'sat_minus': int(hsv_ranges['s_minus'] * 255),  # Convert fractional to OpenCV (0-255)
                'sat_plus': int(hsv_ranges['s_plus'] * 255),
                'val_minus': int(hsv_ranges['v_minus'] * 255),
                'val_plus': int(hsv_ranges['v_plus'] * 255)
            })

        # Pass all colors to viewer using multi-color mode
        if hsv_ranges_list:
            rangeDialog = HSVColorRangeRangeViewer(hsv_ranges_list=hsv_ranges_list)
            rangeDialog.exec()

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing selected options. Supports both:
                - New format: 'hsv_configs' (list of HSV configs)
                - Legacy format: 'hsv_ranges', 'selected_color', etc. (for backward compatibility)
        """
        options = dict()

        if not self.color_rows:
            # Return empty/None values if no colors configured
            options['hsv_configs'] = []
            options['hsv_ranges'] = None
            options['selected_color'] = None
            options['hue_threshold'] = None
            options['saturation_threshold'] = None
            options['value_threshold'] = None
            return options

        # New format: list of HSV configurations
        hsv_configs = []
        for row in self.color_rows:
            hsv_ranges = row.get_hsv_ranges()
            rgb = row.get_rgb()
            hsv_config = {
                'selected_color': rgb,
                'hsv_ranges': hsv_ranges
            }
            hsv_configs.append(hsv_config)

            # Track this color in recent colors (it's being used for processing)
            try:
                self.recent_colors_service.add_hsv_color(hsv_config)
            except Exception as e:
                self.logger.error(f"Error tracking recent color: {e}")

        options['hsv_configs'] = hsv_configs

        # Legacy format: use first color for backward compatibility
        first_row = self.color_rows[0]
        first_hsv_ranges = first_row.get_hsv_ranges()
        options['hsv_ranges'] = first_hsv_ranges
        options['selected_color'] = first_row.get_rgb()
        options['hue_threshold'] = int((first_hsv_ranges['h_minus'] + first_hsv_ranges['h_plus']) * 90)
        options['saturation_threshold'] = int((first_hsv_ranges['s_minus'] + first_hsv_ranges['s_plus']) * 127)
        options['value_threshold'] = int((first_hsv_ranges['v_minus'] + first_hsv_ranges['v_plus']) * 127)

        return options

    def validate(self):
        """
        Validates that at least one color has been configured.

        Returns:
            str: An error message if validation fails, otherwise None.
        """
        if not self.color_rows:
            return "Please add at least one color to detect."
        return None

    def load_options(self, options):
        """
        Sets UI elements based on the provided options.

        Supports both new format (hsv_configs list) and legacy format
        (single hsv_ranges or selected_color + thresholds).

        Args:
            options (dict): The options to use to set UI attributes.
        """
        # Clear existing color rows
        for row in self.color_rows[:]:
            self.remove_color_row(row)

        # Try new format first
        if 'hsv_configs' in options and options['hsv_configs']:
            hsv_configs = options['hsv_configs']
            # Handle string format (from literal_eval in some cases)
            if isinstance(hsv_configs, str):
                hsv_configs = literal_eval(hsv_configs)

            for hsv_config in hsv_configs:
                if isinstance(hsv_config, dict):
                    selected_color = hsv_config.get('selected_color')
                    hsv_ranges = hsv_config.get('hsv_ranges')

                    if isinstance(selected_color, str):
                        selected_color = literal_eval(selected_color)
                    if isinstance(hsv_ranges, str):
                        hsv_ranges = literal_eval(hsv_ranges)

                    if selected_color:
                        color = QColor(selected_color[0], selected_color[1], selected_color[2])
                        self.add_color_row(color, hsv_ranges=hsv_ranges)

        # Fall back to legacy format: hsv_ranges
        elif 'hsv_ranges' in options and options['hsv_ranges']:
            hsv_ranges = options['hsv_ranges']
            if isinstance(hsv_ranges, str):
                hsv_ranges = literal_eval(hsv_ranges)

            selected_color = options.get('selected_color')
            if isinstance(selected_color, str):
                selected_color = literal_eval(selected_color)

            if selected_color:
                color = QColor(selected_color[0], selected_color[1], selected_color[2])
                self.add_color_row(color, hsv_ranges=hsv_ranges)

        # Fall back to older legacy format: selected_color + thresholds
        elif 'selected_color' in options and options['selected_color']:
            selected_color = options['selected_color']
            if isinstance(selected_color, str):
                selected_color = literal_eval(selected_color)

            color = QColor(selected_color[0], selected_color[1], selected_color[2])

            # Get thresholds if available
            h_minus = options.get('hue_threshold', 20)
            h_plus = options.get('hue_threshold', 20)
            s_minus = options.get('saturation_threshold', 50)
            s_plus = options.get('saturation_threshold', 50)
            v_minus = options.get('value_threshold', 50)
            v_plus = options.get('value_threshold', 50)

            self.add_color_row(color, h_minus, h_plus, s_minus, s_plus, v_minus, v_plus)

        self._update_view_range_button()
        self._update_scroll_area()
        self._update_empty_state()

    def _apply_icons(self, theme):
        """
        Loads icon assets based on the currently selected theme.

        Args:
            theme (str): Name of the active theme used to resolve icon paths.
        """
        if hasattr(self, 'addColorButton'):
            self.addColorButton.setIcon(IconHelper.create_icon('fa6s.palette', theme))
        self.viewRangeButton.setIcon(IconHelper.create_icon('fa6s.eye', theme))
