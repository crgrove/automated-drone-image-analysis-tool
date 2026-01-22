from typing import Optional, List, Dict, Any, Tuple
import colorsys

from PySide6.QtCore import Qt
from helpers.TranslationMixin import TranslationMixin
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QLabel,
    QPushButton,
    QDialogButtonBox,
)

from core.services.color.ColorListService import get_predefined_colors


class ColorListDialog(TranslationMixin, QDialog):
    """
    Dialog to pick a color from a predefined list.
    """

    def __init__(self, parent=None, mode: str = 'RGB'):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Select Color from List"))
        self.setMinimumSize(600, 420)
        self._selected_rgb: Optional[Tuple[int, int, int]] = None
        self.mode = mode.upper()  # Normalize to uppercase

        self._colors: List[Dict[str, Any]] = get_predefined_colors()
        self._filtered: List[Dict[str, Any]] = list(self._colors)

        layout = QVBoxLayout(self)

        # Search bar
        search_row = QHBoxLayout()
        search_label = QLabel(self.tr("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.tr("Filter by name or uses…"))
        self.search_input.textChanged.connect(self._apply_filter)
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)
        self._apply_translations()

        # Table - adjust columns based on mode
        self.table = QTableWidget()
        if self.mode == 'HSV':
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                "", self.tr("Name"), self.tr("RGB"), self.tr("HSV"), self.tr("Uses")
            ])
        else:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels([
                "", self.tr("Name"), self.tr("RGB"), self.tr("Uses")
            ])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self._ok_button = buttons.button(QDialogButtonBox.Ok)
        self._ok_button.setText(self.tr("Use Color"))
        self._ok_button.setEnabled(False)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self._populate_table()

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, modal dialogs sometimes need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the search input so users can type immediately
        if hasattr(self, 'search_input'):
            self.search_input.setFocus()

    def _apply_filter(self, text: str) -> None:
        query = (text or "").strip().lower()
        if not query:
            self._filtered = list(self._colors)
        else:
            self._filtered = []
            for c in self._colors:
                if query in c.get("name", "").lower() or query in c.get("uses", "").lower():
                    self._filtered.append(c)
        self._populate_table()

    def _rgb_to_hsv(self, r: int, g: int, b: int) -> Tuple[int, int, int]:
        """Convert RGB (0-255) to HSV (H: 0-359°, S: 0-100%, V: 0-100%)."""
        # Normalize to 0-1 range
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        # Convert using colorsys (returns H: 0-1, S: 0-1, V: 0-1)
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        # Convert to display format: H: 0-359°, S: 0-100%, V: 0-100%
        h_deg = int(round(h * 360)) % 360
        s_pct = int(round(s * 100))
        v_pct = int(round(v * 100))
        return (h_deg, s_pct, v_pct)

    def _populate_table(self) -> None:
        self.table.setRowCount(len(self._filtered))
        for row, c in enumerate(self._filtered):
            rgb = tuple(c.get("rgb", (0, 0, 0)))
            name = c.get("name", "")
            uses = c.get("uses", "")

            # Swatch
            swatch = QWidget()
            swatch.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border: 1px solid #666;")
            self.table.setCellWidget(row, 0, swatch)
            self.table.setRowHeight(row, 22)

            # Name
            self.table.setItem(row, 1, QTableWidgetItem(name))
            # RGB
            self.table.setItem(row, 2, QTableWidgetItem(f"({rgb[0]}, {rgb[1]}, {rgb[2]})"))

            # HSV column (only for HSV mode)
            if self.mode == 'HSV':
                # Check if HSV is already in the data, otherwise convert from RGB
                if 'hsv' in c and isinstance(c['hsv'], (list, tuple)) and len(c['hsv']) == 3:
                    h, s, v = c['hsv']
                else:
                    h, s, v = self._rgb_to_hsv(rgb[0], rgb[1], rgb[2])
                self.table.setItem(row, 3, QTableWidgetItem(f"({h}°, {s}%, {v}%)"))
                # Uses column is now at index 4
                uses_col = 4
            else:
                # Uses column is at index 3 for RGB mode
                uses_col = 3

            # Uses
            self.table.setItem(row, uses_col, QTableWidgetItem(uses))

        self.table.resizeColumnToContents(0)
        self.table.setColumnWidth(0, 26)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        if self.mode == 'HSV':
            self.table.resizeColumnToContents(3)
        self.table.horizontalHeader().setStretchLastSection(True)
        self._ok_button.setEnabled(False)
        self._selected_rgb = None

    def _on_selection_changed(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._filtered):
            self._ok_button.setEnabled(False)
            self._selected_rgb = None
            return
        rgb = tuple(self._filtered[row].get("rgb", (0, 0, 0)))
        self._selected_rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
        self._ok_button.setEnabled(True)

    def _on_double_click(self, row: int, _column: int) -> None:
        if 0 <= row < len(self._filtered):
            rgb = tuple(self._filtered[row].get("rgb", (0, 0, 0)))
            self._selected_rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
            self.accept()

    def _on_accept(self) -> None:
        if self._selected_rgb is not None:
            self.accept()

    def selected_qcolor(self) -> Optional[QColor]:
        if self._selected_rgb is None:
            return None
        r, g, b = self._selected_rgb
        return QColor(r, g, b)
