"""
Matched Filter Row Widget

A widget representing a single matched filter color configuration row with:
- Color swatch
- Threshold slider
- Delete button
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QFrame, QLabel, 
                                QSlider, QPushButton, QSizePolicy, QColorDialog)
from core.services.color.CustomColorsService import get_custom_colors_service


class ClickableColorSwatch(QFrame):
    """A clickable color swatch that opens a color picker when clicked."""
    
    colorChanged = Signal(QColor)
    
    def __init__(self, parent=None, color=None):
        super().__init__(parent)
        self._color = color or QColor(255, 0, 0)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(35, 35)
        self.setMaximumSize(35, 35)
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


class MatchedFilterRowWidget(QWidget):
    """Widget representing a single matched filter color configuration."""
    
    # Signal emitted when this row should be deleted
    delete_requested = Signal(QWidget)
    # Signal emitted when color or threshold changes
    changed = Signal()
    
    def __init__(self, parent=None, color=None, threshold=0.5):
        """
        Initialize a matched filter row widget.
        
        Args:
            parent: Parent widget
            color: QColor or tuple (r, g, b) for the target color
            threshold: Threshold value (0.1 to 1.0)
        """
        super().__init__(parent)
        
        # Store color and threshold
        if color is None:
            self.color = QColor(255, 0, 0)  # Default to red
        elif isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color
            
        self.threshold = threshold
        
        self._setup_ui()
        self._update_display()
        
    def _setup_ui(self):
        """Set up the UI layout and widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)
        
        # Make the entire row slightly shorter
        self.setFixedHeight(42)
        
        # Column 1: Color swatch (clickable to change color)
        self.colorSwatch = ClickableColorSwatch(self, self.color)
        self.colorSwatch.colorChanged.connect(self.set_color)
        layout.addWidget(self.colorSwatch)
        
        # Column 2: Threshold Controls
        threshold_layout = QHBoxLayout()
        threshold_layout.setSpacing(6)
        
        threshold_label = QLabel("Threshold:", self)
        threshold_label.setFont(self.font())
        threshold_layout.addWidget(threshold_label)
        
        self.thresholdSlider = QSlider(Qt.Horizontal, self)
        self.thresholdSlider.setFont(self.font())
        self.thresholdSlider.setMinimum(1)
        self.thresholdSlider.setMaximum(10)
        self.thresholdSlider.setPageStep(1)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(1)
        # Set size policy to expand and fill available space
        self.thresholdSlider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Convert threshold (0.1-1.0) to slider value (1-10)
        slider_value = int(self.threshold * 10)
        self.thresholdSlider.setValue(slider_value)
        self.thresholdSlider.valueChanged.connect(self._on_threshold_changed)
        threshold_layout.addWidget(self.thresholdSlider, 1)  # Stretch factor of 1 to expand
        
        self.thresholdValueLabel = QLabel(self)
        self.thresholdValueLabel.setFont(self.font())
        self.thresholdValueLabel.setStyleSheet("font-weight: bold;")
        self._update_threshold_label()
        threshold_layout.addWidget(self.thresholdValueLabel)
        
        # Add threshold_layout with stretch factor so it expands
        layout.addLayout(threshold_layout, 1)  # Stretch factor to expand
        
        # Column 4: Delete button
        self.deleteButton = QPushButton("✕", self)
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setMinimumSize(28, 28)
        self.deleteButton.setMaximumSize(28, 28)
        # Fixed policy ensures space is reserved at end of row
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
        layout.addWidget(self.deleteButton)
        
    def _on_threshold_changed(self):
        """Handle threshold slider value changes."""
        slider_value = self.thresholdSlider.value()
        self.threshold = slider_value / 10.0
        self._update_threshold_label()
        self.changed.emit()
        
    def _update_threshold_label(self):
        """Update the threshold value label."""
        if self.thresholdSlider.value() == 1:
            self.thresholdValueLabel.setText('.1')
        elif self.thresholdSlider.value() == 10:
            self.thresholdValueLabel.setText('1')
        else:
            self.thresholdValueLabel.setText("." + str(self.thresholdSlider.value()))
    
    def _update_display(self):
        """Update the color swatch display."""
        # Update color swatch (block signals to avoid loop)
        if self.colorSwatch.getColor() != self.color:
            self.colorSwatch.blockSignals(True)
            self.colorSwatch.setColor(self.color)
            self.colorSwatch.blockSignals(False)
        
    def set_color(self, color):
        """
        Set the target color.
        
        Args:
            color: QColor or tuple (r, g, b)
        """
        if isinstance(color, tuple):
            self.color = QColor(color[0], color[1], color[2])
        else:
            self.color = color
        self._update_display()
        self.changed.emit()
        
    def get_color(self):
        """Get the target color as QColor."""
        return self.color
        
    def get_rgb(self):
        """Get the target color as RGB tuple."""
        return (self.color.red(), self.color.green(), self.color.blue())
        
    def get_threshold(self):
        """Get the threshold value."""
        return self.threshold

