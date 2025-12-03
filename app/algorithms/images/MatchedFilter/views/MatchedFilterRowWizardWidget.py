"""
Matched Filter Row Widget for Wizard

A simplified widget for matched filter configuration in the wizard with:
- Color swatch
- Aggressiveness dropdown (instead of threshold slider)
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QLabel, QComboBox,
                               QPushButton, QSizePolicy, QColorDialog)
import qtawesome as qta
from core.services.color.CustomColorsService import get_custom_colors_service


class ClickableColorSwatch(QFrame):
    """A clickable color swatch that opens a color picker when clicked."""

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
        """Set the color and update display."""
        self._color = color
        self._update_style()
        self.colorChanged.emit(color)

    def getColor(self):
        """Get the current color."""
        return self._color

    def _update_style(self):
        """Update the stylesheet with current color."""
        self.setStyleSheet(f"background-color: {self._color.name()}; border: 1px solid #888;")

    def mousePressEvent(self, event):
        """Handle mouse click to open color picker."""
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


class MatchedFilterRowWizardWidget(QWidget):
    """Simplified widget representing a matched filter configuration for wizard."""

    delete_requested = Signal(QWidget)
    changed = Signal()

    # Aggressiveness presets: (label, threshold_value)
    AGGRESSIVENESS_PRESETS = [
        ("Very Strict", 0.9),
        ("Strict", 0.7),
        ("Moderate", 0.5),
        ("Broad", 0.3),
        ("Very Broad", 0.1)
    ]

    def __init__(self, parent=None, color=None, aggressiveness_index=2):
        """
        Initialize a matched filter row wizard widget.

        Args:
            parent: Parent widget
            color: QColor or tuple (r, g, b) for the target color
            aggressiveness_index: Index into AGGRESSIVENESS_PRESETS (0-4, default 2 = Moderate)
        """
        super().__init__(parent)

        # Store color
        if color is None:
            self.color = QColor(255, 0, 0)
        elif isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color

        self.aggressiveness_index = max(0, min(aggressiveness_index, len(self.AGGRESSIVENESS_PRESETS) - 1))

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI layout and widgets."""
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

        # Aggressiveness label (multi-line, vertically centered)
        aggr_label = QLabel("Match\nAggressiveness:", self.rowFrame)
        # Force 11pt font
        _lbl_font = QFont(self.font())
        _lbl_font.setPointSize(11)
        aggr_label.setFont(_lbl_font)
        aggr_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        rowLayout.addWidget(aggr_label)

        # Aggressiveness dropdown
        self.aggressivenessCombo = QComboBox(self.rowFrame)
        # Inputs should be 11pt
        combo_font = QFont(self.font())
        combo_font.setPointSize(11)
        self.aggressivenessCombo.setFont(combo_font)
        for label, _ in self.AGGRESSIVENESS_PRESETS:
            self.aggressivenessCombo.addItem(label)
        self.aggressivenessCombo.setCurrentIndex(self.aggressiveness_index)
        self.aggressivenessCombo.currentIndexChanged.connect(self._on_aggressiveness_changed)
        self.aggressivenessCombo.setMinimumWidth(180)
        self.aggressivenessCombo.setMaximumWidth(220)
        self.aggressivenessCombo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        rowLayout.addWidget(self.aggressivenessCombo)

        # Add spacer to push delete button to the right
        rowLayout.addStretch()

        # Delete button
        self.deleteButton = QPushButton(self.rowFrame)
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setMinimumSize(28, 28)
        self.deleteButton.setMaximumSize(28, 28)
        self.deleteButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.deleteButton.setIcon(qta.icon('fa6s.xmark', color='white'))
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
        """Handle color swatch change."""
        self.color = color
        self.changed.emit()

    def _on_aggressiveness_changed(self, index):
        """Handle aggressiveness dropdown change."""
        self.aggressiveness_index = index
        self.changed.emit()

    def set_color(self, color):
        """Set the target color."""
        if isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color
        self.colorSwatch.blockSignals(True)
        self.colorSwatch.setColor(self.color)
        self.colorSwatch.blockSignals(False)
        self.changed.emit()

    def get_color(self):
        """Get the target color as QColor."""
        return self.color

    def get_rgb(self):
        """Get the target color as RGB tuple."""
        return (self.color.red(), self.color.green(), self.color.blue())

    def get_aggressiveness_index(self):
        """Get the selected aggressiveness index."""
        return self.aggressiveness_index

    def get_threshold(self):
        """Get the numeric threshold value (0.1-1.0)."""
        return self.AGGRESSIVENESS_PRESETS[self.aggressiveness_index][1]
