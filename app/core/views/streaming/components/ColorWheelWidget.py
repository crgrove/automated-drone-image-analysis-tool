"""
ColorWheelWidget.py - Interactive color wheel for hue selection.

A circular color wheel widget that allows users to click on color segments
to select/deselect hue ranges. Designed for color exclusion in detection algorithms.
"""

from typing import List, Optional
from PySide6.QtCore import Qt, QPoint, QRect, Signal
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
import math


class ColorWheelWidget(QWidget):
    """
    Interactive color wheel widget for selecting hue ranges.
    
    Displays a circular color wheel divided into segments. Users can click
    on segments to toggle their selection state. Selected segments are
    highlighted with a border.
    
    Signals:
        selectionChanged: Emitted when selection changes (list of selected hue values in 360° scale)
    """
    
    selectionChanged = Signal(list)  # List of selected hue values (0-360)
    
    def __init__(self, parent=None, size: int = 300):
        """
        Initialize color wheel widget.
        
        Args:
            parent: Parent widget
            size: Size of the color wheel in pixels (default: 300)
        """
        super().__init__(parent)
        self.setMinimumSize(size, size)
        self.setMaximumSize(size, size)
        
        # Color definitions: (name, hue_degrees_360, hex_color)
        self.hue_colors = [
            ("Red", 0, "#FF0000"),
            ("Red-Orange", 20, "#FF3300"),
            ("Orange", 40, "#FF6600"),
            ("Yellow-Orange", 60, "#FF9900"),
            ("Yellow", 80, "#FFCC00"),
            ("Yellow-Green", 100, "#CCFF00"),
            ("Green", 120, "#00FF00"),
            ("Green-Cyan", 140, "#00FF66"),
            ("Cyan", 160, "#00FFCC"),
            ("Cyan-Blue", 180, "#00CCFF"),
            ("Blue", 200, "#0099FF"),
            ("Blue-Violet", 220, "#0066FF"),
            ("Violet", 240, "#0033FF"),
            ("Purple", 260, "#6600FF"),
            ("Magenta", 280, "#9900FF"),
            ("Pink-Magenta", 300, "#CC00FF"),
            ("Pink", 320, "#FF00CC"),
            ("Hot Pink", 340, "#FF0066"),
        ]
        
        # Track selected hues (stored as hue values in 360° scale)
        self.selected_hues: set = set()
        
        # Wheel geometry
        self.center_x = size // 2
        self.center_y = size // 2
        self.inner_radius = size * 0.15  # Inner circle (gray center)
        self.outer_radius = size * 0.45  # Outer edge of color wheel
        
    def set_selected_hues(self, hue_values: List[int]):
        """
        Set which hues are selected.
        
        Args:
            hue_values: List of hue values in 360° scale to mark as selected
        """
        self.selected_hues = set(hue_values)
        self.update()  # Trigger repaint
        self.selectionChanged.emit(sorted(self.selected_hues))
    
    def get_selected_hues(self) -> List[int]:
        """Get list of currently selected hue values (360° scale)."""
        return sorted(self.selected_hues)
    
    def _hue_to_color(self, hue_360: int) -> QColor:
        """
        Convert hue value (0-360) to QColor.
        
        Args:
            hue_360: Hue value in 0-360 scale
            
        Returns:
            QColor with full saturation and value
        """
        # Convert 360° scale to 0-359 for QColor.fromHsv
        hue = hue_360 % 360
        return QColor.fromHsv(hue, 255, 255)
    
    def _point_to_hue(self, x: int, y: int) -> Optional[int]:
        """
        Convert mouse click position to hue value.
        
        Args:
            x, y: Mouse coordinates relative to widget
            
        Returns:
            Hue value in 360° scale, or None if click is outside wheel
        """
        # Calculate distance from center
        dx = x - self.center_x
        dy = y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Check if click is within wheel bounds
        if distance < self.inner_radius or distance > self.outer_radius:
            return None
        
        # Calculate angle from click position
        # atan2 returns -π to π, with 0° pointing right (positive x-axis)
        angle_rad = math.atan2(dy, dx)  # -π to π, 0° = right
        
        # Convert to degrees and normalize to 0-360 range
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0:
            angle_deg += 360
        
        # Find which segment contains this angle
        # Segments are drawn with -90° offset, so segment i starts at (i * 20 - 90)°
        # We need to find which segment's drawn angle range contains angle_deg
        num_segments = len(self.hue_colors)
        angle_per_segment = 360.0 / num_segments
        
        # Check each segment to see if the click angle falls within its drawn range
        for i in range(num_segments):
            # Calculate the segment's start and end angles (in drawing coordinates)
            start_angle = i * angle_per_segment - 90
            end_angle = (i + 1) * angle_per_segment - 90
            
            # Normalize to 0-360 range
            start_angle_norm = start_angle % 360
            end_angle_norm = end_angle % 360
            
            # Check if click angle falls within this segment's range
            if start_angle_norm < end_angle_norm:
                # Normal case: no wraparound
                if start_angle_norm <= angle_deg < end_angle_norm:
                    segment = i
                    break
            else:
                # Wraparound case: segment crosses 0°/360° boundary
                if angle_deg >= start_angle_norm or angle_deg < end_angle_norm:
                    segment = i
                    break
        else:
            # Fallback: shouldn't happen, but use formula as backup
            normalized_angle = (angle_deg + 90) % 360
            segment = int(normalized_angle / 20) % 18
        
        # Get the hue value for this segment
        return self.hue_colors[segment][1]
    
    def mousePressEvent(self, event):
        """Handle mouse clicks to toggle segment selection."""
        if event.button() == Qt.LeftButton:
            hue = self._point_to_hue(event.x(), event.y())
            if hue is not None:
                # Toggle selection
                if hue in self.selected_hues:
                    self.selected_hues.remove(hue)
                else:
                    self.selected_hues.add(hue)
                
                self.update()  # Trigger repaint
                self.selectionChanged.emit(sorted(self.selected_hues))
        
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """Paint the color wheel."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw gray center circle
        center_rect = QRect(
            int(self.center_x - self.inner_radius),
            int(self.center_y - self.inner_radius),
            int(self.inner_radius * 2),
            int(self.inner_radius * 2)
        )
        painter.setBrush(QBrush(QColor(128, 128, 128)))
        painter.setPen(QPen(QColor(64, 64, 64), 2))
        painter.drawEllipse(center_rect)
        
        # Draw color segments
        num_segments = len(self.hue_colors)
        angle_per_segment = 360.0 / num_segments
        
        for i, (name, hue_360, hex_color) in enumerate(self.hue_colors):
            # Calculate angles for this segment
            # In standard math coordinates, 0° is right, counter-clockwise
            # We want Red (0°) at top, so we offset by -90° (rotate clockwise)
            start_angle = i * angle_per_segment - 90
            end_angle = (i + 1) * angle_per_segment - 90
            
            # Normalize to 0-360 range
            start_angle = start_angle % 360
            end_angle = end_angle % 360
            
            # Convert to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            # Create polygon for this segment (pie slice)
            polygon = QPolygon()
            polygon.append(QPoint(self.center_x, self.center_y))  # Center point
            
            # Handle wraparound: if end < start, we need to draw two arcs
            if end_angle < start_angle:
                # First arc: from start to 360° (2π)
                num_points = 10
                for j in range(num_points + 1):
                    # Interpolate from start_rad to 2π
                    angle = start_rad + (2 * math.pi - start_rad) * (j / num_points)
                    x = self.center_x + self.inner_radius * math.cos(angle)
                    y = self.center_y + self.inner_radius * math.sin(angle)
                    polygon.append(QPoint(int(x), int(y)))
                # Second arc: from 0° to end
                for j in range(num_points + 1):
                    angle = end_rad * (j / num_points)
                    x = self.center_x + self.inner_radius * math.cos(angle)
                    y = self.center_y + self.inner_radius * math.sin(angle)
                    polygon.append(QPoint(int(x), int(y)))
                # Outer radius (reverse order)
                for j in range(num_points, -1, -1):
                    angle = end_rad * (j / num_points)
                    x = self.center_x + self.outer_radius * math.cos(angle)
                    y = self.center_y + self.outer_radius * math.sin(angle)
                    polygon.append(QPoint(int(x), int(y)))
                for j in range(num_points, -1, -1):
                    angle = start_rad + (2 * math.pi - start_rad) * (j / num_points)
                    x = self.center_x + self.outer_radius * math.cos(angle)
                    y = self.center_y + self.outer_radius * math.sin(angle)
                    polygon.append(QPoint(int(x), int(y)))
            else:
                # Normal case: no wraparound
                num_points = 10
                for j in range(num_points + 1):
                    angle = start_rad + (end_rad - start_rad) * (j / num_points)
                    x = self.center_x + self.inner_radius * math.cos(angle)
                    y = self.center_y + self.inner_radius * math.sin(angle)
                    polygon.append(QPoint(int(x), int(y)))
                
                # Add points along outer radius (reverse order)
                for j in range(num_points, -1, -1):
                    angle = start_rad + (end_rad - start_rad) * (j / num_points)
                    x = self.center_x + self.outer_radius * math.cos(angle)
                    y = self.center_y + self.outer_radius * math.sin(angle)
                    polygon.append(QPoint(int(x), int(y)))
            
            # Get color for this segment
            color = QColor(hex_color)
            
            # Draw segment with base color
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(64, 64, 64), 1))  # Thin gray border for all segments
            painter.drawPolygon(polygon)
            
            # If selected, draw a semi-transparent grey overlay to "grey out" the segment
            if hue_360 in self.selected_hues:
                # Draw a semi-transparent grey overlay
                grey_overlay = QColor(128, 128, 128, 180)  # Grey with ~70% opacity
                painter.setBrush(QBrush(grey_overlay))
                painter.setPen(Qt.NoPen)  # No border on overlay
                painter.drawPolygon(polygon)
        
        # Draw outer border
        outer_rect = QRect(
            int(self.center_x - self.outer_radius),
            int(self.center_y - self.outer_radius),
            int(self.outer_radius * 2),
            int(self.outer_radius * 2)
        )
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(outer_rect)

