"""
Wizard controller for Color Detection algorithm.

Provides a simplified, guided interface for configuring HSV color detection.
"""

import cv2
import numpy as np

from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QPushButton, QDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
from ast import literal_eval

from algorithms.streaming.ColorDetection.views.ColorDetectionWizard_ui import Ui_ColorDetectionWizard
from algorithms.Shared.views.HSVColorRowWizardWidget import HSVColorRowWizardWidget
from algorithms.Shared.views.HSVColorRangeRangeViewer import HSVColorRangeRangeViewer
from algorithms.images.Shared.views.ColorSelectionMenu import ColorSelectionMenu
from helpers.IconHelper import IconHelper
from core.services.color.RecentColorsService import get_recent_colors_service
from helpers.TranslationMixin import TranslationMixin


class ColorDetectionWizardController(TranslationMixin, QWidget, Ui_ColorDetectionWizard):
    """Wizard controller for Color Detection algorithm."""

    # Signal emitted when validation state changes (e.g., when rows are added/removed)
    validation_changed = Signal()

    def __init__(self, config, theme):
        """Initialize the wizard controller.

        Args:
            config: Algorithm configuration dictionary.
            theme: Theme name for UI styling.
        """
        super().__init__()
        self.config = config
        self.theme = theme
        self.color_rows = []
        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults."""
        # Update container layout spacing and margins to 0 for table appearance
        self.colorsLayout.setSpacing(0)
        self.colorsLayout.setContentsMargins(0, 0, 0, 0)

        # Empty state label
        self.emptyLabel = QLabel(
            self.tr("No Colors Selected"),
            self.colorsContainer
        )
        self.emptyLabel.setAlignment(Qt.AlignCenter)
        self.emptyLabel.setStyleSheet("color: #888; font-style: italic;")
        self.emptyLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.colorsLayout.addWidget(self.emptyLabel, 1, Qt.AlignCenter)

        # View Range button (hidden until colors are added)
        self.viewRangeButton = QPushButton(
            self.tr("View Range"),
            self.widgetAddButton
        )
        self.viewRangeButton.setFont(self.addColorButton.font())
        self.viewRangeButton.setIcon(IconHelper.create_icon('fa6s.eye', self.theme))
        self.viewRangeButton.clicked.connect(self.view_range_button_clicked)
        self.viewRangeButton.hide()
        # Insert before the spacer
        self.horizontalLayout_add.insertWidget(1, self.viewRangeButton)

        # Recent colors service
        self.recent_colors_service = get_recent_colors_service()

        # Common color selection menu (HSV mode with HSV picker and recent colors)
        self.color_selection_menu = ColorSelectionMenu(
            self,
            on_color_selected=self._on_color_selected_from_menu,
            get_default_qcolor=self._get_default_qcolor,
            on_hsv_selected=self._on_hsv_selected_from_picker,
            on_recent_color_selected=self._on_recent_color_selected,
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

    def _on_recent_color_selected(self, color_data: dict):
        """Handle selection from recent colors list."""
        try:
            selected_color = color_data.get('selected_color', (255, 0, 0))
            r, g, b = selected_color
            color = QColor(r, g, b)

            # Try to get HSV ranges from data if available
            hsv_ranges = color_data.get('hsv_ranges')
            if hsv_ranges:
                # Recent color has HSV ranges, use them
                self.add_color_row(color, from_hsv_picker=True, hsv_ranges=hsv_ranges)
            else:
                # Fallback: use default ranges
                self.add_color_row(color)
        except Exception:
            # Fallback to basic color selection
            selected_color = color_data.get('selected_color', (255, 0, 0))
            if isinstance(selected_color, (list, tuple)) and len(selected_color) == 3:
                r, g, b = selected_color
                color = QColor(r, g, b)
                self.add_color_row(color)

    def _on_hsv_selected_from_picker(self, hsv_data: dict):
        """Handle HSV color range selected from HSV picker dialog."""
        # Extract the center HSV color from the data
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
        """Add a new color row widget."""
        row = HSVColorRowWizardWidget(self.colorsContainer, color, tolerance_index, from_hsv_picker=from_hsv_picker)
        row.delete_requested.connect(self.remove_color_row)
        row.changed.connect(self._on_color_changed)

        # Set HSV ranges if provided
        if from_hsv_picker and hsv_ranges:
            row.hsv_ranges = hsv_ranges
            row._apply_mode_visibility()

        self.color_rows.append(row)
        self.colorsLayout.addWidget(row, 0, Qt.AlignTop)
        self.addColorButton.clearFocus()
        self._update_empty_state()
        self._update_view_range_button()
        self.validation_changed.emit()

    def remove_color_row(self, row):
        """Remove a color row widget."""
        if row in self.color_rows:
            self.color_rows.remove(row)
            row.setParent(None)
            row.deleteLater()
            self._update_empty_state()
            self._update_view_range_button()
            self.validation_changed.emit()

    def _on_color_changed(self):
        """Handle color row change."""
        self.validation_changed.emit()

    def _update_empty_state(self):
        """Update empty state label visibility."""
        has_colors = len(self.color_rows) > 0
        self.emptyLabel.setVisible(not has_colors)

    def _update_view_range_button(self):
        """Update view range button visibility."""
        has_colors = len(self.color_rows) > 0
        self.viewRangeButton.setVisible(has_colors)

    def view_range_button_clicked(self):
        """Show color range viewer dialog."""
        if not self.color_rows:
            return

        hsv_ranges_list = []
        for row in self.color_rows:
            color = row.get_color()
            if isinstance(color, QColor):
                rgb = (color.red(), color.green(), color.blue())
            else:
                rgb = (255, 0, 0)

            # Get HSV ranges from row - match Image Analysis Wizard behavior
            if hasattr(row, 'has_hsv_ranges') and row.has_hsv_ranges():
                # HSV picker mode: ranges are in fractional format (0-1), convert to OpenCV format
                ranges = row.get_hsv_ranges_fractional()
                hsv_ranges_list.append({
                    'rgb': rgb,
                    'hue_minus': int(ranges.get('h_minus', 0.1) * 179),  # Convert fractional to OpenCV (0-179)
                    'hue_plus': int(ranges.get('h_plus', 0.1) * 179),
                    'sat_minus': int(ranges.get('s_minus', 0.2) * 255),  # Convert fractional to OpenCV (0-255)
                    'sat_plus': int(ranges.get('s_plus', 0.2) * 255),
                    'val_minus': int(ranges.get('v_minus', 0.2) * 255),
                    'val_plus': int(ranges.get('v_plus', 0.2) * 255)
                })
            else:
                # Tolerance mode: get tolerance values (already in OpenCV format)
                h_range, s_range, v_range = row.get_tolerance_values()
                hsv_ranges_list.append({
                    'rgb': rgb,
                    'hue_minus': h_range,  # Already in OpenCV format (0-179)
                    'hue_plus': h_range,
                    'sat_minus': s_range,  # Already in OpenCV format (0-255)
                    'sat_plus': s_range,
                    'val_minus': v_range,
                    'val_plus': v_range
                })

        range_dialog = HSVColorRangeRangeViewer(hsv_ranges_list=hsv_ranges_list)
        if hasattr(range_dialog, 'setWindowTitle'):
            range_dialog.setWindowTitle(
                self.tr("Color Ranges: {count} colors").format(
                    count=len(hsv_ranges_list)
                )
            )
        range_dialog.exec()

    def get_options(self):
        """Get algorithm options."""
        options = {'color_ranges': []}

        if not self.color_rows:
            return options

        for row in self.color_rows:
            color = row.get_color()
            if isinstance(color, QColor):
                rgb = (color.red(), color.green(), color.blue())
            else:
                rgb = (255, 0, 0)

            # Get HSV ranges
            if hasattr(row, 'hsv_ranges') and row.hsv_ranges:
                # HSV ranges from picker are in fractional format (0-1), convert to OpenCV format
                hsv_data = row.hsv_ranges
                # Convert fractional ranges to OpenCV format (h: 0-179, s/v: 0-255)
                h_minus_frac = hsv_data.get('h_minus', 0.1)  # Default 0.1 = ~18 in OpenCV
                h_plus_frac = hsv_data.get('h_plus', 0.1)
                s_minus_frac = hsv_data.get('s_minus', 0.2)  # Default 0.2 = ~51 in OpenCV
                s_plus_frac = hsv_data.get('s_plus', 0.2)
                v_minus_frac = hsv_data.get('v_minus', 0.2)  # Default 0.2 = ~51 in OpenCV
                v_plus_frac = hsv_data.get('v_plus', 0.2)

                color_range = {
                    'name': f"Color_{len(options['color_ranges']) + 1}",
                    'color': color,
                    'rgb': rgb,
                    'hue_minus': int(h_minus_frac * 179),  # Convert fractional to OpenCV (0-179)
                    'hue_plus': int(h_plus_frac * 179),
                    'sat_minus': int(s_minus_frac * 255),  # Convert fractional to OpenCV (0-255)
                    'sat_plus': int(s_plus_frac * 255),
                    'val_minus': int(v_minus_frac * 255),  # Convert fractional to OpenCV (0-255)
                    'val_plus': int(v_plus_frac * 255)
                }
            else:
                # Use tolerance-based ranges
                h_range, s_range, v_range = row.get_tolerance_values()
                color_range = {
                    'name': f"Color_{len(options['color_ranges']) + 1}",
                    'color': color,
                    'rgb': rgb,
                    'hue_minus': h_range,
                    'hue_plus': h_range,
                    'sat_minus': s_range,
                    'sat_plus': s_range,
                    'val_minus': v_range,
                    'val_plus': v_range
                }

            options['color_ranges'].append(color_range)

            # Track this color in recent colors (it's being used for processing)
            try:
                # For HSV colors, track with HSV ranges if available
                if hasattr(row, 'hsv_ranges') and row.hsv_ranges:
                    hsv_config = {
                        'selected_color': rgb,
                        'hsv_ranges': row.hsv_ranges  # Already in fractional format
                    }
                    self.recent_colors_service.add_hsv_color(hsv_config)
                else:
                    # For tolerance-based colors, track as RGB
                    color_config = {
                        'selected_color': rgb,
                        'color_range': None  # No specific range for tolerance-based
                    }
                    self.recent_colors_service.add_rgb_color(color_config)
            except Exception:
                # Silently fail if tracking fails
                pass

        return options

    def validate(self):
        """Validate configuration."""
        if not self.color_rows:
            return self.tr("Please add at least one color to detect.")
        return None

    def load_options(self, options):
        """Load options into UI."""
        if not isinstance(options, dict):
            return

        # Clear existing color rows
        for row in self.color_rows[:]:
            self.remove_color_row(row)

        # Load color ranges
        if 'color_ranges' in options and options['color_ranges']:
            color_ranges = options['color_ranges']
            if isinstance(color_ranges, str):
                color_ranges = literal_eval(color_ranges)

            for color_config in color_ranges:
                if isinstance(color_config, dict):
                    color = color_config.get('color')
                    if isinstance(color, (list, tuple)) and len(color) == 3:
                        color = QColor(color[0], color[1], color[2])
                    elif not isinstance(color, QColor):
                        continue

                    # Create HSV ranges dict if available
                    # Note: Values in color_config are in OpenCV format (h: 0-179, s/v: 0-255)
                    # But hsv_ranges expects fractional format (0-1) for HSV picker mode
                    hsv_ranges = None
                    if 'hue_minus' in color_config:
                        # Convert from OpenCV format to fractional format for hsv_ranges
                        hsv_ranges = {
                            'h_minus': color_config.get('hue_minus', 20) / 179.0,  # Convert to fractional
                            'h_plus': color_config.get('hue_plus', 20) / 179.0,
                            's_minus': color_config.get('sat_minus', 50) / 255.0,  # Convert to fractional
                            's_plus': color_config.get('sat_plus', 50) / 255.0,
                            'v_minus': color_config.get('val_minus', 50) / 255.0,  # Convert to fractional
                            'v_plus': color_config.get('val_plus', 50) / 255.0,
                            # Also include center HSV values
                            'h': color.getHsvF()[0],
                            's': color.getHsvF()[1],
                            'v': color.getHsvF()[2]
                        }

                    self.add_color_row(color, from_hsv_picker=(hsv_ranges is not None), hsv_ranges=hsv_ranges)
