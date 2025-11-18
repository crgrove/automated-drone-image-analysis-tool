from ast import literal_eval

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.MatchedFilter.views.MatchedFilter_ui import Ui_MatchedFilter
from algorithms.images.MatchedFilter.views.MatchedFilterRowWidget import MatchedFilterRowWidget
from algorithms.images.MatchedFilter.controllers.MatchedFilterRangeViewerController import MatchedFilterRangeViewer

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QColorDialog, QLabel, QSizePolicy, QMenu, QPushButton
from PySide6.QtCore import Qt

from core.services.LoggerService import LoggerService
from core.services.color.CustomColorsService import get_custom_colors_service
from algorithms.Shared.views import ColorPickerDialog
from algorithms.images.Shared.views.ColorSelectionMenu import ColorSelectionMenu


class MatchedFilterController(QWidget, Ui_MatchedFilter, AlgorithmController):
    """Controller for the Matched Filter algorithm widget supporting multiple colors."""

    def __init__(self, config, theme):
        """
        Initializes the MatchedFilterController widget and sets up the UI.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)

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

        # Common color selection menu (RGB mode)
        self.color_selection_menu = ColorSelectionMenu(
            self,
            on_color_selected=self._on_color_selected_from_menu,
            get_default_qcolor=self._get_default_qcolor,
            mode='RGB'
        )
        self.color_selection_menu.attach_to(self.addColorButton)

        self._apply_icons(theme)

        # Enable scrolling when more than 3 colors
        self._update_scroll_area()
        # Update empty state visibility
        self._update_empty_state()

    def add_color_button_clicked(self):
        """
        Handles the add color button click.

        This method is kept for backward compatibility but is now handled by menu actions.
        """
        self.add_color_from_dialog()

    def add_color_from_dialog(self):
        """
        Opens a color picker dialog to allow the user to select a color.
        """
        try:
            # Ensure custom colors are loaded
            custom_colors_service = get_custom_colors_service()

            # Use the last selected color as default, or default to red
            default_color = QColor(255, 0, 0)
            if self.color_rows:
                default_color = self.color_rows[-1].get_color()

            color = QColorDialog.getColor(default_color)

            # Sync custom colors after dialog closes
            custom_colors_service.sync_with_dialog()

            if color.isValid():
                self.add_color_row(color)
        except Exception as e:
            self.logger.error(e)

    def _get_default_qcolor(self):
        """Return the most recent color or a sensible default."""
        if self.color_rows:
            return self.color_rows[-1].get_color()
        return QColor(255, 0, 0)

    def _on_color_selected_from_menu(self, color: QColor):
        """Handle color chosen from the shared color selection menu."""
        self.add_color_row(color)

    def add_color_from_image(self):
        """
        Opens an image viewer dialog with eyedropper tool to select a color from an image.
        """
        try:
            dialog = ColorPickerDialog(self)
            if dialog.exec():
                color_rgb = dialog.get_selected_color()
                if color_rgb:
                    r, g, b = color_rgb
                    color = QColor(r, g, b)
                    self.add_color_row(color)
        except Exception as e:
            self.logger.error(e)

    def add_color_row(self, color, threshold=0.3):
        """
        Add a new color row widget.

        Args:
            color: QColor or tuple (r, g, b) for the target color
            threshold: Threshold value (default 0.3)
        """
        row = MatchedFilterRowWidget(self.scrollAreaWidgetContents, color, threshold)
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
            row: MatchedFilterRowWidget instance to remove
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

    def _update_scroll_area(self):
        """Enable scrolling when more than 3 colors are present."""
        # Calculate approximate height per row (swatch 35px + margins/spacing ~45px total)
        row_height = 45
        spacing = 6

        if len(self.color_rows) > 3:
            # Fixed height to show exactly 3 rows, enable scrolling for more
            # 3 rows + spacing between them + margins
            fixed_height = 3 * row_height + 2 * spacing + 10  # 3 rows, 2 gaps, margins
            self.scrollArea.setMinimumHeight(fixed_height)
            self.scrollArea.setMaximumHeight(fixed_height)
            # Force fixed vertical policy so parent allows this size
            self.scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            # Expand to fit all rows (up to 3), no scrolling needed
            if self.color_rows:
                # Calculate height needed for all rows
                total_height = len(self.color_rows) * row_height + (len(self.color_rows) - 1) * spacing + 10
                self.scrollArea.setMinimumHeight(total_height)
                self.scrollArea.setMaximumHeight(total_height)
                self.scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            else:
                # No rows, minimal height
                self.scrollArea.setMinimumHeight(0)
                self.scrollArea.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

    def _update_empty_state(self):
        """Show a centered message when no colors are configured."""
        if self.color_rows:
            self.emptyLabel.hide()
        else:
            self.emptyLabel.show()

    def view_range_button_clicked(self):
        """
        Handles the view range button click.

        Opens the View Range dialog, displaying detection regions for the
        currently configured matched-filter colors. For multiple colors,
        the viewer combines them (OR), matching the algorithm's behavior.
        """
        if not self.color_rows:
            return

        # Build color config list for viewer
        color_configs = []
        for row in self.color_rows:
            color_configs.append({
                'selected_color': row.get_rgb(),
                'match_filter_threshold': row.get_threshold()
            })

        rangeDialog = MatchedFilterRangeViewer(color_configs)
        rangeDialog.exec()

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing selected options. Supports both:
                - New format: 'color_configs' (list of color configs)
                - Legacy format: 'selected_color', 'match_filter_threshold' (for backward compatibility)
        """
        options = dict()

        if not self.color_rows:
            # Return empty/None values if no colors configured
            options['color_configs'] = []
            options['selected_color'] = None
            options['match_filter_threshold'] = None
            return options

        # New format: list of color configurations
        color_configs = []
        for row in self.color_rows:
            rgb = row.get_rgb()
            threshold = row.get_threshold()
            color_configs.append({
                'selected_color': rgb,
                'match_filter_threshold': threshold
            })
        options['color_configs'] = color_configs

        # Legacy format: use first color for backward compatibility
        first_row = self.color_rows[0]
        options['selected_color'] = first_row.get_rgb()
        options['match_filter_threshold'] = first_row.get_threshold()

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

        Supports both new format (color_configs list) and legacy format
        (single selected_color + match_filter_threshold).

        Args:
            options (dict): The options to use to set UI attributes.
        """
        # Clear existing color rows
        for row in self.color_rows[:]:
            self.remove_color_row(row)

        # Try new format first
        if 'color_configs' in options and options['color_configs']:
            color_configs = options['color_configs']
            # Handle string format (from literal_eval in some cases)
            if isinstance(color_configs, str):
                color_configs = literal_eval(color_configs)

            for color_config in color_configs:
                if isinstance(color_config, dict):
                    selected_color = color_config.get('selected_color')
                    threshold = color_config.get('match_filter_threshold', 0.3)

                    if isinstance(selected_color, str):
                        selected_color = literal_eval(selected_color)
                    if isinstance(threshold, str):
                        threshold = float(threshold)

                    if selected_color:
                        color = QColor(selected_color[0], selected_color[1], selected_color[2])
                        self.add_color_row(color, threshold)

        # Fall back to legacy format
        elif 'selected_color' in options and 'match_filter_threshold' in options:
            selected_color = options['selected_color']
            threshold = options['match_filter_threshold']

            if isinstance(selected_color, str):
                selected_color = literal_eval(selected_color)
            if isinstance(threshold, str):
                threshold = float(threshold)

            if selected_color:
                color = QColor(selected_color[0], selected_color[1], selected_color[2])
                self.add_color_row(color, threshold)

        self._update_view_range_button()
        self._update_scroll_area()
        self._update_empty_state()

    def _apply_icons(self, theme):
        """
        Loads icon assets based on the currently selected theme.

        Args:
            theme (str): Name of the active theme used to resolve icon paths.
        """
        from helpers.IconHelper import IconHelper

        self.addColorButton.setIcon(IconHelper.create_icon('fa6s.palette', theme))
        self.viewRangeButton.setIcon(IconHelper.create_icon('fa6s.eye', theme))
