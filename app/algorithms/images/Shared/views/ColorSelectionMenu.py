from typing import Callable, Optional, Dict, Any

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMenu, QColorDialog, QPushButton, QWidget

from .ColorPickerDialog import ColorPickerDialog
from .ColorListDialog import ColorListDialog


class ColorSelectionMenu:
    """
    Common control to attach a color-selection menu to a button.

    Provides options based on mode:
      - 'RGB': Shows "From Color Picker" (RGB), "From Image", "From List"
      - 'HSV': Shows "From HSV Picker", "From Image", "From List"

    Always available:
      - From Image (Eyedropper) using ColorPickerDialog
      - From List (Predefined colors)

    Mode-specific:
      - From Color Picker (QColorDialog) - RGB mode only
      - From HSV Picker (Custom HSV color range picker) - HSV mode only

    Emits selection by invoking the provided on_color_selected callback with a QColor.
    For HSV picker, uses on_hsv_selected callback with HSV range data dict.
    """

    def __init__(
        self,
        parent: QWidget,
        on_color_selected: Callable[[QColor], None],
        get_default_qcolor: Optional[Callable[[], QColor]] = None,
        on_hsv_selected: Optional[Callable[[Dict[str, Any]], None]] = None,
        get_initial_hsv: Optional[Callable[[], tuple]] = None,
        get_initial_ranges: Optional[Callable[[], Optional[Dict[str, float]]]] = None,
        mode: str = 'RGB',
    ) -> None:
        self.parent = parent
        self.on_color_selected = on_color_selected
        self.on_hsv_selected = on_hsv_selected
        self.get_default_qcolor = get_default_qcolor or (lambda: QColor(255, 0, 0))
        self.get_initial_hsv = get_initial_hsv or (lambda: (0, 1, 1))
        self.get_initial_ranges = get_initial_ranges or (lambda: None)
        self.mode = mode.upper()  # Normalize to uppercase
        self._menu = QMenu(parent)

        # Build actions based on mode
        if self.mode == 'HSV' and self.on_hsv_selected is not None:
            # HSV mode: show HSV picker at the top
            self._menu.addAction("From HSV Color Picker", self._select_from_hsv_picker)
        elif self.mode == 'RGB':
            # RGB mode: show RGB color picker at the top
            self._menu.addAction("From Color Picker", self._select_from_qt_color_dialog)

        # Always show these options (after the mode-specific picker)
        self._menu.addAction("From Image", self._select_from_image_dialog)
        self._menu.addAction("From List", self._select_from_list_dialog)

    def menu(self) -> QMenu:
        return self._menu

    def attach_to(self, button: QPushButton) -> None:
        """
        Attach this menu to the provided button.
        """
        button.setMenu(self._menu)

    # ----- Handlers ----- #
    def _select_from_qt_color_dialog(self) -> None:
        default_color = self.get_default_qcolor()
        color = QColorDialog.getColor(default_color, self.parent)
        if color.isValid():
            self.on_color_selected(color)

    def _select_from_image_dialog(self) -> None:
        dialog = ColorPickerDialog(self.parent)
        if dialog.exec():
            color_rgb = dialog.get_selected_color()
            if color_rgb:
                r, g, b = color_rgb
                color = QColor(r, g, b)
                self.on_color_selected(color)

    def _select_from_list_dialog(self) -> None:
        dialog = ColorListDialog(self.parent, mode=self.mode)
        if dialog.exec():
            qc = dialog.selected_qcolor()
            if qc is not None:
                self.on_color_selected(qc)

    def _select_from_hsv_picker(self) -> None:
        """Open the HSV color range picker dialog."""
        if self.on_hsv_selected is None:
            return

        # Import here to avoid circular dependencies
        from algorithms.Shared.views.ColorRangeDialog import ColorRangeDialog

        initial_hsv = self.get_initial_hsv()
        initial_ranges = self.get_initial_ranges()

        dialog = ColorRangeDialog(None, initial_hsv, initial_ranges, self.parent)

        if dialog.exec() == ColorRangeDialog.Accepted:
            hsv_data = dialog.get_hsv_ranges()
            self.on_hsv_selected(hsv_data)
