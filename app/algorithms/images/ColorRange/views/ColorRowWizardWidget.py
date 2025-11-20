"""
Color Row Widget for Wizard

A simplified widget for color range configuration in the wizard with:
- Color swatch
- Tolerance dropdown (instead of numeric inputs)
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QLabel, QComboBox,
                               QPushButton, QSizePolicy, QColorDialog)
from core.services.color.CustomColorsService import get_custom_colors_service


class ClickableColorSwatch(QFrame):
    """A clickable color swatch that opens a color picker when clicked and displays RGB values."""

    colorChanged = Signal(QColor)

    def __init__(self, parent=None, color=None):
        super().__init__(parent)
        self._color = color or QColor(255, 0, 0)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(80, 35)
        self.setMaximumSize(80, 35)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def setColor(self, color):
        """Set the color and update display.

        Args:
            color: QColor to set.
        """
        self._color = color
        self._update_style()
        self.colorChanged.emit(color)

    def getColor(self):
        """Get the current color.

        Returns:
            Current QColor.
        """
        return self._color

    def _update_style(self):
        """Update the stylesheet with current color.

        Updates the widget's background color and tooltip based on
        the current color value.
        """
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); "
            f"border: 1px solid #888;"
        )
        self.setToolTip(f"RGB: ({r}, {g}, {b})\nClick to change color")
        self.update()

    def paintEvent(self, event):
        """Override paint event to draw RGB text on the swatch.

        Args:
            event: Paint event.
        """
        super().paintEvent(event)
        if self._color:
            r, g, b = self._color.red(), self._color.green(), self._color.blue()
            text_color = Qt.white if (r + g + b) < 384 else Qt.black

            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(text_color)

            font = QFont(self.font())
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)

            text = f"({r},{g},{b})"
            painter.drawText(self.rect(), Qt.AlignCenter, text)
            painter.end()

    def mousePressEvent(self, event):
        """Handle mouse click to open color picker.

        Opens QColorDialog on left click and updates color if valid.

        Args:
            event: Mouse press event.
        """
        if event.button() == Qt.LeftButton:
            try:
                custom_colors_service = get_custom_colors_service()
                color = QColorDialog.getColor(self._color)
                custom_colors_service.sync_with_dialog()
                if color.isValid():
                    self.setColor(color)
            except Exception:
                pass
        super().mousePressEvent(event)


class ColorRowWizardWidget(QWidget):
    """Simplified widget representing a color range configuration for wizard.

    Provides a compact UI for selecting a color and tolerance preset.
    Used in the wizard interface for color range algorithm configuration.

    Attributes:
        delete_requested: Signal emitted when delete button is clicked.
            Emits the widget instance.
        changed: Signal emitted when color or tolerance changes.
        TOLERANCE_PRESETS: List of (label, rgb_range_value) tuples for
            tolerance presets.
    """

    delete_requested = Signal(QWidget)
    changed = Signal()

    # Tolerance presets: (label, rgb_range_value)
    TOLERANCE_PRESETS = [
        ("Very Narrow", 10),
        ("Narrow", 25),
        ("Moderate", 50),
        ("Wide", 75),
        ("Very Wide", 100)
    ]

    def __init__(self, parent=None, color=None, tolerance_index=2):
        """Initialize a color row wizard widget.

        Args:
            parent: Parent widget. Defaults to None.
            color: QColor or tuple (r, g, b) for the target color.
                Defaults to red (255, 0, 0).
            tolerance_index: Index into TOLERANCE_PRESETS (0-4).
                Defaults to 2 (Moderate).
        """
        super().__init__(parent)

        # Store color
        if color is None:
            self.color = QColor(255, 0, 0)
        elif isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color

        self.tolerance_index = max(0, min(tolerance_index, len(self.TOLERANCE_PRESETS) - 1))

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI layout and widgets.

        Creates horizontal layout with color swatch, tolerance dropdown,
        and delete button.
        """
        # Remove all margins from the widget itself
        self.setContentsMargins(0, 0, 0, 0)

        # Outer layout for the row widget
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Frame to visually emulate a table row (bordered container)
        self.rowFrame = QFrame(self)
        self.rowFrame.setObjectName("rowFrame")
        rowLayout = QHBoxLayout(self.rowFrame)
        # Symmetric top/bottom margins so content isn't flush against borders
        rowLayout.setContentsMargins(8, 6, 8, 6)
        rowLayout.setSpacing(12)
        rowLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(self.rowFrame)

        # Keep rows compact horizontally (not full width)
        # Height must accommodate: 6px top margin + 35px swatch + 6px bottom margin = 47px minimum
        # Use 54px to provide visible spacing above and below the swatch
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(54)

        # Make rowFrame expand to fill the row
        self.rowFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Default fixed width for consistency
        DEFAULT_ROW_WIDTH = 520
        try:
            self.rowFrame.setFixedWidth(DEFAULT_ROW_WIDTH)
        except Exception:
            self.rowFrame.setFixedWidth(DEFAULT_ROW_WIDTH)

        # Set border style - will be updated when row is added to container
        self._update_border_style()

        # Color swatch
        self.colorSwatch = ClickableColorSwatch(self.rowFrame, self.color)
        self.colorSwatch.colorChanged.connect(self._on_color_changed)
        rowLayout.addWidget(self.colorSwatch)

        # Tolerance label
        tolerance_label = QLabel("Match\nTolerance:", self.rowFrame)
        # Force 11pt font
        _lbl_font = QFont(self.font())
        _lbl_font.setPointSize(11)
        tolerance_label.setFont(_lbl_font)
        tolerance_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        rowLayout.addWidget(tolerance_label)

        # Tolerance dropdown
        self.toleranceCombo = QComboBox(self.rowFrame)
        # Inputs should be 11pt
        combo_font = QFont(self.font())
        combo_font.setPointSize(11)
        self.toleranceCombo.setFont(combo_font)
        for label, _ in self.TOLERANCE_PRESETS:
            self.toleranceCombo.addItem(label)
        self.toleranceCombo.setCurrentIndex(self.tolerance_index)
        self.toleranceCombo.currentIndexChanged.connect(self._on_tolerance_changed)
        self.toleranceCombo.setMinimumWidth(150)
        self.toleranceCombo.setMaximumWidth(200)
        self.toleranceCombo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        rowLayout.addWidget(self.toleranceCombo)

        # Add spacer to push delete button to the right
        rowLayout.addStretch()

        # Delete button
        self.deleteButton = QPushButton("✕", self.rowFrame)
        btn_font = QFont(self.font())
        btn_font.setPointSize(11)
        self.deleteButton.setFont(btn_font)
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setMinimumSize(28, 28)
        self.deleteButton.setMaximumSize(28, 28)
        self.deleteButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.deleteButton.setStyleSheet("""
            QPushButton#deleteButton {
                background-color: #d32f2f;
                color: white;
                border: 1px solid #b71c1c;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton#deleteButton:hover {
                background-color: #f44336;
            }
            QPushButton#deleteButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.deleteButton.clicked.connect(lambda: self.delete_requested.emit(self))
        self.deleteButton.setFocusPolicy(Qt.NoFocus)  # Prevent delete button from getting focus
        rowLayout.addWidget(self.deleteButton)

    def _update_border_style(self):
        """Update border style based on row position to create table appearance."""
        if not self.parent():
            # Default: show all borders if parent not ready
            self.rowFrame.setStyleSheet("""
                QFrame#rowFrame {
                    border: 1px solid #666;
                    background-color: transparent;
                }
            """)
            return

        parent_layout = self.parent().layout()
        if not parent_layout:
            self.rowFrame.setStyleSheet("""
                QFrame#rowFrame {
                    border: 1px solid #666;
                    background-color: transparent;
                }
            """)
            return

        # Find index of this widget among other row widgets (filter out non-row widgets)
        # Check for row widgets by looking for the _update_border_style method
        row_widgets = []
        for i in range(parent_layout.count()):
            item = parent_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget and hasattr(widget, '_update_border_style'):
                row_widgets.append(widget)

        # Find our index in the list of row widgets
        try:
            row_index = row_widgets.index(self)
        except ValueError:
            # Not found, default to showing all borders
            self.rowFrame.setStyleSheet("""
                QFrame#rowFrame {
                    border: 1px solid #666;
                    background-color: transparent;
                }
            """)
            return

        is_first = (row_index == 0)

        # Style borders to connect and form a table
        # First row: all borders (including top)
        # Other rows: left, right, bottom (no top border to connect)
        if is_first:
            border_style = "border: 1px solid #666;"
        else:
            border_style = "border-left: 1px solid #666; border-right: 1px solid #666; border-bottom: 1px solid #666; border-top: none;"

        self.rowFrame.setStyleSheet(f"""
            QFrame#rowFrame {{
                {border_style}
                background-color: transparent;
            }}
        """)

    def showEvent(self, event):
        """Update border style when widget is shown."""
        super().showEvent(event)
        # Update border style - method handles parent not ready gracefully
        self._update_border_style()

    def _on_color_changed(self, color):
        """Handle color swatch change.

        Args:
            color: New QColor from swatch.
        """
        self.color = color
        self.changed.emit()

    def _on_tolerance_changed(self, index):
        """Handle tolerance dropdown change.

        Args:
            index: New tolerance preset index.
        """
        self.tolerance_index = index
        self.changed.emit()

    def set_color(self, color):
        """Set the target color.

        Args:
            color: QColor or tuple (r, g, b) to set.
        """
        if isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color
        self.colorSwatch.blockSignals(True)
        self.colorSwatch.setColor(self.color)
        self.colorSwatch.blockSignals(False)
        self.changed.emit()

    def get_color(self):
        """Get the target color as QColor.

        Returns:
            Current color as QColor.
        """
        return self.color

    def get_rgb(self):
        """Get the target color as RGB tuple.

        Returns:
            Current color as (r, g, b) tuple.
        """
        return (self.color.red(), self.color.green(), self.color.blue())

    def get_tolerance_index(self):
        """Get the selected tolerance index.

        Returns:
            Current tolerance preset index (0-4).
        """
        return self.tolerance_index

    def get_tolerance_value(self):
        """Get the numeric tolerance value.

        Returns:
            RGB range value for the selected tolerance preset.
        """
        return self.TOLERANCE_PRESETS[self.tolerance_index][1]

    def get_color_range(self):
        """Get the min and max color range as tuples based on tolerance.

        Calculates RGB color range by applying tolerance to the target color.

        Returns:
            Tuple of (min_rgb, max_rgb) where each is (r, g, b) tuple
            with values clamped to [0, 255].
        """
        r, g, b = self.color.red(), self.color.green(), self.color.blue()
        tolerance = self.get_tolerance_value()

        min_rgb = (max(0, r - tolerance), max(0, g - tolerance), max(0, b - tolerance))
        max_rgb = (min(255, r + tolerance), min(255, g + tolerance), min(255, b + tolerance))
        return min_rgb, max_rgb
