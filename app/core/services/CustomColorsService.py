"""
CustomColorsService.py - Manages shared custom colors across all color pickers

This service provides a centralized way to store and retrieve custom colors
that are shared between RGB and HSV color pickers, persisting across sessions.
"""

import json
from typing import List, Tuple, Optional
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog
from core.services.SettingsService import SettingsService


class CustomColorsService:
    """Service to manage custom colors shared across all color pickers."""
    
    MAX_CUSTOM_COLORS = 16  # Qt's QColorDialog supports 16 custom colors
    
    def __init__(self):
        """Initialize the CustomColorsService."""
        self.settings_service = SettingsService()
        self._load_custom_colors()
    
    def _load_custom_colors(self):
        """Load custom colors from settings and apply to QColorDialog."""
        try:
            # Get stored custom colors from settings
            colors_json = self.settings_service.get_setting('custom_colors')
            if colors_json:
                colors = json.loads(colors_json)
                # Apply colors to QColorDialog's static custom colors
                for i, color_rgb in enumerate(colors[:self.MAX_CUSTOM_COLORS]):
                    if color_rgb:
                        color = QColor(color_rgb[0], color_rgb[1], color_rgb[2])
                        QColorDialog.setCustomColor(i, color)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # If there's an error loading, start fresh
            pass
    
    def save_custom_colors(self):
        """Save current custom colors from QColorDialog to settings."""
        colors = []
        for i in range(self.MAX_CUSTOM_COLORS):
            color = QColorDialog.customColor(i)
            if color.isValid():
                colors.append([color.red(), color.green(), color.blue()])
            else:
                colors.append(None)
        
        # Save to settings
        self.settings_service.set_setting('custom_colors', json.dumps(colors))
    
    def add_custom_color(self, color: QColor) -> int:
        """
        Add a color to the custom colors palette.
        
        Args:
            color: QColor to add
            
        Returns:
            Index where the color was added, or -1 if palette is full
        """
        if not color.isValid():
            return -1
        
        # Check if color already exists
        for i in range(self.MAX_CUSTOM_COLORS):
            existing = QColorDialog.customColor(i)
            if existing.isValid() and existing == color:
                return i  # Color already exists
        
        # Find first empty slot or overwrite the oldest (last) one
        for i in range(self.MAX_CUSTOM_COLORS):
            existing = QColorDialog.customColor(i)
            if not existing.isValid():
                # Found empty slot
                QColorDialog.setCustomColor(i, color)
                self.save_custom_colors()
                return i
        
        # No empty slots, overwrite the last one (rotating behavior)
        # Shift all colors down by one position
        for i in range(self.MAX_CUSTOM_COLORS - 1, 0, -1):
            prev_color = QColorDialog.customColor(i - 1)
            if prev_color.isValid():
                QColorDialog.setCustomColor(i, prev_color)
        
        # Add new color at position 0
        QColorDialog.setCustomColor(0, color)
        self.save_custom_colors()
        return 0
    
    def get_custom_colors(self) -> List[Optional[Tuple[int, int, int]]]:
        """
        Get all custom colors as RGB tuples.
        
        Returns:
            List of RGB tuples or None for empty slots
        """
        colors = []
        for i in range(self.MAX_CUSTOM_COLORS):
            color = QColorDialog.customColor(i)
            if color.isValid():
                colors.append((color.red(), color.green(), color.blue()))
            else:
                colors.append(None)
        return colors
    
    def sync_with_dialog(self):
        """
        Synchronize custom colors after a QColorDialog has been used.
        This should be called after any QColorDialog.getColor() call.
        """
        self.save_custom_colors()


# Global instance for sharing across the application
_custom_colors_instance = None

def get_custom_colors_service() -> CustomColorsService:
    """Get the singleton instance of CustomColorsService."""
    global _custom_colors_instance
    if _custom_colors_instance is None:
        _custom_colors_instance = CustomColorsService()
    return _custom_colors_instance