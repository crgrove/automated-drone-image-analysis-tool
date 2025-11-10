"""
Color Row Widget for Wizard

A simplified widget for color range configuration in the wizard with:
- Color swatch
- Tolerance dropdown (instead of numeric inputs)
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
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
        """Set the color and update display."""
        self._color = color
        self._update_style()
        self.colorChanged.emit(color)
    
    def getColor(self):
        """Get the current color."""
        return self._color
    
    def _update_style(self):
        """Update the stylesheet with current color."""
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        self.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); "
            f"border: 1px solid #888;"
        )
        self.setToolTip(f"RGB: ({r}, {g}, {b})\nClick to change color")
        self.update()
    
    def paintEvent(self, event):
        """Override paint event to draw RGB text on the swatch."""
        super().paintEvent(event)
        if self._color:
            from PySide6.QtGui import QPainter, QFont
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


class ColorRowWizardWidget(QWidget):
    """Simplified widget representing a color range configuration for wizard."""
    
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
        """
        Initialize a color row wizard widget.
        
        Args:
            parent: Parent widget
            color: QColor or tuple (r, g, b) for the target color
            tolerance_index: Index into TOLERANCE_PRESETS (0-4, default 2 = Moderate)
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
        """Set up the UI layout and widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignLeft)
        # Keep row compact: don't expand to full dialog width
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(42)
        
        # Color swatch
        self.colorSwatch = ClickableColorSwatch(self, self.color)
        self.colorSwatch.colorChanged.connect(self._on_color_changed)
        layout.addWidget(self.colorSwatch)
        
        # Tolerance label
        tolerance_label = QLabel("Match\nTolerance:", self)
        tolerance_label.setFont(self.font())
        tolerance_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(tolerance_label)
        
        # Tolerance dropdown
        self.toleranceCombo = QComboBox(self)
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
        layout.addWidget(self.toleranceCombo)
        
        # Delete button
        self.deleteButton = QPushButton("✕", self)
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
        layout.addWidget(self.deleteButton)
    
    def _on_color_changed(self, color):
        """Handle color swatch change."""
        self.color = color
        self.changed.emit()
    
    def _on_tolerance_changed(self, index):
        """Handle tolerance dropdown change."""
        self.tolerance_index = index
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
    
    def get_tolerance_index(self):
        """Get the selected tolerance index."""
        return self.tolerance_index
    
    def get_tolerance_value(self):
        """Get the numeric tolerance value."""
        return self.TOLERANCE_PRESETS[self.tolerance_index][1]
    
    def get_color_range(self):
        """Get the min and max color range as tuples based on tolerance."""
        r, g, b = self.color.red(), self.color.green(), self.color.blue()
        tolerance = self.get_tolerance_value()
        
        min_rgb = (max(0, r - tolerance), max(0, g - tolerance), max(0, b - tolerance))
        max_rgb = (min(255, r + tolerance), min(255, g + tolerance), min(255, b + tolerance))
        return min_rgb, max_rgb

