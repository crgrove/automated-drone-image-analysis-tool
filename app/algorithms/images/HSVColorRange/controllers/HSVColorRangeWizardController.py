"""
Wizard controller for Color Range (HSV) algorithm.

Provides a simplified, guided interface for configuring HSV color range detection.
"""

from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QPushButton
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
import cv2
import numpy as np
from ast import literal_eval

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.HSVColorRange.views.HSVColorRangeWizard_ui import Ui_HSVColorRangeWizard
from algorithms.images.HSVColorRange.views.HSVColorRowWizardWidget import HSVColorRowWizardWidget
from algorithms.images.HSVColorRange.controllers.HSVColorRangeViewerController import HSVColorRangeRangeViewer
from algorithms.images.Shared.views.ColorSelectionMenu import ColorSelectionMenu
from helpers.IconHelper import IconHelper


class HSVColorRangeWizardController(QWidget, Ui_HSVColorRangeWizard, AlgorithmController):
    """Wizard controller for Color Range (HSV) algorithm."""

    # Signal emitted when validation state changes (e.g., when rows are added/removed)
    validation_changed = Signal()

    def __init__(self, config, theme):
        """Initialize the wizard controller."""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme

        # List of color row widgets
        self.color_rows = []

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults."""
        # Update container layout spacing and margins to 0 for table appearance
        self.colorsLayout.setSpacing(0)
        self.colorsLayout.setContentsMargins(0, 0, 0, 0)

        # Empty state label
        self.emptyLabel = QLabel("No Colors Selected", self.colorsContainer)
        self.emptyLabel.setAlignment(Qt.AlignCenter)
        self.emptyLabel.setStyleSheet("color: #888; font-style: italic;")
        self.emptyLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.colorsLayout.addWidget(self.emptyLabel, 1, Qt.AlignCenter)

        # View Range button (hidden until colors are added)
        self.viewRangeButton = QPushButton("View Range", self.widgetAddButton)
        self.viewRangeButton.setFont(self.addColorButton.font())
        self.viewRangeButton.setIcon(IconHelper.create_icon('fa6s.eye', self.theme))
        self.viewRangeButton.clicked.connect(self.view_range_button_clicked)
        self.viewRangeButton.hide()
        # Insert before the spacer
        self.horizontalLayout_add.insertWidget(1, self.viewRangeButton)

        # Common color selection menu (HSV mode with HSV picker)
        self.color_selection_menu = ColorSelectionMenu(
            self,
            on_color_selected=self._on_color_selected_from_menu,
            get_default_qcolor=self._get_default_qcolor,
            on_hsv_selected=self._on_hsv_selected_from_picker,
            mode='HSV'
        )
        self.color_selection_menu.attach_to(self.addColorButton)

        # Update empty state visibility
        self._update_empty_state()
        self._update_view_range_button()
        self.validation_changed.emit()

        # Ensure an in-page widget has focus so the dialog Close button doesn't take it
        try:
            self.addColorButton.setFocus(Qt.OtherFocusReason)
        except Exception:
            pass

    def _get_default_qcolor(self):
        """Return the most recent color or a sensible default."""
        if self.color_rows:
            return self.color_rows[-1].get_color()
        return QColor(255, 0, 0)

    def _on_color_selected_from_menu(self, color: QColor):
        """Handle color chosen from the shared color selection menu."""
        self.add_color_row(color)

    def _on_hsv_selected_from_picker(self, hsv_data: dict):
        """Handle HSV color range selected from HSV picker dialog."""
        # Extract the center HSV color from the data
        # The dialog returns 'center_hsv' or we can use 'h', 's', 'v' directly
        if 'center_hsv' in hsv_data:
            h, s, v = hsv_data['center_hsv']
        elif 'h' in hsv_data and 's' in hsv_data and 'v' in hsv_data:
            # Convert from 0-1 range to OpenCV range (0-179, 0-255, 0-255)
            h = int(hsv_data['h'] * 179)
            s = int(hsv_data['s'] * 255)
            v = int(hsv_data['v'] * 255)
        else:
            return  # Invalid data

        # Convert HSV to RGB (OpenCV format: H=0-179, S=0-255, V=0-255)
        # If we have fractional values, use them directly
        if 'h' in hsv_data and isinstance(hsv_data['h'], float) and 0 <= hsv_data['h'] <= 1:
            # Already in 0-1 range, convert to OpenCV for RGB conversion
            h_cv = int(hsv_data['h'] * 179)
            s_cv = int(hsv_data['s'] * 255)
            v_cv = int(hsv_data['v'] * 255)
        else:
            # Already in OpenCV range
            h_cv, s_cv, v_cv = h, s, v

        hsv_array = np.uint8([[[h_cv, s_cv, v_cv]]])
        bgr = cv2.cvtColor(hsv_array, cv2.COLOR_HSV2BGR)[0][0]
        b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2])
        color = QColor(r, g, b)
        # Pass the full hsv_data dict so ranges can be displayed
        self.add_color_row(color, from_hsv_picker=True, hsv_ranges=hsv_data)

    def add_color_row(self, color, tolerance_index=2, from_hsv_picker=False, hsv_ranges=None):
        """
        Add a new color row widget.

        Args:
            color: QColor or tuple (r, g, b) for the target color
            tolerance_index: Tolerance preset index (0-4, default 2 = Moderate)
            from_hsv_picker: If True, color was added via HSV picker (show ranges instead of tolerance dropdown)
            hsv_ranges: Optional dict with HSV ranges (h, s, v, h_minus, h_plus, etc.) when from_hsv_picker is True
        """
        row = HSVColorRowWizardWidget(self.colorsContainer, color, tolerance_index, from_hsv_picker=from_hsv_picker)
        row.delete_requested.connect(self.remove_color_row)
        row.changed.connect(self._on_color_changed)

        # Set HSV ranges if provided (after connecting signals so display updates properly)
        if from_hsv_picker and hsv_ranges:
            row.hsv_ranges = hsv_ranges
            # Force update the display and visibility
            row._apply_mode_visibility()

        self.color_rows.append(row)
        self.colorsLayout.addWidget(row, 0, Qt.AlignTop)

        # Clear focus from Add Color button
        self.addColorButton.clearFocus()

        # Update border styles for all rows to maintain table appearance
        self._update_row_borders()

        self._update_empty_state()
        self._update_view_range_button()
        self.validation_changed.emit()

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

            # Update border styles for all rows to maintain table appearance
            self._update_row_borders()

            self._update_empty_state()
            self._update_view_range_button()

    def _update_row_borders(self):
        """Update border styles for all rows to create table appearance."""
        for row in self.color_rows:
            if hasattr(row, '_update_border_style'):
                row._update_border_style()

    def _on_color_changed(self):
        """Handle when any color row changes."""
        pass  # Could add validation or other updates here

    def _update_empty_state(self):
        """Show a centered message when no colors are configured."""
        if self.color_rows:
            self.emptyLabel.hide()
        else:
            self.emptyLabel.show()

    def _update_view_range_button(self):
        """Show/hide view range button based on whether colors are configured."""
        if self.color_rows:
            self.viewRangeButton.show()
        else:
            self.viewRangeButton.hide()

    def view_range_button_clicked(self):
        """
        Handles the view range button click.

        Opens the View Range dialog, displaying detection regions for all
        configured HSV colors. For multiple colors, the viewer combines them (OR).
        """
        if not self.color_rows:
            return

        # Build color config list for viewer
        color_configs = []
        for row in self.color_rows:
            rgb = row.get_rgb()
            if hasattr(row, 'has_hsv_ranges') and row.has_hsv_ranges():
                ranges = row.get_hsv_ranges_fractional()
                # Use the sum of +/- to produce an approximate integer threshold
                h_avg = int((ranges['h_minus'] + ranges['h_plus']) * 90)
                s_avg = int((ranges['s_minus'] + ranges['s_plus']) * 127)
                v_avg = int((ranges['v_minus'] + ranges['v_plus']) * 127)
            else:
                h_range, s_range, v_range = row.get_tolerance_values()  # integer ranges
                h_avg, s_avg, v_avg = h_range, s_range, v_range

            color_configs.append({
                'selected_color': rgb,
                'hue_threshold': h_avg,
                'saturation_threshold': s_avg,
                'value_threshold': v_avg
            })

        # For now, use first color for backward compatibility with viewer
        # TODO: Update viewer to handle multiple colors
        if color_configs:
            first_config = color_configs[0]
            rangeDialog = HSVColorRangeRangeViewer(
                first_config['selected_color'],
                first_config['hue_threshold'],
                first_config['saturation_threshold'],
                first_config['value_threshold']
            )
            rangeDialog.exec()

    def get_options(self):
        """Get algorithm options mapped to service-expected keys (like non-wizard)."""
        options = dict()

        if not self.color_rows:
            # Expected by services
            options['hsv_configs'] = []
            options['hsv_ranges'] = None
            options['selected_color'] = None
            options['hue_threshold'] = None
            options['saturation_threshold'] = None
            options['value_threshold'] = None
            return options

        # New format: list of HSV configurations (matches non-wizard controller)
        hsv_configs = []
        for row in self.color_rows:
            rgb = row.get_rgb()
            if hasattr(row, 'get_hsv_ranges_fractional'):
                ranges = row.get_hsv_ranges_fractional()
                hsv_ranges = {
                    'h': ranges.get('h'),
                    's': ranges.get('s'),
                    'v': ranges.get('v'),
                    'h_minus': ranges['h_minus'],
                    'h_plus': ranges['h_plus'],
                    's_minus': ranges['s_minus'],
                    's_plus': ranges['s_plus'],
                    'v_minus': ranges['v_minus'],
                    'v_plus': ranges['v_plus'],
                }
            else:
                h_range, s_range, v_range = row.get_tolerance_values()  # All in OpenCV scale
                # Get center HSV values from the color
                h, s, v, _ = row.get_color().getHsvF()
                hsv_ranges = {
                    'h': h,
                    's': s,
                    'v': v,
                    'h_minus': h_range / 179.0,  # Convert from OpenCV scale (0-179) to fractional
                    'h_plus': h_range / 179.0,
                    's_minus': s_range / 255.0,  # Convert from OpenCV scale (0-255) to fractional
                    's_plus': s_range / 255.0,
                    'v_minus': v_range / 255.0,  # Convert from OpenCV scale (0-255) to fractional
                    'v_plus': v_range / 255.0,
                }
            hsv_configs.append({
                'selected_color': rgb,
                'hsv_ranges': hsv_ranges
            })
        options['hsv_configs'] = hsv_configs

        # Legacy format: derive thresholds from first row (using actual HSV ranges if available)
        first_row = self.color_rows[0]
        options['selected_color'] = first_row.get_rgb()
        if hasattr(first_row, 'has_hsv_ranges') and first_row.has_hsv_ranges():
            ranges = first_row.get_hsv_ranges_fractional()
            options['hsv_ranges'] = {
                'h': ranges.get('h'),
                's': ranges.get('s'),
                'v': ranges.get('v'),
                'h_minus': ranges['h_minus'],
                'h_plus': ranges['h_plus'],
                's_minus': ranges['s_minus'],
                's_plus': ranges['s_plus'],
                'v_minus': ranges['v_minus'],
                'v_plus': ranges['v_plus'],
            }
        else:
            h_range, s_range, v_range = first_row.get_tolerance_values()  # All in OpenCV scale
            # Get center HSV values from the color
            h, s, v, _ = first_row.get_color().getHsvF()
            options['hsv_ranges'] = {
                'h': h,
                's': s,
                'v': v,
                'h_minus': h_range / 179.0,  # Convert from OpenCV scale (0-179) to fractional
                'h_plus': h_range / 179.0,
                's_minus': s_range / 255.0,  # Convert from OpenCV scale (0-255) to fractional
                's_plus': s_range / 255.0,
                'v_minus': v_range / 255.0,  # Convert from OpenCV scale (0-255) to fractional
                'v_plus': v_range / 255.0,
            }
        options['hue_threshold'] = int((options['hsv_ranges']['h_minus'] + options['hsv_ranges']['h_plus']) * 90)
        options['saturation_threshold'] = int((options['hsv_ranges']['s_minus'] + options['hsv_ranges']['s_plus']) * 127)
        options['value_threshold'] = int((options['hsv_ranges']['v_minus'] + options['hsv_ranges']['v_plus']) * 127)
        return options

    def validate(self):
        """Validate configuration."""
        if not self.color_rows:
            return "Please add at least one color to detect."
        return None

    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return

        # Clear existing color rows
        for row in self.color_rows[:]:
            self.remove_color_row(row)

        # Try new format first
        if 'color_ranges' in options and options['color_ranges']:
            color_ranges = options['color_ranges']
            # Handle string format
            if isinstance(color_ranges, str):
                color_ranges = literal_eval(color_ranges)

            for color_config in color_ranges:
                if isinstance(color_config, dict):
                    selected_color = color_config.get('selected_color')
                    tolerance_index = color_config.get('tolerance_index', 2)  # Default to Moderate

                    if isinstance(selected_color, str):
                        selected_color = literal_eval(selected_color)

                    if selected_color:
                        color = QColor(selected_color[0], selected_color[1], selected_color[2])
                        self.add_color_row(color, tolerance_index)

        # Fall back to legacy single-color formats
        elif 'selected_color' in options and options['selected_color']:
            selected_color = options['selected_color']
            tolerance_index = options.get('tolerance_index', 2)

            if isinstance(selected_color, str):
                selected_color = literal_eval(selected_color)

            if selected_color:
                color = QColor(selected_color[0], selected_color[1], selected_color[2])
                self.add_color_row(color, tolerance_index)

        self._update_empty_state()
        self._update_view_range_button()
        # Note: validation_changed is already emitted by add_color_row/remove_color_row
