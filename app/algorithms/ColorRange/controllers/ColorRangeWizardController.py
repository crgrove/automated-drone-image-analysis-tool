"""
Wizard controller for Color Range (RGB) algorithm.

Provides a simplified, guided interface for configuring RGB color range detection.
"""

from PySide6.QtWidgets import QWidget, QColorDialog, QLabel, QSizePolicy, QPushButton
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal

from algorithms.AlgorithmController import AlgorithmController
from algorithms.ColorRange.views.ColorRangeWizard_ui import Ui_ColorRangeWizard
from algorithms.ColorRange.views.ColorRowWizardWidget import ColorRowWizardWidget
from algorithms.ColorRange.controllers.ColorRangeRangeViewerController import ColorRangeRangeViewer
from core.services.color.CustomColorsService import get_custom_colors_service
from algorithms.Shared.views import ColorPickerDialog
from algorithms.Shared.views.ColorSelectionMenu import ColorSelectionMenu
from helpers.IconHelper import IconHelper


class ColorRangeWizardController(QWidget, Ui_ColorRangeWizard, AlgorithmController):
    """Wizard controller for Color Range (RGB) algorithm.

    Provides a simplified interface for configuring RGB color range detection.
    Allows users to add multiple color ranges with tolerance presets.

    Attributes:
        validation_changed: Signal emitted when validation state changes
            (e.g., when rows are added/removed).
        theme: Theme name for UI styling.
        color_rows: List of ColorRowWizardWidget instances.
        color_selection_menu: ColorSelectionMenu for quick color selection.
    """

    # Signal emitted when validation state changes (e.g., when rows are added/removed)
    validation_changed = Signal()

    def __init__(self, config, theme):
        """Initialize the wizard controller.

        Args:
            config: Algorithm configuration dictionary.
            theme: Theme name for UI styling.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme

        # List of color row widgets
        self.color_rows = []

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        """Attach custom widgets and set defaults.

        Sets up the empty state label, view range button, and color selection
        menu. Initializes the UI to show the empty state.
        """
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

        # Common color selection menu (RGB mode)
        self.color_selection_menu = ColorSelectionMenu(
            self,
            on_color_selected=self._on_color_selected_from_menu,
            get_default_qcolor=self._get_default_qcolor,
            mode='RGB'
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
        """Return the most recent color or a sensible default.

        Returns:
            QColor instance. Returns the last added color if available,
            otherwise returns red (255, 0, 0).
        """
        if self.color_rows:
            return self.color_rows[-1].get_color()
        return QColor(255, 0, 0)

    def _on_color_selected_from_menu(self, color: QColor):
        """Handle color chosen from the shared color selection menu.

        Args:
            color: Selected QColor from the menu.
        """
        self.add_color_row(color)

    def add_color_row(self, color, tolerance_index=2):
        """Add a new color row widget.

        Args:
            color: QColor or tuple (r, g, b) for the target color.
            tolerance_index: Tolerance preset index (0-4, default 2 = Moderate).
        """
        row = ColorRowWizardWidget(self.colorsContainer, color, tolerance_index)
        row.delete_requested.connect(self.remove_color_row)
        row.changed.connect(self._on_color_changed)

        self.color_rows.append(row)
        self.colorsLayout.addWidget(row, 0, Qt.AlignLeft)

        # Clear focus from Add Color button
        self.addColorButton.clearFocus()

        self._update_empty_state()
        self._update_view_range_button()
        self.validation_changed.emit()

    def remove_color_row(self, row):
        """
        Remove a color row widget.

        Args:
            row: ColorRowWidget instance to remove
        """
        if row in self.color_rows:
            self.color_rows.remove(row)
            self.colorsLayout.removeWidget(row)
            row.deleteLater()

            self._update_empty_state()
            self._update_view_range_button()

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
        currently configured color ranges. For multiple colors, the viewer
        combines them (OR), matching the algorithm's behavior.
        """
        if not self.color_rows:
            return

        # Build color range config list for viewer
        color_ranges = []
        for row in self.color_rows:
            min_rgb, max_rgb = row.get_color_range()
            color_ranges.append({
                'color_range': [min_rgb, max_rgb]
            })

        rangeDialog = ColorRangeRangeViewer(color_ranges)
        rangeDialog.exec()

    def get_options(self):
        """Get algorithm options."""
        options = dict()

        if not self.color_rows:
            # Return empty/None values if no colors configured
            options['color_ranges'] = []
            options['color_range'] = None
            options['selected_color'] = None
            options['range_values'] = None
            return options

        # New format: list of color configurations
        color_ranges = []
        for row in self.color_rows:
            rgb = row.get_rgb()
            tolerance_value = row.get_tolerance_value()
            tolerance_index = row.get_tolerance_index()
            min_rgb, max_rgb = row.get_color_range()
            color_ranges.append({
                'selected_color': rgb,
                'range_values': (tolerance_value, tolerance_value, tolerance_value),  # Uniform tolerance for RGB
                'tolerance_index': tolerance_index,
                'color_range': [min_rgb, max_rgb]
            })
        options['color_ranges'] = color_ranges

        # Legacy format: use first color for backward compatibility
        first_row = self.color_rows[0]
        rgb = first_row.get_rgb()
        tolerance_value = first_row.get_tolerance_value()
        min_rgb, max_rgb = first_row.get_color_range()

        options['color_range'] = [min_rgb, max_rgb]
        options['selected_color'] = rgb
        options['range_values'] = (tolerance_value, tolerance_value, tolerance_value)

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

        from ast import literal_eval

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
